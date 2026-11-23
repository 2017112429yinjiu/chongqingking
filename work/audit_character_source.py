from pathlib import Path
import bpy,json
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'characters/shopkeeper_r18/shopkeeper_authoring.blend'))
rig=bpy.data.objects['ShopkeeperRig']
report={'bones':[b.name for b in rig.pose.bones],'actions':[a.name for a in bpy.data.actions],
 'images':[{'name':im.name,'packed':bool(im.packed_file),'path':im.filepath} for im in bpy.data.images if im.source=='FILE'],'face_meshes':[]}
for ob in bpy.data.objects:
    if ob.type=='MESH' and any(x in ob.name for x in ['brow','lashes','low-poly']):
        points=[ob.matrix_world@v.co for v in ob.data.vertices]
        report['face_meshes'].append({'name':ob.name,'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],'positions':[list(p) for p in points[:12]]})
(root/'audit/r18_source_integrity.json').write_text(json.dumps(report,indent=2))
print('SOURCE_CHECK',json.dumps(report),flush=True)
