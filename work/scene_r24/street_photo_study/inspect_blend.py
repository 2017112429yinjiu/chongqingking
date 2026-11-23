from pathlib import Path
import bpy,json
from mathutils import Vector
root=Path(__file__).resolve().parent
scene=bpy.context.scene
objects=[o for o in scene.objects if '809889623' in o.name and o.type=='MESH' and any(m and 'potted_plant_02' in m.name for m in o.data.materials)]
data={'source':bpy.data.filepath,'revision':scene.get('street_revision'),'workday':[o.name for o in scene.objects if o.name.startswith('Workday12')],'pots':[o.name for o in objects],'packed_price_card':any(im.packed_file and 'greengrocer_card' in im.name for im in bpy.data.images)}
(root/'editable_reopen.json').write_text(json.dumps(data,indent=2),'utf-8')
print('CHECK_BLENDER',data)

