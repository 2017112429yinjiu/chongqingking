from pathlib import Path
import json, numpy as np
from PIL import Image, ImageDraw
p=Path(__file__).resolve().parent
project=p.parents[1]/"project/chongqing_godot_v05"
river=json.loads((project/"source_data/river_r22/river_plan.json").read_bytes())
extent=3600.;cell=3.0;size=int(2*extent/cell)
water=Image.new("L",(size,size));occupied=Image.new("L",water.size)
def footprint(ring):
    return [(round((x+extent)/cell),round((extent-y)/cell)) for x,y in ring]
for ring in river["rings"]:
    ImageDraw.Draw(water).polygon(footprint(ring["points"]),fill=255 if ring["role"]=="outer" else 0)
for building in river["buildings"]:
    ImageDraw.Draw(occupied).polygon(footprint(building["points"]),fill=255)
def overlap(ring,src):
    arr=np.array(ring)
    x0,y0=arr.min(0);x1,y1=arr.max(0)+1
    if x0<0 or y0<0 or x1>size or y1>size:return 1.
    fig=Image.new('1',(int(x1-x0),int(y1-y0)))
    ImageDraw.Draw(fig).polygon([(int(x-x0),int(y-y0)) for x,y in ring],fill=1)
    mask=np.asarray(fig); background=np.asarray(src.crop((int(x0),int(y0),int(x1),int(y1))))
    return float((background[mask]>0).mean())
chosen=[]
for layer in ["white","river"]:
    rows=json.loads((p/f"mass_{layer}.json").read_bytes())
    for r in sorted(rows,key=lambda m:-(m['top']-m['bottom'])*m['area']**.7):
        ring=footprint(r["hull"]);center=np.mean(r['hull'],axis=0)
        if np.linalg.norm(center)<470 or r['top']<27 or r['bottom']>240 or overlap(ring,water)>.22 or overlap(ring,occupied)>.15:continue
        ImageDraw.Draw(occupied).polygon(ring,fill=255)
        chosen.append(r)
(p/'selected.json').write_text(json.dumps(chosen,separators=(',',':')),encoding='utf8')
print({s:sum(r['src']==s for r in chosen) for s in ['white','river']})

