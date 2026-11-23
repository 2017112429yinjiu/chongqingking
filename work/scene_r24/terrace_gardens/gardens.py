"""Open actual planting pits, set the bed on grade and instance the district's licensed plants."""
import bpy,bmesh,math,random,json
import numpy as np
from mathutils import Vector,Matrix
from site_data import game,here,scene,road_objects,Surfaces,save
from grade import obj,changed
rng=random.Random(24021)
ground_objects=[o for o in road_objects if o not in [obj] and not o.hide_render]+[obj]
floors=Surfaces(ground_objects)
layout=json.loads((here.parent/'district_age/survey_after.json').read_text('utf8'))
rx,ry,rwidth=np.array([(x,y,layout['routes'][i][3]/2) for i,l,x,y,_ in layout['samples'] if l==1]).T
collection=bpy.data.collections.new('Resident planting terraces');scene.collection.children.link(collection)
parts=[]; beds=[]; visuals=[]; changed_pits={}; trunks=[]
def mesh(name,verts,faces,slots,material):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update()
    for key in slots:
        mat=bpy.data.materials.get(key) or bpy.data.materials.new(key)
        m.materials.append(mat)
    for f,idx in zip(m.polygons,material):f.material_index=idx
    uv=m.uv_layers.new(name='GardenMetres')
    for f in m.polygons:
        for i in f.loop_indices:
            v=m.vertices[m.loops[i].vertex_index].co
            uv.data[i].uv=(v.x,v.y) if f.normal.z>.6 else (v.x+v.y,v.z)
    node=bpy.data.objects.new(name,m);collection.objects.link(node);visuals.append(name)
def ground(x,y):
    hits=floors.down(x,y,19,15)
    if not hits:raise ValueError(('unsupported bed',x,y))
    return hits[0]
def pit(ring,objects):
    for ob in objects:
        if ob.name in ('COL_Terrace21_Fork',) or ob.name.startswith('COL_Terrain_200m'):
            floors.tree(ob)
        else:continue
        bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
        x0,y0=[min(p[i] for p in ring) for i in [0,1]];x1,y1=[max(p[i] for p in ring) for i in [0,1]]
        pool={f for f in bm.faces if min(v.co.x for v in f.verts)<x1 and max(v.co.x for v in f.verts)>x0 and min(v.co.y for v in f.verts)<y1 and max(v.co.y for v in f.verts)>y0}
        for a,b in zip(ring,ring[1:]+ring[:1]):
            if not pool:break
            t=(b-a).normalized();n=Vector((-t.y,t.x,0));c=Vector((a.x,a.y,0))
            cut=[f for f in pool if min((v.co-c).dot(n) for v in f.verts)<-.00001 and max((v.co-c).dot(n) for v in f.verts)>.00001]
            if cut:
                g=set(cut)
                for f in cut:g.update(f.edges);g.update(f.verts)
                result=bmesh.ops.bisect_plane(bm,geom=list(g),dist=.000002,plane_co=c,plane_no=n)
                pool.update(f for f in result['geom'] if isinstance(f,bmesh.types.BMFace))
            pool={f for f in pool if f.is_valid and (f.calc_center_median()-c).dot(n)>-.000008}
        if pool:
            changed_pits[ob.name]=changed_pits.get(ob.name,0)+len(pool)
            if ob!=obj:changed.setdefault(ob.name,0)
            bmesh.ops.delete(bm,geom=list(pool),context='FACES');bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update()
        bm.free()
conv=Matrix.Rotation(-math.pi/2,4,'X')
def plant(keys,p,scale,angle,typ):
    sources=[scene.objects[k] for k in keys]
    root=next((o for o in sources if any('trunk' in m.name or m.name=='CQ_PH_island_tree_01' for m in o.material_slots)),sources[0])
    coords=[root.matrix_world@v.co for v in root.data.vertices];z=min(v.z for v in coords)
    low=[v for v in coords if v.z<z+.06]
    base=sum(low,Vector())/len(low);base.z=z
    move=Matrix.Translation(p)@Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-base)
    if typ=='tree':
        # Follow the actual deformed trunk centre at three heights, after placement.
        for bottom,top in [(.09,.63),(.63,1.22),(1.22,1.66)]:
            levels=[]
            for level in [bottom,top]:
                sample=[move@v for v in coords if abs((move@v).z-p[2]-level)<.13]
                if not sample:break
                xx=float(np.median([v.x for v in sample]));yy=float(np.median([v.y for v in sample]))
                radius=min(.27,max(.072,float(np.median([math.hypot(v.x-xx,v.y-yy) for v in sample]))))
                levels.append([xx,yy,p[2]+level,radius])
            if len(levels)==2:trunks.append(levels)
    for o in sources:
        dup=o.copy();dup.parent=None;dup.data=o.data;dup.matrix_world=move@o.matrix_world
        dup.name='Garden21_%03d_%s'%(len(parts),o.name);collection.objects.link(dup)
    # Blender Y-up conversion mirrors the existing Godot donor instancing.
    m=conv@move@conv.inverted()
    parts.append({'donors':keys,'kind':typ,'transform':[list(m.col[i][:3]) for i in range(4)]})
spec=[(38.4,-69.8,3.5,1.35,.45,0),(60.,-67.6,3.8,1.45,.63,.41),(67.9,-62.25,4.2,1.55,.64,0),(40.7,-53.9,5.2,2.35,.17,.57),(54.9,-52.1,3.4,1.7,1.4,.36)]
for j,(x,y,length,width,a,tree) in enumerate(spec):
    center=Vector((x,y));ex=Vector((math.cos(a),math.sin(a)));ey=Vector((-ex.y,ex.x))
    def xy(u,v):return center+u*ex+v*ey
    half=length*.5;side=width*.5;ch=.30
    corners=[(-half+ch,-side),(half-ch,-side),(half,-side+ch),(half,side-ch),(half-ch,side),(-half+ch,side),(-half,side-ch),(-half,-side+ch)]
    ring=[xy(*p) for p in corners]
    rim=[];inner=[]; subgap=[];ends=[]
    for i,(b,c) in enumerate(zip(ring,ring[1:]+ring[:1])):
        count=math.ceil((b-c).length/.43)
        for k in range(count):
            p=b.lerp(c,k/count);rim.append(p)
            q=p-center
            inner.append(center+ex*q.dot(ex)*(half-.115)/half+ey*q.dot(ey)*(side-.115)/side)
    clear=min(float(min(np.hypot(rx-p.x,ry-p.y)-rwidth)) for p in rim)
    assert clear>1.8,(j,clear)
    hs=[ground(p.x,p.y)[0] for p in rim]
    xs=np.array([[p.x-x,p.y-y,1] for p in rim]);slope=np.linalg.lstsq(xs,hs,rcond=None)[0]
    def soil(p):return float(slope[2]+.135+.64*(slope[0]*(p.x-x)+slope[1]*(p.y-y)))
    lift=max(max(h-soil(p) for p,h in zip(rim,hs))+.053,0)
    def surface(p):return soil(p)+lift
    def top(p):return surface(p)+.057
    pit([center+(p-center)*.93 for p in ring],set(scene.objects[n] for n in set(ground(p.x,p.y)[1] for p in [center]+rim)))
    vs=[];fs=[];mats=[]
    def add(points,mi):
        idx=len(vs);vs.extend(tuple(pt) for pt in points);fs.append(tuple(range(idx,len(vs))));mats.append(mi)
    def xyz(p,z):return (p.x,p.y,z)
    for i,b in enumerate(rim):
        k=(i+1)%len(rim);c=rim[k];ib=inner[i];ic=inner[k]
        # The continuous mortar backing closes every corner beneath the individual caps.
        add([xyz(b,hs[i]-.075),xyz(c,hs[k]-.075),xyz(c,top(c)-.042),xyz(b,top(b)-.042)],0)
        add([xyz(b,top(b)-.042),xyz(c,top(c)-.042),xyz(ic,top(ic)-.042),xyz(ib,top(ib)-.042)],0)
        start=b.lerp(c,.009);end=c.lerp(b,.009);ins=ib.lerp(ic,.009);ine=ic.lerp(ib,.009)
        cap=[start,end,ine,ins];level=[xyz(q,top(q)) for q in cap];skirt=[xyz(q,top(q)-.051) for q in cap]
        add(level,1+(i+j)%3)
        for e in range(4):add([skirt[e],skirt[(e+1)%4],level[(e+1)%4],level[e]],1+(i+j)%3)
        add([xyz(ib,surface(ib)),xyz(ic,surface(ic)),xyz(center,surface(center))],4)
        subgap.append([*b,hs[i],top(b)])
    mesh('COL_Terrace21_Bed%02d'%j,vs,fs,['Garden21_mortar','Garden21_coping_a','Garden21_coping_b','Garden21_coping_c','Garden21_soil'],mats)
    if tree:
        tx=xy(-.30*half,.02);typ=12 if j!=3 else 17
        plant(['Planted_tree_%02d_%02d'%(typ,i) for i in range(3)],(*tx,surface(tx)-.045),tree,rng.uniform(0,6.28),'tree')
    # Staggered swathes: taller stems uphill, a low broad-leaf fringe on the lane side.
    start=len(parts)
    for side_i,frac in enumerate([-.42,.31]):
        count=round(length/(.65 if side_i else .42))
        for k in range(count):
            u=(-.82+1.64*(k+.5+rng.uniform(-.15,.15))/count)*half;v=frac*side+rng.uniform(-.085,.085);p=xy(u,v)
            if tree and (p-tx).length<.26:continue
            if side_i:
                key='Soil_bed_central_upper_west_shrub_0%d_00'%((k+j)%3);sc=rng.uniform(.63,.99)
            else:key='B_809889623_market_Interior_asset_0_01';sc=rng.uniform(1.05,1.53)
            plant([key],(*p,surface(p)-.026),sc,rng.uniform(0,6.28),'underplant')
    beds.append({'id':j,'center':list(center),'size':[length,width],'clearance_to_mapped_route_edge':clear,'rim':subgap,'tree':bool(tree),'underplants':len(parts)-start})
v=[];f=[]
for levels in trunks:
    start=len(v)
    for xx,yy,zz,rad in levels:
        v.extend((xx+rad*math.cos(i*math.tau/10),yy+rad*math.sin(i*math.tau/10),zz) for i in range(10))
    f.extend((start+i,start+(i+1)%10,start+10+(i+1)%10,start+10+i) for i in range(10))
mesh('COLH_Terrace21_Trunks',v,f,['Garden21_mortar'],[0]*len(f))
scene.objects['COLH_Terrace21_Trunks'].hide_render=True
save('beds.json',beds)
