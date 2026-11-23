"""Export the fitted MPFB body, retained facial shapes, rig and garment meshes."""
import bpy

def export_character(human, path):
    from bl_ext.cq_tools.mpfb.services.exportservice import ExportService
    from bl_ext.cq_tools.mpfb.services.objectservice import ObjectService
    export_root=ExportService.create_character_copy(human,name_suffix='_game')
    export_human=ObjectService.find_object_of_type_amongst_nearest_relatives(export_root,'Basemesh')
    ExportService.bake_modifiers_remove_helpers(export_human,bake_masks=True,bake_subdiv=True,remove_helpers=True,also_proxy=True)
    objects=[export_root]+ObjectService.get_list_of_children(export_root)
    for ob in objects:
        for mod in ob.modifiers:
            if mod.type=='ARMATURE':mod.object=export_root
        if ob.type=='MESH' and ob.data.color_attributes.get('GarmentWear'):
            ob.data.color_attributes.active_color=ob.data.color_attributes['GarmentWear']
    # Bake static phenotype into the base, retaining only the two runtime eyelids.
    if export_human.data.shape_keys:
        keys=export_human.data.shape_keys.key_blocks
        basis=[v.co.copy() for v in keys[0].data]
        closures={k.name:[v.co-basis[i] for i,v in enumerate(k.data)] for k in keys if k.name.startswith('Blink_') or k.name=='Smile'}
        mixed=export_human.shape_key_add(name='FinalPhenotype',from_mix=True)
        coords=[v.co.copy() for v in mixed.data]
        export_human.shape_key_clear()
        for v,co in zip(export_human.data.vertices,coords):v.co=co
        export_human.shape_key_add(name='Basis')
        for name,deltas in closures.items():
            key=export_human.shape_key_add(name=name)
            for i,v in enumerate(key.data):v.co=coords[i]+deltas[i]
            key.value=0
    bpy.context.view_layer.update()
    verts=[]
    deps=bpy.context.evaluated_depsgraph_get()
    for o in objects:
        if o.type!='MESH':continue
        evaluated=o.evaluated_get(deps);mesh=evaluated.to_mesh()
        verts.extend(evaluated.matrix_world@v.co for v in mesh.vertices)
        evaluated.to_mesh_clear()
    low=min(v.z for v in verts);high=max(v.z for v in verts);scale=1.71/(high-low)
    export_root.scale*=scale
    export_root.location.z-=low*scale
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=export_root
    path.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_morph=True,export_apply=True,export_extras=True,export_vertex_color='ACTIVE',export_all_vertex_colors=False)
    return objects,low,high,scale
