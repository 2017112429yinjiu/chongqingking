from pathlib import Path
import bpy, json
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
city=bpy.context.scene
stairs=city.objects['COL_R24_MarketStairs_R24_step_stone']
apron=city.objects['COL_R23_NanquUpperApron']
def surface(obj):
    return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],[p.vertices[:] for p in obj.data.polygons])
native=json.loads((here/'original_apron.json').read_text('utf8'))['triangles_blender']
before=BVHTree.FromPolygons(native,[(i,i+1,i+2) for i in range(0,len(native),3)],all_triangles=True)
after=surface(apron)
probes=[]
for face in apron.data.polygons:
    if apron.data.materials[face.material_index].name!='Market16_CutSandstone':continue
    middle=apron.matrix_world @ face.center
    pos=(middle.x,middle.y,middle.z+1)
    a=before.ray_cast(pos,(0,0,-1),3);b=after.ray_cast(pos,(0,0,-1),3)
    if a[0] is not None and b[0] is not None:
        probes.append([middle.x,a[0].z,-middle.y,b[0].z-a[0].z])
assert len(probes)>20 and max(abs(p[3]) for p in probes)<.001
data=json.loads((here/'measurements.json').read_text('utf8'));scan=surface(stairs)
errors=[]
for x,z,y,kind in data['probes']:
    point=scan.ray_cast((x,-y,z+.25),(0,0,-1),.5)[0]
    errors.append(None if point is None else point.z-z)
assert all(e is not None and abs(e)<.001 for e in errors),errors
deps=[l.filepath for l in bpy.data.libraries if l.filepath.endswith('.blend')]
assert len(deps)>=3
report={'opened':bpy.data.filepath,'engine':bpy.app.version_string,'cap_probes':probes,'max_coping_m':max(abs(p[3]) for p in probes),'tread_probe_errors_m':errors,'linked_rigs':deps}
(here/'reopen.json').write_text(json.dumps(report,indent=2),'utf8')
print('MARKET16_REOPEN',len(errors),len(probes),report['max_coping_m'])
