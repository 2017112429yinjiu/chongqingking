"""Reopen the saved authoring file and measure independent top hits on every tread."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=Path(__file__).resolve().parent/'scene_r24'
g=json.loads((s/'geometry.json').read_text())
stairs=g['stairs']; x,yl,yh=stairs['location']
active=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name in stairs['cut_sources'] or o.name.startswith('COL_R24_MarketStairs'))]
trees=[]
for o in active:
    verts=[o.matrix_world@v.co for v in o.data.vertices]
    trees.append((o.name,BVHTree.FromPolygons(verts,[tuple(q.vertices) for q in o.data.polygons])))
checks=[]
for row in range(stairs['treads']):
    y=yl+(row+.5)*(yh-yl-.32)/stairs['treads'];expected=stairs['lower']+(row+1)*stairs['rise']
    for dx in [-1.05,0,1.05]:
        hits=[]
        for name,tree in trees:
            hit,normal,_,_=tree.ray_cast((x+dx,y,16),(0,0,-1),15)
            if hit is not None and normal.z>.55:hits.append((hit.z,name))
        top,name=max(hits)
        checks.append(dict(step=row+1,x=x+dx,y=y,error_m=abs(top-expected),surface=name))
images=[im.name for im in bpy.data.images if im.packed_file and ('east_windows' in im.name or im.name.startswith('shop_paint'))]
assert len(images)==4 and len(checks)==18 and all(r['error_m']<.003 and r['surface'].startswith('COL_R24_MarketStairs') for r in checks)
print('R24_SOURCE_OPEN_OK',len(active),max(q['error_m'] for q in checks),images)
(s/'source_reopened.json').write_text(json.dumps(dict(file=Path(bpy.data.filepath).name,version=bpy.app.version_string,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),tread_hits=checks,packed_art=images,distant_buildings=len(g['east']['installed'])),indent=1))

