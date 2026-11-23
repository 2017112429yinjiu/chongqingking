from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_data import scene,Surfaces
obs=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith(('COL_Road_734116597_0','COL_Terrain_200m','COL_R21_Footing_Upper_road','COL_R23_PathFoundations','COL_Walk_')))]
s=Surfaces(obs)
for x in [-28,-25,-22,-20,-18,-16,-13,-10]:
    y=86.431-(x+29.669)*.58885
    print('NORTH',x,[(d,[(round(h,2),n.replace('COL_Road_734116597_0_','R.').replace('COL_Terrain_200m_','T.')) for h,n,_ in s.down(x+.508*d,y+.862*d,35,6)[:3]]) for d in [-.15,.02,.70,1.13,1.24,1.55,2.1,3.2]],flush=True)
