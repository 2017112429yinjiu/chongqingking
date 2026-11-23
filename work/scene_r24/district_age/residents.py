"""Editable A04 bike stand and separately ray-fitted neighbourhood printing."""
import json,math,random,bpy
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from math import pi,sin,cos
from roads import scene,terrain,asset,here
from survey import Surfaces
geom={};paint={}
def material(name,rgb,metal=.0,rough=.8):
    m=bpy.data.materials.new('Yard20_'+name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;paint[name]=m
for key,colour,metal,rough in [
 ('rail',(.145,.178,.156),.62,.72),('galv',(.31,.35,.35),.62,.65),('sheet_old',(.19,.246,.231),.49,.78),('oxide',(.18,.074,.041),.32,.9),('galv_light',(.39,.386,.33),.62,.62),('anchor',(.20,.19,.164),.0,.89),
 ('rubber',(.022,.021,.019),.03,.85),('spoke',(.34,.35,.345),.77,.34),('rim',(.39,.40,.38),.8,.38),('green',(.054,.146,.12),.52,.53),('claret',(.246,.075,.061),.42,.59),('blue',(.077,.139,.176),.44,.58),('saddle',(.065,.05,.038),.05,.7),('chrome',(.42,.42,.386),.79,.37),('chain',(.094,.095,.080),.59,.72),('red_reflector',(.44,.044,.021),.16,.35),('basket',(.19,.185,.15),.58,.62),('ink',(1,1,1),0,.93)]:material(key,colour,metal,rough)
def geo(key):
    if key not in geom:geom[key]=[[],[],[],[]]
    return geom[key]
def face(key,vs,mat,uv=None):
    vv,ff,mm,tt=geo(key);n=len(vv);vv.extend([tuple(v) for v in vs]);ff.append(tuple(range(n,n+len(vs))));mm.append(mat);tt.append(uv)
def tube(key,a,b,r,mat,sides=8,r2=None):
    a,b=Vector(a),Vector(b);d=(b-a).normalized()
    if d.length==0:return
    ex=d.cross(Vector((0,0,1)) if abs(d.z)<.92 else Vector((0,1,0))).normalized();ey=d.cross(ex)
    rings=[[c+(ex*cos(2*pi*i/sides)+ey*sin(2*pi*i/sides))*radius for i in range(sides)] for c,radius in [(a,r),(b,r if r2 is None else r2)]]
    for i in range(sides):
        j=(i+1)%sides;face(key,[rings[0][i],rings[0][j],rings[1][j],rings[1][i]],mat)
    face(key,rings[0][::-1],mat);face(key,rings[1],mat)
def box(key,c,size,mat):
    x,y,z=c;s,t,u=(k*.5 for k in size)
    v=[(x+i*s,y+j*t,z+k*u) for k in (-1,1) for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    for ids in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(key,[v[i] for i in ids],mat)
def zground(x,y):
    h=terrain.down(x,y)
    assert h,(x,y)
    return h[0][0]
def gd(p):return [p[0],p[2],-p[1]]
posts=[];wheel_contacts=[]
shelter='COL_Yard20_BikeShelter'
xlow,xhigh=-68.28,-66.23;y0,y1=-25.6,-20.9
roofbase=max(zground(x,y) for x in (xlow,xhigh) for y in (y0,y1))+2.16
def roof(x):return roofbase+(x-xlow)*.115
for x in (xlow,xhigh):
    for y in (y0,y1):
        z=zground(x,y);box(shelter,(x,y,z+.055),(.20,.20,.135),'anchor');box(shelter,(x,y,z+.131),(.133,.133,.019),'oxide')
        box(shelter,(x,y,(z+.13+roof(x))*.5),(.052,.052,roof(x)-z-.13),'rail')
        posts.append(gd((x,y,z)))
        for sign in (1,-1):
            tube(shelter,(x+.047*sign,y-.048,z+.14),(x+.047*sign,y-.048,z+.152),.008,'galv',6)
        inward=1 if y==y0 else -1
        tube(shelter,(x,y,roof(x)-.42),(x,y+inward*.45,roof(x)-.052),.018,'rail')
for x in [xlow,(xlow+xhigh)/2,xhigh]:
    box(shelter,(x,(y0+y1)/2,roof(x)-.022),(.055,y1-y0+.28,.062),'rail')
for y in (y0,(y0+y1)/2,y1):
    tube(shelter,(xlow-.13,y,roof(xlow-.13)-.048),(xhigh+.13,y,roof(xhigh+.13)-.048),.038,'galv',4)
# Each folded roofing sheet is a closed ridge profile, discharging along its fall toward the gutter.
key='Yard20_RoofSheets';xa,xb=xlow-.19,xhigh+.12
edges=[y0-.19+i*(y1-y0+.38)/200 for i in range(201)]
def corr(i):return [0,.013,.013,0][i%4]
for i in range(200):
    ya,yb=edges[i:i+2];ca,cb=corr(i),corr(i+1)
    finish=['sheet_old','galv','sheet_old','galv','galv_light','sheet_old'][min(5,i//34)]
    strip=[(xa,ya,roof(xa)+ca),(xb,ya,roof(xb)+ca),(xb,yb,roof(xb)+cb),(xa,yb,roof(xa)+cb)]
    face(key,strip,finish)
    lower=[(x,y,z-.006) for x,y,z in strip];face(key,lower[::-1],finish)
    for aa,bb in [(3,0),(1,2)]+([(0,1)] if i==0 else [])+([(2,3)] if i==199 else []):face(key,[strip[aa],lower[aa],lower[bb],strip[bb]],finish)
for i in range(0,199,12):
    for x in (xlow,xhigh):
        z=roof(x)+corr(i)+.008;tube(key,(x,edges[i],z-.013),(x,edges[i],z+.002),.011,'oxide' if i%24 else 'galv_light',6)
# Folded gutter with two end caps, pipe collars and a turned-out foot.
for aa,bb in [((xa-.07,-.014),(xa-.06,-.080)),((xa-.06,-.080),(xa+.013,-.080)),((xa+.013,-.080),(xa+.024,-.029))]:
    face(key,[(x,y,roof(xa)+z) for x,z,y in [(aa[0],aa[1],edges[0]),(aa[0],aa[1],edges[-1]),(bb[0],bb[1],edges[-1]),(bb[0],bb[1],edges[0])]],'galv')
px,py=xa-.031,y1-.07;base=zground(px,py)
for a,bb in [((px,py,roof(xa)-.072),(px,py,base+.18)),((px,py,base+.18),(px-.12,py,base+.075))]:tube(shelter,a,bb,.034,'galv',12)
for h in [.49,1.53]:tube(shelter,(px,py,base+h),(px,py,base+h+.027),.039,'rail',12)
# Bicycle wheels lie in the frame plane, with tilt and two independently sampled wheel contacts.
for i,(cy,angle,lean,col,step,basket) in enumerate([(-24.79,.07,.078,'green',True,True),(-23.20,-.12,-.055,'claret',True,False),(-21.75,.13,.072,'blue',False,True)]):
    name='Yard20_Cycle_'+str(i+1);cx=-67.23; span=1.065 if i!=2 else 1.10;radius=.327 if i!=1 else .304
    heading=Vector((cos(angle),sin(angle),0)); side=Vector((-sin(angle),cos(angle),0))
    rear=Vector((cx,cy,0))-heading*span/2;front=rear+span*heading
    zr,zf=zground(rear.x,rear.y),zground(front.x,front.y)
    def world(p):
        x,y,z=p;q=rear+heading*x+side*(y+lean*z)
        return (q.x,q.y,zr+(zf-zr)*x/span+z)
    def bar(a,b,r,mat,s=8):tube(name,world(a),world(b),r,mat,s)
    def shape(verts,mat):face(name,[world(p) for p in verts],mat)
    def hoop(x,y,z,rad,thick,mat,N=36):
        for j in range(N):
            a=2*pi*j/N;b=2*pi*(j+1)/N
            # Continuous eight-sided torus, joined at the angle of the rim.
            def at(t,h):
                rr=rad+thick*cos(h);return (x+rr*cos(t),y+thick*sin(h),z+rr*sin(t))
            for k in range(8):
                u=2*pi*k/8;v=2*pi*(k+1)/8;shape([at(a,u),at(a,v),at(b,v),at(b,u)],mat)
    for x in [0,span]:
        wheel_contacts.append(gd(world((x,0,0))));hoop(x,0,radius,radius-.022,.022,'rubber');hoop(x,0,radius,radius-.045,.010,'rim')
        bar((x,-.054,radius),(x,.054,radius),.022,'chrome',10)
        for j in range(24):
            a=2*pi*j/24;b=a+(.70 if j%2 else -.70)
            bar((x+.023*cos(b),.028*(-1)**j,radius+.023*sin(b)),(x+(radius-.05)*cos(a),0,radius+(radius-.05)*sin(a)),.002,'spoke',4)
        for j in range(16):
            u=pi*(.10+j*.82/16);v=u+pi*.82/16
            shape([(x+(radius+.014)*cos(t),y,radius+(radius+.014)*sin(t)) for t,y in [(u,-.026),(v,-.026),(v,.026),(u,.026)]],'galv')
    crank=(.44,0,.27);seat=(.34,0,.77);steer=(.87,0,.82);crown=(span-.035,0,radius+.20)
    for a,bb,r in [(crank,seat,.019),(crank,(.91,0,.68),.025),((.91,0,.68),steer,.026)]:bar(a,bb,r,col)
    if step:
        for a,bb in [((.38,0,.56),(.51,0,.42)),((.51,0,.42),(.64,0,.42)),((.64,0,.42),steer)]:bar(a,bb,.017,col)
    else:bar(seat,steer,.018,col)
    for s in (-1,1):
        bar((0,.048*s,radius),(.34,.011*s,.71),.010,col)
        bar((0,.048*s,radius),(.44,.023*s,.27),.012,col)
        bar((span,.047*s,radius),crown,.012,'chrome')
        bar((.91,.01*s,.68),crown,.019,col)
    bar(seat,(.33,0,.834),.014,'chrome');bar(steer,(.86,0,.94),.012,'chrome')
    lower=[];upper=[]
    for j in range(18):
        a=2*pi*j/18;x=.334+.113*cos(a);y=.082*sin(a)*(1-.48*cos(a));lower.append((x,y,.829));upper.append((x-.005,y*.94,.857+.013*-cos(a)))
    for j in range(18):k=(j+1)%18;shape([lower[j],lower[k],upper[k],upper[j]],'saddle')
    shape(upper,'saddle')
    for s in (-1,1):
        bar((.86,0,.93),(.86,.14*s,.95),.010,'chrome');bar((.86,.14*s,.95),(.77,.255*s,.968),.011,'chrome')
        bar((.80,.208*s,.961),(.748,.269*s,.972),.017,'rubber')
        bar((.44,.032*s,.27),(.44+.12*s,.068*s,.27-.048*s),.011,'chrome');bar((.44+.12*s,.067*s,.27-.048*s),(.44+.12*s,.149*s,.27-.048*s),.020,'rubber',4)
        for x in (-.105,.12):bar((0,s*.049,radius),(x,s*.059,.692),.005,'chrome')
        bar((-.158,.065*s,.692),(.178,.065*s,.692),.008,'chrome')
        bar((.855,.12*s,.95),(.94,.065*s,.78),.0038,'rubber');bar((.94,.065*s,.78),(span-.03,.045*s,.59),.0038,'rubber')
    for x in [-.154,-.04,.08,.177]:bar((x,-.064,.692),(x,.064,.692),.006,'chrome')
    hoop(.44,.04,.27,.077,.006,'chain',24);bar((0,.047,radius+.031),(.44,.047,.342),.006,'chain');bar((0,.047,radius-.031),(.44,.047,.198),.005,'chain')
    bar((.34,-.035,.265),(.25,-.18,.012),.012,'rail')
    bar((-.23,0,.55),(-.218,0,.594),.021,'red_reflector',8)
    if basket:
        for z,w,l in [(.66,.131,.099),(.84,.168,.135),(.815,.164,.131)]:
            ends=[(1.073+a*l,b*w,z) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
            for j in range(4):bar(ends[j],ends[(j+1)%4],.005,'basket')
        for s in (-1,1):
            for k in range(-4,5):
                t=k/4;bar((1.073+.099*t,s*.131,.66),(1.073+.135*t,s*.168,.84),.0028,'basket',5)
                bar((1.073+.099*s,.131*t,.66),(1.073+.135*s,.168*t,.84),.0028,'basket',5)
            bar((span,.049*s,radius),(1.12,s*.11,.665),.006,'galv')
    # One simplified physical frame inside the silhouette, plus the load-bearing posts and beams.
    proxy='COLH_Yard20_ParkedFrames';p=world((.50,0,.40));box(proxy,p,(1.34,.24,.71),'rail')
marks=[];atlas=bpy.data.images.load(str(asset/'wall_prints.png'));atlas.pack()
m=paint['ink'];nodes=m.node_tree.nodes;bs=nodes.get('Principled BSDF');im=nodes.new('ShaderNodeTexImage');im.image=atlas;m.node_tree.links.new(im.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(im.outputs['Alpha'],bs.inputs['Alpha'])
sites=json.loads((here/'placement.json').read_text('utf8'))
settings={'809889622':[(.80,.91,0,1.38)],'809889624':[(7.85,.99,1,1.35),(3.72,.68,7,1.19)],'1335306667':[(8.22,.83,2,1.32)],'1413081560':[(4.8,1.07,4,1.44),(10.31,.69,6,1.21)],'A03':[(8.65,.93,3,1.40)],'A04':[(8.40,1.06,5,1.41),(13.28,.82,7,1.30)]}
for rec in sites:
    for k,(d,w,which,h) in enumerate(settings.get(str(rec['id']),[])):
        a=Vector(rec['a']);t=Vector(rec['t']);n=Vector(rec['n']);sample=min(rec['spans'],key=lambda r:abs(r[0]-d));p=a+t*d+n*(sample[2]+.004)
        bottom=sample[1]+h-w/2
        pts=[(*list(p+t*s),bottom+u) for s,u in [(-w/2,0),(w/2,0),(w/2,w),(-w/2,w)]]
        col,row=which%4,which//4
        uv=[((col+u)/4,1-(row+v)/2) for u,v in [(0,1),(1,1),(1,0),(0,0)]]
        face('Yard20_Entry_'+str(rec['id']),pts,'ink',uv);marks.append({'id':rec['id'],'surface':sample[3],'centre':gd((*p,bottom+w/2)),'width':w,'print':which})
# Rear wheel stops and locking hoops stand on their own individual feet on the hill.
for yc in (-24.79,-24.02,-23.20,-21.75):
    x=-66.59
    for y in (yc-.094,yc+.094):
        z=zground(x,y);box(shelter,(x,y,z+.019),(.14,.10,.045),'oxide')
        tube(shelter,(x,y,z+.026),(x,y,z+.41),.014,'galv',10)
    za=zground(x,yc-.094)+.41;zb=zground(x,yc+.094)+.41
    tube(shelter,(x,yc-.094,za),(x,yc+.094,zb),.014,'galv',10)
# A00 signage is hand-painted through a worn stencil on a specific masonry face.
material('lettering',(1,1,1));wmat=paint['lettering'];tex=wmat.node_tree.nodes.new('ShaderNodeTexImage')
tex.image=bpy.data.images.load(str(asset/'wall_lettering.png'));tex.image.pack();shader=wmat.node_tree.nodes.get('Principled BSDF')
for inp,outp in [('Base Color','Color'),('Alpha','Alpha')]:wmat.node_tree.links.new(tex.outputs[outp],shader.inputs[inp])
for obj,pts,index in [('Yard20_ShedLetter',[(-66.006,-21.3,16.55),(-66.006,-23.93,16.55),(-66.006,-23.93,17.426),(-66.006,-21.3,17.426)],1),('Yard20_RepairLetter',[(-63.42,-54.009,12.63),(-61.67,-54.009,12.63),(-61.67,-54.009,13.213),(-63.42,-54.009,13.213)],0)]:
    face(obj,pts,'lettering',[(0,.75-.25*index),(1,.75-.25*index),(1,1.-.25*index),(0,1.-.25*index)])
for suffix,a,b,ratio,zc,ix in [('Upper',(-79.5578,26.0045),(-71.6785,26.1264),.57,23.04,2),('Lower',(-71.7657,31.6465),(-80.2652,31.5135),.36,23.59,3)]:
    ta=Vector(a);tb=Vector(b);t=(tb-ta).normalized();n=Vector((t.y,-t.x));q=ta.lerp(tb,ratio)+n*.006
    ps=[(*tuple(q+t*s),zc+h) for s,h in [(-.78,0),(.78,0),(.78,.52),(-.78,.52)]]
    face('Yard20_West'+suffix+'Letter',ps,'lettering',[(0,.75-.25*ix),(1,.75-.25*ix),(1,1.-.25*ix),(0,1.-.25*ix)])
from repair_stand import build as make_repair_tools
pump_feet=[gd(point) for point in make_repair_tools(tube,box,zground)]
new=[]
for key,(vs,fs,mm,tt) in geom.items():
    mesh=bpy.data.meshes.new(key);mesh.from_pydata(vs,[],fs);mats=list(dict.fromkeys(mm))
    for mat in mats:mesh.materials.append(paint[mat])
    for poly,mat in zip(mesh.polygons,mm):poly.material_index=mats.index(mat)
    if any(tt):
        layer=mesh.uv_layers.new(name='Print atlas')
        for poly,uv in zip(mesh.polygons,tt):
            for i,xy in zip(poly.loop_indices,uv):layer.data[i].uv=xy
    ob=bpy.data.objects.new(key,mesh);scene.collection.objects.link(ob);new.append(key)
    if key.startswith('COLH_'):ob.display_type='WIRE'
