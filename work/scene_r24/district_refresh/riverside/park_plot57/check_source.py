"""Reopen the increment or composed district and verify the seal and retained pavilion."""
import json
from pathlib import Path

import bpy

here=Path(__file__).resolve().parent
assets=here.parents[3]/"project/chongqing_godot_v05/assets/district_500"
plan=json.loads((assets/"park-plot57.json").read_bytes())
objects=bpy.context.scene.objects
seal=objects["COL_Park57_NorthDeckWallSeal"]
assert len(seal.data.polygons)==6
assert .37 < seal.dimensions.x < .43 and 1.70 < seal.dimensions.z < 1.80
assert all(face.material_index==0 for face in seal.data.polygons)
assert seal.data.uv_layers.active is not None and seal.data.materials[0].node_tree
entry=objects["COL_Park57_StreetEntryReturn"]
entry_sections=plan["street_entry_return"]["section_east_north_lower_upper"]
assert len(entry.data.polygons)==len(entry_sections)
assert all(.015 < upper-lower < .045 for _,_,lower,upper in entry_sections)
assert entry.data.uv_layers.active is not None
assert any(node.type=="TEX_IMAGE" and node.image
           for node in entry.data.materials[0].node_tree.nodes)
assert all(name not in objects for name in plan["retired_objects"])
walk=objects["COL_Park57_EastWalkGrade"]
assert len(walk.data.polygons)>10 and walk.dimensions.x>4.2
assert sum(1 for obj in objects if obj.name.startswith("Park57_GreenBelt_Plant_"))==8
pavilion=[]
if bpy.data.filepath.endswith("city_and_outer.local.blend"):
    pavilion=json.loads((assets/"pavilion62.json").read_bytes())["new_meshes"]
    assert all(name in objects for name in pavilion)
    assert seal.library and seal.library.filepath.endswith("/park-plot57.blend")
    assert entry.library==objects["COL_WestPlayground_PerimeterSupport"].library==seal.library
    retaining=objects["COL_Outer500_Retaining_and_boundaries"]
    assert retaining.library.filepath.endswith(("/park-plot57.blend","/bridge-park.blend","/park-plot59.blend"))
    assert objects["Huihuigou_TerrazzoPaving"].library.filepath.endswith("/collectibles-market.blend")
print("CQ_PARK57_REOPEN",json.dumps({
    "version":bpy.app.version_string,"objects":len(objects),"libraries":len(bpy.data.libraries),
    "seal_dimensions_m":list(seal.dimensions),"seal_faces":len(seal.data.polygons),
    "seal_finish":seal.data.materials[0].name,"east_deck_cut_path_faces":len(walk.data.polygons),
    "entry_faces":len(entry.data.polygons),"entry_joint_sections":entry_sections,
    "pavilion_meshes_retained":pavilion}))
