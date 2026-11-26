"""The cliff-walk frontage and its open court. EN in metres, elevations in project datum."""
from math import ceil, cos, sin
import numpy as np


def local(p, x, y):
    c,s=cos(p["bearing"]),sin(p["bearing"])
    dx,dy=x-p["east_north"][0],y-p["east_north"][1]
    return c*dx+s*dy,-s*dx+c*dy


def upper(p, member, trim, m):
    z=p["height"]+2.95
    d=p["depth"]/2
    for v in [-d,d-.19]:
        for a,b in zip(p["frame"]["u"],p["frame"]["u"][1:]):
            l,r=(a+b)/2-.88,(a+b)/2+.88
            member(a,v,z,b,v+.19,z+.71,m["lime"])
            member(a,v,z+.71,l,v+.19,z+2.5,m["lime"])
            member(r,v,z+.71,b,v+.19,z+2.5,m["lime"])
            member(l,v,z+2.19,r,v+.19,z+2.5,m["lime"])
            trim(l-.09,v-.09,z+.66,r+.09,v+.23,z+.73,m["flags"])
            for u in (l,(l+r)/2,r):
                trim(u-.04,v+.06,z+.72,u+.04,v+.13,z+2.19,m["wood"])
            for h in (.74,1.72,2.14):
                trim(l,v+.06,z+h,r,v+.13,z+h+.047,m["wood"])
            for u in np.linspace(l,r,7)[1:-1]:
                trim(u-.016,v+.07,z+1.75,u+.016,v+.11,z+2.15,m["wood"])
            trim(l,v+.09,z+.8,r,v+.10,z+2.12,m["glass"])
    # Enclosed timber bays overhang the street on the two roof lots, as on the
    # cliff-walk frontage photograph. Joinery is a reconstruction at this scale.
    axes=p["frame"]["u"]
    for i in (1,len(axes)-3):
        a,b=axes[i]+.15,axes[i+1]-.15
        v=-d-.68
        trim(a,v,z-.13,b,-d+.14,z+.01,m["wood"])
        for u in np.linspace(a+.09,b-.09,5):
            trim(u-.043,v+.025,z-.19,u+.043,-d+.04,z-.075,m["wood"])
            trim(u-.039,v,z,u+.039,v+.09,z+2.32,m["wood"])
        for h in (.11,.56,1.70,2.20):
            trim(a,v-.015,z+h,b,v+.105,z+h+.066,m["wood"])
        for u in np.linspace(a+.08,b-.08,18):
            trim(u-.046,v+.029,z+.13,u+.046,v+.07,z+.59,m["wood"])
        for u in np.linspace(a+.08,b-.08,13):
            trim(u-.013,v+.03,z+1.75,u+.013,v+.095,z+2.23,m["wood"])
        trim(a-.13,v-.14,z+2.29,b+.13,-d+.07,z+2.43,m["tile"])
        for u in (a,b-.08):
            trim(u,v,z,u+.08,-d+.02,z+.62,m["wood"])
            trim(u,v,z+2.18,u+.08,-d+.02,z+2.32,m["wood"])
    for u in [-p["width"]/2,p["width"]/2-.21]:
        member(u,-d,z,u+.21,d,z+2.80,m["lime"])


def shopfront(p,member,trim,panel,m):
    """Shuttered flanking bays leave the working counter and through-passage open."""
    z=p["height"]
    d=p["depth"]*.5
    for rear in (False,True):
        v=d-.23 if rear else -d
        outer=d+.012 if rear else -d-.052
        sign=1 if rear else -1
        for i,(a,b) in enumerate(zip(p["frame"]["u"],p["frame"]["u"][1:])):
            if min(abs(a),abs(b))<2.02 or a<0<b or (not rear and min(abs(a),abs(b))<5):
                continue
            mid=(a+b)/2
            h=.76 if (i+int(rear))%3 else .95
            w=(b-a)*.31
            member(a,v,z,b,v+.22,z+h,m["wallstone"])
            for lo,hi in ((a,mid-w),(mid+w,b)):
                member(lo,v,z+h,hi,v+.22,z+2.68,m["lime"])
            member(mid-w,v,z+2.18,mid+w,v+.22,z+2.68,m["wood"])
            trim(mid-w-.07,outer-.04,z+h-.037,mid+w+.07,outer+.04,z+h+.06,m["flags"])
            for u in (mid-w,mid,mid+w):
                trim(u-.034,v+.05,z+h,u+.034,v+.12,z+2.19,m["wood"])
            for k in (h+.045,1.76,2.11):
                trim(mid-w,v+.045,z+k,mid+w,v+.122,z+k+.045,m["wood"])
            for u in np.linspace(mid-w,mid+w,9)[1:-1]:
                trim(u-.013,v+.062,z+1.8,u+.013,v+.105,z+2.14,m["wood"])
            if i%2==int(rear):
                # Folding pair held against the jamb, with raised panels and paired iron hinges.
                side=mid-w
                x0,x1=side,side+.4
                trim(x0,outer-.035,z+h+.06,x1,outer+.035,z+1.76,m["wood"])
                for k in (h+.19,1.48):
                    trim(x0-.01,outer-.05,z+k,x1+.013,outer+.05,z+k+.044,m["iron"])
        # Wall plate, rafter tails and a shallow overdoor above the rear threshold.
        trim(-p["width"]/2,outer-.055,z+2.67,p["width"]/2,outer+.055,z+2.82,m["wood"])
        if rear:
            for u in np.linspace(-2.25,2.25,7):
                trim(u-.044,d-.10,z+2.51,u+.044,d+.85,z+2.59,m["wood"])
            verts=[(-2.35,d-.02,z+2.91),(2.35,d-.02,z+2.91),(2.35,d+.94,z+2.65),(-2.35,d+.94,z+2.65)]
            panel(verts,m["tile"])
            panel(verts[::-1],m["wood"])


def tiled_roof(batch,ring,eave,rise,m):
    a,b,c,d=np.array(ring,dtype=float)
    left,right=(a+d)/2,(b+c)/2
    def patch(x,y,z,w,h1,h2,mat):
        pts=[(*x,h1),(*y,h1),(*z,h2),(*w,h2)]
        batch.face(pts,mat)
        batch.face(pts[::-1],mat)
    for lo,hi in ((a,b),(d,c)):
        patch(lo,hi,right,left,eave,eave+rise,m["tile"])
        # Three dimensional fascia, battens just under the eaves and a ridge cap.
        patch(lo,hi,hi,lo,eave-.14,eave,m["wood"])
        patch(.96*left+.04*lo,.96*right+.04*hi,right,left,eave+rise-.008,eave+rise+.075,m["tile"])
    for edge,peak in (((a,d),left),((c,b),right)):
        triangle=[(*edge[0],eave),(*edge[1],eave),(*peak,eave+rise)]
        batch.face(triangle,m["lime"])
        batch.face(triangle[::-1],m["lime"])


def grade(p,site,xx,yy,heights,mx,my,rgba):
    def footprint(x,y):
        u,v=local(p,x,y)
        # Front row, its two thresholds and the enclosing courtyard. Feather at the plot edge.
        f=p["depth"]/2
        return np.minimum(np.maximum.reduce([abs(u)-p["width"]/2-.3,-f-2.8-v,v-f-.6]),
                          np.maximum.reduce([abs(u)-10.9,f-.8-v,v-21.3]))
    sx,toe=local(p,*site["street_en"])
    f=p["depth"]/2
    u,v=local(p,xx,yy)
    # Cut the full stair bedding and its shoulder on the uphill side of every tread.
    street_z=p["street_grade"]
    t=np.clip((v-toe)/(-f-2.36-toe),0,1)
    profile=street_z+(p["height"]-street_z)*t
    dist=np.maximum.reduce([abs(u)-2.15,toe+.68-v,v+f+1.8])
    blend=np.clip(1-np.maximum(dist,0)/1.25,0,1)
    heights-=np.maximum(0,heights-(profile-.22))*blend
    weight=np.clip(1-np.maximum(footprint(xx,yy),0)/1.65,0,1)
    heights-=np.maximum(0,heights-(p["height"]-.18))*weight
    u,v=local(p,mx,my)
    approach=np.maximum.reduce([abs(u)-3.15,toe-1.1-v,v+f])
    pavement=np.minimum(footprint(mx,my),approach)
    rgba[:,:,1]=np.maximum(rgba[:,:,1],np.clip(1.1-pavement,0,1))


def outside(p,site,frame,ground,box,body,detail,m):
    z=p["height"]
    f=p["depth"]/2
    sx,sy=local(p,*site["street_en"])
    cx,cy=local(p,*site["court_en"])
    street_z=p["street_grade"]+.042
    def block(u,v,h,x,y,k,mat,batch=body):
        box(batch,frame,u,v,h,x,y,k,m[mat])
    def pave(u0,v0,u1,v1,level):
        block(u0,v0,level-.35,u1,v1,level-.025,"wallstone")
        length=1.06
        for row in range(ceil((v1-v0)/.53)):
            v=v0+row*.53
            for i in range(-1,ceil((u1-u0)/length)+1):
                u=u0+i*length+(row%2)*.53
                a,b=max(u0,u+.005),min(u1,u+length-.005)
                if b-a>.02:
                    block(a,v+.005,level-.027,b,min(v1,v+.525),level,"sillstone" if (i+2*row)%5 else "weathered_flag",detail)
    # Each flag has a visible joint. A continuous stone bed carries the actor.
    pave(-p["width"]/2,-f-2.36,p["width"]/2,-f+.02,z+.027)
    pave(-9.9,f-.03,10.1,18.55,z+.030)
    # Stone lane between the existing public footway and the workshop apron.
    # The toe is on the digitized pedestrian way; the flight ends before the motor road.
    toe=min(sy,-f-3.1)
    end=-f-2.36
    count=max(1,ceil(abs(z+.026-street_z)/.14))
    for i in range(count):
        lo=toe+(end-toe)*i/count
        hi=toe+(end-toe)*(i+1)/count
        h=street_z+(z+.026-street_z)*(i+1)/count
        block(-1.66,lo,min(ground(-1.66,lo),ground(1.66,hi),h-.20)-.22,1.66,hi,h,"sillstone")
    # Follow the mapped footway bend. A narrow continuous bed supports the timber boards.
    walk=np.array([local(p,*q) for q in site["boardwalk_en"]])
    for a,b in zip(walk,walk[1:]):
        direct=b-a
        length=np.linalg.norm(direct)
        normal=np.array([-direct[1],direct[0]])/length
        count_along=ceil(length/.77)
        for j in range(count_along):
            l=a+direct*j/count_along
            r=a+direct*(j+1)/count_along
            if np.linalg.norm((l+r)*.5-[sx,sy])>19.5:
                continue
            def board_point(at,offset,h):
                u,v=at+normal*offset
                return frame(u,v,ground(u,v)+h)
            uv=[(l,-1.05),(r,-1.05),(r,1.05),(l,1.05)]
            underside=[board_point(q,offset,.036) for q,offset in uv]
            body.face(underside,m["wood"])
            body.face(underside[::-1],m["wood"])
            # Limit the outer balustrade to the boardwalk, along the river-facing
            # edge. There is no rail across the workshop throat or on its stone flight.
            def rail_piece(start,finish,y0,y1,h0,h1,material,batch):
                pts=[board_point(q,off,h) for h in (h0,h1) for q,off in
                     ((start,y0),(finish,y0),(finish,y1),(start,y1))]
                for ix in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
                    batch.face([pts[i] for i in ix],m[material])
            rail_piece(l,r,-1.09,-.98,.96,1.055,"wood",body)
            rail_piece(l,r,-1.07,-1.005,.16,.24,"wood",body)
            if j%2==0:
                rail_piece(l,l+(r-l)*.15,-1.105,-.957,.02,1.13,"wood",body)
            for t in (.16,.42,.68,.94):
                rail_piece(l+t*(r-l),l+(t+.042)*(r-l),-1.06,-1.018,.20,.98,"iron",detail)
            for k in range(14):
                x=-1.05+k*.15
                face=[board_point(q,off,.044) for q,off in ((l,x+.004),(r,x+.004),(r,x+.147),(l,x+.147))]
                detail.face(face,m["wood"],[(j*.77/2,k*.15),(j*.77/2+.38,k*.15),(j*.77/2+.38,k*.15+.14),(j*.77/2,k*.15+.14)])
    tu,tv=local(p,*site["tree_en"])
    # Stone surround with a soil opening at the mapped courtyard tree.
    for j in range(12):
        a,b=j*np.pi/6,(j+1)*np.pi/6
        ring=[frame(tu+r*cos(t),tv+r*sin(t),z+h) for r,t,h in
              ((.62,a,.104),(.88,a,.104),(.88,b,.104),(.62,b,.104))]
        body.face(ring,m["flags"])
        detail.face([frame(tu,tv,z+.082),frame(tu+.64*cos(a),tv+.64*sin(a),z+.082),
                     frame(tu+.64*cos(b),tv+.64*sin(b),z+.082)],m["wallstone"])
    # A stone drain follows the uphill side of the lane, with cut slots and
    # butt joints; its outer kerb is entirely on the pedestrian approach.
    for i in range(count):
        v0=toe+(end-toe)*i/count
        v1=toe+(end-toe)*(i+1)/count
        h=street_z+(z+.026-street_z)*(i+1)/count
        block(1.67,v0,h-.19,1.98,v1,h-.03,"wallstone")
        block(1.93,v0,h-.14,2.04,v1,h+.08,"flags")
        for k in range(3):
            v=v0+(v1-v0)*(k+.12)/3
            block(1.69,v,h-.04,1.926,min(v+.14,v1),h+.001,"iron",detail)
    for key in ("upper","west_return","east_return"):
        ring=np.array(site["roof_rings"][key]["en"])
        # Use the long axis for the ridge; verandas open towards the middle.
        if key!="upper":
            ring=ring[[1,2,3,0]] if key=="west_return" else ring[[3,0,1,2]]
        a,b,c,d=ring
        def at(t,v,h):
            xy=(1-v)*((1-t)*a+t*b)+v*((1-t)*d+t*c)
            return (*xy,h)
        def prism(t0,t1,v0,v1,h0,h1,mat,batch=body):
            pts=[at(t,v,h) for h in (h0,h1) for t,v in ((t0,v0),(t1,v0),(t1,v1),(t0,v1))]
            for ix in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
                batch.face([pts[i] for i in ix],m[mat])
        length=np.linalg.norm(b-a)
        bays=max(2,round(length/3.15))
        prism(0,1,0,1,z-.58,z+.09,"wallstone")
        for j in range(bays+1):
            t=j/bays
            prism(max(0,t-.095/length),min(1,t+.095/length),.035,.095,z+.09,z+2.84,"wood")
        prism(0,1,.027,.105,z+2.62,z+2.85,"wood")
        prism(0,1,.93,1,z+.08,z+.61,"wallstone")
        for j in range(bays):
            t0,t1=j/bays,(j+1)/bays
            prism(t0,t0+.31/bays,.93,1,z+.61,z+2.70,"lime")
            prism(t0+.76/bays,t1,.93,1,z+.61,z+2.70,"lime")
            prism(t0+.31/bays,t0+.76/bays,.93,1,z+.61,z+1.04,"lime")
            prism(t0+.31/bays,t0+.76/bays,.93,1,z+2.16,z+2.70,"lime")
            for s in (.32,.54,.75):
                prism(t0+s/bays,t0+(s+.018)/bays,.946,.968,z+1.03,z+2.17,"wood",detail)
            prism(t0+.31/bays,t0+.76/bays,.944,.974,z+1.84,z+1.90,"wood",detail)
            prism(t0+.06/bays,t0+.1/bays,.04,.965,z+2.60,z+2.78,"wood")
        tiled_roof(detail,ring,z+2.90,1.02,m)
    p["front_stair_m"]=abs(toe+f)
    p["back_stair_m"]=0.0
    def pos(u,v,h):return [round(q,4) for q in frame(u,v,h)]
    p["repair_court"]={"street":pos(sx,sy,street_z),"toe":pos(0,toe,street_z),
        "porch":pos(0,-f-1.1,z+.05),"service":pos(0,-.74,z+.05),
        "valve":pos(1.2,-.74,z+.88),"bike":pos(3.8,-f-1.5,z+.07),
        "rear":pos(0,f+.66,z+.05),"court":pos(cx,cy,z+.05),"risers":count,
        "rise_m":round((z+.026-street_z)/count,3),"going_m":round((end-toe)/count,3)}
