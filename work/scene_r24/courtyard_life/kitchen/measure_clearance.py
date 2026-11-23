"""Test all trouser/knee skin vertices in the footprint of the household work surface."""
from pathlib import Path
import bpy,sys,json
here=Path(__file__).resolve().parent
target=here/sys.argv[-1]
sc=bpy.context.scene
mesh=next(o for o in sc.objects if o.type=='MESH' and o.vertex_groups and len(o.data.vertices)>100)
groups={g.index for g in mesh.vertex_groups if any(k in g.name for k in ('Thigh','Calf','Pelvis','Foot'))}
ids=[v.index for v in mesh.data.vertices if v.groups and max(v.groups,key=lambda g:g.weight).group in groups]
times=[]
for f in range(0,193,6):
 sc.frame_set(f);ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
 pts=[ev.matrix_world@ev.data.vertices[i].co for i in ids]
 under=[p for p in pts if -.365<=p.x<=.295 and .211<=-p.y<=.591]
 # Cross rails sit 82 mm below the top, and are 16 mm thick.
 # Restrict their clearance to where a leg actually passes underneath a rail.
 rails=[p for p in under if abs(abs(p.x+.035)-.264)<.017 and abs(-p.y-.401)<.16 or abs(abs(-p.y-.401)-.1444)<.017 and abs(p.x+.035)<.282]
 times.append(dict(frame=f,knee_top=max(p.z for p in under),rail_knee_top=max((p.z for p in rails),default=0.),vertices=len(under)))
max_knee=max(k['knee_top'] for k in times);max_rail=max(k['rail_knee_top'] for k in times)
import math
height=math.ceil(100*max(max_knee+.03+.05,max_rail+.098+.04))/100
rec={'worst_knee_top':max_knee,'worst_under_rail':max_rail,'tabletop_y':height,'old_table_gap_m':.525-.03-max_knee,'board_clearance':height-.03-max_knee,'rail_clearance':height-.098-max_rail,'sampled':times}
target.write_text(json.dumps(rec,indent=2),'utf8')
print('KITCHEN_CLEARANCE',height,max_knee,max_rail,flush=True)
