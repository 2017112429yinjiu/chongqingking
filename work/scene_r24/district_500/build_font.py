"""Make the portable signs subset from the project's OFL source font."""
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

work = Path(__file__).resolve().parents[2]
out = work / "project/chongqing_godot_v05/assets/district_500"
layout = json.loads((out / "layout.json").read_text(encoding="utf-8"))
text = "".join(place["name"] for place in layout["destinations"])+"0123456789"
text += "".join(sign["text"] for plot in layout.get("plots",[]) for sign in plot.get("trade_signs",[]))
font = TTFont(work / "assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf", recalcTimestamp=False)
writer = subset.Subsetter()
writer.populate(text=text)
writer.subset(font)
name = "CQ District Signs"
ps_name = "CQDistrictSigns-Regular"
for record in font["name"].names:
    if record.nameID in (1,3,4,6,16,17):
        value = ps_name if record.nameID in (3,6) else "Regular" if record.nameID==17 else name
        record.string = value.encode(record.getEncoding())
cff = font["CFF "].cff
cff.fontNames[0] = ps_name
cff.topDictIndex[0].FamilyName = name
cff.topDictIndex[0].FullName = name + " Regular"
font.save(out / "district_signs.otf")
