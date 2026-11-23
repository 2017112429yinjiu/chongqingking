from pathlib import Path
import json
p=Path(__file__).resolve().parent/'project/chongqing_godot_v05/assets'
data=json.loads((p/'render_profile_r18.json').read_text(encoding='utf-8'))
data['art_revision']='R18_station_reflection_trial'
data.setdefault('reflections',{})['packing_station']=True
(p/'render_profile_r18_reflection_trial.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
