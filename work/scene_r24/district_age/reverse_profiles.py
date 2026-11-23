from pathlib import Path
import sys,json
from mathutils import Vector
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import scene,Surfaces,road_objects
from math import hypot
cases=[(4,(66.85,72.97),(66.808,75.62),33.19),(13,(-47.70,-94.88),(-47.82,-93.6),6.14),(17,(16.19,-76.87),(16.147,-75.143),9.18),(23,(32.435,-64.395),(30.207,-64.432),11.13),(28,(-23.186,63.145),(-25.,64.),28.95)]
road=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('COL_','COLH_'))])
out={}
for key,a,b,h in cases:
    dx,dy=b[0]-a[0],b[1]-a[1];l=hypot(dx,dy);dx/=l;dy/=l
    rows=[]
    for k in range(-8,29):
        s=k*.18;x=a[0]+s*dx;y=a[1]+s*dy
        hits=road.down(x,y,h+2.3,3.8);rows.append([round(s,2),round(x,2),round(y,2),[(round(z,3),n) for z,n,_ in hits]])
    out[key]=rows
(here/'reverse_profiles.json').write_text(json.dumps(out),encoding='utf8')
