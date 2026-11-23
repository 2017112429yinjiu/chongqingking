import bpy, json, sys
from pathlib import Path
from mathutils import Vector

dst=Path(sys.argv[sys.argv.index('--')+1])
scene=bpy.context.scene
rows=[]
for obj in scene.objects:
    if obj.type!='MESH': continue
    if any(s in obj.name.lower() for s in ['scooter','clothesline','walk_','handrail','door','stair','meter']):
        corners=[obj.matrix_world @ Vector(p) for p in obj.bound_box]
        rows.append({'name':obj.name,'location':list(obj.location),'rotation':list(obj.rotation_euler),'min':[min(v[i] for v in corners) for i in range(3)],'max':[max(v[i] for v in corners) for i in range(3)],'vertices':len(obj.data.vertices),'prop_type':obj.get('prop_type'),'materials':[s.name if s else None for s in obj.data.materials]})
report={'blender_version':bpy.app.version_string,'scene_revision':scene.get('revision'),'object_count':len(scene.objects),'mesh_count':sum(o.type=='MESH' for o in scene.objects),'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'unpacked_images':[{'name':i.name,'path':i.filepath} for i in bpy.data.images if i.source=='FILE' and not i.packed_file],'objects':rows}
dst.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CQ_BLEND_INSPECT', json.dumps({k:v for k,v in report.items() if k not in ['objects','unpacked_images']}),flush=True)
