"""Derive a district-scale use mask from the projected walking routes and specific surveyed shop thresholds."""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
root=Path(__file__).resolve().parent
assets=root.parents[1]/'project/chongqing_godot_v05/assets'
dest=assets/'street_use_r24'
dest.mkdir(exist_ok=True)
size=1024
scale=size/200
def pixel(x,z): return ((x+100)*scale,(z+100)*scale)
def blank(): return Image.new('L',(size,size))
def stroke(image,points,width,value):
    ImageDraw.Draw(image).line([pixel(*pt) for pt in points],fill=value,width=max(1,round(width*scale)),joint='curve')
def soften(image,metres): return np.asarray(image.filter(ImageFilter.GaussianBlur(scale*metres)),dtype=float)/255
def noise(seed,side):
    rng=np.random.default_rng(seed)
    tile=Image.fromarray(rng.integers(0,256,(side,side),dtype=np.uint8))
    return np.asarray(tile.resize((size,size),Image.Resampling.BICUBIC),dtype=float)/255
base_routes=json.loads((assets/'scene_manifest.json').read_text('utf-8-sig'))['routes']
repairs=json.loads((assets/'geometry_repairs_r17.json').read_text('utf-8-sig'))['routes']
replaced={row['name'] for row in repairs}
routes=[row for row in base_routes if row['name'] not in replaced]+repairs
wear=blank(); borders=blank(); sinks=blank()
for route in routes:
    pts=[(x,-y) for x,y in route['points']]
    width=route['width_m']
    stroke(wear,pts,width*.54,235)
    for a,b in zip(pts,pts[1:]):
        dx,dz=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dz)
        if length<.01: continue
        for sign in [-1,1]:
            ox=-dz/length*width*.48*sign;oz=dx/length*width*.48*sign
            stroke(borders,[(a[0]+ox,a[1]+oz),(b[0]+ox,b[1]+oz)],.6,215)
# Draw the protected strip and wet work area where the stall actually stands.
for path,width,value in [
    ([(-29.8,74.70),(-28.5,75.38),(-27.1,75.69),(-26.3,75.82)],.68,252),
    ([(-29.25,74.9),(-29.3,75.8),(-29.0,76.3),(-28.6,76.6)],.46,215),
    ([(-14.55,72.0),(-14.4,74.55),(-14.1,75.1)],.56,188),
    ([(-32.1,73.7),(-27.6,73.4),(-22.0,73.9)],.75,180)]:
    stroke(sinks,path,width,value)
fine=noise(83,248);broad=noise(92,57)
traffic=np.clip(soften(wear,.46)*(.80+.25*broad),0,1)
edge=np.clip(soften(borders,.23)*(.43+.75*broad)*(.74+.35*fine),0,1)
wet=np.clip(soften(sinks,.20)*(.55+.68*fine),0,1)
Image.fromarray(np.uint8(np.stack((traffic,edge,wet),axis=-1)*255)).save(dest/'street_use.png')

