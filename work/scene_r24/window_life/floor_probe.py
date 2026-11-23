import bpy,sys
from pathlib import Path
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import floors
for x,z in [(-33.7,75.3),(-32.5,74.9),(-30.7,74.9),(-29.8,75.2),(-28.7,75.3),(-70.1,21.44),(-68.8,21.6)]:
 print('FLOOR',x,z,[(round(h,3),o) for h,o,n in floors(x,-z)[:3]])
