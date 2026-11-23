"""Apply and identify a reversible high-quality Godot import trial on existing environmental scans."""
from pathlib import Path
import hashlib
import json
import re
import sys

work=Path(__file__).resolve().parent
project=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2]).resolve()
assert work in project.parents and (project/'project.godot').is_file()
out.mkdir(parents=True,exist_ok=True)
manifest=out/'texture_trial.json'
if manifest.exists():raise RuntimeError('Use the existing trial manifest for this candidate.')
consider=('brown_mud_leaves_01','wood_table_worn','concrete_floor_worn_001')
channels=('_diff_2k','_nor_gl_2k','_rough_2k')
changes=[]
for meta in sorted((project/'assets').rglob('*.import')):
    rel=meta.relative_to(project)
    if 'characters' in rel.parts or not any(s in meta.name for s in consider) or not any(s in meta.name for s in channels):continue
    original=meta.read_bytes()
    text=original.decode('utf8')
    if not re.search(r'^compress/mode=0\r?$',text,re.M):continue
    source=Path(str(meta)[:-7])
    record={'path':rel.as_posix(),'image_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'before_import_sha256':hashlib.sha256(original).hexdigest()}
    saved=out/'before'/rel
    saved.parent.mkdir(parents=True,exist_ok=True)
    saved.write_bytes(original)
    # Godot 4.6 desktop VRAM compression; high quality selects BPTC where applicable.
    text=text.replace('compress/mode=0','compress/mode=2').replace('compress/high_quality=false','compress/high_quality=true')
    meta.write_bytes(text.encode('utf8'))
    changes.append(record)
assert len(changes)==32,len(changes)
manifest.write_text(json.dumps({'sources':changes,'scope':'32 environment scan import recipes; original raster bytes retained. Characters, UI, light masks and sky excluded.'},indent=2),encoding='utf8')
