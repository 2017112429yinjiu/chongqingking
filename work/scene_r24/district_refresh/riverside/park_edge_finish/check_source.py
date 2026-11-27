"""Read UVs and packed albedos from the editable finish, then verify composed tree instances."""
import json
from pathlib import Path

import bpy
from mathutils import Vector

here = Path(__file__).resolve().parent
assets = here.parents[3] / "project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "park-edge-finish.json").read_bytes())
scene = bpy.context.scene
objects = scene.objects
names = plan["new_meshes"] + plan["replacement_meshes"]
uv_tile = plan["uv_tile_m"]
uv_counts = dict.fromkeys(uv_tile, 0)
max_uv_error_m = 0.0
for name in names:
    obj = objects[name]
    mesh = obj.data
    uv = mesh.uv_layers.active
    for face in mesh.polygons:
        mat = mesh.materials[face.material_index]
        if not mat.name.startswith("Park Edge "):
            continue
        image, = [node.image for node in mat.node_tree.nodes if node.type == "TEX_IMAGE"]
        assert image.packed_file, (obj.name, image.name)
        key = image.name.split("-park-edge.png")[0]
        uv_counts[key] += 1
        for loop, vertex in zip(face.loop_indices, face.vertices):
            p = obj.matrix_world @ mesh.vertices[vertex].co
            mapped = uv.data[loop].uv * uv_tile[key]
            max_uv_error_m = max(max_uv_error_m, (Vector((p.x, p.y)) - mapped).length)
assert all(uv_counts.values()), uv_counts
assert max_uv_error_m < .0001, max_uv_error_m

trees = []
if bpy.data.filepath.endswith("city_and_outer.local.blend"):
    for spec in plan["planted_trees"]:
        tree, donor = objects[spec["name"]], objects[spec["donor"]]
        pos = tree.matrix_world.translation
        assert tree.data == donor.data
        assert (pos - Vector(spec["east_north_up"])).length < .0001
        trees.append({"name": tree.name, "donor": donor.name, "root_enu": list(pos)})
print("CQ_FINISH_SOURCE", json.dumps({"blender": bpy.app.version_string, "meshes": names,
      "uv_tile_m": uv_tile, "uv_polygon_counts": uv_counts, "max_uv_error_m": max_uv_error_m,
      "shared_tree_meshes": trees}))
