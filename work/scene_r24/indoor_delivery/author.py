"""Rebuild the occupied A04 stairwell inside the build-21 district, in metres."""
from pathlib import Path
import bpy,bmesh,json,math,sys,ast
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
game=here.parents[1]/'project/chongqing_godot_v05'
out=game/'assets/indoor_delivery'
out.mkdir(exist_ok=True)
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import scene,extent
# Use the same UV-preserving plane clipper and metric UV mesher as the street openings.
source=here.parent/'district_connections/author.py'
defs=ast.parse(source.read_text('utf8'))
names=('mark','material','face','box','publish','finish','solid_clip')
exec(compile(ast.Module([d for d in defs.body if isinstance(d,ast.FunctionDef) and d.name in names],[]),str(source),'exec'))
collection=bpy.data.collections.new('A04 unit one - east court to north alley')
scene.collection.children.link(collection)
layout={'new':[],'changed':[],'retired':[]}
batches={};metric_uv={}
G=16.44
U=G+3.45
def prism(x1,x2,z1,z2,lo,hi):
    return ([(x1,-z1),(x2,-z1),(x2,-z2),(x1,-z2)],lo,hi)
domains=[prism(-64.40,-55.05,18.28,20.74,G-.025,U+2.79),
         prism(-55.45,-53.15,18.60,20.40,G+.018,G+2.33),
         prism(-63.18,-61.17,8.86,18.59,U-.20,U+2.72)]
for o in list(scene.objects):
    if o.type!='MESH' or o.hide_render or not o.data.polygons:continue
    if o.name.startswith('R17_Entry_A04_0_'):
        # Transfer the existing detailed leaf, frame, hardware and spyglass as a unit.
        delta=o.matrix_world.to_3x3().inverted()@Vector((-9,0,3.45))
        for v in o.data.vertices:v.co+=delta
        mark(o);continue
    if o.name.startswith('B_A04_courtyard_home_details_'):
        # The north exit occupies a former balcony bay. Remove whole balcony and appliance
        # components so a piece of the old timber railing cannot hang in the opening.
        bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
        pending=set(bm.verts);remove=[]
        while pending:
            group=[pending.pop()]
            for v in group:
                for e in v.link_edges:
                    other=e.other_vert(v)
                    if other in pending:pending.remove(other);group.append(other)
            pts=[v.co for v in group]
            xmin=min(q.x for q in pts);xmax=max(q.x for q in pts)
            if xmin>-66.12 and xmax<-60.27 and min(q.y for q in pts)>-9.16 and max(q.y for q in pts)>-8.97 and min(q.y for q in pts)<-7.62 and min(q.z for q in pts)>19.02 and max(q.z for q in pts)<22.15:
                remove.extend(group)
        if remove:
            bmesh.ops.delete(bm,geom=remove,context='VERTS');finish(o,bm)
        else:bm.free()
    if not ('A04' in o.name or o.name in ('COL_D18_RoomShells','D18_BackRoomFurnishings') or o.name.startswith(('Room15_','COL_Terrain_','COLH_'))):continue
    lo,hi=extent(o)
    if hi[0]<-64.4 or lo[0]>-53.1 or hi[1]<-20.75 or lo[1]>-8.85 or hi[2]<G-.03 or lo[2]>U+2.8:continue
    solid_clip(o,domains)
for name in list(layout['changed']):
    if not scene.objects[name].data.polygons:
        layout['retired'].append(name);layout['changed'].remove(name)
palette={'plaster':(.60,.55,.42),'dado':(.27,.36,.30),'terrazzo':(.39,.39,.35),'edge':(.38,.36,.30),'metal':(.14,.19,.17),'maroon':(.28,.105,.056),'brass':(.59,.48,.26),'enamel':(.73,.68,.53),'conduit':(.34,.35,.31),'lamp':(.96,.88,.68),'tread':(.49,.47,.40)}
mat={k:material('unit22_'+k,c,.50 if k in ('metal','enamel') else .86,.5 if k in ('metal','conduit','brass') else 0.) for k,c in palette.items()}
S='COL_Unit22_Stairhall';D='Unit22_Fittings';R='COL_Unit22_BackGallery'
def slab(n,x1,x2,z1,z2,y1,y2,k):
    box(n,((x1+x2)/2,-(z1+z2)/2,(y1+y2)/2),(abs(x2-x1),abs(z2-z1),abs(y2-y1)),k)
def floor(n,x1,x2,z1,z2,y,k='terrazzo',depth=.15):
    slab(n,x1,x2,z1,z2,y-depth,y,k)
def xwall(x,z1,z2,low,high):
    slab(S,x-.05,x+.05,z1,z2,low,high,'plaster')
    slab(D,x-.054,x+.054,z1,z2,low+.06,low+1.03,'dado')
def zwall(z,x1,x2,low,high):
    slab(S,x1,x2,z-.05,z+.05,low,high,'plaster')
    slab(D,x1,x2,z-.054,z+.054,low+.06,low+1.03,'dado')
def inclined(xa,xb,za,zb,ya,yb,lo,hi,part,k):
    def section(x,y):
        return [(x,y+lo,za),(x,y+lo,zb),(x,y+hi,zb),(x,y+hi,za)]
    # Make each face point away from the solid, independent of travel direction.
    ends=[section(xa,ya),section(xb,yb)]
    middle=Vector(((xa+xb)/2,-(za+zb)/2,(ya+yb+lo+hi)/2))
    for quad in [ends[0],ends[1]]+[[ends[0][i],ends[0][(i+1)%4],ends[1][(i+1)%4],ends[1][i]] for i in range(4)]:
        v=[Vector((x,-z,y)) for x,y,z in quad]
        if (v[1]-v[0]).cross(v[2]-v[0]).dot(sum(v,Vector())/4-middle)<0:v.reverse()
        face(part,v,k)
# Two flights with a resting landing halfway. The north corridor starts beyond the last tread.
x=-55.42
floor(S,x,-54.90,18.36,20.65,G+.008)
runs=[(.258,1)]*9+[(.81,0)]+[(.258,1)]*11
y=G
for run,step in runs:
    y+=step*3.45/20
    floor(S,x-run,x,18.34,20.69,y,'tread',.34)
    if step:slab(D,x-.026,x-.009,18.41,20.61,y+.0007,y+.002,'edge')
    x-=run
for xa,xb,ya,yb in [(-55.42,-57.742,G,G+1.5525),(-57.742,-58.552,G+1.5525,G+1.5525),(-58.552,-61.39,G+1.5525,U)]:
    for z in [18.32,20.71]:
        inclined(xa,xb,z-.05,z+.05,ya,yb,-.34,2.8,S,'plaster')
        inclined(xa,xb,z-.055,z+.055,ya,yb,-.02,1.08,D,'dado')
    inclined(xa,xb,18.29,20.76,ya,yb,2.67,2.81,S,'plaster')
assert abs(x+61.39)<.001
floor(S,-64.37,x,18.32,20.7,U)
xwall(-64.36,18.3,20.73,U,U+2.7)
zwall(20.7,-64.4,x,U,U+2.71)
zwall(18.38,-64.40,-63.12,U,U+2.71)
slab(S,-64.40,x,18.31,20.75,U+2.64,U+2.76,'plaster')
floor(S,-63.15,-61.20,8.967,18.32,U)
xwall(-63.14,8.94,18.36,U,U+2.71)
xwall(-61.22,8.94,18.36,U,U+2.71)
slab(S,-63.18,-61.16,9,18.34,U+2.64,U+2.76,'plaster')
# A real lintel carries the exterior address plaque and caps the opening.
slab(S,-63.17,-61.17,8.967,9.13,U+2.12,U+2.73,'dado')
for x0 in [-63.15,-61.29]:
    slab(S,x0,x0+.085,8.967,9.13,U,U+2.13,'dado')
# The 202 leaf faces the corridor. Recessed panel, latch, handle and threshold.
slab(S,-63.085,-63.01,13.20,14.18,U,U+2.09,'metal')
slab(D,-63.008,-62.986,13.27,14.11,U+.13,U+1.94,'maroon')
for y0 in [.30,1.14]:
    slab(D,-62.987,-62.977,13.34,14.04,U+y0,U+y0+.56,'maroon')
slab(D,-62.999,-62.92,13.33,13.51,U+.985,U+1.010,'brass')
# A replacement lock and a shallow stamped leaf on the second flat.
for za,zb in [(13.29,13.32),(14.06,14.09)]:
    slab(D,-62.986,-62.964,za,zb,U+.17,U+1.92,'metal')
for yy in [.21,.80,1.12,1.83]:
    slab(D,-62.978,-62.961,13.33,14.04,U+yy,U+yy+.021,'maroon')
slab(D,-62.982,-62.952,13.32,13.4,U+.82,U+1.09,'brass')
slab(D,-62.955,-62.932,13.35,13.372,U+.855,U+.889,'metal')
slab(D,-62.979,-62.957,13.68,13.72,U+1.48,U+1.52,'brass')
slab(D,-63.078,-62.98,14.26,14.36,U+1.09,U+1.24,'enamel')
slab(D,-62.981,-62.968,14.29,14.32,U+1.12,U+1.16,'metal')
slab(D,-63.07,-62.54,13.25,14.11,U+.001,U+.012,'metal')
for j in range(18):
    slab(D,-63.05,-62.57,13.28+j*.046,13.29+j*.046,U+.012,U+.015,'dado')
# Exposed conduit turns down to the doorbell. The fuse cabinet stands off the opposite wall.
slab(D,-61.306,-61.28,9.1,18.3,U+2.32,U+2.35,'conduit')
slab(D,-61.314,-61.281,14.9,14.93,U+1.61,U+2.35,'conduit')
slab(D,-61.414,-61.275,14.66,15.18,U+1.31,U+1.72,'metal')
slab(D,-61.424,-61.415,14.70,15.14,U+1.35,U+1.68,'dado')
for j in range(5):slab(D,-61.429,-61.423,15.005,15.105,U+1.38+j*.027,U+1.385+j*.027,'metal')
# Wall shelves beside each occupied flat. The angle brackets meet the plaster behind each shelf.
for wall,zc in [(-64.302,20.38),(-63.087,14.62)]:
    slab(S,wall,wall+.32,zc-.235,zc+.235,U+.86,U+.89,'edge')
    for zz in [zc-.16,zc+.16]:
        slab(D,wall,wall+.025,zz-.014,zz+.014,U+.67,U+.86,'metal')
        slab(D,wall,wall+.284,zz-.014,zz+.014,U+.84,U+.862,'metal')
# Open street gates, hinges and service fittings at a readable scale.
for x0,z0 in [(-54.8,20.48),(-62.95,9.65)]:
    base=G if x0>-60 else U
    for j in range(7):
        if x0>-60:slab(D,x0+j*.125,x0+j*.125+.016,z0,z0+.033,base+.08,base+2.09,'metal')
        else:slab(D,x0,x0+.025,z0+j*.12,z0+j*.12+.016,base+.08,base+2.09,'metal')
    for h in [.10,.94,2.05]:
        if x0>-60:slab(D,x0,x0+.77,z0,z0+.033,base+h,base+h+.034,'metal')
        else:slab(D,x0,x0+.032,z0,z0+.74,base+h,base+h+.034,'metal')
# Upper door opens onto the bridge, with an outside flight that lands in the paved alley.
floor(R,-65.80,-61.88,7.14,8.967,U,'tread',.23)
floor(R,-61.88,-61.20,8.45,8.967,U,'tread',.23)
start=-65.80
count=15
for j in range(count):
    floor(R,start-(j+1)*.28,start-j*.28,7.14,8.967,U-(j+1)*.17,'tread',.34)
end=start-count*.28
inclined(start,end,7.14,8.967,U-.08,U-2.63,-.30,-.12,R,'edge')
for z in [7.18,8.93]:
    for j in range(count):
        xx=start-j*.28;y=U-(j+1)*.17
        slab(R,xx-.28,xx,z-.036,z+.036,y-.28,y+.078,'edge')
        if j%2==0:slab(R,xx-.16,xx-.13,z-.018,z+.018,y+.056,y+.99,'metal')
def beam(name,a,b,w,key):
    a=Vector((a[0],-a[2],a[1]));b=Vector((b[0],-b[2],b[1]))
    along=(b-a).normalized();side=along.cross(Vector((0,0,1))).normalized()*w/2
    up=side.normalized().cross(along)*w/2
    pts=[p+side*i+up*j for p in (a,b) for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[pts[i] for i in f],key)
for z in [7.18,8.93]:
    for h in [.57,1.01]:
        beam(R,(start,U+h-.08,z),(end,U-2.55+h-.08,z),.042,'metal')
for a,b in [((-65.80,7.18),(-61.92,7.18)),((-61.92,7.18),(-61.92,8.49)),((-61.92,8.49),(-61.24,8.49)),((-61.24,8.49),(-61.24,8.967)),((-65.8,8.93),(-63.18,8.93))]:
    count=math.ceil(math.dist(a,b)/.90)
    for i in range(count+1):
        t=i/count;xx=a[0]+(b[0]-a[0])*t;zz=a[1]+(b[1]-a[1])*t
        slab(R,xx-.018,xx+.018,zz-.018,zz+.018,U-.03,U+1.02,'metal')
    for h in [.53,1.02]:beam(R,(a[0],U+h,a[1]),(b[0],U+h,b[1]),.043,'metal')
for xx in [-65.50,-62.15]:
    slab(R,xx-.085,xx+.085,7.30,7.49,17.10,U-.22,'edge')
# Short steel returns protect the gap along the outer top landing.
for xx,yy,zz in [(-55.0,G,19.50),(-58.10,G+1.55,19.50),(-62.92,U,19.55),(-62.17,U,13.85)]:
    slab(D,xx-.23,xx+.23,zz-.105,zz+.105,yy+2.51,yy+2.78,'metal')
    slab(D,xx-.19,xx+.19,zz-.075,zz+.075,yy+2.48,yy+2.51,'lamp')
# Original doorway is now a unit entrance. Mail cubbies face the visitor, with pressed steel folds.
for j in range(4):
    xx=-54.92+j*.305
    for i in range(2):
        yy=G+.83+i*.29
        slab(D,xx,xx+.30,18.50,18.66,yy,yy+.285,'metal')
        slab(D,xx+.022,xx+.277,18.657,18.665,yy+.08,yy+.261,'dado')
        slab(D,xx+.037,xx+.264,18.665,18.673,yy+.215,yy+.231,'metal')
# Reuse the neighbourhood print atlas, one cropped patch per actual wall plane.
notice_name='Unit22_HallNotices'
mat['paper']=material('unit22_paper',(.8,.78,.69),.91)
notices=[((-63.081,U+1.42,16.36),(0,0,-1),.85,1),
         ((-61.276,U+1.47,11.68),(0,0,1),.62,7),
         ((-58.14,G+2.94,20.654),(-1,0,0),.66,5)]
for (cx,cy,cz),(tx,ty,tz),width,which in notices:
    coords=[(cx+tx*dx*width,-(cz+tz*dx*width),cy+dy*width) for dx,dy in [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]]
    face(notice_name,coords,'paper')
publish()
posters=scene.objects[notice_name].data
for poly,(_,_,_,which) in zip(posters.polygons,notices):
    for li,(u,v) in zip(poly.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):
        posters.uv_layers[0].data[li].uv=((which%4+u)/4,(1-which//4+v)/2)
stock=mat['paper']
photo=stock.node_tree.nodes.new('ShaderNodeTexImage')
photo.image=bpy.data.images.load(str(game/'assets/district_age/wall_prints.png'),check_existing=True)
bs=stock.node_tree.nodes.get('Principled BSDF')
stock.node_tree.links.new(photo.outputs['Color'],bs.inputs['Base Color'])
stock.node_tree.links.new(photo.outputs['Alpha'],bs.inputs['Alpha'])
layout['lower_floor']=G;layout['upper_floor']=U
(out/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf8')
bpy.ops.object.select_all(action='DESELECT')
for key in layout['changed']+layout['new']:scene.objects[key].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'unit.glb'),use_selection=True,export_animations=False,export_image_format='NONE')
scene['street_revision']='R24 build 22 - A04 indoor delivery'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_unit.blend'),compress=True,relative_remap=True)
print('UNIT_BUILT',layout,flush=True)
