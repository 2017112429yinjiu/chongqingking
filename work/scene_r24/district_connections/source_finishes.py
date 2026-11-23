# Source-side photographic finishes. Runtime uses the same resources and a room-local vertex light field.
def finish_map(material,key,path,color=True,scale=1.,normal=False):
    tree=material.node_tree;tex=tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(path),check_existing=True)
    if not color:tex.image.colorspace_settings.name='Non-Color'
    uv=tree.nodes.new('ShaderNodeTexCoord');mapping=tree.nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs['Scale'].default_value=scale
    tree.links.new(uv.outputs['UV'],mapping.inputs[0])
    value=mapping.outputs[0]
    if material==mat['kitchenfloor']:
        rot=tree.nodes.new('ShaderNodeVectorRotate');rot.rotation_type='Z_AXIS';rot.inputs['Angle'].default_value=math.pi*.25
        tree.links.new(value,rot.inputs['Vector']);value=rot.outputs[0]
    tree.links.new(value,tex.inputs['Vector'])
    value=tex.outputs['Color']
    if normal:
        nm=tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.48;tree.links.new(value,nm.inputs['Color']);value=nm.outputs['Normal']
    tree.links.new(value,tree.nodes.get('Principled BSDF').inputs[key])
for key,prefix,width in [('kitchenfloor','interior_tiles',1.37),('oldstep','old_mosaic_floor',2.0)]:
    for kind,slot in [('diff','Base Color'),('rough','Roughness'),('nor_gl','Normal')]:
        finish_map(mat[key],slot,out/'surfaces'/f'{prefix}_{kind}_2k.jpg',kind=='diff',1./width,kind=='nor_gl')
finish_map(mat['steel'],'Roughness',project/'assets/characters/serving_counter_r18_CQ_Steel_ROUGHNESS.png',False)
finish_map(mat['steel'],'Normal',project/'assets/characters/serving_counter_r18_CQ_Steel_NORMAL.png',False,1.,True)
finish_map(mat['noodleplaster'],'Base Color',project/'assets/chongqing_district_plastered_wall_04_diff_1k.jpg',True,.54)
paper=material('HandwrittenNotice',(.75,.68,.51),.85,0)
finish_map(paper,'Base Color',out/'soup_notice.jpg')
scene.objects['D18_SoupNotice'].data.materials[0]=paper

for kind,ext,slot in [("diff","jpg","Base Color"),("nor_gl","jpg","Normal"),("rough","png","Roughness")]:
    finish_map(mat["dado"],slot,project/"assets"/f"chongqing_district_tile_cream_v4_{kind}.{ext}",kind=="diff",1./2.85,kind=="nor_gl")
