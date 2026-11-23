"""Temporary in-engine expression comparisons, no production profile mutation."""
from pathlib import Path
import json,copy
project=Path(__file__).resolve().parent/'project/chongqing_godot_v05'
data=json.loads((project/'assets/render_profile_r18.json').read_text(encoding='utf-8'))
for name,strength in [('neutral',0),('warm',.30),('smile',.55)]:
    view=copy.deepcopy(data['diagnostic_views']['r18_face'])
    view['capture_state'].update({'character_clip':'idle','time':1.5,'smile':strength,'look_at_camera':True})
    data['diagnostic_views']['expression_'+name]=view
(project/'assets/render_profile_r18_expression_trial.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
