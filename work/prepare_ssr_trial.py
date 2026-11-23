from pathlib import Path
import json
project=Path(__file__).resolve().parent/'project/chongqing_godot_v05'
data=json.loads((project/'assets/render_profile_r18.json').read_text(encoding='utf-8'))
data['lighting']['ssr']=True
(project/'assets/render_profile_r18_ssr_trial.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
