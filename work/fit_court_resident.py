"""Fit actual deformed garment/shoe surfaces to the sloping tree court and its bench."""
from pathlib import Path
import bpy, json, math, sys
from mathutils import Vector, Matrix
W=Path(__file__).resolve().parent
P=W/'project/chongqing_godot_v05'
A=P/'assets/characters/court_resident'
base=W/'characters/court_resident'
calibration_file=base/'terrain_fit_input.json'
calibration=json.loads(calibration_file.read_text()) if calibration_file.is_file() else None
if '--trial-output' in sys.argv:
    base=W/'characters/court_resident_trial11';A=base/'runtime'
bpy.ops.wm.open_mainfile(filepath=str(base/'court_resident.blend'))
bpy.context.scene.frame_set(1)
o=bpy.data.objects['CourtResident']
eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
points={key:[] for key in ['seat','left','right']}
for v in eo.data.vertices:
    p=eo.matrix_world@v.co
    group=o.vertex_groups[max(v.groups,key=lambda g:g.weight).group].name if v.groups else ''
    if abs(p.x)<.15 and -.12<p.y<.20 and .25<p.z<.66 and ('Pelvis' in group or 'Thigh' in group):points['seat'].append(p)
    for code,key in [(' L ','left'),(' R ','right')]:
        if code in group and p.z<.12:points[key].append(p)
contacts={key:min(values,key=lambda p:p.z).copy() for key,values in points.items()}
print('CONTACTS',contacts)
seats=json.loads((P/'assets/lane_r20/tree_seats.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(W/'scene_r20/chongqing_district.blend'))
prior=bpy.data.collections.get('R20_Court_resident')
if prior:
    for ob in list(prior.objects):bpy.data.objects.remove(ob,do_unlink=True)
scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def floor(p):
    hit,q,_,_,ob,_=scene.ray_cast(dg,Vector((p.x,p.y,30.95)),Vector((0,0,-1)),distance=3.)
    assert hit,(p.x,p.y)
    return q.z,ob.name
fits=[]
for arc,(start,end) in enumerate([(217,321),(55,127)]):
    for theta in range(start,end):
        angle=math.radians(theta)
        x=-26.36+1.56*math.cos(angle);y=70.02+1.56*math.sin(angle)
        loc=Vector((x,y,seats['places'][arc]['seat'][1]-contacts['seat'].z-.005))
        if min(math.hypot(x-p['seat'][0],y+p['seat'][2]) for p in seats['places'])<.89:continue
        for twist in range(-12,13,3):
            yaw=angle+math.pi/2+math.radians(twist)
            rot=Matrix.Rotation(yaw,3,'Z')
            samples={k:loc+rot@v for k,v in contacts.items()}
            hits={k:floor(v) for k,v in samples.items()}
            if 'Tree_seat' not in hits['seat'][1]:continue
            err={k:samples[k].z-hits[k][0] for k in samples}
            merit=max(abs(err['left']),abs(err['right']))+.00008*abs(theta-307)+.00005*abs(twist)
            fits.append((merit,arc,theta,twist,loc.copy(),yaw,samples,hits,err))
assert fits
score,arc,theta,twist,origin,yaw,samples,hits,gaps=min(fits,key=lambda r:r[0])
if calibration:
    x,z,my=calibration['locked_position'];origin=Vector((x,-my,z))
    yaw=calibration['locked_yaw'];arc=calibration['arc'];theta=calibration['theta']
    rot=Matrix.Rotation(yaw,3,'Z');samples={};hits={};gaps={}
    for key,vertices in points.items():
        candidates=[]
        for v in vertices:
            at=origin+rot@v
            surface=floor(at)
            prefix='R20_Court_paving' if key!='seat' else 'R20_Tree_seat'
            if surface[1].startswith(prefix):
                candidates.append((at.z-surface[0],at,v,surface))
        error,point,local,surface=min(candidates,key=lambda t:t[0])
        contacts[key]=local;samples[key]=point;hits[key]=surface;gaps[key]=error
    score=max(abs(e) for e in gaps.values())
def gd(p):return [p.x,p.z,-p.y]
result={'arc':arc,'theta':theta,'yaw':yaw,'position':gd(origin),'blender_local_skin_contacts':{k:list(v) for k,v in contacts.items()},
    'skin_samples':{k:gd(v) for k,v in samples.items()},'surface_hits':hits,'gaps_m':gaps,'score':score}
(A/'bench_fit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('R21_FIT',result)
