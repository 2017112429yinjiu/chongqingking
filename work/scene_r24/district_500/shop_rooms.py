"""Walk-in rooms, working furniture and weather protection for occupied street fronts."""
from math import cos, sin, pi
from random import Random


def furnish(p, cuboid, solid, face, colors):
    w,d,z=p["width"],p["depth"],p["height"]
    front,back=-d/2,d/2
    m=colors
    def box(x0,y0,h0,x1,y1,h1,key):
        cuboid(x0,y0,z+h0,x1,y1,z+h1,m[key])
    def panel(points,key):
        face([(x,y,z+h) for x,y,h in points],m[key])
    def support(x0,y0,h0,x1,y1,h1,key):
        solid(x0,y0,z+h0,x1,y1,z+h1,m[key])
    def vessel(x,y,h,rings,key,n=14):
        for (h0,r0),(h1,r1) in zip(rings,rings[1:]):
            for j in range(n):
                a,b=2*pi*j/n,2*pi*(j+1)/n
                panel([(x+r0*cos(a),y+r0*sin(a),h+h0),(x+r0*cos(b),y+r0*sin(b),h+h0),
                       (x+r1*cos(b),y+r1*sin(b),h+h1),(x+r1*cos(a),y+r1*sin(a),h+h1)],key)
        hz,rad=rings[-1]
        panel([(x+rad*cos(j*2*pi/n),y+rad*sin(j*2*pi/n),h+hz) for j in range(n)],key)
    def table(x,y,sx,sy,h,key="wood",metal="iron"):
        for a in (-1,1):
            for b in (-1,1):
                px=x+a*(sx/2-.075); py=y+b*(sy/2-.075)
                box(px-.035,py-.035,.035,px+.035,py+.035,h-.045,metal)
        support(x-sx/2,y-sy/2,h-.055,x+sx/2,y+sy/2,h,key)
        for side in (-1,1):
            edge=y+side*(sy/2-.06)
            box(x-sx/2+.04,edge-.026,h-.15,x+sx/2-.04,edge+.026,h-.047,metal)
    def wheel(x,y,h,r):
        # Upright wheels on the repair rack. The tyre has an open hub and radial spokes.
        for j in range(28):
            a,b=2*pi*j/28,2*pi*(j+1)/28
            for r0,r1,v0,v1 in [(r,r,-.043,.043),(r-.043,r,-.043,-.043),(r,r-.043,.043,.043)]:
                panel([(x+r0*cos(a),y+v0,h+r0*sin(a)),(x+r0*cos(b),y+v0,h+r0*sin(b)),
                       (x+r1*cos(b),y+v1,h+r1*sin(b)),(x+r1*cos(a),y+v1,h+r1*sin(a))],"rubber")
            if j%2==0:
                panel([(x-.008,y,h),(x+(r-.04)*cos(a),y,h+(r-.04)*sin(a)),
                       (x+(r-.04)*cos(a)+.009,y,h+(r-.04)*sin(a)+.007)],"zinc")
    site=p["name"]
    # The ceiling is a separate limewashed underside to the floor above.
    box(-w/2+.21,front+.20,2.795,w/2-.21,back-.20,2.817,"lime")
    for end in (-1,1):
        x=end*(w/2-.27)
        for v0,v1 in ((front+.25,-1.19),(1.19,back-.25)):
            box(x-.026,v0,.09,x+.026,v1,1.02,"dado")
    if not site:
        # Different resident uses leave the through route between the two thresholds.
        side=1 if p["door_u"]<0 else -1
        x=side*(w/2-1.1)
        table(x,back-1.0,1.45,.45,.43)
        if p["kind"]%2:
            for i in range(3):
                box(x-.58+i*.39,back-.37,1.18,x-.24+i*.39,back-.26,1.49,"iron")
        else:
            for i in range(2):
                vessel(x-.36+i*.73,back-.87,.43,[(0,.12),(.29,.17),(.31,.18)],"clay")
        return
    left,right=-w/2+.32,w/2-.32
    # Paired columns and beams expose the depth of the shop. Outside each
    # opening the timber shutters fold back onto the actual masonry piers.
    bays=5 if w>23 else 4
    for i in range(1,bays):
        x=left+i*(right-left)/bays
        if abs(x-p["door_u"])<1.42: continue
        support(x-.165,front+.09,.04,x+.165,front+.42,2.79,"lime")
        box(x-.18,front+.07,.04,x+.18,front+.45,.38,"stone")
        for j in range(3):
            box(x+.18+j*.07,front+.10,.16,x+.234+j*.07,front+.56,2.21,"wood")
    box(left,front+.05,2.41,right,front+.39,2.77,"wood")
    for v in (front+2.9,back-2.5):
        box(left,v-.09,2.55,right,v+.09,2.80,"wood")
    # Eaves fall towards an outer gutter; exposed underside, fascia and
    # transverse purlins have physical thickness. Crests overlap by one sheet.
    sheet="zinc" if site.endswith("修理铺") else "tile" if site.endswith("茶摊") else "canopy"
    for i in range(32):
        a=left+(right-left)*i/32;b=left+(right-left)*(i+1)/32
        for x0,x1,lift0,lift1 in ((a,a+.045,0,.045),(a+.045,a+.094,.045,0),(a+.094,b,0,0)):
            pts=[(x0,front,2.98+lift0),(x0,front-2.14,2.56+lift0),(x1,front-2.14,2.56+lift1),(x1,front,2.98+lift1)]
            panel(pts,sheet);panel(pts[::-1],sheet)
    box(left,front-2.15,2.46,right,front-2.07,2.56,"zinc")
    for x in (left+.14,(left+right)*.5+2.5,right-.14):
        box(x-.046,front-2.03,.035,x+.046,front-1.94,2.57,"iron")
        panel([(x,front-2.03,2.13),(x,front-1.57,2.62),(x,front-2.03,2.57)],"iron")
    # The rear service side has one enclosed stock room; its open doorway
    # faces the working area, leaving the resident passage unimpeded.
    stock=right-3.0
    support(stock,back-3.15,.035,stock+.17,back-.20,2.78,"lime")
    support(stock+1.28,back-3.15,.035,right,back-2.98,2.78,"dado")
    box(stock,back-3.15,2.16,stock+1.28,back-2.98,2.78,"lime")
    if site.endswith("市场"):
        rng=Random(184)
        for i,(x,y) in enumerate(((left+2.0,front+2.4),(left+2.0,front+5.25),(2.85,front+3.6),(right-2,front+2.5))):
            table(x,y,2.35,1.04,.83)
            for j in range(3):
                xx=x-.75+j*.75
                box(xx-.34,y-.44,.83,xx+.34,y+.44,.88,"wood")
                for yy in (y-.43,y+.43):
                    for k in range(2):box(xx-.35,yy-.024,.87+.075*k,xx+.35,yy+.024,.925+.075*k,"wood")
                for k in range(20):
                    px,py=xx+rng.uniform(-.23,.23),y+rng.uniform(-.30,.30)
                    tone=("greens","clay","gourd","greens")[(i+j)%4]
                    sz=rng.uniform(.075,.117)
                    vessel(px,py,.91+rng.uniform(0,.065),[(0,.03),(.035,sz),(.105,sz*.79),(.13,.027)],tone,7)
        table(left+1.2,back-1.0,1.55,.68,.82)
        box(left+.97,back-1.16,.82,left+1.32,back-.87,.93,"jade")
        vessel(left+1.15,back-1,.93,[(0,.09),(.105,.20),(.12,.21)],"zinc")
    elif site.endswith("茶摊"):
        for x,y in [(left+2.5,front+2.8),(3.05,front+3.7),(left+3,back-2.3),(3.6,back-2.0)]:
            table(x,y,1.43,.91,.73)
            vessel(x+.1,y,.73,[(0,.095),(.08,.14),(.19,.115),(.205,.07),(.23,.08)],"clay")
            for side in (-1,1):
                chairx=x+side*.41; chairy=y+side*.94
                table(chairx,chairy,.49,.46,.43,"wood","wood")
                for dx in (-.20,.20):box(chairx+dx-.025,chairy+side*.20-.025,.42,chairx+dx+.025,chairy+side*.20+.025,.90,"wood")
                box(chairx-.24,chairy+side*.20-.021,.75,chairx+.24,chairy+side*.20+.021,.85,"wood")
                vessel(x+side*.41,y,.73,[(0,.039),(.065,.052),(.076,.052)],"china")
        table(right-1.0,front+1.9,1.20,1.65,.82,"stone")
    else:
        table(left+3.1,front+3.6,3.55,.88,.90)
        for x in (left+1.8,left+2.55,left+3.3):
            wheel(x,front+3.82,1.40,.46)
        for j in range(3):
            box(right-2.5,front+1.6,.10+j*.51,right-.55,front+2.22,.16+j*.51,"iron")
            for k in range(3):
                xx=right-2.18+k*.50
                vessel(xx,front+1.93,.16+j*.51,[(0,.12),(.23,.12),(.28,.07)],"jade" if k%2 else "clay")
        for x in (right-2.48,right-.58):
            for y in (front+1.64,front+2.17):box(x-.035,y-.035,.035,x+.035,y+.035,1.35,"iron")
        table(3.1,-.48,1.88,.72,.32,"iron")
        wheel(3.05,-.48,.77,.42)
