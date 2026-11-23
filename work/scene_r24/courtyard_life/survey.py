from pathlib import Path
import sys,json,math
folder=Path(__file__).resolve().parent
sys.path.insert(0,str(folder.parent/'stair_neighborhood'))
from site_neighborhood import *
def sample(x,z):
    rows=floors(x,-z)
    return round(rows[0][0],3) if rows else None
for x,z in [(-14.2,15.1),(-14.7,15.4),(-14.5,14.45),(-67.1,18.5),(-67.9,18.15),(-67.5,14.35)]:
    print('GRADES',x,z,sample(x,z),[sample(x+u,z+v) for u,v in [(-.55,0),(.55,0),(0,-.55),(0,.55)]])
    relevant=[]
    for ob in scene.objects:
        if ob.type!='MESH' or ob.hide_render:continue
        lo,hi=extent(ob)
        if lo[0]-1.1<x<hi[0]+1.1 and lo[1]-1.1<-z<hi[1]+1.1 and lo[2]<sample(x,z)+2. and hi[2]>sample(x,z)+.19 and not visible_ground(ob):
            relevant.append(ob.name)
    print('NEAR',relevant[:45])

