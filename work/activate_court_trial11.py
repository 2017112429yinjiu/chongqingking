"""Activate the slope-fitted source after the tenth internal run has a complete record."""
from pathlib import Path
import hashlib
import json
import shutil

W=Path(__file__).resolve().parent
P=W/'project/chongqing_godot_v05'
V=P/'verification_r20'
C=V/'current'
trial=W/'characters/court_resident_trial11'
active=W/'characters/court_resident'
model=P/'assets/characters/court_resident'
old=W/'checkpoints/R20_resident_10'
old.mkdir(parents=True,exist_ok=True)
profile=P/'assets/render_profile_r20.json'
data=json.loads(profile.read_text())
assert data['art_revision']=='R20_lane_10_internal'
current_sha=hashlib.sha256((model/'court_resident.glb').read_bytes()).hexdigest()
for name in ['lane_test','street_test','gameplay_test','delivery_end_to_end','survey','performance']:
    record=json.loads((C/(name+'.json')).read_text())
    assert record.get('passed',name=='performance') and record['art_profile']['revision']==data['art_revision']
    assert record['court_resident']['model']==current_sha
gpu=json.loads((V/'resident_court_gpu/performance.json').read_text())
assert gpu['court_resident']['model']==current_sha and gpu['art_profile']['revision']==data['art_revision']
for target in [active/'court_resident.blend',active/'motion_fit.json',profile,P/'scripts/court_resident.gd',P/'scripts/qa_court_resident.gd',model/'court_resident.glb',model/'bench_fit.json']:
    dest=old/target.relative_to(W);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dest)
for source,dest in [(C,V/'trial10'),(V/'resident_court_gpu',old/'court_gpu'),(V/'resident_meter_comparison',old/'meter_comparison')]:
    shutil.copytree(source,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.import'))
for name in ['court_resident.blend','motion_fit.json']:shutil.copy2(trial/name,active/name)
for file in (trial/'runtime').iterdir():
    if file.is_file():shutil.copy2(file,model/file.name)
for settings in model.glob('*.png.import'):
    original=settings.read_text(encoding='utf-8')
    updated=original.replace('compress/mode=0','compress/mode=2').replace('compress/high_quality=false','compress/high_quality=true')
    assert 'compress/mode=2' in updated
    settings.write_text(updated,encoding='utf-8')
for name in ['court_resident.gd','qa_court_resident.gd']:shutil.copy2(trial/name,P/'scripts'/name)
shutil.copy2(trial/'contact_sweep.json',C/'resident_motion/contact_sweep.json')
data['art_revision']='R20_lane_11_internal'
profile.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
print('Source and runtime installed from measured trial')
