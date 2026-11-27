"""Reopen the Liangtingzi source and check both public walking surfaces."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
plan_path=here.parents[4]/"work/project/chongqing_godot_v05/assets/district_500/liangtingzi-45-46.json"
plan=json.loads(plan_path.read_text())
objects=bpy.context.scene.objects
assert all(objects[name].data.polygons for name in plan["new_meshes"])
assert not any(image.is_missing for image in bpy.data.images)
measures={}
for key,name in (("45","COL_Liangtingzi45_PublicFlags"),("46","COL_Liangtingzi46_PublicDescent")):
    mesh=objects[name]
    assert mesh.data.uv_layers
    tree=BVHTree.FromObject(mesh,bpy.context.evaluated_depsgraph_get())
    measures[key]=[]
    for east,north,y in plan["walks"][key]:
        p,n,_,_=tree.ray_cast(Vector((east,north,y+.25)),Vector((0,0,-1)),.50)
        assert p is not None and abs(p.z-y)<.04 and n.z>.83,(key,east,north,y,p,n)
        measures[key].append(list(p))
print("CQ_LIANGTINGZI_SOURCE "+json.dumps({"engine":bpy.app.version_string,"file":bpy.data.filepath,"supports":measures}))
