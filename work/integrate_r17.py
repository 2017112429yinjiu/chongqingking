from pathlib import Path
import json,sys,math,shutil,hashlib,struct
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'project/chongqing_blender_v05'
GAME=ROOT/'project/chongqing_godot_v05'
sys.path.insert(0,str(SOURCE))
import district_layout as dl
from circulation_r17 import ROUTES
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pos(p):return [p[0],round(dl.ground_height(*p)+.42,4),-p[1]]
survey=read(GAME/'assets/walking_survey.json')
survey['sample_adjustments']=[r for r in survey['sample_adjustments'] if r.get('match_xz')!=[1.6,60.4]]
survey['sample_adjustments'].append({'match_xz':[1.6,60.4],'replacement':[1.6,14.4,58.2308],
 'reason':'R17 reroutes the full 3.8 m public stair envelope away from building 809889623. The former centre sample lies on the new safety rail; relocate this clearance sample to the authored new centreline (6,-59.5) to (-20,-52). Both whole-route directions are independently tested with the player capsule.'})
survey['routes']=[r for r in survey['routes'] if not r['name'].startswith('r17_')]
for r in survey['routes']:
    if r['name']=='lower_street_to_spine':
        r['from']=pos((16,-66));r['waypoints']=[pos((6,-59.5)),pos((-20,-52))]
for name,points,width,_ in ROUTES:
    for reverse in [False,True]:
        path=list(reversed(points)) if reverse else points
        a,b=pos(path[0]),pos(path[-1])
        survey['routes'].append({'name':'r17_'+name+('_down' if reverse else '_up'),'from':a,'to':b,
          'waypoints':[pos(p) for p in path[1:-1]],'frames':math.ceil(sum(math.dist(p,q) for p,q in zip(path,path[1:]))/4.2*60*1.6)+180,
          'min_progress_m':max(.2,math.dist(path[0],path[-1])-.8),'min_height_gain_m':b[1]-a[1]-.75,
          'purpose':'R17 revised whole route, real player controller; no waypoint teleport. Width '+str(width)+' m.'})
for name,points in [('worker_entry',[(-68.7,28.9),(-70.5,28.9),(-72.4,28.88)]),('A04_entry',[(-50.5,-19.5),(-52.0,-19.5),(-53.6,-19.5)])]:
    survey['routes'].append({'name':'r17_'+name,'from':pos(points[0]),'to':pos(points[-1]),'waypoints':[pos(points[1])],
       'frames':300,'min_progress_m':2.5,'min_height_gain_m':-.6,'purpose':'Enter repaired vestibule from public approach without crossing rail or stair block.'})
write(GAME/'assets/walking_survey.json',survey)
profile=read(GAME/'assets/render_profile_r17.json') if (GAME/'assets/render_profile_r17.json').exists() else read(GAME/'assets/render_profile_r16.json')
profile['art_revision']='R17_circulation_review'
profile['diagnostic_views'].update({
 'r17_worker_entry':{'title':'山城里入口修正','position':[-65.5,25.1,-27.5],'target':[-72,24,-28.9],'fov':57},
 'r17_worker_door':{'title':'住宅门厅内部','position':[-70.8,24.4,-28.9],'target':[-74.1,24,-28.94],'fov':70},
 'r17_A04_entry':{'title':'住宅平层门厅','position':[-48.6,18.2,18.2],'target':[-53.8,17.6,19.5],'fov':57},
 'r17_west_route':{'title':'西侧绕楼路线','position':[-60,38,-31],'target':[-74,25,-31],'fov':65},
 'r17_east_route':{'title':'东巷连续通道','position':[61,29,11],'target':[47,21,8],'fov':62},
 'r17_narrow_route':{'title':'上层窄巷','position':[-37.4,27.1,-43],'target':[-31.5,27.8,-53],'fov':62}})
write(GAME/'assets/render_profile_r17.json',profile)
source=ROOT/'r17_scene/chongqing_district.glb'
shutil.copy2(source,GAME/'assets/chongqing_district.glb')
with source.open('rb') as f:
    f.read(12);length,kind=struct.unpack('<II',f.read(8));gltf=json.loads(f.read(length))
manifest=read(GAME/'assets/scene_manifest.json')
manifest.update(revision=17,iteration='R17-local-development',glb_bytes=source.stat().st_size,blend_bytes=(ROOT/'r17_scene/chongqing_district.blend').stat().st_size,
 meshes=len(gltf['meshes']),current_evidence='verification_r17 (in progress); verification_r16 and verification are historical',
 geometry_sha256=hashlib.file_digest(source.open('rb'),'sha256').hexdigest())
manifest['historical_metric_notice']='Metrics not explicitly superseded by R16/R17 reports were generated with R15. Triangle total below remains the R15 pre-modifier baseline.'
write(GAME/'assets/scene_manifest.json',manifest)
shutil.copy2(ROOT/'r17_scene/geometry_repairs_r17.json',GAME/'assets/geometry_repairs_r17.json')
print(json.dumps({'routes':len(survey['routes']),'glb_bytes':source.stat().st_size,'meshes':len(gltf['meshes'])}))
