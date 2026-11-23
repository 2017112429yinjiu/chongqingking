"""Fit each travel lane to its own road deck, independently of bridges and terrain above it."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=Path(__file__).resolve().parent/'scene_r24'
src=json.loads((s/'playtest/assets/block_r23/routes.json').read_text(encoding='utf8'))
ways={'west':[1189963547,49182408],'east':[1189963598,830761786]}
spec={};stats={}
for key,ids in ways.items():
    obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.endswith('_asphalt') and any(o.name.startswith('COL_Road_%d_'%i) for i in ids)]
    assert obs,key
    trees=[(o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])) for o in obs]
    rows=src[key];pts=[];report=[];normals=[]
    for x,old,z in rows:
        hits=[]
        for name,tree in trees:
            p,n,_,_=tree.ray_cast((x,-z,60),(0,0,-1),110)
            if p is not None and n.z>.85:hits.append((p.z,name,n))
        if not hits:raise RuntimeError(('Missing carriageway',key,x,z))
        h,name,n=max(hits,key=lambda q:q[0]);pts.append([x,round(h+.006,5),z]);normals.append([round(n.x,6),round(n.z,6),round(-n.y,6)])
        report.append(old-h)
    spec[key]={'points':pts,'normals':normals,'ways':ids}
    stats[key]={'points':len(pts),'largest_old_offset_m':max(report),'above_20cm':sum(d>.20 for d in report),'max_grade':max(abs(q[1]-p[1])/max(.001,math.hypot(q[0]-p[0],q[2]-p[2])) for p,q in zip(pts,pts[1:]))}
(s/'assets/traffic_lanes.json').write_text(json.dumps(spec,separators=(',',':')))
(s/'traffic_fit.json').write_text(json.dumps(stats,indent=1));print('R24_LANES',stats)

