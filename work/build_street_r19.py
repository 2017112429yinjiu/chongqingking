"""R19 original shop/stair detail layer. Run with the unmodified R17 .blend open.
Export a standalone editable layer; never overwrite the R17 city or recovered files.
"""
from pathlib import Path
import bpy,sys,math,json,random,hashlib
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.noise import noise_vector
W=Path(__file__).resolve().parent; SRC=W/'project/chongqing_blender_v05'
OUT=W/'scene_r19'; OUT.mkdir(exist_ok=True)
P=W/'project/chongqing_godot_v05/assets/street_r19';P.mkdir(exist_ok=True)
sys.path.insert(0,str(SRC))
import district_geometry as geo
import scanned_assets as scans
rng=random.Random(1901)
original=set(bpy.context.scene.objects)
materials={}
for m in bpy.data.materials:
    if m.name.startswith('CQ03_PBR_'):materials[m.name[9:]]=m
    elif m.name.startswith('CQ03_'):materials.setdefault(m.name[5:],m)
materials['cloth']=bpy.data.materials['CQ04_Cloth_curtain_beige']
for key,col,rough,metal in [('sage',(.19,.24,.19),.86,0),('cream',(.58,.51,.37),.87,0),('iron',(.065,.072,.063),.7,.7),('zinc',(.32,.34,.32),.58,.72),('oxide',(.16,.075,.038),.96,.1),('sign_red19',(.24,.045,.027),.83,.0),('chalk19',(.76,.71,.57),.92,0),('ceramic19',(.58,.65,.62),.32,0),('chilli19',(.22,.025,.012),.55,0),('brick19',(.28,.14,.09),.98,0)]:
    materials[key]=geo.solid('R19_'+key,col,rough,metal)
geo.setup(materials)
kit=geo.col('R19_Street_life');geo.details=kit
verts=[];faces=[]
for o in original:
    if o.type!='MESH' or not o.name.startswith(('COL_Terrain_','COL_Walk_','COL_Street_')):continue
    n=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
    faces.extend(tuple(n+i for i in f.vertices) for f in o.data.polygons)
ground=BVHTree.FromPolygons(verts,faces)
def height(x,y):
    hit=ground.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
    if hit[0] is None:raise ValueError(('no_ground',x,y))
    return hit[0].z
records=[];hidden=['B_A01_noodle_details_curtain_beige','B_A01_noodle_details_faded_red','Type_梯坎小面']
def batch(name):return geo.Batch('R19_'+name,kit)
def label(body,p,size,mat='chalk19',bold=True):
    # Shop front faces Blender +Y: reading direction is world -X.
    return geo.lettering(body,p,(-1,0),(0,1),size,mat,'R19_Type_'+body,bold)
def proxy(name,lo,hi):
    b=batch('unused');b.name='COLH_R19_'+name
    b.box(tuple((lo[i]+hi[i])/2 for i in range(3)),tuple(hi[i]-lo[i] for i in range(3)),'iron');b.finish()
def scan(key,name,x,y,h,yaw=0,collider=True):
    z=height(x,y)
    objs=scans.make_prop(key,'R19_'+name,(x,y,z),height=h,yaw=yaw,collection=kit)
    bpy.context.view_layer.update()
    # Each lowest support vertex follows the actual R17 paving, avoiding
    # four legs hovering above a tilted ground plane. Upper body stays level.
    initial=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
    lowest=min(p.z for p in initial)
    # Scanned chairs can have four feet at subtly different source heights.
    # Fit each support separately rather than moving only the lowest point.
    def quadrant(p):return (int(p.x>x),int(p.y>y))
    supports={q:min(p.z for p in initial if quadrant(p)==q) for q in {(0,0),(0,1),(1,0),(1,1)}}
    for o in objs:
        o.data=o.data.copy()
        inv=o.matrix_world.inverted()
        for v in o.data.vertices:
            p=o.matrix_world@v.co
            base=supports[quadrant(p)]
            if p.z-base<.20:
                weight=max(0.,1.-max(0.,p.z-base-.025)/.175)
                p.z+=(height(p.x,p.y)+.002-base)*weight
                v.co=inv@p
    pts=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
    lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
    if collider:
        if key=='potted_plant_02':proxy(name,[x-.12,y-.12,z],[x+.12,y+.12,z+h*.34])
        else:proxy(name,lo,hi)
    contacts=[(p.z-height(p.x,p.y)) for p in pts if p.z<z+.035]
    foot_gaps=[min(p.z-height(p.x,p.y) for p in pts if quadrant(p)==q and p.z<z+.15) for q in supports]
    records.append({'name':name,'asset':key,'bounds_blender':[lo,hi],'support_gap_range_m':[min(contacts),max(contacts)] if contacts else None,'four_support_min_gaps_m':foot_gaps})
    return lo,hi
scans.setup(SRC)
# Sign: a restrained enamel fascia, actual folds, fixing bolts, edge paint loss.
b=batch('Sign');b.box((-24.29,-61.80,14.76),(6.30,.17,.82),'sign_red19')
for z in [14.36,15.16]:b.box((-24.29,-61.69,z),(6.34,.035,.025),'iron')
for x in [-27.4,-21.18]:b.box((x,-61.69,14.76),(.035,.035,.81),'iron')
for x in [-27.25,-24.29,-21.33]:
    for z in [14.46,15.06]:b.cylinder((x,-61.69,z),(x,-61.665,z),.017,'zinc',12)
for i in range(85):
    x=rng.uniform(-27.35,-21.23);z=rng.choice([14.39,15.13])+rng.uniform(-.018,.018)
    b.box((x,-61.679,z),(rng.uniform(.008,.045),.004,rng.uniform(.004,.016)),rng.choice(['oxide','zinc']))
b.finish(.004)
label('梯 坎 小 面',(-24.65,-61.655,14.80),.67)
label('现煮',(-21.77,-61.65,14.92),.16)
label('堂食 · 外带',(-21.77,-61.65,14.64),.115)
# New canvas canopy: curved panels, stitched folds and soft scalloped valance.
b=batch('Canvas_awning')
x0,x1=-26.925,-21.655;ny=14;nx=96
vs=[]
for j in range(ny+1):
    t=j/ny
    for i in range(nx+1):
        x=x0+(x1-x0)*i/nx
        z=14.16-.40*t-.09*math.sin(math.pi*t)+.009*math.sin(x*18)*t
        vs.append((x,-62.035+1.28*t,z))
fs=[]
for j in range(ny):
    for i in range(nx):
        a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
b.mesh(vs,fs,'cloth',True)
for i in range(nx):
    a=x0+(x1-x0)*i/nx;c=x0+(x1-x0)*(i+1)/nx
    za=13.76+.009*math.sin(a*18);zc=13.76+.009*math.sin(c*18)
    za2=za-.14-.027*(.5+.5*math.cos(a*14));zc2=zc-.14-.027*(.5+.5*math.cos(c*14))
    b.quad((c,-60.752,zc),(a,-60.752,za),(a,-60.735,za2),(c,-60.735,zc2),'cloth')
objs=b.finish()
for o in objs:
    attr=o.data.color_attributes.new(name='COLOR_0',type='FLOAT_COLOR',domain='CORNER')
    for l in o.data.loops:
        p=o.data.vertices[l.vertex_index].co
        stripe=int((p.x-x0)/.34)%2
        factor=.87+.06*math.sin(p.x*5.7)*math.sin(p.y*13)
        dirt=1.-.20*max(0.,(p.y+61.1)/.37)
        c=(.63,.66,.49) if stripe else (.91,.84,.65)
        attr.data[l.index].color=(*(v*factor*dirt for v in c),1.)
    o.data.color_attributes.active_color=attr
    o.modifiers.new('Two millimetre canvas','SOLIDIFY').thickness=.002
# A fascia task light is attached under the supported canopy, not a floating fill.
b=batch('Fixtures')
b.box((-24.2,-61.5,13.78),(1.28,.09,.075),'zinc')
b.box((-24.2,-61.49,13.734),(1.14,.055,.016),'light_warm')
for x in [-24.65,-23.75]:b.box((x,-61.5,13.85),(.025,.055,.10),'iron')
# Cooker duct follows the shop wall and terminates above the eaves.
xx=-20.50;yy=-61.64
b.pipe([(-22.1,-62.45,14.05),(-22.1,yy,14.05),(xx-.20,yy,14.05)]+[(xx-.20+.20*math.sin(i*math.pi/16),yy,14.25-.20*math.cos(i*math.pi/16)) for i in range(1,9)]+[(xx,yy,18.85)],.10,'zinc',24)
for z in [14.6,16.,17.5,18.25]:
    b.box((xx,-61.84,z),(.34,.28,.035),'iron')
    b.cylinder((xx,yy,z-.025),(xx,yy,z+.025),.11,'iron',24)
b.cylinder((xx,yy,18.84),(xx,yy,18.92),.17,'zinc',24,.10)
for x in [-22.06,-26.4]:
    b.pipe([(x,-61.985,13.98),(x,-61.72,14.22),(x+.12,-61.72,14.35)],.009,'iron',8)
# Facade-mounted low voltage service conduit, explicit clips every 0.8 m.
points=[(-32.7+i*.25,-61.95,15.35-.025*math.sin(i*.25*3)) for i in range(51)]
b.pipe(points,.014,'iron',8)
for x in [-32.6+i*.8 for i in range(16)]:b.box((x,-61.952,15.35),(.035,.055,.06),'zinc')
b.finish(.002)
# Two seats by the closed neighbouring shutter, outside the 4.5 m serving opening.
table=scan('chinese_tea_table','Breakfast_table',-30.35,-60.75,.72,yaw=.04)
scan('plastic_monobloc_chair_01','Breakfast_chair_A',-31.45,-60.50,.80,yaw=-1.39)
scan('plastic_monobloc_chair_01','Breakfast_chair_B',-29.25,-60.55,.80,yaw=1.71)
scan('potted_plant_02','Resident_pot_A',-32.35,-61.35,.72,yaw=.6)
scan('potted_plant_02','Resident_pot_B',-32.80,-61.35,.46,yaw=2.7)
# Move the inherited waste group out of the breakfast/serving area and into
# the side service gap. Exact source objects are hidden by the layer manifest.
for part in ['bin','bagA','bagB','crate']:
    sources=[o for o in original if o.name.startswith('Resident_waste_14_'+part+'_')]
    copies=[]
    for source in sources:
        ob=source.copy();ob.data=source.data;ob.name='R19_Service_'+source.name
        kit.objects.link(ob);ob.location+=Vector((-6.95,-3.7,0));copies.append(ob);hidden.append(source.name)
    bpy.context.view_layer.update()
    ps=[o.matrix_world@v.co for o in copies for v in o.data.vertices]
    low=min(p.z for p in ps);cx=sum(p.x for p in ps)/len(ps);cy=sum(p.y for p in ps)/len(ps)
    dz=height(cx,cy)-low+.003
    for ob in copies:ob.location.z+=dz
    bpy.context.view_layer.update()
# Table objects make the group legible as a breakfast place; dish profile has a rim.
top=table[1][2];b=batch('Breakfast_crockery')
def bowl(cx,cy,z,r):
    profile=[(r*.52,z),(r*.55,z+.025),(r*.98,z+.085),(r,z+.094),(r*.90,z+.094),(r*.49,z+.04)]
    v=[]
    for rr,zz in profile:
        v.extend((cx+rr*math.cos(t*math.tau/32),cy+rr*math.sin(t*math.tau/32),zz) for t in range(32))
    f=[]
    for j in range(len(profile)-1):
        for k in range(32):a=j*32+k;n=j*32+(k+1)%32;f.append((a,n,n+32,a+32))
    b.mesh(v,f,'ceramic19',True)
bowl(-30.55,-60.75,top+.003,.115)
bowl(-30.15,-60.75,top+.003,.09)
for x in [-30.64,-30.615]:b.cylinder((x,-60.85,top+.11),(x+.04,-60.55,top+.11),.004,'timber',10)
b.cylinder((-30.25,-60.95,top),(-30.25,-60.95,top+.14),.038,'ceramic19',24)
b.cylinder((-30.25,-60.95,top+.142),(-30.25,-60.95,top+.15),.04,'iron',24)
b.finish(.001)
# A folded household towel over the actual existing cage lower rail (z16.05).
b=batch('Window_towel')
for i in range(18):
    for j in range(14):
        def towel(u,v):return (-24.82+u*.53+.025*math.sin(v*3)*(u-.5),-61.47+(.014+.031*v)*math.sin(u*math.pi*6.7+.6*v*v)+.055*v*v,16.06-v*(.58+.025*math.cos(u*math.pi*3)))
        b.quad(towel(i/18,j/14),towel((i+1)/18,j/14),towel((i+1)/18,(j+1)/14),towel(i/18,(j+1)/14),'cloth')
for x in [-24.76,-24.35]:b.box((x,-61.46,16.068),(.018,.05,.055),'timber')
for i in range(18):
    a=-24.82+i*.53/18;c=a+.53/18
    b.quad((a,-61.49,16.06),(c,-61.49,16.06),(c,-61.55,15.94),(a,-61.55,15.94),'cloth')
b.finish()
# Local plaster repairs/visible brick live beside openings, not over windows.
b=batch('Wall_repairs')
for x,z,w,h in [(-32.78,12.15,.32,.65),(-27.62,12.55,.27,.46),(-20.18,14.05,.23,.75)]:
    outline=[]
    for k in range(18):
        t=k*math.tau/18;r=rng.uniform(.72,1.)
        outline.append((x+w*.5*math.cos(t)*r,-61.982,z+h*.5*math.sin(t)*r))
    b.mesh(outline,[tuple(reversed(range(18)))],'concrete')
b.finish(.004)
# Drain grates sit flush with current paving; no new step at the entrance.
b=batch('Drains')
for x in [-32.1,-28.4,-20.85]:
    y=-60.1;z=height(x,y)+.007
    b.box((x,y,z),(.52,.30,.012),'iron')
    for i in range(11):b.box((x-.24+i*.048,y,z+.008),(.014,.28,.014),'zinc')
b.finish(.002)
# Match existing stair tread tops; the scan's metre-scale stone surface and
# narrow per-slab joints break the long uniform concrete run without changing rise.
b=batch('Stair_tread_caps');nsteps=0;tops=defaultdict(list)
for o in original:
    if not o.name.startswith('COL_Walk_Central_stair_lane_step_concrete'):continue
    for f in o.data.polygons:
        if f.normal.z<.99:continue
        pts=[o.matrix_world@o.data.vertices[i].co for i in f.vertices]
        c=sum(pts,Vector())/len(pts)
        if not (-52<c.y<-30 and -23<c.x<-16):continue
        tops[round(c.z,4)].extend(pts)
for z,pts in sorted(tops.items()):
    x0=min(p.x for p in pts);x1=max(p.x for p in pts);y0=min(p.y for p in pts);y1=max(p.y for p in pts)
    if x1-x0>4.1 or y1-y0>2.5:continue
    nsteps+=1
    count=6
    for j in range(count):
        lo=x0+(x1-x0)*j/count+.004;hi=x0+(x1-x0)*(j+1)/count-.004
        b.box(((lo+hi)/2,(y0+y1)/2,z+.002),(hi-lo,y1-y0-.006,.008),'step_concrete')
caps=b.finish(.0025)
for ob in caps:
    attr=ob.data.color_attributes.new(name='COLOR_0',type='FLOAT_COLOR',domain='CORNER')
    for face in ob.data.polygons:
        c=face.center;factor=.86+.14*(.5+.5*math.sin(math.floor(c.x/.63)*17+math.floor(c.y*.9)*11))
        for index in face.loop_indices:attr.data[index].color=(factor,factor,factor,1)
    ob.data.color_attributes.active_color=attr
# Low masonry edging holds the stair lane within the slope. It stays beyond
# the public walking width; both ends and the route junctions remain open.
b=geo.Batch('COL_R19_Stair_retaining',kit)
for x in [-22.23,-17.77]:
    for i in range(31):
        y=-49.8+i*.56;lo=height(x,y-.275);hi=height(x,y+.275)
        # Individually level laid stones, narrow joints, softened arrises.
        z=max(lo,hi)
        b.box((x,y,(min(lo,hi)+z+.19)/2),(.25,.546,z+.19-min(lo,hi)),'stone')
        b.box((x,y,z+.205),(.29,.55,.05),'concrete')
b.finish(.009)
scan('potted_plant_02','Stair_resident_pot_A',-23.3,-43.2,.92,yaw=1.7)
scan('potted_plant_02','Stair_resident_pot_B',-23.72,-43.4,.61,yaw=3.)
# Replace the two faceted background silhouette walls with continuous
# terrain relief outside the 200m playable district. Authored context only.
hidden+=['Authored_distant_hill_ridges_hill_near','Authored_distant_hill_ridges_hill_far']
materials['distant19']=geo.solid('R19_distant_terrain',(.20,.25,.23),1.,0)
b=batch('Distant_relief');v=[];f=[];rings=42;segments=256
for j in range(rings+1):
    r=260.+j*39.
    for i in range(segments):
        angle=i*math.tau/segments;x=r*math.cos(angle);y=r*math.sin(angle)
        n=noise_vector(Vector((x*.0027,y*.0027,4.7)))[0]
        small=noise_vector(Vector((x*.010,y*.010,11.8)))[1]
        hill1=math.exp(-((r-800.)/290.)**2)
        hill2=math.exp(-((r-1510.)/290.)**2)
        z=-38.+hill1*(120.+65.*n+13.*small)+hill2*(200.+85.*n+18.*small)
        v.append((x,y,z))
for j in range(rings):
    for i in range(segments):
        a=j*segments+i;c=j*segments+(i+1)%segments
        f.append((a,c,c+segments,a+segments))
b.mesh(v,f,'distant19',True)
for ob in b.finish():
    attr=ob.data.color_attributes.new(name='COLOR_0',type='FLOAT_COLOR',domain='CORNER')
    for l in ob.data.loops:
        p=ob.data.vertices[l.vertex_index].co
        shade=.78+.18*noise_vector(Vector((p.x*.013,p.y*.013,2.)))[2]
        attr.data[l.index].color=(shade,shade*1.03,shade*.99,1.)
    ob.data.color_attributes.active_color=attr
new=set(bpy.context.scene.objects)-original
report={'revision':'R19_scene_05','coordinate_system':'Blender Z up; Godot [x,z,-y]','hide_city_objects':hidden,'grounded_props':records,'stair_treads_capped':nsteps,'source_city':'work/r17_scene/chongqing_district.blend','source_city_sha256':hashlib.sha256((W/'project/chongqing_godot_v05/assets/chongqing_district.glb').read_bytes()).hexdigest(),'practical_lights':[{'position':[-24.2,13.68,61.49],'color':[1.,.86,.65],'energy':.40,'range':2.7}],'notes':['Original R19 geometry and placement; CC0 scans reused from existing prepared library.','New layer is not a surveyed reconstruction. Real photographs used for visual observation only.','Table/chair support vertices fit the actual R17 collision ground. Leaf canopy bounds are not rigid collision volumes.']}
for o in original:bpy.data.objects.remove(o,do_unlink=True)
# Prevent exporting unused unlinked scan templates, cameras, or old city materials.
bpy.ops.object.select_all(action='DESELECT')
for o in new:o.select_set(True)
bpy.context.view_layer.objects.active=next(iter(new))
for o in new:
    if o.name.startswith('COLH_'):o.hide_render=True
# Only referenced images are packed; clean unused original datablocks first.
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'street_life.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(P/'street_life.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_yup=True,export_vertex_color='ACTIVE')
report['objects']=len(new);report['glb_sha256']=hashlib.sha256((P/'street_life.glb').read_bytes()).hexdigest()
report['blend_sha256']=hashlib.sha256((OUT/'street_life.blend').read_bytes()).hexdigest()
(P/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'build_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('R19_BUILT',len(new),'objects',nsteps,'treads',report['glb_sha256'])
