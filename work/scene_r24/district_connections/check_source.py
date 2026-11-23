from pathlib import Path
import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent
scene=bpy.context.scene
plan=json.loads((here.parents[1]/'project/chongqing_godot_v05/assets/connections_r24/layout.json').read_text('utf8'))
report={'source':bpy.data.filepath,'revision':scene.get('street_revision'),'probes':[],'errors':[]}
deps=bpy.context.evaluated_depsgraph_get()
def point(v):return Vector((v[0],-v[2],v[1]))
for spec in plan['kitchen']['probes']:
    ob=scene.objects[spec['mesh']];a,b=[point(spec[k]) for k in ['start','end']]
    hit=BVHTree.FromObject(ob,deps).ray_cast(a,(b-a).normalized(),(b-a).length)[0]
    report['probes'].append({'name':spec['name'],'hit':list(hit) if hit else None,'object':ob.name})
    if hit is None:report['errors'].append(spec['name'])
g=scene.objects['D18_PhotoGinger'];delta=abs(extent(g)[0][2]-plan['ginger']['support_blender_z'])
if delta>.0005:report['errors'].append('ginger bottom')
report['ginger_gap_m']=delta
court_floor=20.53
for n in ['Court_fence_and_hoops_painted_metal','Court_fence_and_hoops_frame']:
    o=scene.objects[n];heights=[]
    for y in (-15.5,15.5):
        zs=[v.co.z for v in o.data.vertices if abs(v.co.y-y)<.21 and -45.8<v.co.x<-23.]
        heights.append(round(max(zs)-court_floor,4) if zs else None)
    report[n]=heights
    if not all(v is not None and 3.96<v<4.17 for v in heights):report['errors'].append(n)
for y in (-9,9):
    o=scene.objects['Street_small_furniture_timber']
    back=[v.co.x for v in o.data.vertices if abs(v.co.x+45.05)<.65 and abs(v.co.y-y)<1.05 and v.co.z>court_floor+.61]
    feet=scene.objects['Street_small_furniture_frame']
    legs=[v.co.z for v in feet.data.vertices if abs(v.co.x+45.05)<.50 and abs(v.co.y-y)<1.0]
    read={'back_x':sum(back)/len(back) if back else None,'base_z':min(legs) if legs else None,'deck_z':court_floor}
    report['bench'+str(y)]=read
    if not back or read['back_x']>=-45.05 or not legs or abs(min(legs)-court_floor)>.045:report['errors'].append('bench'+str(y))
report['passed']=not report['errors']
(here/'native_source_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print('SOURCE18',report['passed'],report['errors'])
if not report['passed']:raise RuntimeError(report['errors'])
