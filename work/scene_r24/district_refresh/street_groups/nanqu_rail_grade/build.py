"""Regrade the existing Nanqu road from camera controls and preserve named owners."""
from bisect import bisect_right
import json
from math import ceil, hypot, pi
from pathlib import Path
from random import Random
import runpy
from statistics import median
import sys

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt

HERE=Path(__file__).resolve().parent
SCENE=HERE.parents[2]

ROAD_DONORS = {
    'COL_R24_LinkDeck_R24_link_asphalt':'COL_R24_LinkDeck_R24_link_asphalt',
    'R24_FlyoverBox_R24_link_concrete':'COL_R24_FlyoverBox_R24_link_concrete',
    'R24_LinkPaint_R24_edge_line':'R24_LinkPaint_R24_edge_line',
    'R24_LinkRail_R24_link_painted_rail':'R24_LinkRail_R24_link_painted_rail',
    'COL_R24_LinkPiers_R24_link_concrete':'COL_R24_LinkPiers_R24_link_concrete',
    'R24_LinkCaps_R24_link_concrete':'COL_R24_LinkCaps_R24_link_concrete',
    'R24_LinkCaps_R24_bearing_pad':'R24_LinkCaps_R24_bearing_pad',
    **{f'COL_Road_59146775_{part}_{finish}':f'COL_Road_59146775_{part}_{finish}' for part in (0,1) for finish in ('asphalt','curb_painted_metal')},
    'Road_paint_59146775_line_white':'Road_paint_59146775_line_white',
    'Road_paint_59146775_line_white.001':'Road_paint_59146775_line_white_001',
}
APPROACH = ('COL_Nanqu_RaisedWestApproach','COL_Nanqu_RiverFootway','Nanqu_FootwayGreyStoneJoints',
            'COL_Nanqu_StreetKerbs','Nanqu_ApproachPaint','Nanqu_RiverBarrierStonePosts',
            'COLH_Nanqu_RiverBarrier','Nanqu_DeckEdgeBrackets','Nanqu_GalvanizedVerticals',
            'COL_Nanqu_EndOfPedestrianAccess','COL_Nanqu_TreeAndFlowerBoxes',
            'Nanqu_TreeAndFlowerCanopies','Nanqu_PedestrianLimitSign','Nanqu_HillsidePlantedStrip')
RAIL = ('COL_Nanjimen_NorthRailSteelBox','Nanjimen_NorthAcousticHood','Nanjimen_NorthHoodDivisions',
        'COL_Nanjimen_NorthRailPiers','Nanjimen_NorthRailBoxStiffeners')
SPUR = ('COL_Houci16_Road_176968735','COL_Houci16_RoadsideEdges','Houci16_JointsAndRoadPaint',
        'COL_Houci16_SpurSlab','COL_Houci16_SpurBearings','COL_Houci16_SpurGuardrail')


def curve(table):
    table=sorted(table)
    xs=[point[0] for point in table]
    def pick(x):
        i=max(0,min(len(table)-2,bisect_right(xs,x)-1))
        a,h0=table[i]; b,h1=table[i+1]
        return h0 + (h1-h0)*(x-a)/(b-a)
    return pick


def load(path, names):
    with bpy.data.libraries.load(str(path), link=True, relative=False) as (old, new):
        missing=set(names)-set(old.objects)
        if missing:
            raise ValueError((path,sorted(missing)))
        new.objects=list(names)
    clones={}
    for old in new.objects:
        obj=old.copy()
        obj.data=old.data.copy()
        bpy.context.collection.objects.link(obj)
        obj.matrix_world=old.matrix_world.copy()
        clones[old.name]=obj
    return clones


def bake(obj):
    transform=obj.matrix_world.copy()
    obj.data.transform(transform)
    obj.parent=None
    obj.matrix_world.identity()
    obj.data.update()


def tree(obj):
    return BVHTree.FromPolygons([v.co for v in obj.data.vertices],[tuple(f.vertices) for f in obj.data.polygons])


def focus_profile(surfaces):
    triangles=[]
    for obj in surfaces:
        obj.data.calc_loop_triangles()
        for face in obj.data.loop_triangles:
            pts=[obj.data.vertices[i].co.copy() for i in face.vertices]
            triangles.append((min(p.x for p in pts),max(p.x for p in pts),pts))
    result=[]
    for e in range(-245,216):
        sections=[]
        for left,right,v in triangles:
            if not left<=e<right:
                continue
            crossing=[]
            for a,b in zip(v,v[1:]+v[:1]):
                if min(a.x,b.x)<=e<max(a.x,b.x):
                    crossing.append(a.lerp(b,(e-a.x)/(b.x-a.x)).z)
            if len(crossing)==2:
                sections.append(sum(crossing)/2)
        if sections:
            result.append((e,median(sections)))
    return result


def bounded_height(obj, lift):
    # The old bearing meshes contain isolated supports separated along the road.
    # Group each support geometrically and hold its original footing fixed.
    vertices=sorted(obj.data.vertices,key=lambda a:a.co.x)
    clusters=[[]]
    for v in vertices:
        if clusters[-1] and v.co.x-clusters[-1][-1].co.x>3.0:
            clusters.append([])
        clusters[-1].append(v)
    for group in clusters:
        low=min(v.co.z for v in group)
        high=max(v.co.z for v in group)
        e=median(v.co.x for v in group)
        for v in group:
            v.co.z+=lift(e)*(v.co.z-low)/max(.001,high-low)
    obj.data.update()


def move(obj, lift, axis=0):
    for v in obj.data.vertices:
        v.co.z+=lift(v.co[axis])
    obj.data.update()


def add_west_bearings(deck, lower_target):
    # These game-side bearers support the exposed portion within the playable boundary.
    # The upstream public fork itself is beyond that boundary.
    roadway=tree(deck)
    values=[]
    for east,north in ((-239,-21.1),(-228,-29.2),(-216,-38.0),(-205,-46.2)):
        hit=roadway.ray_cast(Vector((east,north,65)),Vector((0,0,-1)),55)[0]
        if not hit:
            continue
        top=hit.z
        base=lower_target(east)-.6
        values.append([east,north,base,top])
        for width,depth,bottom,upper in ((.70,.66,base,top-.66),(1.86,.89,top-.66,top-.38)):
            bpy.ops.mesh.primitive_cube_add(size=2,location=(east,north,(upper+bottom)/2))
            part=bpy.context.object
            part.name=f'COL_NanquGrade_WestBearing_{len(values):02d}_{int(width>1)}'
            part.scale=(width,depth,(upper-bottom)/2)
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
            finish=bpy.data.materials.get('Nanqu retaining concrete')
            if finish is None:
                finish=bpy.data.materials.new('Nanqu retaining concrete')
                finish.diffuse_color=(.38,.40,.38,1)
                finish.roughness=.91
            part.data.materials.append(finish)
    return values


def set_spur_slab(asphalt, slab, thickness=.58, elevation=None):
    """Use the same plan and triangulation as the finished running surface."""
    asphalt.data.calc_loop_triangles()
    number=len(asphalt.data.vertices)
    top=[(v.co.x,v.co.y,(elevation(v.co) if elevation else v.co.z)-.032)
         for v in asphalt.data.vertices]
    bottom=[(e,n,z-thickness) for e,n,z in top]
    faces=[tuple(q.vertices) for q in asphalt.data.loop_triangles]
    cut_edges={}
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):
            if (b,a) in cut_edges: del cut_edges[b,a]
            else: cut_edges[a,b]=True
    floor=[tuple(i+number for i in face[::-1]) for face in faces]
    sides=[(b,a,a+number,b+number) for a,b in cut_edges]
    material=slab.data.materials[0]
    replacement=bpy.data.meshes.new('Nanqu-grade spur slab')
    replacement.from_pydata(top+bottom,[],faces+floor+sides)
    replacement.materials.append(material)
    uv=replacement.uv_layers.new(name='UVMap')
    for poly in replacement.polygons:
        for loop in poly.loop_indices:
            e,n,z=replacement.vertices[replacement.loops[loop].vertex_index].co
            uv.data[loop].uv=(e*.5,n*.5+z*.12)
    replacement.update()
    slab.data=replacement


def road_patch(name, samples, half_width, style, base=None, clear_join=None):
    mesh=style['Mesh'](name)
    pavement=style['material']('Nanqu approach aggregate',(.47,.46,.44),'asphalt_02_diff_1k.jpg')
    edge=style['material']('Nanqu approach pale cast kerb',(.60,.61,.59),'concrete_wall_006_diff_2k.jpg')
    centres=[Vector((e,n,z)) for e,n,z in samples]
    edges=[]
    for i, c in enumerate(centres):
        direction=centres[min(i+1,len(centres)-1)]-centres[max(i-1,0)]
        flank=Vector((-direction.y,direction.x,0)).normalized()
        edges.append((c-flank*half_width,c+flank*half_width))
    for a,b in zip(edges,edges[1:]):
        mesh.face([a[0],b[0],b[1],a[1]],pavement)
        if base is not None and (clear_join is None or all((Vector((row[0].x,row[0].y))-clear_join).length>3.6 for row in (a,b))):
            for i in (0,1):
                bottom=[(q.x,q.y,base(q)) for q in (a[i],b[i])]
                mesh.face([a[i],*bottom,b[i]] if i==0 else [b[i],*bottom[::-1],a[i]],edge)
    return mesh.save()


def abutment(north_end, levels, earth, axis, style):
    mesh=style['Mesh']('COL_NanquGrade_RegisteredNorthAbutment')
    stone=style['material']('Nanqu north portal concrete',(.60,.63,.62),'concrete_wall_006_diff_2k.jpg')
    n=north_end
    a,b=[style['read_axis'](axis[key],n,1) for key in ('878019566','1134456893')]
    e=(a.x+b.x)*.5
    deck=levels(n)
    bottom=earth(n)-.50
    # Retain a clear path beneath the open bearing. Wing dimensions are a game fit.
    for side in (-1,1):
        x=e+side*7.20
        ring=lambda z,w:[(x+dx,n+dy,z) for dx,dy in ((-w,-2.10),(w,-2.10),(w,2.00),(-w,2.00))]
        mesh.solid(ring(bottom,1.85),ring(deck-.78,1.50),stone)
        mesh.solid(ring(deck-.78,1.50),ring(deck+.03,2.66),stone)
    return mesh.save()


def east_join(joins):
    # The camera series ends on the spur. Interpolate to the existing playable
    # north road terrain, using measured landing height and approach tangents.
    start,land=joins[0],joins[-1]
    n0,n1=start[1],land[1]
    h0,h1=start[2],land[2]
    for e,n,z in joins:
        t=(n-n0)/(n1-n0)
        a=2*t**3-3*t**2+1; b=t**3-2*t**2+t
        c=-2*t**3+3*t**2; d=t**3-t**2
        y=a*h0+b*(n1-n0)*.055+c*h1+d*(n1-n0)*.20
        yield [e,n,max(y,z+.015 if t>.04 else y)]


def shape_spur_merge(connector, junction, east_axis):
    profile=curve([(n,e) for e,n in east_axis])
    joint_z=lambda n:junction[2]+(n-junction[1])*.071
    for name,obj in connector.items():
        if name=='COL_Houci16_SpurSlab':continue
        running=name=='COL_Houci16_Road_176968735'
        if name in ('COL_Houci16_RoadsideEdges','COL_Houci16_SpurGuardrail'):
            bm=bmesh.new()
            bm.from_mesh(obj.data)
            obsolete=[]
            for face in bm.faces:
                c=face.calc_center_median()
                if c.y>=34. and c.x<profile(c.y)-.48:
                    obsolete.append(face)
            bmesh.ops.delete(bm,geom=obsolete,context='FACES')
            bm.to_mesh(obj.data)
            bm.free()
        if not running:
            # Move the structural faces near the merge with their original
            # vertical offsets from the running strip.
            continue
        for v in obj.data.vertices:
            u=max(0.,min(1.,(v.co.y-31.)/8.))
            w=u*u*(3.-2.*u)
            v.co.z=(1.-w)*v.co.z+w*joint_z(v.co.y)
        obj.data.update()
    return {'north_start':31.,'north_match':39.,'joint':junction,'longitudinal_grade':.071}


def match_incoming(rows, join):
    controls=join['joint']
    out=[]
    for e,n,z in rows:
        u=max(0.,min(1.,(n-join['north_start'])/(join['north_match']-join['north_start'])))
        w=u*u*(3.-2.*u)
        out.append([e,n,z+(controls[2]+(n-controls[1])*join['longitudinal_grade']-z)*w])
    return out


def merge_level(north, original, tie):
    if north <= 33.9 or north >= 49.:
        return original
    # Begin the blend after the existing upstream cross-section. Both
    # approaches share the plane before the first wheel contact at N37.97.
    t = min(1., (north - 33.9) / 3.1, (49. - north) / 3.5)
    plane = tie[2] + (north - tie[1]) * .071
    return original + (plane - original) * t * t * (3. - 2. * t)


def merge_top(parts, tie):
    """Weld the three road strips and the small apron in plan before grading."""
    coordinates, triangles, owners, texture, skirts = [], [], [], [], []
    for index, obj in enumerate(parts):
        mesh = obj.data
        mesh.calc_loop_triangles()
        uv = mesh.uv_layers.active.data
        for tri in mesh.loop_triangles:
            vertices = [mesh.vertices[i].co.copy() for i in tri.vertices]
            tex = [uv[i].uv.copy() for i in tri.loops]
            if tri.normal.z <= .55:
                skirts.append((index, vertices, tex, tri.material_index))
                continue
            start = len(coordinates)
            coordinates.extend(vertices)
            triangles.append([start, start + 1, start + 2])
            owners.append((index, tri.material_index))
            texture.append(tex)
    xy, _, faces, _, _, origins = delaunay_2d_cdt(
        [co.xy for co in coordinates], [], triangles, 1, .00025)
    covered = [(face, sources) for face, sources in zip(faces, origins, strict=True) if sources]
    pieces = [[] for _ in parts]
    grades = {}

    def weights(point, origin):
        a, b, c = [coordinates[i].xy for i in triangles[origin]]
        area = (b - a).cross(c - a)
        w = (point - a).cross(c - a) / area
        t = (b - a).cross(point - a) / area
        return [1 - w - t, w, t]

    for face, sources in covered:
        # Road 16 owns the first strip, then the incoming and outgoing
        # streets. Intersections are no longer exported as stacked faces.
        origin = min(sources)
        for i in face:
            grades[i] = min(origin, grades.get(i, origin))
        average_north = sum(xy[i].y for i in face) / len(face)
        if 36. <= average_north <= 48.:
            # Keep the common carriageway in one collision mesh, including
            # the old three-way vertex and the end of the separate apron.
            index, material = 0, 0
            uv = [xy[i] * .58 for i in face]
        else:
            index, material = owners[origin]
            uv = [sum((value * w for value, w in zip(texture[origin], weights(xy[i], origin))), Vector((0, 0)))
                  for i in face]
        pieces[index].append((face, uv, material))

    deck = []
    for i, point in enumerate(xy):
        if i not in grades:
            deck.append(Vector((point.x, point.y, 0)))
            continue
        origin = grades[i]
        old = sum(coordinates[j].z * w for j, w in zip(triangles[origin], weights(point, origin)))
        deck.append(Vector((point.x, point.y, merge_level(point.y, old, tie))))
    surface = BVHTree.FromPolygons(deck, [face for face, _ in covered], all_triangles=True)
    for index, vertices, tex, material in skirts:
        if 32. <= max(v.y for v in vertices) <= 49.:
            # Skirts sit under the exposed outside edges only. An inner
            # skirt can strike the wheel even when both road tops align.
            a, b = sorted(vertices, key=lambda v: v.z, reverse=True)[:2]
            direction = b.xy - a.xy
            outward = Vector((-direction.y, direction.x)).normalized() * .035
            centre = (a.xy + b.xy) * .5
            def paved(point):
                return surface.ray_cast(Vector((point.x, point.y, 50)), Vector((0, 0, -1)), 28)[0] is not None
            if direction.length > .003 and paved(centre - outward) and paved(centre + outward):
                continue
            for v in vertices:
                if v.z > 31.:
                    v.z = merge_level(v.y, v.z, tie)
        start = len(deck)
        deck.extend(vertices)
        pieces[index].append(([start, start + 1, start + 2], tex, material))
    for obj, section in zip(parts, pieces, strict=True):
        mesh = bpy.data.meshes.new(obj.data.name + ' joined')
        ids = sorted({i for face, _, _ in section for i in face})
        compact = {i: j for j, i in enumerate(ids)}
        mesh.from_pydata([deck[i] for i in ids], [], [[compact[i] for i in face] for face, _, _ in section])
        for material in obj.data.materials:
            mesh.materials.append(material)
        uv = mesh.uv_layers.new(name='UVMap')
        for poly, (_, tex, material) in zip(mesh.polygons, section, strict=True):
            poly.material_index = material
            for li, value in zip(poly.loop_indices, tex, strict=True):
                uv.data[li].uv = value
        mesh.update()
        if obj == parts[0]:
            editable = bmesh.new()
            editable.from_mesh(mesh)
            internal = [
                edge for edge in editable.edges if len(edge.link_faces) == 2
                and all(37. <= v.co.y <= 45.5 for face in edge.link_faces for v in face.verts)
            ]
            # Triangulate the common plane from its border. Interior edges
            # from the old three road owners no longer meet under a wheel.
            bmesh.ops.dissolve_limit(editable, angle_limit=.0009, verts=[],
                                     edges=internal, use_dissolve_boundaries=False)
            editable.to_mesh(mesh)
            editable.free()
            mesh.update()
        obj.data = mesh
    return surface


def fit_spur_paint(obj, old, paved):
    for v in obj.data.vertices:
        if not 30. <= v.co.y <= 46.:
            continue
        ray = Vector((v.co.x, v.co.y, 50))
        previous = old.ray_cast(ray, Vector((0, 0, -1)), 30)[0]
        current = paved.ray_cast(ray, Vector((0, 0, -1)), 30)[0]
        if previous is not None and current is not None:
            v.co.z += current.z - previous.z
    obj.data.update()


def active_west_edge(road, axis, target, style):
    e0,n0=axis[0]; e1,n1=axis[-1]
    heading=Vector((e1-e0,n1-n0,0)).normalized()
    along=lambda p:p.dot(heading)
    flank=Vector((-heading.y,heading.x,0))
    candidates=[]
    for edge in road.data.edges:
        a,b=[road.data.vertices[i].co.copy() for i in edge.vertices]
        direction=b-a
        if 4.8<direction.length<6.2 and abs(direction.normalized().dot(heading))<.32:
            candidates.append((along((a+b)*.5),a,b))
    assert candidates,"the existing west cross-edge must be retained"
    _,a,b=min(candidates,key=lambda edge:edge[0])
    seam=sorted((a,b),key=lambda position:position.dot(flank))
    mid=(seam[0]+seam[1])*.5
    assert (seam[1]-seam[0]).length>4.9, seam
    extend=(mid.x+248.45)/heading.x
    assert 3<extend<13,extend
    m=style['Mesh']('COL_NanquGrade_WestPlayableTie')
    mat=style['material']('Nanqu approach aggregate',(.47,.46,.44),'asphalt_02_diff_1k.jpg')
    rows=[]
    grade=(target(mid.x+.4)-target(mid.x-.4))/.8
    for i in range(9):
        shift=-heading*extend*(1-i/8)
        positions=[p+shift+Vector((0,0,grade*shift.x)) for p in seam]
        rows.append(positions)
    for a,b in zip(rows,rows[1:]):m.face([a[0],b[0],b[1],a[1]],mat)
    return m.save(),[list((a+b)*.5) for a,b in rows]


def junction_apron(point, style):
    from math import cos, sin
    asphalt=style['material']('Nanqu approach aggregate',(.47,.46,.44),'asphalt_02_diff_1k.jpg')
    shape=style['Mesh']('COL_NanquGrade_EastJunctionApron')
    e,n,z=point
    radius=2.62
    ring=[(e+radius*cos(t*pi/12),n+radius*sin(t*pi/12),z+radius*sin(t*pi/12)*.071-.005) for t in range(24)]
    shape.face(ring,asphalt)
    return shape.save()


def north_edge_planting(road_parts, points, targets, style, old):
    trees=[tree(o) for o in road_parts]
    highway=style['Mesh']('COL_NanquGrade_NorthPlanterKerb')
    flowers=style['Mesh']('NanquGrade_NorthRoadsideBlooms')
    fair=style['material']('Nanqu approach pale cast kerb',(.60,.61,.59),'concrete_wall_006_diff_2k.jpg')
    dark=old['tint']('Nanqu upper divider blue-grey',(.082,.193,.264),.22)
    loam=old['tint']('Nanqu verge damp planted soil',(.16,.15,.072))
    palette={'green':[old['tint'](f'Nanqu retained leaf hue {i}',g) for i,g in enumerate(((.074,.20,.045),(.083,.17,.039),(.158,.26,.072),(.088,.22,.072)))],
             'purple':[old['tint'](f'Nanqu roadside bloom {i}',g) for i,g in enumerate(((.63,.05,.25),(.78,.12,.35),(.42,.03,.19)))]}
    def north(e):
        for a,b in zip(points,points[1:]):
            if a[0]<=e<=b[0]:
                u=(e-a[0])/(b[0]-a[0]); return a[1]+u*(b[1]-a[1])
        raise ValueError(e)
    rows=[]
    for i in range(85):
        e=-239+i*.92
        n=north(e)
        derivative=(north(e+.2)-north(e-.2))/.4
        side=Vector((-derivative,1,0)).normalized()
        ray=Vector((e,n,targets(e)+.85))
        hits=[m.ray_cast(ray,Vector((0,0,-1)),2)[0] for m in trees]
        z=max((p.z for p in hits if p is not None),default=targets(e))
        rows.append((Vector((e,n,z)),side))
    random=Random(176034685)
    for (a,na),(b,nb) in zip(rows,rows[1:]):
        def geometry(left,right,z):
            return [a+na*left+Vector((0,0,z)),b+nb*left+Vector((0,0,z)),b+nb*right+Vector((0,0,z)),a+na*right+Vector((0,0,z))]
        highway.solid(geometry(2.78,3.38,-.135),geometry(2.78,3.38,.38),fair)
        highway.solid(geometry(2.84,2.97,.38),geometry(2.84,2.97,.46),dark)
        flowers.face(geometry(3.02,3.35,.412),loam)
        for i in range(12):
            p=a.lerp(b,random.uniform(.04,.98))+na*random.uniform(3.07,3.34)
            p.z+=random.uniform(.41,.62)
            old['flowers'](flowers,p,random,palette,purple=True)
        for i in range(15):
            p=a.lerp(b,random.uniform(.02,.98))+na*random.uniform(2.99,3.35)
            p.z+=random.uniform(.44,.75)
            old['leaf'](flowers,p,random.uniform(0,2*pi),random.uniform(.08,.185),palette['green'][i%4])
    return highway.save(),flowers.save()


def tune_rail_finish(rail):
    touched=set()
    for obj in rail.values():
        for mat in obj.data.materials:
            if mat in touched or not mat.use_nodes: continue
            touched.add(mat)
            node=next((node for node in mat.node_tree.nodes if node.type=='BSDF_PRINCIPLED'),None)
            if node is None: continue
            if 'pale acoustic canopy' in mat.name:
                node.inputs['Emission Color'].default_value=(.62,.66,.63,1)
                node.inputs['Emission Strength'].default_value=.24
            elif 'muted steel box' in mat.name:
                node.inputs['Emission Color'].default_value=(.29,.31,.32,1)
                node.inputs['Emission Strength'].default_value=.15
            elif 'fair-faced concrete' in mat.name:
                node.inputs['Emission Color'].default_value=(.45,.47,.44,1)
                node.inputs['Emission Strength'].default_value=.13


def main():
    controls, output = map(Path,sys.argv[sys.argv.index('--')+1:])
    field=json.loads(controls.read_text())
    output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    city=load(SCENE/'district_patrol/city_and_patrol.blend',ROAD_DONORS)
    approach=load(HERE.parent/'nanqu_04_06_51/nanqu-04-06-51.blend',APPROACH)
    reference=HERE.parent.parent/'riverside/bridge_58_61'
    original=json.loads((reference/'field-controls.json').read_text())
    author=runpy.run_path(str(reference/'build.py'),init_globals={'CQ_RAIL_FUNCTIONS_ONLY':True})
    rail_shift=curve(field['rail_shift_by_north'])
    east_north=original['registered_road_and_rail_east_north']
    source_street=field['existing_58_baseline_game_y']
    north_earth=curve(field['rail_ground_by_north'])
    parts, _, _=author['rail_meshes'](east_north,lambda p:north_earth(p.y),source_street,rail_shift,field['rail_north_join_n'])
    rail={obj.name:obj for obj in parts if obj.name in RAIL}
    for discarded in (obj for obj in parts if obj.name not in RAIL):
        bpy.data.objects.remove(discarded,do_unlink=True)
    connector=load(HERE.parent/'houci_14_16/houci-14-16.blend',SPUR)
    plants=load(HERE.parent/'zhongxing_bridge_18_21/zhongxing-bridge-18-21.blend',('Zhongxing18_ShoulderPlanterBoxes','Zhongxing18_PlantedUpperEdge'))
    all_sources={**city,**approach,**rail,**connector,**plants}
    for obj in all_sources.values(): bake(obj)
    road_surfaces=[obj for name,obj in {**city,**approach,**connector}.items() if name.endswith('_asphalt') or name in ('COL_Nanqu_RaisedWestApproach',SPUR[0])]
    old_table=focus_profile(road_surfaces)
    assert len(old_table)>425, len(old_table)
    baseline=curve(old_table)
    measured=field['road_target_by_east']
    target=curve(measured)
    lift=lambda e:target(e)-baseline(e)
    ground=curve(field['west_terrain_by_east'])
    for name,obj in all_sources.items():
        if name in RAIL:
            continue
        elif name in ('COL_R24_LinkPiers_R24_link_concrete','COL_Houci16_SpurBearings'):
            bounded_height(obj,lift)
        else:
            move(obj,lift)
    pre_merge_road=tree(connector[SPUR[0]])
    spur_merge=shape_spur_merge(connector,field['east_upper_tie'][0],field['east_spur_axis_en'])
    tie=field['east_upper_tie'][0]
    set_spur_slab(connector[SPUR[0]],connector['COL_Houci16_SpurSlab'],
                  elevation=lambda point: merge_level(point.y, point.z, tie))
    west_surface=approach['COL_Nanqu_RaisedWestApproach']
    west_end,west=active_west_edge(west_surface,field['west_visible_tie'],target,author)
    for owner in (west_surface,west_end):
        obj=owner.copy()
        bpy.context.collection.objects.link(obj)
        obj.name='COL_NanquGrade_WestSupportDeck' if owner==west_surface else 'COL_NanquGrade_WestTieSupportDeck'
        set_spur_slab(owner,obj,.58)
        obj.data.materials[0]=author['material']('Nanqu grade warm structural concrete',(.55,.57,.55),'concrete_wall_006_diff_2k.jpg')
    footings=add_west_bearings(west_surface,ground)
    earlier_style=runpy.run_path(str(HERE.parent/'nanqu_04_06_51/build.py'))
    north_edge_planting(road_surfaces,field['western_road_axis_en'],target,author,earlier_style)
    tune_rail_finish(rail)
    planter_floor=tree(approach['COL_Nanqu_RiverFootway'])
    planter_contacts=[]
    for e,n,prior in field['source_planter_contacts']:
        hit=planter_floor.ray_cast(Vector((e,n,prior+lift(e)+.5)),Vector((0,0,-1)),1.)[0]
        if hit is None: raise ValueError(('no sidewalk at retained flowerbox',e,n))
        planter_contacts.append([e,n,hit.z])
    north_n=field['rail_north_join_n']
    levels=lambda n:source_street+42.-.013*(n+175.)+rail_shift(n)
    abutment(north_n,levels,north_earth,east_north,author)
    east=list(east_join(field['east_upper_tie']))
    joined=Vector(east[0][:2])
    earth_east=curve(field['east_join_ground_by_north'])
    east_exit=road_patch('COL_NanquGrade_EastPublicJoin',east,2.58,author,lambda p:earth_east(p.y)-.12,joined)
    incoming=match_incoming(field['east_incoming_join_enu'],spur_merge)
    incoming_earth=curve(field['east_incoming_ground_by_east'])
    east_branch=road_patch('COL_NanquGrade_EastApproachingBranch',incoming,2.55,author,lambda p:incoming_earth(p.x)-.12,joined)
    apron=junction_apron(east[0],author)
    paved=merge_top((connector[SPUR[0]],east_branch,east_exit,apron),east[0])
    fit_spur_paint(connector['Houci16_JointsAndRoadPaint'],pre_merge_road,paved)


    assert len(footings)>=3,footings
    material_keys={}
    for source,obj in all_sources.items():
        runtime=ROAD_DONORS.get(source,source)
        material_keys[runtime]=[slot.material.name if slot.material else None for slot in obj.material_slots]
        # A linked donor can share this name in Blender, so use an unambiguous export name.
        obj.name='Grade__'+runtime
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'nanqu-rail-grade.blend'),compress=True)
    for name,obj in all_sources.items():
        if name in RAIL: continue
        for slot in obj.material_slots:
            prior=slot.material
            if not prior:
                continue
            proxy=bpy.data.materials.get('Grade proxy '+prior.name)
            if proxy is None:
                proxy=bpy.data.materials.new('Grade proxy '+prior.name)
                proxy.diffuse_color=prior.diffuse_color
                proxy.roughness=prior.roughness
            slot.material=proxy
    bpy.ops.export_scene.gltf(filepath=str(output/'nanqu-rail-grade.glb'),export_format='GLB',export_cameras=False,export_lights=False)
    (output/'nanqu-rail-grade.json').write_text(json.dumps({'corrected_meshes':material_keys,
         'planter_contacts':planter_contacts,'use_export_materials':list(RAIL),'old_centre_by_east':old_table,'road_target_by_east':measured,'rail_shift_by_north':field['rail_shift_by_north'],
         'west_bearing_earth_contacts':footings,'north_rail_portal_n':north_n,'east_public_join_enu':east,'east_incoming_join_enu':incoming,'spur_merge':spur_merge,'west_playable_tie_enu':west,
         'notice':'Relative grade in current game ENU. Camera provider Z never used as an absolute game elevation.'},indent=2)+'\n')
    print('Nanqu grade geometry',len(all_sources),len(old_table),'new bearings',len(footings))


main()
