# SPDX-License-Identifier: GPL-3.0-or-later
"""Build a clothed, rigged character from individually licensed CC0 core assets.
MPFB is a GPL build tool; its source is kept outside the runtime game.
"""
from pathlib import Path
import bpy,sys,json,math,hashlib,shutil
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'characters/shopkeeper_r18';OUT.mkdir(parents=True,exist_ok=True)
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
for key,value in {'gender':1.,'age':.73,'muscle':.46,'weight':.61,'height':.53,'asian':1.,'caucasian':0.,'african':0.}.items():
    HumanObjectProperties.set_value(key,value,entity_reference=human)
TargetService.reapply_macro_details(human)
targets=ROOT/'assets_incoming/mpfb/mpfb2-master/src/mpfb/data/targets'
for target,value in {'head/head-age-incr':.22,'head/head-round':.03,'head/head-fat-incr':.08,'cheek/l-cheek-volume-incr':.035,'cheek/r-cheek-volume-incr':.05,'chin/chin-jaw-drop-decr':.08,'mouth/mouth-angles-up':.10,'mouth/mouth-laugh-lines-out':.10,'eyes/l-eye-bag-incr':.12,'eyes/r-eye-bag-incr':.10,'eyes/l-eye-height2-incr':.08,'eyes/r-eye-height2-incr':.06}.items():
    TargetService.load_target(human,str(targets/(target+'.target.gz')),weight=value)
for side in ['left','right']:
    key=TargetService.load_target(human,str(targets/f'expression/units/asian/eye-{side}-closure.target.gz'),weight=0)
    key.name='Blink_'+side
smile=TargetService.load_target(human,str(targets/'expression/units/asian/mouth-corner-puller.target.gz'),weight=0)
smile.name='Smile'
TargetService.load_target(human,str(targets/'expression/units/asian/mouth-compression.target.gz'),weight=.12)
for side in ['left','right']:
    TargetService.load_target(human,str(targets/f'expression/units/asian/eyebrows-{side}-inner-up.target.gz'),weight=.18)

used=[]
def licensed(path):
    text=path.read_text(encoding='utf-8')
    assert 'CC0' in text,(path,'missing individual CC0 header')
    used.append({'file':str(path.relative_to(DATA)),'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),'license':'CC0-1.0','source_header':text.split('name ')[0][:1200]})
    return str(path)
HumanService.set_character_skin(licensed(DATA/'skins/old_asian_male/old_asian_male.mhmat'),human,skin_type='GAMEENGINE')
HumanService.add_builtin_rig(human,'game_engine')
for folder,name,kind in [('eyes','low-poly','Eyes'),('eyebrows','eyebrow012','Eyebrows'),('hair','short04','Hair'),('clothes','male_casualsuit01','Clothes'),('clothes','shoes02','Clothes')]:
    clothing=DATA/folder/name/(name+'.mhclo')
    material_line=next(line.split(maxsplit=1)[1] for line in clothing.read_text(encoding='utf-8').splitlines() if line.startswith('material '))
    licensed((clothing.parent/material_line).resolve())
    HumanService.add_mhclo_asset(licensed(DATA/folder/name/(name+'.mhclo')),human,asset_type=kind,material_type='GAMEENGINE',subdiv_levels=0)
rig=human.parent
rig.name='ShopkeeperRig'
human.name='ShopkeeperBody'
# Garment and animation are separate reproducible authoring modules.
sys.path.insert(0,str(ROOT))
from shopkeeper_tailoring import build
from shopkeeper_performance import animate
from shopkeeper_face_rig import build as build_face_rig
build_face_rig(rig,human)
shirt=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'casualsuit' in o.name)
for ob in bpy.context.scene.objects:
    if ob.type=='MESH':
        for poly in ob.data.polygons:poly.use_smooth=True
        for slot in ob.material_slots:
            if slot.material and slot.material.use_nodes:
                bs=slot.material.node_tree.nodes.get('Principled BSDF')
                if bs:
                    bs.inputs['Roughness'].default_value=.64 if ob==human else .79
                    bs.inputs['Metallic'].default_value=0
                    bs.inputs['Emission Strength'].default_value=0
                    # Opaque surfaces must write depth and receive proper facial shadows.
                    # MPFB GAMEENGINE wired an alpha texture into every material.
                    alpha=bs.inputs['Alpha'];links=list(alpha.links)
                    if any(key in slot.material.name for key in ['hair','short01','short04','eyebrow','eyelash']):
                        if links:
                            source=links[0].from_socket
                            for link in links:slot.material.node_tree.links.remove(link)
                            clip=slot.material.node_tree.nodes.new('ShaderNodeMath');clip.operation='GREATER_THAN';clip.inputs[1].default_value=.25
                            slot.material.node_tree.links.new(source,clip.inputs[0]);slot.material.node_tree.links.new(clip.outputs[0],alpha)
                    else:
                        for link in links:slot.material.node_tree.links.remove(link)
                        alpha.default_value=1
for mod in human.modifiers:
    if mod.type=='SUBSURF':mod.levels=1;mod.render_levels=1
if not any(m.type=='SUBSURF' for m in human.modifiers):
    sub=human.modifiers.new('Face and body surface refinement','SUBSURF');sub.levels=1;sub.render_levels=1
from shopkeeper_skin import bake
bake(human,OUT)
build(rig,shirt,ROOT)
from shopkeeper_drape_bake import apply as apply_drape
apply_drape(ROOT,OUT)
from shopkeeper_bib_drape import apply as apply_bib_drape
apply_bib_drape(ROOT,OUT)
animate(rig,OUT)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'shopkeeper_authoring.blend'),compress=True)
from export_shopkeeper_mesh import export_character
game=ROOT/'project/chongqing_godot_v05/assets/characters'
objects,low,high,scale=export_character(human,game/'shopkeeper_r18.glb')
manifest={'name':'梯坎小面店主','height_m':1.71,'base':'MPFB 2.0.18 core human','assets':used,'animations':['idle','serve','greet'],
 'animation_method':'Idle: 100STYLE Neutral_ID frames 700-1300, recorded pelvis/chest/head/wrist deltas retargeted, bounded and loop-blended, feet fixed with IK. Serve/greet: original authored contact performance. All baked at 30 Hz. Weighted hem bones, not live cloth simulation.','source_license':'Meshes/textures CC0-1.0; idle motion CC-BY-4.0; MPFB tool code GPL-3.0-or-later (not in game)',
 'motion_credit':'The 100STYLE Dataset - Ian Mason','motion_source':'https://www.ianxmason.com/100style/','motion_license_url':'https://creativecommons.org/licenses/by/4.0/',
 'author_credit':'MakeHuman team; Data Collection AB; Joel Palmius; Jonas Hauquier. Attribution voluntary for CC0.',
 'vertices':sum(len(o.data.vertices) for o in objects if o.type=='MESH'), 'meshes':len([o for o in objects if o.type=='MESH']),
 'original_additions':'Cut draped apron with curved pocket, curved bound seams, cupped shoulder tapes, waist ties and hem bones; two articulated eye joints, skin-fitted relaxed eyebrows, runtime blink and smile shapes. Poly Haven Cotton Jersey CC0 PBR maps; colormass and Rico Cilliers, voluntary attribution.',
 'evaluated_floor_before_normalization':low,'evaluated_height_before_normalization':high-low,'export_scale':scale}
(OUT/'PROVENANCE.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(OUT/'PROVENANCE.json',game/'shopkeeper_r18_provenance.json')
shutil.copy2(ROOT/'assets_incoming/mpfb/mpfb2-master/LICENSE.ASSETS.md',game/'MakeHuman_CC0_LICENSE.txt')
notice=(ROOT/'assets_incoming/100style/LICENSE_NOTICE.txt').read_text(encoding='utf-8')
notice+='\nModified for this game: Neutral_ID frames 700-1300, retargeted pelvis/chest/head/wrist deltas, scaled and bounded, fixed-foot IK, 30 Hz resampling and final-second loop blend. Serving and greeting remain original authored performances. Neutral_FW is not integrated.\n'
(game/'100STYLE_CC_BY_4.0_NOTICE.txt').write_text(notice,encoding='utf-8')
print('SHOPKEEPER_EXPORTED',json.dumps({k:v for k,v in manifest.items() if k!='assets'},ensure_ascii=False),flush=True)
