from pathlib import Path
import hashlib,json
here=Path(__file__).resolve().parent
root=here.parents[3]
project=root/'work/project/chongqing_godot_v05'
qa=project/'verification_r24/build16'
inputs=[here/name for name in ['author.py','check_source.py','city_and_market_steps.blend','original_apron.gd','original_apron.json','measurements.json','reopen.json','survey.py','survey.json','front_survey.json','candidate.json','verify.ps1','rebuild.ps1','test.gd','walk_market.gd','review_media.py','asset_record.json','compare_performance.ps1','市场入口前后对照.jpg','从下层人行道看台阶.jpg','从南区路走进菜摊.webp']]
inputs.extend([project/'assets/market_steps_r24/market.glb',project/'scripts/market_steps_r24.gd',project/'shaders/market_sandstone_r24.gdshader'])
for folder in ['before','first','second','current','route','walk_current','encounter_before','perf','first_geometry']:
    inputs.extend(p for p in (here/folder).rglob('*') if p.is_file() and p.suffix.lower() in ['.png','.jpg','.json','.csv','.blend','.glb'])
inputs.extend(p for p in qa.rglob('*.json') if 'passing' not in str(p.relative_to(qa)))
record={'profile':json.loads((here/'candidate.json').read_text('utf8'))['art_revision'],'inherited_window_assets':'../evidence.json','files':{}}
for p in sorted(set(inputs)):
    if p.is_file():
        with p.open('rb') as stream:
            record['files'][p.relative_to(root).as_posix()]=hashlib.file_digest(stream,'sha256').hexdigest()
(here/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
