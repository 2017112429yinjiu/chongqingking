"""Restore the measured R24 Nanqu link and its registered riverside footway."""
from bisect import bisect_right
from math import ceil, cos, sin, tau
from pathlib import Path
import os
from random import Random
import json
import runpy
import sys

import bpy
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(HERE.parent), str(SCENE / "district_500")]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, read
from retire_plots import fingerprint
from interior_terrain import clip_polygon
from riverside import bounds, material, part

START, STOP, WALK_END = -51., 83., 54.5
ROAD_EDGE, WALK_EDGE = 2.60, 5.35


class Street:
    def __init__(self, field, ground, deck):
        self.axis = [Vector(p) for p in field["axis_en"]]
        self.arc = [-(self.axis[1] - self.axis[0]).length]
        self.dirs = []
        for a, b in zip(self.axis, self.axis[1:]):
            self.arc.append(self.arc[-1] + (b - a).length)
            self.dirs.append((b - a).normalized())
        self.normals = [Vector((d.y, -d.x)) for d in self.dirs]
        self.ground, self.deck = ground, deck
        self.joins = [self.normals[0]]
        for a, b in zip(self.normals, self.normals[1:]):
            miter = (a + b).normalized()
            self.joins.append(miter / miter.dot(b))
        self.joins.append(self.normals[-1])
        self.bridge_y = self.deck_at(.02) + .0014

    def interval(self, s):
        return min(max(bisect_right(self.arc, s) - 1, 0), len(self.dirs) - 1)

    def en(self, s, c):
        i = self.interval(s)
        fraction = (s - self.arc[i]) / (self.arc[i + 1] - self.arc[i])
        return self.axis[i].lerp(self.axis[i + 1], fraction) + self.joins[i].lerp(self.joins[i + 1], fraction) * c

    def coord(self, point):
        projected = []
        for i, a in enumerate(self.axis[:-1]):
            delta = point - a
            run = delta.dot(self.dirs[i])
            segment = self.arc[i + 1] - self.arc[i]
            distance = (delta - self.dirs[i] * min(segment, max(0., run))).length_squared
            projected.append((distance, self.arc[i] + run, delta.dot(self.normals[i])))
        return min(projected)[1:]

    @staticmethod
    def hit(bvh, point):
        result = bvh.ray_cast(Vector((*point, 85.)), Vector((0, 0, -1)), 125.)[0]
        if result is None:
            raise ValueError(f"Missing support at {tuple(point)}")
        return result.z

    def land(self, p):
        return self.hit(self.ground, p)

    def deck_at(self, s):
        return self.hit(self.deck, self.en(s, 0))

    def road(self, s, c=0.):
        if s >= 0.:
            return self.deck_at(max(s, .01))
        u = (s - START) / -START
        ease = smooth(u)
        measured = self.land(self.en(START, c))
        # The west lead takes the game terrain's height. Its eastern tangent
        # meets the retained R24 asphalt. Pano Z is not used as a game datum.
        west = measured - .041 * (s - START)
        east = self.bridge_y - .068 * s
        return west * (1. - ease) + east * ease

    def walk(self, s, c):
        return self.road(s, c if s < -.01 else 0.) + .115 * smooth((s - START) / 3.0) - (c-ROAD_EDGE)*.012

    def stock(self, s, c):
        return self.en(s, c), self.road(s, c)

    def slope_top(self, s):
        return self.land(self.en(s, -3.10))

    def grading_floor(self, s, c, old):
        road = self.road(s, min(2.53, max(-2.53, c)))
        depth = .22 + 3.16 * smooth((s+1.)/11.)
        start_mix = smooth((s-START)/5.)
        end_mix = smooth((STOP-s)/9.)
        shore_width = 5.52 + 18.48 * smooth((50.-s)/8.)
        coast_mix = smooth((shore_width - c) / max(.5, shore_width - 5.52))
        if s > WALK_END:
            coast_mix = smooth((3.02-c)/.39)
        hill_mix = smooth((c+4.60)/1.20)
        factor = start_mix * end_mix * coast_mix * hill_mix
        surface = old + min(0., road - depth - old) * factor
        if c > 5.22:
            sight = smooth((s+33.)/16.) * smooth((46.-s)/15.)
            fade = smooth((62.-c)/21.) * smooth((c-5.22)/1.4)
            cap = road - .65 - (c-5.22)*.113
            surface = min(surface, old + min(0., cap-old) * sight * fade)
        return surface

    def sample(self, start, stop, gap):
        breaks = sorted({start, stop, *(s for s in self.arc if start < s < stop),
                         *(s for s in (0., 34., 42., WALK_END, 74.) if start < s < stop)})
        for a, b in zip(breaks, breaks[1:]):
            steps = ceil((b-a)/gap)
            for i in range(steps):
                yield a+(b-a)*i/steps
        yield stop


def smooth(t):
    t = min(1., max(0., t))
    return t*t*(3.-2.*t)


def patch(mesh, street, a, b, left, right, height, finish):
    points = [(a, right), (b, right), (b, left), (a, left)]
    mesh.face([at(street, s, c, height) for s, c in points], finish)


def solid(mesh, street, a, b, left, right, floor, thickness, finish):
    points = [at(street, s, c, floor) for s, c in ((a,right),(b,right),(b,left),(a,left))]
    mesh.solid(points, [(e,n,z+thickness) for e,n,z in points], finish)


def at(street, s, c, height):
    return (*street.en(s, c), height(s, c))


def subdivisions(a,b,c,depth):
    if depth==0:
        yield (a,b,c)
        return
    ab,bc,ca=(a+b)*.5,(b+c)*.5,(c+a)*.5
    for points in ((a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)):
        yield from subdivisions(*points,depth-1)


def regrade(street, local_copy):
    """The terrain cap is continuous across stock tile and triangle boundaries."""
    rows=list(street.sample(START,STOP,2.0))
    corridor=bounds([street.en(s,c) for s in rows for c in (-4.65,62.1)])
    amended=[]
    for obj in list(bpy.context.scene.objects):
        if not obj.name.startswith("COL_Outer500_Surface_"):
            continue
        points=[obj.matrix_world @ v.co for v in obj.data.vertices]
        if not part(bounds(points),corridor):
            continue
        output=Mesh(obj.name)
        changed=False
        for f in obj.data.polygons:
            polygon=[points[i] for i in f.vertices]
            finish=obj.data.materials[f.material_index]
            if not part(bounds(polygon),corridor):
                output.face(polygon,finish)
                continue
            center=sum(polygon,Vector((0.,0.,0.)))/len(polygon)
            s,c=street.coord(center.xy)
            if not START-2.5<s<STOP+2.5 or not -6.65<c<64.5:
                output.face(polygon,finish)
                continue
            for j in range(1,len(polygon)-1):
                for triangle in subdivisions(polygon[0],polygon[j],polygon[j+1],2):
                    mapped=[]
                    for v in triangle:
                        s,c=street.coord(v.xy)
                        z=v.z if s<=START or s>=STOP or c<=-4.6 or c>=62. else street.grading_floor(s,c,v.z)
                        changed|=abs(z-v.z)>.001
                        mapped.append((v.x,v.y,z))
                    output.face(mapped,finish)
        if not changed:
            continue
        copy=local_copy(obj)
        temporary=output.save()
        topology=bmesh.new()
        topology.from_mesh(temporary.data)
        bmesh.ops.remove_doubles(topology,verts=list(topology.verts),dist=.00002)
        for face in topology.faces:
            face.smooth=True
        topology.to_mesh(temporary.data)
        topology.free()
        copy.data=temporary.data
        bpy.data.objects.remove(temporary,do_unlink=True)
        amended.append(copy)
    return amended


def polygon_area(vertices):
    if len(vertices)<3:
        return 0.
    origin=vertices[0]
    return .5*sum((a-origin).cross(b-origin).length for a,b in zip(vertices[1:],vertices[2:]))


def trim_plot_53_apron(street, obj, passes, anchor):
    """Keep the accepted upper and east landing. Cut only its lower west lip."""
    owner=read(HERE/"ownership-53-lower-edge.json")["53"][obj.name]
    owned={value for record in owner for value in record["faces"]}
    faces={}
    assert anchor in owned and any(fingerprint(obj,f)==anchor for f in obj.data.polygons)
    for start,end,left,right in passes:
        rows=list(street.sample(start,end,28.))
        for a,b in zip(rows,rows[1:]):
            quad=[Vector((*street.en(s,c),0.)) for s,c in ((a,right),(b,right),(b,left),(a,left))]
            faces[a]=[(pos,Vector((pos.y-next_.y,next_.x-pos.x,0.)).normalized())
                      for pos,next_ in zip(quad,quad[1:]+quad[:1])]
    mesh=bmesh.new()
    mesh.from_mesh(obj.data)
    original_faces=list(mesh.faces)
    uv=mesh.loops.layers.uv.active
    altered=0
    for src in obj.data.polygons:
        if fingerprint(obj,src) not in owned:
            continue
        vertices=[obj.matrix_world @ obj.data.vertices[j].co for j in src.vertices]
        remaining=[vertices]
        dropped=False
        for planes in faces.values():
            survivors=[]
            for shape in remaining:
                unused=[]
                for distance in [lambda p:11.45-p.z, *(lambda p,o=o,n=n:n.dot(p-o) for o,n in planes)]:
                    shape, outside=clip_polygon(shape,distance)
                    if polygon_area(outside)>1e-7:
                        unused.append(outside)
                    if polygon_area(shape)<1e-7:
                        break
                dropped |= polygon_area(shape)>1e-7
                survivors.extend(unused)
            remaining=survivors
        if not dropped:
            continue
        old=original_faces[src.index]
        for shape in remaining:
            filtered=[v for i,v in enumerate(shape) if (shape[i-1]-v).length_squared>1e-9]
            if len(filtered)<3:
                continue
            new=mesh.faces.new([mesh.verts.new(obj.matrix_world.inverted()@v) for v in filtered])
            new.material_index=old.material_index
            if uv is not None:
                for loop in new.loops:
                    p=loop.vert.co
                    loop[uv].uv=(p.x/2.,p.y/2.) if abs(src.normal.z)>.40 else (p.x*.7+p.y*.6,p.z)
        mesh.faces.remove(old)
        altered+=1
    assert altered
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()
    return altered


def existing_trees(street):
    placed=[]
    retired=[]
    for index,row in enumerate(read(ASSETS/"layout.json")["planting"]):
        name=f"Outer500_Plant_{index:03d}"
        if name not in bpy.context.scene.objects:
            continue
        e,n,_=row["east_north_up"]
        p=Vector((e,n))
        s,c=street.coord(p)
        if not START<s<STOP or not -4.60<c<62.:
            continue
        old=street.land(p)
        dz=street.grading_floor(s,c,old)-old
        if abs(dz)<.26:
            continue
        if -2.65<c<(5.35 if s<WALK_END else 2.65):
            retired.append(name)
        else:
            placed.append({"name":name,"shift_z":dz,"root_east_north":[e,n]})
    return placed,retired


def tint(name, rgb, metallic=0.):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1.)
    mat.metallic = metallic
    mat.roughness = .68
    return mat


def build_street(street, materials):
    road = Mesh("COL_Nanqu_RaisedWestApproach")
    walk = Mesh("COL_Nanqu_RiverFootway")
    stone = Mesh("Nanqu_FootwayGreyStoneJoints")
    curb = Mesh("COL_Nanqu_StreetKerbs")
    wall = Mesh("COL_Nanqu_HillsideRetaining")
    marks = Mesh("Nanqu_ApproachPaint")
    posts = Mesh("Nanqu_RiverBarrierStonePosts")
    contact_rail = Mesh("COLH_Nanqu_RiverBarrier")
    brackets = Mesh("Nanqu_DeckEdgeBrackets")
    railing = Mesh("Nanqu_GalvanizedVerticals")
    way_end = Mesh("COL_Nanqu_EndOfPedestrianAccess")
    furniture = Mesh("COL_Nanqu_TreeAndFlowerBoxes")
    planting = Mesh("Nanqu_TreeAndFlowerCanopies")
    sign = Mesh("Nanqu_PedestrianLimitSign")
    gravel = Mesh("Nanqu_HillsidePlantedStrip")
    asphalt, flags, coping, retaining, timber, concrete = (materials[k] for k in
        ("road","flags","edge","wall","timber","concrete"))
    old_road = street.road
    sidewalk = street.walk
    patch_road = list(street.sample(START,0.,1.1))
    edge = list(street.sample(START,WALK_END,.88))
    for a,b in zip(patch_road,patch_road[1:]):
        patch(road,street,a,b,-ROAD_EDGE,ROAD_EDGE,old_road,asphalt)
        # A thin joint at the original asphalt is intentionally part of the slab.
        if a>-48.:
            for c in (-2.44,2.46):
                patch(marks,street,a,b,c-.044,c+.044,lambda s,t: old_road(s,t)+.009,materials["white"])
    patch(road,street,-.14,.19,-2.59,2.59,lambda s,c:old_road(s,c)+.004,asphalt)
    for a in range(-47, -2, 6):
        patch(marks,street,a,min(a+2.7,-.04),-.047,.047,lambda s,c: old_road(s,c)+.009,materials["white"])
    for a,b in zip(edge,edge[1:]):
        solid(walk,street,a,b,ROAD_EDGE,WALK_EDGE,lambda s,c:sidewalk(s,c)-.29,.29,flags)
        solid(curb,street,a,b,ROAD_EDGE-.11,ROAD_EDGE+.02,lambda s,c:sidewalk(s,c)-.15,.156,coping)
        solid(curb,street,a,b,WALK_EDGE-.16,WALK_EDGE,lambda s,c:sidewalk(s,c)-.22,.285,coping)
        # The transverse dark joints and staggered longitudinal joints share the
        # paving grid, anchored to the metres of the road rather than image UV.
        if a>START+.2:
            patch(stone,street,a,a+.010,2.64,5.19,lambda s,c:sidewalk(s,c)+.003,materials["joint"])
        for i in range(1,5):
            shift = .13 if int((a-START)*1.14)%2 else 0.
            c = 2.65 + i*.49 + shift
            patch(stone,street,a,b,c,c+.008,lambda s,c:sidewalk(s,c)+.003,materials["joint"])
    hill_edges = list(street.sample(START,STOP,1.65))
    for a,b in zip(hill_edges,hill_edges[1:]):
        def toe(s,c):
            floor = old_road(s,-2.53)-.16
            below = floor - (2.5*smooth(s/9.))
            return below if s<74 else min(below,street.slope_top(s)-.02)
        def top(s,c):
            amount = street.slope_top(s)
            return max(toe(s,c)+.04, amount)
        points=[at(street,b,-3.10,toe),at(street,a,-3.10,toe),at(street,a,-3.10,top),at(street,b,-3.10,top)]
        wall.face(points[::-1],retaining)
        solid(wall,street,a,b,-3.12,-2.94,top,.10,coping)
        if a < 73.:
            solid(curb,street,a,b,-2.66,-2.56,lambda s,c:old_road(s,c)-.03,.22,concrete)
        if a >= WALK_END:
            for left,right,mid in ((2.59,2.87,2.75),(-2.87,-2.59,-2.75)):
                solid(way_end,street,a,b,left,right,lambda s,c:old_road(s)+.012,.45,concrete)
                solid(railing,street,a,b,mid-.024,mid+.024,lambda s,c:old_road(s)+.519,.071,materials["blue_rail"])
                solid(railing,street,a,a+.048,mid-.023,mid+.023,
                      lambda s,c:old_road(s)+.45,.114,materials["tube"])
    for a in range(-46,54,2):
        for c in (5.20,):
            base=lambda s,t:sidewalk(s,t)+.07
            solid(posts,street,a-.12,a+.12,c-.093,c+.092,base,.88,coping)
            solid(posts,street,a-.14,a+.14,c-.11,c+.108,lambda s,t:base(s,t)+.87,.075,coping)
            for offset in (.29,.51,.73,.95,1.17,1.39,1.61,1.83):
                x=a+offset
                solid(railing,street,x-.014,x+.014,c-.016,c+.017,lambda s,t:base(s,t)+.15,.63,materials["tube"])
            for z in (.16,.77):
                solid(railing,street,a,a+2.,c-.027,c+.024,lambda s,t:base(s,t)+z,.041,materials["tube"])
            # Continuous simple blocker matches the rail's public boundary.
            p,q = a,a+2.
            positions=[at(street,p,c,base),at(street,q,c,base),
                       at(street,q,c,lambda s,t:base(s,t)+.87),at(street,p,c,lambda s,t:base(s,t)+.87)]
            contact_rail.face(positions,materials["invisible"])
    for s in range(2,54,4):
        a,b=s-.17,s+.17
        locs = [(2.40,-.78),(5.34,-.28),(2.40,-.28)]
        ends=[[( *street.en(t,c), old_road(t)+z) for c,z in locs] for t in (a,b)]
        brackets.solid(ends[0],ends[1],concrete)
    for c in (3.12,4.76):
        solid(way_end,street,WALK_END-.22,WALK_END-.10,c-.055,c+.055,sidewalk,.86,coping)
    solid(way_end,street,WALK_END-.20,WALK_END-.115,2.66,5.31,lambda s,c:sidewalk(s,c)+.65,.073,materials["tube"])
    # Most street furniture stays on the outboard half. These contacts are
    # exported separately for actual in-engine raycasts after import.
    random = Random(59146775)
    contacts = []
    for i,s in enumerate((-41.0,-28.8,-16.9,-4.8,7.0,19.1,30.6,42.37)):
        c = 4.46
        a,b = s-.66,s+.65
        low=sidewalk
        def plinth(s,c):
            return low(s,c) + .035
        solid(furniture,street,a,b,c-.43,c+.43,plinth,.455,timber)
        for x in (a+.055,b-.16):
            for y in (c-.38,c+.27):
                solid(furniture,street,x,x+.10,y,y+.10,sidewalk,.038,coping)
        for l in (c-.441,c+.420):
            for j in range(12):
                x = a + j*.107
                solid(furniture,street,x,x+.081,l,l+.028,plinth,.461,materials["wood_variants"][j%3])
        for l in (c-.457,c+.399):
            solid(furniture,street,a-.04,b+.04,l,l+.057,lambda s,c:low(s,c)+.48,.066,timber)
        for t in (a-.04,b-.005):
            solid(furniture,street,t,t+.059,c-.45,c+.45,lambda s,c:low(s,c)+.48,.066,timber)
        solid(planting,street,a+.054,b-.054,c-.375,c+.375,lambda s,c:low(s,c)+.49,.014,materials["earth"])
        root = Vector((*street.en(s,c),low(s,c)+.49))
        tree(planting, root, 2.25+i%3*.24, random, materials)
        for x in range(53):
            u=random.uniform(a+.08,b-.08); v=random.uniform(c-.35,c+.35)
            p=Vector((*street.en(u,v),low(u,v)+.50))
            flowers(planting,p,random,materials)
        contacts.extend([at(street,x,y,sidewalk) for x,y in ((a,c-.4),(a,c+.4),(b,c-.4),(b,c+.4))])
    for i,s in enumerate((51.35,51.86)):
        c=4.58
        solid(furniture,street,s-.23,s+.23,c-.22,c+.22,sidewalk,.63,materials["bins"][i])
        solid(furniture,street,s-.25,s+.25,c-.24,c+.24,lambda s,c:sidewalk(s,c)+.63,.076,materials["tube"])
        solid(furniture,street,s-.19,s+.19,c-.227,c-.209,lambda s,c:sidewalk(s,c)+.47,.105,materials["joint"])
    s,c=WALK_END-.65,4.97
    solid(way_end,street,s-.035,s+.035,c-.035,c+.035,sidewalk,1.93,materials["tube"])
    center=Vector((*street.en(s-.06,c),sidewalk(s,c)+1.70))
    normal = street.dirs[street.interval(s)]
    tangent=Vector((normal.y,-normal.x,0.))
    for i in range(32):
        a,b=tau*i/32,tau*(i+1)/32
        def rim(t,r):
            return center+tangent*(sin(t)*r)+Vector((0,0,cos(t)*r))
        for poly,finish in (([center,rim(a,.206),rim(b,.206)],materials["white"]),
                            ([rim(a,.206),rim(a,.248),rim(b,.248),rim(b,.206)], materials["red"])):
            sign.face(poly,finish)
            sign.face(poly[::-1],finish)
    # An upright glyph on the back of the curb. No visitor destination beyond it.
    for y0,y1,u0,u1 in ((-.016,.092,-.028,.026),(-.022,.067,.016,.043),(-.149,-.012,-.055,-.023),
                        (-.133,-.006,.022,.048),(.091,.138,-.022,.022)):
        p=center-Vector((*normal,0.))*.006
        face=[p+tangent*u+Vector((0,0,z)) for u,z in ((u0,y0),(u1,y0),(u1,y1),(u0,y1))]
        sign.face(face,materials["joint"])
        sign.face(face[::-1],materials["joint"])
    for a in range(55,80):
        base=lambda s,c:old_road(s)+.437
        for side in (-1,1):
            for j in range(13):
                run=a+j*.071
                c=side*(2.82+random.uniform(-.065,.22))
                p=Vector((*street.en(run,c),base(run,c)))
                flowers(gravel,p,random,materials,purple=True)
                leaf(gravel,p+Vector((0,0,.07)),random.random()*tau,.092,materials["green"][j%4])
    return [m.save() for m in (road,walk,stone,curb,wall,marks,posts,contact_rail,brackets,railing,way_end,furniture,planting,sign,gravel)],contacts


def cylinder(mesh, a, b, radius_a, radius_b, material, segments=7):
    forward = (b-a).normalized()
    axis = forward.cross(Vector((1,0,0))).normalized()
    across = forward.cross(axis)
    angles = [axis*cos(tau*i/segments)+across*sin(tau*i/segments) for i in range(segments)]
    mesh.solid([a+d*radius_a for d in angles],[b+d*radius_b for d in angles],material)


def leaf(mesh,p,axis,width,leaf_material):
    direction=Vector((cos(axis),sin(axis),0.))
    cross=Vector((-direction.y,direction.x,.15))
    front=p+direction*width
    back=p-direction*width
    for side in (-1,1):
        blade = [front,p+cross*(side*width*.55),back,p+Vector((0,0,width*.30))]
        mesh.face(blade,leaf_material)
        mesh.face(blade[::-1],leaf_material)


def tree(mesh,root,height,rng,m):
    crown=root+Vector((.10,-.08,height-.35))
    cylinder(mesh,root,crown,.075,.025,m["bark"])
    for i in range(7):
        angle=tau*i/7+rng.uniform(-.27,.27)
        foot=root.lerp(crown,rng.uniform(.55,.88))
        branch=crown+Vector((cos(angle)*rng.uniform(.28,.64),sin(angle)*rng.uniform(.28,.70),rng.uniform(-.06,.55)))
        cylinder(mesh,foot,branch,.023,.007,m["bark"],5)
        for j in range(39):
            delta=Vector((rng.uniform(-.35,.35),rng.uniform(-.36,.36),rng.uniform(-.23,.28)))
            leaf(mesh,branch+delta,rng.random()*tau,rng.uniform(.09,.19),m["green"][j%4])


def flowers(mesh,root,rng,m,purple=False):
    for i in range(4):
        angle=rng.random()*tau
        p=root+Vector((rng.uniform(-.058,.058),rng.uniform(-.045,.045),rng.uniform(.048,.10)))
        leaf(mesh,p,angle,.061,m["green"][i])
    height=rng.uniform(.125,.219)
    head=root+Vector((0,0,height))
    colors=m["purple"] if purple else m["orange"]
    for i in range(5):
        angle=tau*i/5
        p=head+Vector((cos(angle)*.02,sin(angle)*.02,0.))
        leaf(mesh,p,angle,.023,colors[i%len(colors)])


def main(out):
    field=read(HERE/"field.json")
    previous=runpy.run_path(str(SCENE/"district_refresh/riverside/east_bend/build.py"))
    panda=runpy.run_path(str(HERE.parent/"panda_15_17/build.py"))
    a2=runpy.run_path(str(HERE.parent/"zhongxing_bridge_18_21/build.py"))
    street=Street(field,terrain(),a2["deck_index"]())
    texture_spec={
        "road":("Nanqu exposed west asphalt",(.59,.60,.61),"asphalt_02_diff_1k.jpg"),
        "flags":("Nanqu grey split flagstones",(.66,.70,.73),"stone_floor_diff_2k.jpg"),
        "edge":("Nanqu tumbled grey kerb",(.66,.67,.63),"concrete_floor_worn_001_diff_2k.jpg"),
        "wall":("Nanqu hillside ashlar wall",(.70,.69,.64),"stone_wall_05_diff_2k.jpg"),
        "timber":("Nanqu amber wood box grain",(.78,.57,.229),"wood_table_worn_diff_2k.jpg"),
        "concrete":("Nanqu older concrete apron",(.67,.67,.63),"concrete_wall_006_diff_2k.jpg"),
    }
    finishes={k:material(*args) for k,args in texture_spec.items()}
    finishes.update({
        "white":tint("Nanqu weathered line white",(.73,.73,.67)),
        "red":tint("Nanqu traffic prohibition enamel",(.49,.026,.033)),
        "joint":tint("Nanqu deep concrete mortar",(.20,.193,.18)),
        "tube":tint("Nanqu tarnished green galvanized railing",(.26,.31,.267),.40),
        "blue_rail":tint("Nanqu blue-grey painted carriageway dividers",(.086,.207,.29),.25),
        "earth":tint("Nanqu planted box soil",(.117,.074,.034)),
        "bark":tint("Nanqu ash brown bark",(.17,.127,.085)),
        "invisible":tint("Nanqu rail contact only",(0.,0.,0.)),
    })
    finishes["green"]=[tint(f"Nanqu leaf hue {i}",rgb) for i,rgb in enumerate(((.06,.14,.028),(.105,.199,.052),(.17,.25,.069),(.094,.192,.062)))]
    finishes["orange"]=[tint(f"Nanqu orange bloom {i}",rgb) for i,rgb in enumerate(((.74,.17,.018),(.96,.339,.026),(.84,.228,.022)))]
    finishes["purple"]=[tint(f"Nanqu purple verge bloom {i}",rgb) for i,rgb in enumerate(((.59,.047,.29),(.78,.107,.41),(.44,.025,.21)))]
    finishes["wood_variants"]=[tint(f"Nanqu narrow slat {i}",rgb) for i,rgb in enumerate(((.68,.38,.090),(.59,.302,.065),(.73,.46,.122)))]
    finishes["bins"]=[tint("Nanqu bins blue",(.047,.22,.41)),tint("Nanqu bins charcoal",(.09,.10,.104))]
    additions,contacts=build_street(street,finishes)
    moved_trees, removed_trees=existing_trees(street)
    replacements,retired,counts=panda["retire"](previous,(4,6,51),HERE/"ownership.json")
    envelope=next(obj for obj in replacements if obj.name=="COL_Outer500_Building_envelopes")
    counts["plot53_lower_lip_only"]=trim_plot_53_apron(
        street,envelope,[(44.,54.5,-2.65,5.48),(54.5,60.4,-2.65,2.62)],
        "ae5e9cfc5027929887320960")
    retaining=next(obj for obj in replacements if obj.name=="COL_Outer500_Retaining_and_boundaries")
    counts["plot53_over_04_inner_wheel_line"]=trim_plot_53_apron(
        street,retaining,[(61.5,68.9,.14,2.62)],"bcff5af69551042b38c34871")
    retired.extend(removed_trees)
    grades=regrade(street,previous["local_copy"])
    replacements.extend(grades)
    # Replace only the old outboard rail faces within the exposed walk segment.
    # The uphill divider, all central bridge beam vertices and the existing
    # running surface are retained at their original positions.
    rail=previous["local_copy"](bpy.context.scene.objects["Outer500_LaundryRailReturn"])
    retire_geometry=runpy.run_path(str(HERE.parent/"retire_plots.py"))
    cut=[]
    for f in rail.data.polygons:
        p=rail.matrix_world @ f.center
        s,c=street.coord(p.xy)
        old_river_rail=-.25<=s<=WALK_END+.10 and 2.35<=c<=2.93
        road_only_rails=WALK_END-.10<s<=STOP and 2.35<=abs(c)<=2.93
        if (old_river_rail or road_only_rails) and abs(p.z-street.road(s))<1.80:
            cut.append(f.index)
    assert cut
    retire_geometry["remove_faces"](rail,cut)
    replacements.append(rail)
    counts[rail.name]=len(cut)
    inherited=read(ASSETS/"wilderness-50.json")["borrowed_materials"]
    slots={}
    for obj in replacements:
        names={m.name for m in obj.data.materials}
        aliases=inherited.get(obj.name,{})
        slots[obj.name]={alias:material for alias,material in aliases.items() if alias in names}
    # Terrain shading is assigned by the normal scene. The rail can reuse the
    # original live material slots, which are named in the loaded parent.
    slots[rail.name].update(previous["borrow_slots"](
        [rail],{rail.name:{m.name for m in rail.data.materials}})[rail.name])
    values=[-37.,-31.,-25.,-19.,-13.,-7.,-1.,5.,11.,17.,23.,29.,35.,41.,47.,52.4]
    route=[at(street,s,3.48,street.walk) for s in values]
    driving=[at(street,s,1.05,street.road) for s in [-28,-22,-16,-10,-4,0,6,12,18,24,30,36,42,48,54,60,66,72,78,83,88]]
    frame = [Vector(p) for p in field["plot04_outline_en"]]
    end = Vector(route[-1][:2])
    def distance(a, b):
        axis = b - a
        part = min(1., max(0., (end-a).dot(axis)/axis.length_squared))
        return (end-a.lerp(b, part)).length
    plan={"new_meshes":[ob.name for ob in additions],"replacement_meshes":[ob.name for ob in replacements],
          "retired_objects":retired,"retired_plots":[4,6,51],"removed_face_counts":counts,
          "borrowed_materials":slots,"surface_textures":{
              label:f"res://assets/chongqing_district_{file}" for label,_,file in texture_spec.values()},
          "public_walk":route,"bike_path":driving,"planter_contacts":contacts,
          "walk_limit_station_m":WALK_END,"roadway_way_ids":[176034685,59146775],
          "support_structure":"COL_R24_LinkDeck_R24_link_asphalt","rebase_trees":moved_trees,
          "walk_near_plot04_distance_m":min(distance(a, b) for a,b in zip(frame,frame[1:]+frame[:1]))}
    keep=set(additions+replacements)
    for ob in list(bpy.data.objects):
        if ob not in keep:
            bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    source=Path(os.environ.get("CQ_NANQU_SOURCE",out/"nanqu-04-06-51.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=True)
    bpy.ops.export_scene.gltf(filepath=str(out/"nanqu-04-06-51.glb"),export_format="GLB",
                              export_image_format="NONE",export_cameras=False,export_lights=False)
    (out/"nanqu-04-06-51.json").write_text(json.dumps(plan,indent=2)+"\n")
    print("CQ_NANQU_BUILD", counts)


if __name__=="__main__":
    main(Path(sys.argv[-1]).resolve())
