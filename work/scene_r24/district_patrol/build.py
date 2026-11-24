"""Build the connected stair hall and street corrections from the preserved build 24."""
from pathlib import Path
import ast,json,math,sys,collections
import bpy,bmesh
from mathutils import Vector,Matrix
here=Path(__file__).resolve().parent
game=here.parents[1]/'project/chongqing_godot_v05'
out=game/'assets/district_patrol';out.mkdir(exist_ok=True)
sys.path[:0]=[str(here.parent/'district_age'),str(here.parent/'stair_neighborhood')]
from survey import scene,extent,road,Surfaces
def use(file,names):
    src=here.parent/file
    defs=ast.parse(src.read_text('utf8'))
    exec(compile(ast.Module([node for node in defs.body if isinstance(node,ast.FunctionDef) and node.name in names],[]),str(src),'exec'),globals())
use('district_connections/author.py',('box','publish','face','mark','finish','solid_clip'))
use('indoor_delivery/author.py',('prism','floor','slab','beam','inclined'))
use('vertical_run/author.py',('rake',))
layout=json.loads((game/'assets/vertical_run/layout.json').read_text('utf8'))
collection=bpy.data.collections.new('Resident stair and district patrol corrections');scene.collection.children.link(collection)
mat={k:bpy.data.materials['R18_unit22_'+k] for k in ['terrazzo','tread','plaster','dado','metal','edge','lamp','brass']}
batches={};metric_uv={};measure={}
def retire(name):
    ob=scene.objects.get(name)
    if not ob:return
    ob.hide_render=True;ob.hide_set(True)
    if name not in layout['retired']:layout['retired'].append(name)
    for key in ('changed','new'):
        if name in layout[key]:layout[key].remove(name)
def changed(ob):
    if ob.name not in layout['new']:mark(ob)
# A resident can walk east out of the 202 hall and climb one storey to 301.
A=19.89;L=22.90; xa=-60.98;xb=-56.22
z0=16.84;z1=18.20
shaft=[prism(-61.34,-54.69,16.80,18.27,A-.22,L+2.48),
       prism(-60.92,-54.69,15.345,16.84,L-.19,L+2.48)]
for ob in list(scene.objects):
    if ob.type!='MESH' or ob.hide_render or not ob.data.polygons:continue
    if not ('A04' in ob.name or ob.name.startswith(('Room15_','COLH_')) or ob.name in ['COL_D18_RoomShells','D18_BackRoomFurnishings']):continue
    low,high=extent(ob)
    if high[0]<-61.34 or low[0]>-54.69 or high[1]<-18.27 or low[1]>-15.345 or high[2]<A-.22 or low[2]>L+2.48:continue
    solid_clip(ob,shaft)
for name in ('COL_Unit22_Stairhall','Unit22_Fittings'):
    solid_clip(scene.objects[name],[prism(-61.48,-60.98,16.84,18.16,A+.002,A+2.58)])
for name in ('COL_Blue24_301','Blue24_Fixtures'):
    solid_clip(scene.objects[name],[prism(-60.81,-59.48,15.29,15.61,L+.006,L+2.28)])
S='COL_Patrol25_ResidentStair';D='Patrol25_HallHardware'
floor(S,-61.26,xa,z0,z1,A)
for i in range(17):
    left=xa+i*.28;h=A+(i+1)*(L-A)/17
    floor('Patrol25_ResidentTreads',left,left+.28,z0,z1,h,'tread',.28)
# A continuous collision slope follows the mid-height of the treads; the solid
# visible risers still have their full depth. Both the resident and rider use this shape.
inclined(xa,xb,z0,z1,A,L,-.30,.075,'COLH_Patrol25_StairSlope','edge')
floor(S,xb,-54.74,15.40,z1,L)
floor(S,-60.87,xb,15.40,z0,L)
for z in [z0-.034,z1+.034]:
    inclined(xa,xb,z-.03,z+.03,A,L,-.30,2.46,S,'plaster')
    inclined(xa,xb,z-.034,z+.034,A,L,-.06,.98,D,'dado')
inclined(xa,xb,z0-.05,z1+.05,A,L,2.36,2.48,S,'plaster')
for z,lo,hi in [(18.23,xb,-54.71),(15.37,-59.46,-54.71)]:
    slab(S,lo,hi,z-.035,z+.035,L-.17,L+2.45,'plaster')
slab(S,-54.78,-54.69,15.37,18.26,L-.17,L+2.46,'plaster')
slab(S,-60.92,-60.86,15.36,16.85,L-.17,L+2.45,'plaster')
slab(S,-60.88,xb,15.40,z0,L+2.36,L+2.46,'plaster')
slab(S,xb,-54.71,15.39,z1,L+2.36,L+2.46,'plaster')
# Continuous spandrel between the lower stair and upper return corridor.
slab(S,-60.87,xb,16.797,16.845,L-.17,L+2.42,'plaster')
for x,z,y in [(-58.48,17.50,(A+L)*.5),(-55.46,16.02,L)]:
    slab(D,x-.26,x+.26,z-.08,z+.08,y+2.29,y+2.36,'metal')
    slab(D,x-.22,x+.22,z-.062,z+.062,y+2.27,y+2.29,'lamp')
# Replace the free-ended false ceiling and the two thin free-standing diagonal panels.
blue=scene.objects['COL_Blue24_Stair'];trim=scene.objects['Blue24_Fixtures']
def remove_faces(ob,pred):
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
    dead=[f for f in bm.faces if pred([v.co for v in f.verts],f)]
    if dead:bmesh.ops.delete(bm,geom=dead,context='FACES');finish(ob,bm)
    else:bm.free()
    return len(dead)
def false_ceiling(pts,f):
    xs=[p.x for p in pts];zs=[-p.y for p in pts]
    if min(xs)<-86.065 or max(xs)>-83.78:return False
    return all(abs(p.z-(17.12+min(5.8,max(0.,-p.y-10.4))*3.4/5.8+3.02))<.083 for p in pts)
measure['ceiling_faces']=remove_faces(blue,false_ceiling)
def central(pts,f):
    return all(-83.84<=p.x<=-83.64 and 10.39<=-p.y<=16.21 for p in pts)
measure['old_divider_faces']=remove_faces(blue,central)
def fixtures(pts,f):
    return all(-85.39<=p.x<=-84.32 and 11.80<=-p.y<=15.06 and 2.79<p.z-(17.12+(-p.y-10.4)*3.40/5.80)<3.15 for p in pts)
remove_faces(trim,fixtures)
# A proper central spine encloses the unused slab well. Its top follows the upper flight.
rake(S,-83.805,-83.67,10.40,16.20,23.86,20.55,-6.9,.93,'plaster')
rake(D,-83.82,-83.655,10.40,16.20,23.86,20.55,.93,.98,'terrazzo')
slab(S,-83.80,-83.69,9.04,10.40,16.96,24.81,'plaster')
slab(S,-81.50,-81.40,9.04,10.42,16.95,23.92,'plaster')
# Recessed handrail mounted to the exterior wall, with short brackets into the plaster.
for wall,offset,h1,h2 in [(-86.015,.10,17.12,20.52),(-81.48,-.10,23.92,20.52)]:
    beam(D,(wall+offset,h1+.95,10.4),(wall+offset,h2+.95,16.2),.041,'metal')
    for j in [0,1,2,3]:
        t=.04+j*.30;z=10.4+t*5.8;h=h1+(h2-h1)*t+.95
        beam(D,(wall,h-.07,z),(wall+offset,h,z),.026,'metal')
for z in [11.92,14.94]:
    h=17.12+(z-10.4)*3.40/5.8
    slab(D,-86.025,-85.98,z-.17,z+.17,h+1.89,h+2.12,'metal')
    slab(D,-85.98,-85.95,z-.14,z+.14,h+1.92,h+2.09,'lamp')
rake(D,-86.02,-85.996,11.92,14.94,17.12+(11.92-10.4)*3.4/5.8,17.12+(14.94-10.4)*3.4/5.8,2.03,2.05,'metal')
for k in list(layout['new']):
    if k in layout['changed']:layout['changed'].remove(k)
# Paint the complete court onto the existing structural slab at 20.530 m.
for k in ['COL_Community_court_line_white','COL_Community_court_court_red','COL_Community_court_court_green','Street_small_furniture_dark','Street_small_furniture_aluminium']:retire(k)
# Baked patch panels represented paving finishes above the underlying one-metre terrain.
for ob in list(scene.objects):
    if ob.name.startswith('Urban_paving_joints_and_repairs_'):retire(ob.name)
exec(compile((here/'streets.py').read_text('utf8'),str(here/'streets.py'),'exec'))
publish()
for key in list(layout['changed']):
    if key in layout['new']:layout['changed'].remove(key)
    elif not scene.objects[key].data.polygons:retire(key)
(out/'layout.json').write_text(json.dumps(layout,indent=2),'utf8')
(here/'measurements.json').write_text(json.dumps(measure,indent=2),'utf8')
bpy.ops.object.select_all(action='DESELECT')
for key in layout['changed']+layout['new']:scene.objects[key].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'district.glb'),use_selection=True,export_animations=False,export_image_format='NONE')
scene['street_revision']='R24 build 25 - home stair and district patrol'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_patrol.blend'),compress=True,relative_remap=True)
print('PATROL_BUILD',len(layout['changed']),len(layout['new']),flush=True)
