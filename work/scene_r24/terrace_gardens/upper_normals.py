"""Measure the receiving pavements beside the old school, east alley and central flight."""
from pathlib import Path
import sys,math,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_data import here,scene,Surfaces
source=Surfaces([o for o in scene.objects if o.name in ['COL_Terrain_200m_pavement','COL_Terrain_200m_yard_concrete']])
# Sample in the same orientation as Godot world XZ. Ignore real stair risers and walls.
z=np.zeros((249,217),np.float32);ok=np.zeros_like(z)
for j in range(249):
    for i in range(217):
        hit=source.down(-43+i*.5,96-j*.5,61,65)
        if hit:z[j,i]=hit[0][0];ok[j,i]=1.
k=np.exp(-.5*(np.arange(-6,7)/2.)**2);k/=sum(k)
def filt(a):
    for axis in (0,1):a=np.apply_along_axis(lambda r:np.convolve(np.pad(r,6,'edge'),k,'valid'),axis,a)
    return a
valid=filt(ok);zz=filt(z)/np.maximum(valid,.0001);dz,dx=np.gradient(zz,.5,.5)
n=np.stack((-dx,np.ones_like(z),-dz),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
np.save(here/'upper_normals.npy',np.uint8(np.round(np.dstack((.5+n*.5,np.clip((valid-.65)/.32,0.,1.)))*255)))
