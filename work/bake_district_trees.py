"""Photograph two licensed scan meshes from four azimuths for exterior hillsides."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector
W=Path(__file__).resolve().parent
D=W/'scene_r21/canopy';D.mkdir(exist_ok=True)
source=W/'project/chongqing_blender_v05/scanned_assets/prepared_assets.blend'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=12
scene.render.resolution_x=448;scene.render.resolution_y=448;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
world=bpy.data.worlds.new('Cloud illumination');scene.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.78,.84,.90,1);bg.inputs[1].default_value=.8
for direction,energy in [((.3,-.7,1),2.0),((-.7,.45,.75),1.2)]:
    b=bpy.data.lights.new('Soft canopy light','SUN');ob=bpy.data.objects.new(b.name,b);scene.collection.objects.link(ob)
    ob.rotation_euler=Vector(direction).to_track_quat('Z','Y').to_euler();b.energy=energy;b.angle=.38
cam=bpy.data.cameras.new('Tree elevation');camera=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(camera);scene.camera=camera;cam.type='ORTHO'
stats={}
for row,key in enumerate(['tree_small_02','island_tree_01']):
    with bpy.data.libraries.load(str(source),link=False) as (src,dst):
        dst.objects=sorted(n for n in src.objects if n.startswith('PH_'+key+'_hero_'))
    parts=dst.objects
    for o in parts:scene.collection.objects.link(o)
    bpy.context.view_layer.update()
    coords=[o.matrix_world@v.co for o in parts for v in o.data.vertices]
    low=min(p.z for p in coords);high=max(p.z for p in coords)
    radius=max(max(abs(p.x),abs(p.y)) for p in coords)
    size=max(high-low,radius*2)*1.07
    cam.ortho_scale=size
    # Place the root at a known pixel; use this pivot in the engine billboards.
    mid=Vector((0,0,low+size*.48));stats[key]={'frame_width_over_height':size/(high-low),'root_fraction':.02}
    for col in range(4):
        a=col*math.pi/2
        camera.location=mid+Vector((math.sin(a),-math.cos(a),.025))*13
        camera.rotation_euler=(mid-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(D/f'{row}_{col}.png');bpy.ops.render.render(write_still=True)
    for o in parts:bpy.data.objects.remove(o,do_unlink=True)
(D/'pivot.json').write_text(json.dumps(stats,indent=2))
