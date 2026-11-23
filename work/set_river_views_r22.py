from pathlib import Path
import json
W=Path(__file__).resolve().parent;P=W/'project/chongqing_godot_v05'
plan=json.loads((P/'assets/river_r22/layout.json').read_text(encoding='utf8'))
eye=plan['street_sightlines'][0]['eye']
views={'r22_river_street':{'position':eye,'target':[-502,30,578],'fov':52,'title':'路口行人眼高看江'},
       'r22_river_overview':{'position':[-75,88,66],'target':[-521,14,620],'fov':59,'title':'城区和跨江远景'},
       'r22_river_detail':{'position':[-152,56,245],'target':[-501,25,504],'fov':36,'title':'跨江远景诊断'}}
for f in [P/'assets/render_profile_r22.json',P/'verification_r22/base_profile.json']:
    j=json.loads(f.read_text(encoding='utf8'));j['diagnostic_views'].update(views)
    f.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
