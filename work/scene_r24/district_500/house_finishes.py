"""Site-specific finishes baked from the district's own mineral surfaces."""
from math import cos, sin, pi, ceil
import bpy
import numpy as np


def finishes(assets, materials, material):
    n=768
    y,x=np.mgrid[:n,:n]/n
    def scan(name):
        src=bpy.data.images.load(str(assets/("chongqing_district_"+name)),check_existing=True)
        w,h=src.size
        buf=np.empty(w*h*4,np.float32)
        src.pixels.foreach_get(buf)
        return buf.reshape(h,w,4)[(y*(h-1)).astype(int),(x*(w-1)).astype(int),:3]
    def packed(name,rgb):
        i=material(name,(.45,.42,.36))
        im=bpy.data.images.new(name,n,n,alpha=False)
        data=np.ones((n,n,4),np.float32); data[:,:,:3]=np.clip(rgb,.008,.92)
        im.pixels.foreach_set(data.ravel()); im.update(); im.pack()
        graph=materials[i].node_tree
        tex=graph.nodes.new("ShaderNodeTexImage");tex.image=im
        graph.links.new(tex.outputs["Color"],graph.nodes.get("Principled BSDF").inputs["Base Color"])
        return i
    plaster=scan("plastered_wall_04_diff_1k.jpg"); stone=scan("concrete_floor_worn_001_diff_2k.jpg")
    tone=plaster.mean(axis=2); grit=stone.mean(axis=2)
    def norm(v):
        return np.clip((v-np.mean(v))/(np.std(v)+1e-6),-3,3)
    tone=norm(tone); grit=norm(grit)
    variation=1+.085*tone+.046*grit
    limit=.355+.0018*tone
    wet=np.exp(-y*16)*(1+.2*np.sin(2*pi*x)+.17*grit)
    upper=np.array([.67,.60,.49])
    palettes=[(.23,.32,.25),(.36,.265,.20),(.28,.31,.32)]
    results=[]
    for i,low in enumerate(palettes):
        rgb=np.where((y<limit)[:,:,None],low,upper)*variation[:,:,None]
        scuff=(grit+tone*.21>1.72+1.0*y)&(y<limit)&(y>.015)
        rgb=np.where(scuff[:,:,None],rgb*.58+upper*.42,rgb)
        stripe=(y>=limit)&(y<limit+.004)
        rgb[stripe]*=.58
        rgb*=np.clip(1-.39*wet, .44,1)[:,:,None]
        results.append(packed("Limewash and worn oil dado "+str(i+1),rgb))
    # 30 cm mineral tiles, with individual pieces, recessed mortar and granular wear.
    count=6;ix=(x*count).astype(int);iy=(y*count).astype(int)
    rng=np.random.default_rng(2548);noise=rng.random((n,n))
    shade=rng.uniform(.955,1.045,(count,count))[iy,ix]
    dx=np.minimum((x*count)%1,1-(x*count)%1);dy=np.minimum((y*count)%1,1-(y*count)%1)
    dist=np.minimum(dx,dy)
    speck=np.where(noise>.89,.16,np.where(noise<.11,-.17,0))
    floors=[]
    for i,col in enumerate(((.33,.305,.254),(.40,.30,.235))):
        rgb=np.array(col)*(shade*(1+.09*grit+.03*tone+speck))[:,:,None]
        grout=((dist-.004)/.013).clip(0,1)[:,:,None]
        rgb=rgb*grout+np.array([.15,.135,.116])*(1-grout)
        floors.append(packed("Worn small terrazzo tiles "+str(i+1),rgb))
    paper=material("Neighbourhood paper notices",(.76,.71,.61))
    graph=materials[paper].node_tree; bs=graph.nodes.get("Principled BSDF")
    tex=graph.nodes.new("ShaderNodeTexImage")
    tex.image=bpy.data.images.load(str(assets/"district_age/wall_prints.png"),check_existing=True);tex.image.pack()
    graph.links.new(tex.outputs["Color"],bs.inputs["Base Color"]);graph.links.new(tex.outputs["Alpha"],bs.inputs["Alpha"])
    materials[paper].surface_render_method="DITHERED"
    return {"paint":results,"floors":floors,"paper":paper}


def coat_wall(face, pts, width, bottom, top, mat, phase=0):
    face(pts,mat,[(phase,bottom/2.65),(phase+width/2.65,bottom/2.65),
                  (phase+width/2.65,top/2.65),(phase,top/2.65)])


def floor_surface(face,x0,y0,x1,y1,h,mat):
    nx=max(1,ceil((x1-x0)/.34)); ny=max(1,ceil((y1-y0)/.34))
    for i in range(nx):
        left,right=x0+(x1-x0)*i/nx,x0+(x1-x0)*(i+1)/nx
        for j in range(ny):
            near,far=y0+(y1-y0)*j/ny,y0+(y1-y0)*(j+1)/ny
            xy=[(left,near),(right,near),(right,far),(left,far)]
            face([(a,b,h) for a,b in xy],mat,[(a/1.8,b/1.8) for a,b in xy])


def main_room(p,box,face,m,wall_pieces):
    w,d,z=p["width"]/2,p["depth"]/2,p["height"]
    number=p["plot_id"]
    floor_surface(face,-w+.242,-d+.235,w-.242,d-.235,z+.039,m["floors"][int(p["kind"]==0 and not p["name"])])
    paint=m["paint"][p["kind"]%3]
    # The back wall returns on either side of the door. Keep its opening and lintel.
    gap=1.92 if p["name"] else 1.08
    for a,b in ((-w+.24,p["door_u"]-gap),(p["door_u"]+gap,w-.24)):
        if b-a<.05 or p.get("registered_site"): continue
        for edge,sign in ((d-.234,-1),(-d+.234,1)):
            if sign==1:continue
            pts=[(a,edge,z+.04),(b,edge,z+.04),(b,edge,z+2.74),(a,edge,z+2.74)]
            if sign==1:pts=[pts[1],pts[0],pts[3],pts[2]]
            coat_wall(face,pts,b-a,.04,2.74,paint,a*.16)
    if not p["name"]:
        edge=-d+.234
        for a,b,h0,h1 in wall_pieces(p):
            h0,h1=max(.04,h0),min(2.74,h1)
            pts=[(b,edge,z+h0),(a,edge,z+h0),(a,edge,z+h1),(b,edge,z+h1)]
            coat_wall(face,pts,b-a,h0,h1,paint,a*.16)
    for sign in (-1,1):
        x=sign*(w-.304)
        for a,b in ((-d+.24,-1.19),(1.19,d-.24)):
            pts=[(x,a,z+.041),(x,b,z+.041),(x,b,z+2.74),(x,a,z+2.74)]
            if sign>0:pts=[pts[1],pts[0],pts[3],pts[2]]
            coat_wall(face,pts,b-a,.041,2.74,paint,a*.13)
    # Registered municipal papers belong at the public entrance, beside the door.
    if not p["name"]:
        u=p["door_u"]+gap+.49;y=-d-.008
        size=.70 if number%3 else .93
        cell=(number+2)%8;s,t=(cell%4)/4,(1-cell//4)/2
        face([(u-size/2,y,z+1.10),(u+size/2,y,z+1.10),(u+size/2,y,z+1.10+size),(u-size/2,y,z+1.10+size)],
             m["paper"],[(s,t),(s+.25,t),(s+.25,t+.5),(s,t+.5)])
    else:
        for x in p["frame"]["u"][1:-1]:
            r=p["frame"]["radius"]+.005
            for y in p["frame"]["v"]:
                for a,b in (((x-r,y-r),(x+r,y-r)),((x+r,y-r),(x+r,y+r)),((x+r,y+r),(x-r,y+r)),((x-r,y+r),(x-r,y-r))):
                    coat_wall(face,[(*a,z+.042),(*b,z+.042),(*b,z+1.34),(*a,z+1.34)],2*r,.042,1.34,paint,.2*x)
        # Two shallow drainage grates follow the stall rows. Segmented cast-iron covers.
        if p["name"].endswith("市场"):
            for x in (p["door_u"]-1.84,p["door_u"]+1.82):
                for n in range(int((2*d-.74)/.52)):
                    y=-d+.4+n*.52
                    box(x-.064,y,z+.040,x+.064,y+.51,z+.045,m["iron"])
                    for j in range(5):
                        box(x-.054,y+.056+j*.095,z+.045,x+.054,y+.091+j*.095,z+.048,m["metal"])


def sleep_room(p,lo,hi,front,floor,block,skin,m,i):
    seed=p["plot_id"]+i
    paint=m["paint"][(seed+1)%3]
    # Continuous lining and tile joints measured in room coordinates.
    for x,sign in ((lo+.196,1),(hi-.010 if i==0 else hi-.187,-1)):
        q0,q1=front+.22,12.565
        if i==0 and sign<0:x=hi-.006
        pts=[(x,q0,floor+.014),(x,q1,floor+.014),(x,q1,floor+2.29),(x,q0,floor+2.29)]
        if sign<0:pts=[pts[1],pts[0],pts[3],pts[2]]
        coat_wall(skin,pts,q1-q0,.014,2.29,paint,.13*seed)
    rear=12.564; mid=(lo+hi)/2+.4
    for a,b,h0,h1 in ((lo,hi,0,.855),(lo,mid-.92,.855,2.29),(mid+.92,hi,.855,2.29),(mid-.92,mid+.92,1.935,2.29)):
        coat_wall(skin,[(a,rear,floor+h0),(b,rear,floor+h0),(b,rear,floor+h1),(a,rear,floor+h1)],
                  b-a,h0,h1,paint,a*.23)
    # Replaster the window and door returns of the fourth wall, leaving each opening clear.
    door=lo+(hi-lo)*(.36 if i==0 else .64)
    fy=front+.216
    def front_patch(a,b,h0,h1):
        pts=[(b,fy,floor+h0),(a,fy,floor+h0),(a,fy,floor+h1),(b,fy,floor+h1)]
        coat_wall(skin,pts,b-a,h0,h1,paint,b*.23)
    for a,b in ((lo,door-.56),(door+.56,hi)):
        if b-a<1.75:front_patch(a,b,.01,2.29)
        else:
            wx=(a+b)/2;span=min(1.06,(b-a)*.34)
            front_patch(a,b,.01,.875);front_patch(a,wx-span,.875,2.29)
            front_patch(wx+span,b,.875,2.29);front_patch(wx-span,wx+span,1.925,2.29)
    floor_surface(skin,lo+.19,front+.21,hi-.02,12.57,floor+.005,m["floors"][seed%2])
    # Ceramic wall clock, painted rim, recessed face, hour indices and two hands.
    # Mounted above the bed on the end wall, clear of the towel rack.
    x=hi-(.204 if i else .028); cy,cz=11.44,floor+1.70
    def dial(rr,dx,key):
        pts=[(x-dx,cy+rr*cos(j*pi/16),cz+rr*sin(j*pi/16)) for j in range(32)]
        skin(pts,key);skin(pts[::-1],key)
    dial(.188,.010,"wood");dial(.168,.019,"linen")
    for j in range(12):
        a=j*pi/6; dr=.022 if j%3==0 else .014
        pts=[(x-.021,cy+r*cos(a)-v*sin(a),cz+r*sin(a)+v*cos(a)) for r,v in ((.147-dr,-.006),(.147,-.006),(.147,.006),(.147-dr,.006))]
        skin(pts,"iron");skin(pts[::-1],"iron")
    for angle,length in ((.61+seed%4,.100),(2.4,.134)):
        dy,dz=cos(angle),sin(angle)
        pts=[(x-.024,cy-.008*dz,cz+.008*dy),(x-.024,cy+dy*length,cz+dz*length),(x-.024,cy+.008*dz,cz-.008*dy)]
        skin(pts,"iron");skin(pts[::-1],"iron")
