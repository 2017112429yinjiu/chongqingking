from pathlib import Path
import json,sys
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import road,work
plan=json.loads((work/'project/chongqing_godot_v05/assets/frontage_r24/frontage.json').read_text('utf8'))
for name,vs in plan['parked_contacts'].items():
    print('PARK',name,[(round(z-h[0][0],3),h[0][1]) for x,z,y in vs if (h:=road.down(x,-y,z+.8,2))],flush=True)
