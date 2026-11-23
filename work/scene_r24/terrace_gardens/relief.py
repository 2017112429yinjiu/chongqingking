"""Filter normals across real paving batch boundaries without shading actual risers or kerbs."""
from pathlib import Path
import numpy as np
from site_data import scene,here,Surfaces
from grade import obj
names=('COL_Terrain_200m','COL_Road_176034707_0_pavement','COL_Road_176034707_0_asphalt','COL_D18_NanquShoulder')
surface=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith(names) or o==obj)])
z=np.zeros((209,273),dtype=np.float32);valid=np.zeros_like(z)
for j in range(len(z)):
    for i in range(z.shape[1]):
        h=surface.down(24+i*.25,-34-j*.25,23,20)
        if h:z[j,i]=h[0][0];valid[j,i]=1
def filter_samples(a,sigma):
    r=math.ceil(3*sigma);k=np.exp(-.5*(np.arange(-r,r+1)/sigma)**2);k/=k.sum()
    for axis in [0,1]:a=np.apply_along_axis(lambda row:np.convolve(np.pad(row,(r,r),'edge'),k,'valid'),axis,a)
    return a
import math
v=filter_samples(valid,3.4)
h=filter_samples(z,3.4)/np.maximum(v,.00001)
dz,dx=np.gradient(h,.25,.25)
n=np.stack((-dx,np.ones_like(z),-dz),axis=-1);n=n/np.linalg.norm(n,axis=-1,keepdims=True)
image=np.dstack((n*.5+.5,np.clip((v-.40)/.5,0.,1.)))
np.save(here/'terrace_normals.npy',np.uint8(np.round(np.clip(image,0.,1.)*255)))
