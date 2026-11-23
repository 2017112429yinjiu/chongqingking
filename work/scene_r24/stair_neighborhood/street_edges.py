import numpy as np
# Use the bottom contact vertices of the complete prop, preserving the relations between its parts.
for_support=Surfaces([o for o in scene.objects if visible_ground(o) or (o.type=='MESH' and not o.hide_render and (o.name.startswith('COL_B_') and o.name.endswith('_pavement') or o.name.startswith('COL_Stairside_resident_planter_soil')))])
boundaries=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_Resident_court_boundary_')])
def surface_at(x,y,z):
    hits=for_support.down(x,y,z+1.26,2.52)
    return min(hits,key=lambda r:abs(r[0]-z)) if hits else None
def gm(m):
    cv=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));k=cv@m@cv.inverted()
    return [[k[row][col] for row in range(3)] for col in range(4)]
visible_names={r[0] for r in json.loads((root.parent/'street_photo_study/materials.json').read_text('utf-8-sig'))}
groups=defaultdict(list)
for o in scene.objects:
    if o.type!='MESH' or o.hide_render or o.name.replace('.','_') not in visible_names:continue
    n=o.name
    if n.startswith(('CQF_Crates_','CQF_Bins_')):
        i=re.search(r'[._](\d{3})$',n)
        groups[n.split('_')[1]+'_'+(i.group(1) if i else '000')].append(o)
    elif (m:=re.match(r'((?:R19_Service_)?Resident_waste_\d+_(?:bin|crate|bagA|bagB))_',n)):groups[m[1]].append(o)
adjustments=[];groundaudit=[]
for key,objs in groups.items():
    pts=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
    # An authored crate may already lean with the street. Identify its underside in the prop frame.
    axis=(objs[0].matrix_world.to_3x3()@Vector((0,0,1))).normalized() if key.startswith(('Crates_','Bins_')) else Vector((0,0,1))
    if axis.z<.85:axis=Vector((0,0,1))
    low=min(p.dot(axis) for p in pts);base=[p for p in pts if p.dot(axis)<low+.023]
    # Retain the lowest vertex in each 7 cm patch. Concentrated cap/trim vertices do not dominate the fit.
    foot={}
    for p in base:
        k=(round(p.x/.07),round(p.y/.07))
        if k not in foot or foot[k].z>p.z:foot[k]=p
    pts=list(foot.values())
    if len(pts)<3:continue
    origin=sum(pts,Vector((0,0,0)))/len(pts)
    def fit(dx,dy):
        hits=[surface_at(p.x+dx,p.y+dy,p.z) for p in pts]
        if any(r is None for r in hits):return None
        A=np.array([(p.x-origin.x,p.y-origin.y,1.) for p in pts])
        corrections=np.array([h[0]-p.z for h,p in zip(hits,pts)])
        grad=np.linalg.lstsq(A,corrections,rcond=None)[0]
        angle=math.atan(math.hypot(*grad[:2]))
        if angle>math.radians(20):return None
        rot=Vector((0,0,1)).rotation_difference(Vector((-grad[0],-grad[1],1)).normalized()).to_matrix().to_4x4()
        m=Matrix.Translation(origin+Vector((dx,dy,grad[2])))@rot@Matrix.Translation(-origin)
        out=[m@p for p in pts]
        support=[surface_at(p.x,p.y,p.z) for p in out]
        if any(q is None for q in support):return None
        residual=[p.z-r[0] for p,r in zip(out,support)]
        lift=-min(residual)-.001;m=Matrix.Translation((0,0,lift))@m
        seated=[m@p for p in pts]
        if any(any(q[0]>p.z+.012 for q in boundaries.down(p.x,p.y,p.z+2.10,2.18)) for p in seated):return None
        return max(residual)-min(residual),m,max(abs(v) for v in corrections),[gvec(m@p) for p in pts]
    pre=[surface_at(p.x,p.y,p.z) for p in pts]
    if None in pre:
        if any(abs(p.x)>99.95 or abs(p.y)>99.95 for p in pts):
            for ob in objs:retire(ob);retired.append(ob.name)
            groundaudit.append({'group':key,'status':'outside_authored_ground'})
        else:groundaudit.append({'group':key,'status':'no_complete_support'})
        continue
    initial=max(abs(p.z-h[0]) for p,h in zip(pts,pre))
    current=fit(0,0)
    if initial<.015 and current is not None:groundaudit.append({'group':key,'status':'already_seated','before':initial,'contacts':[gvec(p) for p in pts]});continue
    if current is None or current[0]>.043:
        # Adjacent positions are accepted only on the same receiving ground meshes.
        originals={h[1] for h in pre}
        for dx,dy in [(d*math.cos(a*math.pi/4),d*math.sin(a*math.pi/4)) for d in (.17,.30,.45,.63,.85,1.10,1.40,1.75,2.10) for a in range(8)]:
            shifted=[surface_at(p.x+dx,p.y+dy,p.z) for p in pts]
            if any(not h or h[1] not in originals for h in shifted):continue
            trial=fit(dx,dy)
            if trial and (current is None or trial[0]<current[0]):current=trial
            if current and current[0]<.018:break
    if current is None or current[0]>.055 or current[2]>.90:
        groundaudit.append({'group':key,'status':'uneven_support','before':initial,'center':gvec(origin),'feet':[gvec(p) for p in pts],'hit':list(originals) if 'originals' in locals() else []});continue
    err,m,_,points=current
    for o in objs:o.matrix_world=m@o.matrix_world
    adjustments.append({'group':key,'names':[o.name.replace('.','_') for o in objs],'transform':gm(m),'before':initial,'after':err,'contacts':points})
    groundaudit.append({'group':key,'status':'adjusted','before':initial,'after':err})
# Shared plant meshes retain the licensed maps already loaded by the base city.
plant_instances=[];beds=[]
def plant(donors,x,y,z,scale,angle):
    parts=[scene.objects[k] for k in donors]
    bounds=[o.matrix_world@Vector(c) for o in parts for c in o.bound_box];base=Vector(((min(v.x for v in bounds)+max(v.x for v in bounds))/2,(min(v.y for v in bounds)+max(v.y for v in bounds))/2,min(v.z for v in bounds)))
    move=Matrix.Translation((x,y,z))@Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-base)
    index=len(plant_instances)
    for j,o in enumerate(parts):
        dup=o.copy();dup.data=o.data;dup.parent=None;dup.matrix_world=move@o.matrix_world;dup.name=f'N13_Greenery_{index:02d}_{j}';collection.objects.link(dup)
    plant_instances.append({'donors':donors,'transform':gm(move),'at':gvec(Vector((x,y,z))),'scale':scale})
shrub=['Soil_bed_central_upper_west_shrub_0%d_00'%i for i in range(3)]
tree=['Planted_tree_04_%02d'%i for i in range(3)]
pot=['B_809889623_market_Interior_asset_0_%02d'%i for i in range(3)]
def pit(x,y,r,tree_scale=0.):
    center=floors(x,y)
    if not center:raise ValueError((x,y))
    z=center[0][0];n=22
    rim=[]
    for i in range(n):
        a=i*math.tau/n;xx=x+r*math.cos(a);yy=y+r*math.sin(a);hits=for_support.down(xx,yy,z+.65,1.55)
        if not hits:return
        rim.append((xx,yy,hits[0][0]))
    if (max(q[2] for q in rim)-min(q[2] for q in rim))>.58:return
    # Taper the base into each sampled corner. The planting surface sits under the rim.
    top=max(q[2] for q in rim)+.16
    v=[];f=[]
    for xx,yy,zz in rim:v.extend([(xx,yy,zz-.035),(xx,yy,top),(x+(xx-x)*.89,y+(yy-y)*.89,top),(x+(xx-x)*.89,y+(yy-y)*.89,top-.072)])
    for i in range(n):
        j=(i+1)%n
        f.extend([(4*i,4*j,4*j+1,4*i+1),(4*i+1,4*j+1,4*j+2,4*i+2),(4*i+2,4*j+2,4*j+3,4*i+3)])
    add('COL_N13_PlantingRims',v,f,'cement');add('N13_PlantingSoil',[(q[0],q[1],top-.066) for q in v[3::4]],[tuple(range(n))],'soil')
    if tree_scale:plant(tree,x,y,top-.12,tree_scale,rng.random()*6)
    count=4 if r>.8 else 2
    for j in range(count):
        a=(j+rng.uniform(-.13,.13))*math.tau/count
        plant([shrub[(len(beds)+j)%3]],x+math.cos(a)*r*.49,y+math.sin(a)*r*.49,top-.088,rng.uniform(.48,.76),rng.random()*6)
    beds.append({'center':[x,top,-y],'radius':r,'tree':tree_scale})
for x,y,r,scale in [(-12.6,-16.8,1.13,.47),(-75.90,-19.1,.85,.41),(-37.2,-74.9,.86,.40),(-9.1,-73.9,.69,0),(-68.3,-10.1,.65,0),(-13.35,-27.,.72,0),(-40.6,-56.8,.80,.36),(-54.2,-71.8,.90,.38)]:pit(x,y,r,scale)
# Make isolated pots on flat, protected thresholds only.
for x,y,sc in [(-76.95,-16.45,1.45),(-76.40,-16.23,.97),(-14.6,-73.15,1.25),(-14.9,-73.1,.9),(-47.0,-72.65,1.38),(-47.4,-72.65,.89)]:
    hit=floors(x,y)
    if not hit:continue
    z=hit[0][0]; corners=[surface_at(x+dx,y+dy,z) for dx,dy in [(-.10,0),(.10,0),(0,-.10),(0,.10)]]
    if all(corners) and max(q[0] for q in corners)-min(q[0] for q in corners)<.070:plant(pot,x,y,z-.006,sc,rng.random()*6)
# Route heights come from the actual tread tops, with the body grounded again at runtime.
walks={}
for name,arr in stairs.items():
    use=[p for p in arr if (5<p[2]<51 if name=='central' else -1<p[2]<40)]
    walks[name+'_stairs']=use
market=[]
for x,z in [(-48,75.2),(-43.5,75.9),(-38.1,76.34),(-34.,76.51),(-29.55,77.05),(-25.,76.42),(-21.55,76.24),(-17.1,75.88),(-13.95,75.76),(-10.7,75.74)]:
    h=floors(x,-z)
    if h:market.append([x,h[0][0],z])
walks['market_apron']=market

