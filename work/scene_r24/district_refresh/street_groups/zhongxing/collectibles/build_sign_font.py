"""Make a small, renamed OFL subset for the market's exterior sign."""
from pathlib import Path
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

font_source = Path(sys.argv[1])
font_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
work = Path(__file__).resolve().parents[5]
target = work / "project/chongqing_godot_v05/assets/district_500/market_signs.otf"
font = TTFont(font_source, fontNumber=font_index, recalcTimestamp=False)
maker = subset.Subsetter()
maker.populate(text="中兴路收藏品交易市场")
maker.subset(font)
name = "CQ Market Signs"
postscript = "CQMarketSigns-Regular"
for record in font["name"].names:
    if record.nameID in (1, 3, 4, 6, 16, 17):
        new_name = postscript if record.nameID in (3, 6) else "Regular" if record.nameID == 17 else name
        record.string = new_name.encode(record.getEncoding())
cff = font["CFF "].cff
cff.fontNames[0] = postscript
cff.topDictIndex[0].FamilyName = name
cff.topDictIndex[0].FullName = name + " Regular"
font.save(target)
