"""Bake exterior land use from mapped roads, actual context blocks and planted groves."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np, json,math
W=Path(__file__).resolve().parent
A=W/'project/chongqing_godot_v05/assets/district_r21'
s=W/'project/chongqing_blender_v05/source_data/geo_layout.json'
geo=json.loads(s.read_text(encoding='utf8'));layout=json.loads((A/'layout.json').read_text(encoding='utf8'))
info=json.loads((W/'scene_r21/district_rays.json').read_text(encoding='utf8'))
size=1536;radius=360;scale=size/(2*radius)
def pix(x,y):return ((x+radius)*scale,(y+radius)*scale)
def canvas():return Image.new('L',(size,size),0)
pads=canvas();roads=canvas();trees=canvas()
dp=ImageDraw.Draw(pads);dr=ImageDraw.Draw(roads);dt=ImageDraw.Draw(trees)
for b in geo['context_buildings']+geo['buildings']:
    pts=[pix(*v[:2]) for v in b['points']]
    dp.polygon(pts,fill=245);dp.line(pts+[pts[0]],fill=225,width=round(8*scale),joint='curve')
for name,v in info['meshes'].items():
    if name.startswith('Context_authored_'):
        a,b=v['bounds'];dp.rounded_rectangle([pix(a[0]-3,a[1]-3),pix(b[0]+3,b[1]+3)],radius=7,fill=235)
for r in geo['roads']+geo['paths']:
    if r['tags'].get('tunnel')=='yes':continue
    pts=[pix(*v[:2]) for v in r['points']]
    width=max(2.1,float(r.get('width') or (6.0 if r in geo['roads'] else 2.3)))
    if len(pts)>1:
        dp.line(pts,fill=235,width=round((width+4.5)*scale),joint='curve')
        dr.line(pts,fill=252,width=round(width*scale),joint='curve')
for tree in layout['outer_canopy']:
    x,_,z=tree['position'];r=tree['height']*.53
    dt.ellipse([pix(x-r,-z-r),pix(x+r,-z+r)],fill=215)
out=Image.merge('RGB',(pads.filter(ImageFilter.GaussianBlur(4.2)),roads.filter(ImageFilter.GaussianBlur(1.25)),trees.filter(ImageFilter.GaussianBlur(6.8))))
out.save(A/'exterior_land.png')
