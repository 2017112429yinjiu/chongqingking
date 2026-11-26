"""Reopen the full composed city and verify the registered roofs, route and stair reservation."""
import json
import os
from pathlib import Path

import bpy
import numpy as np

here=Path(__file__).resolve().parent
root=here.parents[2]
game=root/"work/project/chongqing_godot_v05"
site=json.loads((here/"site.json").read_bytes())
layout=json.loads((game/"assets/district_500/layout.json").read_bytes())
p=next(p for p in layout["plots"] if p["plot_id"]==0)
assert bpy.app.version[:3]==(4,3,2)
assert Path(bpy.data.filepath).name=="city_and_outer.local.blend"
required=["COL_Outer500_RepairCourt","Outer500_RepairCourt_TimberAndStone","COL_Outer500_Frame_00","Outer500_Joinery_00"]
parts={n:bpy.data.objects[n] for n in required}
assert all(o.type=="MESH" and o.library for o in parts.values())
reopened_libraries=sorted({Path(bpy.path.abspath(o.library.filepath)).resolve().name for o in parts.values()})
assert reopened_libraries==["outer_district.blend"]
def vertices(o):
    return np.array([list(o.matrix_world@v.co) for v in o.data.vertices])
court=vertices(parts["Outer500_RepairCourt_TimberAndStone"])
front=bpy.data.objects["Outer500_Facades_and_storefronts"]
front_vertices=vertices(front)
roof_residuals={}
for key,ring in site["roof_rings"].items():
    mesh=front_vertices if key.startswith("front") else court
    h=p["roof"]+.22 if key.startswith("front") else p["height"]+2.90
    eaves=mesh[np.abs(mesh[:,2]-h)<.002,:2]
    worst=max(np.linalg.norm(eaves-q,axis=1).min() for q in ring["en"])
    assert worst<.002,(key,worst)
    roof_residuals[key]=round(worst,6)
geo=json.loads((game/"source_data/geo_layout.json").read_bytes())
street=np.array(next(r["points"] for r in geo["roads"] if r["id"]==49182408))
route=p["repair_court"]
def road_distance(q):
    delta=street[1:]-street[:-1]
    t=np.clip(((q-street[:-1])*delta).sum(axis=1)/(delta*delta).sum(axis=1),0,1)
    return np.linalg.norm(q-(street[:-1]+t[:,None]*delta),axis=1).min()
u=np.array([np.cos(p["bearing"]),np.sin(p["bearing"])])
edge_points=[np.array(route[k][:2])+sign*2.04*u for k in ["toe","porch"] for sign in [-1,1]]
road_margin=min(road_distance(a) for a in edge_points)-3.15
assert road_margin>0
assert any(np.linalg.norm(np.array(t["east_north_up"][:2])-site["tree_en"])<.01 for t in layout["planting"])
per_plot=len(layout["plots"])
assert per_plot==71 and sum("registered_site" not in q for q in layout["plots"])==70
record={"blender":bpy.app.version_string,"source":Path(bpy.data.filepath).name,"linked":reopened_libraries,
        "members":{o.name:len(o.data.polygons) for o in parts.values()},"eaves_to_digitized_plan_max_m":roof_residuals,
        "stair_outer_edge_to_motor_road_edge_m":round(road_margin,3),
        "treads":route["risers"],"rise_m":route["rise_m"],"going_m":route["going_m"],
        "pending_old_plots":70}
(Path(os.environ["CQ_QA_DIR"])/"source.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
