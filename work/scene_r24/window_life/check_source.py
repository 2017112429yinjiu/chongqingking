from pathlib import Path
import bpy,json
here=Path(__file__).resolve().parent
scene=bpy.context.scene
assert scene['street_revision']=='R24 build 15 lived-in windows'
members=bpy.data.collections['R24_15_WindowRooms'].objects
assert len(members)==6 and all(o.type=='MESH' and o.data.polygons for o in members)
skins={}
for role in ('red','black','greens'):
    inst=scene.objects['Court14_Resident_'+role]
    objs=inst.instance_collection.objects
    rig=next(o for o in objs if o.type=='ARMATURE')
    path=Path(bpy.path.abspath(rig.library.filepath))
    assert path.exists() and rig.animation_data.action.name=='courtyard_'+role
    if role=='greens':assert path.parent.name=='kitchen'
    skins[role]=str(path.resolve())
stains={}
for name in ('B_A01_noodle_details_moss_grime','B_A04_courtyard_home_details_moss_grime'):
    ob=scene.objects[name];assert ob.data.uv_layers.get('PatchBorder')
    assert any(n.type=='UVMAP' and n.uv_map=='PatchBorder' for n in ob.material_slots[0].material.node_tree.nodes)
    stains[name]=len(ob.data.polygons)
assert not any(o.name.startswith('Room15_Patina') for o in scene.objects)
texture=bpy.data.materials['Window15_oldwood'].node_tree
images=[n.image for n in texture.nodes if n.type=='TEX_IMAGE']
assert images and all(im.packed_file for im in images)
record={'opened':str(Path(bpy.data.filepath).resolve()),'version':bpy.app.version_string,'window_furnishings':[o.name for o in members],'existing_room_sources':skins,'softened':stains,'packed_timber':[im.name for im in images]}
(here/'reopen.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
print('ROOM15_REOPEN',len(members),len(skins),len(stains))
