import sys,json,bpy
from pathlib import Path
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p))
from trim_paving import footprints
for key in ['COL_Walk_Central_stair_lane_step_concrete','COL_Court_east_entry_steps_step_concrete']:
    o=bpy.data.objects[key]
    rows=[]
    for c,rs in footprints(o):
        if c.x<0 and abs(c.y)<4:rows.append(dict(center=list(c),ring=[list(t) for t in rs]))
    print(key,[(tuple(round(t,3) for t in a['center']),[tuple(round(v,2) for v in q[:2]) for q in a['ring']]) for a in rows],flush=True)

