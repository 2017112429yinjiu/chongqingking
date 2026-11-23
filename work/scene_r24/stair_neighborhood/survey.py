from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_neighborhood import *
for x in [-22.25,-21.9,-21.55,-21.25,-21.,-20.75,-20.5,-20.25,-20.,-19.75,-19.5,-19.25,-19.]:
 print('SECTION',x,[(y,[(round(z,2),n.replace('COL_','')[:29]) for z,n,_ in floors(x,y)[:2]]) for y in [-15,-14,-12,-10,-8,-5,-2]],flush=True)
D=[]
for c,ring in tread_rows('COL_Walk_Central_stair_lane_step_concrete'):
 if -18<c.y<4: D.append([list(c),[list(v) for v in ring]])
(root/'court_steps.json').write_text(json.dumps(D),'utf-8')
print('RAILS',[(o.name,extent(o)) for o in scene.objects if o.type=='MESH' and ('rail' in o.name.lower() or 'handhold' in o.name.lower()) and not o.hide_render][:60])
print('PROPS',[(o.name,extent(o)) for o in scene.objects if o.type=='MESH' and o.name.startswith(('CQF_Crates_wood_','Resident_waste_0_crate','R19_Stair_resident_pot_A_02'))][:14])

