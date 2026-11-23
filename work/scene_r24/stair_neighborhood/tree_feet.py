import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
folder=Path(__file__).resolve().parent
layout=json.loads((folder/'geometry_report.json').read_text())
trunks=[]
for idx,rec in enumerate(layout['plants']):
 if not rec['donors'][0].startswith('Planted_tree_'):continue
 ob=bpy.context.scene.objects[f'N13_Greenery_{idx:02d}_1']
 at=rec['at'];soil=at[1]+.054
 pts=[ob.matrix_world@v.co for v in ob.data.vertices];band=[v for v in pts if .12<v.z-soil<.58]
 if len(band)<3:raise RuntimeError(ob.name)
 # Estimate a conservative solid from trunk section samples. Outer roots and branches remain visual.
 x=statistics.median(q.x for q in band);y=statistics.median(q.y for q in band)
 distances=sorted(((v.x-x)**2+(v.y-y)**2)**.5 for v in band)
 radius=max(.09,min(.39,distances[len(distances)//3]))
 trunks.append({'plant':idx,'base':[x,soil-.05,-y],'height':min(1.8,rec['scale']*3.2),'radius':radius,'sample_vertices':len(band)})
print('N13_TRUNKS',trunks)
(folder.parents[1]/'project/chongqing_godot_v05/assets/neighborhood_r24/trunk_sections.json').write_text(json.dumps(trunks,indent=2))
