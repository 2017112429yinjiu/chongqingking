"""Trace to eye/head height through all visible Blender triangles, including non-collision props."""
from pathlib import Path
import bpy,sys,json,math
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent,Surfaces
objects=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH' or obj.hide_render:continue
    lo,hi=extent(obj)
    if hi[0]<-70.8 or lo[0]>-54 or hi[1]<-20.5 or lo[1]>-7.0 or hi[2]<16.4 or lo[2]>22.4:continue
    objects.append(obj)
surfaces=Surfaces(objects)
checks=[];fail=[];overhead=[]
def station(zone,x,z,y):
    hits=[]
    for lo,hi,o in surfaces.cells.get((math.floor(x/8),math.floor(-z/8)),[]):
        if not(lo[0]-.001<=x<=hi[0]+.001 and lo[1]-.001<=-z<=hi[1]+.001 and hi[2]>=y+.025 and lo[2]<=y+2.36):continue
        hit=surfaces.tree(o).ray_cast((x,-z,y+.025),(0,0,1),2.335)[0]
        if hit is not None:hits.append([round(hit.z-y,4),o.name])
    checks.append((zone,x,z,y))
    if hits:overhead.append([zone,round(x,3),round(z,3),sorted(hits)])
    if any(v[0]<2.10 for v in hits):fail.append(overhead[-1])
for side in [-.31,0.,.31]:
    start=-55.42;y=16.44
    for run,step in [(.258,1)]*9+[(.81,0)]+[(.258,1)]*11:
        y+=step*3.45/20
        station('inside flight',start-run*.5,19.50+side,y);start-=run
    for j in range(42):station('upper corridor',-62.44+side,18.70-j*.24,19.89)
    for j in range(6):station('north gate',-62.48+side,9.05-j*.18,19.89)
    for j in range(16):station('gallery',-62.48-j*.20,8.04+side,19.89)
    for j in range(15):station('west steps',-65.80-(j+.5)*.28,8.04+side,19.89-(j+1)*.17)
with (here/'headroom.json').open('w',encoding='utf8') as f:json.dump({'sample_count':len(checks),'floor_relative_m':[.025,2.36],'minimum_clear_m':2.10,'overhead':overhead,'samples':checks,'hits':fail},f)
print('HEADROOM',len(checks),len(fail),fail[:10])
if fail:raise RuntimeError('Geometry in walking envelope')
