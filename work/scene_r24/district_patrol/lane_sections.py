from pathlib import Path
import sys,bpy
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import Surfaces,scene
pieces=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('COL_Terrain_200m','COL_East17','COL_Walk_','Walk_details_','COL_R23_PathFoundations'))]
s=Surfaces(pieces)
for x in [34,36,38,40,42,44,46,48,50,52,54]:
    print('EAST',x,[[round(z,2),round(y*.5,2),name.replace('COL_Terrain_200m_','t_').replace('COL_Walk_East_photo_alley_','east_')] for y in range(-2,14) for z,name,n in s.down(x,y*.5,26,7) if name.startswith(('COL_Terrain','COL_Walk_East'))])
for x,y in [(27.7,19),(26,15),(26,16),(27,17),(28,18),(26,19),(27,20),(28,20),(29,20)]:
    print('BACK',x,y,[(round(z,3),name) for z,name,n in s.down(x,y,27,6)])
