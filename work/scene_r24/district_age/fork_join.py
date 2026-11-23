"""Re-section the eastward end of the shoulder to the actual cut line of its neighbours."""
from roads import *
from survey import road_objects
from bisect import bisect_right
shoulder=scene.objects['COL_D18_NanquShoulder']
bank=scene.objects['D18_RoadEndBedding']
# At the east end the previous exposed bedding crossed the pavement in thin dark upright panels.
# The new rim and neighbouring top faces now share their cross-section and need no flashing.
bm=bmesh.new();bm.from_mesh(bank.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().x>45],context='FACES');bm.to_mesh(bank.data);bm.free();bank.data.update();changed.add(bank.name)
neighbours=Surfaces([o for o in road_objects if not o.hide_render and o.name.startswith(('COL_Terrain_200m','COL_Road_176034707_0_pavement','COL_Road_176034707_0_curb','COL_Road_176034707_0_asphalt'))])
# Read all actual breakpoints where a clipped ground triangle reaches x=47.
end_x=47.;station_rows={}
for v in shoulder.data.vertices:
    p=v.co
    if p.x<37:continue
    x=round(p.x,4);y=round(p.y,5);row=station_rows.setdefault(x,{})
    row[y]=max(row.get(y,-99),p.z)
xs=sorted(station_rows);start=xs[0]
y0,y1=min(station_rows[xs[-1]]),max(station_rows[xs[-1]])
cross={y0,y1};edge_x=47.001
for o in road_objects:
    if o.hide_render or not o.name.startswith(('COL_Terrain_200m','COL_Road_176034707_0')):continue
    for edge in o.data.edges:
        a,b=[o.matrix_world@o.data.vertices[i].co for i in edge.vertices]
        if min(a.x,b.x)<=edge_x<=max(a.x,b.x) and abs(b.x-a.x)>1e-7:
            q=a.lerp(b,(edge_x-a.x)/(b.x-a.x))
            if y0<q.y<y1:cross.add(round(q.y,5))
def lin(keys,values,y):
    k=max(0,min(len(keys)-2,bisect_right(keys,y)-1))
    return values[k]+(values[k+1]-values[k])*(y-keys[k])/(keys[k+1]-keys[k])
def profile(row,y):
    keys=sorted(row);return lin(keys,[row[k] for k in keys],y)
def smooth(t):t=min(1.,max(0.,t));return t*t*(3-2*t)
ts={i/100 for i in range(101)}
# A curb's 2 elevations remain a real curb with a very short fillet at the join.
for y in cross:
    for d in [-.012,0,.012]:ts.add(min(1.,max(0.,(y+d-y0)/(y1-y0))))
for k in station_rows[start]:ts.add((k-min(station_rows[start]))/(max(station_rows[start])-min(station_rows[start])))
ts=sorted(ts)
for i in range(len(ts)-1,0,-1):
    if ts[i]-ts[i-1]<.00004:ts.pop(i-1)
def end_floor(t):
    y=y0+t*(y1-y0)
    hits=neighbours.down(edge_x,y,14,7)
    assert hits,(edge_x,y)
    return hits[0][0]
target=[end_floor(t) for t in ts];first=station_rows[start];first_y=min(first);first_w=max(first)-first_y
bm=bmesh.new();bm.from_mesh(shoulder.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().x>start+.001],context='FACES')
mat_uv=bm.loops.layers.uv.get('SurfaceMetres');course=bm.loops.layers.uv.get('MasonrySetout');stone_index=next(i for i,m in enumerate(shoulder.data.materials) if m.name.startswith('R18_paver'))
lastvs=None
for x in xs:
    row=station_rows[x];a=min(row);w=max(row)-a;alpha=smooth((x-start)/(end_x-start))
    vs=[]
    for i,t in enumerate(ts):
        pz=profile(first,first_y+t*first_w)*(1-alpha)+target[i]*alpha
        # Preserve the existing top and return along both long banks until the terminal section.
        datum=(row[a]-min(first.values()))*(1-alpha)*(1-smooth(t/.30))
        pz+=datum
        if x==start:pz=profile(first,a+t*w)
        vs.append(bm.verts.new((x,a+t*w,pz)))
    if lastvs:
        for i in range(len(ts)-1):
            for ix in [(lastvs[i],vs[i],vs[i+1]),(lastvs[i],vs[i+1],lastvs[i+1])]:
                f=bm.faces.new(ix);f.material_index=stone_index
                for loop in f.loops:
                    p=loop.vert.co
                    if mat_uv:loop[mat_uv].uv=(p.x,p.y)
                    if course:loop[course].uv=(p.y-min(station_rows[round(p.x,4)]),p.x-.6)
        for i in [0,-1]:
            p,q=lastvs[i],vs[i];q2=bm.verts.new(q.co-Vector((0,0,.65)));p2=bm.verts.new(p.co-Vector((0,0,.65)))
            face=bm.faces.new((p,q,q2,p2));face.material_index=1-stone_index
    lastvs=vs
bm.normal_update();bm.to_mesh(shoulder.data);bm.free();shoulder.data.update();changed.add(shoulder.name)
road_record['fork_stations']=len(xs);road_record['fork_section_samples']=len(ts)
