"""Regrade the existing CC0 scans for worn school finishes, preserving surface detail."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

here=Path(__file__).resolve().parent
assets=here.parents[3]/"work/project/chongqing_godot_v05/assets"
def plate(source,name,base,contrast):
    im=Image.open(assets/("chongqing_district_"+source)).convert("RGB").resize((1024,1024),Image.Resampling.LANCZOS)
    rgb=np.asarray(im,dtype=float)
    y=rgb @ [0.2126,0.7152,0.0722]
    # Preserve broad hand-applied variation as well as scratches and fibres.
    height=np.asarray(Image.fromarray(np.uint8(y)).filter(ImageFilter.GaussianBlur(7)),dtype=float)
    shade=(height-np.median(height))*.90+(y-height)*1.20
    if name=="school_screed":
        # Wear over a broader patch of the smoothly finished floor, taken from
        # the same scan. Wrap the low-frequency pattern across the tile edges.
        broad=np.asarray(Image.fromarray(np.uint8(y)).resize((64,64),Image.Resampling.LANCZOS).resize((1024,1024),Image.Resampling.BICUBIC),dtype=float)
        shade+=1.1*np.roll(broad-np.median(broad),(187,391),axis=(0,1))
    graded=np.clip(np.array(base)+shade[:,:,None]*np.array(contrast),0,255)
    Image.fromarray(np.uint8(np.round(graded))).save(here/(name+".jpg"),quality=94,subsampling=0)
def passage_paint():
    # Use actual plaster pits for small exposed lime flecks. An independent
    # broad mask concentrates worn spots rather than speckling the entire wall.
    src=np.asarray(Image.open(assets/"chongqing_district_plastered_wall_04_diff_1k.jpg").convert("L"),dtype=float)
    broad=np.asarray(Image.fromarray(np.uint8(src)).filter(ImageFilter.GaussianBlur(15)),dtype=float)
    patch=np.roll(broad,(213,377),axis=(0,1))
    loss=np.clip((patch-np.percentile(patch,68))*.30,0,1)*np.clip((broad-src-6.)*.14,0,1)
    tone=(src-np.median(src))*.84
    green=np.array((100,123,115))+tone[:,:,None]
    exposed=np.array((187,181,159))+tone[:,:,None]*.7
    rgb=green*(1-loss[:,:,None])+exposed*loss[:,:,None]
    Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(here/"school_passage.jpg",quality=94,subsampling=0)

if __name__=="__main__":
    plate("plastered_wall_04_diff_1k.jpg","school_lime",(225,220,209),(.80,.86,.94))
    plate("concrete_floor_worn_001_diff_2k.jpg","school_screed",(92,81,68),(1.72,1.57,1.42))
    plate("wood_table_worn_diff_2k.jpg","school_pine",(147,120,91),(1.62,1.52,1.18))
    passage_paint()
