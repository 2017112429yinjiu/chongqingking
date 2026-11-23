"""Cut the distant authored terrain to the mapped river and fit a visual crossing."""
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
import hashlib,json,math,random,sys
import numpy as np

W=Path(__file__).resolve().parent; S=W/'scene_r22'; P=W/'project/chongqing_godot_v05'
A=P/'assets/river_r22';A.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'project/chongqing_blender_v05'))
import district_geometry as geo
plan=json.loads((P/'source_data/river_r22/river_plan.json').read_text(encoding='utf8'))
field=np.load(S/'river_fields.npy').astype(np.float32)/255.
minx,miny,maxx,maxy=plan['bounds'];water_z=-16.
city=bpy.context.scene
kit=bpy.data.collections.new('R22_River_context');city.collection.children.link(kit)
colors={'river':(.102,.170,.158,.43,.08),'abutment':(.25,.242,.216,.88,0),'girder':(.252,.258,.245,.87,.03),
        'fascia':(.273,.218,.174,.86,.05),'road':(.113,.121,.119,.89,0),'rail':(.31,.306,.263,.82,.12),
        'shadow':(.126,.146,.139,.83,0),'roof':(.25,.235,.210,.91,0),'window':(.12,.17,.173,.61,.22),
        'wall0':(.414,.394,.344,.89,0),'wall1':(.332,.351,.337,.88,0),'wall2':(.391,.31,.25,.91,0),
        'bus_green':(.175,.329,.281,.68,.12),'bus_cream':(.65,.57,.39,.71,.12),'bus_red':(.445,.218,.146,.71,.12),
        'glass':(.088,.14,.15,.37,.32),'tyre':(.052,.053,.050,.88,0),'steel':(.317,.321,.301,.52,.49)}
mats={k:geo.solid('R22_river_'+k,v[:3],v[3],v[4]) for k,v in colors.items()}
geo.setup(mats)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)))
    return t*t*(3.-2.*t)
def sample(x,y):
    u=(x-minx)*.5;v=(y-miny)*.5
    if u<0 or v<0 or u>=field.shape[1]-1 or v>=field.shape[0]-1:return (0.,0.,0.,0.)
    i,j=int(u),int(v);u-=i;v-=j
    return (field[j,i]*(1-u)+field[j,i+1]*u)*(1-v)+(field[j+1,i]*(1-u)+field[j+1,i+1]*u)*v
def river_height(x,y,z):
    a,b,c,broad=sample(x,y);influence=smooth(355,425,math.hypot(x,y))
    if not influence:return z
    wet=smooth(.075,.55,float(b))
    bank=min(z,water_z+4.2+140.*(1.-smooth(.025,.49,float(broad))))
    bed=bank+(water_z-5.3-bank)*wet
    # A separate, uniformly sampled shoal follows the mapped island. Excavate
    # the inherited long triangles under it so they cannot show through.
    bed+=(water_z-5.3-bed)*smooth(.004,.32,float(c))
    return z+(bed-z)*influence

terrain=[];geometry={}
for label,suffix in [('Outer_ground_context_ground_dirt','Outer'),('R19_Distant_relief_distant19','Relief')]:
    old=bpy.data.objects[label];m=old.data
    original=[tuple(old.matrix_world@v.co) for v in m.vertices]
    m.calc_loop_triangles()
    original_faces=[tuple(p.vertices) for p in m.loop_triangles]
    terrain.append(BVHTree.FromPolygons(original,original_faces,all_triangles=True))
    vv=[];ff=[];lookup={};smoothing=[]
    def index(p):
        key=tuple(round(c,4) for c in p)
        if key not in lookup:
            dz=river_height(*p)
            if suffix=='Relief' and abs(dz-p[2])>.2:
                dz-=.60*smooth(355,425,math.hypot(p[0],p[1]))
            lookup[key]=len(vv);vv.append((p[0],p[1],dz))
        return lookup[key]
    def split(a,b,c,smooth_face,level=0):
        pts=[a,b,c]
        # The same midpoint rule on shared edges preserves the terrain seam.
        candidates=[]
        for i in range(3):
            q,r=pts[i],pts[(i+1)%3];d=(q[0]-r[0])**2+(q[1]-r[1])**2
            if d<7.5**2:continue
            mid=tuple((q[k]+r[k])*.5 for k in range(3))
            if mid[1]>180 or math.hypot(mid[0],mid[1])<295:continue
            if not (minx<mid[0]<maxx and miny<mid[1]<maxy):continue
            f=sample(*mid[:2]);edge=(.01<float(f[1])<.99 or .01<float(f[2])<.99)
            if edge or d>54**2:candidates.append((d,i,mid))
        if candidates and level<12:
            _,i,mid=max(candidates,key=lambda t:t[0])
            split(pts[i],mid,pts[(i+2)%3],smooth_face,level+1)
            split(mid,pts[(i+1)%3],pts[(i+2)%3],smooth_face,level+1)
        else:
            ix=tuple(index(p) for p in pts)
            if len(set(ix))==3:ff.append(ix);smoothing.append(smooth_face)
    for tri in m.loop_triangles:
        verts=[original[i] for i in tri.vertices]
        # The inherited distant relief used a two-sided material and every
        # triangle faced down. Orient the topography consistently for export.
        a,b,c=verts
        if (b[0]-a[0])*(c[1]-a[1]) < (b[1]-a[1])*(c[0]-a[0]):
            verts[1],verts[2]=verts[2],verts[1]
        split(*verts,m.polygons[tri.polygon_index].use_smooth)
    name='R22_Bank_'+suffix
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vv,[],ff);mesh.update()
    ob=bpy.data.objects.new(name,mesh);kit.objects.link(ob);mesh.materials.append(old.data.materials[0])
    uv=mesh.uv_layers.new(name='Metres')
    for f,sm in zip(mesh.polygons,smoothing):
        f.use_smooth=sm
        for k in f.loop_indices:
            p=vv[mesh.loops[k].vertex_index];uv.data[k].uv=(p[0]/4.3,p[1]/4.3)
    # Full editable city contains both, with only the replacement visible.
    old.hide_render=True;old.hide_viewport=True
    geometry[label]={'replacement':name,'triangles':len(ff),'vertices':len(vv)}
def ground(x,y):
    zs=[]
    for tree in terrain:
        p=tree.ray_cast(Vector((x,y,550)),Vector((0,0,-1)),950)[0]
        if p:zs.append(p.z)
    if not zs:return None
    return river_height(x,y,max(zs))

# The clipped sheet follows the mapped outer ring and inner island. Interpolate
# the binary-mask boundary on each triangle, rather than filling a rectangle.
wb=geo.Batch('R22_Water_sheet',kit)
step=14
def cellpt(x,y):
    # Water under the boundary of the editable 200 m city stays outside
    # the playable terrain. Its inner edge sits under the preserved outer ground.
    # Bury a narrow margin under the banks. The intersection with the
    # surveyed terrain defines the visible waterline, not the 14 m cell grid.
    _,water_edge,island,_=sample(x,y)
    return (x,y,max(float(water_edge),float(island))-.14 if math.hypot(x,y)>340 else -.50)
def water_tri(points):
    out=[]
    for a,b in zip(points,points[1:]+points[:1]):
        if (a[2]>0)!=(b[2]>0):
            t=a[2]/(a[2]-b[2]);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),water_z))
        if b[2]>0:out.append((b[0],b[1],water_z))
    if len(out)>2:wb.mesh(out,[tuple(range(len(out)))],'river')
for y in range(int(miny),int(maxy)-step,step):
    for x in range(int(minx),int(maxx)-step,step):
        q=[cellpt(x,y),cellpt(x+step,y),cellpt(x+step,y+step),cellpt(x,y+step)]
        water_tri(q[:3]);water_tri([q[0],q[2],q[3]])
wb.finish()

# The original terrain triangles are elongated along the basin. An independent
# five-metre grid resolves the narrow wet margin in both horizontal directions.
island_ring=next(row['points'] for row in plan['rings'] if row['role']=='inner')
island_v=[];island_f=[];island_index={}
def sand_vertex(x,y):
    key=(x,y)
    if key not in island_index:
        field_value=float(sample(x,y)[2])
        variation=.36*math.sin(x*.021+y*.017)+.16*math.sin(y*.060-x*.022)
        z=water_z-3.1+(6.2+variation)*field_value
        island_index[key]=len(island_v);island_v.append((x,y,z))
    return island_index[key]
for y in range(math.floor(min(p[1] for p in island_ring))-20,math.ceil(max(p[1] for p in island_ring))+20,5):
    for x in range(math.floor(min(p[0] for p in island_ring))-20,math.ceil(max(p[0] for p in island_ring))+20,5):
        if sample(x+2.5,y+2.5)[2]<.025:continue
        island_f.append(tuple(sand_vertex(xx,yy) for xx,yy in [(x,y),(x+5,y),(x+5,y+5),(x,y+5)]))
mesh=bpy.data.meshes.new('R22_Sandbar');mesh.from_pydata(island_v,[],island_f);mesh.update()
island=bpy.data.objects.new(mesh.name,mesh);kit.objects.link(island)
mesh.materials.append(geo.solid('R22 Silt and sand',(.32,.27,.18),.9,0))
for poly in mesh.polygons:poly.use_smooth=True

axes=[];bridge=geo.Batch('R22_Distant_crossing',kit)
for idx,way in enumerate(plan['axes']):
    ends=sorted([Vector(way['points'][0]),Vector(way['points'][-1])],key=lambda p:-p.y)
    a,b=ends;length=(b-a).length;along=(b-a).normalized();across=Vector((-along.y,along.x))
    gz=[ground(*q) for q in ends];assert all(z is not None for z in gz),gz
    approaches=[ground(*(a-along*54)),ground(*(b+along*54))]
    start_z=max(gz[0]+1.1,approaches[0]+.35);end_z=max(gz[1]+1.1,approaches[1]+.35)
    width=15 if idx==0 else 18
    def pt(s,w,z):
        q=a+along*s+across*w
        return (q.x,q.y,z)
    def deck(s):
        t=max(0,min(1,s/length))
        return start_z+(end_z-start_z)*t+2.1*math.sin(math.pi*t)
    def pier_depth(s):
        return 3.45+3.6*(.5+.5*math.cos(2*math.pi*s/(length/7)))**3.1
    for j in range(140):
        start=length*j/140;end=length*(j+1)/140
        z1,z2=deck(start),deck(end);h1,h2=pier_depth(start),pier_depth(end)
        w=width/2
        bridge.quad(pt(start,-w,z1),pt(end,-w,z2),pt(end,w,z2),pt(start,w,z1),'road')
        for sign in [-1,1]:
            ws=sign*w
            bridge.quad(pt(start,ws,z1+.83),pt(end,ws,z2+.83),pt(end,ws,z2-.36),pt(start,ws,z1-.36),'rail')
            bridge.quad(pt(start,ws,z1-.36),pt(end,ws,z2-.36),pt(end,ws-sign*.33,z2-1.55),pt(start,ws-sign*.33,z1-1.55),'fascia')
            bridge.quad(pt(start,ws-sign*.33,z1-1.55),pt(end,ws-sign*.33,z2-1.55),pt(end,ws*.58,z2-h2),pt(start,ws*.58,z1-h1),'girder')
        bridge.quad(pt(start,-w*.58,z1-h1),pt(start,w*.58,z1-h1),pt(end,w*.58,z2-h2),pt(end,-w*.58,z2-h2),'shadow')
    # Generalised background silhouette, fitted to the game's authored heights.
    for j in range(8):
        s=length*j/7;q=pt(s,0,0);foot=ground(q[0],q[1]);foot=water_z-4 if foot is None else min(foot,deck(s)-4)
        top=deck(s)-pier_depth(s)+.15
        for lateral in [-2.9,2.9]:
            bridge.cylinder(pt(s,lateral,foot-.25),pt(s,lateral,top),1.95,'girder',8,2.55)
        bridge.cylinder(pt(s,-width*.35,top-.42),pt(s,width*.35,top-.42),1.66,'girder',8)
    # At each end an opaque sloped approach meets the underlying game terrain.
    for s,sgn in [(0,-1),(length,1)]:
        end=s+sgn*54;q=pt(end,0,0);land=ground(q[0],q[1])
        if land is None:continue
        for e,f in [(s,end)]:
            bridge.quad(pt(e,-width/2,deck(s)),pt(f,-width/2,land+.15),pt(f,width/2,land+.15),pt(e,width/2,deck(s)),'road')
            for side in [-1,1]:
                p0=pt(s,width*.5*side,deck(s));p1=pt(end,width*.5*side,land+.15)
                bridge.quad(p0,p1,(*p1[:2],land-1),(*p0[:2],min(gz)-3),'abutment')
    axes.append({'osm_id':way['id'],'north':[a.x,start_z,-a.y],'south':[b.x,end_z,-b.y],
                 'length':length,'deck_crown_m':2.1,'game_terrain_at_ends':gz})
bridge.finish()

rng=random.Random(89917);blocks=geo.Batch('R22_Opposite_bank',kit);buildings=[]
for rec in plan['buildings']:
    polygon=[Vector(p) for p in rec['points']]
    center=sum(polygon,Vector((0,0)))/len(polygon)
    if sample(*center)[0]>.5:continue
    heights=[ground(*p) for p in polygon]
    if any(z is None for z in heights):continue
    base=max(heights)+.06
    try:levels=int(float(rec['levels_tag'])) if rec['levels_tag'] else None
    except ValueError:levels=None
    if levels is None:levels=max(3,min(18,round(math.sqrt(rec['area'])/3.8)+rng.randint(-2,3)))
    try:height=float(rec['height_tag']) if rec['height_tag'] else levels*3.05
    except ValueError:height=levels*3.05
    top=base+height;wall=rng.choice(['wall0','wall1','wall2'])
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        length=(b-a).length
        if length<.2:continue
        t=(b-a).normalized();n=Vector((t.y,-t.x))
        if (a-center).dot(n)<0:n=-n
        blocks.quad((*a,min(heights)-.3),(*b,min(heights)-.3),(*b,top),(*a,top),wall)
        if length<5:continue
        bays=max(1,round(length/4.4))
        for f in range(levels):
            low=base+(f+.30)*height/levels;high=low+height/levels*.45
            for bay in range(bays):
                p=a+t*((bay+.20)*length/bays)+n*.08;q=a+t*((bay+.76)*length/bays)+n*.08
                blocks.quad((*p,low),(*q,low),(*q,high),(*p,high),'window')
    coords=[Vector((p.x,p.y,top)) for p in polygon]
    for tri in tessellate_polygon([coords]):blocks.mesh([coords[k] for k in tri],[(0,1,2)],'roof')
    buildings.append({'osm_id':rec['osm_id'],'levels':levels,'height':height,'base':base,'tagged_vertical':bool(rec['height_tag'] or rec['levels_tag'])})
blocks.finish()

# At river distances a fixed photographed tree elevation faces the playable
# district. Each surface shares the existing licensed four-view canopy atlas.
foliage=bpy.data.materials.new('R22 Distant riparian crowns');foliage.use_nodes=True
nt=foliage.node_tree;bs=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexImage')
tex.image=bpy.data.images.load(str(P/'assets/district_r21/canopy_atlas.png'),check_existing=True)
nt.links.new(tex.outputs['Color'],bs.inputs['Base Color']);nt.links.new(tex.outputs['Alpha'],bs.inputs['Alpha'])
bs.inputs['Roughness'].default_value=.95
piv=json.loads((P/'assets/district_r21/layout.json').read_text(encoding='utf8'))['canopy_pivots']
blocks_xy=[(min(q[0] for q in r['points'])-3,min(q[1] for q in r['points'])-3,
            max(q[0] for q in r['points'])+3,max(q[1] for q in r['points'])+3) for r in plan['buildings']]
forest=[];locations=set();rng=random.Random(2203)
for i in range(3400):
    x=rng.uniform(-1430.,750);y=rng.uniform(-1490.,97)
    radius=math.hypot(x,y)
    if not 380<radius<1480:continue
    wet,edge,island,broad=sample(x,y)
    if wet>.18 or island>.02 or edge>.23 or not .012<broad<.48:continue
    for j in range(rng.randint(6,17)):
        xx=x+rng.gauss(0,16.);yy=y+rng.gauss(0,12.);wet,edge,island,_=sample(xx,yy)
        if wet>.18 or island>.04 or edge>.22 or math.hypot(xx,yy)<375:continue
        cell=(round(xx/5),round(yy/5))
        if cell in locations or any(l<xx<r and lo<yy<hi for l,lo,r,hi in blocks_xy):continue
        if any(abs((Vector((xx,yy))-Vector((ax['north'][0],-ax['north'][2]))).cross(
            Vector((ax['south'][0]-ax['north'][0],ax['north'][2]-ax['south'][2])).normalized()))<16 for ax in axes):continue
        z=ground(xx,yy)
        if z is None or z<water_z+1:continue
        locations.add(cell);forest.append((xx,yy,z,rng.uniform(4.3,10.7),rng.randrange(2),rng.randrange(4)))
forest_verts=[];forest_faces=[];forest_uv=[]
for x,y,z,height,kind,col in forest:
    width=height*piv[['tree_small_02','island_tree_01'][kind]]['frame_width_over_height']
    right=Vector((-y,x,0)).normalized()*width*.5
    center=Vector((x,y,z-.19+width*.48));up=Vector((0,0,width*.5))
    ix=len(forest_verts);forest_verts.extend([center-right-up,center+right-up,center+right+up,center-right+up])
    forest_faces.append((ix,ix+1,ix+2,ix+3));v=.5 if kind==0 else 0.
    forest_uv.extend([(col/4,v),((col+1)/4,v),((col+1)/4,v+.5),(col/4,v+.5)])
mesh=bpy.data.meshes.new('R22_Riparian_groves');mesh.from_pydata(forest_verts,[],forest_faces);mesh.update()
obj=bpy.data.objects.new(mesh.name,mesh);kit.objects.link(obj);mesh.materials.append(foliage);uv=mesh.uv_layers.new(name='Photographed sides')
for loop in mesh.loops:uv.data[loop.index].uv=forest_uv[loop.vertex_index]

fleet=[]
for i,kind in enumerate(['bus','van','car','bus','car','van']):
    vehicle=geo.Batch('R22_Traffic_'+str(i),kit)
    size={'bus':(2.5,10.3,2.80),'van':(2.05,4.85,2.12),'car':(1.85,4.5,1.38)}[kind];w,l,h=size
    color=['bus_green','bus_cream','bus_red'][i%3]
    vehicle.box((0,0,h*.56),(w,l,h*.85),color)
    vehicle.box((0,.04,h*.76),(w+.024,l*.91,h*.32),'glass')
    for y in [-l*.43,l*.43]+([0,-l*.20,l*.20] if kind=='bus' else []):
        vehicle.box((0,y,h*.76),(w+.038,.12,h*.34),color)
    for y in [-l*.31,l*.31]:
        vehicle.cylinder((-w*.514,y,.38),(w*.514,y,.38),.39,'tyre',14)
    # Godot interprets "vehicle" in imported object names as a physics hint.
    # These six far actors are ordinary transform nodes.
    node=bpy.data.objects.new('R22_TransitActor_'+chr(65+i),None);kit.objects.link(node)
    for ob in vehicle.finish():ob.parent=node
    phase=[.2,.55,.82,.32,.62,.92][i];ax=axes[i%2]
    start=np.array(ax['north']);end=np.array(ax['south']);f=phase if i%2==0 else 1-phase
    pos=start*(1-f)+end*f;pos[1]+=2.1*math.sin(math.pi*f)
    node.location=(pos[0],-pos[2],pos[1]);d=end-start
    node.rotation_euler.z=math.atan2(-d[0],-d[2])+(math.pi if i%2 else 0)
    fleet.append({'node':node.name,'axis':i%2,'reverse':bool(i%2),'phase':phase,'speed_m_s':[9.8,11.3,13.3,10.2,12.5,11.0][i],'kind':kind})

bpy.context.preferences.filepaths.save_version=0
bpy.ops.file.pack_all()
scene=bpy.data.scenes.new('R22 River context');scene.collection.children.link(kit)
bpy.data.libraries.write(str(S/'river_context.blend'),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
bpy.data.scenes.remove(scene)
bpy.ops.object.select_all(action='DESELECT')
for ob in kit.objects:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'river_context.glb'),export_format='GLB',use_selection=True,export_apply=True)
city['composition']='R21 + R22 roof/breakfast layer + editable riverbank, distant crossing and visual traffic; animated traffic/cloth and actual light are in Godot.'
bpy.ops.wm.save_as_mainfile(filepath=str(S/'chongqing_district.blend'),compress=True)
dg=bpy.context.evaluated_depsgraph_get()
street=[]
for x in [-74,-63,-54,-45,-39,-34]:
    for y in [-83,-77,-71,-66]:
        ok,p,n,_,obj,_=city.ray_cast(dg,Vector((x,y,68)),Vector((0,0,-1)),distance=100)
        if not ok or n.z<.88 or not obj.name.startswith(('COL_Terrain_','COL_Road_','COL_Walk_')):continue
        eye=p+Vector((0,0,1.65));axis=axes[0];seen=0
        for t in [.18,.26,.34,.45,.60,.72,.82]:
            q=Vector(axis['north']).lerp(Vector(axis['south']),t)
            target=Vector((q.x,-q.z,q.y+2.1*math.sin(math.pi*t)))
            delta=target-eye;hit,loc,_,_,ob,_=city.ray_cast(dg,eye,delta.normalized(),distance=delta.length+2.)
            if not hit or ob.name.startswith('R22_Distant_crossing') or (loc-eye).length>delta.length-15:seen+=1
        street.append({'eye':[eye.x,eye.z,-eye.y],'support':obj.name,'clear_samples':seen})
street.sort(key=lambda row:(row['clear_samples'],-abs(row['eye'][0]+43)),reverse=True)
record={'terrain':geometry,'axes':axes,'mapped_buildings':buildings,'vehicles':fleet,'river_level_m':water_z,
        'river_trees':len(forest),'shoal_cells':len(island_f),'scan_atlas_sha256':sha(P/'assets/district_r21/canopy_atlas.png'),
        'street_sightlines':street,
        'source_plan_sha256':sha(P/'source_data/river_r22/river_plan.json'),'model_sha256':sha(A/'river_context.glb'),
        'source_sha256':sha(S/'river_context.blend'),'city_sha256':sha(S/'chongqing_district.blend'),
        'scope':'Non-playable background. Mapped plan, art-directed elevations, traffic and generalised construction.'}
(A/'layout.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print('RIVER_BUILT',geometry,len(buildings),[a['north'][1] for a in axes])
