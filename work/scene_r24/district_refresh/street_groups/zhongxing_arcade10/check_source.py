"""Reopen the registered source or combined scene and verify support and retirement."""
from hashlib import file_digest
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

base = Path(__file__).resolve().parents[5]
site = base/"work/project/chongqing_godot_v05/assets/district_500/zhongxing-arcade10.json"
plan = json.loads(site.read_text())
objects = bpy.context.scene.objects
for name in plan["new_meshes"]+plan["replacement_meshes"]:
    obj = objects[name]
    assert len(obj.data.polygons) and obj.data.uv_layers, name
    assert all(m and not m.is_missing for m in obj.data.materials), name
for name in plan["retired_objects"]:
    assert objects.get(name) is None, name
assert not any(image.is_missing for image in bpy.data.images)

def bvh(name):
    obj = objects[name]
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                               [poly.vertices[:] for poly in obj.data.polygons])

foot = bvh("COL_Zhongxing10_ArcadePublicFlags")
eaves = bvh("COL_Zhongxing10_ArcadeSoffitAndExterior")
points = []
for i, (east,north,y) in enumerate(plan["walks"]["10"]):
    point,normal,_,_ = foot.ray_cast(Vector((east,north,y+.19)),Vector((0,0,-1)),.45)
    assert point and abs(point.z-y) < .032 and normal.z > .91, (i,point,normal)
    roof,*_ = eaves.ray_cast(Vector((east,north,y+.17)),Vector((0,0,1)),9.)
    if i>=4:
        assert roof and roof.z-y >3.6, (i,roof,y)
    points.append(dict(en=[east,north],paving=point.z,up_normal=normal.z,covered_y=roof.z if roof else None))
result = {"blender":bpy.app.version_string,"file":Path(bpy.data.filepath).name,
          "plan_sha256":file_digest(site.open("rb"),"sha256").hexdigest(),
          "route":points,"retired_absent":plan["retired_objects"]}
Path(sys.argv[-1]).write_text(json.dumps(result,indent=2)+"\n")
print("CQ_ARCADE10_REOPEN",len(points), len(plan["retired_objects"]))
