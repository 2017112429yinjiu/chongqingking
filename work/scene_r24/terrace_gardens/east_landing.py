"""Ease the southern entry to the transverse landing at the turn of the east alley."""
from site_data import scene,here,Surfaces,save
from grade import changed
from mathutils import Vector
import bmesh,math
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
ground=[scene.objects[n] for n in ('COL_Terrain_200m_pavement','COL_Terrain_200m_yard_concrete')]
stair=Surfaces([scene.objects['COL_Walk_East_photo_alley_step_concrete']])
source=Surfaces(ground)
for ob in ground:source.tree(ob)
def edge(x):return 3.751-(x-34.964)*.02861
def existing(x,y):
    rows=source.down(x,y,23.5,4.)
    return rows[0][0] if rows else None
def cap(x):
    s=min(41.2,max(35.,x));y=edge(s)+.056
    h=stair.down(s,y,23.4,3.)
    if not h:raise ValueError(('landing edge',s,y))
    return h[0][0]
def lift(x,y):
    dist=y-edge(x)
    if not -2.9<dist<2.2 or not 32.65<x<41.2:return 0.
    sw=smooth((x-32.65)/1.75)*(1.-smooth((x-38.)/3.2))
    weight=smooth((dist+2.9)/2.84)*(1.-smooth((dist-.12)/2.08))
    lower=existing(x,edge(x)-.018)
    if lower is None:return 0.
    return max(0.,cap(x)-lower-.072)*sw*weight
counts={}
for ob in ground:
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
    local=[f for f in bm.faces if min(v.co.x for v in f.verts)<42. and max(v.co.x for v in f.verts)>32. and min(v.co.y for v in f.verts)<6.2 and max(v.co.y for v in f.verts)>.2]
    if not local:bm.free();continue
    for coord,stations in [(0,[32.+i*.32 for i in range(32)]),(1,[.2+i*.30 for i in range(21)])]:
        for value in stations:
            selected=[f for f in local if f.is_valid and min(v.co[coord] for v in f.verts)<value-.00001 and max(v.co[coord] for v in f.verts)>value+.00001]
            if not selected:continue
            geom=set(selected)
            for f in selected:geom.update(f.verts);geom.update(f.edges)
            n=Vector((1,0,0)) if coord==0 else Vector((0,1,0))
            res=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.000002,plane_co=n*value,plane_no=n)
            local=list({f for f in local if f.is_valid}|{f for f in res['geom'] if isinstance(f,bmesh.types.BMFace)})
    count=0
    for v in {v for f in local if f.is_valid for v in f.verts}:
        disp=lift(v.co.x,v.co.y)
        if disp>.000001:v.co.z+=disp;count+=1
    if count:bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update();counts[ob.name]=count;changed.setdefault(ob.name,0)
    bm.free()
after=Surfaces(ground);rows=[]
for i in range(41):
    x=35.+i*.06;y=edge(x)-.021;h=after.down(x,y,23.5,4.)[0][0]
    rows.append([x,cap(x)-existing(x,y),cap(x)-h])
save('east_landing.json',{'vertices':counts,'rise_across_toe':rows})
print('EAST_LANDING',rows[5],counts)
