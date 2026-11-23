"""Incremental environment authoring against the packed R22 working city (Blender metres, Z-up)."""
from pathlib import Path
from collections import Counter, defaultdict
import bpy, bmesh, json, math, re, sys, random
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parent
S=W/'scene_r23'; A=S/'assets'; B=W/'project/chongqing_blender_v05'
sys.path.insert(0,str(B))
import district_layout as dl
scene=bpy.context.scene; orig=list(scene.objects)
arch=json.loads((B/'architecture_manifest.json').read_text(encoding='utf8'))
land=json.loads((S/'playtest/assets/landscape_report.json').read_text(encoding='utf8'))
report={};changed={};extras=[];views={};removed=[]
def edit(o):
    if o.name not in changed:
        o.data=o.data.copy();changed[o.name]=o
    return o
def vec(x):return Vector(x)
def write(name,data): (A/name).write_text(json.dumps(data,ensure_ascii=False,indent=1),encoding='utf8')
def material(name,c,r=.85):
    m=bpy.data.materials.new('R23_'+name);m.diffuse_color=(*c,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=r
    return m
def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
    ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);extras.append(ob);return ob
def ground_mesh(o):
    return o.type=='MESH' and o.name.startswith(('COL_Terrain','COL_Walk_','COL_Road_','COL_Community_court_pavement','COL_Court_entry','Designed_Hillside'))
def index(objects):
    trees=[]
    for o in objects:
        vs=[o.matrix_world@v.co for v in o.data.vertices]
        if not vs:continue
        bounds=[(min(v[k] for v in vs),max(v[k] for v in vs)) for k in [0,1]]
        trees.append((o.name,bounds,BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in o.data.polygons])))
    return trees
def sample(x,y,trees,top=90):
    heights=[]
    for _,((x0,x1),(y0,y1)),tree in trees:
        if x0-.001<=x<=x1+.001 and y0-.001<=y<=y1+.001:
            h,n,_,_=tree.ray_cast((x,y,top),(0,0,-1),150)
            if h is not None and abs(n.z)>.48:heights.append(h.z)
    return max(heights) if heights else None
grounds=[o for o in orig if ground_mesh(o)]
soil=lambda o:o.name.startswith(('COL_Terrain','Designed_Hillside'))
terrain=index([o for o in grounds if soil(o)]);surface=index(grounds)
# Secondary shutters lack the entrance domain used by the primary door. Make a flush apron,
# with a blended uphill cut over the surrounding terrain and existing paving.
old_terrain=terrain
aprons=[]
for r in arch['buildings']:
    edge=next(e for e in r['facade_openings'] if e['edge']==r['front_edge'])
    a=vec(edge['a']);u=(vec(edge['b'])-a).normalized();out=vec((u.y,-u.x))
    for l,h,lo,hi in edge['holes']:
        if abs(lo-.03)>.001 or hi<2:continue
        c=a+u*((l+h)/2);floor=r['base_m']+.014
        before=[sample(*(c+u*dx+out*d),surface) for dx in [-1,0,1] for d in [.15,.7]]
        aprons.append((c,u,out,(h-l)/2,floor,str(r['id']),before))
# Survey the documented principal entrances across their full usable width as well.
for building in arch['buildings']:
    for entrance in building['entrances']:
        pos=vec(entrance['position']);c=pos.xy;out=(vec(entrance['approach']).xy-c).normalized()
        u=vec((-out.y,out.x));hw=entrance['width_m']*.5
        before=[sample(*(c+u*dx+out*d),surface) for dx in [-hw*.84,0,hw*.84] for d in [.12,.5]]
        if None not in before and max(before)>pos.z+.095:
            aprons.append((c,u,out,hw,pos.z-.012,'entrance_'+str(building['id']),before))
def cut_z(p):
    z=p.z
    for c,u,n,hw,f,_,_ in aprons:
        q=p.xy-c;side=abs(q.dot(u));d=q.dot(n)
        if side>hw+2.5 or d<-.65 or d>4:continue
        t=max(0,(side-hw-.35)/2.15,(d-1.12)/2.88,(-d-.15)/.50)
        t=min(1,t);t=t*t*(3-2*t);z=min(z,f+(max(z,f)-f)*t)
    return z
for o in orig:
    if not (ground_mesh(o) or o.name.startswith(('Urban_paving_','Walk_details_'))):continue
    if o.matrix_world!=Matrix.Identity(4):continue
    candidates=[(v.index,cut_z(v.co)) for v in o.data.vertices if any(abs(v.co.x-c.x)<7 and abs(v.co.y-c.y)<7 for c,*_ in aprons)]
    changes=[(i,z) for i,z in candidates if o.data.vertices[i].co.z-z>.001]
    if changes:
        edit(o)
        for i,z in changes:o.data.vertices[i].co.z=z
        o.data.update()
terrain=index([o for o in grounds if soil(o)]);surface=index(grounds)
# Preserve soil depth, curb reveal and root contacts when cutting back an uphill frontage.
grade_changes={}
for o in orig:
    if o.type!='MESH':continue
    if o.name.startswith(('Planting_soil_','COL_Planting_low','Planting_leaf_litter_')):
        moves=[]
        for v in o.data.vertices:
            pos=o.matrix_world@v.co
            if not any(abs(pos.x-c.x)<6 and abs(pos.y-c.y)<6 for c,*_ in aprons):continue
            old=sample(pos.x,pos.y,old_terrain);now=sample(pos.x,pos.y,terrain)
            if old is not None and now is not None and old-now>.002:moves.append((v.index,now-old))
        if moves:
            edit(o)
            for ix,dz in moves:o.data.vertices[ix].co.z+=dz
            grade_changes[o.name]=len(moves)
    elif o.name.startswith('Soil_bed_') and any(abs(o.location.x-c.x)<6 and abs(o.location.y-c.y)<6 for c,*_ in aprons):
        old=sample(o.location.x,o.location.y,old_terrain);now=sample(o.location.x,o.location.y,terrain)
        if old is not None and now is not None and old-now>.002:
            edit(o);o.location.z+=now-old;grade_changes[o.name]=1
report['landscape_grade_contacts']=grade_changes
report['shutters']=[];report['primary_grade_repairs']=[]
for c,u,n,hw,f,id,before in aprons:
    after=[sample(*(c+u*dx+n*d),surface) for dx in [-1,0,1] for d in [.15,.7]]
    group='primary_grade_repairs' if id.startswith('entrance_') else 'shutters'
    report[group].append(dict(id=id,threshold=f,before=before,after=after))
    if id=='A05':views['shutter']=[list(c+n*3.1-u*2.3)+[f+1.65],list(c)+[f+1.35]]
# Rigidity is maintained on crates: fit a local plane through all eight corner feet.
# Retain joined slats, bottles and stacked upper crate as one assembly.
groups=defaultdict(list)
for o in orig:
    if o.name.startswith('CQF_Crates_'):groups[tuple(round(x,4) for x in o.location)].append(o)
stats=[]
for _,objects in groups.items():
    ref=objects[0];origin=ref.location.copy();rot=ref.matrix_world.to_3x3()
    feet=[rot@vec((x0+x,y0+y,0)) for x0,y0 in [(0,0),(.56,.05)] for x in [-.23,.23] for y in [-.21,.21]]
    heights=[sample(origin.x+q.x,origin.y+q.y,surface,origin.z+2) for q in feet]
    if None in heights:continue
    coeff=np.linalg.lstsq([[q.x,q.y,1] for q in feet],heights,rcond=None)[0]
    # Kerbs may cross the footprint; test offsets along the same pavement to find coherent support.
    best=None
    for dx,dy in [(0,0),(.38,0),(-.38,0),(0,.38),(0,-.38),(.72,0),(-.72,0),(0,.72),(0,-.72)]:
        hs=[sample(origin.x+q.x+dx,origin.y+q.y+dy,surface,origin.z+1.5) for q in feet]
        if None in hs:continue
        fit=np.linalg.lstsq([[q.x,q.y,1] for q in feet],hs,rcond=None)[0]
        err=max(abs(fit[0]*q.x+fit[1]*q.y+fit[2]-h) for q,h in zip(feet,hs))
        score=err+.012*math.hypot(dx,dy)
        if best is None or score<best[0]:best=(score,dx,dy,fit,hs)
        if dx==dy==0 and err<.011:break
    _,dx,dy,(sx,sy,z),hs=best
    normal=vec((-sx,-sy,1)).normalized();tilt=vec((0,0,1)).rotation_difference(normal).to_matrix().to_4x4()
    for o in objects:
        edit(o)
    yaw=rot.to_euler().z
    matrix=Matrix.Translation((origin.x+dx,origin.y+dy,z+.002))@tilt@Matrix.Rotation(yaw,4,'Z')
    for o in objects:o.matrix_world=matrix
    pts=[matrix@vec((x0+x,y0+y,0)) for x0,y0 in [(0,0),(.56,.05)] for x in [-.23,.23] for y in [-.21,.21]]
    gaps=[p.z-sample(p.x,p.y,surface,origin.z+2) for p in pts]
    # Extend only the low endpoints of the actual corner battens on irregular ground.
    # This keeps the slats square even where fitted feet have unequal lengths.
    inv=matrix.inverted();actual=[]
    for o in objects:
        if '_wood_dark' not in o.name:continue
        for v in o.data.vertices:
            if v.co.z>.0005:continue
            foot=matrix@v.co;h=sample(foot.x,foot.y,surface,origin.z+2)
            if h is not None:
                foot.z=h-.001;v.co=inv@foot;actual.append((matrix@v.co).z-h)
    stats.append(dict(center=list(origin),before_max_abs=max(abs(origin.z-h) for h in heights),rigid_fit_max_abs=max(map(abs,gaps)),after_max_abs=max(map(abs,actual)),translation=[dx,dy]))
report['crates']=stats
# A level seat with individually extended steel legs; when crossing a deck edge, prefer a
# coherent footprint on the same continuous surface. Test all five benches identically.
benches=[]
for x,y in [(-46,-9),(-46,9),(40,56),(-12,61),(-72,-35)]:
    feet=[(i*.65+j*.035,k*.275) for i in [-1,1] for j in [-1,1] for k in [-1,1]]
    def support(dx,dy):return [sample(x+dx+a,y+dy+b,surface) for a,b in feet]
    opts=[(dx,dy) for dx,dy in [(0,0),(.95,0),(-.95,0),(0,.75),(0,-.75)] if None not in support(dx,dy)]
    dx,dy=min(opts,key=lambda d:max(support(*d))-min(support(*d))+.085*math.hypot(*d))
    hs=support(dx,dy);floor=float(np.median(hs))
    frame=bpy.data.objects['Street_small_furniture_frame']
    old=min(v.co.z for v in frame.data.vertices if abs(v.co.x-x)<.95 and abs(v.co.y-y)<.48)
    for key in ['frame','timber']:
        o=edit(bpy.data.objects['Street_small_furniture_'+key])
        for v in o.data.vertices:
            p=v.co
            if abs(p.x-x)>.95 or abs(p.y-y)>.48:continue
            foot=key=='frame' and p.z<old+.015;p.x+=dx;p.y+=dy
            p.z=sample(p.x,p.y,surface)-.002 if foot else p.z+floor-old
    benches.append(dict(x=x,y=y,dx=dx,dy=dy,base=floor,before_gaps=[old-h for h in support(0,0)],foot_embed_m=.002))
report['benches']=benches
views['court_bench']=[[-43,-12.8,22.12],[-45,-9,20.98]]
# Fit sidewalls down to measured terrain only along unshared deck edges. No bridge IDs included.
wall=material('weathered_aggregate',(.245,.211,.168));V=[];F=[];skirt_count={}
for ob in grounds+[o for o in orig if o.name=='R21_Dressed_Central_steps']:
    is_road=ob.name.startswith('COL_Road_') and ob.name.endswith(('_pavement','_asphalt'))
    if is_road:
        road_id=ob.name.split('_')[2]
        if any(str(item['id'])==road_id and item['tags'].get('bridge')=='yes' for item in dl.DATA['roads']):continue
    if not is_road and not ob.name.startswith(('COL_Walk_','COL_Community_court_pavement','COL_Court_entry','R21_Dressed_Central_steps')):continue
    edges=defaultdict(list);me=ob.data
    for p in me.polygons:
        if abs(p.normal.z)<.65:continue
        ring=[ob.matrix_world@me.vertices[i].co for i in p.vertices]
        for a,b in zip(ring,ring[1:]+ring[:1]):
            # Only keep the highest of coincident underside / upper outlines.
            key=tuple(sorted(tuple(round(t,3) for t in v.xy) for v in (a,b)))
            if key[0]!=key[1]:edges[key].append((a,b,p.normal.z))
    faces0=len(F)
    for spans in edges.values():
        top=[(a,b) for a,b,n in spans if n>.6]
        if not top and len(spans)==1:top=[spans[0][:2]]
        if len(top)!=1:continue
        a,b=top[0];steps=max(1,math.ceil((a-b).length/.55))
        inward=vec((a.y-b.y,b.x-a.x,0)).normalized()*.018
        for j in range(steps):
            p=a.lerp(b,j/steps)+inward;q=a.lerp(b,(j+1)/steps)+inward
            hp=sample(p.x,p.y,terrain);hq=sample(q.x,q.y,terrain)
            if hp is None or hq is None or max(p.z-hp,q.z-hq)<.075:continue
            idx=len(V);V.extend([p,q,(q.x,q.y,min(q.z-.035,hq-.06)),(p.x,p.y,min(p.z-.035,hp-.06))]);F.append((idx,idx+3,idx+2,idx+1))
    if len(F)>faces0:skirt_count[ob.name]=len(F)-faces0
if V:mesh('COL_R23_PathFoundations',V,F,wall)
report['foundation_faces']=skirt_count
# Suppress interior units of the two intersecting kerbs using the union of both soil domains.
# Give elevated secondary shutters a supported apron and steps. Mesh bottoms follow the grade.
stair_mat=material('entrance_stone',(.28,.257,.211))
steps=[]
for c,u,n,hw,f,id,before in aprons:
    if id.startswith('entrance_'):continue
    hs=[sample(*(c+n*.46+u*s),surface) for s in [-hw*.8,0,hw*.8]]
    if None in hs or f-min(hs)<.14:continue
    vv=[];ff=[];count=max(1,math.ceil((f-min(hs))/.165))
    for j in range(count):
        d0=.008 if j==0 else .58+(j-1)*.31;d1=.58+j*.31
        top=f-.006-j*.16
        xy=[c+u*s+n*d for s,d in [(-hw-.05,d0),(hw+.05,d0),(hw+.05,d1),(-hw-.05,d1)]]
        low=[sample(*q,surface) for q in xy]
        if None in low or max(top-h for h in low)<.02:continue
        start=len(vv)
        vv.extend([(*q,min(h-.025,top-.034)) for q,h in zip(xy,low)]+[(*q,top) for q in xy])
        ff.extend([tuple(start+k for k in face) for face in [(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]])
    if ff:mesh('COL_R23_ShutterLanding_'+id,vv,ff,stair_mat);steps.append([id,len(ff)//5])
report['downhill_shutter_steps']=steps
def inside(p,poly):return dl.point_in_poly(p,poly)
beds=[b['points'] for b in land['beds']]
rings=[(t['point'],t['radius']) for t in land['tree_wells'] if any(s['name']==t['name'] and s['support'].endswith('tree well') for s in land['plant_support_records'])]
ed=edit(bpy.data.objects['COL_Planting_low_masonry_edges_stone']);bm=bmesh.new();bm.from_mesh(ed.data);bm.verts.ensure_lookup_table();delete=[]
for start in range(0,len(bm.verts),8):
    unit=[bm.verts[i] for i in range(start,start+8)]
    mid=sum((v.co for v in unit),Vector())/8
    inbed=any(inside(mid.xy,p) for p in beds);rad=[(math.dist(mid.xy,c),r) for c,r in rings]
    onring=any(abs(d-r)<.016 for d,r in rad)
    if (onring and inbed) or (not onring and any(d<r-.012 for d,r in rad)):delete.extend(unit)
removed_centres=[sum((v.co for v in delete[i:i+8]),Vector())/8 for i in range(0,len(delete),8)]
if removed_centres:
    q=min(removed_centres,key=lambda p:math.hypot(p.x+20,p.y+20));eye=q.xy+vec((2.3,-2.0))
    views['garden']=[[*eye,sample(*eye,surface)+1.62],list(q)]
bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(ed.data);bm.free()
report['overlapping_kerb_units_removed']=len(delete)//8
# Replace flat double-faced strips while retaining the wire and the original peg sockets.
cloth_colors=[(.10,.215,.194),(.50,.36,.24),(.14,.235,.31),(.57,.54,.43),(.31,.144,.128)]
clothm=[material('washed_cotton_%d'%i,c,.98) for i,c in enumerate(cloth_colors)]
cloth_count=0
for wire in [o for o in orig if o.name.startswith('CQF_Clothesline_') and o.name.endswith('black_metal')]:
    prefix=wire.name.rsplit('_black_metal',1)[0]
    for o in orig:
        if o.name.startswith(prefix+'_') and not o.name.endswith(('wood_light','black_metal')):
            removed.append(o.name);o.hide_render=True;o.hide_set(True)
    pegs=next(o for o in orig if o.name==prefix+'_wood_light')
    boxes=[sum((v.co for v in pegs.data.vertices[k:k+8]),Vector())/8 for k in range(0,len(pegs.data.vertices),8)]
    assert len(boxes)==10
    for i in range(5):
        a,b=boxes[2*i:2*i+2];seed=i+int(prefix.split('_')[-1]);rng=random.Random(seed)
        w=(b.x-a.x)+rng.uniform(.06,.12);cx=(a.x+b.x)/2;h=rng.uniform(.44,.71);phase=rng.uniform(0,6)
        verts=[];faces=[];uv=[]
        for row in range(15):
            v=row/14
            for col in range(21):
                u=col/20;pin=min(abs(cx+(u-.5)*w-a.x),abs(cx+(u-.5)*w-b.x))
                xx=cx+(u-.5)*w+v*v*.012*math.sin(phase+v*3)
                yy=.005+(.012+.032*v)*math.sin(u*math.tau*2.5+phase+v*.6)*min(1,v+.2+pin*5)+.028*v*v
                zz=a.z+.006-v*h-.022*min(1,pin*10)*(1-v)-.015*v*math.sin(phase+u*5)
                verts.append(pegs.matrix_world@vec((xx,yy,zz)));uv.append((u,v))
        for j in range(14):
            for k in range(20):
                ix=j*21+k;faces.append((ix,ix+21,ix+22,ix+1))
        ob=mesh('R23_Towel_%02d'%cloth_count,verts,faces,clothm[(i+abs(int(prefix.split('_')[-1])))%5])
        ob.data.uv_layers.new(name='Cotton')
        for p in ob.data.polygons:
            p.use_smooth=True
            for li in p.loop_indices:ob.data.uv_layers.active.data[li].uv=uv[ob.data.loops[li].vertex_index]
        cloth_count+=1
    if prefix.endswith('-343'):
        q=wire.matrix_world@vec((0,-3.4,-.22));t=wire.matrix_world@vec((0,0,-.31));views['laundry']=[list(q),list(t)]
report['towels']=cloth_count
# Keep the fall side and retire redundant inner rails only on complete, measured flights.
rail_report=[]
for path_name,pts,width in [('Central_stair_lane',dl.SPINE[:6],3.8),('West_residential_link',dl.SUPPLEMENTAL[1][1],2.7)]:
    o=bpy.data.objects.get('COL_Handrails_'+path_name+'_painted_metal')
    if not o:continue
    rules=[]
    for av,bv in zip(pts,pts[1:]):
        a,b=vec(av),vec(bv);u=(b-a).normalized();n=vec((-u.y,u.x))
        losses=[]
        for sign in [-1,1]:
            diffs=[]
            for t in [.2,.35,.5,.65,.8]:
                p=a.lerp(b,t)+n*(sign*(width/2-.16));q=p+n*(sign*.93)
                z=sample(*p,surface);h=sample(*q,surface)
                if z is not None and h is not None:diffs.append(z-h)
            losses.append(max(diffs,default=9))
        # Always retain one continuous grasp side even on a stair following the hillside.
        lesser=0 if losses[0]<losses[1] else 1
        if losses[lesser]<.31 and (b-a).length>9:
            rules.append((a,b,n,[-1,1][lesser]))
    if not rules:continue
    edit(o);bm=bmesh.new();bm.from_mesh(o.data)
    # Pipe meshes are disconnected across runs. Classify each whole member by its midpoint.
    pending=set(bm.verts);delete=[]
    while pending:
        start=pending.pop();part=[start]
        for v in part:
            for e in v.link_edges:
                other=e.other_vert(v)
                if other in pending:pending.remove(other);part.append(other)
        mid=sum((v.co for v in part),Vector())/len(part)
        for a,b,n,sign in rules:
            uv=mid.xy-a;along=uv.dot((b-a).normalized())
            if .6<along<(b-a).length-.6 and abs(uv.dot(n)-sign*(width/2+.15))<.19:
                delete+=part;break
    if delete:bmesh.ops.delete(bm,geom=delete,context='VERTS')
    bm.to_mesh(o.data);bm.free();rail_report.append([path_name,len(rules),len(delete)])
report['rails']=rail_report
# Extend selected, unshared street windows into free interior volume, maintaining a solid
# shell and the original front dressing. The back half gets shelves, containers and task lamps.
wood=material('oiled_bamboo',(.24,.144,.071));paint=material('aged_enamel',(.16,.26,.22))
ceramic=material('cream_crockery',(.61,.59,.47));clay=material('brown_jars',(.34,.15,.072))
metal=material('dull_aluminium',(.34,.35,.33));lamp=material('lit_opal',(.85,.72,.49))
bs=lamp.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.73,.41,1);bs.inputs['Emission Strength'].default_value=2
geo=defaultdict(lambda:[[],[]])
def part(mat,world,faces):
    vs,fs=geo[mat];k=len(vs);vs.extend(world);fs.extend(tuple(k+i for i in f) for f in faces)
def box(mat,at,sizes,to_world):
    x,y,z=at;w,d,h=[v/2 for v in sizes]
    pts=[to_world(x+i*w,y+j*d,z+k*h) for k in [-1,1] for j,i in [(-1,-1),(-1,1),(1,1),(1,-1)]]
    part(mat,pts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
def vessel(mat,x,y,z,profile,world):
    pts=[world(x+r*math.cos(k*math.tau/18),y+r*math.sin(k*math.tau/18),z+dz) for dz,r in profile for k in range(18)]
    faces=[(18*j+k,18*j+(k+1)%18,18*(j+1)+(k+1)%18,18*(j+1)+k) for j in range(len(profile)-1) for k in range(18)]
    part(mat,pts,faces)
rooms=[];lights=[]
for r in arch['buildings']:
    if str(r['id']) not in ['A01','809889623','A02','A05','A06']:continue
    shared={name for gr in r['interior_shared_rooms'] for name in gr['members']}
    es=r['facade_openings'][0];a=vec(es['a']);u=(vec(es['b'])-a).normalized();n=vec((-u.y,u.x))
    plans=r['interior_room_plans']
    choices=[p for p in plans if '_edge0_window' in p['room_id'] and p['room_id'] not in shared and p['storey'] in (0,1) and p['kind']=='window_room']
    for storey in [0,1]:
        options=sorted([p for p in choices if p['storey']==storey],key=lambda p:abs((vec(p['polygon_xy'][0])-a).dot(u)-(vec(es['b'])-a).length*.50))
        for plan in options:
            poly=[vec(v) for v in plan['polygon_xy']];tmin,tmax=min((v-a).dot(u) for v in poly),max((v-a).dot(u) for v in poly)
            dmin,dmax=min((v-a).dot(n) for v in poly),max((v-a).dot(n) for v in poly)
            if dmax>3.5:continue
            tf=(tmin+tmax)*.5;new=min(4.1,dmax+1.80)
            others=[q['polygon_xy'] for q in plans if q!=plan and q['storey']==storey]
            if any(inside(a+u*t+n*d,other) for t in [tmin+.03,tf,tmax-.03] for d in np.arange(dmax+.12,new+.01,.22) for other in others):continue
            floor=plan['floor_top_z'];ceil=plan['ceiling_z'];key='_B_'+str(r['id'])+'_'
            def world(x,d,z):
                q=a+u*(tf+x)+n*d;return (q.x,q.y,floor+z)
            count=0
            for o in orig:
                if not(o.name.startswith('IR_') and key in o.name and o.name.endswith(('room_wall','room_floor'))):continue
                pairs=[]
                for v in o.data.vertices:
                    p=v.co;q=p.xy-a;t=q.dot(u);d=q.dot(n)
                    if tmin-.004<=t<=tmax+.004 and dmin-.004<=d<=dmax+.004 and floor-.004<=p.z<=ceil+.004:
                        offset=(new-dmax)*max(0,(d-dmin)/(dmax-dmin));pairs.append((v.index,n*offset))
                if pairs:
                    edit(o)
                    for idx,delta in pairs:o.data.vertices[idx].co+=vec((*delta,0))
                    count+=len(pairs)
            if not count:continue
            w=tmax-tmin
            use='home' if storey else {'A01':'kitchen','A02':'repair','A05':'grocery','A06':'print','809889623':'grocery'}[str(r['id'])]
            shelves={'home':[1.56],'kitchen':[.86,1.79],'repair':[.92],'print':[.79,1.35],'grocery':[.75,1.25,1.78]}[use]
            for j,h in enumerate(shelves):
                box(wood,(0,new-.31,h),(w*.9,.39,.042),world)
                for i in range(5):
                    x=w*(i-2)*.15;y=new-.32+(i%2)*.045
                    if use=='print':
                        for sheet in range(4+(i%3)*2):box(ceramic,(x+.002*(sheet%2),y,h+.027+sheet*.011),(.18,.20,.01),world)
                    elif use=='repair':
                        box(metal,(x,y,h+.038),(.13,.026,.025),world)
                        vessel(paint,x+.045,y+.035,h+.024,[(0,.03),(.08,.032),(.09,.03)],world)
                    elif (storey+i+j)%3==0:
                        vessel(clay,x,y,h+.022,[(0,.047),(.03,.075),(.15,.073),(.18,.045),(.19,.044)],world)
                    elif (i+j)%2:
                        for k in range(3):vessel(ceramic,x,y,h+.023+k*.016,[(0,.035),(.016,.055),(.051,.092),(.053,.086),(.024,.048)],world)
                    else:box(paint if j%2 else ceramic,(x,y,h+.13),(.14,.13,.21),world)
            for x in [-w*.41,w*.41]:box(metal,(x,new-.23,1.27),(.028,.027,1.52),world)
            # A nearer counter returns into the room, so lateral movement reveals objects at
            # different depths. Keep the centre of the window and passage clear.
            hand=-1 if (storey+len(rooms))%2 else 1
            x=hand*(w*.50-.24);d=new-1.26
            box(wood,(x,d,.829),(.47,.98,.052),world)
            for lx in [-.18,.18]:
                for ly in [-.42,.42]:box(paint,(x+lx,d+ly,.412),(.034,.034,.823),world)
            if use=='kitchen':
                vessel(metal,x,d+.12,.86,[(0,.133),(.025,.164),(.224,.167),(.237,.172),(.242,.162),(.239,.145),(.261,.042),(.277,.022)],world)
                for sign in [-1,1]:box(metal,(x+sign*.174,d+.12,1.027),(.062,.084,.018),world)
                box(wood,(x,d-.27,.868),(.32,.24,.025),world)
            elif use=='home':
                box(wood,(x,d-.24,.873),(.27,.20,.026),world)
                box(ceramic,(x+.016,d-.24,.893),(.24,.19,.013),world)
                vessel(paint,x,d+.20,.859,[(0,.09),(.014,.093),(.034,.036),(.247,.025),(.255,.071)],world)
                vessel(ceramic,x,d+.20,1.09,[(0,.12),(.04,.111),(.14,.071)],world)
                sx=-hand*(w*.50-.28)
                for lx in [-.14,.14]:
                    for ly in [-.12,.12]:box(wood,(sx+lx,d+ly,.196),(.028,.028,.39),world)
                box(wood,(sx,d,.407),(.35,.31,.036),world)
                box(wood,(sx,d+.14,.625),(.33,.026,.17),world)
            elif use=='repair':
                for dx in [-.13,.13]:box(metal,(x+dx,d+.05,.914),(.073,.29,.11),world)
                box(paint,(x,d+.05,.90),(.23,.09,.065),world)
            else:
                for j in range(4):
                    box(clay if use=='grocery' else ceramic,(x,d-.25+j*.155,.944),(.21,.13,.17 if use=='grocery' else .095),world)
            fixture=world(w*.18,new-.92,ceil-floor-.25)
            vessel(lamp,w*.18,new-.92,ceil-floor-.32,[(0,.12),(.035,.15),(.095,.09)],world)
            lights.append(list(fixture))
            rooms.append(dict(id=plan['room_id'],use=use,old_depth=dmax,new_depth=new,vertices=count))
            if str(r['id'])=='A01' and storey==0:
                c=a+u*tf;eye=c-n*2.65+u*.43;views['shop_window']=[[*eye,floor+1.72],[*c,floor+1.70]]
            break
for m,(v,f) in geo.items():mesh('R23_Room_'+m.name,v,f,m)
report['rooms']=rooms
# Meter-sampled paths on imported road/pavement surfaces; XY layout source remains attributed.
def route(ids,offset,trees,lo=-98,hi=98):
    raw=[]
    for id in ids:
        item=next(r for r in dl.DATA['roads']+dl.DATA['paths'] if str(r['id'])==str(id))
        for p in item['points']:
            if not raw or p!=raw[-1]:raw.append(p)
    pts=[]
    for av,bv in zip(raw,raw[1:]):
        a,b=vec(av),vec(bv);uv=(b-a).normalized();n=vec((-uv.y,uv.x))
        for k in range(math.ceil((b-a).length/.82)):
            p=a.lerp(b,k/math.ceil((b-a).length/.82))+n*offset
            if not (lo<=p.x<=hi and abs(p.y)<98.8):continue
            h=sample(*p,trees)
            if h is not None:pts.append([round(p.x,4),round(h+.012,4),round(-p.y,4)])
    return pts
roads=index([o for o in grounds if o.name.endswith('_asphalt')])
routes={'west':route([1189963547,49182408],1.55,roads),'east':route([1189963598,830761786],1.2,roads)}
# The east frontage errand ends before the perpendicular stair flight.
routes['walk']=route([734116601],.23,surface,-78,4.5)
routes['promenade']=route([1189963547,49182408],-5.05,surface,-66,-19)
assert all(len(p)>28 for p in routes.values()),{k:len(v) for k,v in routes.items()}
# Continuous sidewalk on the north side of Nanqu Road, through the gravel/concrete
# material boundary. Recessed catch basins and a small tea table occupy the furniture strip.
prom=route([1189963547,49182408],-5.05,surface,-83,24)
asphalt_rows=[];footway=[];kerb=[];drains=[]
paving=material('sidewalk',(.31,.30,.26));curb=material('basalt_kerb',(.24,.23,.21))
iron=material('drain_iron',(.066,.067,.058));tea=material('worn_red',(.23,.048,.027))
def section(row,t):return row[0].lerp(row[1],t)
for i,pos in enumerate(prom):
    point=vec((pos[0],-pos[2]));v0=prom[max(0,i-1)];v1=prom[min(len(prom)-1,i+1)]
    direction=vec((v1[0]-v0[0],v0[2]-v1[2])).normalized()
    north=vec((direction.y,-direction.x))
    inner=point-north*1.79;outer=point+north*1.51
    zroad=sample(*(inner-north*.18),roads)
    if zroad is None:zroad=sample(*inner,surface)
    zfloor=sample(*outer,surface)
    if zroad is None or zfloor is None:continue
    base=zroad+.125
    outer_z=base+.059
    asphalt_rows.append((vec((*inner,base)),vec((*outer,outer_z))))
def band(name,partrows,mat):
    verts=[tuple(v) for row in partrows for v in row]
    faces=[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(partrows)-1)]
    # Reverse as required so walking collision and directional lighting see an upward normal.
    if (vec(verts[2])-vec(verts[0])).cross(vec(verts[3])-vec(verts[0])).z<0:faces=[f[::-1] for f in faces]
    return mesh(name,verts,faces,mat)
sidewalk=band('COL_R23_NanquSidewalk',asphalt_rows,paving);sidewalk.data.update()
station=[0.]
for ra,rb in zip(asphalt_rows,asphalt_rows[1:]):station.append(station[-1]+(rb[0]-ra[0]).length)
uv=sidewalk.data.uv_layers.new(name='Metres')
for loop in sidewalk.data.loops:
    j,k=divmod(loop.vertex_index,2);uv.data[loop.index].uv=(station[j],k*3.3)
# Excavate the existing substrate before laying the sidewalk. A centreline ray misses
# triangles protruding between sample rows. Subdivide the strip, then grade its full width.
cells=defaultdict(list)
for j,(row,nxt) in enumerate(zip(asphalt_rows,asphalt_rows[1:])):
    a,b=row;f=nxt[0].xy-a.xy;length=f.length
    if length<.001:continue
    for ix in range(math.floor((min(a.x,b.x,nxt[0].x,nxt[1].x)-2)/4),math.floor((max(a.x,b.x,nxt[0].x,nxt[1].x)+2)/4)+1):
        for iy in range(math.floor((min(a.y,b.y,nxt[0].y,nxt[1].y)-2)/4),math.floor((max(a.y,b.y,nxt[0].y,nxt[1].y)+2)/4)+1):
            cells[ix,iy].append((j,a,f/length,length))
def section_grade(pos):
    choices=cells.get((math.floor(pos.x/4),math.floor(pos.y/4)),[])
    nearest=None
    for j,a,f,length in choices:
        q=pos.xy-a.xy;t=min(length,max(0,q.dot(f)));v=q-f*t;dist=v.length
        if nearest and nearest[0]<=dist:continue
        side=(asphalt_rows[j][1].xy-a.xy).normalized()
        cross=v.dot(side);nearest=(dist,cross,a.z+(asphalt_rows[j+1][0].z-a.z)*t/length,j,t,length)
    if nearest is None:return None
    dist,cross,z,j,t,length=nearest
    if (j==0 and t<.0001) or (j==len(asphalt_rows)-2 and t>length-.0001):return None
    edge=max(-cross,cross-3.3,0)
    if edge>1.05:return None
    blend=max(0.,min(1.,(edge-.22)/.83));blend=blend*blend*(3-2*blend)
    return z+.059*max(0,min(cross/3.3,1.))-.105,1-blend
for o in [q for q in grounds if soil(q)]:
    bm=bmesh.new();bm.from_mesh(o.data)
    near_edges=[e for e in bm.edges if any(section_grade(v.co) for v in e.verts) or section_grade((e.verts[0].co+e.verts[1].co)*.5)]
    if not near_edges:bm.free();continue
    bmesh.ops.subdivide_edges(bm,edges=near_edges,cuts=2,use_grid_fill=True)
    count=0
    for v in bm.verts:
        grade=section_grade(v.co)
        if grade and v.co.z>grade[0]:
            v.co.z+=(grade[0]-v.co.z)*grade[1];count+=1
    if count:
        edit(o);bm.to_mesh(o.data);o.data.update()
    bm.free()
# Retain the uphill service terrace with a real stone stem and a sloping cap.
# Leave tapered cross-passages onto the upper frontage instead of fencing the sidewalk.
banks=[];caps=[];wall_faces=[];cap_faces=[];topsoil_index=old_terrain
for a,b in asphalt_rows:
    side=(b.xy-a.xy).normalized();c=b.xy+side*1.08
    bank=sample(*c,topsoil_index)
    if bank is None:bank=b.z
    open_factor=min(1.,max(0.,(min(abs(b.x-k) for k in [-82,-64,-45,-21,1,23])-1.)/2.0))
    top=b.z+max(0.,bank+.04-b.z)*open_factor
    front=b.xy+side*.016;rear=c
    banks.extend([(*front,b.z-.061),(*front,top)])
    caps.extend([(*front,top),(*rear,max(top,bank+.022))])
for i in range(0,len(banks)-2,2):
    if max(banks[i+1][2]-banks[i][2],banks[i+3][2]-banks[i+2][2])>.08:wall_faces.append((i,i+2,i+3,i+1))
    cap_faces.append((i,i+2,i+3,i+1))
bankwall=mesh('COL_R23_NanquRetaining',banks,[f[::-1] for f in wall_faces],wall)
cap=mesh('COL_R23_NanquUpperApron',caps,[f[::-1] for f in cap_faces],curb)
terrain=index([o for o in grounds if soil(o)])
walk_index=index([sidewalk]);exposed=[]
for row in asphalt_rows[2:-2]:
    for t in np.linspace(.02,.98,17):
        p=section(row,t);h=sample(*p.xy,terrain);z=sample(*p.xy,walk_index)
        if h is not None and z is not None:exposed.append(h-z)
report['pavement_substrate']={'sample_count':len(exposed),'highest_substrate_relative_to_pavement_m':max(exposed)}
for j,(a,b) in enumerate(asphalt_rows):
    kerb.append((a-vec((0,0,.022)),a-vec((0,0,max(.14,a.z-(sample(a.x,a.y,terrain) or a.z)+.05)))))
if kerb:
    vs=[tuple(v) for row in kerb for v in row];mesh('COL_R23_NanquCurb',vs,[(i,i+1,i+3,i+2) for i in range(0,len(vs)-2,2)],curb)
routes['promenade']=[]
for j,row in enumerate(asphalt_rows):
    p=section(row,.52)
    if -75<p.x<18:routes['promenade'].append([p.x,p.z+.006,-p.y])
    if j%18==8 and 2<j<len(asphalt_rows)-4:
        f=(asphalt_rows[j+1][0]-row[0]).normalized();g=(row[1]-row[0]).normalized();anchor=section(row,.085)
        def plane(x,y,z):return anchor+f*x+g*y+vec((0,0,z))
        box(iron,(0,0,.002),(.49,.18,.012),plane)
        for k in range(9):box(curb,(-.214+.053*k,0,.012),(.021,.148,.013),plane)
def pole(mat,a,b,rad,ring=10):
    a,b=vec(a),vec(b);f=(b-a).normalized();ref=vec((0,0,1)) if abs(f.z)<.85 else vec((1,0,0))
    i=f.cross(ref).normalized();j=f.cross(i).normalized()
    pts=[p+(i*math.cos(t*math.tau/ring)+j*math.sin(t*math.tau/ring))*rad for p in [a,b] for t in range(ring)]
    part(mat,pts,[tuple(range(ring))[::-1],tuple(range(ring,2*ring))]+[(t,(t+1)%ring,ring+(t+1)%ring,ring+t) for t in range(ring)])
# The public route stays on the inner half. Each furniture foot samples the new sidewalk.
walktree=index([sidewalk]);clearplane=lambda x,y:sample(x,y,walktree)
for spot in [-32,-52]:
    j=min(range(2,len(asphalt_rows)-2),key=lambda k:abs(asphalt_rows[k][0].x-spot))
    row=asphalt_rows[j];center=section(row,.82);f=(asphalt_rows[j+1][0]-row[0]);f.z=0;f.normalize();g=vec((f.y,-f.x,0))
    def world(x,y,z):return center+f*x+g*y+vec((0,0,z))
    def leg(mat,x,y,top,r):
        q=world(x,y,0);h=clearplane(q.x,q.y)
        if h is not None:pole(mat,(q.x,q.y,h-.002),world(x*.96,y,top),r)
    if spot==-32:
        for x in [-.28,.28]:
            for y in [-.21,.21]:leg(wood,x,y,.62,.024)
        for k in range(5):box(wood,(0,-.245+k*.12,.635),(.72,.113,.035),world)
        vessel(tea,.19,.063,.654,[(0,.064),(.05,.071),(.23,.065),(.26,.044),(.28,.04)],world)
        for x in [-.15,-.02]:
            vessel(ceramic,x,-.07,.654,[(0,.026),(.012,.04),(.069,.052),(.071,.048),(.024,.034)],world)
        for dx in [-.72,.71]:
            for sx in [-.14,.14]:
                for sy in [-.14,.14]:leg(wood,dx+sx,sy,.345,.020)
            for k in range(5):box(wood,(dx,-.155+k*.077,.35),(.37,.069,.034),world)
            for sy in [-.14,.14]:pole(wood,world(dx-.14,sy,.14),world(dx+.14,sy,.14),.014)
    else:
        for k in range(2):
            cx=k*.48
            box(tea,(cx,0,.031),(.44,.32,.036),world)
            for sy in [-.16,.16]:
                for j0 in range(3):box(tea,(cx,sy,.085+.066*j0),(.44,.016,.036),world)
                for sx in [-.206,0,.206]:box(tea,(cx+sx,sy,.144),(.023,.020,.24),world)
            for sx in [-.21,.21]:
                for j0 in range(3):box(tea,(cx+sx,0,.085+.066*j0),(.016,.32,.036),world)
            for kk in range(6):
                xx=cx-.13+(kk%3)*.13;yy=-.065+(kk//3)*.13
                vessel(paint,xx,yy,.055,[(0,.044),(.13,.045),(.19,.02),(.23,.018),(.235,.019)],world)
# Transfer newly authored street objects separately from pre-existing indoor batches.
for m,(v,f) in geo.items():
    if m in (wood,paint,ceramic,clay,metal,lamp):
        prev=next((o for o in extras if o.name=='R23_Room_'+m.name),None)
        first=len(prev.data.vertices) if prev is not None else 0
    else:first=0
    if len(v)>first:mesh('R23_Street_'+m.name,v[first:],[tuple(i-first for i in face) for face in f if min(face)>=first],m)
report['sidewalk_length_m']=sum((ra[0]-rb[0]).length for ra,rb in zip(asphalt_rows,asphalt_rows[1:]))
# Author a street-level camera facing along traffic and northward onto the shop row.
p=min(routes['promenade'],key=lambda point:abs(point[0]+38.))
views['main_road']=[[p[0],-p[2],p[1]+1.64],[p[0]+19,-p[2]+2.9,p[1]+2.02]]
for key,(eye,aim) in {'street_support':((-25.,-51.),(-19.,-48.)), 'brick':((-48.,-5.),(-53.,-1.))}.items():
    z=sample(*eye,surface);h=sample(*aim,surface)
    if z is not None and h is not None:views[key]=[[*eye,z+1.64],[*aim,h+.88 if key=='street_support' else z+2.1]]
report['route_samples']={k:len(v) for k,v in routes.items()}
write('routes.json',routes)
# Runtime swaps the edited meshes under the original donor nodes before collision compilation.
# Keep all original material assignments in the editable .blend. Export geometry-only donors.
scene['street_revision']='R23 environment working study'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(S/'chongqing_district.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
lookup={};dummy=material('material_slot',(.5,.5,.5))
for j,(name,o) in enumerate(changed.items()):
    assert len(o.data.materials)<=1,(name,len(o.data.materials))
    proxy=o.copy();proxy.data=o.data.copy();proxy.name='Swap%03d'%j;scene.collection.objects.link(proxy)
    proxy.modifiers.clear();proxy.data.materials.clear();proxy.data.materials.append(dummy);proxy.hide_set(False);proxy.hide_render=False
    proxy.select_set(True);lookup[proxy.name]=name
for o in extras:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'block.glb'),export_format='GLB',use_selection=True,export_animations=False,export_yup=True)
write('block.json',dict(donors=lookup,hide=removed,lights=lights,views={k:[[x,z,-y] for x,y,z in pair] for k,pair in views.items()}))
write('geometry_report.json',report)
print('R23_GEOMETRY',len(lookup),len(rooms),len(V),len(delete),flush=True)

