# Shared support samples for the twelve physical crates. Both stacked pairs keep their nesting.
terrain_objects=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Terrain_200m') and not o.hide_render]
terrain=Surfaces(terrain_objects)
def height(x,y,h):
    hits=terrain.down(x,y,h+1.3,3.0)
    return hits[0][0] if hits else None
measure['crates']=[]
for cluster in range(3):
    for column in range(2):
        objs=[scene.objects['Resident_storage_%d_%02d_00'%(cluster,i)] for i in (column,column+2)]
        lo,hi=extent(objs[0]);cx,cy=(lo[0]+hi[0])/2,(lo[1]+hi[1])/2
        corners=[(x,y) for x in [lo[0]+.012,hi[0]-.012] for y in [lo[1]+.012,hi[1]-.012]]
        heights=[height(x,y,lo[2]) for x,y in corners]
        sx=((heights[2]+heights[3])-(heights[0]+heights[1]))/(2*(hi[0]-lo[0]-.024))
        sy=((heights[1]+heights[3])-(heights[0]+heights[2]))/(2*(hi[1]-lo[1]-.024))
        base=Vector((cx,cy,lo[2]));rot=Vector((0,0,1)).rotation_difference(Vector((-sx,-sy,1)).normalized()).to_matrix().to_4x4()
        target=Vector((cx,cy,sum(heights)/4-.002))
        transform=Matrix.Translation(target)@rot@Matrix.Translation(-base)
        for ob in objs:
            ob.data=ob.data.copy()
            ob.data.transform(ob.matrix_world.inverted()@transform@ob.matrix_world);changed(ob)
        measure['crates'].append([objs[0].name,round(lo[2]-target.z,4),round(max(heights)-min(heights),4)])
# Re-seat the complete number 10 appliance on the masonry spandrel above the door.
origin=Vector((-59.6531,17.6796,21.544));normal=Vector((.4676,.88394,0)).normalized();side=Vector((normal.y,-normal.x,0))
wall_objects=[o for o in scene.objects if o.name.startswith('COL_B_1335306667') and not o.hide_render and o.type=='MESH' and 'pavement' not in o.name]
walls=Surfaces(wall_objects)
def backing(u,h):
    p=origin+side*u+Vector((0,0,h))+normal*.95
    hits=[walls.tree(o).ray_cast(p,-normal,1.3) for o in wall_objects]
    hits=[(v-origin).dot(normal) for v,n,i,d in hits if v is not None and abs(n.dot(normal))>.88]
    return max(hits) if hits else None
offset=None
for dh in [.04,.36,.65,1.68,2.05,2.55]:
    for du in [2.48,-3.12,3.15,-3.65,3.68,-4.22,4.18,-4.65,4.58]:
        hits=[backing(du+u,dh+h) for u in [.45,.606,.875,1.144,1.30] for h in [1.09,1.36,1.63,1.80]]
        if all(v is not None and abs(v+.10)<.13 for v in hits) and max(hits)-min(hits)<.025:
            offset=side*du+Vector((0,0,dh))+normal*(sum(hits)/len(hits)+.06);break
    if offset is not None:break
assert offset is not None
for u in [.606,1.144]:
    # Rubber isolators bear on the steel feet and meet the underside of the case.
    corners=[origin+offset+side*(u+dx)+normal*(.20+dy)+Vector((0,0,h)) for h in [1.208,1.237] for dx,dy in [(-.018,-.07),(.018,-.07),(.018,.07),(-.018,.07)]]
    for ids in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        face('Patrol25_HallHardware',[corners[i] for i in ids],'metal')
moved=0
for ob in scene.objects:
    if not ob.name.startswith('B_1335306667_brick_home_details_') or ob.name.split('_')[-1] not in ['offwhite','aluminium','dark','metal','frame','rust','paper'] and not ob.name.endswith('painted_metal'):continue
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
    free=set(bm.verts);count=0
    while free:
        vs=[free.pop()]
        for v in vs:
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in free:free.remove(other);vs.append(other)
        ps=[v.co-origin for v in vs]
        if all(.158<p.dot(side)<1.30 and -.213<p.dot(normal)<.51 and .74<p.z<1.81 for p in ps):
            for v in vs:v.co+=offset
            count+=1
    if count:finish(ob,bm);moved+=count
    else:bm.free()
measure['appliance']={'components':moved,'offset':list(offset),'wall_samples':hits}
# Civil surfaces abut on shared coordinates although exported in different material batches.
# Recompute corner normals across batches on residential grades. Preserve actual curbs and vertical faces.
fields=collections.defaultdict(lambda:Vector((0,0,0)));maps={}
def at_service(p):return -12<=p.x<=24 and 1<=p.y<=27
for ob in terrain_objects:
    rows=[]
    for f in ob.data.polygons:
        if f.normal.z<.58:continue
        for j in f.loop_indices:
            p=ob.data.vertices[ob.data.loops[j].vertex_index].co
            if not at_service(p) and not (-99.<p.x<98. and -83.<p.y<-40.):continue
            key=tuple(round(float(k),4) for k in p)
            fields[key]+=f.normal*f.area;rows.append((j,f.index,key))
    if rows:maps[ob]=rows
for ob,rows in maps.items():
    normals=[v.vector.copy() for v in ob.data.corner_normals]
    for j,idx,k in rows:
        old=ob.data.polygons[idx].normal
        new=fields[k].normalized()
        if old.dot(new)<.58:continue
        normals[j]=new;ob.data.polygons[idx].use_smooth=True
    ob.data.normals_split_custom_set(normals);ob.data.update();changed(ob)
measure['service_and_south_smoothed_corners']=sum(len(r) for r in maps.values())
# Account for the bank as one piece of masonry. Its original shader changed material
# with individual triangle steepness. Move the whole shoulder into one metric UV batch.
mat['bankstone']=bpy.data.materials['R18_unit22_edge']
bank='COL_Patrol25_CourtBank'
# Split along the toe and crest before assigning material. A centroid-only
# selection leaves a conspicuous sawtooth where the sloping bank meets the lane.
rectangles=[(-22.22,-20.,-15.,15.),(-48.,-45.83,-15.,15.),(-48.,-20.,-17.,-15.)]
def bank_zone(p):
    return any(x0-.00001<=p.x<=x1+.00001 and y0-.00001<=p.y<=y1+.00001 for x0,x1,y0,y1 in rectangles)
for ob in terrain_objects:
    bm=bmesh.new();bm.from_mesh(ob.data);removed=[]
    for axis,stations in enumerate([[-48.,-45.83,-22.22,-20.],[-17.,-15.,15.]]):
        for station in stations:
            active=[f for f in bm.faces if -50<f.calc_center_median().x<-18 and -19<f.calc_center_median().y<17 and min(v.co[axis] for v in f.verts)<station-.00001 and max(v.co[axis] for v in f.verts)>station+.00001]
            if not active:continue
            co=Vector();co[axis]=station;normal=Vector();normal[axis]=1.
            bmesh.ops.bisect_plane(bm,geom=list({g for f in active for g in [f,*f.edges,*f.verts]}),plane_co=co,plane_no=normal,dist=.000002)
    for f in bm.faces:
        c=f.calc_center_median()
        if not bank_zone(c):continue
        ps=[v.co.copy() for v in f.verts]
        face(bank,ps,'bankstone');removed.append(f)
    if removed:
        bmesh.ops.delete(bm,geom=removed,context='FACES');finish(ob,bm)
    else:bm.free()
measure['bank_faces']=len(batches[bank][1])

exec(compile((here/'grading.py').read_text('utf8'),str(here/'grading.py'),'exec'))
# Ground exposed tread ends and free sides where a separated stair ribbon floats above the actual hill.
# Retain the top face and its traffic profile. Build only along the perimeter of level tread polygons.
skirt='Patrol25_StairBeds';sections=[];dedup=set()
foundation=scene.objects['COL_R23_PathFoundations']
old_sides=Surfaces([foundation]).tree(foundation)
for ob in scene.objects:
    if ob.hide_render or not ob.name.startswith('COL_Walk_') or 'step_concrete' not in ob.name:continue
    topedges={}
    for f in ob.data.polygons:
        if f.normal.z<.98:continue
        ps=[ob.matrix_world@ob.data.vertices[i].co for i in f.vertices]
        for a,b in zip(ps,ps[1:]+ps[:1]):
            key=tuple(sorted((tuple(round(v,4) for v in a),tuple(round(v,4) for v in b))))
            if key in topedges:topedges[key]=None
            else:topedges[key]=(a,b)
    for key,pair in topedges.items():
        if not pair or key in dedup:continue
        a,b=pair;d=b-a;length=d.length
        if length<.10:continue
        exterior=Vector((d.y,-d.x,0)).normalized()
        m=(a+b)*.5
        h=height(m.x+exterior.x*.06,m.y+exterior.y*.06,m.z)
        if h is None or m.z-h<.095:continue
        # Existing next tread or solid side footing already supports this edge.
        local=road.down(m.x+exterior.x*.045,m.y+exterior.y*.045,m.z+.08,.24)
        if local and local[0][0]>=m.z-.087:continue
        n=max(1,math.ceil(length/.48))
        made=False
        for i in range(n):
            u=a.lerp(b,i/n);v=a.lerp(b,(i+1)/n)
            g1=height(u.x+exterior.x*.03,u.y+exterior.y*.03,u.z)
            g2=height(v.x+exterior.x*.03,v.y+exterior.y*.03,v.z)
            if g1 is None or g2 is None:continue
            mid=(u+v)*.5
            levels=[mid.z-.072,(mid.z+(g1+g2)*.5)*.5,(g1+g2)*.5+.023]
            if all(old_sides.ray_cast((mid.x+exterior.x*.08,mid.y+exterior.y*.08,h),-exterior,.16)[0] is not None for h in levels):
                continue
            # Inset from existing tread fascia to avoid coplanar faces.
            u-=exterior*.018;v-=exterior*.018
            face(skirt,[v,u,Vector((u.x,u.y,min(u.z-.09,g1-.055))),Vector((v.x,v.y,min(v.z-.09,g2-.055)))],'edge')
            made=True
        if made:sections.append([ob.name,[round(t,3) for t in m],round(m.z-h,3)])
        dedup.add(key)
measure['bedded_edges']=sections
exec(compile((here/'bench.py').read_text('utf8'),str(here/'bench.py'),'exec'))
measure['west_landing_bench']=move_bench(scene,terrain,finish)
# Seat the paired entry posts on the lower pavement beyond the tread junction.
post_ground=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('COL_Terrain_200m','COL_Walk_'))])
post_offsets={};measure['lower_gate_posts']=[]
for key in ['frame','paint_yellow']:
    ob=scene.objects['Street_small_furniture_'+key]
    bm,parts=bench_parts(ob,(14.,18.,-65.,-62.))
    for x in (15,17):
        groups=[vs for vs,c in parts if abs(c.x-x)<.02]
        if key=='frame':
            bottom=min(v.co.z for vs in groups for v in vs)
            floor=post_ground.down(x,-62.85,12.4,3.)[0][0]
            post_offsets[x]=floor-.005-bottom
            measure['lower_gate_posts'].append([x,-62.85,floor])
        for vs in groups:
            for v in vs:v.co+=Vector((0,1.15,post_offsets[x]))
    finish(ob,bm)
plants=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and ('soil' in o.name.lower() or o.name.startswith('COL_Terrain_200m')) and not o.name.startswith(('District_surface','Urban_paving'))])
measure['pavement_scatter']={}
for ob in scene.objects:
    if not ob.name.startswith('Planting_leaf_litter_gravel_and_seedlings_'):continue
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
    pool=set(bm.verts);remove=[]
    while pool:
        group=[pool.pop()]
        for v in group:
            for edge in v.link_edges:
                w=edge.other_vert(v)
                if w in pool:pool.remove(w);group.append(w)
        p=sum((v.co for v in group),Vector())/len(group)
        hits=plants.down(p.x,p.y,p.z+.35,1.0)
        if hits and hits[0][1] in ('COL_Terrain_200m_yard_concrete','COL_Terrain_200m_pavement','COL_Terrain_200m_stone'):
            remove.extend(group)
    measure['pavement_scatter'][ob.name]=len(remove)
    if remove:bmesh.ops.delete(bm,geom=remove,context='VERTS');finish(ob,bm)
    else:bm.free()
