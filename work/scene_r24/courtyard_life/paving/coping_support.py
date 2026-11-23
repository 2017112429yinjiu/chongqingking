"""Measure the underside of coping stones against the dark masonry of the original courtyard wall."""
from pathlib import Path
import json,bpy,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
scene=bpy.context.scene
ob=scene.objects['COL_Resident_court_boundary_0_concrete'];wall=scene.objects['COL_Resident_court_boundary_0_brick_dark']
tree=BVHTree.FromPolygons([wall.matrix_world@v.co for v in wall.data.vertices],[list(p.vertices) for p in wall.data.polygons],all_triangles=False)
rows=[]
for poly in ob.data.polygons:
 pts=[ob.matrix_world@ob.data.vertices[i].co for i in poly.vertices]
 a,b,c=pts[:3];normal=(b-a).cross(c-a).normalized()
 if normal.z>-.98:continue
 center=sum(pts,Vector())/len(pts)
 values=[]
 for pt in [center,*(center*.72+p*.28 for p in pts)]:
  hit=tree.ray_cast(pt+Vector((0,0,.04)),(0,0,-1),.8)[0]
  values.append(None if hit is None else pt.z-hit.z)
 rows.append({'center':list(center),'corners':[list(p) for p in pts],'gap':values})
(here/'coping_support.json').write_text(json.dumps(rows),'utf8')
largest=max((max(abs(g) for g in item['gap'] if g is not None) for item in rows if any(g is not None for g in item['gap'])),default=0)
print('COURT14_COPING',len(rows),largest,sum(None in item['gap'] for item in rows))
