"""Fitted noodle kitchen. All coordinates below are in metres in the shop frame."""
def noodle_kitchen(world,part,half,rear,old):
    name='D18_NoodleKitchen'
    wa=rear-.0375
    def slab(x,d,z,w,b,h,m):part(name,x,d,z,w,b,h,m)
    def rod(a,b,r,key,n=10):
        p=world(*a);q=world(*b);axis=(q-p).normalized()
        e=axis.cross(Vector((0,0,1)) if abs(axis.z)<.88 else Vector((1,0,0))).normalized()
        t=axis.cross(e)
        band=[r*(e*math.cos(i*math.tau/n)+t*math.sin(i*math.tau/n)) for i in range(n)]
        for i,v in enumerate(band):
            u=band[(i+1)%n];face(name,[p+v,p+u,q+u,q+v],key)
        face(name,[p+v for v in reversed(band)],key);face(name,[q+v for v in band],key)
    def lathe(x,d,z,profile,key,n=24,caps=True):
        rings=[[world(x+r*math.cos(i*math.tau/n),d+r*math.sin(i*math.tau/n),z+h) for i in range(n)] for r,h in profile]
        for a,b in zip(rings,rings[1:]):
            for i in range(n):j=(i+1)%n;face(name,[a[i],a[j],b[j],b[i]],key)
        if caps:
            face(name,rings[0][::-1],key);face(name,rings[-1],key)
    def ring(x,d,z,r,t,m):lathe(x,d,z,[(r-t,0),(r,0),(r,t),(r-t,t),(r-t,0)],m,caps=False)
    def tapered(x,d,z,layers,m):
        contour=[[(x+a*w/2,d+b*dep/2,z+h) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]] for w,dep,h in layers]
        for a,b in zip(contour,contour[1:]):
            for i in range(4):j=(i+1)%4;face(name,[world(*q) for q in [a[i],a[j],b[j],b[i]]],m)
        face(name,[world(*q) for q in reversed(contour[0])],m);face(name,[world(*q) for q in contour[-1]],m)
    # Glazed splashback only behind the working line. Insets seat in a grey mortar bed.
    slab(0,wa-.010,1.47,half*2-.03,.030,1.36,'grout')
    for j in range(6):
        for i in range(15):
            x=(i-7)*.204;z=.908+j*.219
            slab(x,wa-.030,z,.200,.018,.214,['oldtile','oldtile','agedtile'][(i*19+j*13+i*j)%9%3])
    # Stove, boiling and straining station, with a folded edge and raised back splash.
    x=-.96;d=wa-.39
    slab(x,d,.416,.99,.67,.73,'stove');slab(x,d,.801,1.05,.73,.044,'steel')
    slab(x,d+.34,.924,1.03,.027,.21,'steel')
    for i in (-.36,.36):
        for j in (-.24,.24):slab(x+i,d+j,.037,.066,.066,.075,'iron')
    slab(x,d-.35,.686,.91,.036,.155,'stove')
    for off in [-.26,.22]:
        rod((x+off,d-.363,.70),(x+off,d-.41,.70),.044,'knob')
        rod((x+off,d-.412,.70),(x+off+.008,d-.416,.725),.006,'rice')
    for off,r,h in [(-.225,.20,.263),(.242,.164,.195)]:
        px=x+off
        lathe(px,d,.823,[(r*.83,0),(r*.94,.014),(r,h-.012),(r+.009,h),(r+.009,h+.009),(r-.007,h+.009),(r-.008,.026)],'steel')
        for sign in [-1,1]:
            q=px+sign*r
            rod((q,d-.043,.823+h*.72),(q+sign*.042,d-.043,.823+h*.72),.009,'iron')
            rod((q+sign*.042,d-.043,.823+h*.72),(q+sign*.042,d+.043,.823+h*.72),.011,'knob')
            rod((q+sign*.042,d+.043,.823+h*.72),(q,d+.043,.823+h*.72),.009,'iron')
        if off<0:
            lathe(px,d,.823+h+.007,[(r+.006,0),(r-.006,.016),(.065,.045),(.018,.048)],'steel')
            lathe(px,d,.823+h+.054,[(.018,0),(.024,.024),(.030,.035),(.026,.041)],'knob')
        else:
            lathe(px,d,.823+h-.05,[(r-.012,0),(r-.012,.003)],'broth')
            rod((px+.03,d,.823+h-.040),(px+.15,d+.06,.823+h+.15),.009,'bamboo')
    # Folded hood fascia and sloping plenum connected to a rectangular duct entering the rear wall.
    hx=-.94;hd=wa-.39
    tapered(hx,hd,1.72,[(1.10,.74,0),(1.10,.74,.068),(.42,.32,.34)],'steel')
    slab(hx,hd,2.158,.32,.27,.205,'duct')
    slab(hx,(wa+hd)/2,2.235,.32,wa-hd+.14,.15,'duct')
    for sx in [-.14,.14]:slab(hx+sx,wa-.035,2.231,.026,.075,.195,'steel')
    for j in range(10):slab(hx-.39+j*.087,hd-.025,1.719,.015,.39,.013,'iron')
    # Open prep bench with four seated legs and an undershelf.
    x=.075;d=wa-.41
    slab(x,d,.857,.94,.64,.047,'steel')
    for a in [-.423,.423]:
        for b in [-.268,.268]:
            slab(x+a,d+b,.417,.034,.034,.834,'steel')
            slab(x+a,d+b,.023,.045,.045,.046,'knob')
    slab(x,d,.215,.894,.584,.027,'steel')
    lathe(x-.155,d-.10,.881,[(.148,0),(.151,.02),(.152,.042),(.148,.048)],'bamboo')
    slab(x-.154,d-.097,.934,.168,.058,.009,'steel');slab(x-.02,d-.097,.937,.094,.027,.016,'knob')
    for i in range(3):
        px=x+.12+i*.098
        lathe(px,d+.14,.881,[(.038,0),(.046,.012),(.047,.102),(.032,.117),(.031,.133)],['chili','amber','jar'][i])
        lathe(px,d+.14,1.014,[(.034,0),(.036,.005),(.036,.019),(.033,.021)],['knob','wine','ivory'][i])
    # Wall-hung bowl shelf is screwed to three triangular brackets reaching its front lip.
    sx=.120;sd=wa-.18;sz=1.521
    slab(sx,sd,sz,.98,.30,.032,'steel')
    slab(sx,sd+.142,sz+.033,.98,.021,.057,'steel')
    for a in [-.403,0,.403]:
        wallx=sx+a
        slab(wallx,wa-.037,sz-.14,.039,.071,.28,'duct')
        rod((wallx,wa-.066,sz-.26),(wallx,sd-.116,sz-.024),.010,'steel')
        slab(wallx,sd-.004,sz-.03,.032,.273,.026,'duct')
    def bowlstack(x,d,z,count):
        for j in range(count):
            b=z+.017*j
            lathe(x,d,b,[(.046,0),(.049,.010),(.055,.016),(.084,.035),(.104,.062),(.107,.072),(.100,.074),(.082,.046),(.049,.025)],'rice')
            ring(x,d,b+.058,.102,.003,'indigo')
    bowlstack(sx-.265,sd-.005,1.537,5);bowlstack(sx+.025,sd+.015,1.537,3);bowlstack(x+.225,d-.125,.881,2)
    for i in range(3):
        lathe(x-.225,d,.230+i*.067,[(.135,0),(.145,.008),(.147,.065),(.138,.068),(.135,.017)],'bamboo')
        ring(x-.225,d,.230+i*.067+.044,.15,.008,'wine')
    # Wall-side sink. Metal sides and a recessed basin leave a real opening.
    x=1.02;d=wa-.40
    for a in [-.394,.394]:
        for b in [-.244,.244]:slab(x+a,d+b,.425,.033,.033,.85,'steel')
    for a in [-1,1]:
        slab(x+a*.345,d,.858,.17,.64,.042,'steel')
        slab(x,d+a*.263,.858,.52,.114,.042,'steel')
        slab(x+a*.254,d,.759,.013,.415,.168,'steel')
        slab(x,d+a*.202,.759,.513,.013,.168,'steel')
    slab(x,d,.676,.512,.412,.014,'steel')
    lathe(x,d,.684,[(.032,0),(.034,.002),(.029,.004)],'knob')
    rod((x+.13,wa-.028,1.10),(x+.13,wa-.25,1.10),.018,'steel')
    rod((x+.13,wa-.25,1.10),(x+.13,wa-.25,1.045),.017,'steel')
    rod((x+.13,wa-.025,1.10),(x+.13,wa-.063,1.10),.042,'duct')
    # Warm task light under the ledge, with an enclosed strip and two end caps.
    slab(.55,wa-.056,1.986,1.23,.108,.059,'duct');slab(.55,wa-.085,1.957,1.14,.059,.023,'opal')
    exec(compile((here/'noodle_front.py').read_text('utf8'),str(here/'noodle_front.py'),'exec'),dict(globals(),**locals()))
    exec(compile((here/'service_wall.py').read_text('utf8'),str(here/'service_wall.py'),'exec'),dict(globals(),**locals()))
    layout['kitchen']={'room':'A01_edge2_door','rear_plane':gd(world(0,wa,1)),'probes':[
        {'name':nm,'start':gd(world(*a)),'end':gd(world(*b)),'mesh':mesh}
        for nm,a,b,mesh in [('pot_on_burner',(-1.185,wa-.39,.831),(-1.185,wa-.39,.803),name),
        ('bowl_on_shelf',(-.145,sd,1.545),(-.145,sd,1.499),name),
        ('bracket_at_wall',(.120,wa-.092,1.37),(.120,wa+.028,1.37),name),
        ('hood_duct_enters_wall',(-.94,wa-.025,2.234),(-.94,wa+.16,2.234),'COL_D18_RoomShells'),
        ('table_foot',(-.348,wa-.678,.017),(-.348,wa-.678,-.06),'COL_D18_RoomShells')]]}
