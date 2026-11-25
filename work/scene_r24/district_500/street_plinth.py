"""Sloping shop approaches, facing stones, water outlets and recessed service hatches."""
from math import ceil


def build(p,frame,batch,box,ground,m):
    w,d,z=p["width"]/2,p["depth"]/2,p["height"]
    a,b=-w+.42,w-.42; rear=-d; front=rear-2.35
    old_bottom=min(ground(x,front) for x in (-w+.65,0,w-.65))-.12
    bottom=min(old_bottom,*[ground(x,front)-.15 for x in (a,b)]); top=z+.02
    def sheet(points,mat,uvs=None):
        batch.face([frame(*v) for v in points],mat,uvs)
    def wall(left,right,h0,h1):
        if h0>=h1 or right<=left:return
        sheet([(left,front,h0),(right,front,h0),(right,front,h1),(left,front,h1)],m["wallstone"],
              [(left/2.20,h0/2.20),(right/2.20,h0/2.20),(right/2.20,h1/2.20),(left/2.20,h1/2.20)])
    # The surface, side returns and rear keep their native surveyed elevation.
    sheet([(a,front,top),(b,front,top),(b,rear,top),(a,rear,top)],m["flags"])
    sheet([(a,rear,bottom),(b,rear,bottom),(b,front,bottom),(a,front,bottom)],m["wallstone"])
    for x,rev in ((a,True),(b,False)):
        pts=[(x,front,bottom),(x,rear,bottom),(x,rear,top),(x,front,top)]
        sheet(pts[::-1] if rev else pts,m["wallstone"])
    sheet([(b,rear,bottom),(a,rear,bottom),(a,rear,top),(b,rear,top)],m["wallstone"])
    # Choose an accessible bay on either side of the existing two flights.
    candidates=[a+1.46,(a+b)*.5,b-1.46]
    x=min(candidates,key=lambda t:max(ground(t+k,front-.30) for k in (-.65,0,.65)))
    sill=max(ground(x+k,front-.25) for k in (-.65,0,.65))+.085
    head=min(sill+1.78,top-.29)
    if head-sill>1.14:
        h=.73; v=front+.32
        wall(a,x-h,bottom,top);wall(x+h,b,bottom,top);wall(x-h,x+h,bottom,sill);wall(x-h,x+h,head,top)
        for edge in (x-h,x+h):
            box(batch,frame,edge-.036,front,sill,edge+.036,v,head,m["stone"])
        box(batch,frame,x-h,front,head,x+h,v,head+.08,m["stone"])
        box(batch,frame,x-h-.04,front-.075,sill-.07,x+h+.04,v,sill,m["stone"])
        box(batch,frame,x-h+.018,v,sill,x+h-.018,v+.075,head,m["iron"])
        for sign in (-1,1):
            mid=x+sign*.36
            box(batch,frame,mid-.331,v-.022,sill+.035,mid+.331,v,head-.03,m["aged_metal"])
            # Raised, downward-facing pressed louvres over the locked service bay.
            for j in range(6):
                zz=head-.18-j*.075
                sheet([(mid-.235,v-.024,zz+.031),(mid+.235,v-.024,zz+.031),
                       (mid+.235,v-.061,zz),(mid-.235,v-.061,zz)],m["iron"])
            box(batch,frame,x+sign*.09-.017,v-.062,sill+.61,x+sign*.09+.017,v-.018,sill+.74,m["metal"])
        p["facade_work"]["retaining_access"]={"u":x,"recess_m":.32,"clear_height_m":head-sill}
    else:wall(a,b,bottom,top)
    # Jointed stone coping across the exposed wall, trimmed at the two stair heads.
    spans=[(a,-p["width"]*.27-1.16),(-p["width"]*.27+1.16,p["width"]*.22-1.16),
           (p["width"]*.22+1.16,b)]
    for lo,hi in spans:
        if hi<=lo:continue
        n=ceil((hi-lo)/.89)
        for j in range(n):
            u0,u1=lo+(hi-lo)*j/n,lo+(hi-lo)*(j+1)/n
            box(batch,frame,u0,front-.078,top-.125,u1-.006,front+.055,top-.004,m["stone"])
        for j in range(max(1,int((hi-lo)/1.45))):
            xx=lo+(j+.51)*(hi-lo)/max(1,int((hi-lo)/1.45))
            zz=ground(xx,front-.09)+.46
            if zz+.35<top and not (head-sill>1.14 and abs(xx-x)<.82):
                box(batch,frame,xx-.082,front-.017,zz,xx+.082,front+.003,zz+.092,m["iron"])
