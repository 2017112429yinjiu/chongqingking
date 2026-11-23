"""Sample the finished walkable slope in world metres to carry its lighting continuously across batches."""
from pathlib import Path
import sys,numpy as np
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import scene,Surfaces,road_objects
fallback=Surfaces(road_objects)
s=Surfaces([ob for ob in scene.objects if ob.type=='MESH' and not ob.hide_render and ob.name.startswith(('COL_Terrain_200m','COL_D18_NanquShoulder','COL_Road_176034707_0_pavement','COL_Road_176034707_0_asphalt'))])
h=np.empty((129,193),dtype=np.float32)
for j in range(129):
    for i in range(193):
        x=30.+i*.1875;y=-60.-j*.1875
        hits=s.down(x,y,22,19)
        if not hits:hits=fallback.down(x,y,22,19)
        h[j,i]=hits[0][0] if hits else np.nan
gaps=np.argwhere(~np.isfinite(h))
print('SLOPE_GRID_VOID',len(gaps),gaps[:20],flush=True)
(here/'slope_grid_gaps.json').write_text(__import__('json').dumps([[30.+float(i)*.1875,60.+float(j)*.1875] for j,i in gaps]),'utf8')
# Outside the two rendered surface batches an empty pixel only supplies a filtering margin.
# Raw void positions are written to the independent collision audit.
for j,i in gaps:
    patch=h[max(0,j-1):j+2,max(0,i-1):i+2]
    if np.isfinite(patch).any():h[j,i]=np.nanmedian(patch)
assert np.isfinite(h).all()
np.save(here/'shoulder_profile.npy',h)
