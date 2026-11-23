# Keep poles vertical and their round bases outside the tread. A short stone socket takes up crossfall.
lamps=defaultdict(list)
for ob in scene.objects:
    if ob.type=='MESH' and ob.name.startswith('CQF_StreetLamp_') and ob.name.replace('.','_') in visible_names:
        ix=re.search(r'[._](\d{3})$',ob.name);lamps[ix[1] if ix else '000'].append(ob)
for key,parts in lamps.items():
    steel=next((p for p in parts if 'black_metal' in p.name),None)
    if not steel:continue
    origin=steel.matrix_world.translation.copy();x,y=origin.xy
    nearest=None
    for route,a,b,c in edge_list:
        dx,dy=b.x-a.x,b.y-a.y;t=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/(dx*dx+dy*dy)))
        edge=Vector((a.x+dx*t,a.y+dy*t,c.z));distance=math.hypot(x-edge.x,y-edge.y)
        if nearest is None or distance<nearest[0]:nearest=distance,edge,c
    trial=[(x,y)]
    if nearest and nearest[0]<.84 and abs(nearest[1].z-origin.z)<1.5:
        _,edge,center=nearest;out=Vector((edge.x-center.x,edge.y-center.y,0)).normalized()
        trial=[(edge.x+out.x*offset,edge.y+out.y*offset) for offset in [.44,.61,.84,1.02,1.24]]
    choice=None
    for xx,yy in trial:
        pts=[(xx+.145*math.cos(i*math.tau/12),yy+.145*math.sin(i*math.tau/12)) for i in range(12)]
        hits=[surface_at(px,py,origin.z) for px,py in pts]
        if not all(hits) or any(h[1].startswith(('R21_Dressed','COL_Walk_Central_stair','COL_Walk_West_residential','COL_Court_side_foundations')) for h in hits):continue
        spread=max(h[0] for h in hits)-min(h[0] for h in hits)
        if spread>.15:continue
        choice=(xx,yy,pts,hits,spread);break
    if choice is None:continue
    xx,yy,pts,hits,spread=choice;top=max(h[0] for h in hits)+.018;shift=Vector((xx-x,yy-y,top-origin.z))
    if shift.length<.025:continue
    pole_move=Matrix.Translation(shift)
    vs=[(px,py,h[0]-.014) for (px,py),h in zip(pts,hits)]+[(px,py,top) for px,py in pts]
    add('COL_N13_LampSockets',vs,[(i,(i+1)%12,(i+1)%12+12,i+12) for i in range(12)]+[tuple(range(12,24))],'cement')
    for ob in parts:ob.matrix_world=pole_move@ob.matrix_world
    adjustments.append({'group':'Lamp_'+key,'names':[o.name.replace('.','_') for o in parts],'transform':gm(pole_move),'before':shift.length,'after':0.,'contacts':[[xx,top,-yy]],'socket':True})
# A small shaded resting place beside the court. Leave the main route and stair mouths clear.
def box_obj(label,c,size,material):
    x,y,z=c;dx,dy,dz=[a*.5 for a in size]
    vv=[(x+u*dx,y+v*dy,z+w*dz) for w in [-1,1] for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    add(label,vv,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)
for key,color in [('oldwood',(.25,.17,.105)),('darkwood',(.125,.084,.050)),('board',(.38,.26,.13)),('ink',(.08,.053,.033)),('redink',(.31,.066,.026)),('tea',(.19,.123,.056))]:mat(key,color)
# Reuse the project's workday wood grain with the same recorded Poly Haven source.
for key in ['oldwood','darkwood','board']:
    m=mats[key];node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(root.parent/'street_photo_study/workday_surfaces'/('timber.jpg' if key!='board' else 'light_cane.jpg')),check_existing=True)
    node.image.pack();m.node_tree.links.new(node.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
furniture=[]
def make_seat(x,y,width,depth,h):
    g=floors(x,y)[0][0];height=g+h
    for u in [-1,1]:
        for v in [-1,1]:
            xx=x+u*(width*.40);yy=y+v*(depth*.38);fh=surface_at(xx,yy,g)
            if not fh:raise ValueError('Seat foot missing')
            box_obj('N13_ChessFurniture',(xx,yy,(fh[0]+height)/2),(.043,.043,height-fh[0]+.008),'darkwood')
    for j in range(3):
        box_obj('N13_ChessFurniture',(x,y+(j-1)*depth/3,height),(width,depth/3-.007,.033),'oldwood')
    furniture.append({'at':[x,height-.13,-y],'size':[width,h*.6,depth]})
    return height+.0165
cx,cy=-12.65,-14.95
h=make_seat(cx,cy,.86,.68,.65)
make_seat(cx-.13,cy-.69,.62,.29,.33);make_seat(cx+.08,cy+.68,.67,.29,.35)
box_obj('N13_ChessFurniture',(cx-.063,cy,h+.01),(.46,.49,.02),'board')
z=h+.022
for i in range(10):box_obj('N13_ChessFurniture',(cx-.063,cy+(i-4.5)*.047,z),(.384,.002,.001),'ink')
for i in range(9):
    xx=cx-.063+(i-4)*.0475
    for side in [-1,1]:box_obj('N13_ChessFurniture',(xx,cy+side*.1175,z),(.002,.188,.001),'ink')
for j,(u,v) in enumerate([(0,0),(3,1),(4,2),(1,4),(6,3),(8,0),(2,2),(4,8),(7,8),(6,9),(8,5),(5,6),(2,7)]):
    xx=cx-.063+(u-4)*.0475;yy=cy+(v-4.5)*.047
    rod('N13_ChessFurniture',(xx,yy,z),(xx,yy,z+.012),.019,'board',14)
    rod('N13_ChessFurniture',(xx-.007,yy,z+.013),(xx+.007,yy+.004,z+.013),.0018,'ink' if j<7 else 'redink',5)
for xx,yy in [(cx+.295,cy+.21),(cx-.34,cy-.21)]:
    rod('N13_ChessFurniture',(xx,yy,h+.005),(xx,yy,h+.102),.034,'ceramic',16,.041)
    rod('N13_ChessFurniture',(xx,yy,h+.100),(xx,yy,h+.104),.035,'tea',16)

