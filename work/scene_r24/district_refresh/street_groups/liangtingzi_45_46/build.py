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
        ("stucco", "Liangtingzi worn shop-side rendered wall", (.81,.77,.66), "concrete_wall_006_diff_2k.jpg"),
        ("wood", "Liangtingzi lower trim and door frames", (.54,.39,.29), "wood_table_worn_diff_2k.jpg"),
    )
    for key, label, color, texture in specifications:
        finishes[key] = make_material(label, color, texture)
        textures[label] = f"res://assets/chongqing_district_{texture}"
    finishes["fence"] = tint("Liangtingzi oxide red closed boundary", (.22,.075,.055))
    finishes["joint"] = tint("Liangtingzi damp stone joints", (.19,.19,.16))
    finishes["notice"] = tint("Liangtingzi pale vertical plaque", (.77,.79,.73))
    finishes["blue"] = tint("Liangtingzi faded blue eave", (.15,.33,.45))
    finishes["opening"] = tint("Liangtingzi shaded street-side shop recess", (.093,.087,.074))
    return finishes, textures


def frontage(edge, tiles, m):
    stones = edge.strip("COL_Liangtingzi45_PublicFlags", 0., 1.76, .053, tiles, m["flag"], m["kerb"])
    rim = Mesh("Liangtingzi45_PavingRimAndJoints")
    for k in range(ceil((edge.stations[-1]-1.)/.53)):
        a = .38+k*.53
        b = a+.53
        box(rim,edge,a,b,.83,.98,.015,.123,m["kerb"])
        box(rim,edge,a+.48,a+.488,-.73,.77,.054,.003,m["joint"])
    return [stones,rim.save()]


def shared_lower_edge(field, ground, tiles, m):
    e,n=field["observations"]["brick_pier_45_46"]["match_en"]
    head=Edge([(e-1.28,n+.19),(e,n)],ground)
    pier=Mesh("COL_Liangtingzi_LowerLaneBrickPierAndWall")
    metal=Mesh("Liangtingzi_LowerLaneRustFenceAndPlaque")
    s=head.stations[-1]
    box(pier,head,s-.27,s+.27,-.275,.275,-.10,2.32,m["brick"])
    box(pier,head,s-.32,s+.32,-.34,.34,2.16,.175,m["kerb"])
    box(metal,head,s-.13,s+.13,.279,.309,1.05,.68,m["notice"])
    box(metal,head,s-.15,s+.15,.281,.295,1.185,.048,m["fence"])
    box(pier,head,.19,s-.30,-.27,.24,-.14,.58,m["brick"])
    box(pier,head,.14,s-.26,-.30,.30,.42,.113,m["kerb"])
    for h in (.64,1.28):
        box(metal,head,.19,s-.23,-.033,.032,h,.042,m["fence"])
    for k in range(ceil((s-.46)/.14)):
        x=.23+k*.143
        box(metal,head,x,x+.026,-.024,.019,.51,.86,m["fence"])

    tree=field["tree_anchor"]
    south=Edge([(tree[0]-1.42,tree[1]-.08),(tree[0]+1.67,tree[1]+.04)],ground)
    apron=south.strip("COL_Liangtingzi45_TreeSideFlags",0.,1.26,.052,tiles,m["flag"],m["kerb"])
    rim=Mesh("Liangtingzi45_StoneTreeWell")
    for lo,hi,near,far in ((1.01,1.09,-.45,.43),(1.77,1.85,-.45,.43),(1.09,1.77,-.45,-.36),(1.09,1.77,.35,.43)):
        box(rim,south,lo,hi,near,far,.058,.10,m["kerb"])
    box(rim,south,1.09,1.77,-.36,.35,.056,.026,m["planting"])
    y=ground.ray_cast(Vector((*tree,92.)),Vector((0.,0.,-1.)),110.)[0].z
    tree_row={"name":"Liangtingzi45_LaneTree","donor":"Outer500_Plant_036","enu":[*tree,y+.071],"yaw":.78,"scale":1.04}
    return [pier.save(),metal.save(),apron,rim.save()],tree_row


def low_shops(edge,m):
    front=Mesh("COL_Liangtingzi46_SunkShopStreetEdge")
    trim=Mesh("Liangtingzi46_EavesAndWindowRecesses")
    for a,b in ((4.4,7.0),(7.0,9.62),(9.62,12.22)):
        for x in (a,b-.20):
            box(front,edge,x,x+.20,.99,1.26,-.78,2.54,m["stucco"])
        box(front,edge,a,b,1.38,1.55,-.75,2.53,m["stucco"])
        box(trim,edge,a+.24,b-.20,1.316,1.381,-.481,1.24,m["opening"])
        box(trim,edge,a+.07,b-.10,.89,1.28,.91,.173,m["wood"])
        box(trim,edge,a-.04,b+.055,.73,1.57,1.79,.115,m["blue"])
        for k in range(7):
            x=a+.20+k*.313
            box(trim,edge,x,x+.025,.735,1.52,1.911,.038,m["blue"])
    return [front.save(),trim.save()]


def descent(edge, tiles, m):
    paving = edge.strip("COL_Liangtingzi46_PublicDescent", 0., 1.62, .063, tiles, m["concrete"], m["kerb"])
    returns = Mesh("COL_Liangtingzi46_LaneEdgeParapet")
    stair = Mesh("COL_Liangtingzi46_SeparateStoneStair")
    cap = Mesh("Liangtingzi46_WornStoneReturns")
    for i in range(18):
        a=.70+i*.60
        b=a+.60
        box(returns,edge,a,b,-1.045,-.83,-.12,.72,m["brick"])
        box(cap,edge,a,b,-1.10,-.79,.59,.105,m["kerb"])
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
        if key=="46":
            layer.extend(low_shops(edge,mats))
    shared,tree=shared_lower_edge(field,field_terrain,cache,mats)
    layer.extend(shared)
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
          "walks":routes,"surface_textures":textures,"borrowed_materials":{},"trees":[tree]}
    (output/f"{name}.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n")
    print("CQ_LIANGTINGZI",json.dumps(routes))


if __name__ == "__main__":
    build(Path(sys.argv[-1]).resolve())
