"""Bring the original curb face to the measured asphalt boundary at the south road fork."""
from roads import scene,changed,road_record
from survey import road_objects,Surfaces
o=scene.objects['COL_D18_NanquShoulder']
other=Surfaces([v for v in road_objects if v!=o and v.name=='COL_Road_49182408_0_asphalt' and not v.hide_render])
rows={}
for v in o.data.vertices:
    p=v.co
    if 22.1<p.x<34.48:rows.setdefault(round(p.x,4),[]).append(v)
moves=[]
for x,verts in rows.items():
    y=min(v.co.y for v in verts);top=max(v.co.z for v in verts if abs(v.co.y-y)<.0002)
    def supported(d):
        return bool(other.down(x,y-d,top+.4,1.2))
    if supported(.0004):continue
    lo,hi=.0004,.18
    if not supported(hi):continue
    for i in range(22):
        mid=(lo+hi)*.5
        if supported(mid):hi=mid
        else:lo=mid
    for v in verts:
        if abs(v.co.y-y)<.00016:v.co.y-=hi
    moves.append([x,y,hi])
o.data.update();changed.add(o.name);road_record['south_asphalt_joint']=moves
