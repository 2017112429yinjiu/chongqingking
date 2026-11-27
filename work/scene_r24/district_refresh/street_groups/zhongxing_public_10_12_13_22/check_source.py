"""Reopen the exterior edits and test each public footway's support."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
project=here.parents[4]/"work/project/chongqing_godot_v05/assets/district_500"
plan=json.loads((project/"zhongxing-public-10-12-13-22.json").read_text())
fixtures=bpy.context.scene.objects
for name in plan["new_meshes"]+plan["replacement_meshes"]:
    mesh=fixtures[name].data
    assert mesh.polygons, name
    assert all(not f.is_missing for f in mesh.materials if f), name
for name in plan["retired_objects"]:
    assert name not in fixtures, name
assert not any(image.is_missing for image in bpy.data.images)
measures={}
for key,stations in plan["walks"].items():
    mesh=fixtures[f"COL_Zhongxing{key}_PublicPaving"]
    assert mesh.data.uv_layers
    tree=BVHTree.FromObject(mesh,bpy.context.evaluated_depsgraph_get())
    points=[]
    for east,north,y in stations:
        p,n,_,_=tree.ray_cast(Vector((east,north,y+.25)),Vector((0,0,-1)),.50)
        assert p is not None and abs(p.z-y)<.08 and n.z>.83,(key,east,north,y,p,n)
        points.append(list(p))
    measures[key]=points
if "Outer500_Plant_036" in fixtures:
    assert all(row["name"] in fixtures for row in plan["trees"])
print("CQ_ZHONGXING_SOURCE "+json.dumps({"engine":bpy.app.version_string,"file":bpy.data.filepath,"supports":measures}))
