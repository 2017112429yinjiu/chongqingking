"""Measure the reopened planter, pavement, and subgrade at each ring segment."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
assets = here.parents[4] / "work/project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "zhongxing-plaza-22-finish.json").read_text())
objects = bpy.context.scene.objects
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in plan["new_meshes"] + plan["replacement_meshes"]:
    assert objects[name].data.polygons and objects[name].data.uv_layers, name
for name in plan["retired_objects"]:
    assert name not in objects, name
apron = BVHTree.FromObject(objects["COL_Zhongxing22_ContinuousPublicApron"], depsgraph)
rim = BVHTree.FromObject(objects["COL_Zhongxing22_SealedStonePlanter"], depsgraph)
earth = BVHTree.FromObject(objects["COL_Outer500_Surface_07_06"], depsgraph)


def surface(tree, en, elevation, distance):
    point, _, _, _ = tree.ray_cast(Vector((*en,elevation)),Vector((0,0,-1)),distance)
    assert point is not None, (en,elevation,distance)
    return point.z


sections = []
for row in plan["exposure_sections"]:
    en = row["floor_en"]
    top = row["cap_y"]
    floor_y = surface(apron,en,top+.05,1.)
    cap_y = surface(rim,row["cap_en"],top+.25,1.)
    below_y = surface(earth,en,top+.05,1.6)
    assert .42 < cap_y-floor_y < .70 and below_y < floor_y-.04 and row["base_y"]<floor_y-.07, row
    sections.append({"en":en,"floor_y":floor_y,"cap_y":cap_y,"on_grade_exposure_m":cap_y-floor_y,
                     "below_floor_terrain_m":floor_y-below_y})
if "Outer500_Plant_036" in objects:
    assert all(row["name"] in objects for row in plan["trees"])
print("CQ_ZHONGXING22_SOURCE " + json.dumps({
    "engine":bpy.app.version_string,"file":bpy.data.filepath,"sections":sections,
    "clip_faces":plan["terrain_faces_clipped"],
}))
