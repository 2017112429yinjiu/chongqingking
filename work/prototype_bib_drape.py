"""Independent full-panel gravity trial with real neck-corner and waist anchors.
No production asset mutation. Review this rest shape before any transfer.
"""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parent;out=root/'characters/cloth_bib_trial'
source=out/'input_character.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;scene.frame_set(1)
rig=bpy.data.objects['ShopkeeperRig'];rig.animation_data.action=None
for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
apron=bpy.data.objects['CQ_SoftApron']
for mod in apron.modifiers:
    if mod.type=='SOLIDIFY':mod.show_viewport=False;mod.show_render=False
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
mesh=bpy.data.meshes.new_from_object(apron.evaluated_get(deps),depsgraph=deps)
trial=bpy.data.objects.new('CQ_FreeBibTrial',mesh);scene.collection.objects.link(trial)
trial.matrix_world=apron.matrix_world
initial=[v.co.copy() for v in trial.data.vertices]
pins=trial.vertex_groups.new(name='Neck corners and waist seam')
for v in trial.data.vertices:
    p=trial.matrix_world@v.co
    if (p.z>1.219 and abs(p.x)>.100) or abs(p.z-.911)<.008:pins.add([v.index],1,'REPLACE')
for original in list(scene.objects):
    if original.type!='MESH' or not ('casualsuit' in original.name or original.name=='ShopkeeperBody'):continue
    m=bpy.data.meshes.new_from_object(original.evaluated_get(deps),depsgraph=deps)
    ob=bpy.data.objects.new('Collider_'+original.name,m);scene.collection.objects.link(ob);ob.matrix_world=original.matrix_world
    ob.modifiers.new('Garment collision','COLLISION');ob.collision.thickness_outer=.003;ob.collision.thickness_inner=.001
    ob.hide_render=True
for ob in scene.objects:
    if ob.type=='MESH' and ob.name.startswith('CQ_') and ob!=trial:ob.hide_render=True
cloth=trial.modifiers.new('Free bib gravity trial','CLOTH')
cloth.settings.quality=10;cloth.settings.mass=.22
cloth.settings.tension_stiffness=22;cloth.settings.compression_stiffness=22;cloth.settings.shear_stiffness=10
cloth.settings.bending_stiffness=.08;cloth.settings.air_damping=4
cloth.settings.vertex_group_mass=pins.name;cloth.settings.pin_stiffness=1
cloth.collision_settings.use_collision=True;cloth.collision_settings.distance_min=.003;cloth.collision_settings.collision_quality=5
cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=150;scene.render.fps=30
for frame in range(1,151):
    scene.frame_set(frame);bpy.context.view_layer.update()
    evaluated=trial.evaluated_get(bpy.context.evaluated_depsgraph_get());evaluated.to_mesh();evaluated.to_mesh_clear()
    if frame%30==0:print('FREE_BIB_FRAME',frame,flush=True)
evaluated=trial.evaluated_get(bpy.context.evaluated_depsgraph_get());m=evaluated.to_mesh();final=[v.co.copy() for v in m.vertices];evaluated.to_mesh_clear()
changes=[(a-b).length for a,b in zip(initial,final)]
report={'experimental_only':True,'input_sha256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),'frames':150,'vertices':len(final),'max_displacement_m':max(changes),'mean_displacement_m':sum(changes)/len(changes),'initial':[list(v) for v in initial],'final':[list(v) for v in final]}
(out/'drape_result.json').write_text(json.dumps(report))
trial.modifiers.clear()
for vertex,co in zip(trial.data.vertices,final):vertex.co=co
solid=trial.modifiers.new('Thin woven edge','SOLIDIFY');solid.thickness=.0012
# Restore first idle only for the visible character; cloth is a static trial.
rig.animation_data.action=bpy.data.actions['idle'];scene.frame_set(1)
scene.world.color=(.14,.14,.14)
def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
for name,position,energy,size in [('Softbox',(2,-3,3),450,3),('Fill',(-2,-1,2),220,2)]:
    light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='DISK';light.size=size
    ob=bpy.data.objects.new(name,light);scene.collection.objects.link(ob);ob.location=position;aim(ob,(0,0,1))
cam=bpy.data.cameras.new('Free bib diagnostic');ob=bpy.data.objects.new('Free bib diagnostic',cam);scene.collection.objects.link(ob)
ob.location=(.8,-2.5,1.38);aim(ob,(0,0,1.0));cam.lens=65;scene.camera=ob
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=900;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'drape_trial.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'cloth_bib_trial.blend'),compress=True);bpy.ops.render.render(write_still=True)
print('FREE_BIB_TRIAL',json.dumps({k:v for k,v in report.items() if k not in ['initial','final']}),flush=True)
