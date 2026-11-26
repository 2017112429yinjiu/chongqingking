"""Rebuild the Caijiashibao lane and the two measured Zhongxing wall cuts."""
import os
from pathlib import Path
import sys

import bpy

HERE = Path(__file__).resolve().parent
GROUPS = HERE.parent
DISTRICT = GROUPS.parents[1] / "district_500"
sys.path[:0] = [str(GROUPS), str(DISTRICT)]

from refresh_geometry import ASSETS, latest_donors, read, strip_plots
from retire_plots import fingerprint, remove_faces
from riverside import make_strip, material, terrain_faces


def build():
    plan = read(ASSETS / "public-edges.json")
    donors = latest_donors([("guoco-frontages", GROUPS / "guoco/guoco-frontages.blend")])
    meshes, retired, counts = strip_plots(
        read(HERE / "public-edges-ownership.json"), (44,), read(ASSETS / "layout.json"), donors
    )
    if retired != plan["retired_objects"] or counts != plan["face_counts"]:
        raise ValueError("Plot 44 ownership differs from the measured donor")

    path = make_strip(
        {"id": "caijiashibao_service_809889613", "points": plan["route_en"],
         "width_m": 2.68, "finish": 0, "raise_m": .021},
        list(terrain_faces()),
        [
            material("Caijiashibao matte fine grey flags", (.35, .39, .38), "stone_floor_diff_2k.jpg"),
            material("Caijiashibao intermediate sandstone seam", (.49, .49, .44), "stone_wall_05_diff_2k.jpg"),
            material("Caijiashibao kerb at planting edge", (.51, .54, .50), "concrete_floor_worn_001_diff_2k.jpg"),
        ],
    )
    path.name = plan["new_meshes"][0]
    wall = bpy.context.scene.objects["COL_Outer500_Retaining_and_boundaries"]
    cuts = plan["zhongxing"]
    fingerprints = [row["fingerprint"] for row in cuts["residual_removed"]]
    fingerprints += [row["sha"] for row in cuts["wheel_trace_followup"]["confirmed_fragments"]]
    for target in fingerprints:
        indices = [face.index for face in wall.data.polygons if fingerprint(wall, face) == target]
        if len(indices) != 1:
            raise ValueError(f"Expected one Zhongxing wall face for {target}, found {len(indices)}")
        remove_faces(wall, indices)

    keep = {*meshes, path}
    for item in list(bpy.data.objects):
        if item not in keep:
            bpy.data.objects.remove(item, do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    output = Path(os.environ.get("CQ_PUBLIC_EDGES_OUTPUT", HERE))
    output.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "public-edges.blend"), compress=True)
    export = output if "CQ_PUBLIC_EDGES_OUTPUT" in os.environ else ASSETS
    bpy.ops.export_scene.gltf(filepath=str(export / "public-edges.glb"), export_format="GLB",
                              export_cameras=False, export_lights=False)
    print("CQ_PUBLIC_EDGES", counts, fingerprints)


build()
