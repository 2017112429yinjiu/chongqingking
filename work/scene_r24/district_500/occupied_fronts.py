"""Outer walk-up elevations. All dimensions and joints follow the existing structural bays."""
from math import cos, sin, pi, hypot
from mathutils import Vector


def tube(face, a, b, radius, mat, sides=8):
    start, end = Vector(a), Vector(b)
    axis = (end-start).normalized()
    ref = Vector((0, 1, 0)) if abs(axis.y) < .9 else Vector((1, 0, 0))
    u = axis.cross(ref).normalized()*radius
    v = axis.cross(u)
    ring = [u*cos(i*2*pi/sides)+v*sin(i*2*pi/sides) for i in range(sides)]
    for j, q in enumerate(ring):
        n = ring[(j+1)%sides]
        face([tuple(start+q),tuple(start+n),tuple(end+n),tuple(end+q)],mat)


def upper_storey(p, level, z, top, draw, box, face, wall, m):
    """Cut the shell between columns before installing the masonry reveals and joinery."""
    half_w,half_d=p["width"]/2,p["depth"]/2
    for side in range(4):
        along_x=side<2
        sign=(-1,1,1,-1)[side]
        # t runs along the facade. q is positive out of the building.
        def point(t,q,h):
            return (t,sign*(half_d+q),h) if along_x else (sign*(half_w+q),t,h)
        def rect(t0,q0,h0,t1,q1,h1,mat,structural=False):
            a,b=point(t0,q0,h0),point(t1,q1,h1)
            (draw if structural else box)(*map(min,zip(a,b)),*map(max,zip(a,b)),mat)
        def surface(points,mat):
            face([point(*pt) for pt in points],mat)
        axes=p["frame"]["u" if along_x else "v"]
        extent=half_w if along_x else half_d-.19
        cursor=-extent
        for index,(lo,hi) in enumerate(zip(axes,axes[1:])):
            span=hi-lo
            if span<2.15 or (not along_x and (index+level+p["plot_id"])%3!=0):
                continue
            seed=p["plot_id"]+index*3+side
            mid=(lo+hi)*.5
            width=min(span-.76,2.24 if along_x else 1.28)
            a,b=mid-width/2,mid+width/2
            choice=(p["plot_id"]+1)%(len(axes)-1)
            bay=side==0 and span>=2.28 and (index==choice or (index==len(axes)-2 and index!=choice))
            gallery=bay and (index==choice or seed%2==0)
            sill=z+(.16 if gallery else .83)
            head=z+2.19
            rect(cursor,-.19,z,a,0,top,wall,True)
            rect(a,-.19,z,b,0,sill,wall,True)
            rect(a,-.19,head,b,0,top,wall,True)
            cursor=b
            mat=m["wood"] if (seed%4==0 or (p["kind"]==0 and side!=0)) else m["trim"]
            # Deep jambs and sill have exposed returns, bottom drip and a sloped nose.
            rect(a-.075,-.22,sill-.035,b+.075,.16,sill+.032,m["stone"])
            rect(a-.055,.095,sill-.081,b+.055,.156,sill-.035,m["stone"])
            for x in (a+.028,b-.028,mid):
                rect(x-.026,-.145,sill+.032,x+.026,-.079,head,mat)
            for h in (sill+.055,head-.30,head-.035):
                rect(a,-.145,h-.020,b,-.079,h+.020,mat)
            # Recessed glass stops at the masonry reveal, with an actual ventilating
            # opening on selected bays. The open casement rotates about its outer hinge.
            tint=m["panes"][(seed+level)%len(m["panes"])]
            rect(a+.05,-.157,head-.274,b-.05,-.147,head-.054,tint)
            rect(a+.05,-.157,sill+.079,mid-.025,-.147,head-.328,tint)
            if (seed+level)%4==0:
                wing=b-mid-.075; tip=b-.055-wing*.81; out=-.10+wing*.58
                corners=[(b-.055,-.10,sill+.082),(tip,out,sill+.082),
                         (tip,out,head-.33),(b-.055,-.10,head-.33)]
                surface(corners,tint); surface(corners[::-1],tint)
                for v,w in zip(corners,corners[1:]+corners[:1]):
                    tube(face,point(*v),point(*w),.022,mat,6)
            else:
                rect(mid+.028,-.157,sill+.079,b-.052,-.147,head-.328,tint)
            if bay:
                # Cast concrete with splayed cheeks and a rebated lower edge.
                reach=1.06 if gallery else .56
                outline=[(a-.19,-.02),(b+.19,-.02),(b+.19,reach-.17),
                         (b+.02,reach),(a-.02,reach),(a-.19,reach-.17)]
                base=z+.11 if gallery else sill-.14
                for v,w in zip(outline,outline[1:]+outline[:1]):
                    surface([(v[0],v[1],base),(w[0],w[1],base),(w[0],w[1],base+.12),(v[0],v[1],base+.12)],m["stone"])
                for h in (base,base+.12):
                    pts=[(x,q,h) for x,q in outline]
                    surface(pts,m["stone"]);surface(pts[::-1],m["stone"])
                for i,(v,w) in enumerate(zip(outline[1:],outline[2:]+outline[:1])):
                    if gallery:
                        bottom,cap=base+.12,base+1.03
                        tube(face,point(*v,cap),point(*w,cap),.025,m["iron"])
                        n=max(1,round(hypot(v[0]-w[0],v[1]-w[1])/.22))
                        for j in range(n):
                            t=j/n; x=v[0]+(w[0]-v[0])*t; q=v[1]+(w[1]-v[1])*t
                            rect(x-.014,q-.014,bottom,x+.014,q+.014,cap,m["iron"])
                    else:
                        # Flower ledge with a breeze-block front, drainage gaps and end returns.
                        for h in (base+.145,base+.36):
                            tube(face,point(*v,h),point(*w,h),.035,m["trim"],6)
                        if i==2:
                            for j in range(max(2,int(width/.31))):
                                x=a+.12+j*.31
                                rect(x,.50,base+.15,x+.055,.56,base+.36,m["trim"])
                if gallery and index==choice:
                    # A resident-enclosed verandah cuts two corners back and projects a rain hood.
                    for v,w in zip(outline[1:],outline[2:]+outline[:1]):
                        for h0,h1,key in ((base+.16,base+.64,"jade"),(base+.68,base+1.92,"pane"),(base+1.97,base+2.21,"pane")):
                            material=m["glass"] if key=="pane" else m[key]
                            quad=[(v[0],v[1],h0),(w[0],w[1],h0),(w[0],w[1],h1),(v[0],v[1],h1)]
                            surface(quad,material);surface(quad[::-1],material)
                        for h in (base+.64,base+1.94,base+2.23):
                            tube(face,point(*v,h),point(*w,h),.026,mat,6)
                        tube(face,point(*v,base+.14),point(*v,base+2.23),.027,mat,6)
                        if hypot(v[0]-w[0],v[1]-w[1])>.9:
                            t,q=(v[0]+w[0])*.5,(v[1]+w[1])*.5
                            rect(t-.019,q-.02,base+.14,t+.019,q+.02,base+2.23,mat)
                    rod=reach-.14
                    tube(face,point(a+.04,rod,base+1.82),point(b-.04,rod,base+1.82),.015,m["metal"])
                    for j in range(11):
                        x0=a+.11+j*.049;x1=x0+.049
                        q0=rod+.032*cos(j*1.23);q1=rod+.032*cos((j+1)*1.23)
                        surface([(x0,q0,base+1.82),(x0,q0+.013,base+1.04),(x1,q1+.013,base+1.04+.024*cos(j)),(x1,q1,base+1.82)],m["cotton"])
                    hood=[(t,q+.055 if q>0 else q,base+2.34-.095*max(0,q)) for t,q in outline]
                    surface(hood,m["metal"]);surface(hood[::-1],m["metal"])
                    p["facade_work"]["enclosed_galleries"]+=1
                p["facade_work"]["clipped_balconies"]+=1
            p["facade_work"]["windows"]+=1
        rect(cursor,-.19,z,extent,0,top,wall,True)


def rainwater(p, box, face, m):
    w,d,z,top=p["width"],p["depth"],p["height"],p["roof"]
    edge=-d/2; x=(w/2-.37) * (1 if p["plot_id"]%2 else -1)
    y=edge-.16
    pitched=p["floors"]<=3 and p["kind"]!=2
    intake=edge-(.44 if pitched else .23)
    rim=top+(.16 if pitched else .25)
    if pitched:
        # Open half-round eaves trough, under the sloped tile drip.
        for j in range(6):
            aa,bb=pi+j*pi/6,pi+(j+1)*pi/6
            qa,ha=intake+.083*cos(aa),rim+.083*sin(aa)
            qb,hb=intake+.083*cos(bb),rim+.083*sin(bb)
            face([(-w/2-.34,qa,ha),(w/2+.34,qa,ha),(w/2+.34,qb,hb),(-w/2-.34,qb,hb)],m["metal"])
    else:
        box(x-.13,edge-.27,top+.17,x+.13,edge+.23,top+.33,m["metal"])
    path=[(x,intake,rim-.045),(x,intake,rim-.32),(x,y,rim-.56),
          (x,y,z+.29),(x,y-.12,z+.15),(x,y-.21,z+.15)]
    for a,b in zip(path,path[1:]): tube(face,a,b,.061,m["metal"])
    for i in range(p["floors"]):
        h=z+.85+i*2.95
        tube(face,(x,y,h),(x,y,h+.055),.072,m["iron"])
        box(x-.031,y,h+.015,x+.031,edge+.02,h+.042,m["iron"])
    if not pitched:
        # Ribbed domestic tank with a domed lid, supply line and bearing feet.
        cx,cy=w/6+.79,.05; bot=top+.41
        for dx in (-.40,.40):
            box(cx+dx-.052,cy-.43,top+.17,cx+dx+.052,cy+.43,bot,m["iron"])
        rings=[(0,.46),(.08,.56),(.14,.58),(.23,.55),(.88,.55),(.94,.58),(1,.54),(1.10,.39),(1.14,.13)]
        for (ha,ra),(hb,rb) in zip(rings,rings[1:]):
            for i in range(16):
                a,b=i*pi/8,(i+1)*pi/8
                face([(cx+ra*cos(a),cy+ra*sin(a),bot+ha),(cx+ra*cos(b),cy+ra*sin(b),bot+ha),
                      (cx+rb*cos(b),cy+rb*sin(b),bot+hb),(cx+rb*cos(a),cy+rb*sin(a),bot+hb)],m["metal"])
        face([(cx+.13*cos(i*pi/8),cy+.13*sin(i*pi/8),bot+1.14) for i in range(16)],m["iron"])
        tube(face,(cx+.54,cy,bot+.19),(cx+.75,cy,bot+.19),.035,m["metal"])
        tube(face,(cx+.75,cy,bot+.19),(cx+.75,cy,top+.14),.035,m["metal"])
