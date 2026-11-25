"""Model the registered Renai wings and Jinma school in their existing public court."""
from pathlib import Path
from math import ceil, cos, sin, pi
from runpy import run_path
import json
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
out = here.parents[2] / "work/project/chongqing_godot_v05/assets/district_500"
study = json.loads((here/"registered.json").read_bytes())
layout = json.loads((out/"layout.json").read_bytes())
verts, faces = [], []
for obj in bpy.context.scene.objects:
    if obj.name.startswith("COL_Outer500_Surface_"):
        offset = len(verts)
        verts.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in face.vertices) for face in obj.data.polygons)
ground = BVHTree.FromPolygons(verts,faces)
def elevation(q):
    hit = ground.ray_cast((*q,160),(0,0,-1))[0]
    if hit is None:
        raise ValueError(f"Missing survey ground at {q}")
    return float(hit.z)

bpy.ops.wm.read_factory_settings(use_empty=True)
assets = out.parent
mats = []
def finish(name, color, texture=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    base = m.node_tree.nodes.get("Principled BSDF")
    base.inputs["Roughness"].default_value=.81
    m.diffuse_color=(*color,1)
    base.inputs["Base Color"].default_value=(*color,1)
    if texture:
        tex=m.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image=bpy.data.images.load(str(assets/("chongqing_district_"+texture)),check_existing=True)
        tex.image.pack()
        # Blender 4.3's glTF exporter recognizes an RGBA Mix multiplier.
        # Carry the same metric texture and tint to Godot, including the flag courses.
        tint=m.node_tree.nodes.new("ShaderNodeMix")
        tint.data_type="RGBA"
        tint.blend_type="MULTIPLY"
        tint.inputs[0].default_value=1.
        tint.inputs[7].default_value=(*(1.-.72*(1.-v) for v in color),1.)
        m.node_tree.links.new(tex.outputs[0],tint.inputs[6])
        m.node_tree.links.new(tint.outputs[2],base.inputs["Base Color"])
        path=assets/("chongqing_district_"+texture.replace("_diff","_nor_gl"))
        if path.exists():
            relief=m.node_tree.nodes.new("ShaderNodeTexImage")
            relief.image=bpy.data.images.load(str(path),check_existing=True)
            relief.image.colorspace_settings.name="Non-Color"
            relief.image.pack()
            normal=m.node_tree.nodes.new("ShaderNodeNormalMap")
            normal.inputs["Strength"].default_value=.48
            m.node_tree.links.new(relief.outputs[0],normal.inputs["Color"])
            m.node_tree.links.new(normal.outputs[0],base.inputs["Normal"])
    mats.append(m)
    return len(mats)-1

lime=finish("Renai ivory mineral render",(.87,.83,.76),"plastered_wall_04_diff_1k.jpg")
chalk=finish("Weathered school limewash",(.80,.78,.65),"plastered_wall_04_diff_1k.jpg")
stone=finish("Honed grey sandstone",(.52,.49,.42),"concrete_floor_worn_001_diff_2k.jpg")
band=finish("Pale carved architraves",(.83,.78,.65),"plastered_wall_04_diff_1k.jpg")
brick=finish("Exposed grey masonry at grade",(.48,.45,.40),"brick_wall_08_diff_2k.jpg")
roof=finish("Glazed grey roof tiles",(.29,.32,.34),"roof_tiles_diff.jpg")
timber=finish("Dark oiled timber",(.32,.22,.16),"wood_table_worn_diff_2k.jpg")
sash=finish("School timber casements",(.36,.23,.16),"wood_table_worn_diff_2k.jpg")
red=finish("Faded iron-oxide eaves",(.28,.054,.032))
iron=finish("Oxidized iron",(.14,.15,.14))
glass=finish("Deep window reflections",(.040,.058,.055))
flags=[finish("Courtyard flags "+str(i),c,"concrete_floor_worn_001_diff_2k.jpg") for i,c in enumerate(((.51,.50,.45),(.60,.59,.52),(.48,.50,.46)))]
glazing=mats[glass]
glazing.surface_render_method="BLENDED"
glazing.node_tree.nodes.get("Principled BSDF").inputs["Alpha"].default_value=.66
glazing.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value=.34
fired=finish("Original fired-brick school piers",(.87,.30,.17),"brick_wall_08_diff_2k.jpg")
green=finish("Painted school green",(.11,.25,.17))
pages=finish("Reading room paper",(.72,.61,.41))

class Mesh:
    def __init__(self,name):
        self.name=name
        self.vertices=[]
        self.faces=[]
        self.slots=[]
    def face(self,points,material):
        offset=len(self.vertices)
        self.vertices.extend(tuple(p) for p in points)
        self.faces.append(tuple(range(offset,offset+len(points))))
        self.slots.append(material)
    def solid(self,lower,upper,material):
        self.face(lower[::-1],material)
        self.face(upper,material)
        for i in range(len(lower)):
            j=(i+1)%len(lower)
            self.face([lower[i],lower[j],upper[j],upper[i]],material)
    def save(self):
        geo=bpy.data.meshes.new(self.name)
        geo.from_pydata(self.vertices,[],self.faces)
        geo.update()
        for m in mats:geo.materials.append(m)
        uv=geo.uv_layers.new()
        for poly,slot in zip(geo.polygons,self.slots):
            poly.material_index=slot
            n=poly.normal
            for i in poly.loop_indices:
                p=geo.vertices[geo.loops[i].vertex_index].co
                # Tile coursing follows the surface, including the upper slopes.
                uv.data[i].uv=(p.x*.48,p.y*.48) if abs(n.z)>.7 else ((p.y*n.x-p.x*n.y)*.48,p.z*.48)
        obj=bpy.data.objects.new(self.name,geo)
        bpy.context.collection.objects.link(obj)
        return obj

def build(record):
    key=record["id"]
    school=key=="jinma_classrooms"
    long_wing=key=="renai_long"
    a,b,c,d=np.asarray(record["points"])
    length=np.linalg.norm(b-a)
    depth=(np.linalg.norm(d-a)+np.linalg.norm(c-b))*.5
    floor=layout["historic_grades"][key]
    bays=13 if school else (21 if long_wing else 9)
    main_door=6 if school else (2 if long_wing else 4)
    pitch=length/bays
    storey=3.48 if school else 3.76
    height=2*storey if school else 2*storey+2.75
    body=Mesh("COL_Court_"+key)
    trim=Mesh("Court_Millwork_"+key)
    interior=Mesh("COL_Court_Structure_"+key)
    furniture=Mesh("Court_Fittings_"+key)
    def xy(x,y):
        f,g=x/length,y/depth
        return ((1-f)*a+f*b)*(1-g)+((1-f)*d+f*c)*g
    def point(x,y,h):
        return [*xy(x,y),floor+h]
    def slab(mesh,x0,y0,z0,x1,y1,z1,slot):
        loop=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        if (b[0]-a[0])*(d[1]-a[1]) < (b[1]-a[1])*(d[0]-a[0]):loop.reverse()
        mesh.solid([point(x,y,z0) for x,y in loop],[point(x,y,z1) for x,y in loop],slot)
    def profile(mesh,poly,near,far,slot):
        # Extrude a polygon drawn in facade coordinates along the reveal.
        front=[point(x,near,z) for x,z in poly]
        back=[point(x,far,z) for x,z in poly]
        if np.cross(b-a,d-a)>0: front.reverse();back.reverse()
        mesh.solid(front,back,slot)
    def beam(mesh,p1,p2,radius,slot):
        # Square-section structural rafters and sash members with mitred ends.
        v=np.array(p2)-p1
        v=v/np.linalg.norm(v)
        ref=np.array([0.,0.,1.]) if abs(v[2])<.94 else np.array([1.,0.,0.])
        u=np.cross(v,ref);u=radius*u/np.linalg.norm(u)
        w=radius*np.cross(v,u)
        offsets=[-u-w,u-w,u+w,-u+w]
        mesh.solid([p1+k for k in offsets],[p2+k for k in offsets],slot)
    def end_wall(x, side, z0, z1, tier):
        # The moving player sees the southeast end first, including its downhill basement.
        openings = 3 if not school else 4
        width = depth/openings
        def endbox(mesh,v0,h0,v1,h1,offset,thick,slot):
            ends=sorted((x+side*offset,x+side*(offset+thick)))
            slab(mesh,ends[0],v0,h0,ends[1],v1,h1,slot)
        def endpoly(mesh,poly,offset,thick,slot):
            near=[point(x+side*offset,y,h) for y,h in poly]
            far=[point(x+side*(offset+thick),y,h) for y,h in poly]
            if np.cross(b-a,d-a)*side<0:near.reverse();far.reverse()
            mesh.solid(near,far,slot)
        for bay in range(openings):
            u=(bay+.5)*width
            radius=min(.70,width*.28)
            bottom=z0+.63
            spring=z0+min(2.13,(z1-z0)*.56)
            top=spring+radius
            slot=brick if tier<0 else wall
            endbox(body,bay*width,z0,u-radius,z1,0,.30,slot)
            endbox(body,u+radius,z0,(bay+1)*width,z1,0,.30,slot)
            endbox(body,u-radius,z0,u+radius,bottom,0,.30,slot)
            if school or tier==2:
                endbox(body,u-radius,top,u+radius,z1,0,.30,slot)
                endbox(trim,u-radius,bottom,u+radius,top,.19,.025,glass)
                endbox(trim,u-radius-.06,top,u+radius+.06,top+.10,-.08,.11,band)
            else:
                arch=[(u+radius*cos(pi-j*pi/16),spring+radius*sin(pi-j*pi/16)) for j in range(17)]
                for (v0,h0),(v1,h1) in zip(arch,arch[1:]):
                    endpoly(body,[(v0,h0),(v1,h1),(v1,z1),(v0,z1)],0,.30,slot)
                endpoly(trim,[(u-radius,bottom),(u+radius,bottom)]+arch[::-1],.2,.03,glass)
                for j in range(16):
                    l=pi*(1-j/16)-.003;r=pi*(1-(j+1)/16)+.003
                    wedge=[(u+rr*cos(t),spring+rr*sin(t)) for rr,t in ((radius,l),(radius,r),(radius+.115,r),(radius+.115,l))]
                    endpoly(trim,wedge,-.08,.115,band)
            endbox(trim,u-.031,bottom,u+.031,spring,.11,.07,timber)
            endbox(trim,u-radius,spring-.15,u+radius,spring-.09,.11,.07,timber)
            endbox(trim,u-radius-.09,bottom-.10,u+radius+.09,bottom,-.12,.18,stone)
        endbox(trim,0,z1-.16,depth,z1-.06,-.10,.15,band)
    wall=chalk if school else lime
    low=min(elevation(q) for q in [a,b,c,d])-floor-.45
    if long_wing:
        # Basements are exposed on the falling ground. Keep their end reveals open.
        slab(body,0,0,min(low,-3.83),length-.34,depth,-.035,brick)
        end_wall(length,-1,-3.76,0,-1)
    else:
        slab(body,0,0,min(low,-.3),length,depth,-.035,brick)
    for level in ([0,1] if school else [0,1,2]):
        z=level*storey
        if school and level==1:
            x0=length*.56-.38;x1=length*.56+23*.35+.91
            y0=depth*.54-1.00;y1=depth*.54+1.00
            for l,r,v,w in ((.05,x0,.05,depth-.05),(x1,length-.05,.05,depth-.05),(x0,x1,.05,y0),(x0,x1,y1,depth-.05)):
                slab(body,l,v,z-.115,r,w,z,timber)
            for y in (y0,y1):slab(interior,x0,y-.08,z-.24,x1,y+.08,z,timber)
        else:
            slab(body,.05,.05,z-.115,length-.05,depth-.05,z,stone if level==0 else timber)
        upper=height if not school and level==2 else z+storey
        for rear in (False,True):
            y=depth if rear else 0
            inside=-1 if rear else 1
            def wallbox(x0,h0,x1,h1,slot=wall):
                slab(body,x0,y,h0,x1,y+inside*.31,h1,slot) if inside>0 else slab(body,x0,y-.31,h0,x1,y,h1,slot)
            def facebox(mesh,x0,h0,x1,h1,offset,thick,slot):
                ys=sorted((y+inside*offset,y+inside*(offset+thick)))
                slab(mesh,x0,ys[0],h0,x1,ys[1],h1,slot)
            for i in range(bays):
                center=(i+.5)*pitch
                entrance=(level==0 and (i==main_door or (key=="renai_cross" and not rear and i==1)))
                portal=long_wing and not rear and i==main_door
                roundlight=portal and level==1
                rad=min(.83,pitch*.34) if not entrance else min(1.10,pitch*.42)
                if roundlight:rad=min(pitch*.45,1.19)
                sill=z if entrance else z+(.40 if roundlight else (.70 if school else .74))
                spring=z+(2.37 if school else 2.24)
                if not school and level==2:spring=z+2.02
                arched=not school and level<2 and not roundlight
                left,right=center-rad,center+rad
                wallbox(i*pitch,z,left,upper)
                wallbox(right,z,(i+1)*pitch,upper)
                if not entrance:wallbox(left,z,right,sill)
                if arched:
                    curve=[(center+rad*cos(pi-k*pi/16),spring+rad*sin(pi-k*pi/16)) for k in range(17)]
                    for j,((x0,h0),(x1,h1)) in enumerate(zip(curve,curve[1:])):
                        profile(body,[(x0,h0),(x1,h1),(x1,upper),(x0,upper)],y,y+inside*.31,wall)
                        # Independent wedge ends leave a visible mortar joint in the ring.
                        lo=pi-(j+.025)*pi/16;hi=pi-(j+.975)*pi/16
                        vous=[(center+r*cos(t),spring+r*sin(t)) for r,t in ((rad,lo),(rad,hi),(rad+.115,hi),(rad+.115,lo))]
                        profile(trim,vous,y-inside*.085,y+inside*.04,band)
                    if not entrance:
                        shape=[(left,sill),(right,sill)]+list(reversed(curve))
                        profile(trim,shape,y+inside*.20,y+inside*.23,glass)
                        facebox(trim,left,spring-.08,right,spring-.025,.14,.055,timber)
                        for a0 in (pi*.25,pi*.50,pi*.75):
                            beam(trim,np.array(point(center,y+inside*.13,spring)),np.array(point(center+rad*.94*cos(a0),y+inside*.13,spring+rad*.94*sin(a0))),.018,timber)
                elif roundlight:
                    middle=z+1.74
                    for j in range(24):
                        t0,t1=j*2*pi/24,(j+1)*2*pi/24
                        def rc(t,r):return (center+r*cos(t),middle+r*sin(t))
                        def square(t):
                            return rc(t,rad/max(abs(cos(t)),abs(sin(t))))
                        profile(body,[rc(t0,rad),rc(t1,rad),square(t1),square(t0)],y,y+inside*.31,band)
                        profile(trim,[rc(t0,rad*.89),rc(t1,rad*.89),rc(t1,rad),rc(t0,rad)],y-.065,y+.04,band)
                        if j%3==0:
                            beam(trim,point(center,y+.13,middle),point(*[rc(t0,rad*.90)[0],y+.13,rc(t0,rad*.90)[1]]),.025,iron)
                    profile(trim,[rc(i*2*pi/32,rad*.89) for i in range(32)],y+.18,y+.21,glass)
                    wallbox(left,sill,right,middle-rad)
                    wallbox(left,middle+rad,right,upper)
                else:
                    top=z+(2.82 if school else 2.11)
                    wallbox(left,top,right,upper)
                    facebox(trim,left-.07,top,right+.07,top+.115,-.07,.13,band)
                    if not entrance:
                        open_leaf=school and not rear and i%3!=1
                        if open_leaf:
                            facebox(trim,left,sill,center,top,.20,.035,glass)
                            facebox(trim,center,top-.47,right,top,.20,.035,glass)
                        else:
                            facebox(trim,left,sill,right,top,.20,.035,glass)
                if not roundlight:
                    cap=spring if arched else (z+2.82 if school else z+2.11)
                    for x in (left,right):facebox(trim,x-.055,sill,x+.055,cap,-.035,.12,sash if school else band)
                    if not entrance:
                        facebox(trim,left-.09,sill-.09,right+.09,sill+.015,-.12,.20,stone)
                        facebox(trim,center-.032,sill,center+.032,cap,.105,.068,sash)
                        facebox(trim,left,cap-.49,right,cap-.435,.10,.065,sash)
                        # Both inner stops remain visible from the reading hall and through the glass.
                        facebox(trim,center-.026,sill,center+.026,cap,.245,.045,sash)
                        facebox(trim,left,cap-.48,right,cap-.43,.245,.046,sash)
                        for u in (left,right):
                            facebox(trim,u-.042,sill,u+.042,cap,.245,.089,sash)
                        if school and not rear and i%3!=1:
                            # Opposed open leaves, as seen in the school court photograph.
                            for sign in (-1,1):
                                hinge=center+sign*rad
                                p0=point(hinge,y-.035,sill+.06)
                                p1=point(hinge-sign*rad*.67,y-.34,sill+.06)
                                hh=np.array([0.,0.,cap-sill-.56])
                                for r0,r1 in ((p0,p1),(p0+hh,p1+hh),(p0,p0+hh),(p1,p1+hh)):
                                    beam(trim,np.array(r0),np.array(r1),.033,sash)
                if portal:
                    for x in (i*pitch+.10,(i+1)*pitch-.10):
                        facebox(trim,x-.12,z,x+.12,upper,-.17,.18,band)
            if school and level==0:
                for index in (main_door,):
                    mid=(index+.5)*pitch
                    for u in (mid-pitch*.44,mid+pitch*.44):
                        facebox(trim,u-.105,0,u+.105,2.93,-.115,.16,band)
                    facebox(trim,mid-pitch*.51,2.86,mid+pitch*.51,3.08,-.14,.17,band)
            facebox(trim,0,upper-.16,length,upper-.07,-.10,.12,stone if school else band)
        # Wall ends and the load-bearing timbers remain visible from the open passage.
        if long_wing and level==0:
            # The public hall continues through the transverse wing at the shared seam.
            gate=depth*.36
            slab(body,0,.28,z,.25,gate-1.07,upper,wall)
            slab(body,0,gate+1.07,z,.25,depth-.28,upper,wall)
            slab(body,0,gate-1.07,z+2.76,.25,gate+1.07,upper,wall)
        else:
            slab(body,0,.28,z,.25,depth-.28,upper,wall)
        end_wall(length,-1,z,upper,level)
        for i in range(0,bays+1,2):
            x=min(length-.18,max(.18,i*pitch))
            for frac in (.32,.70):
                slab(interior,x-.115,depth*frac-.115,z,x+.115,depth*frac+.115,upper-.20,fired if school and level==1 else timber)
                slab(trim,x-.19,depth*frac-.19,z,x+.19,depth*frac+.19,z+.22,stone)
            if school and level==0 and length*.56-.4<x<length*.56+23*.35+.95:
                for l,r in ((.20,depth*.54-1),(depth*.54+1,depth-.20)):
                    slab(interior,x-.105,l,upper-.31,x+.105,r,upper-.10,timber)
            else:
                slab(interior,x-.105,.20,upper-.31,x+.105,depth-.20,upper-.10,timber)
        for frac in (.32,.70):
            slab(interior,.15,depth*frac-.13,upper-.23,length-.15,depth*frac+.13,upper-.04,timber)
    # Pitched, hipped roof, projected drip edge and a visible ridge.
    e=.41; ridge=height+min(depth*.26,3.15)
    ridge_in=min(depth*.38,length*.21)
    edge=[point(-e,-e,height),point(length+e,-e,height),point(length+e,depth+e,height),point(-e,depth+e,height)]
    peak=[point(ridge_in,depth*.5,ridge),point(length-ridge_in,depth*.5,ridge)]
    for face in ([edge[0],edge[1],peak[1],peak[0]],[edge[1],edge[2],peak[1]],[edge[2],edge[3],peak[0],peak[1]],[edge[3],edge[0],peak[0]]):
        if np.cross(np.subtract(face[1],face[0]),np.subtract(face[2],face[0]))[2]<0:face=list(reversed(face))
        trim.face(face,roof)
    beam(trim,np.array(peak[0]),np.array(peak[1]),.09,roof)
    for y in (-e,depth+e):
        slab(trim,-e,y-.06,height-.17,length+e,y+.06,height+.04,timber if school else red)
    for i in range(1,bays):
        x=i*pitch
        for y in (.13,depth-.13):
            beam(trim,np.array(point(x,y,height-.20)),np.array(point(x,depth*.5,ridge-.12)),.085,timber)
    for near in (.42,length-.42):
        for v in (-.16,depth+.16):
            base_z=max(low,elevation(xy(near,v))-floor+.08)
            beam(trim,np.array(point(near,v,base_z)),np.array(point(near,v,height-.15)),.047,iron)
            for z in np.arange(max(0,base_z)+.22,height-.15,1.58):
                slab(trim,near-.09,v-.07,z,near+.09,v+.07,z+.045,iron)
    if long_wing:
        # Shallow pediment over the round light. Side returns give it a visible profile at a grazing angle.
        mid=(main_door+.5)*pitch
        poly=[(mid-1.5*pitch,height+.03),(mid+1.5*pitch,height+.03),(mid,height+1.4)]
        profile(trim,poly,-.35,.12,lime)
        for i in (0,1):
            beam(trim,np.array(point(poly[i][0],-.41,poly[i][1])),np.array(point(mid,-.41,height+1.4)),.095,band)
    stair_route=[]
    if school:
        x0=length*.56
        stair_y=depth*.54
        steps=23
        run=steps*.35
        half=.87
        # Continuous strings, solid treads and landing sit inside a trimmed floor opening.
        for j in range(steps):
            top=storey*(j+1)/steps
            x=x0+j*.35
            slab(interior,x,stair_y-half,top-.15,x+.35,stair_y+half,top,timber)
            slab(trim,x-.027,stair_y-half-.015,top-.035,x+.025,stair_y+half+.015,top,stone)
        for side in (-1,1):
            y=stair_y+side*(half+.035)
            beam(interior,np.array(point(x0,y,-.04)),np.array(point(x0+run,y,storey-.04)),.087,timber)
            beam(trim,np.array(point(x0,y,.85)),np.array(point(x0+run,y,storey+.85)),.038,timber)
            for j in range(0,steps+1,3):
                h=storey*j/steps;x=x0+j*.35
                slab(trim,x-.023,y-.023,h,x+.023,y+.023,h+.85,timber)
        slab(interior,x0+run,stair_y-half-.10,storey-.18,x0+run+.95,stair_y+half+.10,storey,timber)
        # Guard the upstairs gallery where the floor has been opened for the stair.
        for yy in (stair_y-1.0,stair_y+1.0):
            slab(interior,x0-.40,yy-.032,storey+.93,x0+run-.35,yy+.032,storey+1.00,timber)
            for xx in np.arange(x0-.34,x0+run-.39,.68):
                slab(interior,xx-.029,yy-.029,storey,xx+.029,yy+.029,storey+.95,timber)
        # Brick piers, tall cases, a display table and the palette of donated mixed bindings
        # are visible in Chongqing Daily's photographs. Individual titles are not reproduced.
        for branch in (1,3,10):
            x=pitch*branch
            for y in (depth*.25,depth*.77):
                slab(furniture,x-.15,y-.15,storey,x+.15,y+.15,height-.20,fired)
        bookcols=[red,sash,pages,iron,roof,band,timber,green]
        for start,end,y in [(1.1,11.7,depth-.72),(19.,length-1.0,depth-.72),(1.1,8.0,1.0)]:
            bays_n=max(1,int((end-start)/1.22))
            unit=(end-start)/bays_n
            for j in range(bays_n+1):
                x=start+j*unit
                slab(interior,x-.035,y-.20,storey+.10,x+.035,y+.19,storey+2.38,timber)
            for k in range(6):
                z=storey+.16+k*.43
                slab(interior,start,y-.22,z,end,y+.20,z+.038,timber)
                if k==5:continue
                for j in range(bays_n):
                    x=start+j*unit+.065
                    for idx in range(26):
                        bw=.035+.014*((idx*7+j+k)%5)
                        if x+bw>start+(j+1)*unit-.055:break
                        hh=.214+.027*((idx*13+j*3+k)%5)
                        slab(furniture,x,y-.182,z+.038,x+bw-.006,y+.085,z+hh,bookcols[(idx*7+j*3+k*5)%len(bookcols)])
                        x+=bw
        for frac in (.23,.40,.84):
            x=length*frac;y=depth*.40
            slab(interior,x-1.05,y-.48,storey+.77,x+1.05,y+.48,storey+.86,timber)
            for dx in (-.82,.82):
                for dy in (-.32,.32):
                    slab(furniture,x+dx-.05,y+dy-.05,storey,x+dx+.05,y+dy+.05,storey+.78,timber)
            for pile in range(3):
                for layer in range(2+pile%2):
                    z=storey+.86+.055*layer
                    xx=x-.64+pile*.50
                    slab(furniture,xx,y-.20,z,xx+.33,y+.17,z+.045,pages)
                    slab(furniture,xx-.005,y-.205,z+.042,xx+.335,y+.174,z+.053,bookcols[(pile+layer)%8])
            for delta in (-.73,.77):
                xx=x+delta;yy=y-.90
                slab(furniture,xx-.21,yy-.19,storey+.42,xx+.21,yy+.19,storey+.47,timber)
                for dx in (-.16,.16):
                    for dy in (-.15,.15):
                        slab(furniture,xx+dx-.025,yy+dy-.025,storey,xx+dx+.025,yy+dy+.025,storey+.43,timber)
                slab(furniture,xx-.20,yy-.19,storey+.67,xx+.20,yy-.13,storey+.87,timber)
        # Short display partitions on the ground level leave the front to rear passage open.
        for x in (pitch*2,pitch*10):
            slab(interior,x-.10,depth*.38,0,x+.10,depth*.61,2.43,chalk)
            slab(trim,x-.115,depth*.38,0,x+.115,depth*.61,.91,green)
            for y in (depth*.42,depth*.50,depth*.58):
                slab(trim,x+.105,y-.30,1.12,x+.16,y+.30,1.92,timber)
                slab(trim,x+.162,y-.255,1.18,x+.175,y+.255,1.85,pages)
        stair_route=[[float(v) for v in point(x,stair_y,h)] for x,h in ((x0-.64,0),(x0+.56,.30),(x0+run+.40,storey),(x0+run+1.32,storey))]
        stair_route.append([float(v) for v in point(x0+run+1.35,depth*.78,storey)])
        # One green canopy and folding chairs beside the frontage appear in the court photograph.
        ux=length*.83;uy=-2.60
        ground_z=elevation(xy(ux,uy))-floor
        slab(furniture,ux-.026,uy-.026,ground_z,ux+.026,uy+.026,ground_z+2.59,iron)
        for j in range(8):
            l=j*pi/4;r=(j+1)*pi/4
            tri=[point(ux,uy,ground_z+2.64),point(ux+1.46*cos(l),uy+1.46*sin(l),ground_z+2.17),point(ux+1.46*cos(r),uy+1.46*sin(r),ground_z+2.17)]
            furniture.face(tri,green);furniture.face(tri[::-1],green)
        slab(furniture,ux-.45,uy-.36,ground_z+.72,ux+.45,uy+.36,ground_z+.77,timber)
        for side in (-1,1):
            cx=ux+side*.97
            slab(furniture,cx-.205,uy-.22,ground_z+.44,cx+.205,uy+.22,ground_z+.48,timber)
            for yy in (uy-.18,uy+.18):
                for dx in (-1,1):
                    beam(furniture,np.array(point(cx+dx*.19,yy,ground_z)),np.array(point(cx-dx*.15,yy,ground_z+.46)),.018,iron)
        # The painted reading-room name is legible in the courtyard photograph.
        from mathutils import Matrix, Vector
        curve=bpy.data.curves.new("Jinma painted lettering","FONT")
        curve.body="山城·时光里图书馆"
        curve.font=bpy.data.fonts.load(str(here.parents[2]/"work/assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf"))
        curve.size=1.14
        curve.align_x="CENTER"
        obj=bpy.data.objects.new("Court_Jinma_painted_name",curve)
        bpy.context.collection.objects.link(obj)
        curve.materials.append(mats[red])
        midpoint=length*.76
        inward=xy(midpoint,1)-xy(midpoint,0)
        outward=Vector((-inward[0],-inward[1],0)).normalized()
        up=Vector((0,0,1))
        right=up.cross(outward)
        matrix=Matrix((right,up,outward)).transposed().to_4x4()
        matrix.translation=Vector(point(midpoint,-.022,3.03))
        obj.matrix_world=matrix
        bpy.context.view_layer.objects.active=obj
        obj.select_set(True)
        bpy.ops.object.convert(target="MESH")
        obj.select_set(False)
    for mesh in (body,trim,interior,furniture):
        if mesh.faces:mesh.save()
    mid=(main_door+.5)*pitch
    return {"id":key,"ring":record["points"],"floor":floor,"height_to_eaves":height,
            "bays":bays,"stairs_to_library":stair_route,"post_rows":[.32,.70],"entry":xy(mid,0).tolist(),"back":xy(mid,depth).tolist(),
            "inward":((xy(mid,1)-xy(mid,0))/np.linalg.norm(xy(mid,1)-xy(mid,0))).tolist(),
            "inside":xy(mid,depth*.52).tolist(), "joint":xy(0,depth*.36).tolist() if long_wing else xy(1.5*pitch,0).tolist(),
            "joint_inside":xy(1.05,depth*.36).tolist() if long_wing else xy(1.5*pitch,1.40).tolist()}

buildings=[build(s) for s in study["buildings"]]

paths=run_path(str(here/"court_paths.py"))["pave"](buildings,elevation,Mesh,flags,stone)
data={"buildings":buildings,"courtyard_connections":paths,"registered_source":"work/scene_r24/shancheng_courts/registered.json"}
(out/"historic_courts.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/"delivery_courts.blend"),compress=True)
bpy.ops.export_scene.gltf(filepath=str(out/"historic_courts.glb"),export_format="GLB",export_yup=True)
