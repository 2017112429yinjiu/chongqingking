"""Blender 4.3.2. Build the market terraces on the verified R23 city, in metres/Z-up."""
from pathlib import Path
from collections import defaultdict
import bpy,bmesh,json,math,random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parent;S=W/'scene_r24'; export=S/'assets';export.mkdir(exist_ok=True)
V=Vector;Z=V((0,0,1));rng=random.Random(24032)
scene=bpy.context.scene; originals=list(scene.objects);dirty={};made=[]
report={}; views={}; fixtures=[]
def change(o):
    if o.name not in dirty:o.data=o.data.copy();dirty[o.name]=o
def bounds(o):
    p=[o.matrix_world@V(q) for q in o.bound_box]
    return [(min(v[k] for v in p),max(v[k] for v in p)) for k in range(3)]
def support_mesh(o):
    return o.type=='MESH' and o.name.startswith(('COL_Terrain','COL_Road_','COL_Walk_','COL_Community_court_pavement','COL_R23_Nanqu','COL_Court_entry'))
def spatial(objs):
    entries=[]
    for o in objs:
        pos=[o.matrix_world@v.co for v in o.data.vertices];faces=[tuple(p.vertices) for p in o.data.polygons]
        if pos and faces:entries.append((bounds(o),BVHTree.FromPolygons(pos,faces),o.name))
    return entries
ground_trees=spatial([o for o in originals if support_mesh(o)])
def ground(x,y):
    hits=[]
    for ((xl,xh),(yl,yh),_),tree,name in ground_trees:
        if xl-.001<=x<=xh+.001 and yl-.001<=y<=yh+.001:
            p,n,_,_=tree.ray_cast((x,y,65),(0,0,-1),100)
            if p is not None and abs(n.z)>.55:hits.append(p.z)
    if not hits:raise ValueError(('No ground',x,y))
    return max(hits)
def mat(name,rgb,rough=.83,metal=0):
    m=bpy.data.materials.new('R24_'+name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m
steel=mat('galvanised',(.235,.239,.211),.54,.58);iron=mat('painted_iron',(.054,.075,.065),.66,.35)
pine=mat('old_pine',(.21,.126,.064));bamboo=mat('split_bamboo',(.28,.184,.078))
dark=mat('rubber',(.024,.028,.026));stone=mat('step_stone',(.25,.225,.185))
green=mat('crate_green',(.037,.15,.108),.58);red=mat('crate_russet',(.255,.054,.032),.59)
canvas=mat('market_canvas',(.37,.227,.121),.95);blue=mat('repair_canvas',(.124,.193,.213),.91)
twine=mat('hemp',(.241,.192,.132));paper=mat('labels',(.82,.81,.73))
brass=mat('brass',(.42,.292,.093),.47,.65);cream=mat('enamel',(.43,.45,.34),.58,.18)
ceramic=mat('cup',(.61,.55,.413),.34);amber=mat('opal',(.85,.73,.50))
lampnode=amber.node_tree.nodes.get('Principled BSDF')
lampnode.inputs['Emission Color'].default_value=(.98,.78,.57,1);lampnode.inputs['Emission Strength'].default_value=1.1
atlas=bpy.data.images.load(str(S/'shop_paint.png'));atlas.pack()
pic=paper.node_tree.nodes.new('ShaderNodeTexImage');pic.image=atlas
paper.node_tree.links.new(pic.outputs['Color'],paper.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
fruit=mat('produce',(.4,.4,.4));vc=fruit.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Pigment'
fruit.node_tree.links.new(vc.outputs['Color'],fruit.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
buffers=defaultdict(lambda:[[],[],[],[],[]])
def surface(group,m,verts,faces,smooth=False,uv=None,col=None):
    ps,fs,uvs,colors,sm=buffers[group,m];start=len(ps)
    ps.extend(tuple(q) for q in verts);fs.extend(tuple(start+i for i in f) for f in faces)
    uvs.extend(uv or [(0,0)]*len(verts));colors.extend(col or [(.4,.4,.4)]*len(verts));sm.extend([smooth]*len(faces))
def box(group,m,c,size):
    x,y,z=c;a,b,h=[q*.5 for q in size]
    pp=[(x+i*a,y+j*b,z+k*h) for k in [-1,1] for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    surface(group,m,pp,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
def rod(group,m,a,b,r,r1=None,sides=9):
    a,b=V(a),V(b);f=(b-a).normalized()
    u=f.cross(Z if abs(f.z)<.86 else V((1,0,0))).normalized();v=f.cross(u)
    rr=r if r1 is None else r1
    verts=[p+(u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides))*radius for p,radius in [(a,r),(b,rr)] for i in range(sides)]
    faces=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,sides+(i+1)%sides,sides+i) for i in range(sides)]
    surface(group,m,verts,faces,True)
def label(group,c,w,h,rect):
    x,y,z=c;l,t,r,b=rect
    uv=[(l/1536,1-b/1024),(r/1536,1-b/1024),(r/1536,1-t/1024),(l/1536,1-t/1024)]
    surface(group,paper,[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],[(0,1,2,3)],uv=uv)
def finish():
    col=bpy.data.collections.new('R24 Market frontage');scene.collection.children.link(col)
    for (group,m),(ps,fs,uvs,cols,smooth) in buffers.items():
        name=group+'_'+m.name;me=bpy.data.meshes.new(name);me.from_pydata(ps,[],fs);me.update();me.materials.append(m)
        if any(v!=(0,0) for v in uvs):
            uv=me.uv_layers.new(name='UVMap')
            for loop in me.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
        if m==fruit:
            ca=me.color_attributes.new(name='Pigment',type='FLOAT_COLOR',domain='POINT')
            for i,color in enumerate(cols):ca.data[i].color=(*color,1.)
        for poly,sm in zip(me.polygons,smooth):poly.use_smooth=sm
        ob=bpy.data.objects.new(name,me);col.objects.link(ob);made.append(ob)
# Cut all old walking and cosmetic sheets at the junction. Cutting in four planes
# preserves surrounding UVs, slot assignments and the existing upper walk.
cx=-21.40;xl,xh=cx-1.27,cx+1.27;yl,yh=-79.94,-77.50
low=ground(cx,yl-.12);high=ground(cx,yh+.11);cuts={}
for o in originals:
    if o.type!='MESH' or not o.name.startswith(('COL_Terrain','COL_Walk_','Walk_details_','COL_R23_Nanqu','COL_R23_PathFoundations','Urban_paving_')):continue
    ((ox,ex),(oy,ey),(oz,ez))=bounds(o)
    if ex<xl or ox>xh or ey<yl or oy>yh or oz>high+.3 or ez<low-.2:continue
    bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
    def nearby(face):
        coords=[v.co for v in face.verts]
        return max(p.x for p in coords)>xl-.08 and min(p.x for p in coords)<xh+.08 and max(p.y for p in coords)>yl-.08 and min(p.y for p in coords)<yh+.08
    for k,val in [(0,xl),(0,xh),(1,yl),(1,yh)]:
        local=[]
        for face in bm.faces:
            if nearby(face) and min(v.co[k] for v in face.verts)<val and max(v.co[k] for v in face.verts)>val:
                local.append(face)
        if not local:continue
        geom=set(local)
        for face in local:geom.update(face.edges);geom.update(face.verts)
        at=V((0,0,0));at[k]=val;norm=V((0,0,0));norm[k]=1
        bmesh.ops.bisect_plane(bm,geom=list(geom),plane_co=at,plane_no=norm,dist=.00003)
    inside=[f for f in bm.faces if xl-.00002<f.calc_center_median().x<xh+.00002 and yl-.00002<f.calc_center_median().y<yh+.00002 and f.calc_center_median().z<high+.3]
    if inside:
        cuts[o.name]=len(inside);bmesh.ops.delete(bm,geom=inside,context='FACES')
        change(o);bm.transform(o.matrix_world.inverted());bm.to_mesh(o.data);o.data.update()
    bm.free()
assert cuts and high-low>.5,(cuts,low,high)
count=math.ceil((high-low)/.18);tread=(yh-yl-.32)/count
for i in range(count):
    first=yl+i*tread;end=yh+.007 if i==count-1 else first+tread
    top=low+(high-low)*(i+1)/count
    box('COL_R24_MarketStairs',stone,(cx,(first+end)/2,(top+low-.22)/2),(xh-xl+.01,end-first,top-low+.22))
    # Close each cut flank up to its actual neighbouring surface.
    for edge,sign in [(xl,-1),(xh,1)]:
        side_top=ground(edge+sign*.04,(first+end)/2)
        if side_top>top+.018:
            box('COL_R24_MarketStairs',stone,(edge+sign*.029,(first+end)/2,(side_top+top)/2),(.066,end-first,side_top-top))
for x in [xl+.09,xh-.09]:
    rod('R24_StairJoints',iron,(x,yl+.018,low+.02),(x,yl+.018,low+.10),.011)
report['stairs']=dict(location=[cx,yl,yh],clear_width=xh-xl,rise=(high-low)/count,treads=count,lower=low,upper=high,cut_sources=cuts)
# Long rails were carried through a 0.20 m clipping pass. Identify complete upright
# shafts geometrically, join their plan points into actual remaining runs and retain
# endpoints at existing gaps. Open sides with large drops keep their denser protection.
rails=[]
for key in ['Central_stair_lane','West_residential_link']:
    o=bpy.data.objects['COL_Handrails_'+key+'_painted_metal'];bm=bmesh.new();bm.from_mesh(o.data)
    groups=defaultdict(list);pending=set(bm.verts)
    while pending:
        part=[pending.pop()]
        for v in part:
            for edge in v.link_edges:
                q=edge.other_vert(v)
                if q in pending:pending.remove(q);part.append(q)
        lo=[min(v.co[k] for v in part) for k in range(3)];hi=[max(v.co[k] for v in part) for k in range(3)]
        if .04<hi[0]-lo[0]<.079 and .04<hi[1]-lo[1]<.079:
            if hi[2]-lo[2]>.6 or hi[2]-lo[2]<.001:
                groups[tuple(round((a+b)/2,3) for a,b in zip(lo[:2],hi[:2]))].append((part,lo[2],hi[2]))
    posts=sorted(xy for xy,r in groups.items() if any(h-l>.6 for _,l,h in r))
    adj={p:[q for q in posts if p!=q and math.dist(p,q)<.265] for p in posts}
    visited=set();discard=set();retained=[];high_count=0
    for seed in sorted(posts,key=lambda p:(len(adj[p])!=1,p)):
        if seed in visited:continue
        path=[];q=seed
        while q not in visited:
            path.append(q);visited.add(q);options=[a for a in adj[q] if a not in visited]
            if not options:break
            q=min(options,key=lambda a:math.dist(a,q))
        if len(path)<4:continue
        last=0;segment=0
        for j in range(1,len(path)-1):
            p=path[j];d=(V(path[j+1])-V(path[j-1])).normalized();n=V((-d.y,d.x))
            heights=[ground(*(V(p)+n*s)) for s in [-.62,.62]]
            exposed=abs(heights[0]-heights[1])>.68
            high_count+=int(exposed)
            segment+=math.dist(path[j-1],p)
            spacing=.43 if exposed else 1.24
            if segment>=spacing-.085 or len(adj[p])!=2:
                segment=0;last=j
            else:discard.add(p)
        retained.append((path[0],path[-1]))
    delete=[v for xy in discard for part,_,_ in groups[xy] for v in part]
    if delete:
        bmesh.ops.delete(bm,geom=delete,context='VERTS');change(o)
        for xy in set(posts)-discard:
            z=ground(*xy);bottom=min(a for _,a,_ in groups[xy])
            for part,_,_ in groups[xy]:
                for v in part:
                    if abs(v.co.z-bottom)<.022:v.co.z=z-.012
        bm.to_mesh(o.data);o.data.update()
    rails.append(dict(route=key,posts_before=len(posts),posts_after=len(posts)-len(discard),original_run_ends=len(retained)*2,sampled_exposed_posts=high_count))
    bm.free()
report['rails']=rails
def fabric(group,material,cx,front,back,width,z_front,z_back,sag):
    nu,nv=36,14;verts=[];uv=[];faces=[]
    for j in range(nv+1):
        t=j/nv
        for i in range(nu+1):
            u=i/nu;phase=u*math.tau*2
            z=z_front*(1-t)+z_back*t - sag*math.sin(t*math.pi)*(abs(math.sin(phase))+.15)
            z+=.021*math.sin(phase*3+.5)*math.sin(t*math.pi)
            verts.append((cx+width*(u-.5),front+(back-front)*t,z));uv.append((u,t))
    for j in range(nv):
        for i in range(nu):
            k=j*(nu+1)+i;faces.append((k,k+1,k+nu+2,k+nu+1))
    surface(group,material,verts,faces,True,uv)
    # Hem and drip edge are attached to the front tube, with a variable hanging free edge.
    vs=[];tex=[];fs=[]
    for i in range(nu+1):
        u=i/nu;x=cx+width*(u-.5);wave=math.sin(u*math.tau*7+.45)
        vs.extend([(x,front,z_front),(x,front-.023-.015*wave,z_front-.175-.021*wave)])
        tex.extend([(u,0),(u,-.15)])
        if i:fs.append((2*i-2,2*i-1,2*i+1,2*i))
    surface(group,material,vs,fs,True,tex)
def frame(group,cx,front,back,w,zf,zb):
    sockets=[]
    for x in [cx-w/2+.075,cx+w/2-.075]:
        for y,z in [(front+.065,zf),(back-.065,zb)]:
            soil=ground(x,y);sockets.append([x,y,soil])
            fixtures.append(dict(kind='post',position=[x,(soil+z)/2,-y],height=z-soil,radius=.027))
            box(group,iron,(x,y,soil+.013),(.145,.14,.033))
            rod(group,steel,(x,y,soil-.009),(x,y,z),.026)
            for ox in [-.05,.05]:rod(group,steel,(x+ox,y,soil+.028),(x+ox,y,soil+.04),.012,sides=6)
        rod(group,iron,(x,front+.06,zf-.03),(x,back-.05,zb-.03),.022)
        rod(group,steel,(x,front+.06,zf-.42),(x,front+.43,zf+.055),.014)
    for y,z in [(front+.055,zf-.017),(back-.055,zb-.024)]:
        rod(group,iron,(cx-w/2+.02,y,z),(cx+w/2-.02,y,z),.023)
    for x in [cx-w*.23,cx,cx+w*.23]:rod(group,iron,(x,front+.025,zf-.017),(x,back-.035,zb-.022),.014)
    return sockets
def table(group,x,y,z,w,d):
    feet=min(ground(x+a*w*.45,y+b*d*.40) for a in [-1,1] for b in [-1,1])
    fixtures.append(dict(kind='counter',position=[x,(z+.023+feet)/2,-y],size=[w,z+.023-feet,d]))
    for ox in [-w*.455,w*.455]:
        for oy in [-d*.405,d*.405]:
            px=x+ox;py=y+oy
            rod(group,iron,(px,py,ground(px,py)-.009),(px,py,z+.02),.02,sides=8)
        rod(group,iron,(x+ox,y-d*.40,z-.43),(x+ox,y+d*.40,z-.43),.018)
    for oy in [-d*.40,d*.40]:rod(group,iron,(x-w*.46,y+oy,z-.055),(x+w*.46,y+oy,z-.055),.024)
    box('COL_'+group,pine,(x,y,z),(w,d,.056))
def crate(group,x,y,z,w,d,h,m):
    box(group,m,(x,y,z+.026),(w-.03,d-.03,.032))
    for sy in [-1,1]:
        yy=y+sy*(d/2-.012);box(group,m,(x,yy,z+h),(w,.034,.036))
        for j in [1,2]:box(group,m,(x,yy,z+j*h*.29),(w,.018,.022))
        for i in range(8):box(group,m,(x+w*(i/7-.5)*.96,yy,z+h/2),(.023,.025,h))
    for sx in [-1,1]:
        xx=x+sx*(w/2-.011)
        for j in [1,2,3]:box(group,m,(xx,y,z+(j-.2)*h/3),(.025,d,.032))
        for sy in [-.45,0,.45]:box(group,m,(xx,y+d*sy,z+h/2),(.023,.03,h))
def lathe(group,m,x,y,z,shape,sides=18):
    vs=[(x+r*math.cos(k*math.tau/sides),y+r*math.sin(k*math.tau/sides),z+h) for h,r in shape for k in range(sides)]
    faces=[(j*sides+k,j*sides+(k+1)%sides,(j+1)*sides+(k+1)%sides,(j+1)*sides+k) for j in range(len(shape)-1) for k in range(sides)]
    surface(group,m,vs,faces,True)
def spindle(start,axis,radii,color,group='R24_Greengrocer',ns=7,bend=.01):
    axis=V(axis);a=V(start);d=axis.normalized();u=d.cross(Z if abs(d.z)<.88 else V((1,0,0))).normalized();v=d.cross(u)
    ps=[];cs=[]
    for j,rad in enumerate(radii):
        t=j/(len(radii)-1);mid=a+axis*t+u*(bend*math.sin(t*math.pi))
        for i in range(ns):
            ang=i*math.tau/ns;p=mid+(u*math.cos(ang)+v*math.sin(ang))*rad
            ps.append(p);tint=rng.uniform(.91,1.05)*(.82+.18*t)
            cs.append(tuple(c*tint for c in color))
    fs=[(j*ns+k,j*ns+(k+1)%ns,(j+1)*ns+(k+1)%ns,(j+1)*ns+k) for j in range(len(radii)-1) for k in range(ns)]
    fs+=[tuple(range(ns))[::-1],tuple(range((len(radii)-1)*ns,len(radii)*ns))]
    surface(group,fruit,ps,fs,True,col=cs)
def blade(start,angle,length,width,rise,color):
    base=V(start);f=V((math.cos(angle),math.sin(angle),0));u=V((-f.y,f.x,0));ps=[];cs=[]
    for k in range(7):
        t=k/6;mid=base+f*length*(t**1.25)+Z*rise*(1.55*t-.57*t*t)
        w=width*(.15*(1-t)+math.sin(math.pi*t)**.70)
        for side in [-1,0,1]:
            ps.append(mid+u*w*side+Z*(.014*math.sin(math.pi*t) if side==0 else .004*math.sin(t*14+angle)))
            pigment=(.48,.51,.23) if k<2 and side==0 else color
            cs.append(tuple(v*(.74+.26*t)*(1.15 if side==0 else 1) for v in pigment))
    surface('R24_Greengrocer',fruit,ps,[(j*3+i,(j+1)*3+i,(j+1)*3+i+1,j*3+i+1) for j in range(6) for i in range(2)],True,col=cs)
def basket(x,y,z,r):
    for j in range(7):
        h=.026+j*.021;rr=r*(.69+j*.05)
        lathe('R24_Greengrocer',bamboo,x,y,z,[(h-.004,rr),(h,rr+.004),(h+.005,rr)],32)
    for k in range(18):
        a=k*math.tau/18
        rod('R24_Greengrocer',bamboo,(x+.68*r*math.cos(a),y+.68*r*math.sin(a),z+.015),
            (x+r*math.cos(a+.07),y+r*math.sin(a+.07),z+.164),.004,sides=5)
    lathe('R24_Greengrocer',bamboo,x,y,z,[(.149,r),(.158,r+.007),(.166,r)],40)
vendor='R24_Greengrocer'
cx0=-26.35;front=-75.37;back=-73.13;width=4.75;zf=11.22;zb=11.94
report['market_post_contacts']=frame(vendor,cx0,front,back,width,zf,zb)
fabric(vendor,canvas,cx0,front-.11,back+.045,width+.16,zf,zb,.116)
# The fascia is behind the canopy, beneath the existing residential sills.
box(vendor,pine,(cx0,back-.087,11.03),(3.83,.088,.48))
label(vendor,(cx0,back-.134,11.03),3.77,.44,(0,0,1536,319))
# A shallow timber lining takes the shelving brackets and keeps paper and stock
# away from the damp masonry plinth. Broken lengths and knots remain visible.
for k in range(25):
    x=cx0-2.16+k*.180;foot=ground(x,back-.03);top=10.75+.022*math.sin(k*1.7)
    box(vendor,pine,(x,back-.027,(top+foot)/2),(.172,.042,top-foot))
for h in [9.56,10.49]:
    box(vendor,iron,(cx0,back-.061,h),(4.51,.028,.046))
for x in [cx0-1.57,cx0+1.41]:
    rod(vendor,iron,(x,back-.076,10.15),(x,back-.40,10.47),.015)
box(vendor,pine,(cx0,back-.21,10.48),(3.51,.38,.037))
# Lighting under the canopy remains local to the stall. The cleats and lead touch the frame.
rod(vendor,iron,(cx0-1.23,-74.27,11.52),(cx0+1.23,-74.27,11.52),.043)
rod(vendor,amber,(cx0-1.08,-74.278,11.482),(cx0+1.08,-74.278,11.482),.021)
table(vendor,cx0,-74.91,9.73,4.12,.72)
for i in range(4):
    # Old slatted front with a small gap between planks, set back under the stock.
    box(vendor,pine,(cx0,-75.185,9.25+i*.098),(4.02,.032,.089))
for x in [cx0-1.92,cx0-.03,cx0+1.92]:
    box(vendor,iron,(x,-75.209,9.398),(.035,.019,.43))
    for zz in [9.24,9.56]:rod(vendor,steel,(x,-75.223,zz),(x,-75.212,zz),.008,sides=6)
# One end closes the counter in light corrugated sheet; the back stays open for stock.
for i in range(15):
    y=-75.20+i*.044
    box(vendor,green,(cx0+2.03+.009*math.cos(i*math.pi),y,9.40),(.025,.049,.53))
for k in range(3):
    x=cx0-1.28+.52*k;y=back-.22
    lathe(vendor,ceramic,x,y,10.50,[(0,.062),(.014,.074),(.103,.111),(.112,.109),(.108,.098)],19)
    if k!=1:lathe(vendor,bamboo,x+.005,y,10.61,[(0,.108),(.014,.102),(.039,.027)],19)
table(vendor,cx0+.46,-73.55,9.87,2.87,.48)
for i,offset in enumerate([-1.51,-.58,.31,1.14]):
    x=cx0+offset;y=-74.89;z=9.759
    if i in (0,3):crate(vendor,x,y,z,.73,.55,.149,green if not i else red)
    else:basket(x,y,z,.284)
    if i==0:
        for k in range(19):
            px=x+rng.uniform(-.272,.272);py=y+rng.uniform(-.18,.18)
            zz=z+.104+rng.uniform(.005,.037);start=(px,py,zz)
            for l in range(5):
                blade(start,math.tau*l/5+rng.random()*.6,rng.uniform(.055,.115),rng.uniform(.028,.050),rng.uniform(.10,.178),(rng.uniform(.024,.052),rng.uniform(.096,.17),.027))
    elif i==1:
        for k in range(19):
            a=k*2.4;rr=.195*math.sqrt(k/19);px=x+rr*math.cos(a);py=y+rr*math.sin(a)
            height=z+.172+.063*(1-rr/.2);ang=a+.55
            spindle((px,py,height),(.175*math.cos(ang),.16*math.sin(ang),-.047),[.012,.038,.044,.039,.020,.002],(.51,.503,.36),ns=11)
            for l in range(2):blade((px,py,height),ang+2.7+l*.7,.053,.013,.038,(.16,.245,.082))
    elif i==2:
        for k in range(60):
            a=k*2.40;rr=.21*math.sqrt(k/60);px=x+rr*math.cos(a);py=y+rr*math.sin(a)
            h=z+.151+.076*(1-rr/.22);v=rng.random()*math.tau
            spindle((px,py,h),(.10*math.cos(v),.08*math.sin(v),-.018),[.008,.016,.012,.007,.002],(rng.uniform(.31,.47),.035,.019),bend=.02)
            spindle((px,py,h),(-.022*math.cos(v),-.016*math.sin(v),.017),[.005,.003],(.077,.148,.034))
    else:
        for k in range(40):
            px=x+rng.uniform(-.26,.17);py=y+rng.uniform(-.14,.09);bottom=z+.092+rng.random()*.044
            spindle((px,py,bottom),(.054,.04,.02),[.005,.009,.006],(.60,.61,.40))
            for j in range(2):blade((px+.05,py+.04,bottom+.018),rng.uniform(.45,.84),rng.uniform(.13,.22),.008,rng.uniform(.052,.124),(.077,.197,.064))
    rod(vendor,iron,(x-.19,y-.245,z+.02),(x-.19,y-.257,z+.215),.0045)
    label(vendor,(x-.19,y-.266,z+.201),.154,.100,(384*i+3,593,384*(i+1)-3,843))
# A calibrated tabletop scale with weighing pan and small customer-facing display.
sx=cx0+1.78;sy=-74.88
box(vendor,cream,(sx,sy,9.806),(.37,.36,.079))
lathe(vendor,steel,sx,sy,9.84,[(0,.081),(.028,.085),(.042,.17),(.051,.18)],26)
rod(vendor,iron,(sx+.13,sy+.09,9.83),(sx+.13,sy+.09,10.13),.012)
box(vendor,dark,(sx+.085,sy+.08,10.145),(.22,.045,.071))
label(vendor,(sx+.085,sy+.054,10.145),.196,.048,(6,850,1530,1018))
for k in range(3):
    x=cx0+.32+k*.53;y=-73.54
    crate(vendor,x,y,9.901,.48,.39,.24,green if k%2 else red)
for k in range(2):
    x=cx0-1.66+k*.66;y=-74.28
    g=ground(x,y);crate(vendor,x,y,g+.006,.58,.41,.23,red);crate(vendor,x,y,g+.244,.55,.39,.22,green)
# A recessed repair booth on the adjoining upper terrace has a separate canopy, left
# jamb, return wall, work lamp and a key-cutting bench. The front remains accessible.
repair='R24_RepairBooth';cx1=-12.18;yfront=-74.62;yback=-71.46;w=3.55;roof=11.94;rear=12.29
report['repair_post_contacts']=frame(repair,cx1,yfront,yback,w,roof,rear)
fabric(repair,blue,cx1,yfront-.055,yback+.08,w+.13,roof,rear,.063)
for j in range(14):
    x=cx1-w*.49+.13+j*(w*.98/14)
    foot=ground(x,yback)
    box('COL_'+repair,iron,(x,yback,(foot+12.13)/2),(.25,.062,12.13-foot))
for j in range(13):
    x=cx1-w*.49+.25+j*(w*.98/14)
    box(repair,steel,(x,yback-.04,10.68),(.012,.025,2.30))
for y in [yfront+.52,yfront+1.54,yfront+2.55]:
    x=cx1-w*.5;g=ground(x,y)
    box('COL_'+repair,iron,(x,y,(g+11.27)/2),(.055,1.016,11.27-g))
# Shelter side is partly glazed. Frame and small louvers have actual thickness.
for yy in [yfront+.01,yfront+1.03,yfront+2.05,yback-.02]:
    rod(repair,iron,(cx1-w*.5,yy,11.26),(cx1-w*.5,yy,11.91),.023)
table(repair,cx1-.27,-72.22,10.29,2.38,.70)
box(repair,green,(cx1-.68,-72.29,10.407),(.62,.335,.17))
for dx in [-.16,.16]:
    box(repair,steel,(cx1-.68+dx,-72.37,10.557),(.113,.19,.129))
    rod(repair,brass,(cx1-.68+dx,-72.47,10.58),(cx1-.68+dx,-72.51,10.58),.034,sides=12)
rod(repair,steel,(cx1-.91,-72.26,10.64),(cx1-.43,-72.26,10.64),.024)
box(repair,pine,(cx1+.25,yback-.11,11.09),(1.27,.05,.61))
for row in range(3):
    for k in range(8):
        if (row*8+k)%6==0:continue
        x=cx1-.29+k*.151;y=yback-.145;z=10.895+row*.175
        rod(repair,brass,(x,y,z+.095),(x,y-.013,z+.045),.006)
        lathe(repair,brass,x,y-.023,z+.02,[(0,.013),(.017,.018),(.029,.011)],9)
        box(repair,brass,(x,y-.021,z-.017),(.011,.009,.072))
        for j in range(2):box(repair,brass,(x+.006,y-.021,z-.029-j*.013),(.016,.009,.005))
box(repair,pine,(cx1-.06,yfront-.03,11.67),(2.69,.071,.43))
label(repair,(cx1-.06,yfront-.069,11.67),2.62,.379,(3,322,1533,584))
for x in [cx1-.95,cx1+.84]:
    rod(repair,iron,(x,yfront+.015,11.88),(x,yfront+.015,roof),.011)
bowlx=cx1+w*.32;bowly=yfront+.43;gz=ground(bowlx,bowly)
lathe(repair,steel,bowlx,bowly,gz,[(0,.174),(.031,.173),(.46,.184),(.474,.18),(.474,.165),(.04,.16)],22)
# Worn drawers, task light, cutting wheel guard and a can of graphite by the key machine.
for j in range(3):
    x=cx1-.93+j*.47
    box(repair,iron,(x,-72.39,10.107),(.45,.36,.24))
    box(repair,cream,(x,-72.581,10.11),(.425,.023,.206))
    rod(repair,steel,(x-.071,-72.616,10.12),(x+.071,-72.616,10.12),.009)
rod(repair,iron,(cx1-.7,-72.09,10.46),(cx1-.7,-72.09,10.92),.028)
rod(repair,steel,(cx1-.79,-72.10,10.77),(cx1-.53,-72.10,10.77),.077,sides=20)
rod(repair,brass,(cx1-.55,-72.10,10.77),(cx1-.52,-72.10,10.77),.091,sides=24)
rod(repair,iron,(cx1-.53,-72.13,10.59),(cx1-.47,-72.42,10.83),.015)
rod(repair,dark,(cx1-.47,-72.42,10.83),(cx1-.45,-72.48,10.90),.025)
lathe(repair,cream,cx1+.47,-72.30,10.32,[(0,.044),(.09,.043),(.108,.022),(.12,.020)],12)
rod(repair,iron,(cx1+.44,yback-.035,11.66),(cx1+.47,-72.19,11.71),.023)
lathe(repair,iron,cx1+.47,-72.19,11.57,[(0,.145),(.024,.157),(.095,.060),(.134,.045)],20)
lathe(repair,amber,cx1+.47,-72.19,11.56,[(0,.062),(.037,.08),(.062,.05)],16)
for j,m in enumerate([blue,dark,red]):
    x=bowlx+(j-1)*.067;y=bowly+(.032 if j==1 else -.025);top=gz+.71+j*.046
    pts=[];side=16
    for k,(off,rad) in enumerate([(.16,.018),(.36,.040),(.48,.035),(.64,.057),(.73,.064)]):
        for ix in range(side):
            t=ix*math.tau/side+.13*k
            rr=rad*(.68 if ix%2 else 1.)
            pts.append((x+.029*k/4+rr*math.cos(t),y+rr*math.sin(t),gz+off+j*.021+(.017*math.cos(4*t) if k==4 else 0)))
    surface(repair,m,pts,[(k*side+i,k*side+(i+1)%side,(k+1)*side+(i+1)%side,(k+1)*side+i) for k in range(4) for i in range(side)])
    lathe(repair,dark,x+.015,y,gz+.48+j*.021,[(0,.039),(.015,.039)],16)
    stem=gz+.71+j*.021
    for k in range(9):
        t1=math.pi*k/9;t2=math.pi*(k+1)/9
        rod(repair,dark,(x+.061-.031*math.cos(t1),y,stem+.11+.033*math.sin(t1)),(x+.061-.031*math.cos(t2),y,stem+.11+.033*math.sin(t2)),.009)
    rod(repair,steel,(x+.03,y,stem-.015),(x+.03,y,stem+.11),.008)
report['new_lights']=[[cx0,-74.28,11.43],[cx1-.4,-72.38,11.69]]
views['stall']=[[cx0-1.13,-78.54,ground(cx0-1.13,-78.54)+1.64],[cx0,-74.32,10.25]]
views['counter']=[[cx0+.73,-76.66,ground(cx0+.73,-76.66)+1.64],[cx0-.17,-74.57,10.13]]
views['repair']=[[-11.03,-77.30,ground(-11.03,-77.3)+1.64],[cx1-.1,-72.30,10.86]]
views['stairs']=[[-23.92,-81.05,ground(-23.92,-81.05)+1.64],[cx,-78.55,8.66]]
views['court']=[[ -34.,7.,22.15],[-18.7,1.,20.62]]
import sys
sys.path.insert(0,str(W))
from east_blocks_r24 import build as add_east_blocks
report['east']=add_east_blocks(scene,S,spatial,bounds,surface,box,mat,bpy)
from flyover_frontage_r24 import build as add_flyover
report['flyover']=add_flyover(scene,S,spatial,surface,box,rod,mat)
views['viaduct']=[[-21.40,-80.62,9.46],[-21.40,-101.70,10.0]]
finish()
bpy.context.preferences.filepaths.save_version=0
scene['street_revision']='R24 market terraces internal'
bpy.ops.wm.save_as_mainfile(filepath=str(S/'chongqing_district.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
lookup={};dummy=mat('original_slot',(.5,.5,.5))
for i,(name,o) in enumerate(dirty.items()):
    assert len(o.data.materials)==1,name
    dup=o.copy();dup.data=o.data.copy();dup.modifiers.clear();dup.name='R24Donor%03d'%i
    scene.collection.objects.link(dup);dup.data.materials.clear();dup.data.materials.append(dummy);dup.hide_set(False)
    dup.select_set(True);lookup[dup.name]=name
for o in made:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(export/'frontage.glb'),export_format='GLB',use_selection=True,export_animations=False,export_yup=True)
def godot(xyz):return [xyz[0],xyz[2],-xyz[1]]
spec=dict(donors=lookup,views={k:[godot(a),godot(b)] for k,(a,b) in views.items()},lights=[godot(p) for p in report['new_lights']],resident=godot((cx0+.23,-74.12,ground(cx0+.23,-74.12))))
spec['fixtures']=fixtures
spec['retire']=report['flyover']['retired']
(export/'frontage.json').write_text(json.dumps(spec,indent=1),encoding='utf8')
(S/'geometry.json').write_text(json.dumps(report,indent=1),encoding='utf8')
print('R24_FRONTAGE',len(dirty),len(made),rails,report['stairs'],flush=True)

