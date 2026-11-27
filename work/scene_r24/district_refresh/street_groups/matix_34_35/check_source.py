"""Reopen the Mati Street source and check both public walking surfaces."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
plan_path=here.parents[4]/"work/project/chongqing_godot_v05/assets/district_500/mati-34-35.json"
plan=json.loads(plan_path.read_text())
objects=bpy.context.scene.objects
assert all(objects[name].data.polygons for name in plan["new_meshes"])
assert not plan["retired_objects"] and not plan["replacement_meshes"]
if len(objects)>20:
    assert all(f"COL_Outer500_Frame_{code}" in objects for code in (34,35))
assert not any(image.is_missing for image in bpy.data.images)
measures={}
for key,name in (("34","COL_Mati34_PublicApproach"),("35","COL_Mati35_PublicApproach")):
    mesh=objects[name]
    assert mesh.data.uv_layers
    tree=BVHTree.FromObject(mesh,bpy.context.evaluated_depsgraph_get())
    measures[key]=[]
    for east,north,y in plan["walks"][key]:
        p,n,_,_=tree.ray_cast(Vector((east,north,y+.25)),Vector((0,0,-1)),.50)
        assert p is not None and abs(p.z-y)<.04 and n.z>.83,(key,east,north,y,p,n)
        measures[key].append(list(p))
print("CQ_MATI_SOURCE "+json.dumps({"engine":bpy.app.version_string,"file":bpy.data.filepath,"supports":measures}))
