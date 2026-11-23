from bisect import bisect_right
from itertools import accumulate
from mathutils.geometry import intersect_line_line_2d
stair_areas=[]
all_rows={}
for obj in scene.objects:
    if obj.type=='MESH' and obj.name.startswith('COL_Walk_') and obj.name.endswith('_step_concrete'):
        all_rows[obj.name]=tread_rows(obj.name)
def make_flight(key,first,last,width):
    source='COL_Walk_'+key+'_step_concrete';full=all_rows[source];rows=full[first:last+1]
    edges=[]
    for i,(centre,ring) in enumerate(rows):
        index=first+i
        aim=(full[min(index+1,len(full)-1)][0]-full[max(0,index-1)][0]).xy.normalized()
        sides=list(zip(ring,ring[1:]+ring[:1]))
        transverse=sorted(sides,key=lambda q:abs((q[1]-q[0]).xy.normalized().dot(aim)))[:2]
        ends=sorted([(a+b).xy*.5 for a,b in transverse],key=lambda q:q.dot(aim));edges.append(ends)
    knots=[edges[0][0]]+[(a[1]+b[0])*.5 for a,b in zip(edges,edges[1:])]+[edges[-1][1]]
    distance=[0.]+list(accumulate((b-a).length for a,b in zip(knots,knots[1:])))
    corners=[]
    for j in range(1,len(knots)-1):
        incoming=(knots[j]-knots[j-1]).normalized();outgoing=(knots[j+1]-knots[j]).normalized()
        if incoming.dot(outgoing)>.99995:continue
        radius=min(3.45,distance[j]-.1,distance[-1]-distance[j]-.1)
        if radius>.04:corners.append((distance[j],radius,knots[j],incoming,outgoing))
    def station(s):
        i=min(len(knots)-2,max(0,bisect_right(distance,s)-1))
        tangent=(knots[i+1]-knots[i]).normalized();pos=knots[i]+tangent*(s-distance[i])
        for centre,r,q,enter,leave in corners:
            if abs(s-centre)>r:continue
            t=(s-centre+r)/(2*r)
            pos=q-enter*(r*(1-t)**2)+leave*(r*t*t);tangent=(enter*(1-t)+leave*t).normalized();break
        return pos,Vector((-tangent.y,tangent.x))
    domains=[];last_top=None
    for i,(centre,ring) in enumerate(rows):
        h=centre.z;a=distance[i];b=distance[i+1];steps=max(1,math.ceil((b-a)/.68))
        prev_h=full[first+i-1][0].z if first+i>0 else h-.14
        # Flatten the top of every course; vertical faces share their neighbour's exact plan edge.
        pitch=width*.5;apron=1.12 if key.startswith('Central') else .78
        def section(t):
            pos,normal=station(a+(b-a)*t)
            left=pos+normal*pitch;right=pos-normal*pitch
            outer=[left+normal*apron,right-normal*apron]
            # Continuous flanks follow the rise, maintaining a small reveal at the stone nosing.
            z=prev_h+(h-prev_h)*t-.038
            bank=[]
            for side,end in enumerate(outer):
                g=yard(*end,h)
                if g is None:
                    direction=normal if side==0 else -normal
                    for offset in [.06,.16,.32,.60,1.]:
                        g=yard(*(end+direction*offset),h)
                        if g is not None:break
                bank.append(g if g is not None else z-.15)
            return left,right,outer,z,bank
        A=section(0.)
        for j in range(steps):
            B=section((j+1)/steps)
            l,r,outer,za,ba=A;m,n,far,zb,bb=B
            def at(p,z):return (p.x,p.y,z)
            d0=(b-a)*j/steps;d1=(b-a)*(j+1)/steps
            surface_face('COL_D18_StoneFlights',[at(l,h),at(r,h),at(n,h),at(m,h)],'stone',[(0,d0),(width,d0),(width,d1),(0,d1)])
            for side_idx,(u,v,edge1,edge2,z1,z2) in enumerate([(l,m,outer[0],far[0],ba[0],bb[0]),(r,n,outer[1],far[1],ba[1],bb[1])]):
                face('COL_D18_StoneFlights',[at(u,h),at(v,h),at(v,zb-.24),at(u,za-.24)][::1 if side_idx==0 else -1],'stone')
                # Split on a consistent diagonal on the authored hillside.
                for tri,uvs in [([at(u,za),at(v,zb),at(edge2,z2)],[(0,a+d0),(0,a+d1),(apron,a+d1)]),([at(u,za),at(edge2,z2),at(edge1,z1)],[(0,a+d0),(apron,a+d1),(apron,a+d0)])]:
                    surface_face('COL_D18_LaneShoulders',tri,'paver',uvs)
                # Bedding beneath the outer cut closes pinholes where the existing terrain triangles cross the seam.
                direction1=(edge1-u).normalized();direction2=(edge2-v).normalized()
                ext1=edge1+direction1*.19;ext2=edge2+direction2*.19
                for tri in [[at(edge1-direction1*.12,z1-.095),at(edge2-direction2*.12,z2-.095),at(ext2,z2-.095)],[at(edge1-direction1*.12,z1-.095),at(ext2,z2-.095),at(ext1,z1-.095)]]:
                    topquad('D18_BeddedEdges',tri,'mortar')
                face('COL_D18_LaneShoulders',[at(edge1,z1),at(edge2,z2),at(edge2,z2-.65),at(edge1,z1-.65)][::1 if side_idx==0 else -1],'mortar')
            if j==0:
                face('COL_D18_StoneFlights',[at(l,h),at(r,h),at(r,prev_h-.2),at(l,prev_h-.2)][::-1],'stone')
            domains.append(([outer[0],outer[1],far[1],far[0]],min(ba+bb+[h])-.93,h+.48))
            A=B
        pos,normal=station((a+b)*.5)
        layout['stairs'].append({'lane':key,'row':first+i,'point':gd((*pos,h)),'normal_xy':list(normal),'width':width})
    stair_areas.extend(domains)
    affected=[source,'Walk_details_'+key+'_stone','COL_N13_StairFoundations','COL_R23_PathFoundations',
              'COL_Terrain_200m_pavement','COL_Terrain_200m_yard_concrete','District_surface_repairs_and_utilities_soil_dark','Urban_paving_joints_and_repairs_soil_dark']
    if key.startswith('Central'):affected+=['R21_Dressed_Central_steps','COL_R19_Stair_retaining_stone','COL_R19_Stair_retaining_concrete']
    for name in affected:
        ob=scene.objects.get(name)
        if ob:solid_clip(ob,domains)
    print('FLIGHT18',key,len(rows),len(domains),flush=True)
make_flight('Central_stair_lane',2,23,3.80)
make_flight('East_photo_alley',19,32,2.50)

# Decorative seven-bar packets were scattered by distance along a path regardless of its use.
# Retire complete packets at stair footprints and turn seams. Keep the separately fitted downhill inlets.
def inside_pad(x,y,ring,pad=.22):
    sign=1 if sum(a.x*b.y-b.x*a.y for a,b in zip(ring,ring[1:]+ring[:1]))>0 else -1
    return all(sign*((b.x-a.x)*(y-a.y)-(b.y-a.y)*(x-a.x))>=-pad*(b-a).length for a,b in zip(ring,ring[1:]+ring[:1]))
records=json.loads((here.parent/'lane_connections/side_inlets/legacy_grate_contacts.json').read_text('utf8'))
for site in records['sites']:
    x,h,neg_y=site['position'];y=-neg_y
    if any(abs(centre.z-h)<.85 and abs(centre.x-x)<5 and abs(centre.y-y)<5 and inside_pad(x,y,[v.xy for v in ring],.35) for rows in all_rows.values() for centre,ring in rows):
        layout['drains'].append([x,y,h])
def remove_groups(ob,choose):
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world);todo=set(bm.verts);removed=[]
    while todo:
        group=[todo.pop()]
        for v in group:
            for e in v.link_edges:
                w=e.other_vert(v)
                if w in todo:todo.remove(w);group.append(w)
        center=sum((g.co for g in group),Vector())/len(group)
        if choose(center):removed+=group
    if removed:bmesh.ops.delete(bm,geom=removed,context='VERTS');finish(ob,bm)
    else:bm.free()
for name in ['Street_small_furniture_dark','Street_small_furniture_aluminium']:
    remove_groups(scene.objects[name],lambda p:any(abs(p.x-x)<.205 and abs(p.y-y)<.145 and abs(p.z-h)<.048 for x,y,h in layout['drains']))
# The corner bollards used to come through the pale stone treads. Move them to opposite verge sockets.
frame=scene.objects['Street_small_furniture_frame']; paint=scene.objects['Street_small_furniture_paint_yellow']
for ob in [frame,paint]:
    for vertex in ob.data.vertices:
        v=vertex.co
        for before,after in [(-22.,-23.80),(-20.,-16.45)]:
            if abs(v.x-before)<.10 and abs(v.y+50)<.10:
                old_base=12.565
                tip=yard(after,-49.7,12.6)
                if tip is not None:
                    from district_layout import ground_height
                    v.x+=after-before;v.y+=.30;v.z+=tip-(ground_height(before,-50)+.13)
                break
    ob.data.update();mark(ob)
