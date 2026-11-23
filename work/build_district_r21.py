"""Fit a planted retaining bank and a layered city surround to the open R20 city."""
from pathlib import Path
import bpy,math,random,json,re,sys,hashlib
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

W=Path(__file__).resolve().parent;S=W/'scene_r21';A=W/'project/chongqing_godot_v05/assets/district_r21'
project=W/'project/chongqing_blender_v05'
sys.path.insert(0,str(project))
import district_layout as plan
import landscape_v05 as planting
source=list(bpy.context.scene.objects)
layer=bpy.data.collections.new('R21_District_environment');bpy.context.scene.collection.children.link(layer)
architecture=[];instances=[];far=[];beds=[];roofs=[];nearby=[];rng=random.Random(77121)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def ground_tree():
    verts=[];faces=[]
    for ob in source:
        if not ob.name.startswith(('COL_Terrain_200m_','Outer_ground_context_')):continue
        start=len(verts);verts.extend(ob.matrix_world@v.co for v in ob.data.vertices)
        faces.extend(tuple(start+i for i in poly.vertices) for poly in ob.data.polygons)
    return BVHTree.FromPolygons(verts,faces)
terrain=ground_tree()
def ground(x,y):
    p=terrain.ray_cast(Vector((x,y,250)),Vector((0,0,-1)),400)[0]
    if p is None:raise ValueError(('ground missing',x,y))
    return p.z

wall=bpy.data.materials.new('R21 Mottled sandstone masonry');wall.use_nodes=True
nt=wall.node_tree;bs=nt.nodes.get('Principled BSDF')
folder=W/'assets_incoming/district_r21/mossy_stone_wall'
for rec in json.loads((folder/'PROVENANCE.json').read_text(encoding='utf8'))['files']:
    k=rec['map'];tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(folder/rec['file']))
    if k!='diff':tx.image.colorspace_settings.name='Non-Color'
    if k=='nor_gl':
        normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.64
        nt.links.new(tx.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
    else:nt.links.new(tx.outputs['Color'],bs.inputs['Base Color' if k=='diff' else 'Roughness'])
soil=bpy.data.materials.get('CQ03_PBR_ground_dirt')
cap=bpy.data.materials.get('CQ03_PBR_step_concrete')
def plain(name,color,r):
    m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=r;return m
roofmat=plain('R21 Oxidised sheet roof',(.118,.132,.118),.74)
brick=plain('R21 Weathered roof service room',(.24,.191,.146),.91)
frame=plain('R21 Roof screen iron',(.074,.072,.059),.74)
water=plain('R21 Galvanised water tank',(.34,.36,.33),.43)

class Surface:
    def __init__(self,name,materials):
        self.name=name;self.mats=materials;self.verts=[];self.faces=[];self.uv=[];self.slots=[]
    def quad(self,vs,uv,slot=0):
        offset=len(self.verts);self.verts.extend(vs);self.faces.append(tuple(range(offset,offset+len(vs))));self.uv.extend(uv);self.slots.append(slot)
    def box(self,x,y,z,l,w,h,slot=0):
        pts=[(x+u*l/2,y+v*w/2,z+t*h) for t in (0,1) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        for inds in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
            self.quad([pts[i] for i in inds],[(0,0),(l,0),(l,h),(0,h)],slot)
    def finish(self):
        m=bpy.data.meshes.new(self.name);m.from_pydata(self.verts,[],self.faces);m.update()
        ob=bpy.data.objects.new(self.name,m);layer.objects.link(ob)
        for mat in self.mats:m.materials.append(mat)
        uv=m.uv_layers.new(name='Metre UV')
        for face,slot in zip(m.polygons,self.slots):
            face.material_index=slot
            for k in face.loop_indices:uv.data[k].uv=self.uv[m.loops[k].vertex_index]
        architecture.append(ob);return ob

def place(donor,x,y,z,height,yaw,near=True):
    parts=sorted((ob for ob in source if ob.name.startswith(donor+'_')),key=lambda o:o.name)
    assert parts,donor
    base=parts[0];factor=height/base['placed_height_m'];scale=base.scale.x*factor
    for i,old in enumerate(parts):
        new=old.copy();new.data=old.data;layer.objects.link(new)
        new.name=f'R21_Plant_{len(instances):03}_{i:02}'
        new.matrix_world=Matrix.Translation(Vector((x,y,z)))@Matrix.Rotation(yaw,4,'Z')@Matrix.Scale(scale,4)
    spec={'donors':[o.name for o in parts],'position':[x,z,-y],'yaw':yaw,'scale':scale,'height':height,'trunk':near and donor.startswith('Planted_tree')}
    instances.append(spec);nearby.append((x,y))

def terrace(name,poly,width,rise):
    # Each run has a level cap, an earth backfill and walls returned into grade.
    top=max(ground(x,y) for x,y in poly)+rise
    mesh=Surface('COL_R21_Bank_'+name,[wall,soil,cap])
    trim=Surface('R21_Coping_'+name,[cap])
    dist=0.;previous=None;inside=[]
    for i,(x,y) in enumerate(poly):
        before=Vector(poly[max(0,i-1)]);after=Vector(poly[min(len(poly)-1,i+1)])
        axis=(after-before).normalized();inward=Vector((-axis.y,axis.x))
        inside.append((x+inward.x*width,y+inward.y*width))
    perimeter=poly+inside[::-1]
    # Only the cap is level. The inverted foot is fitted to the actual tiled terrain.
    for (x,y),(xx,yy) in zip(perimeter,perimeter[1:]+perimeter[:1]):
        length=math.hypot(xx-x,yy-y);steps=max(1,math.ceil(length/.68))
        for j in range(steps):
            u=j/steps;v=(j+1)/steps;xa=x+(xx-x)*u;ya=y+(yy-y)*u;xb=x+(xx-x)*v;yb=y+(yy-y)*v
            za=ground(xa,ya)-.12;zb=ground(xb,yb)-.12
            mesh.quad([(xa,ya,za),(xb,yb,zb),(xb,yb,top),(xa,ya,top)],[(dist/3.8,(za-top)/3.8),((dist+length/steps)/3.8,(zb-top)/3.8),((dist+length/steps)/3.8,0),(dist/3.8,0)])
            dist+=length/steps
    for i in range(len(poly)-1):
        a,b=map(Vector,poly[i:i+2]);c,d=map(Vector,inside[i:i+2])
        mesh.quad([(*a,top-.015),(*b,top-.015),(*d,top-.015),(*c,top-.015)],[tuple(q/1.6) for q in [a,b,d,c]],1)
        length=(b-a).length;n=max(2,round(length/.78));direction=(b-a).normalized();normal=Vector((-direction.y,direction.x))
        for j in range(n):
            aa=a+(b-a)*(j/n)+direction*.004;bb=a+(b-a)*((j+1)/n)-direction*.004
            edge=[aa-normal*.035,bb-normal*.035,bb+normal*.21,aa+normal*.21]
            z=top+.037+rng.uniform(-.004,.004)
            trim.quad([(*p,z) for p in edge],[tuple(p/1.8) for p in edge])
            for p,q in zip(edge,edge[1:]+edge[:1]):
                trim.quad([(*p,top-.024),(*q,top-.024),(*q,z),(*p,z)],[(0,0),((q-p).length,0),((q-p).length,.06),(0,.06)])
        # Small clusters leave visible soil, caps and variation in planting height.
        for j in range(round(length/1.17)):
            u=(j+.5)/round(length/1.17);p=(a.lerp(b,u)).lerp(c.lerp(d,u),rng.uniform(.27,.75))
            place('Soil_bed_central_upper_west_shrub_01',p.x,p.y,top-.034,rng.uniform(.32,.85),rng.uniform(0,math.tau),False)
    mesh.finish();trim.finish()
    clearance=min(planting.route_clearance(tuple(Vector(a).lerp(Vector(b),k/10))) for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]) for k in range(11))
    assert clearance>.65,(name,clearance)
    beds.append({'name':name,'front':poly,'rear':inside,'top':top,'route_margin_m':clearance})
    return top

lo=terrace('CourtLower',[(-38.0,75.1),(-34.1,75.6),(-29.8,77.1)],2.10,.69)
hi=terrace('CourtUpper',[(-43.6,81.3),(-38.4,80.75),(-34.1,81.65),(-32.8,82.5)],2.64,.76)
place('Planted_tree_01',-34.6,76.64,lo-.08,9.7,2.13)
place('Planted_tree_02',-39.7,82.2,hi-.09,8.3,-.83)
for donor,x,y,height,yaw in [
    ('Planted_tree_01',-23.48,-34.3,8.0,1.07),('Planted_tree_02',-15.96,-26.8,7.3,-.75),
    ('Planted_tree_02',-23.42,-46.9,5.7,2.84)]:
    assert planting.route_clearance((x,y))>1.2
    place(donor,x,y,ground(x,y)-.095,height,yaw)

# Model a usable stepped shoulder in the mid-distance rather than a straight
# square edge at the district perimeter. Mid / far canopy sites avoid blocks and roads.
outside_boxes=[]
for ob in source:
    if not re.match(r'^Context_(?:\d+|authored_\d+_\d+)_',ob.name):continue
    vv=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    outside_boxes.append((min(p.x for p in vv),min(p.y for p in vv),max(p.x for p in vv),max(p.y for p in vv)))
def clear_context(x,y):
    if any(a-2<x<c+2 and b-2<y<d+2 for a,b,c,d in outside_boxes):return False
    for rd in plan.DATA['roads']+plan.DATA['paths']:
        if rd['tags'].get('tunnel')=='yes':continue
        for a,b in zip(rd['points'],rd['points'][1:]):
            if min(a[0],b[0])-6<x<max(a[0],b[0])+6 and min(a[1],b[1])-6<y<max(a[1],b[1])+6 and plan.distance_segment((x,y),a,b)[0]<plan.road_width(rd)/2+1.4:return False
    return True
for belt in range(3):
    for group in range(52):
        a=(group+rng.uniform(-.31,.31))/52*math.tau
        radius=(126+54*belt+rng.uniform(-11,14))/max(abs(math.cos(a)),abs(math.sin(a)))
        cx,cy=math.cos(a)*radius,math.sin(a)*radius
        for k in range(rng.randrange(4,12)):
            x=cx+rng.gauss(0,8.8);y=cy+rng.gauss(0,6.6)
            if max(abs(x),abs(y))<113 or not clear_context(x,y) or any((x-a)**2+(y-b)**2<15 for a,b in nearby):continue
            z=ground(x,y);height=rng.uniform(6.4,15.8);kind=rng.randrange(2);yaw=rng.uniform(-math.pi,math.pi)
            far.append({'position':[round(x,3),round(z-.13,3),round(-y,3)],'height':round(height,3),'kind':kind,'yaw':round(yaw,4),'shade':round(rng.uniform(.79,1.09),3)})
            nearby.append((x,y))

# Varied roof service structures break the repeated flat cornice. Footings sit on
# the measured roof face, inside actual roof polygons, away from existing tanks.
rooftops=Surface('R21_Rooftop_stairheads',[brick,roofmat,frame,water])
for ob in sorted(source,key=lambda o:o.name):
    if not re.match(r'^Context_(?:\d+|authored_\d+_\d+)_',ob.name) or ob.type!='MESH':continue
    coords=[ob.matrix_world@v.co for v in ob.data.vertices]
    z=max(p.z for p in coords)
    faces=[p for p in ob.data.polygons if all(abs(coords[i].z-z)<.02 for i in p.vertices)]
    if not faces:continue
    box=ob.bound_box;cx=sum(v.x for v in coords)/len(coords);cy=sum(v.y for v in coords)/len(coords)
    if max(abs(cx),abs(cy))>260:continue
    poly=max(faces,key=lambda f:f.area)
    pts=[(coords[i].x,coords[i].y) for i in poly.vertices]
    if len(pts)<3:continue
    center=Vector((sum(p[0] for p in pts)/len(pts),sum(p[1] for p in pts)/len(pts)))
    size=rng.choice([2.8,3.4,4.1]);anchor=None
    for j in range(40):
        x=center.x+rng.uniform(-14,14);y=center.y+rng.uniform(-12,12)
        if math.hypot(x-center.x,y-center.y)<6:continue
        if all(plan.point_in_poly((x+dx*size/2,y+dy*1.5),pts) for dx in [-1,1] for dy in [-1,1]):
            anchor=(x,y);break
    if anchor is None:continue
    x,y=anchor;h=rng.uniform(2.1,4.3)
    rooftops.box(x,y,z-.035,size,2.8,h,0);rooftops.box(x,y,z+h-.05,size+.30,3.12,.18,1)
    if rng.random()<.65:
        for j in range(4):rooftops.box(x-size*.25+j*.34,y-1.416,z+h*.36,.19,.038,.62,2)
    roofs.append({'donor':ob.name,'position':[x,z,-y],'height':h})
if rooftops.faces:rooftops.finish()
sys.path.insert(0,str(W))
from district_window_life import build as add_window_life
facades=add_window_life(source,project,layer,architecture,ground,plain)
from district_stone_steps import build as add_stones
stonework=add_stones(source,layer,architecture,W,S)
from district_foundations import build as add_footings
footings=add_footings(source,ground,Surface,wall)
old_caps=bpy.data.objects.get('R19_Stair_tread_caps_step_concrete')
if old_caps:
    old_caps.hide_render=True;old_caps.hide_viewport=True

# In Blender the far representations face the middle of the district. The game
# selects the matching photographed azimuth for the live camera instead.
atlas_mat=plain('R21 Exterior canopy preview',(1,1,1),.93)
tree_nt=atlas_mat.node_tree;atlas_tex=tree_nt.nodes.new('ShaderNodeTexImage')
atlas_tex.image=bpy.data.images.load(str(A/'canopy_atlas.png'))
tree_bs=tree_nt.nodes.get('Principled BSDF')
tree_nt.links.new(atlas_tex.outputs['Color'],tree_bs.inputs['Base Color'])
tree_nt.links.new(atlas_tex.outputs['Alpha'],tree_bs.inputs['Alpha'])
preview=Surface('R21_Exterior_canopy_authoring',[atlas_mat])
pivots=json.loads((S/'canopy/pivot.json').read_text())
for plant in far:
    x,z,my=plant['position'];y=-my
    toward=Vector((-x,-y,0)).normalized();right=Vector((-toward.y,toward.x,0))
    kind=plant['kind'];width=plant['height']*pivots[['tree_small_02','island_tree_01'][kind]]['frame_width_over_height']
    center=Vector((x,y,z+.48*width));half=Vector((0,0,width*.5));u=right*(width*.5)
    angle=math.atan2(toward.x,-toward.y)-plant['yaw'];col=math.floor(angle/(math.pi/2)+.5)%4
    v0=.5 if kind==0 else 0
    preview.quad([center-u-half,center+u-half,center+u+half,center-u+half],[(col/4,v0),((col+1)/4,v0),((col+1)/4,v0+.5),(col/4,v0+.5)])
preview_object=preview.finish();architecture.remove(preview_object)

# Save a separate authored kit and full city with linked vegetation meshes.
bpy.context.preferences.filepaths.save_version=0
bpy.context.scene['revision']=21
bpy.context.scene['composition']='R20 city plus R21 terraces, district greenery, stone flights, roof and facade fittings. Playable lighting, wall runoff and view-dependent exterior canopies use assets/render_profile_r21.json in Godot.'
bpy.context.view_layer.update()
kit_source=S/'district_environment.blend'
bpy.ops.file.pack_all()
kit_scene=bpy.data.scenes.new('District R21 environment kit')
kit_scene.collection.children.link(layer)
bpy.data.libraries.write(str(kit_source),{kit_scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
bpy.data.scenes.remove(kit_scene)
bpy.ops.object.select_all(action='DESELECT')
for obj in architecture:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'terraces.glb'),export_format='GLB',use_selection=True,export_apply=True)
layout={'trees_and_shrubs':instances,'outer_canopy':far,'terraces':beds,'rooftops':roofs,'facades':facades,'canopy_pivots':pivots,'base_city_sha256':sha(W/'scene_r20/chongqing_district.blend'),'kit_sha256':sha(kit_source),'terraces_glb_sha256':sha(A/'terraces.glb')}
layout['stonework']=stonework
layout['footings']=footings
(A/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(S/'chongqing_district.blend'),compress=True)
print('DISTRICT_BUILT',len(instances),len(far),len(roofs),beds,flush=True)
