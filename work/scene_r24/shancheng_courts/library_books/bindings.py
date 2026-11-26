"""Jinma library volumes. Coordinates within each book are thickness, cover width, height."""
from pathlib import Path
from math import cos, sin, pi
from random import Random
import bpy

here=Path(__file__).resolve().parent

def surface(name,color_map,roughness,rough_map=None):
    material=bpy.data.materials.new(name)
    material.use_nodes=True
    nodes=material.node_tree
    shader=nodes.nodes.get("Principled BSDF")
    shader.inputs["Roughness"].default_value=roughness
    for filename,socket in ((color_map,"Base Color"),(rough_map,"Roughness")):
        if not filename:continue
        tex=nodes.nodes.new("ShaderNodeTexImage")
        tex.image=bpy.data.images.load(str(here/filename),check_existing=True)
        if socket=="Roughness":tex.image.colorspace_settings.name="Non-Color"
        tex.image.pack()
        nodes.links.new(tex.outputs["Color"],shader.inputs[socket])
    return material

def materials():
    return [surface("Jinma printed bookcloth and jackets","jackets.jpg",.69,"binding_roughness.png"),
            surface("Jinma cut paper signatures","cut_paper.png",.89),
            surface("Jinma printed reading spread","reading_spread.jpg",.85)]

class Volumes:
    def __init__(self,name,point,mats):
        self.name,self.point,self.mats=name,point,mats
        self.vertices,self.faces,self.slots,self.uvs=[],[],[],[]
        self.count=0
        self.prints=set()

    def face(self,points,slot,uv):
        start=len(self.vertices)
        self.vertices.extend(points)
        self.faces.append(tuple(range(start,start+len(points))))
        self.slots.append(slot)
        self.uvs.extend(uv)

    def book(self,origin,size,edition,mode="standing",slope=0,yaw=0,reverse=False,aged=False):
        w,d,h=size
        x0,y0,z0=origin
        direction=-1 if reverse else 1
        ca,sa=cos(slope),sin(slope)
        cy,sy=cos(yaw),sin(yaw)
        lift=max(0,w*sa)
        cache={}
        def at(p):
            if p not in cache:
                x,y,z=p
                if mode=="flat":u,v,up=y,z,x
                elif mode=="display":u,v,up=y,-x,z
                else:u,v,up=x*ca+z*sa,y,z*ca-x*sa+lift
                cache[p]=self.point(x0+direction*(u*cy-v*sy),y0+direction*(v*cy+u*sy),z0+up)
            return cache[p]
        def jacket(points,rect):
            # rect uses pixels from the plate's upper left; UVs start at its lower left.
            l,t,r,b=rect
            cellx,celly=edition%8*512,edition//8*256
            uv=[((cellx+u)/4096,1-(celly+v)/2048) for u,v in ((l,b),(r,b),(r,t),(l,t))]
            self.face([at(p) for p in points],0,uv)
        def page(points,scale=1.0):
            off=(edition%7)*.087
            width=(.43 if aged else .32)*scale
            tone=(1 if aged else (0,2,3)[edition%3])*.25
            self.face([at(p) for p in points],1,[(off,tone+.009),(off+width,tone+.009),
                                                  (off+width,tone+.24),(off,tone+.24)])
        self.count+=1
        self.prints.add(edition)
        thick=.0011 if w<.032 else .0026
        gap=.002 if w<.032 else .0042
        # Front and back boards slightly overhang the paper block. Narrow edge polygons
        # fold the printed stock over the board at the head, tail and fore-edge.
        for side in (0,1):
            outer=w if side else 0.
            inner=w-thick if side else thick
            ring=[(outer,0,0),(outer,d,0),(outer,d,h),(outer,0,h)]
            inside=[(inner,0,0),(inner,d,0),(inner,d,h),(inner,0,h)]
            if not side:
                ring=[ring[i] for i in (1,0,3,2)]
                inside=[inside[i] for i in (1,0,3,2)]
            jacket(ring,(291,5,502,248) if side else (7,5,209,248))
            # Cover flaps inside the edge; the printed face stays on the exterior.
            jacket(inside[::-1],(24,42,105,57))
            for i in range(4):
                j=(i+1)%4
                jacket([ring[j],ring[i],inside[i],inside[j]],(291,10,296,245))
        # Four facets turn the wrap into the spine; preserve continuous printed artwork.
        def curve(t,z):
            return w*t,-.0011-(.11 if w>.032 else .055)*w*sin(pi*t),z
        for j in range(4):
            a,b=j/4,(j+1)/4
            jacket([curve(a,0),curve(b,0),curve(b,h),curve(a,h)],(218+a*60,6,218+b*60,248))
            jacket([curve(a,h),curve(b,h),(w*b,gap,h),(w*a,gap,h)],(220,14,276,18))
            jacket([curve(b,0),curve(a,0),(w*a,gap,0),(w*b,gap,0)],(220,14,276,18))
        # Woven endband at the head of selected hardbacks, folded into the spine.
        if w>.038 and edition%3==0:
            jacket([(thick,.0004,h-.0006),(w-thick,.0004,h-.0006),
                    (w-thick,gap+.0025,h-.001),(thick,gap+.0025,h-.001)],(221,198,275,204))
        # Inset signatures leave a lip of cover visible; the cut lines run across
        # the book's thickness on each of the three exposed paper surfaces.
        l,r=thick,w-thick
        front,back=gap,d-gap
        page([(l,front,h-gap),(r,front,h-gap),(r,back,h-gap),(l,back,h-gap)])
        page([(r,front,gap),(l,front,gap),(l,back,gap),(r,back,gap)])
        page([(r,back,gap),(l,back,gap),(l,back,h-gap),(r,back,h-gap)])

    def open_book(self,x,y,z):
        # A splayed spread has a low glued gutter, arched leaves and a visible
        # stack of underlying signatures resting on the desk.
        self.count+=1
        # A visible jacket lip extends beyond the fore edge and the tail of the spread.
        for side in (-1,1):
            outer=x+side*.217
            pts=[self.point(x,y-.004,z+.002),self.point(outer,y-.004,z+.002),
                 self.point(outer,y+.298,z+.002),self.point(x,y+.298,z+.002)]
            if side<0:pts.reverse()
            self.face(pts,0,[(.056,.986),(.057,.986),(.057,.983),(.056,.983)])
            last=None
            for t in (0,.08,.25,.50,.75,1.):
                a=x+side*.212*t
                top=z+.013+.023*sin(t*pi*.92)
                new=[self.point(a,y,top),self.point(a,y+.294,top)]
                if last is not None:
                    pts=[last[0],new[0],new[1],last[1]]
                    uv=[(.5+side*old*.49,.015),(.5+side*t*.49,.015),(.5+side*t*.49,.985),(.5+side*old*.49,.985)]
                    if side<0:pts.reverse();uv.reverse()
                    self.face(pts,2,uv)
                    for idx,bound in ((0,y),(1,y+.294)):
                        pts=[self.point(x+side*.212*old,bound,z+.002),self.point(a,bound,z+.002),new[idx],last[idx]]
                        if (side<0)!=(idx==1):pts.reverse()
                        self.face(pts,1,[(.1,.51),(.1,.74),(.4,.74),(.4,.51)])
                last,old=new,t
            pts=[self.point(a,y,z+.002),self.point(a,y+.294,z+.002),new[1],new[0]]
            if side<0:pts.reverse()
            self.face(pts,1,[(.1,.1),(.1,.94),(.4,.94),(.4,.1)])

    def save(self):
        mesh=bpy.data.meshes.new(self.name)
        mesh.from_pydata(self.vertices,[],self.faces)
        for mat in self.mats:mesh.materials.append(mat)
        mesh.polygons.foreach_set("material_index",self.slots)
        uv=mesh.uv_layers.new(name="Binding print UV")
        uv.data.foreach_set("uv",[v for pair in self.uvs for v in pair])
        mesh.update()
        obj=bpy.data.objects.new(self.name,mesh)
        obj["volumes"]=self.count
        obj["printed_designs"]=len(self.prints)
        bpy.context.collection.objects.link(obj)

def fill_case(index,start,end,y,bays,storey,point,mats,tiers,pitch,deck):
    rng=Random(1864+index)
    unit=(end-start)/bays
    reverse=index==2
    direction=-1 if reverse else 1
    batch=Volumes("Court_Jinma_Books_Case_%d"%(index+1),point,mats)
    for k in range(tiers):
        base=storey+.16+k*pitch+deck
        for j in range(bays):
            x=start+j*unit+.049
            right=start+(j+1)*unit-.049
            feature=(j*3+k+index)%11==2
            flat=(j+3*k+2*index)%12==3
            if flat:
                # One returned stack per few bays. A flat book's height becomes its shelf depth.
                height=.0
                for m in range(3+(j+k)%3):
                    thick=rng.uniform(.018,.033)
                    batch.book((x+(.205 if reverse else 0),y-direction*.156,base+height),
                               (thick,.18,.243),(7*j+5*k+m)%64,"flat",reverse=reverse,yaw=.014*sin(m+j))
                    height+=thick
                x+=.21
            # Acquisition runs share trim size, stock and publication design. Mix in
            # individually donated books; leave the occasional book-width space.
            run=0
            while x<right-.025:
                family=(j+2*k+3*index+run*3)%8
                count=rng.randint(3,7)
                first=rng.randrange(8)
                h0=rng.choice((.225,.249,.268,.286,.301))
                w0=rng.uniform(.021,.038)
                d0=h0*rng.uniform(.63,.72)
                inset=rng.uniform(.016,.049)
                leaning=(run+2*k+j)%6==1
                for n in range(count):
                    edition=family*8+(first+n)%8
                    h=h0+rng.uniform(-.006,.006)
                    w=w0*rng.uniform(.72,1.24)
                    d=d0+rng.uniform(-.005,.005)
                    if n==count-1 and rng.random()<.62:
                        edition=rng.randrange(64)
                        h=rng.uniform(.202,.304)
                        d=h*.71
                    face=feature and n==0 and run==1
                    angle=.064 if leaning and not face else 0.
                    # Parallel tilted bindings share a slope. Reserve the last
                    # book's complete swept width before starting the next run.
                    width=d if face else w*cos(angle)+h*sin(angle)
                    if x+width>right:
                        x=right
                        break
                    u=x+width if reverse else x
                    v=y+direction*(-.211+inset+rng.uniform(-.004,.004))
                    batch.book((u,v,base),(w,d,h),edition,"display" if face else "standing",
                               angle,reverse=reverse,aged=(family+n)%4<2)
                    advance=width if face or n==count-1 else w/max(.99,cos(angle))
                    x+=advance+rng.uniform(.0006,.0028)
                x+=rng.uniform(.005,.019) if rng.random()<.77 else rng.uniform(.025,.055)
                run+=1
    batch.save()

def fill_tables(length,depth,storey,point,mats):
    batch=Volumes("Court_Jinma_Books_DisplayTables",point,mats)
    for desk,frac in enumerate((.23,.40,.84)):
        centre=length*frac
        for pile in range(3):
            x=centre-.79+pile*.56
            y=depth*.40-.19
            base=storey+.86
            if desk==1 and pile==1:
                batch.open_book(x+.17,y,base)
                continue
            for layer in range(2+pile%2):
                thick=.023+.007*((desk+pile+layer)%3)
                size=(thick,.19+.018*pile,.27+.025*((desk+pile)%3))
                batch.book((x+.004*layer,y+.004*(layer%2),base),size,(11*desk+7*pile+layer)%64,
                           "flat",yaw=.075*sin((1+desk)*3+pile*2+layer))
                base+=thick
    batch.save()
