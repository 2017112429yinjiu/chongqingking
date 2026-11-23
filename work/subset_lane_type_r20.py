"""Keep all legacy UI characters and the new notices in an OFL UI subset."""
from pathlib import Path
import hashlib, sys, json, shutil
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'tools/fonttools_r20'))
from fontTools import subset
from fontTools.ttLib import TTFont
P=W/'project/chongqing_godot_v05'
F=W/'assets_incoming/r20_noto'
font=TTFont(F/'NotoSansCJKsc-Regular.otf')
original=set(TTFont(P/'assets/fonts/cq_ui.otf').getBestCmap())
txt=''.join(p.read_text(encoding='utf-8') for p in (P/'scripts').glob('*.gd'))
txt+=''.join(p.read_text(encoding='utf-8-sig') for p in (P/'assets').glob('render_profile*.json'))
print_text=(W/'paint_lane_prints_r20.py').read_text(encoding='utf-8')
need={ord(c) for c in print_text if '\u3400'<=c<='\u9fff'}
for face in ['Regular','Bold']:
    actual=TTFont(F/f'NotoSansCJKsc-{face}.otf').getBestCmap()
    assert not need-actual.keys(),need-actual.keys()
sub=subset.Subsetter()
sub.populate(unicodes=original|{ord(c) for c in txt+print_text})
sub.subset(font)
current='--r21' in sys.argv
name='CQ District UI' if current else 'CQ Lane UI'
ps_name='CQDistrictUI-Regular' if current else 'CQLaneUI-Regular'
for record in font['name'].names:
    if record.nameID in [1,3,4,6,16,17]:
        value=ps_name if record.nameID in [3,6] else ('Regular' if record.nameID==17 else name)
        record.string=value.encode(record.getEncoding())
cff=font['CFF '].cff
cff.fontNames[0]=ps_name
cff.topDictIndex[0].FamilyName=name
cff.topDictIndex[0].FullName=name+' Regular'
dest=P/'assets/fonts'/('cq_district_ui.otf' if current else 'cq_lane_ui.otf')
font.save(dest)
rights=F/'LICENSE.txt'
shutil.copyfile(rights,P/'assets/fonts/R20_OFL.txt')
record={'upstream':'https://github.com/notofonts/noto-cjk','commit':(F/'source_commit.txt').read_text().strip(),'license':'SIL OFL 1.1','derived_font':dest.name,'modifications':'Subset and renamed for the district UI. Full original faces used offline for four original printed designs.','copyright':font['name'].getDebugName(0),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [*F.glob('*.otf'),rights,dest]}}
(P/'assets/fonts'/('R21_font_sources.json' if current else 'R20_font_sources.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('UI font',dest.stat().st_size,'bytes, print glyphs checked',len(need))
