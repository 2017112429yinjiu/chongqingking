"""Check the retained park-side line and the exported Changbin shoulder."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
asset=here.parents[4] / "work/project/chongqing_godot_v05/assets/district_500/changbin-55.json"
plan=json.loads(asset.read_text())
scene=bpy.context.scene
for name in plan["replacement_meshes"]+plan["new_meshes"]:
    mesh=scene.objects[name].data
    assert len(mesh.polygons)>0 and not any(mat.is_missing for mat in mesh.materials if mat is not None),name
for name in plan["retired_objects"]:
    assert name not in scene.objects,name
deps=bpy.context.evaluated_depsgraph_get()
mesh=scene.objects["COL_Changbin55_PublicShoulder"]
surface=BVHTree.FromObject(mesh,deps)
support=[]
for e,n,z in plan["walk"]:
    point,normal,_,_=surface.ray_cast(Vector((e,n,z+.18)),Vector((0.,0.,-1.)),.4)
    assert point is not None and abs(point.z-z)<.025 and normal.z>.87,(e,n,z,point,normal)
    support.append(list(point))
print("CQ_CHANGBIN55_SOURCE "+json.dumps({"version":bpy.app.version_string,"file":bpy.data.filepath,"contacts":support}))
