import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent;out=root/'characters/rider_r18_trial'
bpy.ops.wm.open_mainfile(filepath=str(out/'rider_authoring.blend'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');body=bpy.data.objects['m024_hipoly_81_bones_opacity']
groups={g.index:g.name for g in body.vertex_groups}
parts={side:[v.index for v in body.data.vertices if sum(g.weight for g in v.groups if groups[g.group] in ['Bip01 '+side+' Foot','Bip01 '+side+' Toe0'])>.65] for side in ['L','R']}
report=[]
poses=[('ride_steer',1),('ride_steer',31),('ride_steer',61),('ride_idle',1),('ride_idle',31)]+[('ride_support',f) for f in range(1,32)]
for clip,frame in poses:
    rig.animation_data.action=bpy.data.actions[clip];bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
    eval_ob=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=eval_ob.to_mesh()
    points=[eval_ob.matrix_world@v.co for v in mesh.vertices]
    feet={side:{'count':len(ids),'min_z':min(points[i].z for i in ids),'min_x':min(points[i].x for i in ids),'max_x':max(points[i].x for i in ids)} for side,ids in parts.items()}
    # Test the source shoe surface, not just the ankle bone, against the known
    # deck slab. Full body/fender collision still needs additional inspection.
    deck_inside=[i for i in parts['L'] if abs(points[i].x)<.17 and -.11<points[i].y<.41 and .334<points[i].z<.358]
    report.append({'clip':clip,'frame':frame,'feet':feet,'left_shoe_vertices_inside_deck_over_4mm':len(deck_inside)});eval_ob.to_mesh_clear()
result={'source_sha256':hashlib.file_digest((out/'rider_authoring.blend').open('rb'),'sha256').hexdigest(),'scope':'weighted shoe vertices, flat source plane and deck slab; not full body self-collision','poses':report,'passed':all(r['left_shoe_vertices_inside_deck_over_4mm']==0 for r in report)}
(out/'contact_audit.json').write_text(json.dumps(result,indent=2))
print('RIDER_SHOE_AUDIT',result['passed'],len(report),'poses',flush=True)
assert result['passed']
