"""Bind repeated viewport timings to their camera transforms and native framebuffer images."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw

work=Path(__file__).resolve().parent
project=work/'project/chongqing_godot_v05'
evidence=project/'verification_r22'
groups=['perf_reference','current','native_repeat_current','native_repeat_base','native_checked_current','native_aa_trial']
sessions={group:json.loads((evidence/group/'native_1080.json').read_text(encoding='utf8')) for group in groups}
results={}
for group,session in sessions.items():
    assert session['framebuffer']==[1920,1080] and session['scale']==1 and session['native_window_3d_disabled']
    for row,ref in zip(session['views'],sessions['current']['views']):
        assert all(row[k]==ref[k] for k in ['view','position','fov','samples'])
        if 'readback_sha256' in row:
            file=evidence/group/('1080_'+row['view']+'.png')
            with file.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==row['readback_sha256']
            with Image.open(file) as image:assert image.size==(1920,1080)
        results.setdefault(row['view'],{})[group]=row['gpu_p95_ms']
report={'device':sessions['current']['gpu'],'gpu_p95_ms':results,'framebuffer':[1920,1080],'samples_per_view_per_launch':240,
        'run_order':['perf_reference','current','native_repeat_current','native_repeat_base','native_checked_current','native_aa_trial'],
        'scope':'Independent application launches, same fixed camera, root 3D disabled. Windows desktop GPU load and memory vary between launches. Alternate AA is diagnostic only.'}
(evidence/'current/native_timing_comparison.json').write_text(json.dumps(report,indent=2),encoding='utf8')
out=Image.new('RGB',(1208,706),'#191918')
draw=ImageDraw.Draw(out)
for i,(view,rect) in enumerate([('central_steps',(200,50,800,370)),('r22_river_street',(650,520,1250,840))]):
    for j,group in enumerate(['native_checked_current','native_aa_trial']):
        x=j*608;y=i*353
        with Image.open(evidence/group/('1080_'+view+'.png')) as im:out.paste(im.crop(rect),(x,y+29))
        draw.text((x+6,y+7),['MSAA 2x','FXAA'][j]+'  |  '+view+'  |  native pixels',fill='#e9e7da')
out.save(evidence/'native_aa_trial/edges_comparison.png')
