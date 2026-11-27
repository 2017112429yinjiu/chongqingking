"""Check the landing support and true geometric door recess after reopening."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
assets = here.parents[4] / "work/project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "jiefang-gate25-finish.json").read_text())
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
for name in plan["replacement_meshes"]+plan["new_meshes"]:
    assert scene.objects[name].data.uv_layers, name
for name in plan["retired_objects"]:
    assert name not in scene.objects, name
support = []
for i,(east,north,y) in enumerate(plan["walks"]["25"]):
    name = "COL_Jiefang25_JoinedFlags" if i==0 else plan["replacement_meshes"][0]
    tree = BVHTree.FromObject(scene.objects[name],deps)
    hit, normal, _, _ = tree.ray_cast(Vector((east,north,y+.20)),Vector((0,0,-1)),.40)
    assert hit is not None and abs(hit.z-y)<.04 and normal.z>.80, (i,hit,normal)
    support.append(list(hit))
fit = json.loads((here.parent/"jiefang_public_24_25_26/field.json").read_text())["stairs_25"]
a,b = [Vector(fit[k]["en"]) for k in ("left","right")]
tangent = (b-a).normalized()
inward = Vector((-tangent.y,tangent.x,0.))
e,n,y = plan["eye_controls"]["center_enu"]
origin = Vector((e,n,y+1.5))-inward*2
glazing = BVHTree.FromObject(scene.objects["Jiefang25_SoffitVerticalsAndGlass"],deps)
head = BVHTree.FromObject(scene.objects["COL_Jiefang25_StoneWingsAndHead"],deps)
door,_,_,_ = glazing.ray_cast(origin,inward,4.)
underside,_,_,_ = head.ray_cast(origin+Vector((0,0,2.1)),inward,4.)
assert door is not None and underside is not None
recess = (door-underside).dot(inward)
assert .68 < recess < .90, recess
print("CQ_GATE25_SOURCE "+json.dumps({"file":bpy.data.filepath,"engine":bpy.app.version_string,
                                     "recess_m":recess,"supports":support}))
