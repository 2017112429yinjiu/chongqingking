import bpy,json
from pathlib import Path
from mathutils import Matrix
folder=Path(__file__).resolve().parent
dest=folder.parents[1]/'project/chongqing_godot_v05/assets/neighborhood_r24'
manifest=json.loads((folder.parents[1]/'project/chongqing_blender_v05/scanned_assets/manifest.json').read_text('utf-8-sig'))
bpy.ops.object.select_all(action='DESELECT')
copies=[];metrics={}
for species in ['island_tree_01','tree_small_02']:
 for level in ['medium','low']:
  names=manifest['prepared_assets'][species]['variants'][level]['objects']
  for part,name in enumerate(names):
   ob=bpy.data.objects[name]
   target=ob.copy();target.data=ob.data.copy();target.data.materials.clear()
   target.name=f'Canopy_{species}_{level}_{part}';target.parent=None;target.matrix_world=Matrix.Identity(4)
   bpy.context.scene.collection.objects.link(target);target.hide_set(False);target.hide_render=False;target.hide_viewport=False
   target.select_set(True);copies.append(target.name)
   metrics[target.name]=[list(target.bound_box[0]),list(target.bound_box[6]),len(target.data.polygons)]
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=str(dest/'tree_distances.glb'),export_format='GLB',use_selection=True,export_animations=False)
(folder/'tree_distances.json').write_text(json.dumps(metrics,indent=2))
print('N13_CANOPIES',len(copies),sum(row[2] for row in metrics.values()))
