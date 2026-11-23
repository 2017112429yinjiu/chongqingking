"""Internal source/evidence checkpoint. This does not create a delivery archive."""
from pathlib import Path
import json,hashlib,shutil,sys,datetime
root=Path(__file__).resolve().parent;game=root/'project/chongqing_godot_v05';evidence=game/'verification_r18'
version=int(sys.argv[1]);movie=sys.argv[2];source=root/'characters/rider_r18_trial'
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
vehicle=read(evidence/'rider_current/report.json');performance=read(evidence/'performance.json');motion=read(root/f'audit/{movie}_metadata.json')
assert vehicle['passed']
for key,path in [('rider','assets/characters/rider_r18.glb'),('rider_import','assets/characters/rider_r18.glb.import'),('vehicle','assets/vehicles/scooter_r18.glb'),('controller','scripts/scooter_controller.gd'),('visual','scripts/scooter_visual.gd')]:
    assert vehicle[key+'_sha256']==sha(game/path),(key,'GPU QA mismatch')
for key in ['rider','vehicle']:assert performance[key+'_sha256']==vehicle[key+'_sha256']
for key in ['rider','vehicle','rider_import']:assert motion[key+'_sha256']==vehicle[key+'_sha256']
for key in ['scooter_controller','scooter_visual','gameplay']:assert motion['scripts'][key]==sha(game/f'scripts/{key}.gd')
assert read(evidence/'gameplay_test.json')['passed'] and read(evidence/'delivery_end_to_end.json')['passed']
if version>=9:
    for path in ['gameplay_test.json','delivery_end_to_end.json']:
        check=read(evidence/path)
        for key in ['rider','vehicle','controller']:assert check[key+'_sha256']==vehicle[key+'_sha256'],(path,key)
    contact_audit=read(source/'contact_audit.json')
    assert contact_audit['passed'] and contact_audit['source_sha256']==sha(source/'rider_authoring.blend')
for event in motion['events']:
    for key in ['enter','park','exit']:
        if key in event:assert event[key],(key,'movie state transition failed')
report={'status':'Internal iteration only; user has not accepted cinematic quality','vehicle_build':version,'recorded_at':datetime.datetime.now().astimezone().isoformat(),'rider_qa':vehicle,'performance':performance,'movie':motion,'source':{},'gameplay_tests':len(read(evidence/'gameplay_test.json')['tests']),'delivery':read(evidence/'delivery_end_to_end.json'),'reviewed_source_frames':[75,180,315] if version>=9 else [75,180,290],'limitations':['No full-body mount/dismount animation','Static authored shoe contacts; cross-slope foot fitting unfinished','No exhaustive body self-collision','Original scooter shell and box still crude','Player rider is not autonomous NPC simulation','Current shopkeeper20 retained; no cinematic approval']}
checkpoint=root/f'checkpoints/R18_vehicle_{version:02}';checkpoint.mkdir(parents=True,exist_ok=True)
for path in [source/'rider_authoring.blend',source/'scooter_articulated.blend',source/'build_report.json',root/'build_rider_trial.py',root/'install_rider_trial.py',root/'configure_rider_import.py',source/'contact_audit.json']:
    report['source'][path.name]=sha(path);shutil.copy2(path,checkpoint/path.name)
for relative in ['scripts/scooter_controller.gd','scripts/scooter_visual.gd','scripts/gameplay.gd','scripts/qa_rider.gd','scripts/qa_rider_motion.gd','scripts/main.gd','assets/characters/rider_r18.glb','assets/characters/rider_r18.glb.import','assets/characters/rider_r18_provenance.json','assets/characters/ROCKETBOX_MIT_LICENSE.txt','assets/vehicles/scooter_r18.glb','assets/CREDITS.txt']:
    dst=checkpoint/'game'/relative;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(game/relative,dst)
shutil.copytree(evidence/'rider_current',checkpoint/'rider_current',dirs_exist_ok=True)
for name in ['gameplay_test.json','delivery_end_to_end.json','performance.json']:shutil.copy2(evidence/name,checkpoint/name)
for path in [evidence/'vehicle_review_summary.json',checkpoint/'review_summary.json']:path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('INTERNAL_CHECKPOINT',version,'rider tests',len(vehicle['tests']),'gameplay',report['gameplay_tests'],'movie',motion['frames'])
