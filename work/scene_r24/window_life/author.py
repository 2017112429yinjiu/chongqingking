"""Build two occupied upper windows and a street-side pantry inside the measured rooms."""
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bpy,json,math
from collections import defaultdict
here=Path(__file__).resolve().parent
assets=here.parents[1]/'project/chongqing_godot_v05/assets/rooms_r24'
assets.mkdir(exist_ok=True)
source=here.parent/'street_photo_study/workday_surfaces/timber.jpg'
collection=bpy.data.collections.new('R24_15_WindowRooms');bpy.context.scene.collection.children.link(collection)
verts=defaultdict(list);faces=defaultdict(list);slots=defaultdict(list);materials={}
def material(key,rgb,rough=.72,metal=0.,wood=False):
    m=bpy.data.materials.new('Window15_'+key);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1.);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    if wood:
        im=m.node_tree.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(source),check_existing=True);im.image.pack();m.node_tree.links.new(im.outputs[0],bs.inputs['Base Color'])
    materials[key]=m
for key,rgb,rough,metal in [('ivory',(.68,.65,.50),.33,.12),('celadon',(.27,.42,.32),.27,.18),('bottle',(.101,.29,.25),.31,.19),('vintage_red',(.33,.067,.041),.42,.13),('steel',(.47,.46,.40),.34,.69),('darksteel',(.13,.145,.14),.47,.54),('clay',(.31,.178,.098),.73,0),('paper',(.65,.52,.33),.91,0),('blue',(.10,.22,.29),.40,.13),('bamboo',(.49,.331,.161),.79,0),('green',(.26,.34,.20),.88,0),('rice',(.51,.416,.29),.76,0),('tile',(.59,.62,.55),.39,.04),('grout',(.31,.32,.27),.85,0),('brown',(.16,.087,.052),.74,0),('cream',(.71,.685,.57),.61,0)]:
    material(key,rgb,rough,metal)
material('oldwood',(.36,.25,.14),wood=True)
site='main';label='';anchors=[];floors=[];checks=[];lights=[]
def world(v):
    l,d,h=v
    return Vector((l,d-73,h)) if site=='main' else Vector((d-66,-l,h))
def god(v):return [v.x,v.z,-v.y]
def face(ps,mat):
    points=[world(p) for p in ps]
    n=len(verts[label]);verts[label].extend([tuple(p) for p in points]);faces[label].append(tuple(range(n,n+len(ps))));slots[label].append(mat)
def box(c,size,m):
    x,y,z=c;a,b,h=[v*.5 for v in size]
    corners=[(x+i*a,y+j*b,z+k*h) for k in [-1,1] for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    for g in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face([corners[t] for t in g],m)
def rod(a,b,r,mat,n=10,r2=None):
    a,b=Vector(a),Vector(b);d=(b-a).normalized();u=d.orthogonal().normalized();v=d.cross(u);r2=r if r2 is None else r2
    loops=[[p+(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n))*rr for i in range(n)] for p,rr in [(a,r),(b,r2)]]
    for i in range(n):j=(i+1)%n;face([loops[0][i],loops[0][j],loops[1][j],loops[1][i]],mat)
    face(loops[0][::-1],mat);face(loops[1],mat)
def line(points,r,m,n=8):
    for a,b in zip(points,points[1:]):
        if (Vector(a)-Vector(b)).length>.000001:rod(a,b,r,m,n)
def vessel(x,y,z,profile,m,n=40):
    prev=None
    for r,h in profile:
        ring=[(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z+h) for i in range(n)]
        if prev is None:face(ring[::-1],m)
        else:
            for i in range(n):j=(i+1)%n;face([prev[i],prev[j],ring[j],ring[i]],m)
        prev=ring
    face(prev,m)
def torus(x,y,z,r,thick,m):
    pts=[(x+r*math.cos(i*math.tau/40),y+r*math.sin(i*math.tau/40),z) for i in range(41)]
    line(pts,thick,m,6)
def handle(x,y,z,rad,rise,m):
    line([(x-rad,y,z),(x-rad*1.07,y,z+rise*.73),(x-rad*.76,y,z+rise),(x+rad*.75,y,z+rise),(x+rad*1.07,y,z+rise*.72),(x+rad,y,z)],.009,m,10)
def kettle(x,y,z):
    vessel(x,y,z,[(.078,0),(.102,.018),(.112,.055),(.107,.119),(.078,.157),(.065,.16)],'ivory')
    torus(x,y,z+.147,.085,.004,'bottle');vessel(x,y,z+.157,[(.067,0),(.051,.014),(.012,.016)],'steel');vessel(x,y,z+.172,[(.019,0),(.015,.021)],'brown')
    # Tapered pouring spout, dark inner lip and an arched carrying handle.
    p=(x-.105,y-.008,z+.067);b=(x-.151,y-.012,z+.108);tip=(x-.187,y-.013,z+.145)
    rod(p,b,.030,'ivory',20,.019);rod(b,tip,.020,'ivory',20,.017);rod(tip,(tip[0]-.002,tip[1],tip[2]+.001),.013,'darksteel',16)
    handle(x,y,z+.114,.095,.146,'darksteel')
def thermos(x,y,z,m):
    vessel(x,y,z,[(.064,0),(.084,.013),(.086,.042),(.085,.291),(.077,.326),(.048,.348),(.045,.364)],m)
    vessel(x,y,z+.349,[(.049,0),(.051,.033),(.045,.040)],'cream')
    for r,h in [(.086,.037),(.086,.269),(.081,.314)]:torus(x,y,z+h,r,.004,'ivory')
    line([(x+.063,y,z+.293),(x+.115,y,z+.282),(x+.130,y,z+.256),(x+.126,y,z+.159),(x+.070,y,z+.127)],.011,'cream',10)
    for ang in [-2.25,-1.9,-1.6]:
        cx=x+math.cos(ang)*.0857;cy=y+math.sin(ang)*.0857
        line([(cx,cy,z+.097),(cx+.007,cy-.001,z+.129),(cx+.013,cy+.001,z+.148)],.0025,'green',5)
        for j in range(4):
            v=(cx+.011+.005*math.cos(j*math.pi/2),cy-.002,z+.148+.006*math.sin(j*math.pi/2))
            rod((cx+.011,cy,z+.148),v,.003,'cream',7)
def cup(x,y,z,m):
    vessel(x,y,z,[(.030,0),(.041,.004),(.041,.069),(.043,.071),(.039,.071),(.038,.011)],m,28)
    torus(x,y,z+.070,.041,.0026,'darksteel');line([(x+.039,y,z+.054),(x+.062,y,z+.050),(x+.064,y,z+.025),(x+.038,y,z+.019)],.0047,m)
def bowl(x,y,z,r,m,stack=1):
    for i in range(stack):
        h=z+i*.018
        vessel(x,y,h,[(r*.40,0),(r*.46,.007),(r*.77,r*.25),(r,r*.48),(r*.97,r*.49),(r*.88,r*.36),(r*.44,.012)],m)
        torus(x,y,h+r*.48,r,.002,'blue')
def jar(x,y,z,h,r,m):
    vessel(x,y,z,[(r*.86,0),(r,.014),(r,h*.68),(r*.85,h*.78),(r*.70,h*.83),(r*.74,h*.90)],m,32)
    vessel(x,y,z+h*.9,[(r*.79,0),(r*.81,.017),(r*.72,.022)],'clay',32)
def hanger(x,y,z,size,m):
    # A bowl skimmer with rope around the handle, and wire rings in a shallow basket.
    rod((x,y,z),(x,y-.009,z-size*.76),.006,'steel')
    rod((x,y,z-.015),(x,y,z-size*.44),.011,m)
    cy=y;cz=z-size;rx=size*.24
    for k in (1.,.79,.58,.36):
        pts=[(x-rx*(1-k)*.29,cy+rx*k*math.cos(i*math.tau/28),cz+rx*k*math.sin(i*math.tau/28)) for i in range(29)]
        line(pts,.0026,'steel',6)
    for i in range(10):
        a=i*math.tau/10;rod((x-rx*.27,cy,cz),(x,cy+rx*math.cos(a),cz+rx*math.sin(a)),.002,'steel',5)
def check(x,y,z,target):checks.append([label,god(world((x,y,z))),target])
def light(pos,aim,energy):
    lights.append(dict(site=site,at=god(world(pos)),aim=god(world(aim)),energy=energy))

# Two main-road windows have separate homes and different purposes.
site='main';label='Room15_TeaShelf';left=-32.282;wall=-30.468;top=13.18
box(((left+wall)/2,.48,top-.014),((wall-left),.30,.028),'oldwood')
for side,direction in [(left,1),(wall,-1)]:
    box((side+direction*.027,.48,top-.049),(.054,.26,.042),'brown')
    for dep in (.398,.562):
        box((side+direction*.007,dep,top-.093),(.016,.025,.091),'darksteel')
        anchors.append([label,god(world((side,dep,top-.10))),site])
label='Room15_TeaService';thermos(-31.64,.48,top,'vintage_red');kettle(-31.18,.50,top);cup(-31.88,.455,top,'celadon')
check(-31.64,.48,top,'tea shelf');light((-31.85,.23,13.91),(-31.39,.61,13.27),.63)
site='main';label='Room15_SupperWall';wall=-27.126
box((wall-.011,.995,13.45),(.020,1.34,.86),'grout')
for row in range(5):
    for col in range(9):
        box((wall-.024,.397+col*.148,13.122+row*.164),(.011,.145,.161),'tile')
rod((wall-.092,.442,13.76),(wall-.092,1.52,13.76),.01,'darksteel',12)
for d in (.46,1.50):
    rod((wall+.006,d,13.76),(wall-.093,d,13.76),.014,'darksteel');anchors.append([label,god(world((wall,d,13.76))),site])
for d in (.63,.94,1.20):
    line([(wall-.093,d,13.771),(wall-.113,d,13.78),(wall-.121,d,13.75),(wall-.114,d,13.726)],.004,'steel')
hanger(wall-.116,.63,13.733,.32,'brown')
# Wooden rice paddle and deep metal ladle hanging from the same rail.
rod((wall-.116,.94,13.733),(wall-.116,.94,13.529),.009,'bamboo')
for i in range(24):
    a,b=[q*math.tau/24 for q in (i,i+1)]
    face([(wall-.137,.94,13.468),(wall-.117,.94+math.cos(a)*.039,13.468+math.sin(a)*.066),(wall-.117,.94+math.cos(b)*.039,13.468+math.sin(b)*.066)],'bamboo')
rod((wall-.116,1.20,13.733),(wall-.126,1.2,13.45),.007,'steel')
vessel(wall-.131,1.20,13.366,[(.009,0),(.035,.013),(.052,.039),(.054,.045),(.048,.040),(.015,.007)],'steel')
light((-28.64,.23,13.94),(-27.19,.9,13.5),.65)
# A shade hangs from the actual ceiling, visible above the sill from the lower pavement.
label='Room15_Pendant';cx=-28.32;dep=.83;ceiling=14.478
vessel(cx,dep,ceiling-.023,[(.046,0),(.052,.012),(.052,.023)],'cream')
rod((cx,dep,ceiling-.023),(cx,dep,14.075),.0037,'darksteel')
vessel(cx,dep,13.994,[(.027,0),(.025,.073),(.015,.084)],'cream')
vessel(cx,dep,13.925,[(.128,0),(.131,.008),(.083,.034),(.041,.086),(.029,.096)],'bottle',48)
vessel(cx,dep,13.919,[(.12,0),(.124,.007)],'ivory',48)
vessel(cx,dep,13.88,[(.011,0),(.023,.011),(.025,.032),(.018,.047)],'ivory')
anchors.append([label,god(world((cx,dep,ceiling))),site])
# West pantry counter stands on its own inside the glass, with room behind it.
site='west';label='Room15_PantryBench';floor=16.470;top=17.536
for l in (20.79,21.82):
    for d in (.54,.90):
        box((l,d,(floor+top-.038)/2),(.049,.052,top-.038-floor),'oldwood')
        floors.append([label,god(world((l,d,floor))),site])
box((21.305,.72,top-.023),(1.18,.48,.046),'oldwood')
box((21.305,.93,top-.102),(1.10,.026,.132),'oldwood')
label='Room15_PantryWare'
bowl(20.98,.615,top,.122,'ivory',4);jar(21.70,.70,top,.23,.072,'celadon');thermos(21.47,.76,top,'bottle')
vessel(21.20,.78,top,[(.059,0),(.068,.113),(.070,.118),(.060,.117),(.055,.015)],'blue',32)
for i in range(13):
    a=i*2.4;x=21.2+.046*math.cos(a);y=.78+.042*math.sin(a)
    rod((x,y,top+.04),(x+math.cos(a)*.021,y+math.sin(a)*.021,top+.217+.019*math.sin(a*1.6)),.0027,'bamboo',7)
check(21.47,.76,top,'pantry counter')
light((21.08,.28,18.64),(21.28,1.39,17.75),.8)
created=[]
for name,points in verts.items():
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(points,[],faces[name]);mesh.update()
    ob=bpy.data.objects.new(name,mesh);collection.objects.link(ob);created.append(ob)
    used=list(dict.fromkeys(slots[name]))
    for key in used:mesh.materials.append(materials[key])
    uv=mesh.uv_layers.new(name='UVMap')
    for poly,key in zip(mesh.polygons,slots[name]):
        poly.material_index=used.index(key)
        for i in poly.loop_indices:
            p=mesh.vertices[mesh.loops[i].vertex_index].co
            uv.data[i].uv=(p.y*.82,p.z) if abs(poly.normal.x)>.65 else ((p.x*.82,p.z) if abs(poly.normal.y)>.65 else (p.x*.82,p.y*.82))
bpy.ops.object.select_all(action='DESELECT')
for ob in created:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(assets/'rooms.glb'),export_format='GLB',use_selection=True,export_animations=False)
# Verify each mounting point against the original relevant interior mesh, which has no player collider.
lookup={}
for label,point,room in anchors+floors:
    is_floor=label=='Room15_PantryBench'
    target=('IR_B_A01_noodle_Interiors_' if room=='main' else 'IR_B_A04_courtyard_home_Interiors_')+('room_floor' if is_floor else 'room_wall')
    ob=bpy.context.scene.objects[target]
    if target not in lookup:lookup[target]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
    p=Vector((point[0],-point[2],point[1]));hit=lookup[target].find_nearest(p)
    assert hit and hit[3]<.004,(label,target,hit)
with (assets/'layout.json').open('w',encoding='utf8') as f:json.dump(dict(lights=lights,fixtures=anchors+floors,contacts=checks),f,indent=2)
bpy.context.scene['street_revision']='R24 build 15 lived-in windows'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_rooms.blend'),compress=True,relative_remap=True)
print('ROOM15',len(created),len(anchors),len(floors),len(lights),flush=True)
