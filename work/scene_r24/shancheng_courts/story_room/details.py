"""Window-pier stand, desk lamp, compact radio and stock above the shelves."""
from math import sin,cos,tau
from mathutils import Vector

def stand(g,x,y,m):
    # Curved legs bow outward from a narrow neck supporting the square top.
    for s in (-1,1):
        for t in (-1,1):
            points=[(x+s*w,y+t*d,h) for w,d,h in ((.17,.14,.004),(.16,.128,.15),(.106,.092,.54),(.112,.10,.77),(.156,.13,.923))]
            for j,(a,b) in enumerate(zip(points,points[1:])):
                g.tube(a,b,(.023,.025,.025,.030)[j],m['walnut'],sides=6)
    g.board(x,y,.905,.365,.321,.028,m['wood'],.006)
    g.board(x,y,.232,.257,.218,.019,m['wood'])
    return .933

def cloth(g,x,y,z,w,d,m):
    pts=[]
    for i in range(32):
        # Sample a rectangle by side for a softly rippled overhanging textile.
        side,j=divmod(i,8);t=j/8
        u,v=((-.5+t,-.5),(.5,-.5+t),(.5-t,.5),(-.5,.5-t))[side]
        pts.append((x+u*w,y+v*d,z+.0032+.0005*sin(i*1.3)))
    centre=(x,y,z+.0035)
    for i,p in enumerate(pts):
        q=pts[(i+1)%len(pts)]
        g.face([centre,p,q],m['cloth'])
        def hem(a,j):return (x+(a[0]-x)*1.035,y+(a[1]-y)*1.036,z-.037-.014*cos(j*1.35))
        a,b=hem(p,i),hem(q,i+1)
        g.face([q,p,a,b],m['cloth'])
        for j in range(2):
            v=Vector(a).lerp(Vector(b),j/2)
            g.tube(v,v+Vector((.001,.001,-.010)),.0009,m['cloth'],sides=5)

def lamp(g,x,y,z,m):
    g.turn(x,y,z,[(0,.069),(.013,.075),(.028,.052),(.035,.033)],m['green'])
    a=(x,y,z+.032)
    for b in ((x,y,z+.205),(x-.014,y-.009,z+.265),(x-.049,y-.025,z+.295),(x-.071,y-.04,z+.286)):
        g.tube(a,b,.006,m['black']);a=b
    g.tube(a,(x-.105,y-.055,z+.246),.023,m['green'],.067,24)
    g.tube((x-.105,y-.055,z+.246),(x-.106,y-.055,z+.245),.060,m['paper'],sides=24)

def small_radio(g,x,y,z,m):
    # Low oval portable set at the near end of the window desk in the press photograph.
    for t in (-1,1):g.tube((x+t*.082,y,z+.051),(x+t*.082,y,z+.102),.057,m['enamel'],sides=24)
    g.board(x,y,z+.014,.218,.111,.088,m['enamel'],.020)
    g.board(x,y,z+.094,.157,.107,.015,m['black'],.009)
    for s in (-1,1):
        g.tube((x+s*.067,y-.055,z+.056),(x+s*.067,y-.059,z+.056),.034,m['black'],sides=24)
        g.board(x+s*.082,y+.011,z+.105,.009,.012,.061,m['black'])
    g.board(x,y+.011,z+.159,.171,.012,.009,m['black'])
    g.board(x,y-.058,z+.047,.037,.005,.021,m['steel'])

def earthenware(g,x,y,z,m):
    g.turn(x,y,z,[(0,.039),(.013,.050),(.085,.052),(.096,.054)],m['enamel'])
    g.tube((x,y,z+.095),(x,y,z+.097),.046,m['black'],sides=20)
    for a,b in (((.047,.075),(.079,.076)),((.079,.076),(.082,.035)),((.082,.035),(.048,.026))):
        g.tube((x+a[0],y,z+a[1]),(x+b[0],y,z+b[1]),.006,m['enamel'])
