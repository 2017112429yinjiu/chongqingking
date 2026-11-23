from pathlib import Path
from PIL import Image
import numpy as np
here=Path(__file__).resolve().parent;h=np.load(here/'shoulder_profile.npy')
w=np.arange(-9,10);weight=np.exp(-.5*(w/3.6)**2);weight=weight/weight.sum()
for axis in [0,1]:h=np.apply_along_axis(lambda row:np.convolve(np.pad(row,(9,9),'edge'),weight,'valid'),axis,h)
dz,dx=np.gradient(h,.1875,.1875)
n=np.stack((-dx,np.ones_like(dx),-dz),axis=-1);n=n/np.linalg.norm(n,axis=-1,keepdims=True)
img=Image.fromarray(np.round((n*.5+.5)*255).astype(np.uint8))
img.save(here.parents[1]/'project/chongqing_godot_v05/assets/district_age/shoulder_gradient.png')
