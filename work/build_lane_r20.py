"""Author the upper stair lane in the opened R19 assembled city. Blender XY metres."""
from pathlib import Path
import bpy, math, sys, json, hashlib, random
from mathutils import Vector
W=Path(__file__).resolve().parent
S=W/'scene_r20'; S.mkdir(exist_ok=True)
A=W/'project/chongqing_godot_v05/assets/lane_r20'; A.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'project/chongqing_blender_v05'))
import district_geometry as g
source=set(bpy.context.scene.objects)
kit=g.col('R20_Upper_stair_lane')
mats={};g.setup(mats);g.details=kit
for key,color,r,m in [
    ('steel',(.19,.20,.18),.45,.76),('iron',(.075,.066,.046),.84,.4),
    ('ochre',(.21,.142,.072),.82,.18),('wood',(.19,.115,.069),.89,0),
    ('jade',(.062,.11,.091),.8,.28),('twine',(.18,.16,.11),.88,0),
    ('cotton',(.66,.57,.40),.95,0),('indigo',(.115,.18,.22),.96,0),
    ('clay',(.24,.048,.028),.64,.45),('pin',(.45,.43,.33),.65,.35),
    ('brass',(.31,.21,.103),.41,.79),('oxide',(.099,.123,.083),.84,.25)]:
    mats[key]=g.solid('R20_'+key,color,r,m)
for key in ['enamel','notice','repair','basket']:
    mat=g.solid('R20_print_'+key,(1,1,1),.53 if key=='enamel' else .93)
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(S/'print_sources'/(key+'.png')))
    mat.node_tree.links.new(tex.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    mats[key]=mat
# Reuse the existing project scan at a physical scale on the noticeboard.
for suffix,socket in [('diff','Base Color'),('rough','Roughness')]:
    tex=mats['wood'].node_tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(W/'project/chongqing_godot_v05/assets'/('chongqing_district_wood_table_worn_'+suffix+'_2k.'+('jpg' if suffix=='diff' else 'png'))),check_existing=True)
    if suffix=='rough':tex.image.colorspace_settings.name='Non-Color'
    mats['wood'].node_tree.links.new(tex.outputs['Color'],mats['wood'].node_tree.nodes['Principled BSDF'].inputs[socket])
mats['wood']['uv_meters']=1.35
origin=Vector((-39.5608,40.9019,0));u=(Vector((-31.5071,55.1011,0))-origin).normalized()
v=Vector((u.y,-u.x,0));Z=Vector((0,0,1))
def pt(s,d,z):return origin+u*s+v*d+Z*z
def group(name):return g.Batch(name,kit,origin,u[:2],v[:2])
def rail_z(s):return 25.96+.149*s
mats['rail_enamel']=g.solid('R20_hand_worn_rail',(.196,.063,.036),.55,.39)
base=group('COL_R20_Returned_handrail')
start,end=1.2,15.75
base.pipe([(start,.006,rail_z(start)-.045),(start,.10,rail_z(start)-.045),(start+.055,.123,rail_z(start+.055)),(end-.055,.123,rail_z(end-.055)),(end,.10,rail_z(end)-.045),(end,.006,rail_z(end)-.045)],.022,'rail_enamel',24)
for s in [1.55,3.7,5.95,8.2,10.45,12.7,15.3]:
    z=rail_z(s)
    base.cylinder((s,-.005,z-.095),(s,.011,z-.095),.044,'iron',20)
    base.pipe([(s,.009,z-.095),(s,.108,z-.095),(s,.123,z-.063),(s,.123,z-.015)],.009,'steel',12)
    for ds in [-.027,.027]:
        base.cylinder((s+ds,.011,z-.095),(s+ds,.017,z-.095),.006,'pin',8)
base.finish()

# UVs follow page edges and still read correctly from either orientation.
def sheet(name,key,center,tangent,outward,width,height,curl=0,tilt=0):
    cols,rows=8,10
    t=Vector(tangent);normal=Vector(outward);coords=[];uvs=[];faces=[]
    for j in range(rows+1):
        for i in range(cols+1):
            a=i/cols;b=j/rows
            x=(a-.5)*width;z=(b-.5)*height
            loose=curl*((1-b)**3*(.3+.7*a*a)+.11*math.sin(a*math.tau*1.7)*(1-b))
            coords.append(center+t*(x*math.cos(tilt)-z*math.sin(tilt))+Z*(x*math.sin(tilt)+z*math.cos(tilt))+normal*loose)
            uvs.append((a,b))
    for j in range(rows):
        for i in range(cols):
            k=j*(cols+1)+i;faces.append((k,k+1,k+cols+2,k+cols+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(coords,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);kit.objects.link(ob);mesh.materials.append(mats[key])
    uv=mesh.uv_layers.new()
    for loop in mesh.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]

f=group('R20_Notice_case')
mid=9.05;z=28.02
for j in range(6):
    f.box((mid-.55+j*.22,.035,z),(.219,.07,.90),'wood')
for s in [mid-.66,mid+.66]:f.box((s,.06,z),(.035,.095,.94),'jade')
for zz in [z-.45,z+.45]:f.box((mid,.065,zz),(1.35,.09,.032),'jade')
f.quad((mid-.73,-.004,z+.51),(mid+.73,-.004,z+.51),(mid+.73,.175,z+.47),(mid-.73,.175,z+.47),'jade')
f.box((mid,.17,z+.455),(1.47,.018,.045),'jade')
for s,zz,key,w,h,tilt in [(mid-.391,z+.04,'notice',.44,.615,.043),(mid+.045,z+.065,'repair',.35,.51,-.052),(mid+.404,z-.05,'basket',.27,.38,.074)]:
    sheet('R20_Post_'+key,key,pt(s,.080,zz),u,v,w,h,.021,tilt)
    for dx in [-.33*w,.33*w]:
        f.cylinder((s+dx,.081,zz+h*.43+dx*tilt),(s+dx,.087,zz+h*.43+dx*tilt),.007,'pin',12)
f.finish(.003)
f=group('R20_Address')
f.box((6.98,.016,28.18),(.575,.032,.286),'iron')
sheet('R20_Enamel_address','enamel',pt(6.98,.034,28.18),u,v,.57,.28)
for ds in [-.265,.265]:
    for dz in [-.115,.115]:f.cylinder((6.98+ds,.034,28.18+dz),(6.98+ds,.039,28.18+dz),.005,'pin',10)
f.finish(.003)

# A projecting bamboo drying pole returns to two anchors in solid wall bays.
f=group('R20_Drying_rack')
for s in [9.53,13.05]:
    f.box((s,.014,31.55),(.10,.032,.24),'iron')
    f.pipe([(s,.014,31.46),(s,.66,31.72),(s,.04,31.72)],.015,'iron',12)
f.cylinder((9.32,.63,31.74),(13.24,.63,31.73),.022,'ochre',16,.018)
for s in [9.51,10.14,11.02,11.77,12.44,13.06]:
    f.cylinder((s-.009,.63,31.735),(s+.009,.63,31.735),.023,'twine',14)
f.finish()
def cloth(name,mid,width,length,kind):
    b=group(name)
    def xy(i,j):
        a=i/30-.5;t=j/24
        # Sleeve blocks widen a short-sleeved work shirt above the waist.
        span=width if kind=='cotton' else width*(.68+.32*(1-min(1,max(0,(t-.25)/.13))))
        neck=.10*math.exp(-(a/.15)**2) if kind=='indigo' else 0
        shoulder=.15*abs(a)*2 if kind=='indigo' else 0
        return (mid+a*span+.026*t*math.sin(t*2.8),
                .697+(.013+.037*t)*math.sin((a+.5)*15+t*.84)+.025*t*t,
                31.687-t*length-(neck+shoulder)*(1-t)+.025*math.sin(a*8)*t)
    points=[xy(i,j) for j in range(25) for i in range(31)]
    quads=[(j*31+i,j*31+i+1,(j+1)*31+i+1,(j+1)*31+i) for j in range(24) for i in range(30)]
    b.mesh(points,quads,kind,True)
    if kind=='indigo':
        back=[(x,.645-(y-.697)*.65,z+.014) for x,y,z in points]
        b.mesh(back,[tuple(reversed(q)) for q in quads],kind,True)
        for j in range(24):
            if j in (5,6,7):continue
            for c in (0,30):
                a=j*31+c;d=a+31
                b.quad(points[a],points[d],back[d],back[a],kind)
        for i in range(30):
            if 11<=i<=18:continue
            b.quad(points[i],points[i+1],back[i+1],back[i],kind)
    else:
        # Return over the rod, with a short free tail behind it.
        for i in range(30):
            a=points[i];d=points[i+1]
            top_a=(a[0],.634,31.759);top_d=(d[0],.634,31.759)
            b.quad(a,d,top_d,top_a,kind)
            b.quad(top_a,top_d,(d[0],.597,31.54),(a[0],.597,31.54),kind)
    for ob in b.finish():
        attr=ob.data.color_attributes.new(name='COLOR_0',type='FLOAT_COLOR',domain='CORNER')
        for lp in ob.data.loops:
            row,col=divmod(lp.vertex_index%(25*31),31)
            if kind=='cotton':
                factor=.5 if col in (2,3,26,27) or row in (21,22) else .95
                rgb=(factor*.92,factor*.95,factor)
            else:
                factor=.91+.07*math.sin(col*.61+row*.11)
                if row in (1,23) or (row<5 and col in (1,29)):factor*=.80
                rgb=(factor*.92,factor,factor)
            attr.data[lp.index].color=(*rgb,1)
        ob.data.color_attributes.active_color=attr
        ob.modifiers.new('Sewn hem thickness','SOLIDIFY').thickness=.002
    return xy
cloth('R20_Striped_hand_towel',10.36,.60,.72,'cotton')
cloth('R20_Work_shirt',11.99,.71,.77,'indigo')
f=group('R20_Laundry_fixings')
for s in (10.14,10.56):
    f.box((s,.645,31.715),(.02,.073,.084),'wood')
# Wire hanger follows both shoulders and hooks over the pole.
f.pipe([(11.68,.669,31.52),(11.99,.669,31.67),(12.30,.669,31.52),(11.68,.669,31.52)],.005,'steel',8)
f.pipe([(11.99,.666,31.68),(11.99,.665,31.75),(12.015,.639,31.775),(12.036,.609,31.75)],.005,'steel',8)
f.finish()
def walking_stones():
    # Derive the tread footprint and elevation from each pair of top triangles.
    # A chipped upper lip wraps the nose; the playable collision stays at the source level.
    from collections import defaultdict
    prng=random.Random(2096)
    stair=next(o for o in source if o.name=='COL_Walk_Narrow_upper_passage_step_concrete')
    mat=stair.data.materials[0].copy()
    mat.name='R20_Dressed_stone'
    mats['slab']=mat
    tops=defaultdict(set)
    for face in stair.data.polygons:
        if face.normal.z<.999:continue
        for j in face.vertices:
            p=stair.matrix_world@stair.data.vertices[j].co
            tops[round(p.z,3)].add((round(p.x,5),round(p.y,5)))
    stone=g.Batch('R20_Hand_laid_treads',kit)
    heights=[]
    for level,corners in sorted(tops.items()):
        if len(corners)!=4:continue
        points=[Vector((x,y,level)) for x,y in corners]
        near=sorted(points,key=lambda p:p.y)[:2];far=sorted(points,key=lambda p:p.y)[2:]
        near.sort(key=lambda p:p.x);far.sort(key=lambda p:p.x)
        # Order the corners by the true uphill axis, including the turn at the landing.
        travel=(sum(far,Vector())-sum(near,Vector())).normalized()
        if abs(travel.dot((near[1]-near[0]).normalized()))>.1:continue
        lengths=[0.,prng.uniform(.38,.65),1.] if len(heights)%4 else [0.,1.]
        for a,b in zip(lengths,lengths[1:]):
            ca=near[0].lerp(near[1],a+.004);cb=near[0].lerp(near[1],b-.004)
            da=far[0].lerp(far[1],a+.004);db=far[0].lerp(far[1],b-.004)
            side=(cb-ca).normalized()
            # Eighteen-millimetre overhang hides the old square edge in close views.
            ca-=travel*.018;cb-=travel*.018;da-=travel*.01;db-=travel*.01
            ring=[ca+travel*.017,ca+side*.018,ca.lerp(cb,.28)-travel*.002,
                  ca.lerp(cb,.59)+travel*prng.uniform(.001,.008),cb-side*.013,cb+travel*.021,db,da]
            lower=[q-Z*.087 for q in ring]
            upper=[q+Z*.006 for q in ring]
            stone.mesh(lower+upper,[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,8+(i+1)%8,8+i) for i in range(8)],'slab')
        heights.append(level)
    for ob in stone.finish(.003):
        attr=ob.data.color_attributes.new(name='COLOR_0',type='FLOAT_COLOR',domain='CORNER')
        for lp in ob.data.loops:
            block=lp.vertex_index//16
            tone=.67+.23*(.5+.5*math.sin(block*17.82))
            attr.data[lp.index].color=(tone,tone*.987,tone*.95,1.)
        ob.data.color_attributes.active_color=attr
    print('R20_TREAD_LEVELS',len(heights))
walking_stones()
# Resident's rinse tap and removable slotted cover. Fit the assembly to the
# opposite masonry face, whose direction differs from the handrail wall by 3.4 degrees.
rc=Vector((-27.2234,57.4066,0))
rt=(Vector((-35.3256,44.9366,0))-rc).normalized()
rv=Vector((rt.y,-rt.x,0))
center=pt(13.10,0,0)
mount=rc+rt*(center-rc).dot(rt)
wash=g.Batch('R20_Rinse_tap',kit,mount,rt[:2],rv[:2])
floor_point=mount+rv*.18
from mathutils.bvhtree import BVHTree
floor_verts=[];floor_faces=[]
for ob in source:
    if ob.type!='MESH' or not ob.name.startswith(('COL_Walk_','COL_Terrain_','COL_Street_')):continue
    off=len(floor_verts)
    floor_verts.extend(ob.matrix_world@p.co for p in ob.data.vertices)
    floor_faces.extend(tuple(off+i for i in face.vertices) for face in ob.data.polygons)
ground=BVHTree.FromPolygons(floor_verts,floor_faces)
def floor_z(p):
    return ground.ray_cast(p+Z*34,-Z,14)[0].z
gz=floor_z(floor_point)
wash.pipe([(-.48,-.012,gz+.32),(-.48,.054,gz+.32),(0,.054,gz+.32),(0,.054,gz+.90)],.018,'iron',16)
for s,h in [(-.32,.32),(0,.64)]:
    wash.box((s,.011,gz+h),(.084,.023,.026),'iron')
    wash.pipe([(s-.037,.02,gz+h),(s-.022,.059,gz+h),(s,.076,gz+h),(s+.022,.059,gz+h),(s+.037,.02,gz+h)],.004,'pin',10)
    for delta in [-.032,.032]:
        wash.cylinder((s+delta,.021,gz+h),(s+delta,.029,gz+h),.006,'steel',8)
for h,radius in [(.33,.024),(.83,.024),(.857,.023)]:
    wash.cylinder((0,.054,gz+h-.012),(0,.054,gz+h+.012),radius,'iron',12)
wash.cylinder((0,.054,gz+.864),(0,.054,gz+.89),.025,'brass',6)
# Continuous cast body follows a quarter-circle rather than intersecting tubes.
profile=[(.054,.879,.020),(.078,.879,.024),(.101,.879,.031),(.125,.879,.026),(.152,.879,.021)]
for i in range(1,13):
    a=i*math.pi/24
    profile.append((.152+.033*math.sin(a),.846+.033*math.cos(a),.021-.003*i/12))
profile.extend([(.185,.832,.018),(.185,.826,.020),(.185,.817,.020)])
rings=[];n=28
for j,(d,h,r) in enumerate(profile):
    low=profile[max(0,j-1)];high=profile[min(len(profile)-1,j+1)]
    dy,dz=high[0]-low[0],high[1]-low[1];l=math.hypot(dy,dz)
    for i in range(n):
        a=math.tau*i/n
        rings.append((r*math.cos(a),d+r*math.sin(a)*dz/l,gz+h-r*math.sin(a)*dy/l))
faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)]
wash.mesh(rings,faces,'brass',True)
wash.cylinder((0,.185,gz+.820),(0,.185,gz+.817),.014,'iron',24)
for h,r,seg in [(.907,.025,16),(.921,.021,6),(.932,.015,12)]:
    wash.cylinder((0,.115,gz+h-.009),(0,.115,gz+h+.006),r,'brass',seg)
wash.cylinder((0,.115,gz+.887),(0,.115,gz+.95),.011,'steel',12)
rim=[];faces=[]
for i in range(36):
    a=math.tau*i/36;r=.045+.004*math.cos(a*5)
    for j in range(10):
        b=math.tau*j/10
        rim.append(((r+.007*math.cos(b))*math.cos(a),.115+(r+.007*math.cos(b))*math.sin(a),gz+.95+.007*math.sin(b)))
        faces.append((10*i+j,10*((i+1)%36)+j,10*((i+1)%36)+(j+1)%10,10*i+(j+1)%10))
wash.mesh(rim,faces,'clay',True)
wash.cylinder((0,.115,gz+.944),(0,.115,gz+.961),.010,'pin',6)
for angle in [0,2.094,4.189]:
    wash.cylinder((0,.115,gz+.95),(.046*math.cos(angle),.115+.046*math.sin(angle),gz+.95),.005,'clay',8)
for ob in wash.finish(.001):
    tint=ob.data.color_attributes.new(name='COLOR_0',type='FLOAT_COLOR',domain='CORNER')
    for loop in ob.data.loops:
        p=ob.data.vertices[loop.vertex_index].co
        mottled=.79+.16*math.sin(p.x*172+p.z*82)*math.sin(p.y*151)
        patina=max(0,.45+.55*math.sin(p.z*93+p.y*46))
        tint.data[loop.index].color=(mottled*(1-.24*patina),mottled*(1-.04*patina),mottled,1.)
    ob.data.color_attributes.active_color=tint
grate=g.Batch('R20_Drain_cover',kit,mount,rt[:2],rv[:2])
def grate_pt(s,d,h):
    return (s,d,floor_z(mount+rt*s+rv*d)+h)
for a in range(10):
    s=-.185+a*.039
    grate.quad(grate_pt(s,.07,.006),grate_pt(s+.021,.07,.006),grate_pt(s+.021,.28,.006),grate_pt(s,.28,.006),'iron')
for d in [.057,.28]:
    grate.quad(grate_pt(-.20,d,.007),grate_pt(.196,d,.007),grate_pt(.196,d+.012,.007),grate_pt(-.20,d+.012,.007),'iron')
grate.finish()
print('R20_WASH_POINT',list(floor_point),gz)
spout=mount+rv*.185+Z*(gz+.817)
tap_source={'outlet':[spout.x,spout.z,-spout.y],'ground_y':gz,'outward':[rv.x,0,-rv.y]}
(A/'rinse_fixture.json').write_text(json.dumps(tap_source,indent=2),encoding='utf-8')
sys.path.insert(0,str(W))
from upper_court_seat_r20 import build as build_tree_seats
build_tree_seats(g,kit,floor_z,A)
new=set(bpy.context.scene.objects)-source
for ob in source:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(S/'upper_lane.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'upper_lane.glb'),export_format='GLB',export_apply=True,export_vertex_color='ACTIVE',export_lights=False,export_cameras=False)
print('R20_EXPORT',len(new),'objects')
