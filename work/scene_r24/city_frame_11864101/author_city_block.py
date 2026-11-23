"""Author the court, canopy and graded junction fixes together with the editable city planning layer."""
import bpy,sys,json,math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root))
from trim_paving import repair
scene=bpy.context.scene
project=root.parents[1]/"project/chongqing_godot_v05"
assets=project/"assets/street_finish_r24"
assets.mkdir(exist_ok=True)
def group(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
street=group('R24_11_Court_and_yards')
city=group('R24_11_Local_city_frame')
geos=defaultdict(lambda:([],[]))
mats={}
def mat(key,col,metal=0.,rough=.76):
    m=bpy.data.materials.new('City11_'+key)
    m.diffuse_color=(*col,1.)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=m.diffuse_color
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    mats[key]=m
mat('zinc',(.258,.294,.288),.48,.70);mat('lip',(.227,.182,.133),.41);mat('steel',(.105,.134,.124),.34);mat('wash',(.256,.304,.269),.33)
mat('target',(.42,.064,.037),.03);mat('plate',(.19,.12,.085),.34)
def meshpart(key,vs,fs):
    v,f=geos[key]; off=len(v);v.extend([tuple(p) for p in vs]);f.extend(tuple(off+i for i in face) for face in fs)
def prism(key,a,b,r,n=8):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.orthogonal().normalized();v=axis.cross(u)
    vs=[p+r*(u*math.cos(k*math.tau/n)+v*math.sin(k*math.tau/n)) for p in (a,b) for k in range(n)]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    meshpart(key,vs,fs)
def flush(collection):
    objects=[]
    for (name,m), (verts,faces) in geos.items():
        if not faces:continue
        data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
        obj=bpy.data.objects.new(name,data);collection.objects.link(obj);data.materials.append(mats[m]);objects.append(obj)
    geos.clear()
    return objects
def export(objs,path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.hide_set(False);o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False,export_yup=True)
retire=[];contacts=[]
for i in range(3):
    old=scene.objects[f'Courtyard_service_canopy_{i}_painted_metal']; coords=[old.matrix_world@v.co for v in old.data.vertices]
    lo=[min(v[k] for v in coords) for k in range(3)];hi=[max(v[k] for v in coords) for k in range(3)]
    cx=(lo[0]+hi[0])/2; cy=(lo[1]+hi[1])/2; peak=hi[2]-.025
    def roof(y):return peak-.065*(cy+1.70-y)
    key=lambda suffix,m:(f'Canopy{i}_{suffix}',m)
    N=160
    verts=[]
    for side in [0,1]:
        for y in [cy-1.70,cy+1.70]:
            for j in range(N+1):
                x=cx-1.90+3.8*j/N
                z=roof(y)+(.012 if j%4 in (1,2) else 0)-side*.009
                verts.append((x,y,z))
    def v(side,edge,j):return (side*2+edge)*(N+1)+j
    faces=[]
    for j in range(N):
        faces += [(v(0,0,j),v(0,0,j+1),v(0,1,j+1),v(0,1,j)),(v(1,1,j),v(1,1,j+1),v(1,0,j+1),v(1,0,j)),(v(1,0,j),v(1,0,j+1),v(0,0,j+1),v(0,0,j)),(v(0,1,j),v(0,1,j+1),v(1,1,j+1),v(1,1,j))]
    for j in (0,N): faces.append((v(0,0,j),v(0,1,j),v(1,1,j),v(1,0,j)))
    meshpart(key('Roof','zinc'),verts,faces)
    for y in [cy-1.50,cy,cy+1.50]:
        prism(key('Purlins','steel'),(cx-1.84,y,roof(y)-.034),(cx+1.84,y,roof(y)-.034),.040,8)
    for x in [cx-1.70,cx+1.70]:
        prism(key('SideRail','steel'),(x,cy-1.61,roof(cy-1.61)-.096),(x,cy+1.61,roof(cy+1.61)-.096),.041)
        for sg in [-1,1]:
            y=cy+sg*1.50
            z=min(v.z for v in coords if (v.x-x)**2+(v.y-y)**2<.019)
            top=roof(y)-.078
            prism(key('Posts','wash'),(x,y,z),(x,y,top),.047,10)
            prism(key('Shoes','steel'),(x,y,z-.018),(x,y,z+.08),.066,8)
            prism(key('Braces','steel'),(x,y,top-.33),(x,y-sg*.33,roof(y-sg*.33)-.095),.020)
            contacts.append([i,round(z,3),round(top,3),round(roof(y)-.034,3)])
    for y in [cy-1.70,cy+1.70]:prism(key('Hem','lip'),(cx-1.9,y,roof(y)-.003),(cx+1.9,y,roof(y)-.003),.017)
    retire.append(old.name);old.hide_render=True;old.hide_set(True)
# Paint a single flat annulus per board. Retain the rim from the original red mesh and remove its two line blocks.
import bmesh
red=scene.objects['Court_fence_and_hoops_faded_red']
bm=bmesh.new();bm.from_mesh(red.data); kill=[]
for f in bm.faces:
    c=red.matrix_world@f.calc_center_median()
    if abs(abs(c.y)-11.15)<.03 and abs(abs(c.x+34)-.28)<.035:kill.append(f)
assert len(kill)>=12,len(kill)
bmesh.ops.delete(bm,geom=kill,context='FACES');bm.to_mesh(red.data);bm.free()
for end in [-1,1]:
    y=end*11.153
    coords=[(-.295,23.59),(.295,23.59),(.295,24.035),(-.295,24.035),(-.254,23.63),(.254,23.63),(.254,23.995),(-.254,23.995)]
    meshpart(('Court_Rim_Target','target'),[(x-34,y,z) for x,z in coords],[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)] if end>0 else [(4,5,1,0),(5,6,2,1),(6,7,3,2),(7,4,0,3)])
    for dx in (-.46,.46):
        prism(('Court_board_bracing','plate'),(-34,end*11.96,23.70),(-34+dx,end*11.25,24.05),.027,8)
details=flush(street)
cuts=repair(scene)
from court_landing import rebuild
tee=rebuild(scene)
donors={}
temp=[]
for i,name in enumerate([red.name,*cuts,*tee['stones']]):
    o=scene.objects[name]
    ob=o.copy();ob.data=o.data.copy();ob.modifiers.clear();ob.name=f'FinishDonor{i:02d}'
    scene.collection.objects.link(ob);ob.data.materials.clear();ob.data.materials.append(mats['steel']);temp.append(ob);donors[ob.name]=o.name
export(details+temp,assets/"street_finish.glb")
for ob in temp:bpy.data.objects.remove(ob,do_unlink=True)
(assets/"finish.json").write_text(json.dumps(dict(donors=donors,retire=retire),indent=2),encoding="utf8")
# Skyline envelopes derived from each source. Keep the internal reference outside the redistributable game assets.
for j,c in enumerate([(.245,.254,.239),(.242,.262,.272),(.301,.285,.257),(.280,.286,.279),(.254,.233,.209),(.217,.247,.257)]):mat(f'wall{j}',c)
mat('sill',(.169,.196,.204));mat('cap',(.21,.219,.215))
def shell(source,poly,low,high,material):
    n=len(poly); vs=[(x,y,z) for z in [low,high] for x,y in poly]
    meshpart((source+'_'+material,material),vs,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]+[tuple(range(n,2*n))])
for rec in json.loads((root/'selected.json').read_bytes()):
    poly=rec['hull'];crown=rec['crown'];top=rec['top'];bottom=min(rec['bottom'],-20.);src=rec['src'];nid=rec['node']
    shoulder=top-max(1.0,min(8.,(top-rec['bottom'])*.13))
    shell(src,poly,bottom,shoulder-.65,'wall'+str(nid%6))
    shell(src,crown if len(crown)>=3 else poly,shoulder-.16,top,'wall'+str(nid%6))
    shell(src,poly,shoulder-.65,shoulder+.03,'cap')
context=flush(city)
export(context,root/"city_frame.glb")
frame_report=dict(canopy_contacts=contacts,removed_original_mark_faces=len(kill),tread_cuts=cuts,court_tee=tee,city_meshes=len(context),detail_meshes=len(details),source_notes="Local design study, unverified commercial rights")
(root/'build.json').write_text(json.dumps(frame_report,indent=2),encoding="utf8")
bpy.context.preferences.filepaths.save_version=0
scene['street_revision']='R24 build 11 city context and courtyard repairs'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'city_and_block_r24.blend'),compress=True)
print('STREET_FRAME_DONE',frame_report,flush=True)

