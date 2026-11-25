"""Run with Blender after reopening outer_district.blend."""
import json
import os
from pathlib import Path

import bpy

objects = [obj for obj in bpy.context.scene.objects if obj.name.startswith("COL_Outer500_Surface_")]
points = [obj.matrix_world @ v.co for obj in objects for v in obj.data.vertices]
bounds = [[float(fn(point[axis] for point in points)) for axis in range(3)] for fn in (min, max)]
missing = [image.name for image in bpy.data.images if image.source=="FILE" and not image.packed_file]
matrix = {
    "blender": bpy.app.version_string,"source": Path(bpy.data.filepath).name,
    "terrain_bounds_east_north_up_m": bounds,
    "extent_m": [bounds[1][axis]-bounds[0][axis] for axis in range(3)],
    "terrain_objects": len(objects),"terrain_triangles":sum(len(obj.data.polygons) for obj in objects),
    "mesh_objects":sum(obj.type=="MESH" for obj in bpy.context.scene.objects),
    "unpacked_images":missing,
}
assert matrix["extent_m"][:2] == [500,500] and not missing, matrix
if os.environ.get("CQ_QA_DIR"):
    path=Path(os.environ["CQ_QA_DIR"])
    path.mkdir(exist_ok=True,parents=True)
    (path/"blender_footprint.json").write_text(json.dumps(matrix,indent=2)+"\n")
print(json.dumps(matrix))
