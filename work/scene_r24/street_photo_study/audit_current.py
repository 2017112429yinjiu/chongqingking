from pathlib import Path
import hashlib,json
from PIL import Image
root=Path(__file__).resolve().parent
project=root.parents[1]/'project/chongqing_godot_v05'
qa=project/'verification_r24/build12'
def read(f):return json.loads(f.read_text('utf-8-sig'))
def digest(f):
    with f.open('rb') as src:return hashlib.file_digest(src,'sha256').hexdigest()
def captures(log):
    text=log.read_text('utf-8-sig',errors='replace')
    assert not any(line.startswith(('SCRIPT ERROR','SHADER ERROR','ERROR:')) for line in text.splitlines()),log
    return {k['view']:k for k in [json.loads(line.split(' ',1)[1]) for line in text.splitlines() if line.startswith('CQ_CAPTURE {')]}
before=captures(root/'before.log')|captures(root/'before_extra.log')
after=captures(root/'current_captures.log')
pairs={}
for key,rec in after.items():
    old=before[key]
    for prop in ['position','target','fov','width','height']:assert old[prop]==rec[prop],(key,prop)
    assert rec['save_error']==old['save_error']==0
    assert Image.open(Path(rec['path'])).size==(1280,720)
    pairs[key]={'old':digest(Path(old['path'])),'current':digest(Path(rec['path']))}
frames=read(root/'motion/continuous.json')
assert frames['reached'] and Image.open(root/'走过菜摊.webp').n_frames==frames['captured']
poses=read(root/'verified_supports.json')
assert len(poses)==24 and max(abs(a['diff']) for a in poses)<.002
stats={}
for fn in ['walk','delivery_end_to_end','smoke','seam_walk']:
    result=read(qa/(fn+'.json'))
    assert result.get('passed',result.get('success')),fn
    if 'art_profile' in result:assert result['art_profile']['sha256']==digest(project/'assets/render_profile_r24.json')
    if fn in ['walk','delivery_end_to_end']:
        assert result['runtime_sha256']['res://assets/street_use_r24/workday.glb']==digest(project/'assets/street_use_r24/workday.glb')
    stats[fn]=True
gpu={}
for variant in ['before','current']:
    d=read(qa/'pair_verified'/variant/'native_1080.json')
    if variant=='current':
        assert d['runtime_sha256']['res://assets/street_use_r24/workday.glb']==digest(project/'assets/street_use_r24/workday.glb')
    gpu[variant]=[{k:v[k] for k in ['view','samples','gpu_p50_ms','gpu_p95_ms','frame_interval_p95_ms']} for v in d['views']]
assert len(pairs)==10
reopen=read(root/'editable_reopen.json')
assert reopen['packed_price_card'] and len(reopen['workday'])==16
out={'profile_sha256':digest(project/'assets/render_profile_r24.json'),'engine':'Godot 4.6.3 Forward+','matched_cameras':pairs,'support_points':len(poses),'worst_support_difference_m':max(abs(q['diff']) for q in poses),'motion':{k:v for k,v in frames.items() if k!='samples'},'checks':stats,'gpu_comparison_1080':gpu}
(root/'review_result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='matched_cameras'},ensure_ascii=False))

