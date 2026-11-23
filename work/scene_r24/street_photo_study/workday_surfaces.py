from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
root=Path(__file__).resolve().parent
asset=root.parents[1]/'project/chongqing_godot_v05/assets'
dest=root/'workday_surfaces';dest.mkdir(exist_ok=True)
raw=Image.open(asset/'chongqing_district_wood_table_worn_diff_2k.jpg').convert('L').resize((768,768),Image.Resampling.LANCZOS)
val=np.asarray(raw,dtype=float)
mid=np.asarray(raw.filter(ImageFilter.GaussianBlur(5)),dtype=float)
lo,hi=np.quantile(val,[.035,.965])
grain=np.clip((val-mid)/max(4,(hi-lo)*.24),-1,1)
wear=np.clip((val-lo)/(hi-lo),0,1)
palettes={'timber':([65,49,39],[152,125,96]),'old_cane':([71,52,36],[156,122,80]),'split_bamboo':([94,70,47],[182,148,100]),'light_cane':([110,84,54],[192,164,119])}
for name,(shadow,light) in palettes.items():
    q=(.69*wear+.18+.10*grain)[:,:,None]
    pixels=np.array(shadow)+(np.array(light)-shadow)*q
    Image.fromarray(np.uint8(np.clip(pixels,0,255))).save(dest/(name+'.jpg'),quality=91,subsampling=0)
# Desaturated trolley paint with small, irregular losses at the scale of millimetres.
r=np.random.default_rng(334)
islands=Image.fromarray(r.integers(0,255,(96,96),dtype=np.uint8)).resize((768,768),Image.Resampling.BICUBIC)
field=np.asarray(islands,dtype=float)/255
chips=np.clip((.14-field)*12+np.clip(-grain,0,1)*.36,0,1)[:,:,None]
coating=np.array([90,106,90])+(wear[:,:,None]-.48)*24+grain[:,:,None]*3
iron=np.array([90,66,45])+(wear[:,:,None]-.5)*39
Image.fromarray(np.uint8(np.clip(coating*(1-chips)+iron*chips,0,255))).save(dest/'paint.jpg',quality=90,subsampling=0)

