"""Original procedural micro-normal bake. No third-party maps or photo claims."""
import bpy
def bake(human,out):
    material=human.data.materials[0];nt=material.node_tree;bs=nt.nodes.get('Principled BSDF')
    coords=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=620;noise.inputs['Detail'].default_value=2.2;noise.inputs['Roughness'].default_value=.57
    nt.links.new(coords.outputs['Object'],noise.inputs['Vector'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.28;bump.inputs['Distance'].default_value=.00022
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    image=bpy.data.images.new('CQ_Skin_MicroNormal',width=2048,height=2048,alpha=False)
    image.colorspace_settings.name='Non-Color';image.generated_color=(.5,.5,1,1)
    texture=nt.nodes.new('ShaderNodeTexImage');texture.image=image;nt.nodes.active=texture
    bpy.ops.object.select_all(action='DESELECT');human.select_set(True);bpy.context.view_layer.objects.active=human
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.device='CPU'
    scene.render.bake.margin=12;scene.render.bake.use_clear=True
    print('SKIN_MICRONORMAL_BAKE',flush=True)
    bpy.ops.object.bake(type='NORMAL')
    image.filepath_raw=str(out/'skin_micro_normal.png');image.file_format='PNG';image.save();image.pack()
    for link in list(bs.inputs['Normal'].links):nt.links.remove(link)
    normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.65
    nt.links.new(texture.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
    bs.inputs['Roughness'].default_value=.58
    print('SKIN_MICRONORMAL_SAVED',flush=True)
