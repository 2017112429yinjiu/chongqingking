"""Compile only measured native data. Keep stairs and the parked vehicle separate from naked pavement."""
from pathlib import Path
from collections import Counter
import hashlib,json,math,sys
import numpy as np
here=Path(__file__).resolve().parent
game=here.parents[1]/'project/chongqing_godot_v05'
qa=game/'verification_r24/terrace_gardens'
folder=qa/(sys.argv[1] if len(sys.argv)>1 else 'final_checks21')
def read(p):return json.loads(p.read_text('utf8'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def slope(heights,triplets):
    return [abs(math.degrees(math.atan((heights[c]-heights[b])*2)-math.atan((heights[b]-heights[a])*2))) for a,b,c in triplets]
old=read(here/'sections_before.json');new=read(here/'sections_after.json');probe=read(folder/'slope/probe.json')
native=dict(zip(read(here/'probe_keys.json'),probe['heights']))
surface=set(read(here/'grade.json')['cut'])|{'COL_Terrace21_Fork'}
valid={key for key,(h,n) in native.items() if n in surface and h is not None}
triplets=[row for row in new['triplets'] if set(row)<=valid]
pairs=[row for row in new['pairs'] if set(row)<=valid]
native_h={key:v[0] for key,v in native.items()}
geometry={}
for label,hs in [('old_source',old['heights']),('new_source',new['heights']),('engine',native_h)]:
    diff=slope(hs,triplets)
    geometry[label]={'grade_break_deg_p95':float(np.percentile(diff,95)),'grade_break_deg_max':max(diff),'seam_max_height_change_over_40mm':max(abs(hs[a]-hs[b]) for a,b in pairs)}
park=read(folder/'parked/tyres.json')
wheels=[e for pieces in park.values() for name,err in pieces if not name.endswith('_00') for e in err]
district=read(folder/'ground/district.json')
drives={prefix:[s for i in range(3) for s in read(folder/(prefix+str(i))/'drives.json')] for prefix in ['out','back']}
lesson_files=[f for f in (folder/'three_orders').glob('*.json') if 'passed' in read(f)]
lesson=read(lesson_files[0])
walk_folder=qa/sys.argv[2] if len(sys.argv)>2 else folder/'walk'
roots_folder=qa/sys.argv[3] if len(sys.argv)>3 else folder/'roots'
toe_folder=qa/sys.argv[4] if len(sys.argv)>4 else folder/'toe'
walk=read(walk_folder/'walk.json');pts=walk['path']
roots=read(roots_folder/'roots.json');toe=read(toe_folder/'rides.json');north=read(folder/'north/rides.json')
root_errors=[v['root_minus_soil_m'] for v in roots if v['bed'].startswith('COL_Terrace21_Bed') and v['root_minus_soil_m'] is not None]
travel=sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
beds=read(here/'beds.json')
totals={k:[len(district[k]),sum(p[-2] is None for p in district[k])] for k in ['sections','grid','south_joint','western_median','western_extra']}
measured=read(folder/'north_source/north.json')
independent={(('grid' if r[0]=='ground_grid' else r[0]),r[1]):r for r in measured}
original_missing={k:val[1] for k,val in totals.items()}
resolved={}
for k in ('grid','sections'):
    resolved[k]=[]
    for i,r in enumerate(district[k]):
        if r[-2] is not None:continue
        q=independent.get((k,i))
        if q and q[-2] is not None and abs(q[5]-q[-2])<.012 and abs(q[5]-q[4])>.375:
            resolved[k].append({'index':i,'old':q[4],'source':q[5],'game':q[-2]})
    totals[k][1]-=len(resolved[k])
result={'historical_band_misses':original_missing,'surveyed_fill':resolved,'north_independent_points':len(measured),'engine':district['engine'],'native_surface_nodes':dict(Counter(n for _,n in native.values())),'native_ground_missing':sum(h is None for h,n in native.values()),'matched_surface_height_points':len(valid),'matched_triplets':len(triplets),'matched_seam_pairs':len(pairs),'metrics':geometry,'native_vs_source_max_m':max(abs(native_h[k]-new['heights'][k]) for k in valid),'bed_min_clearance_to_mapped_edge_m':min(b['clearance_to_mapped_route_edge'] for b in beds),'tree_count':sum(b['tree'] for b in beds),'underplants':sum(b['underplants'] for b in beds),'wheels':len(wheels),'max_wheel_contact_m':max(map(abs,wheels)),'public_road_probes_total_and_missing':totals,'ride_runs':{k:{'count':len(v),'passed':sum(r['state']=='passed' for r in v),'targets':sum(r['targets'] for r in v)} for k,v in drives.items()},'registered_orders_passed':lesson['passed'],'lesson_checks':len(lesson['checks']),'walk_passed':all(walk['targets']),'walk_sampled_m':travel,'source_sha256':sha(here/'city_and_gardens.blend'),'model_sha256':sha(game/'assets/terrace_gardens/terrace.glb')}
result['root_probes']={'expected':80,'found':len(root_errors),'root_minus_soil_m':[min(root_errors,default=None),max(root_errors,default=None)]}
result['east_landing_runs']={'expected':6,'passed':sum(r['passed'] for r in toe)}
result['north_ramp_runs']={'expected':6,'passed':sum(r['passed'] for r in north)}
result['passed']=len(north)==6 and all(r['passed'] for r in north) and len(root_errors)==80 and min(root_errors)>-.06 and max(root_errors)<=.005 and len(toe)==6 and all(r['passed'] for r in toe) and len(valid)>2000 and not result['native_ground_missing'] and geometry['engine']['grade_break_deg_p95']<2. and geometry['engine']['seam_max_height_change_over_40mm']<.015 and result['native_vs_source_max_m']<.001 and result['wheels']==12 and result['max_wheel_contact_m']<.018 and result['walk_passed'] and result['registered_orders_passed'] and all(not missing for _,missing in totals.values()) and all(v['passed']==26 for v in result['ride_runs'].values())
save(folder/'summary.json',result)
print(json.dumps(result,ensure_ascii=True))
if not result['passed']:raise SystemExit(2)
