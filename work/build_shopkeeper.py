# SPDX-License-Identifier: GPL-3.0-or-later
"""Build a clothed, rigged character from individually licensed CC0 core assets.
MPFB is a GPL build tool; its source is kept outside the runtime game.
"""
from pathlib import Path
import bpy,sys,json,math,hashlib,shutil
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'characters/shopkeeper_r17';OUT.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'assets_incoming/mpfb/system_assets'
bpy.context.preferences.use_preferences_save=False
bpy.context.preferences.extensions.repos.new(name='CQ isolated tools',module='cq_tools',custom_directory=str(ROOT/'assets_incoming/mpfb/mpfb2-master/src'))
bpy.ops.preferences.addon_enable(module='bl_ext.cq_tools.mpfb')
from bl_ext.cq_tools.mpfb.services.humanservice import HumanService
from bl_ext.cq_tools.mpfb.services.targetservice import TargetService
from bl_ext.cq_tools.mpfb.services.exportservice import ExportService
from bl_ext.cq_tools.mpfb.services.objectservice import ObjectService
from bl_ext.cq_tools.mpfb.entities.objectproperties import HumanObjectProperties
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
human=HumanService.create_human()
for key,value in {'gender':1.,'age':.58,'muscle':.42,'weight':.57,'height':.53,'asian':1.,'caucasian':0.,'african':0.}.items():
    HumanObjectProperties.set_value(key,value,entity_reference=human)
TargetService.reapply_macro_details(human)
used=[]
def licensed(path):
    text=path.read_text(encoding='utf-8')
    assert 'CC0' in text,(path,'missing individual CC0 header')
    used.append({'file':str(path.relative_to(DATA)),'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),'license':'CC0-1.0','source_header':text.split('name ')[0][:1200]})
    return str(path)
HumanService.set_character_skin(licensed(DATA/'skins/middleage_asian_male/middleage_asian_male.mhmat'),human,skin_type='GAMEENGINE')
HumanService.add_builtin_rig(human,'game_engine')
for folder,name,kind in [('eyes','low-poly','Eyes'),('eyebrows','eyebrow001','Eyebrows'),('eyelashes','eyelashes01','Eyelashes'),('hair','short02','Hair'),('clothes','male_casualsuit01','Clothes'),('clothes','shoes02','Clothes')]:
    HumanService.add_mhclo_asset(licensed(DATA/folder/name/(name+'.mhclo')),human,asset_type=kind,material_type='GAMEENGINE',subdiv_levels=0)
rig=human.parent
rig.name='ShopkeeperRig'
human.name='ShopkeeperBody'
# Original fabric apron, fitted to the dressed torso. It belongs to the rig,
# rather than being a rectangular floating plate in the game world.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
shirt=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'casualsuit' in o.name)
deps=bpy.context.evaluated_depsgraph_get()
evaluated=shirt.evaluated_get(deps);shirt_mesh=evaluated.to_mesh()
surface=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in shirt_mesh.vertices],[list(p.vertices) for p in shirt_mesh.polygons])
evaluated.to_mesh_clear()
apron_mat=bpy.data.materials.new('CQ_Apron_WashedCotton');apron_mat.use_nodes=True
bs=apron_mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.30,.27,.20,1);bs.inputs['Roughness'].default_value=.92
def apron_piece(name,vertices,faces,material):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material);ob.parent=rig
    groups={n:ob.vertex_groups.new(name=n) for n in ['pelvis','spine_01','spine_02','spine_03']}
    anchors=[(.84,'pelvis'),(1.02,'spine_01'),(1.19,'spine_02'),(1.39,'spine_03')]
    for v in mesh.vertices:
        if v.co.z<=anchors[0][0]:groups['pelvis'].add([v.index],1.,'REPLACE');continue
        if v.co.z>=anchors[-1][0]:groups['spine_03'].add([v.index],1.,'REPLACE');continue
        for (za,ba),(zb,bb) in zip(anchors,anchors[1:]):
            if za<=v.co.z<=zb:
                weight=(v.co.z-za)/(zb-za)
                groups[ba].add([v.index],1-weight,'REPLACE');groups[bb].add([v.index],weight,'REPLACE');break
    arm=ob.modifiers.new('Apron follows torso','ARMATURE');arm.object=rig
    for p in mesh.polygons:p.use_smooth=True
    return ob
rows=25;cols=17;vertices=[];faces=[];fronts=[]
for iz in range(rows):
    z=max(.97,.64+iz/(rows-1)*.68)
    hits=[surface.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2.)[0] for x in [-.19,-.14,-.08,0,.08,.14,.19]]
    fronts.append(min(h.y for h in hits if h is not None)-.035)
fronts=[sum(fronts[max(0,i-1):min(rows,i+2)])/len(fronts[max(0,i-1):min(rows,i+2)]) for i in range(rows)]
for iz in range(rows):
    z=.64+iz/(rows-1)*.68
    width=.235 if z<1.03 else .235-(z-1.03)/.29*.085
    for ix in range(cols):
        x=(ix/(cols-1)*2-1)*width
        # A coherent draped front stays clear of shirt pockets and button gaps.
        y=fronts[iz]+.012*(x/width)**2
        y-=.007*math.sin(ix/(cols-1)*math.tau*3)*(1-(z-.64)/.68)
        vertices.append((x,y,z))
        if ix and iz:
            k=iz*cols+ix;faces.append((k-cols-1,k-cols,k,k-1))
apron=apron_piece('CQ_ShopApron',vertices,faces,apron_mat)
solid=apron.modifiers.new('Fabric thickness','SOLIDIFY');solid.thickness=.0018
# Neck straps and a stitched front pocket remain part of the same skeleton.
for side in [-1,1]:
    line=[(side*.135,-.15,1.31),(side*.10,-.10,1.40),(side*.085,.005,1.45),(side*.09,.075,1.39),(side*.14,.11,1.28)]
    vv=[(x+dx,y,z) for x,y,z in line for dx in [-.013,.013]]
    ff=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(line)-1)]
    apron_piece('CQ_ApronStrap_'+str(side),vv,ff,apron_mat)
apron_piece('CQ_ApronPocket',[(-.10,fronts[7]-.009,.83),(.10,fronts[7]-.009,.83),(.115,fronts[12]-.012,.99),(-.115,fronts[12]-.012,.99)],[(0,1,2,3)],apron_mat)
for ob in bpy.context.scene.objects:
    if ob.type=='MESH':
        for poly in ob.data.polygons:poly.use_smooth=True
        for slot in ob.material_slots:
            if slot.material and slot.material.use_nodes:
                node=next((n for n in slot.material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
                if node:
                    node.inputs['Roughness'].default_value=.68
                    node.inputs['Metallic'].default_value=0
                    node.inputs['Emission Strength'].default_value=0
def world_rotation(bone,axis,angle):
    basis=bone.bone.matrix_local.to_quaternion()
    return basis.inverted()@Quaternion(axis,angle)@basis
def arms_down():
    for side in ['l','r']:
        bone=rig.pose.bones['upperarm_'+side]
        direction=bone.bone.tail_local-bone.bone.head_local
        sign=1 if direction.x>0 else -1
        target=Vector((sign*.15,-.01,-.46))
        q=direction.rotation_difference(target)
        basis=bone.bone.matrix_local.to_quaternion()
        bone.rotation_quaternion=basis.inverted()@q@basis
    for bone in rig.pose.bones:
        if any(bone.name.startswith(p) for p in ['index_','middle_','ring_','pinky_']):
            bone.rotation_quaternion=Quaternion((1,0,0),.11)
for bone in rig.pose.bones:bone.rotation_mode='QUATERNION'
arms_down()
rest={b.name:b.rotation_quaternion.copy() for b in rig.pose.bones}
rig.animation_data_create()
bpy.context.scene.render.fps=24
for name,duration in [('idle',72),('serve',48)]:
    action=bpy.data.actions.new(name);rig.animation_data.action=action
    for frame in range(1,duration+2,3):
        phase=(frame-1)/duration
        for b in rig.pose.bones:b.rotation_quaternion=rest[b.name].copy()
        rig.pose.bones['spine_02'].rotation_quaternion=world_rotation(rig.pose.bones['spine_02'],(0,1,0),.008*math.sin(phase*math.tau))
        rig.pose.bones['head'].rotation_quaternion=world_rotation(rig.pose.bones['head'],(0,0,1),.022*math.sin(phase*math.tau))
        if name=='serve':
            reach=math.sin(math.pi*phase)**2
            for side in ['l','r']:
                b=rig.pose.bones['upperarm_'+side]
                b.rotation_quaternion=rest[b.name]@world_rotation(b,(1,0,0),-.55*reach)
                b=rig.pose.bones['lowerarm_'+side]
                b.rotation_quaternion=world_rotation(b,(1,0,0),-.32*reach)
        for b in rig.pose.bones:b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name)
    for curve in action.fcurves:
        for key in curve.keyframe_points:key.interpolation='BEZIER'
rig.animation_data.action=bpy.data.actions['idle']
bpy.context.scene.frame_set(1)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'shopkeeper_authoring.blend'),compress=True)
export_root=ExportService.create_character_copy(human,name_suffix='_game')
export_human=ObjectService.find_object_of_type_amongst_nearest_relatives(export_root,'Basemesh')
ExportService.bake_modifiers_remove_helpers(export_human,bake_masks=True,bake_subdiv=False,remove_helpers=True,also_proxy=True)
objects=[export_root]+ObjectService.get_list_of_children(export_root)
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
game=ROOT/'project/chongqing_godot_v05/assets/characters';game.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(game/'shopkeeper_r17.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_morph=False,export_apply=True,export_extras=True)
manifest={'name':'梯坎小面店主','height_m':1.71,'base':'MPFB 2.0.18 core human','assets':used,'animations':['idle','serve'],
 'animation_method':'Authored procedural keyframes, not motion capture; motion requires visual refinement.','source_license':'CC0-1.0; MPFB tool code GPL-3.0-or-later (not in game)',
 'author_credit':'MakeHuman team; Data Collection AB; Joel Palmius; Jonas Hauquier. Attribution voluntary for CC0.',
 'vertices':sum(len(o.data.vertices) for o in objects if o.type=='MESH'), 'meshes':len([o for o in objects if o.type=='MESH']),
 'original_additions':'Fitted cotton apron, neck straps and pocket; authored geometry.',
 'evaluated_floor_before_normalization':low,'evaluated_height_before_normalization':high-low,'export_scale':scale}
(OUT/'PROVENANCE.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(OUT/'PROVENANCE.json',game/'shopkeeper_r17_provenance.json')
shutil.copy2(ROOT/'assets_incoming/mpfb/mpfb2-master/LICENSE.ASSETS.md',game/'MakeHuman_CC0_LICENSE.txt')
print('SHOPKEEPER_EXPORTED',json.dumps({k:v for k,v in manifest.items() if k!='assets'},ensure_ascii=False),flush=True)
