"""Open the original city, relink its libraries, append the editable outer layer."""
import json
from pathlib import Path

import bpy
import bmesh

here = Path(__file__).resolve().parent
root = here.parents[2]
refs = json.loads((root / "docs/version-control/blender-source-check.json").read_text(encoding="utf-8-sig"))["reference_paths"]
for ref in refs:
    target = root / ref["repository_path"]
    if not target.exists() or target.stat().st_size < 200:
        raise RuntimeError(f"Required source dependency missing: {target}")
    if ref["kind"] == "image":
        image = bpy.data.images.get(ref["name"])
        if image is not None and not image.packed_file:
            image.filepath = str(target)
            image.reload()
    else:
        lib = next((item for item in bpy.data.libraries
                    if item.filepath.replace("\\","/").endswith("/"+target.name)),None)
        if lib is not None:
            result = bpy.ops.wm.lib_relocate(library=lib.name,directory=str(target.parent)+"/",filename=target.name)
            if "FINISHED" not in result:
                raise RuntimeError(f"Library relocation failed: {target}")

layout = json.loads((root / "work/project/chongqing_godot_v05/assets/district_500/layout.json").read_text(encoding="utf-8-sig"))
retired = [f"_{oid}_" for oid in layout.get("osm_building_ids", [])]
local_study = bpy.data.collections.get("R24_11_Local_city_frame")
if local_study:
    local_study.hide_viewport=True
    local_study.hide_render=True
edge=json.loads((root/"work/project/chongqing_godot_v05/assets/district_500/edge_ground.json").read_bytes())
for item in bpy.context.scene.objects:
    if item.name.startswith(tuple(edge["context_prefixes"])):
        transform=item.matrix_world.copy();transform.translation.z+=edge["context_shift_z"];item.matrix_world=transform
    if item.name==layout.get("interior_rail_return",{}).get("original"):
        item.hide_set(True)
        item.hide_render=True
    if item.name in ("Outer_ground_context_ground_dirt","R22_Bank_Outer","R22_Bank_Relief") or (
            item.name.startswith("Context_") and any(mark in item.name for mark in retired)):
        item.hide_set(True)
        item.hide_render=True
    if item.name.startswith(tuple(layout.get("retired_context_prefixes", []))):
        item.hide_set(True)
        item.hide_render=True
    if item.name=="R21_Rooftop_stairheads" and layout.get("retired_roof_positions"):
        piece=bmesh.new()
        piece.from_mesh(item.data)
        unwanted=[]
        for face in piece.faces:
            v=item.matrix_world @ face.calc_center_median()
            if any(abs(v.x-x)<2.35 and abs(v.y+south)<1.65 and up-.10<v.z<up+4.65
                   for x,up,south in layout["retired_roof_positions"]):
                unwanted.append(face)
        bmesh.ops.delete(piece,geom=unwanted,context="FACES")
        piece.to_mesh(item.data)
        piece.free()

with bpy.data.libraries.load(str(here / "outer_district.blend"), link=True, relative=True) as (source,draft):
    draft.objects=list(source.objects)
collection=bpy.data.collections.new("500 m playable expansion")
bpy.context.scene.collection.children.link(collection)
court_data=json.loads((root / "work/project/chongqing_godot_v05/assets/district_500/historic_courts.json").read_bytes())
old_roots=court_data["superseded_outer_roots"]
with bpy.data.libraries.load(str(here / "interior_terrain.blend"), link=True, relative=True) as (source, corrected):
    corrected.objects = source.objects[:]
replaced = {obj.name for obj in corrected.objects}
for obj in corrected.objects:
    collection.objects.link(obj)
for obj in draft.objects:
    if obj.name in replaced:
        continue
    if (obj.name.startswith("Outer500_Plant_") and
        any((obj.location.x-x)**2+(obj.location.y-y)**2<.01 for x,y in old_roots)):
        continue
    collection.objects.link(obj)
with bpy.data.libraries.load(str(here.parent/"outer_neighborhood/landing_53.blend"),link=True,relative=True) as (source,landing):
    landing.objects=["COL_Outer500_53_LowLanding"]
collection.objects.link(landing.objects[0])
with bpy.data.libraries.load(str(here.parent/"street_blocks/shancheng_lane.blend"),link=True,relative=True) as (source,lane):
    lane.objects=source.objects[:]
for item in lane.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(here.parent/"shancheng_courts/delivery_courts.blend"),link=True,relative=True) as (source,courts):
    courts.objects=source.objects[:]
for item in courts.objects:
    collection.objects.link(item)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here / "city_and_outer.local.blend"),relative_remap=True,compress=True)
