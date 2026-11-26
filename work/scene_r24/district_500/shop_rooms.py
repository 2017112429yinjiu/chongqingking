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
        side=1 if p["door_u"]<0 else -1
        # A side room opens off the public passage. The threshold and the
        # household furniture follow the same measured floor as the street door.
        jamb=p["door_u"]+side*1.40
        opening=-.45
        for a,b in ((front+.24,opening-.70),(opening+.70,back-.24)):
            support(jamb-.105,a,.035,jamb+.105,b,2.77,"lime")
            box(jamb-.124,a,.04,jamb+.124,b,.62,"dado")
        support(jamb-.105,opening-.70,2.13,jamb+.105,opening+.70,2.77,"wood")
        edge=side*(w/2-.30);mid=(jamb+edge)/2
        p["room"]={"door_v":opening,"jamb_u":jamb,"inside_u":mid,"use":("bedroom","washroom","kitchen","sitting_room")[p["kind"]]}
        # A panel folds into the room. Sill, frames and small cupboard close
        # the unused service bays while leaving the side window open to daylight.
        x0,x1=sorted((jamb+side*.12,jamb+side*.90))
        box(x0,opening+.70,.09,x1,opening+.77,2.09,"wood")
        for y in (-1.13,0,1.13):box(edge-.025,y-.026,.88,edge+.025,y+.026,2.10,"wood")
        table(mid,back-1.02,1.24,.52,.73,"wood","wood")
        x=side*(w/2-1.03)
        if p["kind"]==0:
            support(x-.67,front+.55,.14,x+.67,front+2.47,.44,"wood")
            box(x-.64,front+.58,.44,x+.64,front+2.43,.55,"linen")
            box(x-.62,front+.64,.55,x+.62,front+1.55,.60,"jade")
            box(x-.44,front+1.93,.55,x+.44,front+2.36,.66,"linen")
        elif p["kind"] in (1,2):
            support(x-.65,front+.42,.035,x+.65,front+1.71,.84,"dado")
            box(x-.70,front+.38,.84,x+.70,front+1.76,.91,"stone")
            if p["kind"]==2:
                vessel(x,front+.93,.91,[(0,.12),(.085,.24),(.18,.25),(.22,.22)],"iron")
                vessel(x,front+.93,1.13,[(0,.24),(.04,.10),(.074,.037)],"zinc")
            else:
                vessel(x,front+.96,.91,[(0,.12),(.13,.25),(.15,.25)],"china")
                box(x+.26,front+.61,.91,x+.295,front+.66,1.23,"zinc")
                box(x+.12,front+.61,1.20,x+.295,front+.66,1.23,"zinc")
        else:
            table(x,front+1.28,1.23,.54,.43,"wood","wood")
            for i in range(2):vessel(mid-.23+i*.45,back-1.02,.73,[(0,.044),(.075,.065)],"china")
        domestic_bay(p, box, support, panel, vessel, table)
        return
    left,right=-w/2+.32,w/2-.32
    # Paired columns and beams expose the depth of the shop. Outside each
    # opening the timber shutters fold back onto the actual masonry piers.
    for x in p["frame"]["u"][1:-1]:
        for j in range(3):
            box(x+.20+j*.07,front+.10,.16,x+.254+j*.07,front+.56,2.21,"wood")
    # Eaves fall towards an outer gutter; exposed underside, fascia and
    # transverse purlins have physical thickness. Crests overlap by one sheet.
    sheet="zinc" if site.endswith("修理铺") else "tile" if site.endswith("茶摊") else "canopy"
    hood_left,hood_right=(-4.36,4.48) if p.get("registered_site") else (left,right)
    for i in range(32):
        a=hood_left+(hood_right-hood_left)*i/32;b=hood_left+(hood_right-hood_left)*(i+1)/32
        for x0,x1,lift0,lift1 in ((a,a+.045,0,.045),(a+.045,a+.094,.045,0),(a+.094,b,0,0)):
            pts=[(x0,front,2.98+lift0),(x0,front-2.14,2.56+lift0),(x1,front-2.14,2.56+lift1),(x1,front,2.98+lift1)]
            panel(pts,sheet);panel(pts[::-1],sheet)
    box(hood_left,front-2.15,2.46,hood_right,front-2.07,2.56,"zinc")
    for x in (hood_left+.14,(hood_left+hood_right)*.5+2.5,hood_right-.14):
        box(x-.046,front-2.03,.035,x+.046,front-1.94,2.57,"iron")
        panel([(x,front-2.03,2.13),(x,front-1.57,2.62),(x,front-2.03,2.57)],"iron")
    # The rear service side has one enclosed stock room; its open doorway
    # faces the working area, leaving the resident passage unimpeded.
    stock=right-3.0
    support(stock,back-3.15,.035,stock+.17,back-.20,2.78,"lime")
    support(stock+1.28,back-3.15,.035,right,back-2.98,2.78,"dado")
    box(stock,back-3.15,2.16,stock+1.28,back-2.98,2.78,"lime")
    # Use the rear bay for the stock that belongs to this particular business.
    # Uprights sit on the floor; each shelf and its goods share a height.
    rack_x=left+.57
    for y in (back-4.10,back-2.55,back-1.0):
        for x in (rack_x,rack_x+.66):
            support(x-.035,y-.035,.035,x+.035,y+.035,2.01,"iron")
    for level in (.30,.92,1.53):
        box(rack_x-.04,back-4.16,level-.065,rack_x+.70,back-.94,level,"wood")
        for j in range(4):
            v=back-3.86+j*.76
            if site.endswith("茶摊"):
                vessel(rack_x+.33,v,level,[(0,.13),(.05,.18),(.29,.18),(.35,.13),(.37,.14)],"clay" if j%2 else "jade")
                vessel(rack_x+.33,v,level+.37,[(0,.14),(.03,.12),(.055,.04)],"wood")
            elif site.endswith("修理铺"):
                wheel(rack_x+.32,v,level+.264,.26)
            else:
                for delta in (-.24,.24):
                    box(rack_x+.05,v+delta,level,rack_x+.59,v+delta+.035,level+.26,"wood")
                for xx in (rack_x+.05,rack_x+.56):
                    for h in (.03,.145):
                        box(xx,v-.23,level+h,xx+.035,v+.25,level+h+.065,"wood")
    # Two working bays flank a narrower public passage. Sills and partitions
    # enclose the stock areas without closing the sightline between entrances.
    aisle=p["door_u"]
    signs=[]
    p["trade_signs"]=signs
    def board(x,v,h,width,text,tone):
        box(x-width/2,v-.055,h-.20,x+width/2,v+.025,h+.20,tone)
        signs.append({"text":text,"u":x,"v":v-.061,"h":h,"width":width})
    for side in (-1,1):
        x=aisle+side*(2.14 if side>0 else 2.53)
        v=front+(1.48 if side>0 else 2.67)
        outer=right-.25 if side>0 else left+.25
        endx=x+side*2.32
        low,high=sorted((x,endx))
        support(low,v,.035,high,v+.40,.78,"dado" if not site.endswith("修理铺") else "iron")
        support(low-.055,v-.07,.78,high+.055,v+.45,.86,"wood")
        for end in (low+.065,high-.065):
            box(end-.04,v+.36,.86,end+.04,v+.44,2.63,"wood")
        box(low,v+.32,2.39,high,v+.46,2.61,"wood")
        # A solid return at the side wall makes a deep shopfront, with a
        # side door to the public aisle between the counter and back room.
        lo,hi=sorted((outer,outer-side*1.12))
        support(lo,front+.30,.035,hi,front+.58,2.51,"lime")
        box(lo,front+.274,.035,hi,front+.30,.87,"dado")
        # A hanging reflector, short cable and ceiling rose use the same axis.
        sx=(low+high)/2; sy=v+1.27
        box(sx-.07,sy-.07,2.75,sx+.07,sy+.07,2.80,"wood")
        box(sx-.009,sy-.009,2.34,sx+.009,sy+.009,2.76,"rubber")
        vessel(sx,sy,2.15,[(0,.18),(.06,.16),(.16,.047),(.19,.035)],"jade",16)
        vessel(sx,sy,2.135,[(0,.105),(.012,.165)],"china",16)
    if site.endswith("市场"):
        # Two permanent wet-market counters flank the central run between
        # the columns. Rear working strips stay clear for restocking.
        for sign in (-1,1):
            inner=aisle+sign*1.91
            outer=inner+sign*.91
            lo,hi=sorted((inner,outer))
            support(lo,-1.51,.035,hi,1.51,.68,"dado")
            support(lo-.055,-1.55,.68,hi+.055,1.55,.76,"stone")
            for v in (-1.49,-.52,.50,1.48):
                box(lo-.02,v-.025,.76,hi+.02,v+.025,.87,"wood")
            for sx in (lo,hi):
                box(sx-.021,-1.5,.76,sx+.021,1.5,.84,"wood")
            if sign>0:
                produce=Random(704)
                for idx in range(16):
                    yy=-1.34+(idx%8)*.37+produce.uniform(-.055,.055)
                    xx=lo+.25+(idx//8)*.36+produce.uniform(-.045,.045)
                    for leaf in range(6):
                        a=leaf*pi/3+produce.uniform(-.52,.52)
                        length=produce.uniform(.12,.23)
                        rows=[]
                        for t,wide,h in ((0,.009,0),(.28,.024,.065),(.52,.049,.123),(.79,.041,.16),(1,.003,.13)):
                            cx=xx+length*t*t*cos(a);cy=yy+length*t*t*sin(a)
                            rows.append([(cx-sin(a)*wide,cy+cos(a)*wide,.76+h+wide*.35),
                                         (cx,cy,.76+h),(cx+sin(a)*wide,cy-cos(a)*wide,.76+h+wide*.38)])
                        for lower,upper in zip(rows,rows[1:]):
                            for k in (0,1):
                                blade=[lower[k],lower[k+1],upper[k+1],upper[k]]
                                panel(blade,("greens","leaf_light","leaf_dark")[leaf%3])
                                panel(blade[::-1],"leaf_dark")
        # A pack-out bench with a wall shelf faces the return aisle.
        x=aisle+4.15
        support(x,back-.90,.035,x+2.56,back-.28,.83,"dado")
        box(x-.05,back-.96,.83,x+2.61,back-.27,.90,"stone")
        for j in range(3):
            xx=x+.20+j*.79
            box(xx,back-.80,.90,xx+.55,back-.38,.94,"wood")
        box(x,back-.61,1.57,x+2.56,back-.27,1.64,"wood")
        for xx in (x+.13,x+2.31):
            box(xx,back-.39,1.31,xx+.06,back-.26,1.57,"iron")
        for j in range(6):
            vessel(x+.28+j*.40,back-.44,1.64,[(0,.09),(.20,.12),(.25,.085)],"clay" if j%2 else "china")
        board(aisle+3.22,front+1.76,2.20,1.40,"时令蔬菜","jade")
        board(aisle-3.62,front+2.94,2.18,1.36,"干货杂粮","wood")
        # Sack lips and hanging balance on the grain stall.
        for j in range(5):
            vessel(aisle-2.86-j*.39,front+2.86,.86,[(0,.14),(.28,.21),(.41,.17),(.43,.20)],"linen" if j%2 else "gourd",12)
        bowl_x=aisle+3.68; bowl_y=front+1.68
        vessel(bowl_x,bowl_y,.86,[(0,.16),(.10,.12),(.16,.095)],"jade")
        vessel(bowl_x,bowl_y,1.02,[(0,.08),(.085,.25),(.104,.26)],"zinc")
        for i,(x,y) in enumerate(((left+2.0,front+2.4),(left+2.0,front+5.25),(2.85,front+3.6),(right-2,front+2.5))):
            table(x,y,2.35,1.04,.83)
            for j in range(3):
                xx=x-.75+j*.75
                box(xx-.34,y-.44,.83,xx+.34,y+.44,.88,"wood")
                for yy in (y-.43,y+.43):
                    for k in range(2):box(xx-.35,yy-.024,.87+.075*k,xx+.35,yy+.024,.925+.075*k,"wood")
        table(left+1.2,back-1.0,1.55,.68,.82)
        box(left+.97,back-1.16,.82,left+1.32,back-.87,.93,"jade")
        vessel(left+1.15,back-1,.93,[(0,.09),(.105,.20),(.12,.21)],"zinc")
    elif site.endswith("茶摊"):
        board(aisle+3.27,front+1.74,2.20,1.48,"盖碗老荫茶","wood")
        for j in range(3):
            vessel(aisle+2.5+j*.41,front+1.64,.86,[(0,.075),(.18,.09),(.29,.08),(.33,.059)],"jade" if j!=1 else "china")
        for j in range(4):
            vessel(aisle-2.86-j*.38,front+2.86,.86,[(0,.062),(.043,.099),(.053,.105)],"china")
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
        board(aisle+3.27,front+1.75,2.20,1.48,"补胎打气","jade")
        board(aisle-3.67,front+2.94,2.20,1.35,"修车配件","wood")
        # Tool board sits behind the low workbench, each spanner on a peg.
        box(aisle+2.24,front+1.94,1.05,aisle+4.18,front+2.03,1.98,"wood")
        for j in range(8):
            x=aisle+2.38+j*.225;bottom=1.29+(j%3)*.065
            box(x-.021,front+1.907,bottom,x+.021,front+1.937,1.69,"zinc")
            box(x-.058,front+1.906,1.65,x+.058,front+1.937,1.70,"zinc")
            for dx in (-.045,.045):
                box(x+dx-.014,front+1.906,1.68,x+dx+.014,front+1.937,1.75,"zinc")
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


def domestic_bay(p, box, support, panel, vessel, table):
    """Work surfaces, storage and domestic fittings set against actual walls."""
    side = 1 if p["door_u"] < 0 else -1
    edge = side * (p["width"]/2-.27)
    front, back = -p["depth"]/2+.24, p["depth"]/2-.24
    mid = p["room"]["inside_u"]
    # The kitchen runs along the street wall with the sink beside the cooker.
    # Work in distances from the outside corner so either handedness fits.
    def cabinet(a, v0, bottom, b, v1, top, mat, physical=False):
        lo, hi = sorted((edge-side*a, edge-side*b))
        (support if physical else box)(lo,v0,bottom,hi,v1,top,mat)
    def pot(a,v,h,profile,mat):
        vessel(edge-side*a,v,h,profile,mat)
    def shelf(a,b,v,h):
        cabinet(a,v,h,b,v+.38,h+.055,"wood")
        for at in (a+.12,b-.12):
            cabinet(at,v,h-.22,at+.037,v+.062,h,"iron")
            cabinet(at,v,h-.042,at+.037,v+.36,h,"iron")
    use=p["room"]["use"]
    if use in ("kitchen","washroom"):
        cabinet(.08,front+.02,.92,3.00,front+.052,1.55,"dado")
        cabinet(1.43,front+.06,.045,3.0,front+.77,.83,"wood",True)
        for a,b in ((1.48,2.18),(2.22,2.94)):
            cabinet(a,front+.76,.14,b,front+.80,.74,"jade")
            cabinet(a+.12,front+.80,.62,a+.35,front+.837,.645,"zinc")
        # A recessed basin has four raised lips, a bowl bottom and wall faucet.
        for a,b,v0,v1 in ((1.38,1.57,.02,.82),(2.43,3.04,.02,.82),(1.57,2.43,.02,.17),(1.57,2.43,.67,.82)):
            cabinet(a,front+v0,.83,b,front+v1,.895,"stone")
        cabinet(1.57,front+.17,.78,2.43,front+.67,.835,"zinc")
        cabinet(1.92,front+.09,.89,1.96,front+.13,1.22,"zinc")
        cabinet(1.92,front+.09,1.19,1.96,front+.40,1.22,"zinc")
        cabinet(1.92,front+.37,1.145,1.96,front+.40,1.22,"zinc")
        shelf(1.43,2.96,front+.06,1.62)
        if use=="kitchen":
            for j in range(4):
                pot(1.70,front+.25,1.676+j*.034,[(0,.07),(.046,.13),(.052,.128)],"china")
            for j in range(3):
                pot(2.07+j*.25,front+.23,1.676,[(0,.055),(.16,.058),(.19,.034)],("jade","clay","china")[j])
            cabinet(.12,front+.07,1.72,1.29,front+.64,1.84,"zinc")
            cabinet(.32,front+.08,1.84,1.08,front+.37,2.03,"iron")
            cabinet(.56,front+.09,2.03,.84,front+.34,2.80,"zinc")
            cabinet(2.57,front+.20,.897,2.92,front+.63,.93,"wood")
        else:
            # Slatted front, a recessed drum door, soap bottles and drying pole.
            cabinet(.18,front+1.61,.04,1.05,front+2.37,.91,"linen",True)
            cabinet(.21,front+2.366,.69,1.02,front+2.403,.866,"zinc")
            cabinet(.28,front+2.402,.745,.54,front+2.414,.825,"rubber")
            for h,r,y0,key in ((.43,.278,2.395,"zinc"),(.43,.243,2.409,"rubber"),(.43,.203,2.416,"iron"),
                              (.782,.049,2.418,"china")):
                cx=edge-side*(.614 if h<.6 else .807)
                ring=[(cx+r*cos(j*pi/16),front+y0,h+r*sin(j*pi/16)) for j in range(32)]
                panel(ring,key);panel(ring[::-1],key)
            cabinet(.75,front+2.417,.38,.815,front+2.455,.51,"zinc")
            for j in range(3):
                pot(1.72+j*.37,front+.24,1.676,[(0,.067),(.17,.08),(.27,.044),(.30,.033)],("jade","china","clay")[j])
            cabinet(1.60,front+.48,1.43,2.81,front+.51,1.465,"zinc")
            cabinet(2.23,front+.48,1.07,2.63,front+.515,1.46,"canopy")
    else:
        # Panelled cupboard and built-in storage are on the street wall,
        # outside both the side-door swing and the approach to the window.
        cabinet(1.63,front+.07,.07,2.92,front+.62,1.98,"wood",True)
        for j in range(2):
            a=1.67+j*.62
            cabinet(a,front+.62,.17,a+.58,front+.65,1.88,"wood")
            cabinet(a+.08,front+.65,.70,a+.50,front+.67,1.64,"canopy")
            cabinet(a+.49,front+.67,.93,a+.52,front+.71,1.06,"zinc")
        if use=="sitting_room":
            cabinet(.12,front+.06,.095,1.29,front+.55,.64,"wood",True)
            cabinet(.28,front+.10,.64,1.15,front+.32,1.22,"rubber")
            cabinet(.32,front+.32,.72,1.11,front+.34,1.17,"iron")
        else:
            shelf(.17,1.23,front+.08,1.44)
            for j in range(5):
                a=.31+j*.115
                cabinet(a,front+.11,1.50,a+.08,front+.35,1.77-(j%3)*.036,("jade","clay","linen")[j%3])
    # A chair at the existing table, along with its working surface.
    table(mid+.56*side,back-1.38,.42,.41,.43,"wood","wood")
    for dx in (-.18,.18):
        x=mid+.56*side+dx
        box(x-.022,back-1.61,.43,x+.022,back-1.566,.84,"wood")
    box(mid+.56*side-.20,back-1.61,.72,mid+.56*side+.20,back-1.566,.84,"wood")
    vessel(mid-.26,back-.78,.73,[(0,.059),(.18,.075),(.22,.043)],"clay")
