"""Surveyed courts, timber galleries and shared paved access on the outer slopes."""
from math import cos,sin,hypot,ceil,pi
import numpy as np


def world(p,u,v):
    x,y=p["east_north"];c,s=cos(p["bearing"]),sin(p["bearing"])
    return x+c*u-s*v,y+s*u+c*v


def local(p,x,y):
    ox,oy=p["east_north"];c,s=cos(p["bearing"]),sin(p["bearing"])
    return (x-ox)*c+(y-oy)*s,-(x-ox)*s+(y-oy)*c


def select_courts(plots,patch,roads):
    selected=[]
    for i,p in enumerate(plots):
        if not p["name"] and (len(selected)>=11 or p["width"]<14 or p["plot_id"]%4!=0):
            continue
        width=min(8.75,p["width"]/2-.28)
        # The workshop's uphill neighbour takes the north-west corner.
        center=4.8 if p["name"].endswith("修理铺") else 0.0
        if center: width=7.2
        rear=p["depth"]/2
        samples=[world(p,center+u,rear+v) for u in (-width,0,width) for v in (1,5,9,13)]
        if any(not patch(x,y) or max(abs(x),abs(y))>245 or roads(x,y)[0]<roads(x,y)[1]+1.7 for x,y in samples):
            continue
        def overlaps(other):
            for x,y in samples:
                u,v=local(other,x,y)
                if abs(u)<other["width"]/2+1.4 and abs(v)<other["depth"]/2+1.4:
                    return True
            return False
        if any(overlaps(q) for q in plots if q is not p):
            continue
        p["court"]={"half_width":width,"center_u":center,"stair_side":1 if p["name"].endswith("茶摊") or (not p["name"] and i%3) else -1}
        selected.append(p)
    return selected


def terrace_ground(p,xx,yy,levels):
    u,v=local(p,xx,yy)
    u=u-p["court"]["center_u"]
    rear=p["depth"]/2
    outside=np.maximum.reduce([np.abs(u)-p["court"]["half_width"]-.35,rear-.3-v,v-rear-13.05,np.zeros_like(xx)])
    weight=np.clip(1-outside/1.85,0,1)
    levels[:]-=np.maximum(0,levels-(p["height"]-.22))*weight


def build_court(p,box,face,ground,c):
    d=p["depth"]/2; z=p["height"]; k=p["court"]["stair_side"]; w=p["court"]["half_width"]
    center=p["court"]["center_u"]
    def block(x0,v0,h0,x1,v1,h1,material,physical=True):
        a,b=sorted((k*x0,k*x1))
        box(center+a,d+v0,z+h0,center+b,d+v1,z+h1,c[material],physical)
    def skin(points,key):
        verts=[(center+k*x,d+v,z+h) for x,v,h in points]
        face(verts if k>0 else verts[::-1],c[key])
    # Paving, foundations and side retaining faces are bounded by the same slab.
    foot=min(ground(center+k*x,d+v)-z for x in (-w,0,w) for v in (.1,6,12.8))-.32
    block(-w,0,foot,w,12.85,.065,"wallstone")
    block(-w,.02,.065,w,12.83,.09,"flags")
    # On the low side a short wall leaves the corner open to the connecting alley.
    block(-w,3.8,.09,-w+.27,8.64,.81,"wallstone")
    block(-w-.035,3.8,.81,-w+.30,8.64,.89,"flags")
    # Each tread meets its neighbour at the riser. The masonry follows the flight.
    stair_x=w-1.38; count=18; tread=.306; start=1.16; end=start+count*tread
    for i in range(count):
        a=start+i*tread
        block(stair_x-.87,a,.09,stair_x+.87,a+tread,.09+(i+1)*.157,"flags")
    floor=.09+count*.157
    front=end+1.74
    block(-w+.28,end,floor-.19,w-.22,front+.09,floor,"wood")
    for x in (-w+.48,-1.75,2.25,w-.48):
        block(x-.085,end+.13,.09,x+.085,end+.30,floor-.18,"wood")
    # The balcony rail ends at the stair opening.
    block(-w+.37,end+.10,floor+.87,stair_x-1.02,end+.18,floor+.95,"wood")
    for i in range(max(1,int((stair_x+w-1.45)/.38))):
        x=-w+.52+i*.38
        block(x-.025,end+.12,floor,x+.025,end+.17,floor+.90,"wood")
    leaf="brick" if p["name"].endswith("茶摊") or p["kind"]==1 else "lime"
    # Two joined homes with different roof heights. Doors and recessed windows
    # are true openings. Each family's balcony shares the stair and landing.
    for i,(lo,hi) in enumerate(((-w+.28,.3),(.3,w-.22))):
        mid=lo+(hi-lo)*(.36 if i==0 else .64)
        head=floor+2.48+(i*.20)
        for h in (.09,floor):
            # Cut the family's front window on the wider masonry return.
            for a,b in ((lo,mid-.56),(mid+.56,hi)):
                if b-a<1.75:
                    block(a,front,h,b,front+.21,h+2.32,leaf)
                    continue
                wx=(a+b)/2; span=min(1.06,(b-a)*.34)
                block(a,front,h,b,front+.21,h+.88,leaf)
                block(a,front,h+.88,wx-span,front+.21,h+2.32,leaf)
                block(wx+span,front,h+.88,b,front+.21,h+2.32,leaf)
                block(wx-span,front,h+1.92,wx+span,front+.21,h+2.32,leaf)
                block(wx-span-.085,front-.14,h+.84,wx+span+.085,front+.06,h+.92,"flags")
                for frame_x in (wx-span,wx,wx+span):
                    block(frame_x-.034,front+.065,h+.92,frame_x+.034,front+.14,h+1.93,"wood",False)
                block(wx-span,front+.065,h+1.60,wx+span,front+.14,h+1.65,"wood",False)
                # Open half-shutter sits proud of the return rather than filling the opening.
                block(wx+span+.035,front-.08,h+.93,min(b,wx+span+.48),front-.01,h+1.90,"wood",False)
                for j in range(4):
                    block(wx+span+.04,front-.105,h+1.05+j*.18,min(b,wx+span+.44),front-.078,h+1.08+j*.18,"iron",False)
                block(a,front-.015,h+.02,b,front+.006,h+.35,"wallstone",False)
            block(mid-.56,front,h+2.08,mid+.56,front+.21,h+2.32,"wood")
            # Open door leaf is hinged flat against the interior return.
            block(mid-.55,front+.22,h+.04,mid-.48,front+.98,h+2.03,"wood")
            block(lo,12.57,h,hi,12.83,h+.86,leaf)
            window=(hi+lo)/2+.40; edge_l=window-.92; edge_r=window+.92
            block(lo,12.57,h+.86,edge_l,12.83,h+2.30,leaf)
            block(edge_r,12.57,h+.86,hi,12.83,h+2.30,leaf)
            block(edge_l,12.57,h+1.93,edge_r,12.83,h+2.30,leaf)
            for t in (.25,.50,.75):
                x=edge_l+(edge_r-edge_l)*t
                block(x-.023,12.62,h+.86,x+.023,12.69,h+1.93,"wood",False)
            block(edge_l-.06,12.42,h+.82,edge_r+.06,12.64,h+.89,"wood",False)
            block(lo,front+.20,h,lo+.19,12.58,h+2.32,leaf)
        block(lo,front,.09+2.32,hi,12.81,floor,"lime")
        block(lo,front,floor+2.30,hi,12.83,head,"lime")
        block(lo,front,head-.04,hi,front+.20,head+.35,"wood")
        for px in (lo+.24,hi-.24):
            block(px-.07,end+.12,floor,px+.07,end+.27,head,"wood")
            skin([(px,end+.16,head-.55),(px,end+.80,head+.10),(px,end+.16,head+.03)],"wood")
        # The pitched tiled overhang covers the usable gallery outside the doors.
        ridge=10.43
        for a,b,za,zb in ((end-.28,ridge,head,head+.86),(ridge,13.1,head+.86,head+.12)):
            poly=[(lo-.12,a,za),(hi+.12,a,za),(hi+.12,b,zb),(lo-.12,b,zb)]
            skin(poly,"tile");skin(poly[::-1],"tile")
            for x in (lo,hi):
                gable=[(x,a,head-.05),(x,b,head-.05),(x,b,zb),(x,a,za)]
                skin(gable,"wood");skin(gable[::-1],"wood")
            for j in range(1,round((hi-lo)/.25)):
                x=lo+j*.25
                skin([(x-.039,a,za+.01),(x,a,za+.044),(x,b,zb+.044),(x-.039,b,zb+.01)],"tile")
        block(lo-.12,end-.28,head-.12,hi+.12,end+.17,head,"wood",False)
        # Interior platform bed, quilt and small table are set away from the threshold.
        bedx=hi-2.12
        block(bedx,10.55,floor+.16,hi-.26,12.28,floor+.45,"wood")
        block(bedx+.03,10.58,floor+.45,hi-.29,12.26,floor+.54,"cloth",False)
        block(bedx+.12,11.85,floor+.54,hi-.46,12.19,floor+.65,"linen",False)
        block(hi-.37,10.54,floor+.39,hi-.23,12.29,floor+.78,"wood",False)
        block(bedx-.61,11.65,floor+.03,bedx-.09,12.22,floor+.56,"wood")
        for j in range(2):
            block(bedx-.55,11.624,floor+.17+j*.22,bedx-.17,11.65,floor+.32+j*.22,"wood",False)
            block(bedx-.40,11.60,floor+.22+j*.22,bedx-.32,11.624,floor+.25+j*.22,"zinc",False)
        block(lo+.35,10.91,floor+.06,lo+1.02,12.23,floor+1.78,"wood")
        block(lo+1.021,10.94,floor+.14,lo+1.045,11.54,floor+1.69,"wood",False)
        for ipeg in (11.49,11.65):
            block(lo+1.04,ipeg,floor+.89,lo+1.08,ipeg+.039,floor+1.03,"zinc",False)
        if i==0:
            p["court"].update({"room_u":center+k*mid,"stair_u":center+k*stair_x,
                "stair_v":d+start,"landing_v":d+end+.84,"room_v":d+front+1.02,"upper_m":floor,
                "bed_local":[center+k*(bedx+.7),d+11.52],"other_room_u":center+k*(.3+(w-.22-.3)*.64)})
    block(w-.4,front,.09,w-.22,12.81,floor+2.50,leaf)
    # One household shares the gallery for washing. The rod brackets enter
    # the wall, and both folded cloths hang from the same supported rail.
    rod0,rod1=-w+1.04,-w+4.08
    for x in (rod0,rod1):
        block(x-.027,front-.62,floor+1.97,x+.027,front+.10,floor+2.025,"iron",False)
    block(rod0,front-.63,floor+1.99,rod1,front-.58,floor+2.04,"iron",False)
    for j,(x,span,drop,tex) in enumerate(((rod0+.21,.72,.79,"cloth"),(rod0+1.35,.55,.65,"linen"))):
        for n in range(9):
            a=x+n*span/9;b=x+(n+1)*span/9
            va=front-.63+.044*cos(n*pi/2);vb=front-.63+.044*cos((n+1)*pi/2)
            poly=[(a,va,floor+2.04),(a,va-.055,floor+2.04-drop+.036*cos(n)),
                  (b,vb-.055,floor+2.04-drop+.036*cos(n+1)),(b,vb,floor+2.04)]
            skin(poly,tex);skin(poly[::-1],tex)
        for peg in (x+.05,x+span-.05):
            block(peg-.016,front-.65,floor+1.98,peg+.016,front-.59,floor+2.075,"wood",False)
    # A masonry wash trough occupies the wall opposite the stairs.
    block(-w+.38,5.05,.09,-w+1.00,6.29,.68,"wallstone")
    for a,b in ((5.05,5.14),(6.20,6.29)):
        block(-w+.38,a,.68,-w+1.00,b,.91,"stone")
    for x in (-w+.38,-w+.92):
        block(x,5.14,.68,x+.08,6.20,.90,"stone")
    # Side exit from the court follows measured downhill grade.
    edge=-w; v=2.08
    for n in range(1,33):
        run=n*.33
        low=ground(center+k*(edge-run),d+v)-z
        if .09-low<=n*.16:break
    for i in range(n):
        level=.09-max(.09-low,0)*i/n
        block(edge-(i+1)*.33,v-.91,min(foot,level-.19),edge-i*.33,v+.91,level,"flags")
    p["court"]["exit_local"]=[center+k*(edge-run),d+v]


def connect_lanes(plots,segments,patch,road_distance,mask_x,mask_y,rgba):
    # The texture mask lives on the physical terrain triangles. Visible stone
    # follows their elevation even where a connector crosses a former tile seam.
    def visible_walk(a,b,half):
        delta=np.subtract(b,a)
        scale=float(delta@delta)
        if scale<.1:return
        xs=np.where((mask_x[0]>=min(a[0],b[0])-half-1)&(mask_x[0]<=max(a[0],b[0])+half+1))[0]
        ys=np.where((mask_y[:,0]>=min(a[1],b[1])-half-1)&(mask_y[:,0]<=max(a[1],b[1])+half+1))[0]
        if not len(xs) or not len(ys):return
        sl=np.s_[ys[0]:ys[-1]+1,xs[0]:xs[-1]+1]
        x,y=mask_x[sl],mask_y[sl]
        f=np.clip(((x-a[0])*delta[0]+(y-a[1])*delta[1])/scale,0,1)
        amount=np.clip((half-np.hypot(x-a[0]-f*delta[0],y-a[1]-f*delta[1]))*2+.5,0,1)
        rgba[sl+(1,)]=np.maximum(rgba[sl+(1,)],amount*(np.maximum(abs(x),abs(y))>101))
    def clear(a,b,avoid_roads):
        length=hypot(b[0]-a[0],b[1]-a[1])
        for f in np.linspace(0,1,max(3,int(length/1.0))):
            x,y=a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f
            if not patch(x,y) or max(abs(x),abs(y))<102:return False
            if avoid_roads and road_distance(x,y)[0]<road_distance(x,y)[1]+.9:return False
            for p in plots:
                u,v=local(p,x,y)
                if abs(u)<p["width"]/2+.18 and -p["depth"]/2-.18<v<p["depth"]/2+.18:return False
                if p.get("court") and abs(u-p["court"]["center_u"])<p["court"]["half_width"]+.18 and p["depth"]/2<v<p["depth"]/2+12.90:return False
        return True
    points=[];paths=[]
    for i,p in enumerate(plots):
        f=-p["depth"]/2
        u=p["door_u"]
        front=world(p,u if not p["name"] else -.27*p["width"],f-p.get("front_stair_m",8.7)-.18)
        back=world(p,*p["court"]["exit_local"]) if p.get("court") else world(p,u,-f+p["back_stair_m"]+.21)
        points.extend([(i,front),(i,back)])
        candidates=[]
        for a,b,w,_ in segments:
            ab=b-a;t=float(np.clip((np.asarray(front)-a)@ab/(ab@ab),0,1))
            center=a+t*ab;v=np.asarray(front)-center;l=float(np.linalg.norm(v))
            if l>.1:candidates.append((abs(l-w-1),tuple(center+v/l*(w+.8))))
        for dist,q in sorted(candidates)[:9]:
            if dist<36 and clear(front,q,False):
                visible_walk(front,q,1.03);paths.append({"type":"street","plots":[i],"points":[front,q]});break
    edges=[]
    for a,(i,p) in enumerate(points):
        for b,(j,q) in enumerate(points[:a]):
            length=hypot(p[0]-q[0],p[1]-q[1])
            if i!=j and 1.7<length<34:edges.append((length,a,b))
    degree={};seen=set()
    for _,a,b in sorted(edges):
        i,p=points[a];j,q=points[b];pair=tuple(sorted((i,j)))
        if pair in seen or degree.get(a,0)>=2 or degree.get(b,0)>=2 or not clear(p,q,True):continue
        seen.add(pair);degree[a]=degree.get(a,0)+1;degree[b]=degree.get(b,0)+1
        visible_walk(p,q,.94);paths.append({"type":"shared","plots":[i,j],"points":[p,q]})
    return paths
