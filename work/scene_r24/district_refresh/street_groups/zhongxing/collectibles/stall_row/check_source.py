"""Reopen the stall increment and check that stock geometry outside the east bay is unchanged."""
from collections import Counter
import json
from pathlib import Path

import bpy

HERE=Path(__file__).resolve().parent
STOCK="COL_Huihuigou_MarketFurnishings"
parts=("Huihuigou_EastRowGreenGlaze","Huihuigou_EastRowSteelShopfront","Huihuigou_EastRowPrintedCards")
scene=bpy.context.scene
assert all(name in scene.objects for name in parts)
letters=[obj for obj in scene.objects if obj.type=="FONT" and obj.name.startswith("Market stall ")]
assert len(letters)==5 and all(obj.data.font.packed_file for obj in letters)

if bpy.data.filepath.endswith("city_and_outer.local.blend"):
    assert scene.objects[STOCK].library.filepath.endswith("/stall-row.blend")
    assert scene.objects["COL_Park57_NorthDeckWallSeal"].library.filepath.endswith("/park-plot57.blend")
else:
    current=scene.objects[STOCK]
    assets=HERE.parents[5]/"project/chongqing_godot_v05/assets/district_500"
    affected=json.loads((assets/"market-stall-row.json").read_bytes())["local_bounds_east_north"]
    with bpy.data.libraries.load(str(HERE.parent/"collectibles-market.blend"),link=False) as (_, donor):
        donor.objects=[STOCK]
    def outside_stock(obj):
        result=Counter()
        for poly in obj.data.polygons:
            x,n,_=poly.center
            if any(a<=x<=b and c<=n<=d for (a,b),(c,d) in affected):
                continue
            points=[tuple(round(value,5) for value in obj.data.vertices[i].co) for i in poly.vertices]
            result[tuple(sorted(points))]+=1
        return result
    original=outside_stock(donor.objects[0])
    assert original==outside_stock(current)
    print("CQ_STALL_STOCK_FACES_IDENTICAL_OUTSIDE_BAY",sum(original.values()))
print("CQ_STALL_REOPEN",bpy.app.version_string,len(scene.objects),len(bpy.data.libraries),
      [obj.data.body for obj in letters])
