# This is executed by noodle_kitchen so it shares the counter datum and light placement.
# The door opens onto a short flight. Return both sides of each nosing into the existing plinth.
for x,d,z,w,b,h in [(0,-.78,-.375,1.64,.38,.18),(0,-.415,-.276,1.64,.35,.284)]:
    part('COL_D18_NoodleEntry',x,d,z,w,b,h,'oldstep')
# Masonry cooker with a separate clean pass at the street. Counter front faces arriving customers.
cx=-1.33;cd=.78
slab(cx,cd,.402,1.56,.80,.805,'grout')
for j in range(4):
    for i in range(8):
        slab(cx+(i-3.5)*.193,cd-.408,.118+j*.196,.189,.018,.192,'skirt' if j==0 else 'oldtile')
for j in range(4):
    for i in range(4):slab(cx+.783,cd+(i-1.5)*.195,.118+j*.196,.018,.191,.192,'skirt' if j==0 else 'oldtile')
slab(cx,cd,.835,1.64,.85,.06,'steel')
slab(cx,cd+.415,.918,1.61,.024,.125,'steel')
# Countertop and open pot, rolled rim, side handles. Condiments and drain basket share the clean work surface.
lathe(-1.70,.78,.865,[(.195,0),(.216,.016),(.228,.302),(.241,.314),(.241,.324),(.226,.324),(.213,.026)],'steel',40)
lathe(-1.70,.78,1.145,[(.221,0),(.222,.003)],'broth',40)
for sign in [-1,1]:
    for dy in [-.065,.065]:rod((-1.7+sign*.223,.78+dy,1.085),(-1.7+sign*.27,.78+dy,1.085),.01,'steel')
    rod((-1.7+sign*.270,.715,1.085),(-1.7+sign*.270,.845,1.085),.011,'knob')
# Handled noodle strainer, shallow fry basket and one bunch of noodles above the surface.
for rad,z in [(.036,1.112),(.062,1.13),(.085,1.156),(.102,1.183)]:
    ring(-1.66,.80,z,rad,.003,'steel')
rod((-1.573,.83,1.177),(-1.43,.95,1.325),.006,'steel')
rod((-1.43,.95,1.325),(-1.355,1.008,1.408),.014,'bamboo')
for j in range(19):
    y=.736+j*.0046;prev=(-1.74,y,1.149)
    for k in range(1,12):
        q=(-1.74+k*.012,y+.009*math.sin(.73*k+j*.41),1.15+.016*math.sin(math.pi*k/12)+.007*math.sin(k+.6*j))
        rod(prev,q,.0023,'noodle',6);prev=q
# Oil, spring onion and pickle pots. Heights and fill levels follow use.
for x,y,r,h,key in [(-1.14,.755,.118,.087,'chilioil'),(-.87,.81,.101,.089,'scallion'),(-1.00,1.048,.084,.092,'brine')]:
    z=.865
    lathe(x,y,z,[(r*.66,0),(r*.74,.011),(r,h-.01),(r,h),(r-.006,h+.003),(r*.72,.017)],'brownware')
    lathe(x,y,z+h-.021,[(r*.91,0),(r*.93,.003)],key)
    if key=='scallion':
        for i in range(46):
            a=i*2.4;rr=math.sqrt((i+.5)/46)*r*.78
            px=x+math.cos(a)*rr;py=y+math.sin(a)*rr
            rod((px,py,z+h-.019),(px+.007*math.cos(i),py+.008*math.sin(i),z+h-.016),.0036,['leaf','scallion','celadon'][i%3],7)
    if key=='chilioil':
        rod((x+.025,y,z+h-.014),(x+.13,y+.056,z+h+.08),.006,'steel')
bowlstack(-.769,.539,.866,5)
# The tray is refilled from behind; a handful of chopsticks rather than a uniform comb.
lathe(-1.34,1.04,.865,[(.043,0),(.052,.009),(.056,.131),(.049,.133),(.044,.015)],'brownware')
for i in range(19):
    a=i*2.4;r=.04*math.sqrt((i+.5)/19);x=-1.34+r*math.cos(a);y=1.04+r*math.sin(a)
    rod((x,y,.902),(x+.42*r*math.cos(a),y+.42*r*math.sin(a),1.115+.025*math.sin(i*1.3)),.003,'bamboo',6)
# Compact square eating table for the original injection-moulded chair. Cup and chopsticks sit beside one used bowl.
tx=1.28;td=1.70
slab(tx,td,.721,.77,.71,.037,'formica')
for a in [-.31,.31]:
    for b in [-.278,.278]:
        rod((tx+a,td+b,.017),(tx+a*.90,td+b*.90,.705),.014,'duct')
        rod((tx+a,td+b,0),(tx+a,td+b,.027),.017,'knob')
for j in [-.25,.25]:slab(tx,td+j,.667,.62,.022,.065,'timber')
bowlstack(tx-.13,td+.025,.741,1)
for j in [0,1]:
    rod((tx+.026+j*.014,td-.20,.746),(tx+.235+j*.011,td-.053,.752),.0035,'bamboo',7)
# Tapered low stool at the side wall; the entrance and the path to the rear stay clear.
sx=1.67;dd=.81
def stool(x,y,h,col):
    tapered(x,y,h-.042,[(.34,.255,0),(.358,.267,.013),(.342,.257,.039)],col)
    for a in [-1,1]:
        for b in [-1,1]:
            rod((x+a*.162,y+b*.12,.007),(x+a*.127,y+b*.086,h-.032),.018,col)
        rod((x+a*.146,y-.111,.124),(x+a*.146,y+.111,.124),.010,col)
stool(sx,dd,.342,'stoolgreen')
# Painted guides sit in the old jambs. Folded shutter, stop beads and motor conduit terminate at the door head.
for sg in [-1,1]:
    slab(sg*2.198,.018,1.23,.049,.07,2.46,'duct')
    slab(sg*2.166,-.008,1.23,.017,.049,2.46,'stove')
for j in range(3):slab(0,.03,2.48+j*.044,4.36,.077,.035,'duct')
# Split-height tile splash and washable lower walls, with a coved junction to the floor.
for sg in [-1,1]:
    slab(sg*2.192,1.22,.605,.026,2.40,1.215,'dado')
    slab(sg*2.173,1.22,.066,.026,2.40,.129,'skirt')
    slab(sg*2.174,1.22,1.215,.025,2.4,.035,'oldtile')
# The masonry returns were repainted above the dado. A hung towel and stock lean toward the cook's side.
for sg in [-1,1]:
    slab(sg*2.195,1.22,1.849,.022,2.40,1.253,'noodleplaster')
rod((-2.168,.59,1.41),(-2.064,.59,1.41),.013,'duct')
rod((-2.168,1.01,1.41),(-2.064,1.01,1.41),.013,'duct')
rod((-2.064,.59,1.41),(-2.064,1.01,1.41),.012,'steel')
for side_sign,length in [(-1,.32),(1,.22)]:
    for i in range(12):
        for j in range(7):
            def cloth(i,j):
                u=i/12;v=j/7
                return world(-2.064+side_sign*(.014+.019*math.sin(u*math.tau*2.6+.4*v)+.012*v),.67+.24*u,1.429-v*(length+.020*math.sin(5*u)))
            points=[cloth(i,j),cloth(i+1,j),cloth(i+1,j+1),cloth(i,j+1)]
            face(name,points,'workrag');face(name,points[::-1],'workrag')
# Hand-washed enamel basin and reused oil jug below the service counter's return.
lathe(-1.73,1.53,.004,[(.112,0),(.142,.02),(.204,.135),(.21,.145),(.201,.15),(.178,.107),(.12,.012)],'oldtile',40)
ring(-1.73,1.53,.144,.209,.006,'indigo')
tapered(-1.57,1.92,0,[(.22,.16,0),(.23,.17,.06),(.23,.17,.24),(.14,.12,.30)],'oiljug')
lathe(-1.57,1.92,.298,[(.039,0),(.036,.032),(.032,.047)],'wine')
# Goose-neck wall tap and a fixed gas pipe return into the splashback.
for i in (0,1):
    d=.47+i*.42;slab(-2.153,d,1.183,.070,.055,.14,'duct')
rod((-2.108,.46,1.183),(-2.108,.90,1.183),.012,'duct')
rod((-2.108,.90,1.183),(-2.108,.90,.71),.012,'duct')
# Worn timber chopping board joins the pot, sloping toward the clean pickup end.
slab(-.966,1.37,.680,.61,.31,.044,'bamboo')
for a in [-.26,.26]:
    for b in [-.11,.11]:rod((-.966+a,1.37+b,0),(-.966+a,1.37+b,.66),.015,'duct')
# Remove the old apron floor exactly under the new wearing surface. The new surface and inset share a level.
floor_ring=[world(l,d,0).xy for l,d in [(-2.168,.012),(2.168,.012),(2.168,old+.02),(-2.168,old+.02)]]
for ob in list(scene.objects):
    if ob.type=='MESH' and ob.name.startswith(('COL_IR_B_A01_noodle_Shop_envelope_pavement','IR_B_A01_noodle_Interiors_room_floor','COL_B_A01_noodle_pavement')):
        solid_clip(ob,[(floor_ring,world(0,0,-.072).z,world(0,0,.010).z)])
part('COL_D18_NoodleEntry',0,(old+.032)*.5,-.03,4.338,old+.008,.06,'kitchenfloor')
