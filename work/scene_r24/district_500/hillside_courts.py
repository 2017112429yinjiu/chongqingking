"""Surveyed courts, timber galleries and shared paved access on the outer slopes."""
from math import cos,sin,hypot,ceil,pi
import numpy as np
from pathlib import Path
from runpy import run_path
sleep_room=run_path(str(Path(__file__).with_name('house_finishes.py')))['sleep_room']


def world(p,u,v):
    x,y=p["east_north"];c,s=cos(p["bearing"]),sin(p["bearing"])
    return x+c*u-s*v,y+s*u+c*v


def local(p,x,y):
    ox,oy=p["east_north"];c,s=cos(p["bearing"]),sin(p["bearing"])
    return (x-ox)*c+(y-oy)*s,-(x-ox)*s+(y-oy)*c


def select_courts(plots,patch,roads):
    selected=[]
    # Preserve the established upper landings when other plots leave the prototype.
    stair_sides={0:-1,1:-1,2:1,8:1,40:1,48:-1,52:1,56:1,60:-1,64:1,72:-1}
    for p in plots:
        if p["plot_id"] not in stair_sides:
            continue
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
        p["court"]={"half_width":width,"center_u":center,"stair_side":stair_sides[p["plot_id"]]}
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
    def skin(points,key,uvs=None):
        verts=[(center+k*x,d+v,z+h) for x,v,h in points]
        mat=c[key] if isinstance(key,str) else key
        face(verts if k>0 else verts[::-1],mat,uvs if k>0 or uvs is None else uvs[::-1])
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
    edges=(-w+.28,.30,w-.22)
    posts=[edges[0]+.24,(edges[0]+edges[1])*.5,edges[1],(edges[1]+edges[2])*.5,edges[2]-.24]
    for x in posts:
        block(x-.12,end+.085,.09,x+.12,end+.335,.29,"wallstone")
        block(x-.095,end+.11,.29,x+.095,end+.31,floor-.40,"wood")
    block(posts[0]-.10,end+.09,floor-.40,posts[-1]+.10,end+.33,floor-.19,"wood")
    for j in range(1,ceil((2*w-.58)/.60)):
        x=-w+.28+j*.60
        block(x-.039,end+.34,floor-.31,x+.039,front+.11,floor-.19,"wood")
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
        for px in [x for x in posts if lo<=x<hi]:
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
        sleep_room(p,lo,hi,front,floor,block,skin,c,i)
        # Interior platform bed, quilt and small table are set away from the threshold.
        bedx=hi-2.12
        for xx in (bedx+.07,hi-.39):
            for yy in (10.61,12.15):
                block(xx,yy,floor,xx+.09,yy+.09,floor+.32,"wood")
        block(bedx,10.55,floor+.29,hi-.26,12.28,floor+.45,"wood")
        block(bedx+.03,10.58,floor+.45,hi-.29,12.26,floor+.54,"linen",False)
        # Folded cotton drops over the bed rail with a loose hem, leaving the
        # pillow and bed frame visible from the doorway.
        layers=[(bedx-.055,.32),(bedx-.035,.49),(bedx+.05,.57),(bedx+.70,.588),(hi-.81,.57)]
        for j in range(9):
            va=10.61+j*.173; vb=va+.173
            for (a,ha),(b,hb) in zip(layers,layers[1:]):
                skin([(a,va,floor+ha+.014*cos(j)),(b,va,floor+hb+.014*cos(j)),
                      (b,vb,floor+hb+.014*cos(j+1)),(a,vb,floor+ha+.014*cos(j+1))],"cloth")
        for yy in (10.78,11.57):
            pillow=[(hi-.80,yy),(hi-.47,yy-.045),(hi-.34,yy+.065),(hi-.34,yy+.47),
                    (hi-.44,yy+.55),(hi-.78,yy+.50),(hi-.86,yy+.36),(hi-.86,yy+.09)]
            rings=[]
            for ratio,lift in ((1,.545),(.94,.589),(.77,.633),(.44,.646)):
                rings.append([(hi-.595+(x-hi+.595)*ratio, yy+.25+(y-yy-.25)*ratio,floor+lift) for x,y in pillow])
            for outer,inner in zip(rings,rings[1:]):
                for j in range(len(outer)):
                    n=(j+1)%len(outer)
                    skin([outer[j],outer[n],inner[n],inner[j]],"oat")
            skin(rings[-1],"oat")
        block(hi-.37,10.54,floor+.39,hi-.23,12.29,floor+.78,"wood",False)
        block(bedx-.61,11.65,floor+.03,bedx-.09,12.22,floor+.56,"wood")
        for j in range(2):
            block(bedx-.55,11.624,floor+.17+j*.22,bedx-.17,11.65,floor+.32+j*.22,"wood",False)
            block(bedx-.40,11.60,floor+.22+j*.22,bedx-.32,11.624,floor+.25+j*.22,"zinc",False)
        # Enamel flask, lid, cup and side handle above the bedside drawers.
        tx,ty=bedx-.42,11.99
        for dh,dt,r0,r1,key in ((.56,.61,.085,.10,"iron"),(.61,.87,.10,.093,"jade"),(.87,.92,.093,.056,"zinc"),(.92,.952,.058,.058,"clay")):
            for j in range(12):
                a,b=j*pi/6,(j+1)*pi/6
                skin([(tx+r0*cos(a),ty+r0*sin(a),floor+dh),(tx+r0*cos(b),ty+r0*sin(b),floor+dh),
                      (tx+r1*cos(b),ty+r1*sin(b),floor+dt),(tx+r1*cos(a),ty+r1*sin(a),floor+dt)],key)
        block(tx-.15,ty-.014,floor+.64,tx-.12,ty+.014,floor+.84,"iron",False)
        for h in (.64,.82): block(tx-.15,ty-.014,floor+h,tx-.065,ty+.014,floor+h+.025,"iron",False)
        # A wash towel doubles back over a rail fixed to the masonry by the bed.
        block(hi-.23,9.19,floor+1.57,hi-.16,10.34,floor+1.68,"wood",False)
        for yy in (9.24,10.27):
            block(hi-.18,yy-.024,floor+1.58,hi+.015,yy+.024,floor+1.65,"iron",False)
        for yy in (9.34,9.64,9.97,10.20):
            block(hi-.31,yy-.018,floor+1.58,hi-.18,yy+.018,floor+1.62,"iron",False)
        block(hi-.32,9.24,floor+1.60,hi-.29,9.72,floor+1.634,"zinc",False)
        for j in range(12):
            def hem(n):
                yy=9.29+n*.031
                fold=.009*cos(n*1.70)
                return [(hi-.31+fold,yy,floor+1.03+.012*sin(n*.45)),(hi-.325+fold,yy,floor+1.39),
                        (hi-.316,yy,floor+1.638),(hi-.29,yy,floor+1.638),(hi-.283+fold,yy,floor+1.20)]
            a,b=hem(j),hem(j+1)
            for h in range(len(a)-1):
                strip=[a[h],b[h],b[h+1],a[h+1]]
                skin(strip,"denim");skin(strip[::-1],"denim")
        for y in (9.96,10.19):
            block(hi-.32,y,floor+1.12,hi-.28,y+.028,floor+1.57,"wood",False)
        block(hi-.37,9.90,floor+.85,hi-.24,10.30,floor+1.14,"clay",False)
        block(lo+.35,10.91,floor+.06,lo+1.02,12.23,floor+1.78,"wood")
        block(lo+1.021,10.94,floor+.14,lo+1.045,11.54,floor+1.69,"wood",False)
        for ipeg in (11.49,11.65):
            block(lo+1.04,ipeg,floor+.89,lo+1.08,ipeg+.039,floor+1.03,"zinc",False)
        # Exposed ceiling joists bear into front and rear wall plates.
        for j in range(1,ceil((hi-lo)/.77)):
            x=lo+j*.77
            block(x-.044,front+.12,floor+2.17,x+.044,12.72,floor+2.31,"wood")
        for face_v in (front+.18,12.44):
            block(lo,face_v,floor+2.09,hi,face_v+.17,floor+2.22,"wood")
        # A writing ledge, drawer and stool share the wall with the wardrobe.
        block(lo+.20,9.15,floor+.73,lo+.83,10.54,floor+.80,"wood")
        for vy in (9.21,10.39):
            block(lo+.25,vy,floor,lo+.76,vy+.08,floor+.73,"wood")
        block(lo+.23,9.21,floor+.58,lo+.81,9.71,floor+.73,"wood")
        block(lo+.845,9.34,floor+.65,lo+.88,9.56,floor+.68,"iron",False)
        block(lo+.88,9.50,floor+.39,lo+1.30,9.92,floor+.45,"wood")
        for xx in (lo+.92,lo+1.24):
            for vy in (9.54,9.85):
                block(xx,vy,floor,xx+.045,vy+.045,floor+.39,"wood",False)
        for j in range(3):
            block(lo+.28,10.08,floor+.80+j*.036,lo+.68,10.40,floor+.834+j*.036,("jade","linen","clay")[j],False)
        # A drawn pair of cotton curtains leaves the middle of the rear window open.
        block(edge_l-.16,12.37,floor+2.02,edge_r+.16,12.40,floor+2.055,"iron",False)
        for x in (edge_l-.12,edge_r+.12):
            block(x-.018,12.38,floor+2.018,x+.018,12.60,floor+2.055,"iron",False)
        for start in (edge_l-.10,edge_r-.28):
            for j in range(8):
                x=start+j*.048
                va=12.38+.040*cos(j*pi/2)
                vb=12.38+.040*cos((j+1)*pi/2)
                textile=[(x,va,floor+2.025),(x,va-.035,floor+.74),(x+.048,vb-.035,floor+.75),(x+.048,vb,floor+2.025)]
                curtain=("sage","oat","denim")[(p["plot_id"]+i)%3]
                skin(textile,curtain);skin(textile[::-1],curtain)
        # Beneath the sleeping bay is a work/storage room with a deep slated rack.
        for hh in (.30,.94,1.58):
            block(lo+.38,11.68,hh,lo+1.72,12.33,hh+.065,"wood")
        for xx in (lo+.41,lo+1.65):
            for yy in (11.72,12.24):
                block(xx,yy,.09,xx+.055,yy+.055,1.68,"wood")
        for j in range(3):
            block(lo+.48+j*.34,11.76,1.005,lo+.76+j*.34,12.17,1.34,"canopy",False)
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
        stairs=p.get("kerb_stairs",{})
        if "front" in stairs:front=world(p,*stairs["front"]["toe"])
        if "back" in stairs:back=world(p,*stairs["back"]["toe"])
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
        route=[p,q]
        # A sideways entrance needs room to approach the toe past the cheek wall.
        # Route the paving along the outside edge only when the direct segment intersects it.
        # The runoff wall bounds the 55/57 lane. Its previously walked straight
        # approach clears both low treads inside the paving.
        ends=() if {plots[i]["plot_id"],plots[j]["plot_id"]}=={55,57} else ((0,plots[i]),(-1,plots[j]))
        for end,owner in ends:
            for key,stair in owner.get("kerb_stairs",{}).items():
                toe=stair["toe"]
                if hypot(*(np.array(route[end])-world(owner,*toe)))>.05:continue
                direction=-1 if key=="front" else 1
                mid=stair["pad"][0];edge=stair["edge"]
                side=stair["direction"];last=toe[0]-side*.24
                local_line=np.array([local(owner,*pt) for pt in np.linspace(route[0],route[-1],81)])
                near=(local_line[:,0]>min(mid-.97,last)-.36)&(local_line[:,0]<max(mid+.97,last)+.36)
                depth=direction*(local_line[:,1]-edge)
                if not np.any(near&(depth>-.30)&(depth<stair["width_m"]+.37)):continue
                outer=edge+direction*(stair["width_m"]+.91)
                upstream=mid-side*1.68
                bends=[world(owner,toe[0]+side*.38,outer),world(owner,upstream,outer)]
                if end==0:route[1:1]=bends
                else:route[-1:-1]=reversed(bends)
        for u,v in zip(route[:-1],route[1:]):visible_walk(u,v,.94)
        paths.append({"type":"shared","plots":[i,j],"points":route})
    return paths
