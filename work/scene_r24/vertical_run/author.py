"""Join two existing residential shells in the build 22 editable district."""
import ast, json, math, sys
from pathlib import Path
import bmesh,bpy
from mathutils import Vector
here=Path(__file__).resolve().parent
game=here.parents[1]/'project/chongqing_godot_v05'
out=game/'assets/vertical_run'
out.mkdir(exist_ok=True)
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent,scene,ground
def use(file,names):
    root=ast.parse(file.read_text('utf8'))
    exec(compile(ast.Module([d for d in root.body if isinstance(d,ast.FunctionDef) and d.name in names],[]),str(file),'exec'),globals())
use(here.parent/'district_connections/author.py',('mark','face','box','publish','finish','solid_clip'))
use(here.parent/'indoor_delivery/author.py',('prism','slab','floor','beam'))
use(here.parent/'district_connections/author.py',('material',))
collection=bpy.data.collections.new('Blue tile stair and upper crossing')
scene.collection.children.link(collection)
layout=json.loads((game/'assets/indoor_delivery/layout.json').read_text('utf8'))
batches={};metric_uv={}
mat={k:bpy.data.materials['R18_unit22_'+k] for k in ['terrazzo','tread','plaster','metal','dado','edge','brass','enamel','maroon','conduit','lamp']}
mat['blueiron']=material('blue24_blueiron',(.32,.38,.35),.74,.28)
mat['greyglass']=material('blue24_glass',(.61,.69,.69),.28,.08)
mat['doorwood']=material('blue24_doorwood',(.32,.19,.105),.72,0.)
S='COL_Blue24_Stair'; B='COL_Blue24_Crossing'; H='COL_Blue24_301'; D='Blue24_Fixtures'
G=17.12; U=23.92; M=20.52; L=22.90
# The long front opening belongs to the service stair. Clip other rooms only inside its envelope.
volumes=[prism(-86.12,-81.40,9.01,17.91,G-.19,U+2.68),
         prism(-86.12,-83.72,8.03,9.18,G-.17,G+2.46),
         prism(-83.68,-81.47,8.10,9.15,U+.80,U+2.25),
         prism(-81.52,-79.12,9.22,15.43,U-.19,U+2.64),
         prism(-79.24,-77.13,13.36,15.43,U-.19,U+2.59),
         prism(-66.97,-58.58,13.36,15.43,L-.17,U+2.55)]
for ob in list(scene.objects):
    if ob.type!='MESH' or ob.hide_render or not ob.data.polygons:continue
    if not (any(tag in ob.name for tag in ['A03','A04']) or ob.name.startswith(('Room15_','COLH_','COL_Terrain_')) or ob.name in ('COL_D18_RoomShells','D18_BackRoomFurnishings')):continue
    lo,hi=extent(ob)
    if hi[0]<-86.13 or lo[0]>-58.57 or hi[1]<-17.92 or lo[1]>-8.02 or hi[2]<G-.20 or lo[2]>U+2.69:continue
    # Remove the complete old balcony bay outside the upper stair window. Separate
    # slats, posts and laundry shared the same mounting slab in the original mesh.
    if ob.name.startswith(('B_A03_blue_apartments_details_','B_A04_courtyard_home_details_')):
        bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
        pending=set(bm.verts);remove=[]
        while pending:
            group=[pending.pop()]
            for v in group:
                for edge in v.link_edges:
                    other=edge.other_vert(v)
                    if other in pending:pending.remove(other);group.append(other)
            vs=[v.co for v in group]
            x0,x1=min(v.x for v in vs),max(v.x for v in vs)
            z0,z1=min(-v.y for v in vs),max(-v.y for v in vs)
            y0,y1=min(v.z for v in vs),max(v.z for v in vs)
            north_bay=-85.52<x0 and x1<-82.48 and z0<9.12 and z1<9.39 and (16.0<y0 and y1<20.17 or 24.33<y0 and y1<26.7)
            blue_bridge_bay=-78.49<x0 and x1<-76.95 and 13.08<z0 and z1<15.95 and 24.22<y0 and y1<28.05
            home_bridge_bay=-67.0<x0 and x1<-65.50 and 12.98<z0 and z1<15.55 and 24.16<y0 and y1<26.65
            if north_bay or blue_bridge_bay or home_bridge_bay:
                remove.extend(group)
        if remove:
            bmesh.ops.delete(bm,geom=remove,context='VERTS');finish(ob,bm)
        else:bm.free()
    if ob.name.startswith('COL_Terrain_'):
        solid_clip(ob,[prism(-86.06,-83.72,8.10,9.05,G-1,G+1)]+[q for q in volumes if min(-v[1] for v in q[0])>=9.01])
    else:solid_clip(ob,volumes)
# A closed stairwell faces the north alley. Its upper window admits light from the same alley.
def plaster(n,x0,x1,z0,z1,lo,hi):
    slab(n,x0,x1,z0,z1,lo,hi,'plaster')
def dado_x(x,z0,z1,lo,hi):
    slab(D,x-.012,x+.012,z0,z1,lo,hi,'dado')
def wall_z(z,x0,x1,lo,hi):
    plaster(S,x0,x1,z-.06,z+.06,lo,hi)
def strip(n,x0,x1,z0,z1,y):
    slab(n,x0,x1,z0,z1,y-.025,y,'edge')
floor(S,-86.06,-83.72,9.05,10.40,G)
# Reuse the perimeter elevations from the original alley. The inset landing
# shares an edge with the street and has solid cheeks down to its footing.
limits=[(-86.06,8.10),(-83.72,8.10),(-83.72,9.05),(-86.06,9.05)]
apron=[]
for x,z in limits:
    h=ground.down(x,-z,G+1,2)[0][0] if z<9 else G
    apron.append(Vector((x,-z,h)))
face(S,list(reversed(apron)),'terrazzo')
for i in range(4):
    a,b=apron[i],apron[(i+1)%4]
    face(S,[b,a,Vector((a.x,a.y,G-.65)),Vector((b.x,b.y,G-.65))],'edge')
# Dressed reveals and a continuous sill replace the removed lower balcony
# and its old window opening at the back-lane entrance.
for xa,xb in [(-86.24,-86.035),(-83.76,-82.52)]:
    plaster(S,xa,xb,8.90,9.09,G-.36,G+2.64)
    slab(D,xa,xb,8.886,8.901,G-.09,G+.59,'edge')
plaster(S,-86.24,-82.52,8.89,9.11,G+2.35,G+2.70)
slab(D,-86.31,-82.49,8.80,9.11,G+2.68,G+2.74,'terrazzo')
for j in range(20):
    z=10.4+j*.29;y=G+(j+1)*.17
    floor(S,-86.06,-83.79,z,z+.29,y,'tread',.24)
    strip(D,-86.01,-83.84,z+.012,z+.032,y+.001)
    z=16.2-j*.29;y=M+(j+1)*.17
    floor(S,-83.69,-81.45,z-.29,z,y,'tread',.24)
    strip(D,-83.64,-81.5,z-.03,z-.009,y+.001)
floor(S,-86.06,-81.45,16.2,17.86,M)
floor(S,-83.70,-81.45,9.04,9.22,U)
floor(S,-83.70,-79.19,9.22,10.40,U)
floor(S,-81.45,-79.19,10.40,15.36,U)
floor(S,-79.19,-78.0,13.40,15.36,U)
plaster(S,-86.11,-86.02,8.95,17.87,G-.15,U+2.55)
plaster(S,-81.49,-81.41,10.41,17.87,G-.15,U+2.52)
wall_z(17.87,-86.10,-81.43,G-.15,U+2.55)
def rake(n,x0,x1,z0,z1,h0,h1,bottom,top,k):
    end=lambda z,h:[Vector((x0,-z,h+bottom)),Vector((x1,-z,h+bottom)),Vector((x1,-z,h+top)),Vector((x0,-z,h+top))]
    a,b=end(z0,h0),end(z1,h1)
    center=sum(a+b,Vector())/8
    for q in [a,b]+[[a[i],a[(i+1)%4],b[(i+1)%4],b[i]] for i in range(4)]:
        if (q[1]-q[0]).cross(q[2]-q[0]).dot(sum(q,Vector())/4-center)<0:q=list(reversed(q))
        face(n,q,k)
for low,high,k in [(-.23,.85,'dado'),(.85,.91,'terrazzo')]:
    rake(S,-83.83,-83.745,10.4,16.2,G+.085,M+.085,low,high,k)
    rake(S,-83.735,-83.65,10.4,16.2,U-.085,M-.085,low,high,k)
rake(S,-86.055,-83.79,10.4,16.2,G,M,2.96,3.08,'plaster')
floor(S,-86.055,-83.79,8.98,10.40,G+3.08,'plaster',.12)
floor(S,-86.02,-81.49,9.07,17.81,G-.25,'terrazzo',.14)
wall_z(9.04,-86.10,-83.72,G+2.36,U+2.57)
wall_z(9.04,-83.72,-81.41,G-.15,U+.84)
wall_z(9.04,-83.72,-81.41,U+2.18,U+2.57)
floor(S,-86.10,-81.41,9.04,17.9,U+2.66,'plaster',.13)
for x in [-83.67,-82.59,-81.52]:
    slab(D,x-.022,x+.022,8.98,9.10,U+.84,U+2.19,'metal')
for y in [U+.855,U+1.86,U+2.165]:
    slab(D,-83.69,-81.49,8.98,9.10,y-.018,y+.018,'metal')
slab(D,-83.73,-81.43,8.90,9.20,U+.81,U+.86,'terrazzo')
# Entrance jambs, upper hallway return and glazed landing; no landing opens into a blank wall.
for x in [-85.99,-83.83]:
    slab(D,x-.034,x+.034,8.91,9.09,G,G+2.36,'metal')
slab(D,-86.03,-83.79,8.91,9.09,G+2.32,G+2.37,'metal')
wall_z(9.25,-81.43,-79.15,U-.15,U+2.54)
wall_z(15.38,-81.46,-78.0,U-.15,U+2.54)
plaster(S,-79.21,-79.13,9.24,13.39,U-.15,U+2.54)
wall_z(13.38,-79.18,-77.98,U-.14,U+2.55)
floor(S,-81.46,-79.14,9.22,15.41,U+2.64,'plaster',.12)
floor(S,-79.14,-77.98,13.38,15.41,U+2.64,'plaster',.12)
rake(D,-86.025,-85.995,10.4,16.2,G,M,-.01,.94,'dado')
rake(D,-81.507,-81.481,10.4,16.2,U,M,-.01,.94,'dado')
for z in [11.92,14.94]:
    base=G+(z-10.4)*3.40/5.80
    rake(D,-85.37,-84.34,z-.085,z+.085,base-.050,base+.05,2.90,2.96,'metal')
    rake(D,-85.30,-84.41,z-.059,z+.059,base-.050,base+.05,2.875,2.90,'lamp')
slab(S,-83.64,-81.55,9.048,9.061,U+.88,U+2.14,'greyglass')
slab(D,-86.02,-81.50,17.79,17.817,M,M+1.0,'dado')
# Steel stringers and cross frames span the actual 12 m alley. Raised parapets guard its open sides.
floor(B,-78.0,-66.0,13.40,15.36,U,'tread',.16)
for z in [13.41,15.35]:
    slab(B,-78.04,-65.96,z-.055,z+.055,U-.32,U-.12,'blueiron')
    slab(B,-78.02,-65.98,z-.07,z+.07,U,U+.26,'edge')
    for j in range(7):
        x=-78+j*2
        slab(B,x-.042,x+.042,z-.04,z+.04,U+.23,U+1.41,'blueiron')
        if j<6:
            beam(D,(x,U+.32,z),(x+2,U+1.34,z),.040,'blueiron')
            beam(D,(x,U+1.34,z),(x+2,U+.32,z),.040,'blueiron')
    for h in [.71,1.40]:slab(B,-78,-66,z-.038,z+.038,U+h-.026,U+h+.026,'blueiron')
for x in [-77.84,-75,-72,-69,-66.16]:
    slab(B,x-.045,x+.045,13.40,15.36,U-.26,U-.16,'blueiron')
# Riveted cover plates mark the main truss connections. Keep their thickness off the walking surface.
for z,sgn in [(13.41,1),(15.35,-1)]:
    for j in range(1,6):
        x=-78+j*2
        for h in [.39,1.28]:
            slab(D,x-.125,x+.125,z+sgn*.042,z+sgn*.053,U+h-.09,U+h+.09,'blueiron')
            for xx in [x-.073,x+.073]:
                slab(D,xx-.011,xx+.011,z+sgn*.054,z+sgn*.063,U+h-.018,U+h+.004,'brass')
# Close the old window rebates beside and above the new bridge openings.
for xa,xb,max_y in [(-78.065,-77.98,27.70),(-66.04,-65.94,26.42)]:
    for za,zb in [(13.17,13.405),(15.355,15.75)]:
        plaster(B,xa,xb,za,zb,U-.24,max_y)
    plaster(B,xa,xb,13.17,15.75,U+2.37,max_y)
    for za,zb in [(13.32,13.41),(15.35,15.44)]:
        slab(D,xa-.045,xb+.045,za,zb,U,U+2.38,'blueiron')
    slab(D,xa-.047,xb+.047,13.33,15.43,U+2.33,U+2.40,'blueiron')
# A half-level descent in the original house ends at a real leaf, bell and ledge.
floor(H,-66,-65,13.40,15.36,U)
for j in range(6):
    x=-65+j*.30;y=U-(j+1)*.17
    floor(H,x,x+.30,13.40,15.36,y,'tread',.23)
    strip(D,x+.26,x+.28,13.45,15.31,y+.001)
floor(H,-63.20,-58.66,13.40,15.36,L)
for z in [13.37,15.39]:
    plaster(H,-66,-58.62,z-.05,z+.05,L-.15,U+2.51)
    slab(D,-65.92,-58.69,z-.057,z+.057,L+.08,L+1.17,'dado')
floor(H,-66.02,-58.61,13.34,15.43,U+2.55,'plaster',.12)
plaster(H,-58.68,-58.59,13.36,15.41,L-.15,U+2.48)
slab(D,-58.80,-58.69,13.54,14.63,L,L+2.14,'metal')
slab(D,-58.815,-58.803,13.605,14.565,L+.045,L+2.08,'doorwood')
for h in [.24,1.01]:
    slab(D,-58.828,-58.814,13.69,14.48,L+h,L+h+.60,'doorwood')
slab(D,-58.84,-58.817,14.36,14.43,L+.86,L+1.09,'brass')
slab(D,-58.892,-58.84,14.382,14.41,L+.985,L+1.012,'brass')
slab(D,-58.907,-58.88,14.285,14.408,L+.986,L+1.011,'brass')
slab(D,-58.85,-58.82,14.07,14.10,L+1.47,L+1.50,'brass')
slab(H,-58.995,-58.68,14.74,15.20,L+.86,L+.90,'edge')
for z in [14.8,15.14]:
    beam(D,(-58.70,L+.64,z),(-58.96,L+.86,z),.022,'metal')
slab(D,-58.76,-58.69,14.78,14.90,L+1.18,L+1.32,'enamel')
for z in [13.35,15.42]:
    slab(B,-66.16,-65.96,z-.04,z+.04,U-.36,U+.31,'edge')
# Service hardware follows plaster or structure. Fluorescent housings sit flush against the ceiling.
for x,z,y in [(-84.85,13.7,U+2.53),(-82.58,11.1,U+2.53),(-80.3,14.4,U+2.52),(-61,14.36,U+2.43)]:
    slab(D,x-.36,x+.36,z-.084,z+.084,y-.045,y,'metal')
    slab(D,x-.32,x+.32,z-.067,z+.067,y-.067,y-.045,'lamp')
for x in [-84.78,-83.96]:
    slab(D,x-.30,x+.30,17.71,17.79,M+1.10,M+1.55,'metal')
    slab(D,x-.28,x+.28,17.69,17.71,M+1.12,M+1.53,'dado')
    slab(D,x+.19,x+.22,17.665,17.692,M+1.25,M+1.31,'brass')
slab(D,-84.83,-83.94,17.70,17.744,M+1.60,M+1.633,'conduit')
slab(D,-84.80,-84.77,17.70,17.744,M+1.54,M+1.63,'conduit')
# Low-contrast rubber mat and a small resident's repair notice at 301.
slab(D,-59.36,-58.817,13.58,14.58,L+.001,L+.011,'metal')
for j in range(15):
    slab(D,-59.32,-58.86,13.62+j*.061,13.635+j*.061,L+.011,L+.014,'dado')
slab(D,-61.72,-60.86,13.419,13.445,L+1.16,L+1.81,'doorwood')
slab(D,-61.67,-60.91,13.445,13.451,L+1.21,L+1.76,'dado')
publish()
assert not [k for k in layout['changed'] if not scene.objects[k].data.polygons], 'Empty clipped source requires retirement'
layout['crossing_levels_m']=[G,M,U,L];layout['span_m']=12
(out/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf8')
bpy.ops.object.select_all(action='DESELECT')
for key in layout['changed']+layout['new']:scene.objects[key].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'vertical.glb'),use_selection=True,export_animations=False,export_image_format='NONE')
scene['street_revision']='R24 build 24 - blue stair and cross-alley delivery'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_crossing.blend'),compress=True,relative_remap=True)
print('CROSSING_BUILT',len(layout['changed']),len(layout['new']),flush=True)
