"""Subset Noto Sans CJK SC Bold for the editable Blender stall signs (SIL OFL 1.1)."""
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTCollection

source=TTCollection(sys.argv[1])
font=next(f for f in source.fonts if f["name"].getDebugName(1)=="Noto Sans CJK SC")
font.recalcTimestamp=False
builder=subset.Subsetter()
builder.populate(text="旧电器回收音响寄售台扇碟机 35640元")
builder.subset(font)
family,postscript="CQ Stall Labels","CQStallLabels-Bold"
for record in font["name"].names:
    if record.nameID in (1,3,4,6,16,17):
        name=postscript if record.nameID in (3,6) else "Bold" if record.nameID==17 else family
        record.string=name.encode(record.getEncoding())
cff=font["CFF "].cff
cff.fontNames[0]=postscript
cff.topDictIndex[0].FamilyName=family
cff.topDictIndex[0].FullName=family+" Bold"
font.save(Path(sys.argv[2]))
