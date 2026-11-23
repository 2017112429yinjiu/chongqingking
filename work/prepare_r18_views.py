from pathlib import Path
import json
p=Path(__file__).resolve().parent/'project/chongqing_godot_v05'
data=json.loads((p/'assets/render_profile_r17.json').read_text(encoding='utf-8'))
for key,clip,t in [('idle','idle',0),('reach','serve',1.12),('lift','serve',1.65),('place','serve',2.4)]:
    data['diagnostic_views']['r18_'+key]={'title':'R18 internal character '+key,'position':[-23.3,13.35,58.3],'target':[-25.6,12.7,59.8],'fov':42,'capture_state':{'character_clip':clip,'time':t,'food_ready':True}}
data['diagnostic_views']['r18_workstation']={'title':'Packing station context','position':[-22.8,13.2,57.8],'target':[-25.3,12.2,59.8],'fov':47,'capture_state':{'character_clip':'serve','time':1.65,'food_ready':True}}
data['diagnostic_views']['r18_player_eye']={'title':'Player eye-height interaction','position':[-23.63,12.79,58.80],'target':[-25.59,12.60,59.8],'fov':50,'capture_state':{'character_clip':'idle','time':0,'food_ready':True}}
data['diagnostic_views']['r18_greet']={'title':'Recognition and greeting','position':[-23.63,12.79,58.80],'target':[-25.59,12.60,59.8],'fov':50,'capture_state':{'character_clip':'greet','time':.65,'smile':.259,'food_ready':False}}
data['diagnostic_views']['r18_face']={'title':'In-engine face diagnostic','position':[-24.70,12.73,59.35],'target':[-25.59,12.66,59.8],'fov':37,'capture_state':{'character_clip':'greet','time':.65,'smile':.259,'food_ready':False}}
for key in ['r18_face','r18_greet','r18_player_eye']:data['diagnostic_views'][key]['capture_state']['look_at_camera']=True
data['diagnostic_views']['r18_grip']={'title':'Hand and paper-handle contact','position':[-24.65,12.57,59.20],'target':[-25.142,12.29,59.717],'fov':34,'capture_state':{'character_clip':'serve','time':1.65,'food_ready':True}}
for view in data['diagnostic_views'].values():
    pose=view.get('capture_state',{})
    if pose.get('character_clip')=='serve':pose['look_at_food']=True
data['art_revision']='R18_shopkeeper_internal'
data['lighting'].update({'packing_task_light_energy':.12,'shadow_split_1':.035,'shadow_split_2':.16,'shadow_split_3':.45})
(p/'assets/render_profile_r18.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
