import json,hashlib,statistics
from pathlib import Path
from PIL import Image
p=Path(__file__).resolve().parent
game=p.parents[1]/'project/chongqing_godot_v05'
qa=game/'verification_r24/build11'
def read(f):return json.loads(f.read_bytes())
def sha(f):
    with f.open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
walk=read(qa/'seam_walk.json')
assert walk['passed'] and len(walk['routes'])==4 and walk['install']=={'donors':9,'local_frame':True,'missing':[],'retired':3}
assert read(p/'reopen_final.json')['board_target_quads']==8
assert all(r['max_step']<.7 and all(pt['ok'] for pt in r['goals']) for r in walk['routes'])
out={'source_fingerprints':{},'files':{},'captures':{},'walk':walk,'gpu':{},'geo':{},'regression':{}}
for f in [p/'city_and_block_r24.blend',p/'city_frame.glb',p/'selected.json',game/'assets/street_finish_r24/street_finish.glb',game/'assets/street_finish_r24/finish.json',game/'assets/render_profile_r24.json',game/'scripts/city_frame_r24.gd', game/'shaders/city_envelope_r24.gdshader',game/'shaders/court_canopy_r24.gdshader']:
    out['files'][f.name]={'sha256':sha(f),'bytes':f.stat().st_size}
for name,info in read(p/'sources.json').items():
    if isinstance(info,dict) and 'archive_sha256' in info:out['source_fingerprints'][name]=info['archive_sha256']
for f in sorted((p/'final_views').glob('*.png')):
    with Image.open(f) as im:assert im.size==(1280,720)
    out['captures'][f.name]=sha(f)
assert len(out['captures'])==10
for name in ['smoke','block_test','delivery_end_to_end','corner_walk','walk']:
    data=read(qa/(name+'.json'))
    assert data.get('passed',data.get('success')),name
    out['regression'][name]={'passed':True,'checks':len(data['tests']) if 'tests' in data else None,'metres':data.get('metres'),'sha256':sha(qa/(name+'.json'))}
for variant in ['build10','build11']:
    data=read(qa/('gpu_'+variant)/'native_1080.json')
    out['gpu'][variant]=[{k:v[k] for k in ('view','samples','gpu_p50_ms','gpu_p95_ms','frame_interval_p95_ms')} for v in data['views']]
    assert all(r['samples']==240 for r in out['gpu'][variant])
reg=read(p/'registration.json');out['geo']={'training':reg['train_inliers'],'holdout':reg['test_inliers'],'median_error_native_m':statistics.median(r['xy_error'] for r in reg['pairs']),'max_error_native_m':max(r['xy_error'] for r in reg['pairs'])}
assert set(read(p/'engine_results.json'))=={'seams','smoke','delivery','street','corner','walk'}
assert all(v==0 for v in read(p/'engine_results.json').values())
(p/'verified.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('verified',len(out['captures']),sum(r['metres'] for r in walk['routes']),out['geo'])

