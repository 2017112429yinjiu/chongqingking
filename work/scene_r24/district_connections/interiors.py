# Back rooms are cut through the measured old lining. Reject space used by a
# neighbouring room on the same level. Keep the street facade and its glazing.
architecture=json.loads((work/'project/chongqing_blender_v05/architecture_manifest.json').read_text('utf8'))['buildings']
def overlaps(p,ring):
    inside=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>p.y)!=(b[1]>p.y) and p.x<(b[0]-a[0])*(p.y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside
def deepen(building,plan,shop,kind):
    polygon=[Vector(p) for p in plan['polygon_xy']]
    if len(polygon)!=4:return
    back=(polygon[0]+polygon[1])*.5;front=(polygon[2]+polygon[3])*.5
    inward=(back-front).normalized();side=Vector((inward.y,-inward.x))
    width=(polygon[0]-polygon[1]).length;old=(back-front).length;floor=plan['floor_top_z'];h=2.45 if shop else 2.54
    candidates=[o for o in scene.objects if o.type=='MESH' and ('B_'+str(building['id'])+'_') in o.name and (o.name.startswith(('COL_IR_','IR_','B_')))]
    shell=next((o for o in candidates if (o.name.endswith('Shop_envelope_plaster_grey') if shop else o.name.endswith('Interiors_room_wall'))),None)
    if not shell:return
    tree=Surfaces([shell]).tree(shell)
    def world(l,d,z):
        p=front+side*l+inward*d;return Vector((p.x,p.y,floor+z))
    p=world(0,.16,1.35);pt=tree.ray_cast(p,Vector((*inward,0)),8.)[0]
    if pt is None:return
    actual=(pt.xy-front).dot(inward)
    if actual<.85 or actual>5.0:return
    half=min(1.56 if shop else 1.09,width*.47-.025)
    if half<.58:return
    others=[q['polygon_xy'] for q in building['interior_room_plans'] if q['storey']==plan['storey'] and q['room_id']!=plan['room_id']]
    def free(d):
        for u in [-half-.09,0,half+.09]:
            p=world(u,d,0).xy
            if not overlaps(p,building['points']) or any(overlaps(p,ring) for ring in others):return False
        return True
    depth=actual
    for i in range(1,22):
        d=actual+i*.17
        if not free(d):break
        depth=d
        if depth>= (5.65 if shop else 4.70):break
    if depth-actual<1.15:return
    # Preserve complete small objects attached to the former back wall by moving them into the rear bay.
    # The lining, wall tile and length of the original structural box are cut separately.
    noodle=plan['room_id']=='A01_edge2_door'
    for obj in candidates:
        if not obj.name.startswith('IR_') or not '_Interiors_' in obj.name or obj.name.endswith(('_room_wall','_room_floor')):continue
        key=obj.name.rsplit('_Interiors_',1)[-1]
        if noodle and key not in ('tile','tile_cream'):
            def within_front(c):
                q=c.xy-front
                return -.18<q.dot(inward)<actual+.14 and abs(q.dot(side))<width*.57 and -.17<c.z-floor<h+.39
            remove_groups(obj,within_front)
            continue
        if shop and key in ('tile_cream','tile'):continue
        bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world);todo=set(bm.verts);moved=False;remove=[]
        while todo:
            group=[todo.pop()]
            for v in group:
                for e in v.link_edges:
                    w=e.other_vert(v)
                    if w in todo:todo.remove(w);group.append(w)
            c=sum((v.co for v in group),Vector())/len(group);xy=c.xy-front
            if not(floor+.01<c.z<floor+h+.1 and abs(xy.dot(side))<(width*.51 if shop else half+.08) and actual-.77<xy.dot(inward)<actual+.11):continue
            if shop:
                depth_at=xy.dot(inward)
                span=max((v.co.xy-front).dot(side) for v in group)-min((v.co.xy-front).dot(side) for v in group)
                is_caption=span>.69 and floor+1.55<c.z<floor+2.59 and abs(depth_at-(actual-.13))<.15
                sign_face=key=='faded_red' and span>1 and floor+1.45<c.z<floor+2.25
                if noodle and not sign_face:
                    remove.extend(group);continue
                if is_caption or sign_face:continue
                # Transfer the whole rear fit-out as an assembly. Keep fragments and their crockery together.
                if abs(xy.dot(side))>width*.51 or xy.dot(inward)<actual-.64:continue
                for v in group:
                    l=(v.co.xy-front).dot(side)
                    v.co+=Vector((*inward,0))*(depth-actual+.035)+Vector((*side,0))*(-.33*l)
            else:
                if max(abs((v.co.xy-front).dot(side)) for v in group)>half+.13:continue
                for v in group:v.co+=Vector((*inward,0))*(depth-actual-.09)
            moved=True
        if remove:bmesh.ops.delete(bm,geom=remove,context='VERTS');moved=True
        if moved:finish(obj,bm)
        else:bm.free()
    hole=[world(l,d,0).xy for l,d in [(-half,actual-.34),(half,actual-.34),(half,actual+.28),(-half,actual+.28)]]
    openings=0
    for ob in candidates:
        if ob==shell or (shop and ob.name.endswith(('Interiors_tile_cream','Interiors_tile'))):
            openings+=solid_clip(ob,[(hole,floor-.015,floor+h-.10)])
    if openings==0:raise RuntimeError(('opening missing',plan['room_id'],actual))
    if noodle:
        # Retire the old red board and its geometric text together. Keep the exterior sign and prices.
        for caption in scene.objects:
            if caption.type!='MESH' or not caption.name.startswith('Type_'):continue
            lo,hi=extent(caption);m=(Vector(lo)+Vector(hi))*.5;q=m.xy-front
            if abs(q.dot(inward)-(actual-.1))<.15 and abs(q.dot(side)-.76)<.38 and abs(m.z-floor-1.73)<.22:
                layout['retired'].append(caption.name);caption.hide_render=True;caption.hide_set(True)
    # One connected space with a front counter/window, a pass-through and a furnished back wall.
    start=actual+.008;rear=depth+.09
    name='COL_D18_RoomShells'
    def part(name,l,d,z,sw,sd,sh,key):
        a=sw*.5;b=sd*.5;c=sh*.5
        pts=[world(l+i*a,d+j*b,z+k*c) for k in [-1,1] for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        for idx in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[pts[t] for t in idx],key)
    part(name,0,(start+rear)*.5,-.037,half*2+.12,rear-start,.075,'kitchenfloor' if noodle else ('cement' if shop else 'timber'))
    part(name,0,(start+rear)*.5,h+.015,half*2+.12,rear-start,.07,'noodleplaster' if noodle else 'lime')
    for sign in [-1,1]:part(name,sign*(half+.036),(start+rear)*.5,h*.5,.07,rear-start,h,'noodleplaster' if noodle else 'wall')
    part(name,0,rear,h*.5,half*2+.14,.075,h,'noodleplaster' if noodle else ('deepgreen' if shop else 'lime'))
    furniture='D18_BackRoomFurnishings'
    for side_sign in [-1,1]:
        part(furniture,side_sign*(half-.024),actual+.015,1.17,.058,.14,2.34,'noodleplaster' if noodle else 'timber')
    part(furniture,0,actual+.015,h-.11,half*2+.12,.15,.09,'noodleplaster' if noodle else 'timber')
    # Rear bench, under-counter cupboards, rails and everyday items occupy different depth planes.
    if noodle:
        noodle_kitchen(world,part,half,rear,actual)
    else:
        bench_d=depth-.42;wide=half*1.48
        part(furniture,-half*.12,bench_d,.87,wide,.48,.065,'porcelain' if shop else 'timber')
        for j in [-1,1]:
            part(furniture,-half*.12+j*(wide*.5-.065),bench_d,.43,.075,.40,.86,'redwood')
        part(furniture,-half*.12,bench_d+.17,.47,wide-.12,.047,.65,'bluegrey')
        part(furniture,half-.128,depth-1.,1.52,.256,.57,.043,'timber')
        for stud in [-.206,.206]:
            part(furniture,half-.018,depth-1.+stud,1.417,.045,.03,.181,'iron')
            part(furniture,half-.113,depth-1.+stud,1.485,.217,.031,.026,'iron')
        for j in range(4):
            part(furniture,-half*.46+j*.19,bench_d,.98,.095,.105,.17+(.052 if j%2 else 0),['porcelain','bluegrey','ochre','lime'][j])
        # A lit upper cupboard and pendant make the rear plane legible through the front opening.
        part(furniture,-half*.37,depth-.09,1.73,min(.94,half),.16,.57,'timber')
        part(furniture,-half*.37,depth-.182,1.73,min(.82,half*.9),.028,.43,'bluegrey')
        part(furniture,half*.38,depth-.65,h-.19,.022,.022,.30,'iron')
        part(furniture,half*.38,depth-.65,h-.36,.31,.20,.045,'porcelain')
    if shop:
        # A solid transom carries the original sign board and its lettering. The pass-through below stays open.
        if not noodle:part(furniture,0,actual+.015,h-.20,half*2+.11,.17,.36,'redwood')
        # Seat the old menus against the transom, along with their separately authored glyphs.
        # All bits of a sign receive exactly the same translation, including rotated shop fronts.
        for board in [ob for ob in candidates if ob.name.endswith(('Interiors_faded_red','Interiors_timber'))]:
            bm=bmesh.new();bm.from_mesh(board.data);bm.transform(board.matrix_world);todo=set(bm.verts);updated=False
            while todo:
                group=[todo.pop()]
                for v in group:
                    for edge in v.link_edges:
                        other=edge.other_vert(v)
                        if other in todo:todo.remove(other);group.append(other)
                c=sum((v.co for v in group),Vector())/len(group);q=c.xy-front
                span=max((v.co.xy-front).dot(side) for v in group)-min((v.co.xy-front).dot(side) for v in group)
                vertical=max(v.co.z for v in group)-min(v.co.z for v in group)
                if abs(q.dot(inward)-(actual-.13))>.15 or abs(q.dot(side))>half or span<.69 or not .41<vertical<.63 or not floor+1.5<c.z<floor+2.61:continue
                glyphs=[]
                for lab in scene.objects:
                    if lab.type!='MESH' or not lab.name.startswith('Type_'):continue
                    lo,hi=extent(lab);middle=(Vector(lo)+Vector(hi))*.5;delta=middle-c
                    if abs(delta.xy.dot(inward))<.10 and abs(delta.xy.dot(side))<.17 and abs(delta.z)<.20:glyphs.append(lab)
                move=Vector((*inward,0))*(actual-.093-q.dot(inward))+Vector((0,0,floor+h-.23-c.z))
                for vert in group:vert.co+=move
                for lab in glyphs:
                    for vert in lab.data.vertices:vert.co=lab.matrix_world.inverted()@(lab.matrix_world@vert.co+move)
                    lab.data.update();mark(lab)
                updated=True
            if updated:finish(board,bm)
            else:bm.free()
        # Front, middle and rear are spatially separate. Fixtures differ with the use of the building.
        if building['id']=='A02':
            part(furniture,-half+.10,depth-.85,1.38,.13,1.38,.98,'timber')
            for j in range(6):
                part(furniture,-half+.175,depth-1.35+j*.17,1.29,.045,.055,.31+j%2*.09,'iron')
        elif building['id']=='A05':
            for j in range(3):
                for k in range(4):part(furniture,half-.37,depth-.76-j*.35,.18+k*.087,.57,.28,.052,'timber')
        elif building['id']=='A06':
            part(furniture,half-.43,depth-.89,.74,.72,.78,.72,'bluegrey')
            for j in range(4):part(furniture,half-.43,depth-.9,.83+j*.08,.62,.48,.04,'lime')
        elif not noodle:
            for j in [-1,1]:
                part(furniture,-half+.37,depth-1.17,1.05+j*.11,.55,.70,.075,'bluegrey')
    eye=world(half*.28,-3.6,1.64);aim=world(-half*.18,depth-.15,1.22)
    layout['rooms'].append({'id':plan['room_id'],'type':kind,'front':gd((*front,floor)),'inward':[inward.x,0,-inward.y],'half':half,'old_depth':actual,'new_depth':depth,'top':h,'light':gd(world(0,depth-.98,h-.45)),'eye':gd(eye),'aim':gd(aim),'portal_faces':openings})
for id,edge,order in [('A01',0,1),('A04',3,1),('A06',0,1),('A05',0,1)]:
    b=next(k for k in architecture if str(k['id'])==id)
    shops=[r for r in b['interior_room_plans'] if r['room_id'].endswith('_door') and any(e['type']=='shop' for e in b['entrances'])]
    for plan in shops:deepen(b,plan,True,'shop')
    windows=[r for r in b['interior_room_plans'] if r['storey']==0 and ('_edge'+str(edge)+'_window') in r['room_id']]
    for plan in windows[1:-1][:2]:deepen(b,plan,False,'flat')
b=next(k for k in architecture if str(k['id'])=='A02')
deepen(b,next(r for r in b['interior_room_plans'] if r['room_id'].endswith('_door')),True,'repair_shop')
print('INTERIORS18',[(r['id'],r['new_depth']) for r in layout['rooms']],flush=True)

# The grocery visible alongside the reported long flight has a rotated front.
for id in ['809889623','A07','809889629','1335306666','809889626','809889622']:
    b=next((k for k in architecture if str(k['id'])==id),None)
    if b is None:continue
    for plan in b['interior_room_plans']:
        if plan['room_id'].endswith('_door') and plan.get('storey',0)==0:
            deepen(b,plan,True,'shop');break
