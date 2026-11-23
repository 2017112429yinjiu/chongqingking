"""Bind the retained city, profile, native captures and original unshared assets."""
from pathlib import Path
import hashlib,json
here=Path(__file__).resolve().parent
root=here.parents[2]
project=root/'work/project/chongqing_godot_v05'
qa=project/'verification_r24/build15'
def digest(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
items=[here/n for n in ['city_and_windows.blend','author.py','wall_finish.py','check_source.py','candidate.json','pre_visibility_profile.json','asset_record.json','reopen.json','verify.ps1','rebuild.ps1','audit.gd','walk.gd','南区路窗下对照.jpg','西巷窗内对照.jpg','沿南区路看窗.webp','reference_work.jpg']]
items.extend((project/'assets/rooms_r24').glob('*'))
items.extend(here.glob('perf/*gd'))
items.extend([here/'perf/bake.json',here/'perf/comparison.json',here/'perf/solo/comparison.json',here/'perf/window_state.json',here/'perf/stage_times.json',project/'scripts/window_life_r24.gd',project/'shaders/wall_patina_r24.gdshader'])
for folder in [here/'current',here/'before',here/'walk_current',here/'perf/solo',qa]:
    items.extend(f for f in folder.rglob('*') if f.suffix.lower() in ['.png','.jpg','.json'])
record={'revision':json.loads((here/'candidate.json').read_text('utf8'))['art_revision'],'source_links':'../courtyard_life/evidence.json','files':{}}
for path in sorted(set(items)):
    if path.is_file() and path.suffix!='.import':
        record['files'][path.relative_to(root).as_posix()]=digest(path)
(here/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
