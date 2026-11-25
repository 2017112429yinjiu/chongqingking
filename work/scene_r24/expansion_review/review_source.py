"""Check the reopened combined scene, including the registered R21 roof equipment supports."""
import json
import os
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[3]
game = root / "work/project/chongqing_godot_v05"
source = Path(bpy.data.filepath).resolve()
expected = root / "work/scene_r24/district_500/city_and_outer.local.blend"
assert bpy.app.version == (4, 3, 2) and source == expected
assert bpy.data.objects.get("Outer500_Plant_000")
libraries = []
for lib in bpy.data.libraries:
    target = Path(bpy.path.abspath(lib.filepath, library=lib.parent)).resolve()
    assert target.is_file() and target.is_relative_to(root), (lib.name, target)
    assert not any(block.is_missing for block in lib.users_id), lib.name
    libraries.append(target.relative_to(root).as_posix())
images = []
for img in bpy.data.images:
    if img.source != "FILE" or img.packed_file or not img.filepath:
        continue
    target = Path(bpy.path.abspath(img.filepath, library=img.library)).resolve()
    assert target.is_file() and target.is_relative_to(root), (img.name, target)
    images.append(target.relative_to(root).as_posix())
layout = json.loads((game / "assets/district_500/layout.json").read_text(encoding="utf-8"))
old = json.loads((game / "assets/district_r21/layout.json").read_text(encoding="utf-8"))
structure = next(ob for ob in bpy.context.scene.objects if ob.name.startswith("COL_Outer500_") and "Building" in ob.name)
deps = bpy.context.evaluated_depsgraph_get()
roof = BVHTree.FromObject(structure, deps)
supports = []
for item in old["rooftops"]:
    name = item["donor"]
    tokens = name.split("_")
    if not tokens[1].isdigit() or int(tokens[1]) not in layout["osm_building_ids"]:
        continue
    x, elevation, z = item["position"]
    origin = structure.matrix_world.inverted() @ Vector((x, -z, elevation + 0.5))
    found, _, _, _ = roof.ray_cast(origin, Vector((0, 0, -1)), 1.0)
    assert found is not None, name
    actual = (structure.matrix_world @ found).z
    assert abs(actual - elevation) < .012, (name, actual, elevation)
    supports.append({"donor": name, "east_north": [x,-z], "fixture_base_m":elevation, "roof_m":actual})
assert len(supports) == len(layout["osm_building_ids"])
trees = [ob for ob in bpy.context.scene.objects if ob.name.startswith("Outer500_Plant_")]
assert len(trees) == len(layout["planting"])
out = {"engine": bpy.app.version_string,"source": source.relative_to(root).as_posix(),
       "libraries": sorted(libraries), "external_image_count":len(images),
       "trees":len(trees),"unique_tree_meshes":len({t.data.name for t in trees}),"registered_rooftop_supports":supports}
dest = Path(os.environ["CQ_QA_DIR"]) / "combined_source.json"
dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",encoding="utf-8")
print("COMBINED_SOURCE", len(trees), len(supports), len(libraries))
