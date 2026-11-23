"""Promote verified R24 runtime files only; preserve each original before replacement."""
from pathlib import Path
import hashlib,json,shutil,os
w=Path(__file__).resolve().parent;s=w/'scene_r24'
src=s/'playtest';dst=w/'project/chongqing_godot_v05';backup=s/'prior_active_files'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
walk=json.loads((src/'verification_r24/junction05/walk.json').read_text(encoding='utf8'))
assert walk['success'] and walk['counters_block'] and walk['bridge_top_hits']==49 and len(walk['waypoints'])==15
road=json.loads((src/'verification_r24/junction05/traffic.json').read_text(encoding='utf8'))
corner=json.loads((src/'verification_r24/junction05/corner_walk.json').read_text(encoding='utf8'))
assert road['passed'] and len(road['parked_wheels'])==12 and road['live']['soffit_hits']>0
assert road['runtime_sha256']['res://assets/frontage_r24/frontage.glb']==sha(src/'assets/frontage_r24/frontage.glb')
assert corner['passed'] and len(corner['checkpoints'])==24
profile=json.loads((src/'assets/render_profile_r24.json').read_text(encoding='utf8'))
if profile.get('washcloth_shader'):
    reviewed=src/'verification_r24/scan10b'
    cloth=json.loads((reviewed/'cotton.json').read_text(encoding='utf8'))
    motion=json.loads((reviewed/'cloth_mask_check.json').read_text(encoding='utf8'))
    assert cloth['passed'] and motion['mesh_pin_and_hem_rows_inspected']==15
    assert max(motion['changed_silhouette_pixels_vs_phase_0']['peg_edge'])<=2
    for rel in [profile['washcloth_shader'],'res://assets/frontage_r24/terry_pile.png','res://scripts/block_r23.gd']:
        assert cloth['runtime_sha256'][rel]==sha(src/rel.removeprefix('res://'))
source=json.loads((s/'source_reopened.json').read_text(encoding='utf8'))
assert source['sha256']==sha(s/'chongqing_district.blend')
files=['scripts/explorer.gd','scripts/main.gd','scripts/qa_block_r23.gd','scripts/qa_context.gd','scripts/block_r23.gd','assets/viewpoints.json','assets/render_profile_r24.json']
files += [p.relative_to(src).as_posix() for folder,pattern in [('scripts','frontage_r24.gd*'),('shaders','*r24.gdshader*'),('assets/frontage_r24','*'),('source_data/east_r24','*')] for p in (src/folder).glob(pattern) if p.is_file()]
files=list(dict.fromkeys(files))
old=json.loads((w/'scene_r23/active_install.json').read_text(encoding='utf8'))
installed=s/'active_install.json'
records=json.loads(installed.read_text(encoding='utf8')) if installed.exists() else {}
for rel in files:
    target=dst/rel;incoming=src/rel;prev=sha(target)
    if rel in records:assert prev in [records[rel]['installed'],records[rel]['prior']],rel
    elif rel in old:assert prev==old[rel]['installed'],rel
    if target.exists() and not (backup/rel).exists() and prev!=sha(incoming):
        (backup/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup/rel)
    if rel not in records:records[rel]=dict(prior=prev,installed=None)
    records[rel]['installed']=sha(incoming)
for rel in sorted(files,key=lambda path: path=='scripts/main.gd'):
    target=dst/rel; target.parent.mkdir(parents=True,exist_ok=True)
    if sha(target)!=records[rel]['installed']:
        pending=target.with_name(target.name+'.r24tmp')
        shutil.copyfile(src/rel,pending);os.replace(pending,target)
    assert sha(target)==records[rel]['installed'],rel
out=dst/'verification_r24';out.mkdir(exist_ok=True);(out/'.gdignore').touch()
installed.write_text(json.dumps(records,indent=1))
print('R24_INSTALLED',len(records),dst)

