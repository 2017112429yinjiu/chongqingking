"""Measure seated clothing and shoe contacts against the visible court on both actions."""
from pathlib import Path
import bpy, math, json, hashlib, sys
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parent
P=W/'project/chongqing_godot_v05'
A=P/'assets/characters/court_resident'
base=W/'characters/court_resident'
evidence=P/'verification_r20/current/resident_motion'
if '--trial-output' in sys.argv:
    base=W/'characters/court_resident_trial11';A=base/'runtime';evidence=base
fit=json.loads((A/'bench_fit.json').read_text())
x,z,minus_y=fit['position'];origin=Vector((x,-minus_y,z));rotation=Matrix.Rotation(fit['yaw'],3,'Z')
def measure_group(point,group):
    if group.endswith(('Pelvis','Thigh')) and abs(point.x)<.15 and -.12<point.y<.20 and .25<point.z<.66:return 'seat'
    if point.z<.12:
        if ' L ' in group:return 'left'
        if ' R ' in group:return 'right'
samples=[]
bpy.ops.wm.open_mainfile(filepath=str(base/'court_resident.blend'))
scene=bpy.context.scene;obj=bpy.data.objects['CourtResident'];rig=bpy.data.objects['CourtResidentRig']
labels=[obj.vertex_groups[max(v.groups,key=lambda g:g.weight).group].name if v.groups else '' for v in obj.data.vertices]
for clip in ['sit_rest','sit_look']:
    action=bpy.data.actions[clip];rig.animation_data.action=action
    first,last=map(round,action.frame_range)
    for frame in sorted(set(round(first+(last-first)*i/64) for i in range(65))):
        scene.frame_set(frame);eo=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        groups={'left':[],'right':[],'seat':[]}
        for vertex in eo.data.vertices:
            local=eo.matrix_world@vertex.co
            group=measure_group(local,labels[vertex.index])
            if group:groups[group].append(origin+rotation@local)
        samples.append((clip,frame,groups))
bpy.ops.wm.open_mainfile(filepath=str(W/'scene_r20/chongqing_district.blend'))
def tree(prefix):
    obj=next(obj for obj in bpy.context.scene.objects if obj.name.startswith(prefix))
    obj=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[list(p.vertices) for p in obj.data.polygons])
surfaces={'seat':tree('R20_Tree_seat_wood'),'paving':tree('R20_Court_paving_step_concrete')}
rows=[]
for clip,frame,groups in samples:
    row={'clip':clip,'frame':frame,'gaps_m':{},'surface_samples':{}}
    for name,points in groups.items():
        surface=surfaces['seat' if name=='seat' else 'paving'];gaps=[]
        for p in points:
            hit,_,_,_=surface.ray_cast(Vector((p.x,p.y,31.5)),Vector((0,0,-1)),3.)
            if hit is not None:gaps.append(p.z-hit.z)
        assert gaps,(clip,frame,name)
        row['gaps_m'][name]=min(gaps);row['surface_samples'][name]=len(gaps)
    rows.append(row)
ranges={key:[min(row['gaps_m'][key] for row in rows),max(row['gaps_m'][key] for row in rows)] for key in ['seat','left','right']}
report={'source_mesh':'Skinned garment and shoes, 65 frames per clip, including 48 between the fitting samples. Signed minimum surface separation against the visible curved seat/paving per foot and seated pelvis. Negative values denote penetration.',
 'model_sha256':hashlib.file_digest((A/'court_resident.glb').open('rb'),'sha256').hexdigest(),'ranges_m':ranges,'samples':rows}
evidence.mkdir(exist_ok=True)
(evidence/'contact_sweep.json').write_text(json.dumps(report,indent=2))
print('R20_CONTACT_SWEEP',ranges)
