"""Build the registered Binjiang tower, its public apron and the adjoining curved frontage."""
from collections import Counter
import json
from math import sin, pi
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(SCENE/"district_500"), str(SCENE/"district_refresh/street_groups")]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, read
from retire_plots import fingerprint, remove_faces
from riverside import make_strip, terrain_faces

def ring_ccw(points):
    values=[Vector(p) for p in points]
    area=sum(a.x*b.y-b.x*a.y for a,b in zip(values,values[1:]+values[:1]))
    return values if area>0 else values[::-1]

def inside(p, ring):
    crossings=(a.x+(p.y-a.y)*(b.x-a.x)/(b.y-a.y) for a,b in zip(ring,ring[1:]+ring[:1])
               if (a.y>p.y)!=(b.y>p.y))
    return sum(p.x<x for x in crossings)%2==1

def slab(mesh, points, z, top, finish):
    mesh.solid([(*p,z) for p in points],[(*p,top) for p in points],finish)

def bar(mesh, a, axis, normal, l, r, near, depth, low, high, finish):
    corners=[a+axis*x+normal*y for x,y in ((l,near),(r,near),(r,depth),(l,depth))]
    slab(mesh,corners,low,high,finish)

def axes(ring):
    for a,b in zip(ring,ring[1:]+ring[:1]):
        axis=(b-a).normalized()
        yield a,axis,Vector((-axis.y,axis.x)),(b-a).length

def plain(name, rgb, roughness=.58):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*rgb,1.)
    mat.use_nodes=True
    shader=mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value=mat.diffuse_color
    shader.inputs["Roughness"].default_value=roughness
    return mat

def podium(ring,levels,m):
    floors=Mesh("COL_Binjiang_1128648941_Podium")
    detail=Mesh("Binjiang_Podium_Stone_Piers_Glazing")
    contents=Mesh("Binjiang_Recessed_Landing_And_Louvres")
    slab(floors,ring,1.9,levels[0],m["foot"])
    for z in levels[1:]:
        slab(floors,ring,z-.195,z,m["sand"])
    for side,(a,t,n,length) in enumerate(axes(ring)):
        count=max(2,round(length/3.35))
        pitch=length/count
        for j in range(count+1):
            u=j*pitch
            lo,hi=max(0,u-.27),min(length,u+.27)
            bar(floors,a,t,n,lo,hi,-.15,.47,levels[0]-.06,levels[-1]+.66,m["pier"])
            bar(detail,a,t,n,lo+.03,hi-.03,-.19,-.146,levels[0]+.09,levels[-1]+.48,m["sand"])
        for floor,(z,next_z) in enumerate(zip(levels,levels[1:])):
            for bay in range(count):
                l,r=bay*pitch+.28,(bay+1)*pitch-.28
                north=-n.y>.46
                low_opening=floor<2 and not north
                bar(floors,a,t,n,l,r,.025,.38,z+.02,z+(.32 if north and floor==2 else .47),m["foot"] if floor==0 else m["sand"])
                bar(detail,a,t,n,l,r,.03,.47,next_z-.69,next_z-.075,m["sand"])
                if low_opening or (not north and floor in (2,3) and bay%5 in (1,2)):
                    # The outdoor garage bay can be seen to its recessed shadow wall.
                    bar(floors,a,t,n,l+.01,r-.01,2.1,2.22,z+.3,next_z-.65,m["recess"])
                    for stripe in range(3):
                        h=z+.69+stripe*.135
                        bar(contents,a,t,n,l+.06,r-.06,.36,.405,h,h+.035,m["rail"])
                else:
                    recess=.36 if north and floor==2 and bay in (2,3,4,5) else .49
                    bottom=z+(.105 if north and floor==2 else .50)
                    bar(floors,a,t,n,l,r,recess,recess+.03,bottom,next_z-.67,m["blue"] if (bay+floor)%4 else m["teal"])
                    for section in (0.0,.33,.67,1.):
                        u=l+section*(r-l)
                        bar(detail,a,t,n,u-.026,u+.026,recess-.02,recess+.043,bottom,next_z-.67,m["rail"])
                    if north and floor==2:
                        bar(detail,a,t,n,l+.18,r-.18,-.09,.02,next_z-.70,next_z-.31,m["sign"] if bay%3==1 else m["lintel"])
                        bar(detail,a,t,n,l+.40,l+.43,recess-.055,recess-.015,bottom+.61,bottom+1.02,m["pier"])
        bar(floors,a,t,n,0.,length,-.02,.30,levels[-1],levels[-1]+.27,m["pier"])
    return [x.save() for x in (floors,detail,contents)]

def tower(name,ring,bottom,count,height,m,style):
    body=Mesh(name)
    centre=sum(ring,Vector((0,0)))/len(ring)
    # An inset high-rise sits over the photographed lower street envelope.
    plate=[centre+(p-centre)*(.79 if style=="sand" else .66) for p in ring]
    top=bottom+count*height
    for side,(a,t,n,length) in enumerate(axes(plate)):
        count_bays=max(2,round(length/(2.74 if style=="sand" else 2.93)))
        bay=length/count_bays
        for k in range(count):
            low=bottom+k*height
            band=.63 if style=="sand" else .74
            bar(body,a,t,n,0.,length,0,.25,low,low+band,m["sand"] if style=="sand" else m["brick"])
            for j in range(count_bays):
                u=j*bay
                ribbon=(style=="sand" and side in (1,3,4) and j in (count_bays//3,count_bays//3+1))
                rib=.17 if not ribbon else .10
                structural=m["pier"] if style=="sand" and j%4==0 else m[style]
                bar(body,a,t,n,u,u+rib,-.10,.28,low+band,low+height,structural)
                bar(body,a,t,n,u+bay-rib,u+bay,-.025,.25,low+band,low+height,structural)
                opening=m["teal"] if ribbon else [m["blue"],m["greyblue"],m["dimblue"]][(j*3+k+side)%3]
                bar(body,a,t,n,u+rib,u+bay-rib,.24,.29,low+band,low+height,opening)
                if not ribbon:
                    u2=u+bay*(.46 if (j+side)%2 else .53)
                    bar(body,a,t,n,u2-.025,u2+.025,.19,.245,low+band,low+height,m["rail"])
                if style=="brick" and j%3!=1:
                    bar(body,a,t,n,u+.10,u+bay-.10,-.37,.05,low+band,low+band+.135,m["brick"])
            if k%9==8 or k==count-1:
                bar(body,a,t,n,0.,length,-.15,.25,low+height-.15,low+height,m["pier"] if style=="sand" else m["brick"])
        bar(body,a,t,n,0.,length,-.04,.41,top,top+.92,m[style])
    slab(body,plate,top-.13,top+.10,m["foot"])
    inset=[centre+(p-centre)*(.49) for p in plate]
    slab(body,inset,top+.10,top+2.08,m[style])
    return body.save(),plate,top

def curved_neighbor(corners,m):
    northwest,northeast,*south=corners
    east=northeast-northwest
    edge=[northwest.lerp(northeast,i/14)+Vector((0,2.18*sin(pi*i/14))) for i in range(15)]
    ring=ring_ccw(edge+south)
    floor=Mesh("COL_Binjiang_704006726_Curved_Podium")
    fronts=Mesh("Binjiang_Salmon_Arc_Windows_And_Grilles")
    levels=(1.0,4.28,7.56,10.81,14.08,17.43,20.54)
    slab(floor,ring,-.65,1.,m["foot"])
    for z in levels[1:]:
        slab(floor,ring,z-.2,z,m["brick"])
    for a,t,n,L in axes(ring):
        public=-n.y>.54
        count=max(1,round(L/4.4))
        bay=L/count
        for k,(low,high) in enumerate(zip(levels,levels[1:])):
            for j in range(count):
                u=j*bay
                width=.29 if public else .37
                bar(floor,a,t,n,u,min(u+width,L),-.045,.48,low,high,m["brick"])
                bar(floor,a,t,n,max(0,u+bay-width),u+bay,-.045,.48,low,high,m["brick"])
                bar(floor,a,t,n,u+width,u+bay-width,.03,.48,low,low+(.46 if public else .69),m["brick"])
                bar(fronts,a,t,n,u+width,u+bay-width,-.21,.42,high-.55,high+.08,m["coping"])
                glass=public and k>=2 and k!=3
                set_back=.24 if glass else (1.23 if public and k==3 else 2.64)
                bar(floor,a,t,n,u+width,u+bay-width,set_back,set_back+.035,
                    low+.62,high-.53,m["greyblue"] if glass else m["recess"])
                if glass:
                    for s in (.25,.5,.75):
                        x=u+s*bay
                        bar(fronts,a,t,n,x-.025,x+.025,.195,.235,low+.62,high-.54,m["rail"])
        if public:
            bar(floor,a,t,n,0.,L,-.14,.63,levels[-1],levels[-1]+.63,m["coping"])
            bar(fronts,a,t,n,.12,L-.12,.22,.63,levels[-1]+.47,levels[-1]+.71,m["leaf"])
    return [floor.save(),fronts.save()],levels[-1],ring

def paving(site, tiles, ground, m, previous):
    project=runpy.run_path(str(HERE.parent/"park_plot59/build.py"),run_name="park_projection")
    plot_paths={}
    pieces=[]
    landings=Mesh("Binjiang_Stone_Entrance_Aprons")
    areas={
      "70":[[80.5,-115.2],[97.7,-116.6],[101.2,-109.6],[96.8,-106.2],[86.2,-108.2]],
      "71":[[98.5,-139.7],[105.5,-141.3],[111.9,-134.5],[110.6,-119.8],[105.7,-112.0],[100.0,-114.7]],
      "72":[[111.5,-135.0],[115.8,-139.6],[122.2,-139.35],[126.0,-133.1],[124.3,-116.0],[120.8,-110.0],[117.0,-113.3]],
      "73":[[136.3,-134.35],[140.2,-137.6],[147.0,-137.4],[151.0,-134.8],[152.25,-129.95],[150.25,-126.8],[149.55,-119.8],[145.2,-117.3],[140.25,-121.0]],
    }
    area={}
    for key,shape in areas.items():
        area[key]=project["project"](landings,project["triangle_parts"](shape),tiles,previous,m["pavers"],lift=.045)
        assert area[key]>25.,(key,area[key])
    pieces.append(landings.save())
    frontage=[[96.78,-106.35],[98,-106.6],[103.5,-107.61],[108,-108.6],[115.2,-109.62],
              [120.9,-111],[128.6,-113.08],[137.95,-115.82],[144.7,-118.15],[149.4,-119.39]]
    street=make_strip({"id":"COL_Binjiang_Jiefang_South_Sidewalk","points":frontage,"width_m":2.15,
                       "finish":0,"raise_m":.053},tiles,[m["pavers"],m["pavers"],m["edge"]])
    pieces.append(street)
    for key,value in site["public_routes"].items():
        stations=value["stations"]
        # Extend a short stone landing past both checks, so the test begins and turns within paving.
        vec=list(map(Vector,stations))
        trace=[list(vec[0]+(vec[0]-vec[1]).normalized()*.67),*stations,
               list(vec[-1]+(vec[-1]-vec[-2]).normalized()*.68)]
        piece=make_strip({"id":"COL_Binjiang_Walk_"+key,"points":trace,"width_m":2.52 if key in ("70","73") else 2.32,
                          "finish":0,"raise_m":.067},tiles,[m["pavers"],m["pavers"],m["edge"]])
        piece.name="COL_Binjiang_Walk_"+key
        pieces.append(piece)
        plot_paths[key]={**value,"start_ground_m":ground(vec[0])+.067,"destination_game_m":ground(vec[-1])+.067}
    return pieces,plot_paths,area

def sill_landing(m,ground):
    # The public path stops north of the photographed shop doors.
    mesh=Mesh("COL_Binjiang_Podium_Sill_Landing")
    back=(Vector((83.2,-114.82)),Vector((86.17,-115.30)))
    front=(Vector((83.2,-113.25)),Vector((86.17,-113.72)))
    height=7.91
    mesh.face([(*front[1],ground(front[1])+.053),(*front[0],ground(front[0])+.053),
               (*back[0],height),(*back[1],height)],m["edge"])
    mesh.face([(*back[0],height),(*back[0],ground(back[0])-.13),(*front[0],ground(front[0])-.13),
               (*front[0],ground(front[0])+.053)],m["foot"])
    mesh.face([(*front[1],ground(front[1])+.053),(*front[1],ground(front[1])-.13),(*back[1],ground(back[1])-.13),
               (*back[1],height)],m["foot"])
    return mesh.save()

def build(tmp):
    assert Path(bpy.data.filepath).name in ("city_and_outer.local.blend","city_and_outer.before_binjiang.local.blend")
    site=read(HERE/"site.json")
    meta=read(HERE/"retired-faces.json")
    old=runpy.run_path(str(HERE.parent/"east_bend/build.py"),run_name="shared_source")
    prior=runpy.run_path(str(HERE.parent/"plots_63_66/build.py"),run_name="road_surface_tools")
    writer=runpy.run_path(str(HERE.parent/"park_edge_finish/build.py"),run_name="image_writer")["png"]
    reused={
      "sand":("Binjiang pale honey limestone","concrete_wall_006_diff_2k.jpg",(187,174,143)),
      "pier":("Binjiang pale limestone trim","concrete_wall_006_diff_2k.jpg",(204,193,169)),
      "foot":("Binjiang textured stone base","stone_wall_05_diff_2k.jpg",(117,111,96)),
      "brick":("Binjiang adjacent red brown veneer","brick_wall_08_diff_2k.jpg",(160,112,94)),
      "coping":("Binjiang red podium coping","concrete_wall_006_diff_2k.jpg",(143,91,76)),
      "pavers":("Binjiang grey entry flags","stone_floor_diff_2k.jpg",(139,142,143)),
      "edge":("Binjiang warm paving edge","concrete_wall_006_diff_2k.jpg",(176,174,166)),
    }
    m={slot:prior["tinted_material"](*spec,tmp,writer) for slot,spec in reused.items()}
    for key,name,col,rough in (("teal","Blue green window ribbons",(.076,.172,.191),.27),
              ("blue","Shaded blue glass",(.078,.111,.148),.27),("greyblue","Silver grey glazing",(.143,.185,.20),.33),
              ("dimblue","Light muted blue glass",(.118,.153,.174),.34),("recess","Recessed structural shade",(.077,.069,.062),.90),
              ("rail","Dark bronze glazing mullions",(.062,.067,.069),.46),
              ("sign","Muted red shop fascia",(.26,.063,.036),.60),("lintel","Stone lintels",(.32,.268,.215),.81),
              ("leaf","Podium parapet low planting",(.102,.147,.061),.89)):
        m[key]=plain("Binjiang "+name,col,rough)
    original=terrain()
    tiles=list(terrain_faces())
    def ground(p):
        at,_,_,_=original.ray_cast(Vector((*p,42.)),Vector((0,0,-1)),90.)
        assert at is not None,list(p)
        return at.z
    scene=bpy.context.scene
    replacements=[]
    for name,keys in meta["faces"].items():
        replacement=old["local_copy"](scene.objects[name])
        targets=Counter(keys)
        indices=[p.index for p in replacement.data.polygons if fingerprint(replacement,p) in targets]
        assert Counter(fingerprint(replacement,replacement.data.polygons[i]) for i in indices)==targets,name
        remove_faces(replacement,indices)
        replacements.append(replacement)
    tower_ring=ring_ccw(site["ways"]["1128648941"]["east_north"][:-1])
    neighbor_corners=list(map(Vector,site["ways"]["704006726"]["east_north"][:-1]))
    level=(3.17,5.72,7.91,10.82,13.95,17.25)
    objects=podium(tower_ring,level,m)
    high,r0,roof=tower("Binjiang_Tower_1128648941",tower_ring,level[-1],35,3.16,m,"sand")
    objects.append(high)
    others,z,body=curved_neighbor(neighbor_corners,m)
    objects.extend(others)
    high_other,r1,roof_other=tower("Binjiang_Adjacent_Tower_704006726",ring_ccw(neighbor_corners),z,23,2.84,m,"brick")
    objects.append(high_other)
    paths,route_records,areas=paving(site,tiles,ground,m,[])
    objects.extend(paths+[sill_landing(m,ground)])
    retired=set(meta["retired_objects"])|{"COL_EastGarage_StreetFrontage68","EastGarage_StreetFrontageLouvers68"}
    vegetation=[]
    for ob in scene.objects:
        root=ob.matrix_world.translation.xy
        if ob.name.startswith("Outer500_Plant_") and any(inside(root,ring) for ring in (tower_ring,body)):
            vegetation.append(ob.name)
    retired.update(vegetation)
    assert all(ob in scene.objects for ob in retired)
    # The old East Bend frontage served as a proxy for the same building. Preserve the adjacent walkway and ramps.
    keep=set(objects+replacements)
    for ob in list(bpy.data.objects):
        if ob not in keep:
            bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"binjiang-70-73.blend"),relative_remap=True,compress=True)
    preceding=read(ASSETS/"raijiapo-east-bend.json")["borrowed_materials"]
    donors={name:set(slots.values()) for name,slots in preceding.items()}
    slots=old["borrow_slots"](replacements,donors)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/"binjiang-70-73.glb"),export_format="GLB",export_cameras=False,export_lights=False)
    record={"retired_plots":[70,71,72,73],"retired_objects":sorted(retired),"replacement_meshes":[o.name for o in replacements],
            "new_meshes":[o.name for o in objects],"borrowed_materials":slots,"public_routes":route_records,
            "retired_runtime_frontage":site["retired_runtime_frontage"],
            "terrace_area_m2":areas,"render_buildings":{"1128648941":{"walkable_levels":list(level),"top_m":roof,"tower_plan":[list(p) for p in r0]},
                    "704006726":{"podium_roof":z,"top_m":roof_other,"tower_plan":[list(p) for p in r1]}},
            "plant_roots_inside_new_building":vegetation,"removed_face_counts":{n:len(v) for n,v in meta["faces"].items()}}
    (ASSETS/"binjiang-70-73.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n")
    print("CQ_BINJIANG_BUILD",len(objects),len(replacements),areas,roof,roof_other,vegetation)

if __name__=="__main__":
    with TemporaryDirectory() as tmp:
        build(Path(tmp))
