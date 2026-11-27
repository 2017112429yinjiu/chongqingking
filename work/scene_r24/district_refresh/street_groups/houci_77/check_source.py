"""Reopen the editable finish and test the composed terrain at the registered cross-sections."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
assets = here.parents[3]/"project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets/"houci-77.json").read_bytes())
objects = bpy.context.scene.objects
expected=plan["new_meshes"] + plan["replacement_meshes"]
assert all(name in objects for name in expected)
assert not set(plan["retired_objects"]).intersection(objects.keys())
if Path(bpy.data.filepath).name == "city_and_outer.local.blend":
    for name in ("COL_Guoco_T1_1374780314","COL_Guoco_T2_1374780313","COL_Guoco_PodiumPublicPassage"):
        assert name in objects, name

def bvh(object_name):
    ob = objects[object_name]
    positions = [ob.matrix_world @ v.co for v in ob.data.vertices]
    return BVHTree.FromPolygons(positions, [tuple(p.vertices) for p in ob.data.polygons])

surface_names = (["COL_Houci_Public_Flagstones"]*2 + ["COL_Houci_Street_Kerbs"]
                 + ["COL_Houci_1306489251_Asphalt"]*3
                 + ["COL_Houci_Street_Kerbs"] + ["COL_Houci_Public_Flagstones"]*2)
mesh = {name:bvh(name) for name in set(surface_names)}
sections=[]
for row in plan["sections_east_north"]:
    section=[]
    for en, name in zip(row, surface_names, strict=True):
        target, normal, _, _ = mesh[name].ray_cast(Vector((*en,42.)),Vector((0.,0.,-1.)),60.)
        assert target is not None and normal.z > .9, (en, name, target, normal)
        section.append([*en, target.z, normal.z, name])
    sections.append(section)
for name in plan["new_meshes"]:
    ob = objects[name]
    assert ob.data.uv_layers.active and ob.data.uv_layers.active.data
    assert all(mat.use_nodes for mat in ob.data.materials)

print("CQ_HOUCI_SOURCE",json.dumps({"blender":bpy.app.version_string,"source":Path(bpy.data.filepath).name,
      "meshes":{name:len(objects[name].data.polygons) for name in expected},
      "sample_count":sum(map(len,sections)),"cross_sections":sections}))
