"""Grade the outer pavement to the existing terrace. Preserve the car's four tyre patches."""
import math,bmesh,json
from mathutils import Vector
from roads import scene,changed,road_record,asset
from survey import work
def ramp(a,b,t):
    t=max(0.,min(1.,(t-a)/(b-a)));return t*t*(3.-2.*t)
edge_mesh=scene.objects['COL_Road_176034707_0_pavement']
spans=[]
for f in edge_mesh.data.polygons:
    if f.normal.z<.20:continue
    pts=[edge_mesh.matrix_world@edge_mesh.data.vertices[i].co for i in f.vertices]
    if max(p.x for p in pts)<46.99 or min(p.x for p in pts)>70:continue
    spans+=list(zip(pts,pts[1:]+pts[:1]))
def outer(x):
    rows=[]
    for a,b in spans:
        if min(a.x,b.x)-.00001<=x<=max(a.x,b.x)+.00001 and abs(b.x-a.x)>.00002:
            p=a.lerp(b,(x-a.x)/(b.x-a.x))
            if abs(p.y-(-75.897+.43*(x-47)))<5:rows.append((p.y,p.z))
    return max(rows) if rows else None
contacts=json.loads((work/'project/chongqing_godot_v05/assets/frontage_r24/frontage.json').read_text('utf8'))['parked_contacts']['Parked_car_46_-78']
patches=[(x,-y) for x,z,y in contacts]
# A wheel usually lands inside a large paving triangle. Protect the vertices supporting its
# actual contact patch, even when each triangle corner lies outside the tyre's own radius.
seats=set()
for ob in scene.objects:
    if ob.type!='MESH' or not ob.name.startswith('COL_Terrain_200m'):continue
    for f in ob.data.polygons:
        if f.normal.z<.45:continue
        vs=[ob.matrix_world@ob.data.vertices[i].co for i in f.vertices]
        if max(v.x for v in vs)<49 or min(v.x for v in vs)>55 or max(v.y for v in vs)<-74.5 or min(v.y for v in vs)>-69.:continue
        for a,c in patches:
            if min(v.x for v in vs)-.22<a<max(v.x for v in vs)+.22 and min(v.y for v in vs)-.22<c<max(v.y for v in vs)+.22:
                seats.update(tuple(round(k,4) for k in q) for q in vs);break
altered={}
for ob in scene.objects:
    if ob.type!='MESH' or not ob.name.startswith('COL_Terrain_200m'):continue
    count=0
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co;x,y,z=p
        if not 46.998<x<65 or not -81<y<-62:continue
        if tuple(round(k,4) for k in p) in seats:continue
        rim=outer(max(47.0002,x))
        if not rim:continue
        by,h=rim;d=y-by
        if not -1.55<d<4.6:continue
        protected=min(math.hypot(x-a,y-b) for a,b in patches)
        weight=(1.-ramp(60,65,x))*(1.-ramp(1.1,4.55,d))*ramp(.45,1.03,protected)
        target=h+.128*d+.011*max(0.,d)**2
        if d<-.12:target=min(z,h+.18*d-.055);weight*=ramp(-1.55,-.45,d)
        p.z+=weight*(target-z);v.co=ob.matrix_world.inverted()@p;count+=1
    if count:ob.data.update();changed.add(ob.name);altered[ob.name]=count
# The historic fascia was fitted against the old terrain. Seat its upper rail on the road edge
# and its lower rail just inside the new ground on the outer side, leaving the carriageway curbs intact.
from survey import Surfaces
ground=Surfaces([o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Terrain_200m') and not o.hide_render])
ob=scene.objects['COL_R24_JunctionStem_R24_junction_stem'];bm=bmesh.new();bm.from_mesh(ob.data);remove=[]
for f in bm.faces:
    p=f.calc_center_median()
    if not 47.<p.x<64.8 or not -80<p.y<-61:continue
    rim=outer(p.x)
    if not rim or abs(p.y-rim[0])>.18:continue
    pts=sorted([v.co for v in f.verts],key=lambda q:q.z,reverse=True)
    hits=[ground.down(q.x,q.y+.035,q.z+.5,1.5) for q in pts[:2]]
    if all(h and q.z-h[0][0]<.052 for q,h in zip(pts[:2],hits)):remove.append(f)
if remove:bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(ob.data);ob.data.update();changed.add(ob.name)
bm.free();road_record['joined_outer_sidewalk']={'vertices':altered,'old_panels':len(remove)}
