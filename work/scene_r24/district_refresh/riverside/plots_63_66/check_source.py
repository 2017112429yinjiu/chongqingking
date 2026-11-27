"""Reopen the editable increment and probe its public paths and distinct road levels."""
import json
from pathlib import Path

import bpy
from mathutils import Vector

here = Path(__file__).resolve().parent
assets = here.parents[3] / "project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "changbin-bend-and-edge.json").read_bytes())
objects = bpy.context.scene.objects
graph = bpy.context.evaluated_depsgraph_get()
combined = bpy.data.filepath.endswith("city_and_outer.local.blend")
assert all(name in objects for name in plan["new_meshes"] + plan["replacement_meshes"])
assert all(name not in objects for name in plan["retired_objects"])
if combined:
    assert all(objects[name].library.filepath.endswith("/changbin-bend-and-edge.blend")
               for name in plan["new_meshes"]+plan["replacement_meshes"])
    for name in ("COL_Riverside_62_registered_body", "COL_Raijiapo_Ramp_1256839997",
                 "COL_Outer500_Frame_67", "COL_Park59_PublicPaving", "Park61_WestParkEdgePath"):
        assert name in objects, name


def contact(obj, e, n, height):
    inverse = obj.matrix_world.inverted()
    found, loc, normal, face = obj.evaluated_get(graph).ray_cast(
        inverse @ Vector((e,n,height)), inverse.to_3x3() @ Vector((0,0,-1)), distance=28)
    if not found:
        return None
    return {"point_enu":list(obj.matrix_world@loc),"normal_up":normal.z,"face":face}


floors = {}
for group, route in plan["routes"].items():
    name = route["walk_mesh"]
    item = objects[name]
    assert item.data.uv_layers.active
    assert all(any(n.image and n.image.packed_file for n in m.node_tree.nodes if n.type == "TEX_IMAGE")
               for m in item.data.materials)
    floors[group] = []
    for e,n in route["stations"]:
        for offset in (-.7,0,.7):
            hit = contact(item,e+.029,n+offset,8.)
            assert hit and hit["normal_up"]>.86, (group,e,n,offset,hit)
            floors[group].append(hit)
walk_contacts = sum(map(len,floors.values()))

upper = objects["COL_Changbin_InsideBend_1375242615"]
upper_samples = []
for e,s,n,up in plan["upper_curve_sections_game_enu"][1:-1:3]:
    hit = contact(upper,e+.021,(n+s)/2,up+2)
    assert hit and abs(hit["point_enu"][2]-up)<.017 and hit["normal_up"]>.9
    upper_samples.append(hit)

lower = {}
for way, rows in plan["lower_ramp_sections_game_enu"].items():
    ramp = objects["COL_Changbin_LowRamp_"+way]
    assert ramp.data.uv_layers.active
    lower[way] = []
    for east,north,land,up in rows[2:-2:4]:
        hit = contact(ramp,east+.023,north,up+2)
        assert hit and abs(hit["point_enu"][2]-up)<.017 and hit["normal_up"]>.8
        lower[way].append({"ground_game_m":land,**hit})

print("CQ_CHANGBIN_SOURCE",json.dumps({"blender":bpy.app.version_string,"composition":combined,
      "walk_contact_count":walk_contacts,"walk":floors,"upper_deck":upper_samples,"low_ramps":lower,
      "retired_whole":plan["retired_objects"],"retired_shared_faces":plan["removed_shared_geometry"]}))
