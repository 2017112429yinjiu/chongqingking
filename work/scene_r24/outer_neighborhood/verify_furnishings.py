"""Check the cut rail and the new wicker baskets and armchairs in the saved city."""
import json
import os
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[3]
assert Path(bpy.data.filepath).resolve()==root/"work/scene_r24/district_500/city_and_outer.local.blend"
layout=json.loads((root/"work/project/chongqing_godot_v05/assets/district_500/layout.json").read_text(encoding="utf-8"))
info=layout["interior_rail_return"]; plot=next(p for p in layout["plots"] if p["plot_id"]==info["plot"])
from math import cos, sin
c,s=cos(plot["bearing"]),sin(plot["bearing"])
original=bpy.data.objects[info["original"]]; repaired=bpy.data.objects[info["replacement"]]
assert original.hide_render and not repaired.hide_render
def surface(obj):
    mesh=obj.data
    return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in mesh.vertices],[face.vertices[:] for face in mesh.polygons])
after=surface(repaired)
errors=[]; outside=0; max_error=0
for face in original.data.polygons:
    point=original.matrix_world @ face.center
    x=point.x-plot["east_north"][0]; y=point.y-plot["east_north"][1]
    if abs(x*c+y*s)<plot["width"]/2-.095 and abs(-x*s+y*c)<plot["depth"]/2-.095 and -.175<point.z-plot["height"]<2.835:
        continue
    distance=after.find_nearest(point)[3]
    max_error=max(max_error,distance);outside+=1
    if distance>.002:errors.append(["outdoor_rail",face.index,distance])
bodies=[o for o in bpy.context.scene.objects if o.name=="COL_Outer500_Building_envelopes" or o.name.startswith("COL_Outer500_Court_")]
surfaces=[surface(o) for o in bodies]
rooms=[]
for index,item in enumerate(layout["household"]):
    if item["asset"] not in ("Court14_BackBasket_and_greens","chinese_armchair"):continue
    p=next(p for p in layout["plots"] if p["plot_id"]==item["plot"])
    pos=Vector(item["origin"])
    if item["asset"]=="chinese_armchair" and pos.z < p["height"]+2:continue
    prefix="Outer500_Household_%03d_"%index
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH" and o.name.startswith(prefix)]
    low=min((o.matrix_world@v.co).z for o in meshes for v in o.data.vertices)
    hits=[tree.ray_cast(pos+Vector((0,0,.075)),Vector((0,0,-1)),.23)[0] for tree in surfaces]
    ground=max((hit.z for hit in hits if hit is not None),default=-1000)
    gap=low-ground
    rooms.append({"plot":item["plot"],"asset":item["asset"],"gap_m":round(gap,5)})
    if abs(gap)>.016:errors.append([item["asset"],index,gap])
out={"blender":bpy.app.version_string,"original_rail_outdoor_face_centers":outside,"max_exterior_difference_m":max_error,
     "basket_and_seat_contacts":rooms,"failures":errors}
Path(os.environ["CQ_QA_DIR"],"furnishing_contacts.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
assert not errors and len(rooms)==47 and outside>0,(len(rooms),errors[:4])
