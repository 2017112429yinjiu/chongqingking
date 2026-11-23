from pathlib import Path
import bpy,sys,json
ROOT=Path(__file__).resolve().parent
bpy.context.preferences.use_preferences_save=False
bpy.context.preferences.extensions.repos.new(name='CQ isolated tools',module='cq_tools',custom_directory=str(ROOT/'assets_incoming/mpfb/mpfb2-master/src'))
bpy.ops.preferences.addon_enable(module='bl_ext.cq_tools.mpfb')
from bl_ext.cq_tools.mpfb.services.humanservice import HumanService
from bl_ext.cq_tools.mpfb.services.locationservice import LocationService
from bl_ext.cq_tools.mpfb.services.targetservice import TargetService
from bl_ext.cq_tools.mpfb.entities.objectproperties import HumanObjectProperties
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
human=HumanService.create_human()
for key,value in {'gender':1.,'age':.58,'muscle':.45,'weight':.55,'height':.45,'asian':1.,'caucasian':0.,'african':0.}.items():
    HumanObjectProperties.set_value(key,value,entity_reference=human)
TargetService.reapply_macro_details(human)
HumanService.add_builtin_rig(human,'game_engine')
print('CQ_CHARACTER_PROBE',json.dumps({'name':human.name,'dimensions':list(human.dimensions),'user_data':LocationService.get_user_data(),
 'objects':[{ 'name':o.name,'type':o.type,'bones':list(o.data.bones.keys()) if o.type=='ARMATURE' else []} for o in bpy.context.scene.objects]}),flush=True)
