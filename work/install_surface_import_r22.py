"""Install the validated BPTC recipes from the isolated project into the active Godot project."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image

work=Path(__file__).resolve().parent
root=work/'project/chongqing_godot_v05'
trial=work/'gpu_trial_r22'
proof=trial/'verification'

def read(path):return json.loads(path.read_text(encoding='utf8'))
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

old,new=[read(proof/f/'texture_probe.json') for f in ['base','candidate']]
assert len(old['maps'])==len(new['maps'])==32 and new['cached_scan_bytes']<old['cached_scan_bytes']
assert all(a['path']==b['path'] and a['already_loaded'] and b['already_loaded'] and
           (a['width'],a['height'],a['mips'])==(b['width'],b['height'],b['mips']) for a,b in zip(old['maps'],new['maps']))
rows=read(proof/'texture_trial.json')['sources']
captures={}
for frame in read(proof/'native_1080.json')['views']:
    name=frame['view']
    a=root/'verification_r22/native_checked_current'/('1080_'+name+'.png')
    b=proof/a.name
    assert sha(b)==frame['readback_sha256']
    with Image.open(a) as im,Image.open(b) as other:
        assert im.size==other.size==(1920,1080)
        delta=np.asarray(im.convert('RGB'),dtype='int16')-np.asarray(other.convert('RGB'),dtype='int16')
        captures[name]={'active_png_sha256':sha(a),'candidate_png_sha256':sha(b),'mean_absolute_rgb_8bit':float(np.abs(delta).mean())}
if not (work/'checkpoints/R22_district_06/manifest.json').is_file():raise RuntimeError('Prior artist checkpoint missing')
for row in rows:
    path=row['path'];meta=root/path;choice=trial/'project'/path
    assert sha(meta)==row['before_import_sha256'] and sha(Path(str(meta)[:-7]))==row['image_sha256'],path
    assert 'path.bptc=' in choice.read_text(encoding='utf8') and 'compress/mode=2' in choice.read_text(encoding='utf8')
    row['validated_import_sha256']=sha(choice)
for row in rows:
    path=row['path'];shutil.copy2(trial/'project'/path,root/path)
    assert sha(root/path)==row['validated_import_sha256']
record={'revision':'R22_surface_import_01','maps':rows,'source_pixels':'Unchanged','msaa':'2x',
        'probe_mib_before_after':[old['scene_texture_bytes_before_readback']/1048576,new['scene_texture_bytes_before_readback']/1048576],
        'cached_scan_mib_before_after':[old['cached_scan_bytes']/1048576,new['cached_scan_bytes']/1048576],
        'captures':captures}
(root/'assets/roofs_r22/surface_imports.json').write_text(json.dumps(record,indent=2),encoding='utf8')
