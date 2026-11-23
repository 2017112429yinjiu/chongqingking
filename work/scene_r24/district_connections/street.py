# Court backstops. Preserve the original metal sections and wire diameter by
# extending each existing diagonal with new full-height diamonds instead of stretching the weave.
for name in ['Court_fence_and_hoops_frame','Court_fence_and_hoops_painted_metal']:
    obj=scene.objects[name]
    old_top=22.614 if name.endswith('frame') else 22.562
    floor=20.53;target=floor+4.05
    if name.endswith('frame'):
        for v in obj.data.vertices:
            # Preserve intermediate rails, post diameters and top rail section.
            if v.co.z>22.48:v.co.z+=target-old_top
        obj.data.update();mark(obj)
    else:
        bm=bmesh.new();bm.from_mesh(obj.data)
        # Repeat the original 2.12 m diamond panel at its native gauge. Clip its
        # upper and lower boundaries to the top rail and the original top seam.
        dup=bmesh.new();dup.from_mesh(obj.data)
        dz=2.12
        for v in dup.verts:v.co.z+=dz
        bmesh.ops.bisect_plane(dup,geom=list(dup.verts)+list(dup.edges)+list(dup.faces),plane_co=(0,0,target-.03),plane_no=(0,0,1),clear_outer=True,dist=1e-6)
        m=bpy.data.meshes.new('CourtTopMesh');dup.to_mesh(m);dup.free();bm.from_mesh(m);bpy.data.meshes.remove(m)
        bm.to_mesh(obj.data);bm.free();obj.data.update();mark(obj)
# Two west sideline seats. Their backs are now west, so both face the playing surface.
for key in ['frame','timber']:
    ob=scene.objects['Street_small_furniture_'+key]
    for center_y in [-9.,9.]:
        cx=-45.05;cy=center_y
        vs=[v for v in ob.data.vertices if abs(v.co.x-cx)<1.01 and abs(v.co.y-cy)<.38]
        assert vs
        for vertex in vs:
            q=vertex.co;dx=q.x-cx;dy=q.y-cy;q.x=cx-dy;q.y=cy+dx
        if key=='frame':layout['benches'].append({'centre':gd((cx,cy,20.53)),'forward':[1,0,0]})
    ob.data.update();mark(ob)

# Rejoin the two road cross sections over the length of the old abrupt cut.
from district_layout import DATA
roads=Surfaces([o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Road_') and o.name.endswith('_asphalt')])
road_walk=Surfaces([o for o in scene.objects if visible_ground(o) and not o.name.startswith(('COL_R23_Nanqu','Walk_details'))])
a_road=next(r for r in DATA['roads'] if str(r['id'])=='49182408')['points']
b_road=next(r for r in DATA['roads'] if str(r['id'])=='176034707')['points']
upper=next(r for r in DATA['paths']+DATA['roads'] if str(r['id'])=='734116598')['points']
def line_y(x,points):
    for a,b in zip(points,points[1:]):
        if min(a[0],b[0])-.00002<=x<=max(a[0],b[0])+.00002 and abs(b[0]-a[0])>.001:
            return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
    return min(points,key=lambda p:abs(p[0]-x))[1]
def smooth(v):v=max(0,min(1,v));return v*v*(3-2*v)
edge_obj=scene.objects['COL_R23_NanquSidewalk']
old=[edge_obj.matrix_world@v.co for v in edge_obj.data.vertices]
start=min([v for v in old if -1<v.x<3 and v.y<-80.8],key=lambda v:abs(v.x-1.))
start_x=start.x
def old_z(x,y,default):
    hits=road_walk.down(x,y,default+1.3,3)
    return hits[0][0] if hits else default
west_paving=Surfaces([o for o in scene.objects if o.type=='MESH' and (o.name.startswith(('COL_Terrain_200m','COL_R23_Nanqu','COL_Road_176034707_0_pavement','COL_Walk_OSM_734116598'))) and not o.hide_render])
sections=[];domains=[]
# End on the upper branch of the road fork; sample across the intact old paving there.
for ix in range(103):
    t=ix/102.;x=start_x+(47.-start_x)*t
    path=a_road if x<34.5216 else b_road
    centre_y=line_y(x,path)
    # Measured inner edge of the preserved lower footway, including its normal offset.
    verge=centre_y+(start.y-line_y(start_x,a_road))
    high_y=max(verge+4.6,line_y(x,upper)+2.15)
    ref=roads.down(x,verge-.32,18,13)
    zroad=ref[0][0] if ref else old_z(x,verge-.47,8.4)
    low=zroad+.125
    back=yard(x,high_y,low+.75)
    if back is None:back=old_z(x,high_y,low+.7)
    rise_width=high_y-verge-3.30
    distances=[0,1.45,2.8,3.30]+[3.30+rise_width*k/8 for k in range(1,9)]
    s=[];blend=smooth((x-start_x)/4.)
    for j,v in enumerate(distances):
        y=verge+v;z=low+min(v,1.45)*.016+(back-low-.023)*smooth((v-1.45)/(high_y-verge-1.45))
        if j==len(distances)-1:z=back
        if x<start_x+4:
            old_west=west_paving.down(start_x-.025,start.y+v,low+2.6,4.)
            z_high=old_west[0][0] if old_west else z
            sidewalk_z=low+min(v,3.0)*.017
            prev=sidewalk_z+(z_high-sidewalk_z)*smooth((v-2.82)/.97)
            z=prev+(z-prev)*blend
        if x>42:
            original=old_z(x,y,z)
            z=z+(original-z)*smooth((x-42)/5.)
        s.append((x,y,z))
    sections.append(s)
for a,b in zip(sections,sections[1:]):
    for j in range(len(a)-1):
        for tri in [[a[j],b[j],b[j+1]],[a[j],b[j+1],a[j+1]]]:
            uv=[(q[1]-(a[0][1] if q[0]==a[0][0] else b[0][1]),q[0]-start_x) for q in tri]
            surface_face('COL_D18_NanquShoulder',tri,'paver',uv)
    for j in [0,-1]:
        p,q=a[j],b[j]
        face('COL_D18_NanquShoulder',[p,q,(q[0],q[1],q[2]-.65),(p[0],p[1],p[2]-.65)],'mortar')
    domains.append(([a[0][:2],b[0][:2],b[-1][:2],a[-1][:2]],min(z[2] for z in a+b)-.95,max(z[2] for z in a+b)+.85))
    layout['banks'].append([gd(q) for q in a])
# Transverse boundary against the old street. Measure both lips and join them with an
# inward-bedded end face. Oblique sightlines at the west end used to escape under the street.
for row,dx in [(sections[0],-.14),(sections[-1],.14)]:
    for p,q in zip(row,row[1:]):
        end=[]
        for u in (p,q):
            hits=west_paving.down(u[0]+dx,u[1],u[2]+1.85,3.5)
            z=hits[0][0] if hits and abs(hits[0][0]-u[2])<1.3 else u[2]
            end.append((u[0]+dx,u[1],z-.032))
        e,g=end
        for tri in [[p,q,g],[p,g,e]]:topquad('D18_RoadEndBedding',tri,'mortar')
        for i,j in [(p,q),(q,g),(g,e),(e,p)]:
            wall=[i,j,(j[0],j[1],min(i[2],j[2])-.78),(i[0],i[1],min(i[2],j[2])-.78)]
            face('D18_RoadEndBedding',wall,'mortar');face('D18_RoadEndBedding',wall[::-1],'mortar')
bank_names=[o for o in scene.objects if o.type=='MESH' and (o.name.startswith(('COL_R23_Nanqu','COL_Terrain_200m','COL_Walk_OSM_734116598','Walk_details_OSM_734116598','COL_R23_PathFoundations','COL_R21_Footing_Entry_stair','COL_Walk_OSM_734116594_0_step_concrete','Walk_details_OSM_734116594','COL_Road_176034707_0_pavement','COL_Road_176034707_0_curb','District_surface_repairs_and_utilities','Urban_paving_joints')))]
for o in bank_names:
    low,high=bounds(o)
    if low[0]>48 or high[0]<start_x-.1 or high[1]<-84 or low[1]>-64:continue
    solid_clip(o,domains)
print('BANK18',start_x,len(sections),flush=True)

# This obsolete block occupied the exact roadside wedge that has just been rebuilt.
layout['retired']=[o.name for o in scene.objects if o.name.startswith('COL_R24_CloseTerrace_R24_corner_')]
# The road-side handrail belonged to the trim batch, not the separate handrail collection.
for ob in scene.objects:
    if not ob.name.startswith('Walk_details_') or not ob.name.endswith('_painted_metal'):continue
    route=ob.name[len('Walk_details_'):-len('_painted_metal')]
    if scene.objects.get('COL_Walk_'+route+'_step_concrete'):
        layout['retired'].append(ob.name)
        if ob.name in layout['changed']:layout['changed'].remove(ob.name)
for name in layout['retired']:
    o=scene.objects[name];o.hide_render=True;o.hide_set(True)

for end_y in [-15.5,15.5]:box('COLH_D18_CourtBackstops',(-34,end_y,22.48),(24,.045,4.15),'iron')
