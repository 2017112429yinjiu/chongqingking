"""Reopen the editable Blender increment and check the exported foot grades."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
asset=here.parents[4] / "work/project/chongqing_godot_v05/assets/district_500/nanqu-04-06-51.json"
plan=json.loads(asset.read_text())
graph=bpy.context.evaluated_depsgraph_get()
scene=bpy.context.scene
for name in plan["new_meshes"] + plan["replacement_meshes"]:
    item=scene.objects[name]
    if name in plan["new_meshes"]:
        assert item.data.uv_layers, name
    assert not any(mat.is_missing for mat in item.data.materials if mat is not None), name
for name in plan["retired_objects"]:
    assert name not in scene.objects, name
footway=BVHTree.FromObject(scene.objects["COL_Nanqu_RiverFootway"],graph)
point_samples=[]
max_grade_error=0.
for e,n,z in plan["public_walk"] + plan["planter_contacts"]:
    found,normal,_,_=footway.ray_cast(Vector((e,n,z+.18)),Vector((0,0,-1)),.35)
    assert found is not None and abs(found.z-z)<.025 and normal.z>.92, (e,n,z,found,normal)
    max_grade_error=max(max_grade_error,abs(found.z-z))
    point_samples.append((e,n,found.z))
print("CQ_NANQU_SOURCE "+json.dumps({"file":bpy.data.filepath,"version":bpy.app.version_string,
      "ground_contacts":len(point_samples),"max_grade_error_m":max_grade_error,"points":point_samples,"retired":plan["retired_plots"]}))
