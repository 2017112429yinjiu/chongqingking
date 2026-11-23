"""Join the east flight to the upper courtyard walk, and set its drain into the slope."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
project=here.parents[1]/'project/chongqing_godot_v05'
sys.path.insert(0,str(here))
sys.path.insert(0,str(here.parent/'city_frame_11864101'))
sys.path.insert(0,str(here.parents[1]/'project/chongqing_blender_v05'))
from trim_paving import cut
from district_layout import ground_height
assets=project/'assets/lane_connection_r24';assets.mkdir(exist_ok=True)
scene=bpy.context.scene
main=scene.objects['COL_Walk_Upper_courtyard_walk_pavement']
trim=scene.objects['Walk_details_Upper_courtyard_walk_stone']
stairs=scene.objects['COL_Walk_East_photo_alley_step_concrete']
edge=scene.objects['Walk_details_East_photo_alley_stone']
wall=scene.objects['COL_R23_PathFoundations']
changed=[main,trim,stairs,edge,wall];added=[]
H=23.50552;low_y,high_y=12.46,14.90
def smooth(t):
    t=min(1,max(0,t));return t*t*(3-2*t)
def grade(y,z):
    w=smooth((y-7.1)/(low_y-7.1))*smooth((20.3-y)/(20.3-high_y))
    return z+(H-z)*w
def worldmesh(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world);return bm
def finish(ob,bm):
    bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);bm.free();ob.data.update()
def points(ob):return [ob.matrix_world@v.co for v in ob.data.vertices]
east=sorted(set((round(v.y,6),round(v.x,6)) for v in points(main) if 5.9<v.y<23 and 26.+(v.y-5)*.235<v.x<28.4+(v.y-5)*.235))
west=sorted(set((round(v.y,6),round(v.x,6)) for v in points(main) if 6.2<v.y<23 and 23.6+(v.y-5)*.235<v.x<26.+(v.y-5)*.235))
def side_at(y,line):
    for (a,x),(b,u) in zip(line,line[1:]):
        if a<=y<=b:return x+(u-x)*(y-a)/(b-a)
    return min(line,key=lambda r:abs(r[0]-y))[1]
def east_x(y):return side_at(y,east)
# Force the main surface and both edge strips to have the same landing break lines.
cuts=sorted(set([low_y,high_y]+[7.75+i*.55 for i in range(23)]))
for ob in (main,trim):
    bm=worldmesh(ob)
    for y in cuts:
        faces=[f for f in bm.faces if min(v.co.y for v in f.verts)<y<max(v.co.y for v in f.verts) and 21<f.calc_center_median().x<35]
        if faces:
            geo=set(faces)
            for face in faces:geo.update(face.verts);geo.update(face.edges)
            bmesh.ops.bisect_plane(bm,geom=list(geo),plane_co=(0,y,0),plane_no=(0,1,0),dist=.000002)
    for v in bm.verts:
        x,y,z=v.co
        if 21<x<35 and 7.1<y<20.3:
            lip=.01 if ob==trim else 0.
            v.co.z=grade(y,z-lip)+lip
    if ob==main:
        bay=bpy.data.materials.new('East17_CourtLanding');bay.diffuse_color=(.25,.23,.21,1)
        ob.data.materials.append(bay);slot=len(ob.data.materials)-1
        for face in bm.faces:
            p=face.calc_center_median()
            if 7.75<=p.y<=18.75 and 22<p.x<34:face.material_index=slot
    if ob==trim:
        dead=[face for face in bm.faces if low_y-.00001<face.calc_center_median().y<high_y+.00001 and face.calc_center_median().x>east_x(face.calc_center_median().y)-.04 and face.calc_center_median().x<32]
        bmesh.ops.delete(bm,geom=dead,context='FACES')
    finish(ob,bm)
# Remove the disconnected original last five steps and their decorative nosings.
direction=Vector((-7.,9.)).normalized();start=Vector((33.,5.+2*9/7))
def past(p):
    delta=Vector((p.x,p.y))-start
    return delta.dot(direction)>-.0001 and abs(delta.x*direction.y-delta.y*direction.x)<1.47 and p.x<35 and p.y<17
for ob in (stairs,edge):
    bm=worldmesh(ob)
    geom=list(bm.verts)+list(bm.edges)+list(bm.faces)
    bmesh.ops.bisect_plane(bm,geom=geom,plane_co=(*start,0),plane_no=(*direction,0),dist=.000002)
    dead=[f for f in bm.faces if past(f.calc_center_median())]
    bmesh.ops.delete(bm,geom=dead,context='FACES');finish(ob,bm)
# Retire the old support faces locally, including those inside the new branch opening.
bm=worldmesh(wall)
dead=[f for f in bm.faces if (past(f.calc_center_median()) or (7.15<f.calc_center_median().y<20.25 and side_at(f.calc_center_median().y,west)-.28<f.calc_center_median().x<east_x(f.calc_center_median().y)+.28))]
bmesh.ops.delete(bm,geom=dead,context='FACES');finish(wall,bm)
def mesh(name,parts,material):
    verts=[];faces=[]
    for ps,fs in parts:
        n=len(verts);verts.extend(ps);faces.extend(tuple(n+i for i in face) for face in fs)
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(material)
    ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);added.append(ob)
    uv=me.uv_layers.new()
    for face in me.polygons:
        for idx in face.loop_indices:
            v=me.vertices[me.loops[idx].vertex_index].co;n=face.normal
            pair=(v.x,v.y) if abs(n.z)>.6 else ((v.y,v.z) if abs(n.x)>abs(n.y) else (v.x,v.z))
            uv.data[idx].uv=(pair[0]*.62,pair[1]*.62)
    return ob
def prism(ring,bottom):
    # Ring contains 3D top coordinates in counterclockwise plan order.
    ps=[tuple(v) for v in ring]
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ps,ps[1:]+ps[:1]))<0:ps.reverse()
    n=len(ps);vs=ps+[(x,y,bottom(x,y,z)) for x,y,z in ps]
    return vs,[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,n+i,n+(i+1)%n,(i+1)%n) for i in range(n)]
def surf(ob):
    return BVHTree.FromPolygons(points(ob),[face.vertices[:] for face in ob.data.polygons])
main_skin=surf(main)
def height(tree,x,y):
    hit=tree.ray_cast(Vector((x,y,55)),Vector((0,0,-1)),70)[0]
    return hit.z if hit is not None else None
# The terminal edge follows every surveyed turn in the existing upper walkway, not a chord through its bend.
marks=sorted(set([low_y,high_y]+[y for y,x in east if low_y<y<high_y]+[y for y in cuts if low_y<y<high_y]))
end=Vector((east_x((low_y+high_y)*.5),(low_y+high_y)*.5))
start_across=Vector((direction.y,-direction.x))
end_across=Vector((east_x(high_y)-east_x(low_y),high_y-low_y)).normalized()
end_dir=Vector((-end_across.y,end_across.x))
def cross_section(t):
    # Cubic Hermite approaches from the old flight and arrives perpendicular to the shared landing.
    p=(2*t**3-3*t*t+1)*start+(t**3-2*t*t+t)*direction*7.8+(-2*t**3+3*t*t)*end+(t**3-t*t)*end_dir*4.25
    across=start_across.lerp(end_across,t*t*(3-2*t)).normalized()
    out=[]
    for y in marks:
        u=(y-low_y)/(high_y-low_y)
        out.append(p+across*(u-.5)*2.5 if t<.999999 else Vector((east_x(y),y)))
    return out
sections=[cross_section(i/5.) for i in range(6)]
rows=[];stones=[];samples=[];side_samples=[];loops=[]
for i,(near,far) in enumerate(zip(sections,sections[1:])):
    z=H-(4-i)*.169265
    # Individual transverse bays share their internal seam and cover the full width.
    for j in range(len(near)-1):
        band=[near[j],near[j+1],far[j+1],far[j]]
        part=prism([(v.x,v.y,z) for v in band],lambda x,y,h:min(ground_height(x,y)-.38,h-.36))
        stones.append(part)
    poly=[near[0],near[-1],far[-1],far[0]]
    rows.append([[v.x,v.y] for v in poly])
    for frac in (.12,.35,.5,.66,.88):
        a=near[0].lerp(near[-1],frac);b=far[0].lerp(far[-1],frac)
        for t in (.09,.42,.87):
            pt=a.lerp(b,t);samples.append([pt.x,z,-pt.y,'stair'])
    for j in [0,-1]:
        pt=near[j].lerp(far[j],.5);side_samples.append([pt.x,z-.04,-pt.y])
flight=mesh('COL_East17_TerraceSteps',stones,stairs.data.materials[0])
metric=flight.data.uv_layers.new(name='NosingMetres')
n_bays=len(marks)-1
# Each closed prism has six faces. Local coordinates stay continuous over adjacent bays.
for face in flight.data.polygons:
    course=face.index//(6*n_bays);near,far=sections[course],sections[course+1]
    axis=(near[-1]-near[0]).normalized()
    travel=Vector((-axis.y,axis.x))
    if travel.dot(far[0]-near[0])<0:travel=-travel
    for idx in face.loop_indices:
        p=flight.data.vertices[flight.data.loops[idx].vertex_index].co
        diff=Vector((p.x,p.y))-near[0]
        metric.data[idx].uv=(diff.dot(axis),diff.dot(travel))
flight.data.uv_layers.active_index=0
from shoulders import patch
landscape=patch(scene,main,stairs,rows,sections,marks,H,east,west,side_at,height,main_skin,ground_height,mesh,changed)
# Add actual support down to the terrain on the long road edges, with a real gap reserved for the flight.
skirts=[]
for line in [east,west]:
    ys=sorted(set([7.16,20.24,low_y,high_y]+[y for y,x in line if 7.16<y<20.24]+[y for y in cuts if 7.16<y<20.24]))
    for a,b in zip(ys,ys[1:]):
        if line is east and low_y-.00001<(a+b)*.5<high_y+.00001:continue
        x,u=side_at(a,line),side_at(b,line)
        inner=-.006 if line is east else .006
        za=height(main_skin,x+inner,a);zb=height(main_skin,u+inner,b)
        if za is None or zb is None:continue
        skirts.append(([(x,a,za),(u,b,zb),(u,b,min(zb-.24,ground_height(u,b)-.24)),(x,a,min(za-.24,ground_height(x,a)-.24))],[(0,1,2,3)]))
skirt=mesh('COL_East17_LandingReturns',skirts,wall.data.materials[0])
# Replace the obsolete seven-bar pairs at this intersection. One now seats in the new slope; the second was inside the stair footprint.
grates=[(27.992,9.5),(31.13333,11.)]
for key in ['dark','aluminium']:
    ob=scene.objects['Street_small_furniture_'+key];bm=worldmesh(ob)
    clean=[f for f in bm.faces if any(abs(f.calc_center_median().x-x)<.216 and abs(f.calc_center_median().y-y)<.155 for x,y in grates)]
    assert clean
    bmesh.ops.delete(bm,geom=clean,context='FACES');finish(ob,bm);changed.append(ob)
# Old painted repair rods were placed at a sampled height before the landing was graded.
# Remove a complete mark where it crosses the reconstructed paving.
for label in ['Urban_paving_joints_and_repairs_soil_dark','District_surface_repairs_and_utilities_soil_dark']:
    ob=scene.objects.get(label)
    if ob is None:continue
    bm=worldmesh(ob);visited=set();dead=[]
    for seed in list(bm.verts):
        if seed in visited:continue
        pile=[seed];visited.add(seed)
        for v in pile:
            for e in v.link_edges:
                other=e.other_vert(v)
                if other not in visited:visited.add(other);pile.append(other)
        if any(24.3<v.co.x<36.5 and 6.4<v.co.y<17.75 for v in pile):
            dead.extend(pile)
    if dead:
        bmesh.ops.delete(bm,geom=dead,context='VERTS');finish(ob,bm);changed.append(ob)
    else:bm.free()
def mat(name,color,metal,rough):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=m.diffuse_color;b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
    return m
iron=mat('East17_AgedCastIron',(.065,.064,.053),.59,.77)
inside=mat('East17_GullyInterior',(.019,.021,.019),.12,.94)
cx,cy=grates[0];u=Vector((.977,-.214));v=Vector((.214,.977))
def grate_pt(a,b,offset=0):
    xy=Vector((cx,cy))+u*a+v*b
    z=height(main_skin,*xy);assert z is not None
    return Vector((xy.x,xy.y,z+offset))
ring=[grate_pt(a,b) for a,b in [(-.235,-.155),(.235,-.155),(.235,.155),(-.235,.155)]]
center=sum(ring,Vector())/4
assert cut(main,[(center,ring)])>0
def rectangle(x1,y1,x2,y2,depth,top):
    return prism([grate_pt(a,b,top) for a,b in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]],lambda x,y,h:h-depth)
r=.235;t=.155;lip=.021
frame=[rectangle(-r,-t,r,-t+lip,.059,-.0005),rectangle(-r,t-lip,r,t,.059,-.0005),rectangle(-r,-t+lip,-r+lip,t-lip,.059,-.0005),rectangle(r-lip,-t+lip,r,t-lip,.059,-.0005)]
for i in range(8):
    x=-.180+i*.0514
    frame.append(rectangle(x-.009,-t+lip,x+.009,t-lip,.026,-.0015))
grate=mesh('COL_East17_IronGrate',frame,iron)
# Ease the cast edges and use two recessed transverse bearers below the slats.
bevel=grate.modifiers.new('Cast edge radius','BEVEL');bevel.width=.0021;bevel.segments=2
bpy.context.view_layer.objects.active=grate
bpy.ops.object.modifier_apply(modifier=bevel.name)
bearers=mesh('East17_GrateBearers',[rectangle(-r+lip,-.085,r-lip,-.073,.012,-.027),rectangle(-r+lip,.065,r-lip,.077,.012,-.027)],iron)
sump=mesh('East17_GullyBed',[rectangle(-r,-t,r,t,.012,-.055)],inside)
# Reject disconnected floor patches among the upper approaches.
join_samples=[]
for y in marks:
    x=east_x(y);join_samples.append([x,H,-y])
for y in [9.0,10.5,11.7,12.46,13.07,13.7,14.29,14.90,15.6,16.4,17.8,18.4,19.0,19.7,20.0,20.55]:
    for frac in [.14,.50,.86]:
        x=side_at(y,west)*(1-frac)+east_x(y)*frac;z=height(main_skin,x,y)
        if z is not None:samples.append([x,z,-y,'landing'])
record={'shoulders':landscape,'source_nodes':[o.name for o in changed],'new_nodes':[o.name for o in added],'height':H,'steps':rows,'join':join_samples,'floor_probes':samples,'side_probes':side_samples,'drain_rim':[[q.x,q.z,-q.y] for q in ring],'drain_center':[center.x,center.z,-center.y],'removed_grates':grates,'bay_width':(sections[-1][-1]-sections[-1][0]).length}
(assets/'layout.json').write_text(json.dumps(record,indent=2),'utf8')
bpy.ops.object.select_all(action='DESELECT')
for ob in changed+added:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(assets/'junction.glb'),export_format='GLB',use_selection=True,export_animations=False,export_image_format='NONE')
scene['street_revision']='R24 build 17, east junction and drain seat'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_lane_connections.blend'),compress=True,relative_remap=True)
print('JUNCTION17',record['source_nodes'],record['new_nodes'],len(samples),len(marks))
