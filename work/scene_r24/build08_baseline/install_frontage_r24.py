"""Promote verified R24 runtime files only; preserve each original before replacement."""
from pathlib import Path
import hashlib,json,shutil,os
w=Path(__file__).resolve().parent;s=w/'scene_r24'
src=s/'playtest';dst=w/'project/chongqing_godot_v05';backup=s/'prior_active_files'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
walk=json.loads((src/'verification_r24/trial08/walk.json').read_text(encoding='utf8'))
assert walk['success'] and walk['counters_block'] and walk['bridge_top_hits']==49 and len(walk['waypoints'])==15
source=json.loads((s/'source_reopened.json').read_text(encoding='utf8'))
assert source['sha256']==sha(s/'chongqing_district.blend')
files=['scripts/explorer.gd','scripts/main.gd','scripts/qa_block_r23.gd','scripts/qa_context.gd','assets/viewpoints.json','assets/render_profile_r24.json']
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

