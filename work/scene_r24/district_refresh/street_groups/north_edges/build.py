"""Build three public frontage fragments from registered field-photo sightlines."""
from bisect import bisect_right
from math import ceil
from pathlib import Path
from random import Random
import json
import os
import runpy
import sys

import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
R24=HERE.parents[2]
sys.path[:0]=[str(HERE.parent),str(R24/"district_500")]
from factory import Mesh, terrain
from refresh_geometry import ASSETS,read
from retire_plots import fingerprint, remove_faces
from riverside import make_strip,material,terrain_faces


class Edge:
    def __init__(self, points, ground):
        self.points=[Vector(p) for p in points]
        self.ground=ground
        self.stations=[0.]
        self.axes=[]
        for a,b in zip(self.points,self.points[1:]):
            distance=(b-a).length
            self.stations.append(self.stations[-1]+distance)
            self.axes.append((b-a)/distance)
        self.normals=[Vector((-line.y,line.x)) for line in self.axes]
        self.corners=[self.normals[0]]
        for a,b in zip(self.normals,self.normals[1:]):
            middle=(a+b).normalized()
            self.corners.append(middle/middle.dot(b))
        self.corners.append(self.normals[-1])

    def en(self, station, across):
        i=next((i for i,b in enumerate(self.stations[1:]) if station<b),len(self.axes)-1)
        a,b=self.stations[i:i+2]
        t=(station-a)/(b-a)
        return self.points[i].lerp(self.points[i+1],t)+self.corners[i].lerp(self.corners[i+1],t)*across

    def ground_y(self,p):
        hit=self.ground.ray_cast(Vector((*p,92.)),Vector((0.,0.,-1.)),110.)[0]
        assert hit is not None,tuple(p)
        return hit.z

    def at(self,station,across,lift):
        p=self.en(station,across)
        return (*p,self.ground_y(p)+lift)

    def strip(self,name,lateral,width,thickness,tiles,finish,edge):
        length=self.stations[-1]
        spec={"id":name,"points":[list(self.en(s,lateral)) for s in self.stations],
              "width_m":width,"finish":1,"raise_m":thickness}
        ob=make_strip(spec,tiles,[finish,finish,edge])
        ob.name=name
        return ob

    def walk(self, distance, lateral):
        return self.at(distance,lateral,.047)


def tint(name,rgb,rough=.88):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*rgb,1.)
    mat.roughness=rough
    return mat


def box(mesh,edge,a,b,c,d,base,height,finish):
    low=[edge.at(s,t,base) for s,t in ((a,c),(b,c),(b,d),(a,d))]
    mesh.solid(low,[(x,y,z+height) for x,y,z in low],finish)


def graded_footway(edge, lateral, m):
    """Keep the public through surface above the rough triangulated stock verge."""
    stations = set(edge.stations)
    for a, b in zip(edge.stations, edge.stations[1:]):
        parts = ceil((b-a)/.78)
        stations.update(a+(b-a)*i/parts for i in range(1, parts))
    stations = sorted(stations)
    half = .66
    offsets = [lateral+half*i/4. for i in range(-4, 5)]
    tops = [max(edge.ground_y(edge.en(s, p)) for p in offsets)+.105 for s in stations]
    roadbed = Mesh("COL_North38_Footway")
    for a, b, h0, h1 in zip(stations, stations[1:], tops, tops[1:]):
        low_left, low_right = edge.en(a, lateral-half), edge.en(a, lateral+half)
        high_left, high_right = edge.en(b, lateral-half), edge.en(b, lateral+half)
        roadbed.face([(*low_left,h0),(*high_left,h1),(*high_right,h1),(*low_right,h0)],m["flags"])
        for u, v in ((low_left, high_left), (low_right, high_right)):
            roadbed.face([(*u,edge.ground_y(u)-.055),(*v,edge.ground_y(v)-.055),(*v,h1),(*u,h0)],m["border"])
    for s,h in ((stations[0],tops[0]),(stations[-1],tops[-1])):
        u,v=edge.en(s,lateral-half),edge.en(s,lateral+half)
        roadbed.face([(*u,edge.ground_y(u)-.055),(*v,edge.ground_y(v)-.055),(*v,h),(*u,h)],m["border"])

    def height(station):
        i=min(bisect_right(stations,station)-1,len(stations)-2)
        t=(station-stations[i])/(stations[i+1]-stations[i])
        return tops[i]+t*(tops[i+1]-tops[i])

    return roadbed.save(),height


def seal_street(edge, code, walk_lateral, tiles, m):
    road_width={"38":3.16,"40":2.54,"41":2.78}[code]
    road_offset=-1.45 if code=="40" else 0.
    road=edge.strip(f"COL_North{code}_Street",road_offset,road_width,.021,tiles,m["asphalt"],m["asphalt"])
    if code=="38":
        bank,walking_height=graded_footway(edge,walk_lateral,m)
    else:
        bank=edge.strip(f"COL_North{code}_Footway",walk_lateral,1.32,.047,tiles,m["flags"],m["border"])
        def walking_height(station):
            return edge.walk(station,walk_lateral)[2]
    trim=Mesh(f"North{code}_StoneJointsAndKerb")
    random=Random(int(code))
    joints=Mesh(f"North{code}_StoneFlagJoint")
    for i in range(ceil(edge.stations[-1]/.59)):
        a=i*edge.stations[-1]/ceil(edge.stations[-1]/.59)
        b=min(edge.stations[-1],(i+1)*edge.stations[-1]/ceil(edge.stations[-1]/.59))
        margin=walk_lateral+(-.62 if walk_lateral>0 else .62)
        c,d=sorted((margin,margin+(.08 if walk_lateral>0 else -.08)))
        if code=="38":
            da,db=walking_height(a),walking_height(b)
            vertices=[(*edge.en(s,t),y) for s,t,y in ((a,c,da),(b,c,db),(b,d,db),(a,d,da))]
            trim.solid(vertices,[(x,y,z+.064) for x,y,z in vertices],m["red"])
        else:
            box(trim,edge,a,b,c,d,.016,.060,m["border"])
        if i==0:
            continue
        mid=walk_lateral+random.uniform(-.13,.14)
        for u,v in ((walk_lateral-.58,mid),(mid+.012,walk_lateral+.58)):
            points=[(*edge.en(s,t),walking_height(s)+.0025) for s,t in ((a,u),(a+.007,u),(a+.007,v),(a,v))] if code=="38" else [edge.at(s,t,.050) for s,t in ((a,u),(a+.007,u),(a+.007,v),(a,v))]
            joints.face(points,m["joint"])
    return [road,bank,trim.save(),joints.save()],walking_height


def shutters_38(edge,m):
    body=Mesh("COL_North38_StreetFacade")
    finish=Mesh("North38_ShuttersRevealsAndBays")
    rng=Random(38009940)
    # A narrow outdoor elevation marks the recorded shutter frontage. No room
    # geometry or invented entrance connects to the neighboring household.
    left,right=21.0,30.25
    width=(right-left)/3
    for k in range(3):
        a,b=left+k*width,left+(k+1)*width
        base=.065
        box(body,edge,a,b,2.85,3.13,base,3.08,m["brick"][k])
        box(finish,edge,a+.18,b-.13,2.78,2.86,.16,2.30,m["recess"])
        for band in range(25):
            lift=.21+.083*band
            box(finish,edge,a+.29,b-.23,2.744,2.773,lift,.061,m["shutter"][k])
        for x in (a+.16,b-.20):
            box(finish,edge,x,x+.065,2.697,2.78,.13,2.44,m["stone"])
        box(finish,edge,a-.045,b+.04,2.32,2.89,2.64,.11,m["stone"])
        box(finish,edge,a,b,2.36,2.53,2.55,.12,m["oxide"])
        if k==2:
            continue
        for lvl in (3.62,6.20):
            box(body,edge,a,b,2.86,3.17,lvl-.57,2.50,m["lived"][k])
            box(finish,edge,a+.35,b-.34,2.63,2.86,lvl+.09,1.35,m["recess"])
            box(finish,edge,a+.31,b-.3,2.48,2.86,lvl-.015,.21,m["stone"])
            for idx in range(6):
                x=a+.43+idx*.35
                box(finish,edge,x,x+.026,2.56,2.595,lvl+.19,1.12,m["metal"])
            box(finish,edge,a+.37,b-.33,2.555,2.60,lvl+.39,.026,m["metal"])
            if lvl<5:
                x=a+.68+rng.uniform(-.18,.15)
                box(finish,edge,x,x+.44,2.59,2.74,lvl+.56,.42,m["curtain"])
    return [body.save(),finish.save()]


def stone_wall(edge, code, start, stop, side, palette, m):
    rng=Random(int(code)*513)
    shell=Mesh(f"COL_North{code}_PublicRetaining")
    front=Mesh(f"North{code}_CoursesAndWeathering")
    crown=Mesh(f"North{code}_WallCoping")
    top=1.72 if code=="40" else 3.10
    courses=4 if code=="40" else 7
    course_height=.39
    for i in range(ceil((stop-start)/.80)):
        a=start+i*.80;b=min(stop,a+.80)
        box(shell,edge,a,b,side,side+.37,-.16,top+.11,m["core"])
        box(crown,edge,a,b,side-.035,side+.44,top-.04,.12,m["stone"])
    for row in range(courses):
        a=start
        lift=.07+row*course_height
        while a<stop-.10:
            width=rng.uniform(.53,1.27)
            b=min(a+width,stop)
            if stop-b<.25:
                b=stop
            face=side-rng.uniform(.017,.077)
            mat=palette[rng.choices(range(len(palette)),[5,4,3,1])[0]]
            box(front,edge,a+.012,b-.009,face,side+.035,lift+rng.uniform(-.02,.013),
                .363+rng.uniform(-.022,.012),mat)
            a=b
    if code=="41":
        for i in range(ceil((stop-start)/.63)):
            a=start+i*.63;b=min(stop,a+.63)
            if b-a<.28: break
            for lo,hi in ((a,a+.16),(b-.135,b)):
                box(crown,edge,lo,hi,side-.015,side+.41,top+.065,.38,m["core"])
            box(crown,edge,a,b,side-.027,side+.415,top+.43,.13,m["stone"])
        exhibit=Mesh("North41_HistoricDisplayWall")
        for i in range(3):
            a=stop-3.4+i*1.07;b=a+1.00
            box(exhibit,edge,a+.085,b-.075,side-.18,side-.122,.79,1.04,m["poster"])
            for z in (.68,1.04,1.88):
                box(exhibit,edge,a,b,side-.223,side-.18,z,.043,m["red_lacquer"])
            for j in range(5):
                s=a+j*.245
                box(exhibit,edge,s,s+.038,side-.225,side-.18,.70,1.20,m["red_lacquer"])
        return [shell.save(),front.save(),crown.save(),exhibit.save()]
    return [shell.save(),front.save(),crown.save()]


def main(output):
    field=read(HERE/"field.json")
    stock=terrain()
    tiles=list(terrain_faces())
    ac=runpy.run_path(str(HERE.parent/"panda_15_17/build.py"))
    replace=runpy.run_path(str(R24/"district_refresh/riverside/east_bend/build.py"))
    materials={}
    textures={}

    def textured(key,name,rgb,asset):
        mat=material(name,rgb,asset)
        materials[key]=mat
        textures[name]=f"res://assets/chongqing_district_{asset}"
        return mat

    for key,label,color,filename in (
        ("asphalt","North lane small aggregate",(.67,.67,.65),"asphalt_02_diff_1k.jpg"),
        ("flags","North lane split stone flag",(.76,.75,.68),"stone_floor_diff_2k.jpg"),
        ("border","North lane curb limestone",(.69,.69,.65),"concrete_floor_worn_001_diff_2k.jpg"),
        ("red","North lane clay-red edging",(.53,.29,.235),"brick_wall_08_diff_2k.jpg"),
        ("stone","North lane ashlar top",(.81,.77,.65),"concrete_floor_worn_001_diff_2k.jpg"),
        ("core","North lane dark joint mortar",(.45,.44,.39),"stone_wall_05_diff_2k.jpg")):
        textured(key,label,color,filename)
    mats=materials
    bricks=[(.69,.63,.55),(.76,.70,.59),(.66,.61,.54)]
    mats["brick"]=[textured(f"brick{i}",f"North38 narrow springing brick {i}",color,"brick_wall_08_diff_2k.jpg")
                   for i,color in enumerate(bricks)]
    mats["lived"]=[textured(f"render{i}",f"North38 old concrete render {i}",color,"concrete_wall_006_diff_2k.jpg")
                   for i,color in enumerate(((.84,.81,.74),(.68,.67,.61)))]
    flags=[(.76,.73,.64),(.65,.60,.51),(.80,.73,.58),(.53,.581,.49)]
    stone=[textured(f"ash{i}",f"North public coursed ashlar {i}",color,"stone_wall_05_diff_2k.jpg")
           for i,color in enumerate(flags)]
    mats.update({a:tint(b,c) for a,b,c in (
        ("joint","North paving fine joint",(.182,.176,.151)),("recess","North38 shutter pocket",(.11,.101,.082)),
        ("metal","North38 oxidized window guard",(.162,.154,.132)),("oxide","North38 shutter lintel oxide",(.285,.173,.109)),
        ("curtain","North38 faded curtain",(.42,.256,.186)),("poster","North41 quiet panel",(.33,.30,.245)),
        ("red_lacquer","North41 red painted panel",(.32,.039,.031)))})
    mats["shutter"]=[tint(f"North38 shutter color {i}",c)
                     for i,c in enumerate(((.34,.342,.307),(.27,.256,.213),(.41,.376,.31)))]
    station_40=next(row["en"] for row in field["records"] if row["pano"]=="0902920012230515132237063AU")
    chosen={"38":list(reversed([x["east_north"] for x in field["road_chains"]["38"]["stations"]])),
            "40":[station_40]+[x["east_north"] for x in reversed(field["road_chains"]["40"]["stations"][:])][:3],
            "41":[x["east_north"] for x in field["road_chains"]["41"]["stations"][:4]]}
    additions=[]
    paths={}
    for code,seq in chosen.items():
        edge=Edge(seq,stock)
        lateral={"38":-2.04,"40":.54,"41":1.93}[code]
        street,walking_height=seal_street(edge,code,lateral,tiles,mats)
        additions.extend(street)
        if code=="38":
            additions.extend(shutters_38(edge,mats))
        elif code=="40":
            warm=[textured(f"wall40_{i}",f"North40 faded pink stone {i}",color,"stone_wall_05_diff_2k.jpg")
                  for i,color in enumerate(((.83,.69,.56),(.72,.58,.49),(.86,.72,.62),(.54,.47,.39)))]
            additions.extend(stone_wall(edge,code,.64,21.3,1.39,warm,mats))
        else:
            additions.extend(stone_wall(edge,code,8.75,23.4,2.70,stone,mats))
        marks={"38":[10.5,14.,17.,20.3,23.5,27.1,29.9],
               "40":[25.,21.5,17.2,13.1,9.5,6.4],
               "41":[1.7,5.6,9.4,12.4,15.5,18.4,21.6]}[code]
        paths[code]=[(*edge.en(st,lateral),walking_height(st)) for st in marks]
    replacements,retired,counts=ac["retire"](replace,(38,),HERE/"ownership.json")
    cut=field["old_40_foundation_projection"]
    label=cut["mesh"]
    owner=read(HERE/"ownership.json")["40"][label]
    expected=set(cut["fingerprints"])
    assert expected <= {key for block in owner for key in block["faces"]}
    envelope=next(obj for obj in replacements if obj.name==label or obj.name.startswith(label+"."))
    faces=[face.index for face in envelope.data.polygons if fingerprint(envelope,face) in expected]
    assert len(faces)==len(expected),(label,faces)
    remove_faces(envelope,faces)
    counts[label]+=len(faces)
    plan={"retired_plots":[38],"retired_objects":retired,"replacement_meshes":[r.name for r in replacements],
          "new_meshes":[a.name for a in additions],"affected_faces":counts,"walks":paths,"surface_textures":textures}
    parent=read(ASSETS/"changbin-55.json")["borrowed_materials"]
    plan["borrowed_materials"]={}
    for obj in replacements:
        present={m.name for m in obj.data.materials}
        plan["borrowed_materials"][obj.name]={alias:name for alias,name in parent[obj.name].items() if alias in present}
    for obj in list(bpy.data.objects):
        if obj not in set((*replacements,*additions)):
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    for mesh in (*replacements,*additions):
        for slot in mesh.material_slots:
            if slot.material and slot.material.library:
                slot.material=slot.material.make_local()
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    source=Path(os.environ.get("CQ_NORTH_EDGES_SOURCE",output/"north-38-40-41.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=True)
    bpy.ops.export_scene.gltf(filepath=str(output/"north-38-40-41.glb"),export_format="GLB",export_image_format="NONE",
                              export_cameras=False,export_lights=False)
    (output/"north-38-40-41.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n")
    print("CQ_NORTH_EDGES",counts,paths)


if __name__=="__main__":
    main(Path(sys.argv[-1]).resolve())
