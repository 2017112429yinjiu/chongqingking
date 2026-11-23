from pathlib import Path
import json,bpy
here=Path(bpy.data.filepath).resolve().parent
scene=bpy.context.scene
assert scene['street_revision'] in ('R24 14c courtyard paving','R24 14d kitchen and courtyard paving')
actors={}
for role in ('black','red','greens'):
    instance=scene.objects['Court14_Resident_'+role]
    members=list(instance.instance_collection.objects)
    assert {o.type for o in members}=={'MESH','ARMATURE'}
    arm=next(o for o in members if o.type=='ARMATURE')
    assert arm.animation_data and arm.animation_data.action
    assert Path(bpy.path.abspath(arm.library.filepath)).is_file()
    if '14d' in scene['street_revision'] and role=='greens':
        assert Path(bpy.path.abspath(arm.library.filepath)).resolve()==here/'greens.blend'
    actors[role]=[str(arm.animation_data.action.name),len(arm.data.bones)]
assert not any(o.name.startswith('CourtPaving_') for o in scene.objects)
for name in ('pavement','yard_concrete'):assert len(scene.objects['COL_Terrain_200m_'+name].data.polygons)>1000
furn=[o for o in scene.objects if o.name.startswith('Court14_') and o.type=='MESH']
assert len(furn)>5
open_images=[]
for o in furn:
    for slot in o.material_slots:
        if not slot.material or not slot.material.use_nodes:continue
        for node in slot.material.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image:
                im=node.image
                assert im.packed_file or Path(bpy.path.abspath(im.filepath)).exists()
                open_images.append(im.name)
report={'file':str(Path(bpy.data.filepath).resolve()),'blender':bpy.app.version_string,'actors':actors,'furnishing_meshes':len(furn),'embedded_images':sorted(set(open_images))}
(here/'reopen.json').write_text(json.dumps(report,indent=2),'utf8')
print('COURT14_REOPEN',report)
