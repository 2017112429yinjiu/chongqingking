"""Retain the original HUD repertoire and add text for the first playable shift."""
import hashlib
import json
from pathlib import Path
import sys

work = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(work / "tools/fonttools_r20"))
from fontTools import subset
from fontTools.ttLib import TTFont

project = work / "project/chongqing_godot_v05"
fonts = project / "assets/fonts"
source = work / "assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf"
old = TTFont(fonts / "cq_district_ui.otf")
full = TTFont(source)
text = "".join((project / "scripts" / name).read_text("utf8") for name in ("day_one.gd", "lunch_run.gd", "passage_order.gd", "blue_stair.gd", "mentor_demonstration.gd", "shift_collection_shelf.gd", "gameplay.gd", "main.gd"))
chars = set(old.getBestCmap()) | {ord(c) for c in text}
pick = subset.Subsetter()
pick.populate(unicodes=chars)
pick.subset(full)
for record in full["name"].names:
    if record.nameID in (1, 3, 4, 6, 16, 17):
        name = "CQFirstShift-Regular" if record.nameID in (3, 6) else ("Regular" if record.nameID == 17 else "CQ First Shift")
        record.string = name.encode(record.getEncoding())
cff = full["CFF "].cff
cff.fontNames[0] = "CQFirstShift-Regular"
cff.topDictIndex[0].FamilyName = "CQ First Shift"
cff.topDictIndex[0].FullName = "CQ First Shift Regular"
output = fonts / "first_shift.otf"
full.save(output)
metadata = json.loads((fonts / "R21_font_sources.json").read_text("utf8"))
metadata["derived_font"] = output.name
metadata["modifications"] = "Subset and renamed from existing Noto Sans CJK SC Regular for the first-shift HUD and instructor label."
metadata["files"] = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in [source, fonts/"R20_OFL.txt", output]}
(fonts/"first_shift_sources.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n","utf8")
