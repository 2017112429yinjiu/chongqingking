"""Facade-local damp, lime and patch weights. Z follows the street; Y follows the lintels."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
folder=Path(__file__).resolve().parent;work=folder.parents[1]
dest=work/'project/chongqing_godot_v05/assets/courtyard_r24'
rng=np.random.default_rng(4228);W,H=1280,768
z,y=np.meshgrid(9+(np.arange(W)+.5)*21/W,26-(np.arange(H)+.5)*11/H)
def noise(w,h):
    im=Image.fromarray(rng.integers(0,256,(h,w),dtype=np.uint8))
    return np.asarray(im.resize((W,H),Image.Resampling.BICUBIC)).astype(float)/255.
b=noise(48,23);fine=noise(214,142);grain=noise(720,400)
grime=np.zeros_like(z);salt=grime.copy()
j=json.loads((folder/'window_survey.json').read_text())
for name,polys in j:
    if 'details_glass' not in name:continue
    for x,center,cy,width,height in polys:
        if width<.55 or height<1.3:continue
        sill=cy-height/2-.06
        for sign in [-1,1]:
            at=center+sign*width*.5
            downward=sill-y
            reach=rng.uniform(.38,.92);w=rng.uniform(.021,.055)+.030*np.clip(downward,0,1)
            streak=np.exp(-((z-at-(b-.5)*.052)/w)**2)*np.clip(1-downward/reach,0,1)*np.clip(downward/.07,0,1)
            grime=np.maximum(grime,streak*(.52+.48*fine))
# Uneven damp base and a mineral edge at the sheltered foot of the wall.
edge=16.65+.24*np.sin(z*.48)+.22*(b-.5)+.085*(fine-.5)
damp=np.clip((edge-y+.23)/.43,0,1)*(.23+.43*b)*(.72+.28*grain)
salt=np.exp(-((y-edge-.03)/.082)**2)*(.30+.70*fine)*np.clip((b-.25)/.5,0,1)
# A lime repair between window bays, and a smaller repair low beside the rack.
patch=np.zeros_like(z)
for zz,yy,ww,hh in [(19.49,17.30,.56,.26),(15.73,16.92,.31,.26),(22.97,18.35,.25,.34)]:
    edge_x=np.abs(z-zz)-ww+(fine-.5)*.055+(b-.5)*.09
    edge_y=np.abs(y-yy)-hh+(fine-.5)*.043+(b-.5)*.047
    patch=np.maximum(patch,np.clip(-np.maximum(edge_x,edge_y)/.053,0,1)*(.35+.50*fine+.15*grain))
rgb=np.dstack([np.maximum(damp,grime),salt,patch])
Image.fromarray(np.uint8(255*np.clip(rgb,0,1))).save(dest/'west_plaster.png',optimize=True)

