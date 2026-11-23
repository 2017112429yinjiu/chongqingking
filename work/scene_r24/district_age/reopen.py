import sys,json,bpy,hashlib
from pathlib import Path
from mathutils import Vector
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import scene,Surfaces,work
base=work/'project/chongqing_godot_v05/assets/district_age';plan=json.loads((base/'layout.json').read_text('utf8'));place=json.loads((here/'placement.json').read_text('utf8'))
missing=[k for k in plan['new']+plan['changed'] if scene.objects.get(k) is None or not scene.objects[k].data.polygons]
remain=[k for k in plan['retired'] if scene.objects.get(k) and not scene.objects[k].hide_render and scene.objects[k].data.polygons]
ground=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_Terrain_200m')])
contact=[]
for i in range(3):
    o=scene.objects['Yard20_Cycle_'+str(i+1)];foot_pts=[Vector((p[0],-p[2],p[1])) for p in plan['tyres'][2*i:2*i+2]]
    for q in foot_pts:
        deltas=[]
        for v in o.data.vertices:
            p=o.matrix_world@v.co
            if (p.xy-q.xy).length>.19 or p.z>q.z+.06:continue
            h=ground.down(p.x,p.y,p.z+.15,.35);assert h
            deltas.append(p.z-h[0][0])
        contact.append(min(deltas))
paper=[]
for mark in plan['prints']:
    site=next(a for a in place if a['id']==mark['id']);t=Vector((*site['t'],0));n=Vector((*site['n'],0));c=mark['centre'];center=Vector((c[0],-c[2],c[1]))
    ob=scene.objects[mark['surface']];sample=Surfaces([ob]);depths=[]
    for side,height in [(0,0),(-.18,-.18),(-.18,.18),(.18,.18),(.18,-.18)]:
        p=center+t*(side*mark['width'])+Vector((0,0,height*mark['width']))
        h,_,_,d=sample.tree(ob).ray_cast(p+n*.05,-n,.12);depths.append(round(d-.05,5) if h is not None else None)
    paper.append([mark['id'],depths])
def sha(p):
    with p.open('rb') as src:
        return hashlib.file_digest(src,'sha256').hexdigest()
report={'source':bpy.data.filepath,'version':bpy.app.version_string,'missing':missing,'retired_visible':remain,'lowest_tyre_minus_terrain_m':contact,'paper_offsets_m':paper,'hashes':{p.name:sha(p) for p in [Path(bpy.data.filepath),*(x for x in base.iterdir() if x.suffix in ['.glb','.png','.json'])]}}
(here/'source_check.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),'utf8');assert not missing and not remain and max(abs(z) for z in contact)<.006
assert len(paper)==len(plan['prints']) and all(d is not None and .001<d<.008 for _,ds in paper for d in ds)
print('REOPENED',contact,paper,flush=True)
