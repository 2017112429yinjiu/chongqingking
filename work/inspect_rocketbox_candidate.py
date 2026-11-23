"""Import the untouched MIT candidate in an isolated Blender scene for inspection."""
from pathlib import Path
import bpy,json
root=Path(__file__).resolve().parent;source=root/'assets_incoming/rocketbox_research/Male_Adult_10'
out=root/'characters/rocketbox_candidate10';out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(source/'Export/Male_Adult_10_facial.fbx'),use_anim=False)
report={'objects':[],'materials':[],'images':[]}
for ob in bpy.context.scene.objects:
    item={'name':ob.name,'type':ob.type,'scale':list(ob.scale),'location':list(ob.location),'hidden':ob.hide_get()}
    if ob.type=='MESH':
        coords=[ob.matrix_world@v.co for v in ob.data.vertices]
        item.update({'vertices':len(ob.data.vertices),'bounds':[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)],'materials':[m.name for m in ob.data.materials],'shapes':[k.name for k in ob.data.shape_keys.key_blocks] if ob.data.shape_keys else []})
    if ob.type=='ARMATURE':item['bones']=[b.name for b in ob.data.bones]
    report['objects'].append(item)
for mat in bpy.data.materials:
    report['materials'].append({'name':mat.name,'textures':[{'node':n.name,'label':n.label,'image':n.image.name if n.image else None,'linked_to':[(l.to_node.name,l.to_socket.name) for out_socket in n.outputs for l in out_socket.links]} for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'] if mat.use_nodes else []})
for im in bpy.data.images:report['images'].append({'name':im.name,'path':im.filepath,'size':list(im.size)})
(out/'import_audit.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out/'raw_import.blend'),compress=True)
print('ROCKETBOX_IMPORTED',json.dumps({'meshes':[{k:o[k] for k in ['name','vertices','bounds','materials']} for o in report['objects'] if o['type']=='MESH'],'materials':report['materials'],'images':report['images']}),flush=True)
