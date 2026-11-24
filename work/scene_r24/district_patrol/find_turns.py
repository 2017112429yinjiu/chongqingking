"""Locate old tread / flat path junctions for comparison with player frame 09."""
from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import scene,Surfaces
ground=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and
    (o.name.startswith(('COL_Walk_','COL_East17_CourtyardPaving','COL_D18_LaneShoulders')) or o.name=='COL_R23_PathFoundations')])
records=[]
for obj in scene.objects:
    if obj.hide_render or not obj.name.startswith('COL_Walk_') or not obj.name.endswith('step_concrete'):continue
    hits=[]
    for f in obj.data.polygons:
        if f.normal.z<.998:continue
        vs=[obj.matrix_world@obj.data.vertices[v].co for v in f.vertices]
        c=sum(vs,Vector())/len(vs)
        for dx,dy in ((0,0),(.7,0),(-.7,0),(0,.7),(0,-.7)):
            for z,name,n in ground.down(c.x+dx,c.y+dy,c.z+.45,.9):
                if name==obj.name or 'Foundation' in name:continue
                hits.append((c,name))
    for p,name in hits:
        if any((p-Vector(r['centre'])).length<4.8 for r in records):continue
        records.append({'centre':list(p),'flight':obj.name,'neighbour':name})
for rec in records:
    p=Vector(rec['centre'])
    def candidates(name):
        options=[]
        for i in range(60):
            d=Vector((math.cos(i*math.tau/60),math.sin(i*math.tau/60),0))
            for length in [3.45,3.2,3.0]:
                q=p+d*length
                ds=[z for z,n,_ in ground.down(q.x,q.y,p.z+1.5,3.) if n==name]
                if ds:
                    q.z=ds[0]
                    options.append((d,q))
                    break
        return options
    pairs=[(a.dot(b),s,e) for a,s in candidates(rec['flight']) for b,e in candidates(rec['neighbour'])]
    if pairs:
        _,s,e=min(pairs,key=lambda item:item[0])
        rec['approach']=[list(s),list(e)]
(here/'legacy_turns.json').write_text(json.dumps(records,indent=2),'utf8')
print('CANDIDATES',len(records))
