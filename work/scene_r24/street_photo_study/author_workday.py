"""Original editable shop work areas and swept leaves. All ground anchors query the authored street mesh."""
from pathlib import Path
from collections import defaultdict
import bpy, math, json, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parent
project=root.parents[1]/'project/chongqing_godot_v05'
scene=bpy.context.scene
deps=bpy.context.evaluated_depsgraph_get()
surfaces=[]
for obj in scene.objects:
    if obj.type!='MESH' or obj.hide_render: continue
    if not obj.name.startswith(('COL_Terrain_200m','COL_Walk_','R21_Dressed','COL_Road_','COL_R23_NanquSidewalk','COL_R23_NanquUpperApron','COL_R23_PathFoundations','R24Donor','COL_R24_MarketStairs','COL_R24_MarketLanding')):continue
    if any(tag in obj.name.lower() for tag in ('rail','curb','pole','lamp','wood','asphaltmark')): continue
    bounds=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    surfaces.append((min(v.x for v in bounds),max(v.x for v in bounds),min(v.y for v in bounds),max(v.y for v in bounds),obj))
trees={}
audit=[]
def support(x,y,expect=None):
    hits=[]
    for x1,x2,y1,y2,ob in surfaces:
        if not(x1-.001<=x<=x2+.001 and y1-.001<=y<=y2+.001):continue
        if ob.name not in trees: trees[ob.name]=BVHTree.FromObject(ob,deps)
        inv=ob.matrix_world.inverted();down=Vector((0,0,-1))
        loc,n,idx,dist=trees[ob.name].ray_cast(inv@Vector((x,y,80)),(inv.to_3x3()@down).normalized())
        if loc is None:continue
        norm=(inv.to_3x3().transposed()@n).normalized()
        if norm.z<.64:continue
        height=(ob.matrix_world@loc).z
        if expect is None or abs(height-expect)<1.45:hits.append((height,ob.name,norm))
    if not hits: raise RuntimeError(f'no actual ground under {x:.3f},{y:.3f} expected {expect}')
    return max(hits,key=lambda row:row[0])
rng=random.Random(48231)
geometry=defaultdict(lambda:([],[],[]))
palette={
 'split_bamboo':(.32,.17,.062,.84,0),'light_cane':(.47,.286,.116,.86,0),'old_cane':(.21,.112,.048,.89,0),
 'enamel':(.69,.665,.50,.38,.13),'blue_rim':(.042,.095,.113,.37,.34),'water':(.108,.145,.111,.23,.28),
 'dark_steel':(.073,.084,.077,.70,.43),'rubber':(.033,.029,.025,.87,0),'alu':(.32,.34,.31,.57,.65),
 'paint':(.19,.26,.174,.79,.03),'timber':(.286,.146,.052,.85,0),'cut_end':(.56,.51,.32,.89,0),
 'cabbage':(.22,.33,.084,.85,0),'pale_leaf':(.38,.48,.155,.83,0),'green':(.095,.21,.048,.81,0),
 'ochre_leaf':(.34,.186,.039,.90,0),'brown_leaf':(.128,.077,.034,.91,0),'dry_leaf':(.28,.22,.10,.89,0),'cord':(.39,.256,.119,.88,0),
 'terracotta':(.37,.116,.055,.84,0),'ash':(.27,.253,.195,.83,0)}
materials={}
for name,(r,g,b,rough,metal) in palette.items():
    m=bpy.data.materials.new('Workday12_'+name);m.diffuse_color=(r,g,b,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;materials[name]=m
# Use an independently toned board, cane and enamel finish on the close-up working items.
for key in ('timber','old_cane','split_bamboo','light_cane','paint'):
    mat=materials[key];nt=mat.node_tree;node=nt.nodes.new('ShaderNodeTexImage')
    node.image=bpy.data.images.load(str(root/'workday_surfaces'/(key+'.jpg')),check_existing=True)
    node.image.pack();nt.links.new(node.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
group=''
def part(v,f,mat):
    vs,fs,ms=geometry[group];i=len(vs);vs.extend(v);fs.extend([tuple(i+j for j in face) for face in f]);ms.extend([mat]*len(f))
def rod(a,b,r,mat,sides=7,r2=None):
    a,b=Vector(a),Vector(b);ax=(b-a).normalized()
    u=ax.cross(Vector((0,0,1)) if abs(ax.z)<.8 else Vector((1,0,0))).normalized();v=ax.cross(u);verts=[]
    for center,rad in [(a,r),(b,r if r2 is None else r2)]:
        for i in range(sides):
            t=math.tau*i/sides;verts.append(center+rad*(math.cos(t)*u+math.sin(t)*v))
    part(verts,[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)],mat)
def ring(x,y,z,rx,ry,wire,mat,segments=36):
    # One continuous watertight round cross section, avoiding capped joins.
    v=[];f=[]
    for i in range(segments):
        a=i*math.tau/segments
        for j in range(5):
            t=j*math.tau/5;v.append((x+(rx+wire*math.cos(t))*math.cos(a),y+(ry+wire*math.cos(t))*math.sin(a),z+wire*math.sin(t)))
    for i in range(segments):
        for j in range(5):f.append((i*5+j,((i+1)%segments)*5+j,((i+1)%segments)*5+(j+1)%5,i*5+(j+1)%5))
    part(v,f,mat)
def box(x,y,z,dims,mat):
    dx,dy,dz=[d/2 for d in dims]
    part([(x+a*dx,y+b*dy,z+c*dz) for c in [-1,1] for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
def anchor(label,x,y,hint=None):
    h,owner,n=support(x,y,hint);audit.append(dict(item=label,x=x,blender_y=y,height=h,support=owner));return h
def bowl(x,y,h,r,mat,fill=False):
    levels=[(r*.54,.005),(r*.65,.023),(r*.99,r*.46),(r,r*.51),(r*.95,r*.51),(r*.91,r*.44),(r*.58,.034)]
    n=40;vs=[];fs=[]
    for radius,z in levels:
        vs.extend([(x+radius*math.cos(i*math.tau/n),y+radius*math.sin(i*math.tau/n),h+z) for i in range(n)])
    for k in range(len(levels)-1):
        for i in range(n):fs.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
    fs.append(tuple(range(6*n,7*n)));part(vs,fs,mat);ring(x,y,h+r*.50,r,r,.008,'blue_rim')
    if fill:rod((x,y,h+.053),(x,y,h+r*.28),r*.754,'water',40)
def leaf(cx,cy,zz,length,width,angle,mat,lift=.008):
    ux,uy=math.cos(angle),math.sin(angle);v=[]
    for i,span in [(0,.045),(.23,.78),(.54,1),(.80,.59),(1,.02)]:
        for j in [-1,0,1]:
            v.append((cx+length*(i-.5)*ux-j*width*span*uy,cy+length*(i-.5)*uy+j*width*span*ux,zz+lift*(math.sin(i*math.pi)*(.36 if j else 1)+.21*i)))
    part(v,[(k*3+j,(k+1)*3+j,(k+1)*3+j+1,k*3+j+1) for k in range(4) for j in range(2)],mat)
def basket(x,y,h,r):
    for i in range(33):
        a=math.tau*i/33;col=['split_bamboo','light_cane','old_cane'][i%3]
        rod((x+math.cos(a)*r*.59,y+math.sin(a)*r*.59,h+.012),(x+math.cos(a)*r,y+math.sin(a)*r,h+.217),.006,col,5)
    for i in range(13):
        q=i/12;rr=r*(.60+.40*q);ring(x,y,h+.012+.205*q,rr,rr,.006,'light_cane' if i%4==0 else 'split_bamboo',44)
    for i in range(-5,6):
        u=i*r*.105;half=math.sqrt((r*.60)**2-u*u)
        rod((x+u,y-half,h+.015),(x+u,y+half,h+.015),.009,'old_cane',5)
    for i in range(35):
        a=rng.uniform(0,math.tau);rr=rng.uniform(0,r*.68)
        leaf(x+math.cos(a)*rr,y+math.sin(a)*rr,h+.075+rng.random()*.095,.16+rng.random()*.07,.042,rng.uniform(0,math.tau),rng.choice(['cabbage','pale_leaf','green']),.045)
def settle_on_grade(x,y,h,keep_water=False):
    normal=support(x,y,h)[2]
    verts,faces,mats=geometry[group]
    water={i for face,m in zip(faces,mats) if m=='water' for i in face} if keep_water else set()
    origin=Vector((x,y,h));rotation=Vector((0,0,1)).rotation_difference(normal)
    for i,v in enumerate(verts):
        point=origin+rotation@(Vector(v)-origin)
        if i in water:point.z=v[2]
        verts[i]=tuple(point)
def stool(label,x,y,hint):
    h=anchor(label,x,y,hint)
    for ox in [-.17,.17]:
        for oy in [-.115,.115]:
            px=x+ox*1.14;py=y+oy*1.20;b=anchor(label+' foot',px,py,h)
            rod((px,py,b+.002),(x+ox*.82,y+oy*.83,h+.335),.022,'paint',6)
        rod((x+ox,y-.13,h+.14),(x+ox,y+.13,h+.14),.014,'timber')
    for i in range(3): box(x,y+(i-1)*.088,h+.351,(.425,.083,.034),'timber')
# Godot +z south, Blender +y north. The items sit at the two outer ends of the selling area.
group='Workday12_SortingBasket'
x,y=-24.24,-75.78;h=anchor(group,x,y,9.25);basket(x,y,h,.335);settle_on_grade(x,y,h)
group='Workday12_WashingCorner'
x,y=-28.99,-75.38;h=anchor(group,x,y,9.28);bowl(x,y,h,.335,'enamel',True);settle_on_grade(x,y,h,True)
group='Workday12_StallSeat';stool(group,-28.73,-74.66,9.25)
group='Workday12_HandBroom'
x,y=-28.86,-74.93;h=anchor(group,x,y,9.25)
rod((x,y,h+.20),(x+.13,y+.22,h+1.12),.014,'timber')
for i in range(46):
    dx=rng.uniform(-.115,.115);dy=rng.uniform(-.046,.046)
    rod((x+dx,y+dy,h+.02+rng.random()*.023),(x+.019+dx*.18,y+.031+dy*.29,h+.26),.0045,'split_bamboo' if i%3 else 'old_cane',5)
for i in range(3):ring(x+.018,y+.031,h+.22+i*.012,.043-i*.006,.028-i*.003,.004,'cord')
group='Workday12_RepairStand'
x,y=-13.18,-74.26;h=anchor(group,x,y,9.4)
# A wheel off its bicycle, held upright in a small two-foot fork stand, with a removable parts dish.
cx,cy,cz=x,y,h+.407;r=.314
for radius,thick,mat in [(r,.022,'rubber'),(r-.026,.010,'alu')]:
    v=[];f=[];n=56;m=8
    for i in range(n):
        a=math.tau*i/n
        for j in range(m):
            b=math.tau*j/m;v.append((cx+(radius+thick*math.cos(b))*math.cos(a),cy+thick*math.sin(b),cz+(radius+thick*math.cos(b))*math.sin(a)))
    for i in range(n):
        for j in range(m):f.append((i*m+j,i*m+(j+1)%m,((i+1)%n)*m+(j+1)%m,((i+1)%n)*m+j))
    part(v,f,mat)
rod((cx,cy-.073,cz),(cx,cy+.073,cz),.022,'alu',14)
for i in range(28):
    a=i*math.tau/28;rod((cx,cy+(.057 if i%2 else -.057),cz),(cx+math.cos(a)*(r-.025),cy,cz+math.sin(a)*(r-.025)),.0023,'alu',4)
for side in [-1,1]:
    px=x+side*.235;py=y-.09;fz=anchor('wheel stand foot',px,py,h)
    box(px,py,fz+.014,(.078,.31,.028),'dark_steel');rod((px,py,fz+.023),(cx,cy-.087,cz),.014,'paint',7)
x,y=-13.61,-74.36;h=anchor('parts dish',x,y,9.4);bowl(x,y,h,.142,'alu')
for i in range(5):
    xx=x+rng.uniform(-.055,.055);yy=y+rng.uniform(-.048,.048);ring(xx,yy,h+.042,.013,.013,.003,'dark_steel',12)
group='Workday12_SweptEdges'
# Clusters are concentrated beside thresholds and at sheltered edges, with independent support per leaf.
for x,y,n,veg in [(-28.80,-75.67,12,True),(-24.14,-75.57,11,True),(-29.55,-75.74,6,False),(-13.85,-74.7,6,False),(-72.70,-20.70,12,False),(-71.84,-15.28,8,False),(-17.0,-20.2,10,False),(-17.20,-16.1,8,False),(-38.8,-79.47,8,False),(-36.5,-78.85,9,False)]:
    for i in range(n):
        xx=x+rng.gauss(0,.24);yy=y+rng.gauss(0,.16);h,owner,normal=support(xx,yy)
        a=rng.uniform(0,math.tau);ln=rng.uniform(.07,.154);wi=ln*rng.uniform(.18,.31)
        # Transform each blade onto its support plane, leaving the vein slightly curled.
        start=len(geometry[group][0]);leaf(xx,yy,h+.003,ln,wi,a,rng.choice(['cabbage','green','pale_leaf'] if veg else ['ochre_leaf','dry_leaf','brown_leaf']),.010)
        vs=geometry[group][0]
        for k in range(start,len(vs)):
            px,py,pz=vs[k];vs[k]=(px,py,pz-((px-xx)*normal.x+(py-yy)*normal.y)/normal.z)
exec(compile((root/'household_and_cart.py').read_text('utf-8'),str(root/'household_and_cart.py'),'exec'))
exec(compile((root/'price_card_and_ground.py').read_text('utf-8'),str(root/'price_card_and_ground.py'),'exec'))
layer=bpy.data.collections.new('R24_12_Street_workday');scene.collection.children.link(layer)
for plant in extras:layer.objects.link(plant)
layer.objects.link(card_object)
objects=[card_object]
for name,(vs,fs,ms) in geometry.items():
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    keys=list(dict.fromkeys(ms))
    for k in keys:me.materials.append(materials[k])
    slot={key:k for k,key in enumerate(keys)}
    for poly,mat in zip(me.polygons,ms):poly.material_index=slot[mat]
    # Align grain with the board on each flat face; the UV scale is in metres.
    uv=me.uv_layers.new(name='Timber metres')
    for poly in me.polygons:
        if keys[poly.material_index] not in ('timber','old_cane','split_bamboo','light_cane','paint'):continue
        ids=list(poly.vertices);coords=[me.vertices[i].co for i in ids]
        axis=max((b-a for a,b in zip(coords,coords[1:]+coords[:1])),key=lambda v:v.length_squared)
        if axis.length_squared<1e-12:continue
        axis.normalize();cross=poly.normal.cross(axis).normalized()
        for li in poly.loop_indices:
            pos=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(pos.dot(axis)*.87,pos.dot(cross)*2.10)
    ob=bpy.data.objects.new(name,me);layer.objects.link(ob);objects.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
out=project/'assets/street_use_r24';out.mkdir(exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(out/'workday.glb'),export_format='GLB',use_selection=True,export_animations=False,export_yup=True)
(root/'supports.json').write_text(json.dumps({'anchors':audit,'objects':{o.name:len(o.data.polygons) for o in objects}},indent=2),'utf-8')
bpy.context.preferences.filepaths.save_version=0
scene['street_revision']='R24 build 12 street material and market threshold study'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'city_and_street_use.blend'),compress=True,relative_remap=True)
print('STREET_USE_DONE',len(objects),len(audit),flush=True)

