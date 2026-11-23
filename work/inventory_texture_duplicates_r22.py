"""Locate exact duplicate image sources without assuming that all copies reside on the GPU."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import re
from PIL import Image

work=Path(__file__).resolve().parent
project=work/'project/chongqing_godot_v05'
groups=defaultdict(list)
for path in (project/'assets').rglob('*'):
    if path.suffix.lower() not in {'.png','.jpg','.jpeg','.webp'}:continue
    with path.open('rb') as stream:
        groups[hashlib.file_digest(stream,'sha256').hexdigest()].append(path)
duplicates=[]
for digest,files in groups.items():
    if len(files)<2:continue
    with Image.open(files[0]) as raster:
        size=list(raster.size)
    paths=[]
    for image in sorted(files):
        settings=Path(str(image)+'.import')
        imports=[]
        if settings.exists():
            for target in re.findall(r'^path(?:\.[\w]+)?="res://([^"]+)"',settings.read_text(encoding='utf8'),re.M):
                compiled=project/target
                if compiled.exists():imports.append({'path':target,'disk_bytes':compiled.stat().st_size})
        paths.append({'path':image.relative_to(project).as_posix(),'godot_imports':imports})
    duplicates.append({'image_sha256':digest,'size':size,'files':paths})
duplicates.sort(key=lambda row:(-len(row['files']),row['files'][0]['path']))
report={'images_examined':sum(len(v) for v in groups.values()),'duplicate_groups':len(duplicates),
        'scope':'Identical source bytes; disk imports can differ by sampler/format. This does not measure GPU residency.',
        'groups':duplicates}
out=project/'verification_r22/current/texture_duplicates.json'
out.write_text(json.dumps(report,indent=2),encoding='utf8')
print(report['images_examined'],report['duplicate_groups'])
