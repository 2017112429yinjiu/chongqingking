from pathlib import Path
import json,shutil
W=Path(__file__).resolve().parent
P=W/'project/chongqing_godot_v05'
C=W/'checkpoints/R19_before_scene'; C.mkdir(parents=True,exist_ok=True)
for f in ['scripts/main.gd','assets/render_profile_r18.json']:
    dst=C/f;dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(P/f,dst)
base=json.loads((P/'assets/render_profile_r18.json').read_text())
for variant,settings in {
    'soft_day':dict(hdri_path='',procedural_clouds=True,cloud_coverage=.88,cloud_strength=.42,cloud_scale=1.15,ambient_energy=.72,background_energy=1.0,sky_contribution=1.,sun_energy=.6,sun_color=[1.,.96,.88],sun_rotation_deg=[-39,-111,0],sun_angular_distance=5.,exposure=1.0,fog_density=.0009,fog_color=[.68,.72,.71],fog_aerial_perspective=.45,ssil_intensity=.28),
    'daylight':dict(sun_rotation_deg=[-48,-116,0],hdri_rotation_deg=[0,-81.9,0],sun_energy=1.05,ambient_energy=.46,hdri_energy=1.30,exposure=1.0,fog_density=.0008)
}.items():
    p=json.loads(json.dumps(base));p['art_revision']='R19_'+variant+'_trial';p['lighting'].update(settings)
    p['label_zh']='R19 / '+variant;p['notes']=['R19 fixed-camera scene lighting comparison. Internal trial, not film-quality acceptance.']
    (P/f'assets/render_profile_r19_{variant}.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
i=json.loads((W/'audit/r19_source_inventory.json').read_text(encoding='utf-8'))
for o in i['objects']:
    if 'A01_noodle_details' in o['name'] or 'Sign' in o['name'] or ('Awning' in o['name']):
        print(o['name'],[[round(x,3) for x in p] for p in o['bounds']],o['materials'])
a=json.loads((W/'project/chongqing_blender_v05/architecture_manifest.json').read_text())
for b in a['buildings']:
    if str(b['id'])=='A01':print('BUILDING',json.dumps({k:b.get(k) for k in ['id','front_edge','base_m','entrances','points']},ensure_ascii=False))
