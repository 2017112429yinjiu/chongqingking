"""Open the original city, relink its libraries, append the editable outer layer."""
import json
import os
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
group_assets = root / "work/project/chongqing_godot_v05/assets/district_500"
xingchen_plan = json.loads((group_assets / "xingchen.json").read_bytes())
pavilion_plan = json.loads((group_assets / "pavilion62.json").read_bytes())
market_plan = json.loads((group_assets / "collectibles-market.json").read_bytes())
stall_plan = json.loads((group_assets / "market-stall-row.json").read_bytes())
retired = [f"_{oid}_" for oid in layout.get("osm_building_ids", []) +
           [xingchen_plan["way"], *market_plan["mapped_residential_ways"]]]
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
factory_dir = here.parent / "district_refresh/street_groups"
factory_plan = json.loads((group_assets / "match_factory.json").read_bytes())
matix_plan = json.loads((group_assets / "matix_streets.json").read_bytes())
zhongxing_plan = json.loads((group_assets / "zhongxing-retaining.json").read_bytes())
west_court_plan = json.loads((group_assets / "west-court.json").read_bytes())
west_ramp_plan = json.loads((group_assets / "west-ramp.json").read_bytes())
guoco_plan = json.loads((group_assets / "guoco-frontages.json").read_bytes())
public_plan = json.loads((group_assets / "public-edges.json").read_bytes())
public_override = set(public_plan["replacement_meshes"])
public_retired = set(public_plan["retired_objects"])
xingchen_override = set(xingchen_plan["replacement_meshes"] + xingchen_plan["retired_objects"])
pavilion_override = set(pavilion_plan["replacement_meshes"] + pavilion_plan["retired_objects"])
market_override = set(market_plan["replacement_meshes"] + market_plan["retired_objects"])
park57_plan = json.loads((group_assets / "park-plot57.json").read_bytes())
bridge_park_plan = json.loads((group_assets / "bridge-park.json").read_bytes())
park59_plan = json.loads((group_assets / "park-plot59.json").read_bytes())
park61_plan = json.loads((group_assets / "park-plot61.json").read_bytes())
park_finish_plan = json.loads((group_assets / "park-edge-finish.json").read_bytes())
changbin_plan = json.loads((group_assets / "changbin-bend-and-edge.json").read_bytes())
east_plan = None if os.environ.get("CQ_EAST_PARENT") == "1" else json.loads((group_assets / "raijiapo-east-bend.json").read_bytes())
binjiang_plan = None if not east_plan or os.environ.get("CQ_BINJIANG_PARENT") == "1" else json.loads((group_assets / "binjiang-70-73.json").read_bytes())
houci_plan = None if not binjiang_plan or os.environ.get("CQ_HOUCI_PARENT") == "1" else json.loads((group_assets / "houci-77.json").read_bytes())
panda_plan = None if not houci_plan or os.environ.get("CQ_PANDA_PARENT") == "1" else json.loads((group_assets / "panda-15-17.json").read_bytes())
bridge_margins = None if not panda_plan or os.environ.get("CQ_ZHONGXING_PARENT") == "1" else json.loads((group_assets / "zhongxing-bridge-18-21.json").read_bytes())
houci_connectors = None if not bridge_margins or os.environ.get("CQ_HOUCI_14_16_PARENT") == "1" else json.loads((group_assets / "houci-14-16.json").read_bytes())
fenghuangtai = None if not houci_connectors or os.environ.get("CQ_FENGHUANGTAI_11_PARENT") == "1" else json.loads((group_assets / "fenghuangtai-11.json").read_bytes())
wilderness = None if not fenghuangtai or os.environ.get("CQ_WILDERNESS_50_PARENT") == "1" else json.loads((group_assets / "wilderness-50.json").read_bytes())
wilderness_finish = None if not wilderness or os.environ.get("CQ_WILDERNESS_50_FINISH_PARENT") == "1" else json.loads((group_assets / "wilderness-50-finish.json").read_bytes())
nanqu = None if not wilderness or os.environ.get("CQ_NANQU_PARENT") == "1" else json.loads((group_assets / "nanqu-04-06-51.json").read_bytes())
roadside_55 = None if not nanqu or os.environ.get("CQ_CHANGBIN_55_PARENT") == "1" else json.loads((group_assets / "changbin-55.json").read_bytes())
north_edges = None if not roadside_55 or os.environ.get("CQ_NORTH_EDGE_PARENT") == "1" else json.loads((group_assets / "north-38-40-41.json").read_bytes())
liangtingzi = None if not north_edges or os.environ.get("CQ_LIANGTINGZI_PARENT") == "1" else json.loads((group_assets / "liangtingzi-45-46.json").read_bytes())
mati34 = None if not liangtingzi or os.environ.get("CQ_MATI34_PARENT") == "1" else json.loads((group_assets / "mati-34-35.json").read_bytes())
public_zhongxing = None if not mati34 or os.environ.get("CQ_ZHONGXING_PUBLIC_PARENT") == "1" else json.loads((group_assets / "zhongxing-public-10-12-13-22.json").read_bytes())
public_jiefang = None if not public_zhongxing or os.environ.get("CQ_JIEFANG_PUBLIC_PARENT") == "1" else json.loads((group_assets / "jiefang-public-02-24-25-26.json").read_bytes())
public_zhongxing22 = None if not public_zhongxing or os.environ.get("CQ_ZHONGXING22_PARENT") == "1" else json.loads((group_assets / "zhongxing-plaza-22-finish.json").read_bytes())
binjiang_override = set() if not binjiang_plan else set(binjiang_plan["replacement_meshes"] + binjiang_plan["retired_objects"])
east_override = set() if east_plan is None else set(east_plan["replacement_meshes"] + east_plan["retired_objects"]) | binjiang_override
changbin_override = set(changbin_plan["replacement_meshes"] + changbin_plan["retired_objects"]) | east_override
park_finish_override = set(park_finish_plan["replacement_meshes"] + park_finish_plan["retired_objects"]) | changbin_override
park61_override = set(park61_plan["replacement_meshes"] + park61_plan["retired_objects"]) | park_finish_override
park59_override = set(park59_plan["replacement_meshes"] + park59_plan["retired_objects"]) | park61_override
bridge_park_override = set(bridge_park_plan["replacement_meshes"] + bridge_park_plan["retired_objects"]) | park59_override
park57_override = set(park57_plan["replacement_meshes"] + park57_plan["retired_objects"]) | bridge_park_override
later_public_meshes = public_override | public_retired | xingchen_override | pavilion_override | market_override | park57_override
guoco_override = set(guoco_plan["replacement_meshes"])
guoco_retired = set(guoco_plan["retired_objects"])
factory_override = set(factory_plan["replacement_meshes"])
factory_retired = set(factory_plan["retired_objects"])
matix_override = set(matix_plan["replacement_meshes"])
matix_retired = set(matix_plan["retired_objects"])
zhongxing_override = set(zhongxing_plan["replacement_meshes"])
west_court_override = set(west_court_plan["replacement_meshes"])
west_ramp_override = set(west_ramp_plan["replacement_meshes"])
with bpy.data.libraries.load(str(factory_dir / "match_factory.blend"), link=True, relative=True) as (source, factory):
    factory.objects = [name for name in factory_plan["new_meshes"] + factory_plan["replacement_meshes"]
                       if name not in matix_override and name not in guoco_override
                       and name not in later_public_meshes]
for item in factory.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir / "matix/matix_streets.blend"), link=True, relative=True) as (source, matix):
    matix.objects = matix_plan["new_meshes"] + [name for name in matix_plan["replacement_meshes"]
                                                 if name not in zhongxing_override and name not in west_court_override
                                                 and name not in guoco_override and name not in later_public_meshes]
for item in matix.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir / "zhongxing/zhongxing-retaining.blend"), link=True, relative=True) as (source, zhongxing):
    zhongxing.objects = [name for name in zhongxing_plan["replacement_meshes"]
                         if name not in guoco_override and name not in later_public_meshes]
for item in zhongxing.objects:
    collection.objects.link(item)
court_data=json.loads((root / "work/project/chongqing_godot_v05/assets/district_500/historic_courts.json").read_bytes())
old_roots=court_data["superseded_outer_roots"] + guoco_plan["retired_roots_east_north"]
with bpy.data.libraries.load(str(here / "interior_terrain.blend"), link=True, relative=True) as (source, corrected):
    corrected.objects = source.objects[:]
replaced = ({obj.name for obj in corrected.objects} | factory_override | factory_retired | matix_override
            | matix_retired | west_court_override | guoco_override | guoco_retired | later_public_meshes)
for obj in corrected.objects:
    if obj.name not in factory_override | matix_override | west_court_override | guoco_override | later_public_meshes:
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
with bpy.data.libraries.load(str(here / "riverside.blend"), link=True, relative=True) as (source, riverside):
    riverside.objects = list(source.objects)
for item in riverside.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(here.parent / "district_refresh/riverside/west_court/west-court.blend"),
                             link=True, relative=True) as (source, west_court):
    west_court.objects = [name for name in west_court_plan["replacement_meshes"] + west_court_plan["new_meshes"]
                          if name not in guoco_override and name not in later_public_meshes
                          and name not in west_ramp_override]
for item in west_court.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir.parent / "riverside/west_ramp/west-ramp.blend"),
                             link=True, relative=True) as (_, west_ramp):
    west_ramp.objects = [name for name in west_ramp_plan["replacement_meshes"] + west_ramp_plan["new_meshes"]
                         if name not in park57_override]
for item in west_ramp.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir / "guoco/guoco-frontages.blend"), link=True, relative=True) as (source, guoco):
    guoco.objects = [name for name in guoco_plan["replacement_meshes"] + guoco_plan["new_meshes"]
                     if name not in later_public_meshes]
for item in guoco.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir / "matix/public-edges.blend"), link=True, relative=True) as (_, public):
    public.objects = [name for name in public_plan["replacement_meshes"] + public_plan["new_meshes"]
                      if name not in xingchen_override | pavilion_override | market_override | park57_override]
for item in public.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir / "xingchen/xingchen.blend"), link=True, relative=True) as (_, xingchen):
    xingchen.objects = [name for name in xingchen_plan["replacement_meshes"] + xingchen_plan["new_meshes"]
                        if name not in pavilion_override | market_override | park57_override]
for item in xingchen.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir.parent / "riverside/pavilion62/pavilion62.blend"),
                             link=True, relative=True) as (_, pavilion):
    pavilion.objects = [name for name in pavilion_plan["replacement_meshes"] + pavilion_plan["new_meshes"]
                        if name not in market_override | park57_override]
for item in pavilion.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir / "zhongxing/collectibles/collectibles-market.blend"),
                             link=True, relative=True) as (_, market):
    market.objects = [name for name in market_plan["replacement_meshes"] + market_plan["new_meshes"]
                      if name not in park57_override and name not in stall_plan["replacement_meshes"]] + ["Huihuigou_Sign_Anchor"]
for item in market.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir / "zhongxing/collectibles/stall_row/stall-row.blend"),
                             link=True, relative=True) as (_, stalls):
    stalls.objects = stall_plan["replacement_meshes"] + stall_plan["new_meshes"]
for item in stalls.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir.parent / "riverside/park_plot57/park-plot57.blend"),
                             link=True, relative=True) as (_, park57):
    park57.objects = [name for name in park57_plan["replacement_meshes"] + park57_plan["new_meshes"]
                      if name not in bridge_park_override]
for item in park57.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir.parent / "riverside/bridge_58_61/bridge-park.blend"),
                             link=True, relative=True) as (_, bridge_park):
    bridge_park.objects = [name for name in bridge_park_plan["replacement_meshes"] + bridge_park_plan["new_meshes"]
                           if name not in park59_override]
for item in bridge_park.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir.parent / "riverside/park_plot59/park-plot59.blend"),
                             link=True, relative=True) as (_, park59):
    park59.objects = [name for name in park59_plan["replacement_meshes"] + park59_plan["new_meshes"]
                      if name not in park61_override]
for item in park59.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir.parent / "riverside/park_plot61/park-plot61.blend"),
                             link=True, relative=True) as (_, park61):
    park61.objects = [name for name in park61_plan["replacement_meshes"] + park61_plan["new_meshes"]
                      if name not in park_finish_override]
for item in park61.objects:
    collection.objects.link(item)
with bpy.data.libraries.load(str(factory_dir.parent / "riverside/park_edge_finish/park-edge-finish.blend"),
                             link=True, relative=True) as (_, park_finish):
    park_finish.objects = [name for name in park_finish_plan["replacement_meshes"] + park_finish_plan["new_meshes"]
                           if name not in changbin_override]
for item in park_finish.objects:
    collection.objects.link(item)
for name,scale in park_finish_plan["tree_local_scale"].items():
    linked = collection.objects[name]
    editable = linked.copy()
    collection.objects.unlink(linked)
    editable.name = name
    editable.scale = tuple(a*b for a,b in zip(editable.scale,scale))
    collection.objects.link(editable)
for spec in park_finish_plan["planted_trees"]:
    plant = collection.objects[spec["donor"]].copy()
    plant.name = spec["name"]
    plant.location = spec["east_north_up"]
    plant.rotation_euler.z += spec["yaw_offset_rad"]
    plant.scale *= spec["scale"]
    collection.objects.link(plant)
with bpy.data.libraries.load(str(factory_dir.parent / "riverside/plots_63_66/changbin-bend-and-edge.blend"),
                             link=True, relative=True) as (_, changbin):
    changbin.objects = [name for name in changbin_plan["replacement_meshes"] + changbin_plan["new_meshes"]
                        if name not in east_override]
for item in changbin.objects:
    collection.objects.link(item)
if east_plan:
    with bpy.data.libraries.load(str(factory_dir.parent / "riverside/east_bend/raijiapo-east-bend.blend"),
                                 link=True, relative=True) as (_, east_bend):
        east_bend.objects = [name for name in east_plan["replacement_meshes"] + east_plan["new_meshes"]
                             if name not in binjiang_override]
    for item in east_bend.objects:
        collection.objects.link(item)
    spec = east_plan["tree"]
    plant = collection.objects[spec["donor"]].copy()
    plant.name = spec["name"]
    plant.location = spec["enu"]
    plant.scale *= .89
    plant.rotation_euler.z += .83
    collection.objects.link(plant)
if binjiang_plan:
    for name in binjiang_plan["retired_runtime_frontage"]:
        if name in bpy.context.scene.objects:
            bpy.context.scene.objects[name].hide_render=True
            bpy.context.scene.objects[name].hide_set(True)
    with bpy.data.libraries.load(str(factory_dir.parent / "riverside/binjiang/binjiang-70-73.blend"),
                                 link=True, relative=True) as (_, binjiang):
        binjiang.objects = binjiang_plan["replacement_meshes"] + binjiang_plan["new_meshes"]
    for item in binjiang.objects:
        collection.objects.link(item)
if houci_plan:
    for name in houci_plan["replacement_meshes"] + houci_plan["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "houci_77/houci-77.blend"),
                                 link=True, relative=True) as (_, houci):
        houci.objects = houci_plan["replacement_meshes"] + houci_plan["new_meshes"]
    for item in houci.objects:
        collection.objects.link(item)
if panda_plan:
    for name in panda_plan["replacement_meshes"] + panda_plan["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "panda_15_17/panda-15-17.blend"),
                                 link=True, relative=True) as (_, panda):
        panda.objects = panda_plan["replacement_meshes"] + panda_plan["new_meshes"]
    for item in panda.objects:
        collection.objects.link(item)
    for spec in panda_plan["trees"]:
        plant = collection.objects[spec["donor"]].copy()
        plant.name = spec["name"]
        plant.location = spec["enu"]
        plant.rotation_euler.z += spec["yaw"]
        plant.scale *= spec["scale"]
        collection.objects.link(plant)
if bridge_margins:
    for name in bridge_margins["replacement_meshes"] + bridge_margins["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "zhongxing_bridge_18_21/zhongxing-bridge-18-21.blend"),
                                 link=True, relative=True) as (_, margins):
        margins.objects = bridge_margins["replacement_meshes"] + bridge_margins["new_meshes"]
    for item in margins.objects:
        collection.objects.link(item)
if houci_connectors:
    for name in houci_connectors["replacement_meshes"] + houci_connectors["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "houci_14_16/houci-14-16.blend"),
                                 link=True, relative=True) as (_, connectors):
        connectors.objects = houci_connectors["replacement_meshes"] + houci_connectors["new_meshes"]
    for item in connectors.objects:
        collection.objects.link(item)
if fenghuangtai:
    for name in fenghuangtai["replacement_meshes"] + fenghuangtai["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "fenghuangtai_11/fenghuangtai-11.blend"),
                                 link=True, relative=True) as (_, junction):
        junction.objects = fenghuangtai["replacement_meshes"] + fenghuangtai["new_meshes"]
    for item in junction.objects:
        collection.objects.link(item)
if wilderness:
    for name in wilderness["replacement_meshes"] + wilderness["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "wilderness_50/wilderness-50.blend"),
                                 link=True, relative=True) as (_, edge):
        edge.objects = wilderness["replacement_meshes"] + wilderness["new_meshes"]
    for item in edge.objects:
        collection.objects.link(item)
if wilderness_finish:
    for name in wilderness_finish["replacement_meshes"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "wilderness_50/wilderness-50-finish.blend"),
                                 link=True, relative=True) as (_, finish):
        finish.objects = wilderness_finish["replacement_meshes"] + wilderness_finish["new_meshes"]
    for item in finish.objects:
        collection.objects.link(item)
if nanqu:
    for name in nanqu["replacement_meshes"] + nanqu["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "nanqu_04_06_51/nanqu-04-06-51.blend"),
                                 link=True, relative=True) as (_, site):
        site.objects = nanqu["replacement_meshes"] + nanqu["new_meshes"]
    for item in site.objects:
        collection.objects.link(item)
    for spec in nanqu.get("rebase_trees", []):
        item=collection.objects[spec["name"]]
        moved=item.copy()
        collection.objects.unlink(item)
        collection.objects.link(moved)
        moved.name=spec["name"]
        moved.location.z+=spec["shift_z"]
if roadside_55:
    for name in roadside_55["replacement_meshes"] + roadside_55["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(here.parent / "district_refresh/riverside/roadside_55/changbin-55.blend"),
                                 link=True, relative=True) as (_, roadside):
        roadside.objects = roadside_55["replacement_meshes"] + roadside_55["new_meshes"]
    for item in roadside.objects:
        collection.objects.link(item)
if north_edges:
    for name in north_edges["replacement_meshes"] + north_edges["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "north_edges/north-38-40-41.blend"),
                                 link=True, relative=True) as (_, public_north):
        public_north.objects = north_edges["replacement_meshes"] + north_edges["new_meshes"]
    for item in public_north.objects:
        collection.objects.link(item)
if liangtingzi:
    with bpy.data.libraries.load(str(factory_dir / "liangtingzi_45_46/liangtingzi-45-46.blend"),
                                 link=True, relative=True) as (_, public_lane):
        public_lane.objects = liangtingzi["new_meshes"]
    for item in public_lane.objects:
        collection.objects.link(item)
    for entry in liangtingzi.get("trees", []):
        planted=collection.objects[entry["donor"]].copy()
        planted.name=entry["name"]
        planted.location=entry["enu"]
        planted.scale*=entry["scale"]
        planted.rotation_euler.z+=entry["yaw"]
        collection.objects.link(planted)
if mati34:
    with bpy.data.libraries.load(str(factory_dir / "matix_34_35/mati-34-35.blend"),
                                 link=True, relative=True) as (_, mati_margin):
        mati_margin.objects = mati34["new_meshes"]
    for item in mati_margin.objects:
        collection.objects.link(item)
if public_zhongxing:
    for name in public_zhongxing["replacement_meshes"] + public_zhongxing["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "zhongxing_public_10_12_13_22/zhongxing-public-10-12-13-22.blend"),
                                 link=True, relative=True) as (_, south_margin):
        south_margin.objects = public_zhongxing["new_meshes"] + public_zhongxing["replacement_meshes"]
    for item in south_margin.objects:
        collection.objects.link(item)
    for entry in public_zhongxing["trees"]:
        planted=collection.objects[entry["donor"]].copy()
        planted.name=entry["name"]
        planted.location=entry["enu"]
        planted.scale*=entry["scale"]
        planted.rotation_euler.z+=entry["yaw"]
        collection.objects.link(planted)
if public_jiefang:
    for name in public_jiefang["replacement_meshes"] + public_jiefang["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "jiefang_public_24_25_26/jiefang-public-02-24-25-26.blend"),
                                 link=True, relative=True) as (_, jiefang_margin):
        jiefang_margin.objects = public_jiefang["new_meshes"] + public_jiefang["replacement_meshes"]
    for item in jiefang_margin.objects:
        collection.objects.link(item)
if public_zhongxing22:
    for name in public_zhongxing22["replacement_meshes"] + public_zhongxing22["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "zhongxing_plaza22_finish/zhongxing-plaza-22-finish.blend"),
                                 link=True, relative=True) as (_, plaza_apron):
        plaza_apron.objects = public_zhongxing22["new_meshes"] + public_zhongxing22["replacement_meshes"]
    for item in plaza_apron.objects:
        collection.objects.link(item)
    for entry in public_zhongxing22["trees"]:
        planted=collection.objects[entry["donor"]].copy()
        planted.name=entry["name"]
        planted.location=entry["enu"]
        planted.scale*=entry["scale"]
        planted.rotation_euler.z+=entry["yaw"]
        collection.objects.link(planted)
if public_jiefang and os.environ.get("CQ_WESTERN_PUBLIC_PARENT") != "1":
    western = json.loads((group_assets / "western-public-30-31-33-49.json").read_bytes())
    for name in western["replacement_meshes"] + western["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "western_public_30_31_33_49/western-public-30-31-33-49.blend"),
                                 link=True, relative=True) as (_, western_margin):
        western_margin.objects = western["new_meshes"] + western["replacement_meshes"]
    for item in western_margin.objects:
        collection.objects.link(item)
if public_jiefang and os.environ.get("CQ_JIEFANG_GATE25_PARENT") != "1":
    gate25 = json.loads((group_assets / "jiefang-gate25-finish.json").read_bytes())
    for name in gate25["replacement_meshes"] + gate25["retired_objects"]:
        collection.objects.unlink(collection.objects[name])
    with bpy.data.libraries.load(str(factory_dir / "jiefang_gate25_finish/jiefang-gate25-finish.blend"),
                                 link=True, relative=True) as (_, gate_model):
        gate_model.objects = gate25["new_meshes"] + gate25["replacement_meshes"]
    for item in gate_model.objects:
        collection.objects.link(item)
grade_source = factory_dir / "nanqu_rail_grade/nanqu-rail-grade.blend"
grade_manifest = group_assets / "nanqu-rail-grade.json"
nanqu_grade = bool(nanqu and grade_source.exists() and grade_manifest.exists()
                   and os.environ.get("CQ_NANQU_RAIL_PARENT") != "1")
if nanqu_grade:
    controls = json.loads(grade_manifest.read_bytes())
    donor_names = set(controls["corrected_meshes"])
    source_names = donor_names | {"R24_FlyoverBox_R24_link_concrete"}
    for obj in list(bpy.context.scene.objects):
        if obj.name.replace(".", "_") in source_names:
            for owner in list(obj.users_collection):
                owner.objects.unlink(obj)
    with bpy.data.libraries.load(str(grade_source), link=True, relative=True) as (archive, layer):
        layer.objects = [name for name in archive.objects if name.startswith(("Grade__", "COL_NanquGrade_", "NanquGrade_"))]
        assert donor_names <= {name.removeprefix("Grade__") for name in layer.objects}
    for obj in layer.objects:
        collection.objects.link(obj)
bpy.context.preferences.filepaths.save_version=0
output_name = "city_and_outer.local.blend" if nanqu else (
    "city_and_outer.before_nanqu.local.blend" if wilderness else
    "city_and_outer.before_wilderness_50.local.blend" if fenghuangtai else
    "city_and_outer.before_fenghuangtai_11.local.blend" if houci_connectors else
    "city_and_outer.before_houci_14_16.local.blend" if bridge_margins else
    "city_and_outer.before_zhongxing_18_21.local.blend" if panda_plan else
    "city_and_outer.before_panda.local.blend" if houci_plan else
    "city_and_outer.before_houci.local.blend" if binjiang_plan else
    "city_and_outer.before_binjiang.local.blend" if east_plan else "city_and_outer.before_east.local.blend")
if nanqu_grade:
    output_name = os.environ.get("CQ_NANQU_GRADE_OUTPUT", "city_and_outer.nanqu_grade.local.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(here / output_name),relative_remap=True,compress=True)
