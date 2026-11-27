"""Add only the registered public frontage and lane head along Liangtingzi."""
from math import ceil
from pathlib import Path
import json
import os
import runpy
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
common = runpy.run_path(str(HERE.parent / "north_edges/build.py"))
Edge, Mesh, ground_field = (common[x] for x in ("Edge", "Mesh", "terrain"))
make_material, tint, box = (common[x] for x in ("material", "tint", "box"))


def make_materials():
    textures, finishes = {}, {}
    specifications = (
        ("flag", "Liangtingzi grey split stone paving", (.78,.77,.73), "stone_floor_diff_2k.jpg"),
        ("kerb", "Liangtingzi light cut stone edging", (.70,.71,.68), "concrete_floor_worn_001_diff_2k.jpg"),
        ("brick", "Liangtingzi blue-grey stone fence base", (.48,.50,.49), "brick_wall_08_diff_2k.jpg"),
        ("step", "Liangtingzi pale step tread", (.76,.77,.72), "concrete_floor_worn_001_diff_2k.jpg"),
        ("concrete", "Liangtingzi worn descending concrete", (.60,.64,.59), "concrete_floor_worn_001_diff_2k.jpg"),
        ("planting", "Liangtingzi soil in shaded pits", (.35,.43,.29), "leaf_scattered_gravel_diff_2k.jpg"),
    )
    for key, label, color, texture in specifications:
        finishes[key] = make_material(label, color, texture)
        textures[label] = f"res://assets/chongqing_district_{texture}"
    finishes["fence"] = tint("Liangtingzi oxide red closed boundary", (.22,.075,.055))
    finishes["joint"] = tint("Liangtingzi damp stone joints", (.19,.19,.16))
    return finishes, textures


def frontage(edge, tiles, m):
    stones = edge.strip("COL_Liangtingzi45_PublicFlags", 0., 1.76, .053, tiles, m["flag"], m["kerb"])
    rim = Mesh("Liangtingzi45_PavingRimAndJoints")
    fence = Mesh("COL_Liangtingzi45_PublicSideFence")
    uprights = Mesh("Liangtingzi45_RustMetalUprights")
    for k in range(ceil((edge.stations[-1]-1.)/.53)):
        a = .38+k*.53
        b = a+.53
        box(rim,edge,a,b,.83,.98,.015,.123,m["kerb"])
        box(rim,edge,a+.48,a+.488,-.73,.77,.054,.003,m["joint"])
    for a,b in ((3.12,6.91),(6.91,10.72),(10.72,12.18)):
        box(fence,edge,a,b,-1.50,-1.12,-.16,.60,m["brick"])
        box(fence,edge,a-.055,b+.045,-1.55,-1.075,.44,.095,m["kerb"])
        box(fence,edge,a-.128,a+.145,-1.63,-1.045,.40,1.48,m["brick"])
        box(fence,edge,a-.186,a+.183,-1.68,-1.005,1.86,.105,m["kerb"])
        box(uprights,edge,a+.19,b-.11,-1.36,-1.314,.61,.043,m["fence"])
        box(uprights,edge,a+.19,b-.11,-1.36,-1.314,1.35,.040,m["fence"])
        for k in range(ceil((b-a-.30)/.155)):
            st=a+.20+k*.155
            box(uprights,edge,st,st+.027,-1.36,-1.315,.53,.94,m["fence"])
    for s in (4.7,9.35):
        box(rim,edge,s-.45,s+.45,-1.03,-.76,.012,.13,m["kerb"])
        box(rim,edge,s-.45,s+.45,-1.28,-1.02,.035,.044,m["planting"])
    return [stones,rim.save(),fence.save(),uprights.save()]


def descent(edge, tiles, m):
    paving = edge.strip("COL_Liangtingzi46_PublicDescent", 0., 1.62, .063, tiles, m["concrete"], m["kerb"])
    returns = Mesh("COL_Liangtingzi46_LaneEdgeParapet")
    stair = Mesh("COL_Liangtingzi46_SeparateStoneStair")
    cap = Mesh("Liangtingzi46_WornStoneReturns")
    for i in range(16):
        a=.70+i*.60
        b=a+.60
        box(returns,edge,a,b,-1.045,-.82,-.12,.91,m["brick"])
        box(cap,edge,a,b,-1.10,-.76,.77,.105,m["kerb"])
    for i in range(8):
        a=1.2+i*.34
        b=a+.34
        left,right=.92,1.97
        p=edge.en((a+b)*.5,(left+right)*.5)
        height=edge.ground_y(p)+.16
        top=[(*edge.en(s,t),height) for s,t in ((a,left),(b,left),(b,right),(a,right))]
        stair.solid([(x,y,z-.46) for x,y,z in top],top,m["step"])
        ledge=[(*edge.en(s,t),height+.004) for s,t in ((b-.043,left),(b,left),(b,right),(b-.043,right))]
        cap.face(ledge,m["joint"])
    return [paving,returns.save(),stair.save(),cap.save()]


def build(output):
    field=json.loads((HERE/"field.json").read_text())
    field_terrain=ground_field()
    cache=list(common["terrain_faces"]())
    mats,textures=make_materials()
    layer, routes=[],{}
    for key, method, rise in (("45",frontage,.053),("46",descent,.063)):
        shape=field["geometry"][key]
        edge=Edge(shape["path"],field_terrain)
        layer.extend(method(edge,cache,mats))
        routes[key]=[edge.at(station,0.,rise) for station in shape["marks"]]
    retained=set(layer)
    for obj in list(bpy.data.objects):
        if obj not in retained:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    name="liangtingzi-45-46"
    source=Path(os.environ.get("CQ_LIANGTINGZI_SOURCE",output/f"{name}.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(output/f"{name}.glb"),export_format="GLB",export_image_format="NONE",
                             export_cameras=False,export_lights=False)
    plan={"retired_plots":[],"retired_objects":[],"new_meshes":[x.name for x in layer],"replacement_meshes":[],
          "walks":routes,"surface_textures":textures,"borrowed_materials":{}}
    (output/f"{name}.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n")
    print("CQ_LIANGTINGZI",json.dumps(routes))


if __name__ == "__main__":
    build(Path(sys.argv[-1]).resolve())
