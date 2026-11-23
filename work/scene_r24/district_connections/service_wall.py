# A compact wall fan above the dining place. The motor bracket and cable terminate on the return.
from mathutils import Quaternion
fx=2.015;fd=1.16;fz=1.99
axis=Vector((-.90,.27,-.18)).normalized();ey=Vector((0,0,1)).cross(axis).normalized();ez=axis.cross(ey)
def fanpoint(radius,theta,along):
    p=Vector((fx,fd,fz))+axis*along+ey*(radius*math.cos(theta))+ez*(radius*math.sin(theta))
    return tuple(p)
def wire_circle(radius,along,gauge,matname):
    for j in range(36):
        rod(fanpoint(radius,j*math.tau/36,along),fanpoint(radius,(j+1)*math.tau/36,along),gauge,matname,5)
slab(2.151,fd,fz-.02,.092,.122,.22,'skirt')
rod((2.155,fd,fz-.03),(fx,fd,fz),.039,'duct')
rod(fanpoint(0,0,-.054),fanpoint(0,0,.034),.066,'stoolgreen',21)
for along in [-.010,.087]:wire_circle(.203,along,.005,'duct')
for r in [.055,.103,.15,.19]:wire_circle(r,.1+(1-r/.20)*.02,.0024,'steel')
for j in range(24):
    a=math.tau*j/24
    rod(fanpoint(.035,a,.123),fanpoint(.20,a,.087),.0026,'steel',6)
    rod(fanpoint(.20,a,.087),fanpoint(.203,a,-.01),.0027,'steel',6)
for j in range(4):
    a=math.tau*j/4
    blade=[world(*fanpoint(r,a+off,along)) for r,off,along in [(.031,0,.035),(.155,-.42,.039),(.183,-.35,.035),(.178,.08,.051),(.125,.43,.066),(.037,.42,.042)]]
    face(name,blade,'stoolgreen');face(name,blade[::-1],'stoolgreen')
rod(fanpoint(0,0,.10),fanpoint(0,0,.132),.039,'knob',21)
for a,b in [((2.146,fd,1.91),(2.166,fd+.03,1.71)),((2.166,fd+.03,1.71),(2.171,fd+.18,1.56)),((2.171,fd+.18,1.56),(2.171,fd+.31,1.64))]:rod(a,b,.004,'knob',7)
slab(2.172,fd+.32,1.65,.030,.076,.089,'oldtile')
# One well-used insulated flask for the dining table and a blue-rimmed mug. The handle sits clear of the wall.
x=1.54;d=1.88;z=.740
lathe(x,d,z,[(.052,0),(.065,.014),(.072,.057),(.073,.222),(.065,.242),(.043,.267),(.039,.277)],'flask',32)
ring(x,d,z+.027,.071,.004,'duct');ring(x,d,z+.224,.070,.004,'duct')
lathe(x,d,z+.274,[(.036,0),(.048,.009),(.049,.037),(.043,.044)],'knob')
for a,b in [((x+.068,d,z+.19),(x+.104,d,z+.205)),((x+.104,d,z+.205),(x+.108,d,z+.067)),((x+.108,d,z+.067),(x+.069,d,z+.065))]:rod(a,b,.006,'knob')
lathe(x-.168,d,z,[(.032,0),(.042,.009),(.049,.083),(.044,.086),(.039,.018)],'oldtile',24)
ring(x-.168,d,z+.08,.049,.003,'indigo')
# The landlord's paper note is taped flat to this particular wall at customer height.
# It has its own UV and readable, authored Chinese type.
pp=[world(2.161,d,zz) for d,zz in [(1.67,1.456),(1.99,1.456),(1.99,1.648),(1.67,1.648)]]
new='D18_SoupNotice';face(new,pp,'rice');face(new,pp[::-1],'rice')
for idx,coords in [(0,[(1,0),(0,0),(0,1),(1,1)]),(1,[(1,1),(0,1),(0,0),(1,0)])]:metric_uv[(new,idx)]=coords
for d in [1.69,1.97]:slab(2.159,d,1.636,.003,.049,.017,'paintcream')
