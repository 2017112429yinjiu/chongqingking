import sys,json,math,bpy
from pathlib import Path
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent
s=bpy.context.scene
hits={}
for o in s.objects:
    if o.type!='MESH' or o.hide_render:continue
    lo,hi=extent(o)
    if hi[0]<-63.25 or lo[0]>-61.1 or hi[1]<-9.0 or lo[1]>-7 or hi[2]<19.9 or lo[2]>22.1:continue
    parts=[]
    for p in o.data.vertices:
        x,y,h=o.matrix_world@p.co
        if -63.25<x<-61.1 and -9.0<y<-7 and 19.9<h<22.1:parts.append((x,-y,h))
    if parts:hits[o.name]=[len(parts),[round(min(v[i] for v in parts),3) for i in range(3)],[round(max(v[i] for v in parts),3) for i in range(3)]]
print('OPENING',hits,flush=True)
try:import numpy as np
except ImportError:raise
tree=[s.objects['Planted_tree_22_0'+str(i)] for i in range(3)]
origin=tree[0].matrix_world.translation
parts=[]
for o in tree:
    coords=np.array([list(o.matrix_world@p.co) for p in o.data.vertices]);parts.append((coords[:,0]-origin.x,-coords[:,1]+origin.y,coords[:,2]))
for center_z in [7.55,7.85,8.0]:
    for west in [-65.1,-66.55]:
        for i,(xx,zz,h) in enumerate(parts):
            x=origin.x+xx;z=-origin.y+zz
            deck=(x>=west)&(x<-61.17)&(z>center_z-.90)&(z<center_z+.90)&(h>19.84)&(h<22.19)
            stair_y=19.89-np.clip((west-x)/4.2,0.,1.)*2.55
            steps=(x>west-4.2)&(x<west)&(z>center_z-.90)&(z<center_z+.90)&(h>stair_y-.05)&(h<stair_y+2.30)
            print('WEST',center_z,west,i,int(deck.sum()),int(steps.sum()),flush=True)
for i,(xx,zz,h) in enumerate(parts):
    x=origin.x+xx;z=-origin.y+zz
    for right in [-61.75,-61.88,-62.00,-62.10]:
        overlap=(x>-65.80)&(((x<right)&(z>7.14)&(z<8.95))|((x<-61.19)&(z>=8.45)&(z<9.06)))&(h>19.84)&(h<22.20)
        print('FACECLEAR',i,right,int(overlap.sum()))
scores=[]
for deg in range(0,360,5):
    a=math.radians(deg);m=math.cos(a);n=math.sin(a);score=[]
    for xx,zz,h in parts:
        x=origin.x+xx*m+zz*n;z=-origin.y-xx*n+zz*m
        along=np.clip((x+61.2)/3.36,0.,1.)
        stair_y=19.89-along*2.04
        mid=(x>-63.4)&(x<-57.65)&(z>5.0)&(z<7.05)&(h>stair_y-.04)&(h<stair_y+2.30)
        deck=(x>-63.30)&(x<-61.03)&(z>6.9)&(z<9.1)&(h>19.84)&(h<22.19)
        wall=(z>9.04)&(x>-66)&(x<-53)&(h<25.)
        score.append([int((mid|deck).sum()),int(wall.sum())])
    scores.append((deg,score))
print('CANOPY_FIT',sorted(scores,key=lambda a:sum(p[0]+p[1] for p in a[1]))[:6],scores[0],flush=True)
(here/'opening_check.json').write_text(json.dumps({'opening':hits,'rotations':scores}),'utf8')
