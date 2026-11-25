"""Ground-floor apertures shared by masonry, paint and joinery."""
from math import cos,pi


def plan(p):
    if p["name"]:return []
    axes=p["frame"]["u"];entry=p["door_u"];out=[]
    for j,(lo,hi) in enumerate(zip(axes,axes[1:])):
        a,b=lo+.32,hi-.32
        if a<entry<b:continue
        if b<=entry:a,b=a,min(b,entry-1.32)
        else:a,b=max(a,entry+1.32),b
        if b-a<1.04:continue
        width=min(2.04,b-a);u=(a+b)*.5
        out.append({"left":u-width/2,"right":u+width/2,"sill":.92 if p["kind"] in (1,2) else .77,
                    "head":2.16,"shutter":(p["plot_id"]+j)%5==0})
    return out


def wall_pieces(p):
    openings=[(s["left"],s["right"],s["sill"],s["head"]) for s in p["street_windows"]]
    openings.append((p["door_u"]-1.08,p["door_u"]+1.08,0,2.45))
    left=-p["width"]/2
    for a,b,sill,head in sorted(openings):
        if a>left:yield left,a,0,2.82
        if sill:yield a,b,0,sill
        yield a,b,head,2.82
        left=b
    if left<p["width"]/2:yield left,p["width"]/2,0,2.82


def install(p,box,face,m):
    edge=-p["depth"]/2;z=p["height"]
    for j,s in enumerate(p["street_windows"]):
        a,b=s["left"],s["right"];sill=z+s["sill"];head=z+s["head"];mid=(a+b)*.5
        trim=m["wood"] if (p["kind"]+j)%3==0 else m["trim"]
        box(a-.085,edge-.138,sill-.068,b+.085,edge+.20,sill+.015,m["stone"])
        for x in (a+.026,b-.026,mid):
            box(x-.025,edge+.065,sill+.012,x+.025,edge+.116,head,trim)
        for h in (sill+.033,head-.31,head-.03):
            box(a,edge+.065,h-.021,b,edge+.116,h+.021,trim)
        for x0,x1,h0,h1 in ((a+.054,mid-.029,sill+.058,head-.338),(a+.05,b-.05,head-.284,head-.049)):
            face([(x0,edge+.124,h0),(x1,edge+.124,h0),(x1,edge+.124,h1),(x0,edge+.124,h1)],m["glass"])
        # The other half is open toward the room. Gather the curtain on one side.
        if s["shutter"]:
            for n in range(5+j%3):
                high=head-.015-n*.061
                face([(a-.04,edge-.09,high),(b+.04,edge-.09,high),
                      (b+.04,edge-.112,high-.049),(a-.04,edge-.112,high-.049)],m["metal"])
            box(a-.085,edge-.13,head,b+.085,edge+.01,head+.14,m["metal"])
        else:
            box(a-.052,edge+.24,head-.07,b+.052,edge+.264,head-.048,m["iron"])
            width=(b-a)*(.22 if j%2 else .29);low=sill+.12
            for n in range(9):
                x0=a+.04+width*n/9;x1=x0+width/9
                v0=edge+.239+.029*cos(n*1.95);v1=edge+.239+.029*cos((n+1)*1.95)
                face([(x0,v0,head-.064),(x0,v0+.021,low+.021*cos(n)),(x1,v1+.021,low+.021*cos(n+1)),(x1,v1,head-.064)],m["cotton"])
    if p["street_windows"]:
        u=p["door_u"];span=1.08
        for x in (u-span-.022,u+span+.022):
            box(x-.033,edge-.028,z+.035,x+.033,edge+.20,z+2.44,m["wood"])
        box(u-span-.05,edge-.030,z+2.405,u+span+.05,edge+.20,z+2.46,m["wood"])
