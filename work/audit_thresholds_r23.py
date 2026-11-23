"""Audit actual substrate outside every documented primary entrance, plus the rear half of the ten extended rooms."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parent;S=W/'scene_r23'
arch=json.loads((W/'project/chongqing_blender_v05/architecture_manifest.json').read_text(encoding='utf8'))
edit=json.loads((S/'assets/geometry_report.json').read_text());rooms={r['id']:r for r in edit['rooms']}
trees=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not o.name.startswith(('COL_Terrain','COL_Walk_','COL_Road_','COL_Community_court_pavement','COL_R23_NanquSidewalk')):continue
    vs=[o.matrix_world@v.co for v in o.data.vertices];bounds=[(min(v[k] for v in vs),max(v[k] for v in vs)) for k in (0,1)]
    trees.append((bounds,BVHTree.FromPolygons(vs,[tuple(f.vertices) for f in o.data.polygons]),o.name))
def ground(p,terrain=False):
    rows=[]
    for bounds,bvh,name in trees:
        if terrain and not name.startswith('COL_Terrain'):continue
        if all(l-.001<=p[i]<=h+.001 for i,(l,h) in enumerate(bounds)):
            q,n,_,_=bvh.ray_cast((p.x,p.y,80),(0,0,-1),120)
            if q is not None and abs(n.z)>.6:rows.append(q.z)
    return max(rows) if rows else None
primary=[];room_soil=[]
for b in arch['buildings']:
    for e in b['entrances']:
        p=Vector(e['position']);out=(Vector(e['approach']).xy-p.xy).normalized();u=Vector((-out.y,out.x))
        points=[p.xy+out*depth+u*(side*e['width_m']*.42) for side in (-1,0,1) for depth in (.12,.5)]
        z=[q for q in (ground(v) for v in points) if q is not None]
        primary.append(dict(building=b['id'],baseline=p.z,coverage=len(z),highest_relative=max(z)-p.z if z else None))
    for rp in b['interior_room_plans']:
        if rp['room_id'] not in rooms:continue
        row=rooms[rp['room_id']];poly=[Vector(p) for p in rp['polygon_xy']]
        a=Vector(b['facade_openings'][0]['a']);u=(Vector(b['facade_openings'][0]['b'])-a).normalized();n=Vector((-u.y,u.x))
        ts=[(q-a).dot(u) for q in poly];ws=[min(ts)+.10,(min(ts)+max(ts))/2,max(ts)-.1]
        z=[q for q in (ground(a+u*t+n*d,True) for t in ws for d in [row['old_depth']+.10,(row['new_depth']+row['old_depth'])/2,row['new_depth']-.11]) if q is not None]
        room_soil.append(dict(room=rp['room_id'],coverage=len(z),highest_soil_above_floor=max(z)-rp['floor_top_z'] if z else None))
(S/'threshold_audit.json').write_text(json.dumps(dict(primary=primary,extended_rooms=room_soil),indent=2),encoding='utf8')

