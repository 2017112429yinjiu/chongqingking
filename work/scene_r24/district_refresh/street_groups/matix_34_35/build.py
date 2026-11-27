"""Make public street-edge improvements at two registered Mati Street cameras."""
import json
import os
from pathlib import Path
import runpy
import sys
from math import ceil

import bpy

HERE=Path(__file__).resolve().parent
common=runpy.run_path(str(HERE.parent/"north_edges/build.py"))
Edge,Mesh,material,tint,box=(common[key] for key in ("Edge","Mesh","material","tint","box"))


def materials():
    mats,textures={},{}
    for key,label,color,existing in (
        ("approach","Mati lane grey asphalt",(.69,.68,.65),"asphalt_02_diff_1k.jpg"),
        ("flat","Mati street light split slabs",(.81,.80,.74),"stone_floor_diff_2k.jpg"),
        ("curb","Mati terrace concrete curb",(.73,.71,.64),"concrete_floor_worn_001_diff_2k.jpg"),
        ("base","Mati dark thin brick edging",(.56,.57,.54),"brick_wall_08_diff_2k.jpg"),
        ("retaining","Mati worn mixed retaining stone",(.61,.58,.50),"stone_wall_05_diff_2k.jpg"),
        ("soil","Mati exposed fill behind curb",(.42,.47,.34),"leaf_scattered_gravel_diff_2k.jpg"),
    ):
        mats[key]=material(label,color,existing)
        textures[label]=f"res://assets/chongqing_district_{existing}"
    mats["iron"]=tint("Mati iron rail and gutter channels",(.096,.094,.081))
    mats["wet"]=tint("Mati deep drain recesses",(.068,.068,.057))
    return mats,textures


def fence(edge,plot,a,b,lateral,base,m):
    fence=Mesh(f"Mati{plot}_LaneFenceIron")
    width=.047
    for y in (base+.056,base+.88):
        box(fence,edge,a,b,lateral,lateral+width,y,.046,m["iron"])
    for i in range(ceil((b-a)/.147)):
        s=a+i*.147
        box(fence,edge,s,min(b,s+.023),lateral,lateral+width,base,.96,m["iron"])
    for s in (a,(a+b)/2.,b-.09):
        box(fence,edge,s,s+.085,lateral-.028,lateral+.076,base-.065,1.04,m["iron"])
    return fence.save()


def public_drain(edge,plot,s,lateral,m):
    drain=Mesh(f"Mati{plot}_DrainAndKerb")
    box(drain,edge,s,s+.68,lateral,lateral+.31,.024,.013,m["wet"])
    for i in range(12):
        a=s+.016+i*.055
        box(drain,edge,a,a+.022,lateral+.012,lateral+.295,.034,.016,m["iron"])
    return drain.save()


def build(out):
    field=json.loads((HERE/"field.json").read_text())
    ground=common["terrain"]()
    tiles=list(common["terrain_faces"]())
    m,textures=materials()
    walks={}; new=[]
    for plot,spec in field["public_approach"].items():
        edge=Edge(spec["path"],ground)
        mat=m["approach"] if plot=="34" else m["flat"]
        new.append(edge.strip(f"COL_Mati{plot}_PublicApproach",0.,1.58,.061,tiles,mat,m["curb"]))
        limits=(1.60,10.45) if plot=="34" else (2.65,11.61)
        wall=Mesh(f"COL_Mati{plot}_PublicSideTerrace")
        raised=.59 if plot=="34" else .83
        a,b=limits
        step=.54
        lateral=-.99 if plot=="34" else .96
        for i in range(ceil((b-a)/step)):
            u=a+i*step
            v=min(b,u+step)
            if plot=="34":
                box(wall,edge,u,v,lateral-.33,lateral,-.19,raised+.19,m["base"])
                box(wall,edge,u,v,lateral-.38,lateral+.04,raised,.093,m["curb"])
            else:
                box(wall,edge,u,v,lateral,lateral+.42,-.19,raised+.19,m["retaining"])
                box(wall,edge,u,v,lateral-.035,lateral+.48,raised,.11,m["base"])
        new.append(wall.save())
        new.append(fence(edge,plot,a+.12,b-.09,lateral-.22 if plot=="34" else lateral+.12,raised+.084,m))
        new.append(public_drain(edge,plot,1.30,-.62,m))
        walks[plot]=[edge.at(s,0.,.061) for s in spec["stations"]]
    for obj in list(bpy.data.objects):
        if obj not in new:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    name="mati-34-35"
    source=Path(os.environ.get("CQ_MATI34_35_SOURCE",out/f"{name}.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(out/f"{name}.glb"),export_format="GLB",export_image_format="NONE",
                             export_cameras=False,export_lights=False)
    plan={"retired_plots":[],"retired_objects":[],"new_meshes":[x.name for x in new],"replacement_meshes":[],
          "walks":walks,"surface_textures":textures,"borrowed_materials":{}}
    (out/f"{name}.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n")
    print("CQ_MATI_PUBLIC",json.dumps(walks))


if __name__=="__main__":
    build(Path(sys.argv[-1]).resolve())
