"""Check the new edge mesh and the composed scene's remaining land contacts."""
import json
from pathlib import Path

import bpy
from mathutils import Vector

here = Path(__file__).resolve().parent
assets = here.parents[3] / "project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "park-plot61.json").read_bytes())
scene = bpy.context.scene
objects = scene.objects
assert all(name in objects for name in plan["new_meshes"] + plan["replacement_meshes"])
assert all(name not in objects for name in plan["retired_objects"])
for name in ("Park61_WestParkEdgePath","Park61_NearTreeBelt"):
    mesh = objects[name].data
    assert len(mesh.polygons)>10 and mesh.uv_layers.active is not None
    assert any(node.image and node.image.packed_file for material in mesh.materials
               for node in material.node_tree.nodes if node.type == "TEX_IMAGE")
park61 = objects["Park61_WestParkEdgePath"]
graph = bpy.context.evaluated_depsgraph_get()
samples = []
for e,n in plan["route_east_north"][1:-1]:
    hit,loc,normal,_,obj,_ = scene.ray_cast(graph,Vector((e+.031,n+.015,5)),Vector((0,0,-1)),distance=16)
    assert hit and obj.name==park61.name and normal.z>.88, (e,n,obj and obj.name)
    samples.append({"en":[e,n],"game_up":loc.z,"normal_up":normal.z,"mesh":obj.name})
if bpy.data.filepath.endswith("city_and_outer.local.blend"):
    assert park61.library and park61.library.filepath.endswith(("/park-plot61.blend","/park-edge-finish.blend"))
    assert objects.get("COL_Park59_PublicPaving")
    pavilion = json.loads((assets / "pavilion62.json").read_bytes())["new_meshes"]
    assert all(objects[name].library.filepath.endswith("/pavilion62.blend") for name in pavilion)

print("CQ_PARK61_SOURCE",json.dumps({
    "blender":bpy.app.version_string,"curve_contacts":samples,
    "removed_scene_objects":plan["retired_objects"],"removed_shared_faces":plan["removed_shared_geometry"],
}))
