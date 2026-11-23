from pathlib import Path
import bpy,json,hashlib
root=Path(__file__).resolve().parent;source=root/'characters/serving_counter_r18/serving_counter.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));deps=bpy.context.evaluated_depsgraph_get();points=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh();points.extend(evaluated.matrix_world@v.co for v in mesh.vertices);evaluated.to_mesh_clear()
report={'source_sha256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),'objects':len(bpy.context.scene.objects),'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],'images':[{'name':im.name,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE']}
(root/'audit/r18_counter_source.json').write_text(json.dumps(report,indent=2));print('COUNTER_SOURCE_AUDIT',json.dumps(report))
