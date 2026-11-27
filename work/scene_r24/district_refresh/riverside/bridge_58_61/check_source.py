"""Check the editable increment and the linked district at their stored game levels."""
import json
from pathlib import Path

import bpy
from mathutils import Vector

here = Path(__file__).resolve().parent
assets = here.parents[3] / "project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "bridge-park.json").read_bytes())
scene = bpy.context.scene
objects = scene.objects
tracked = plan["new_meshes"] + plan["replacement_meshes"]
park59 = objects.get("COL_Park59_PublicPaving")
park61 = objects.get("Park61_WestParkEdgePath")
park_finish = objects.get("ParkEdge_WestFoldGreyReturn")
override_libraries = {}
for layer,manifest in ((park59,"park-plot59.json"),(park61,"park-plot61.json"),(park_finish,"park-edge-finish.json")):
    if layer:
        park_plan = json.loads((assets / manifest).read_bytes())
        tracked = [name for name in tracked if name not in park_plan["retired_objects"]]
        library_path = "/"+manifest.replace(".json",".blend")
        library = next((lib for lib in bpy.data.libraries if lib.filepath.endswith(library_path)), None)
        override_libraries.update({name:library for name in park_plan["replacement_meshes"]})
assert all(name in objects for name in tracked)
assert all(name not in objects for name in plan["retired_objects"])
rail = objects["COL_Nanjimen_NorthRailSteelBox"]
parking = objects["COL_Raijiapo_GarageParkingSlabs"]
assert len(parking.data.polygons) > 350
assert len(rail.data.polygons) > 300
for name in ("BridgePark_EastGroundWalk", "BridgePark_ChangbinParkFootway",
             "COL_Raijiapo_GaragePublicEnvelope", "COL_Nanjimen_NorthRailPiers"):
    mesh = objects[name].data
    assert mesh.uv_layers.active
    assert all(material for material in mesh.materials)
    assert any(node.image and node.image.packed_file for material in mesh.materials
               for node in material.node_tree.nodes if node.type == "TEX_IMAGE")

positions = []
for site_id, position in plan["plots"].items():
    e, n = position
    hit, loc, _, _, mesh, _ = scene.ray_cast(
        bpy.context.evaluated_depsgraph_get(),
        Vector((e+.031, n-.019, 5)), Vector((0, 0, -1)), distance=30,
    )
    assert hit and objects.get(mesh.name), (site_id, mesh and mesh.name, list(loc))
    assert mesh.name.startswith(("BridgePark_", "COL_Outer500_Surface_", "Park61_")), (site_id, mesh.name)
    positions.append({"plot":site_id, "ground":round(loc.z, 4), "mesh":mesh.name})

if bpy.data.filepath.endswith("city_and_outer.local.blend"):
    assert all(objects[name].library == override_libraries.get(name,rail.library) for name in tracked)
    assert objects.get("COL_Outer500_Frame_59") or park59
    assert objects.get("COL_Outer500_Frame_61") or park61
    assert objects.get("COL_Park57_NorthDeckWallSeal") and objects.get("COL_Park57_StreetEntryReturn")
    pavilion = json.loads((assets / "pavilion62.json").read_bytes())
    assert all(name in objects for name in pavilion["new_meshes"])

print("CQ_BRIDGE_PARK_SOURCE", json.dumps({
    "blender": bpy.app.version_string, "added":len(plan["new_meshes"]),
    "shared_replaced":len(plan["replacement_meshes"]), "removed":len(plan["retired_objects"]),
    "rail_faces":len(rail.data.polygons), "parking_slab_faces":len(parking.data.polygons),
    "park_stop_ground":positions,
}))
