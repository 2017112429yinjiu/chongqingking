from pathlib import Path
import json
p=Path(__file__).resolve().parent/'project/chongqing_godot_v05/assets'
data=json.loads((p/'render_profile_r18.json').read_text(encoding='utf-8'))
data['art_revision']='R18_character_soft_day_trial'
data['lighting'].update({'hdri_energy':1.2,'ambient_energy':.38,'sky_contribution':.8,'exposure':1.0,'sun_energy':1.2,'shadow_normal_bias':.25,'shadow_bias':.035,'shadow_split_1':.035,'shadow_split_2':.16,'shadow_split_3':.45,'ssao_radius':.7,'ssao_light_affect':.4})
data['notes'].append('R18 trial: closer first cascade for human detail, lower skylight/exposure; compare against unchanged R17 daylight before adopting.')
(p/'render_profile_r18_softday.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
