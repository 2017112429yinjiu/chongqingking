import json
from pathlib import Path
p=Path(__file__).resolve().parent/'project/chongqing_godot_v05/assets/render_profile_v05.json'
j=json.loads(p.read_text(encoding='utf-8'))
j['diagnostic_views']={
 'r16_scooter':{'title':'电瓶车贴地','position':[-17.3,13.4,56.5],'target':[-20.5,12.5,59],'fov':48},
 'r16_clothesline':{'title':'西侧晾衣支架','position':[-74,20.1,9],'target':[-70.3,19.2,5],'fov':62},
 'r16_roof':{'title':'屋檐封口','position':[-47,30,20],'target':[-54,28,20],'fov':58},
 'r16_shop':{'title':'店主与取餐入口','position':[-22,13.5,57],'target':[-25.4,13.4,61],'fov':60},
 'r16_meter':{'title':'电表箱近景','position':[-27.2,12.3,59.8],'target':[-27.83,12.01,61.77],'fov':45}}
p.with_name('render_profile_r16.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
