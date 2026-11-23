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
flyover=g['flyover']
def from_mesh(ob):
    return BVHTree.FromPolygons([ob.matrix_world@vert.co for vert in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons])
bridge_top=[from_mesh(o) for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith('COL_R24_LinkDeck') or o.name in ['COL_Road_59146775_0_asphalt','COL_Road_59146775_1_asphalt'])]
bottom=from_mesh(next(o for o in bpy.context.scene.objects if o.name.startswith('R24_FlyoverBox_')))
section_checks=[]
for i in range(49):
    x=-23+i
    upper=[v for tree in bridge_top if (v:=tree.ray_cast((x,-100,23),(0,0,-1),22))[0] is not None]
    under=bottom.ray_cast((x,-100,5),(0,0,1),12)
    assert upper and under[0] is not None,(x,upper,under)
    roof=max(upper,key=lambda item:item[0].z);thickness=roof[0].z-under[0].z
    assert roof[1].z>.95 and under[1].z<-.95 and .87<thickness<.95,(x,roof[1],under[1],thickness)
    section_checks.append([x,roof[0].z,under[0].z,thickness])
images=[im.name for im in bpy.data.images if im.packed_file and ('east_windows' in im.name or im.name.startswith(('shop_paint','road_names')))]
assert len(images)==5 and len(checks)==18 and all(r['error_m']<.003 and r['surface'].startswith('COL_R24_MarketStairs') for r in checks)
# Measure the actual saved ramp and all three parked groups after reopening.
ramp=bpy.context.scene.objects['COL_Road_59146775_1_asphalt']
pts=[ramp.matrix_world@v.co for v in ramp.data.vertices]
meters=[(a+b)*.5 for a,b in zip(pts[::2],pts[1::2])]
grade=max(abs(a.z-b.z)/(a.xy-b.xy).length for a,b in zip(meters,meters[1:]))
assert grade<.105 and g['ramp_grade']['original_max_grade']>.50
assert len(g['parked'])==3 and len(g['road_joins'])==2 and g['corner']['soil_faces_removed']>0
assert len(g['corner']['bearing_faces'])>=180
print('R24_SOURCE_OPEN_OK',len(active),max(q['error_m'] for q in checks),images)
(s/'source_reopened.json').write_text(json.dumps(dict(file=Path(bpy.data.filepath).name,version=bpy.app.version_string,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),tread_hits=checks,packed_art=images,distant_buildings=len(g['east']['installed']),bridge_cross_sections=section_checks,east_ramp_max_grade=grade,parked_groups=list(g["parked"]),verge_rows=len(g["corner"]["bearing_faces"])),indent=1))

