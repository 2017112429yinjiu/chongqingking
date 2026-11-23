"""Re-cut the packed R18 apron and author a two-handed serving action."""
from pathlib import Path
import hashlib
import json
import math
import sys
import bpy
from mathutils import Matrix

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from export_shopkeeper_mesh import export_character
from shopkeeper_performance import animate

SOURCE=ROOT/'characters/shopkeeper_r18/shopkeeper_authoring.blend'
OUT=ROOT/'characters/shopkeeper_r21'
GAME=ROOT/'project/chongqing_godot_v05/assets/characters'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.preferences.filepaths.save_version=0
bpy.context.preferences.use_preferences_save=False
bpy.context.preferences.extensions.repos.new(name='CQ isolated tools',module='cq_tools',custom_directory=str(ROOT/'assets_incoming/mpfb/mpfb2-master/src'))
bpy.ops.preferences.addon_enable(module='bl_ext.cq_tools.mpfb')
rig=bpy.data.objects['ShopkeeperRig']
rig.animation_data.action=None
bpy.data.actions.remove(bpy.data.actions['serve'])
for bone in rig.pose.bones:
    bone.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for side,x in [('l',.09),('r',-.09)]:
    joint=rig.data.edit_bones.new('bib_'+side)
    joint.head=(x,-.155,1.08)
    joint.tail=(x,-.16,1.19)
    joint.parent=rig.data.edit_bones['spine_02']
bpy.ops.object.mode_set(mode='OBJECT')

# Cut in long bias folds from the tie and model their continuation across pocket,
# hem and stitch meshes in the same garment coordinates.
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not ob.name.startswith('CQ_'):
        continue
    groups={side:ob.vertex_groups.new(name='bib_'+side) for side in ['l','r']}
    colors=ob.data.color_attributes.get('GarmentWear')
    for v in ob.data.vertices:
        x,y,z=v.co
        if colors:
            color=colors.data[v.index].color
            wear=max(0.,min(1.,(color[0]-.26)/.24))
            fade=.5+.5*math.sin(27*x+9*z)*math.cos(13*z-7*x)
            colors.data[v.index].color=(.105+.083*wear+.012*fade,.147+.096*wear+.013*fade,.13+.061*wear+.010*fade,1.)
        if y>-.035 or not .49<z<1.245:
            continue
        skirt=max(0.,min(1.,(.942-z)/.39))
        wave=x+.033*math.sin(7*z)+.08*(z-.88)
        ridge=math.exp(-((wave+.073)/.026)**2)+.72*math.exp(-((wave-.105)/.032)**2)
        v.co.y-=skirt*(.001+.027*ridge)
        v.co.z+=skirt*skirt*(.009*math.sin(16*x+.5)-.012*x/.22)
        bib=max(0.,min(1.,(z-.935)/.26))
        tension=max(0.,math.sin(math.pi*bib))
        v.co.y-=tension*(.004+.008*math.cos(24*z+17*x))**2/.012
        if tension and abs(x)<.225:
            side='l' if x>0 else 'r'
            amount=.73*tension**1.3*(.40+.60*min(1.,abs(x)/.08))
            for old in list(v.groups):
                ob.vertex_groups[old.group].add([v.index],old.weight*(1-amount),'REPLACE')
            groups[side].add([v.index],amount,'REPLACE')
    ob.data.update()
for key,color in [('CQ_Cotton_BoundSeams',(.082,.112,.093,1)),('CQ_Cotton_Lockstitch',(.28,.24,.17,1))]:
    bpy.data.materials[key].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=color
from shopkeeper_hair_finish import finish
finish(bpy.data.objects['Human.short04'],OUT)
animate(rig,OUT,counter_service=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'shopkeeper_authoring.blend'),compress=True)
asset=GAME/'shopkeeper_r21.glb'
objects,low,high,scale=export_character(bpy.data.objects['ShopkeeperBody'],asset)
manifest=json.loads((ROOT/'characters/shopkeeper_r18/PROVENANCE.json').read_text(encoding='utf8'))
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
manifest.update(revision='R21 counter service',source_blend_sha256=sha(SOURCE),
                editable_blend_sha256=sha(OUT/'shopkeeper_authoring.blend'),runtime_glb_sha256=sha(asset),
                export_scale=scale,evaluated_height_before_normalization=high-low,evaluated_floor_before_normalization=low,
                modifications_r21='Original two-hand carry and weight shift. Washed green fabric, asymmetric bias folds, two skinned bib controls and three hem controls. Short04 CC0 texture repainted with temple grey and soft coverage; original UVs retained. R18 idle, greet and skin retained.')
for path in [OUT/'PROVENANCE.json',GAME/'shopkeeper_r21_provenance.json']:
    path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
print('R21_EXPORTED',asset,scale,flush=True)
