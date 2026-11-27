"""Reopen the exact market increment and confirm editable stock and textured surfaces."""
import json

import bpy

objects = bpy.context.scene.objects
names = (
    "COL_Huihuigou_MarketFurnishings",
    "Huihuigou_TerrazzoPaving",
    "Huihuigou_WainscotAndShutters",
    "Huihuigou_SuspendedDuctsAndConduit",
    "Huihuigou_EntryShoulderAndNosing",
)
checks = {}
for name in names:
    obj = objects[name]
    assert obj.data.uv_layers.active is not None,name
    checks[name] = {"dimensions_m":list(obj.dimensions),"polygons":len(obj.data.polygons),
                    "materials":[mat.name for mat in obj.data.materials]}
    assert checks[name]["polygons"] > 100,name
stock = checks[names[0]]["materials"]
assert all(any(text in material for material in stock)
           for text in ("fan","washer porthole","CRT glass","clear glass","aluminium"))
authored = bpy.data.images["Market terrazzo authored from worn concrete"]
assert tuple(authored.size)==(256,256) and authored.packed_file
print("CQ_MARKET_ART_SOURCE",json.dumps(checks))
