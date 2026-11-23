import bpy,json
from pathlib import Path
from mathutils import Vector
folder=Path(__file__).resolve().parent
rows=[]
for ob in bpy.context.scene.objects:
 if not ob.name.startswith('Planted_tree_') or ob.type!='MESH':continue
 rows.append({'name':ob.name,'points':len(ob.data.vertices),'local_bounds':[[round(o,4) for o in v] for v in [ob.bound_box[0],ob.bound_box[6]]],'matrix':[list(v) for v in ob.matrix_world],'material':list(m.name for m in ob.data.materials)})
(folder/'tree_inventory.json').write_text(json.dumps(rows))

kinds={o['name'].rsplit('_',1)[0]:('island_tree_01' if 'island_tree' in o['material'][0] else 'tree_small_02') for o in rows if o['name'].endswith('_02')}
(folder.parents[1]/'project/chongqing_godot_v05/assets/neighborhood_r24/tree_species.json').write_text(json.dumps(kinds,indent=2))
