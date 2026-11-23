"""Original brushed-steel surface, baked in Blender for portable glTF PBR."""
import bpy

def bake(material,out):
    nt=material.node_tree;bs=nt.nodes.get('Principled BSDF')
    uv=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1,220,1)
    nt.links.new(uv.outputs['UV'],mapping.inputs[0])
    grain=nt.nodes.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=2;grain.inputs['Detail'].default_value=1.5
    nt.links.new(mapping.outputs[0],grain.inputs['Vector'])
    broad=nt.nodes.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=5;broad.inputs['Detail'].default_value=2
    nt.links.new(uv.outputs['UV'],broad.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=0;ramp.inputs['From Max'].default_value=1
    ramp.inputs['To Min'].default_value=.30;ramp.inputs['To Max'].default_value=.46
    nt.links.new(broad.outputs['Fac'],ramp.inputs['Value']);nt.links.new(ramp.outputs[0],bs.inputs['Roughness'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.20;bump.inputs['Distance'].default_value=.00005
    nt.links.new(grain.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    bpy.ops.mesh.primitive_plane_add(size=1)
    plane=bpy.context.object;plane.name='Baking surface only';plane.data.materials.append(material)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.device='CPU';scene.render.bake.margin=8
    images={}
    for kind in ['NORMAL','ROUGHNESS']:
        im=bpy.data.images.new('CQ_Steel_'+kind,width=1024,height=1024,alpha=False);im.colorspace_settings.name='Non-Color'
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;nt.nodes.active=tex
        bpy.ops.object.select_all(action='DESELECT');plane.select_set(True);bpy.context.view_layer.objects.active=plane
        bpy.ops.object.bake(type=kind)
        im.filepath_raw=str(out/f'steel_{kind.lower()}.png');im.file_format='PNG';im.save();im.pack();images[kind]=tex
    for socket in ['Roughness','Normal']:
        for link in list(bs.inputs[socket].links):nt.links.remove(link)
    normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.7
    nt.links.new(images['NORMAL'].outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
    nt.links.new(images['ROUGHNESS'].outputs['Color'],bs.inputs['Roughness'])
    bpy.data.objects.remove(plane,do_unlink=True)
    print('BRUSHED_STEEL_MAPS_BAKED',flush=True)
