"""Summarize measured routes and separate missing surfaces from actual driving outcomes."""
import json,sys,math
from pathlib import Path
here=Path(__file__).resolve().parent
qa=here.parents[1]/'project/chongqing_godot_v05/verification_r24/district_age'
run=sys.argv[1] if len(sys.argv)>1 else 'play20'
def read(phase,filename):return json.loads((qa/(run+'_'+phase)/filename).read_text('utf8'))
district=read('ground','district.json')
routes=[(i,r) for i,r in enumerate(district['routes']) if not r['tunnel']]
result={'engine':district['engine'],'scene_mesh_sha256':district['scene']['yard_donor_sha256'],'map_lines':len(district['routes']),'surface_sections':len(routes),'surface_route_length_m':round(sum(r['m'] for i,r in routes),2),'map_only_tunnel_sections':[i for i,r in enumerate(district['routes']) if r['tunnel']],'native_probes':{},'rides':{},'anchors':district['contacts']}
for field,rows in [('three_tracks',district['sections']),('ground_grid',district['grid']),('asphalt_joint',district['south_joint']),('western_median',district.get('western_median',[])),('western_extra',district.get('western_extra',[]))]:
    result['native_probes'][field]={'total':len(rows),'missing':sum(row[-2] is None for row in rows)}
for key in ['out','back']:
    trials=sorted([r for i in range(3) for r in read(key+str(i),'drives.json')],key=lambda r:r['id'])
    reached=sum(r.get('reached',0) for r in trials)
    result['rides'][key]={'completed':sum(r['state']=='passed' for r in trials),'waypoints_reached':reached,'waypoints_expected':sum(r.get('targets',0) for r in trials),'routes':[{'id':r['id'],'state':r['state'],'route':r.get('route',''),'last_contact':r.get('last_contact',{}) if r['state']!='passed' else {}} for r in trials]}
    assert [r['id'] for r in trials]==[i for i,r in routes]
result['western_median_ground_intrusions']=sum(row[-2] is not None and row[-2]>row[2]+.035 and (row[-1].startswith('COL_Terrain') or 'PathFoundations' in row[-1]) for row in district.get('western_median',[]))
result['under_higher_surface']= district['below_another_level']
wheel_errors=[e for parts in read('parked','tyres.json').values() for name,err in parts if not name.endswith('_00') for e in err]
result['parked_car_tyres']={'measured':len(wheel_errors),'max_abs_m':max(map(abs,wheel_errors),default=None)}
result['complete']=len(wheel_errors)==12 and result['parked_car_tyres']['max_abs_m']<.018 and result['western_median_ground_intrusions']==0 and all(s['missing']==0 for s in result['native_probes'].values()) and all(s['completed']==len(routes) for s in result['rides'].values()) and all(a['error_m'] is not None and abs(a['error_m'])<.008 for a in district['contacts'])
target=qa/(run+'_ground')/'summary.json'
target.write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(result['complete'],result['surface_route_length_m'],result['native_probes'],[v['completed'] for v in result['rides'].values()])
if not result['complete']:sys.exit(2)
