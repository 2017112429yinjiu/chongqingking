"""Original small, readable domestic interiors for district revision 14.

These are authored metre-scale meshes, not downloaded assets or image cards.
The module has no Blender dependency: it writes into the facade's existing
material batches and can be checked for geometry cost before the heavy build.
The silhouettes are deliberately constructed from their real components:
thin books with separate page blocks, hollow pottery, tapered furniture legs,
chair backs, shaped cushions, and lamp shades. No solid placeholder contents.
"""
import math
import random


def _sub(a, b): return tuple(x-y for x, y in zip(a, b))
def _add(a, b): return tuple(x+y for x, y in zip(a, b))
def _mul(a, s): return tuple(x*s for x in a)
def _dot(a, b): return sum(x*y for x, y in zip(a, b))
def _cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def _norm(a):
    d=math.sqrt(_dot(a, a))
    return _mul(a, 1/d) if d > 1e-9 else (0, 0, 1)


class Place:
    """Lightweight local placement, allowing chairs and books to turn/lean."""
    def __init__(self, frame, origin=(0, 0, 0), yaw=0, lean=0):
        self.f=frame; self.o=origin
        cy, sy=math.cos(yaw), math.sin(yaw)
        cl, sl=math.cos(lean), math.sin(lean)
        self.axes=((cy*cl, sy*cl, -sl), (-sy, cy, 0), (cy*sl, sy*sl, cl))

    def transform(self, p):
        return tuple(self.o[j]+sum(self.axes[i][j]*p[i] for i in range(3)) for j in range(3))

    def mesh(self, vs, fs, mat, smooth=False):
        self.f.mesh([self.transform(p) for p in vs], fs, mat, smooth)

    def quad(self, a, b, c, d, mat): self.mesh([a, b, c, d], [(0, 1, 2, 3)], mat)

    def cylinder(self, a, b, r, mat, segments=8, r2=None):
        self.f.cylinder(self.transform(a), self.transform(b), r, mat, segments, r2)

    def box(self, p, size, mat):
        x,y,z=p; a,b,c=[s/2 for s in size]
        self.mesh([(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
                   (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)],
                  [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)


def floor_leg(f,a,b,r,mat,segments=8,r2=None,*,floor):
    """Extend a known floor support to its floor without moving its furniture.

    Retain the original cylinder's complete XY footprint and upper ring.
    Only the lower ring is extended vertically and cut to a horizontal sole.
    Unwrap yaw placements exactly as Place.cylinder does before constructing
    the rings, preserving the old vertex orientation even for rotated chairs.
    """
    while isinstance(f,Place):
        if abs(f.axes[0][2])+abs(f.axes[1][2])+abs(f.axes[2][2]-1)>1.e-10:
            raise ValueError('A floor support needs a horizontal floor placement')
        a,b=f.transform(a),f.transform(b)
        floor=f.transform((0,0,floor))[2];f=f.f
    n=_norm(_sub(b,a));aux=(0,0,1) if abs(n[2])<.9 else (1,0,0)
    u=_norm(_cross(n,aux));v=_cross(n,u);vs=[]
    for ring,(p,rr) in enumerate([(a,r),(b,r if r2 is None else r2)]):
        for i in range(segments):
            theta=2*math.pi*i/segments
            point=_add(p,_mul(_add(_mul(u,math.cos(theta)),_mul(v,math.sin(theta))),rr))
            vs.append((point[0],point[1],floor) if ring==0 else point)
    fs=[tuple(reversed(range(segments))),tuple(range(segments,2*segments))]+[
        (i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
    f.mesh(vs,fs,mat,True)


def bevel(f, p, size, mat, radius=.012):
    """A genuine 26-face bevelled solid, 44 triangles, no modifier required."""
    h=[v/2 for v in size]; r=min(radius, min(h)*.72)
    inset=[v-r for v in h]; vs=[]; fs=[]
    def face(points):
        c=tuple(sum(q[i] for q in points)/len(points) for i in range(3))
        n=_cross(_sub(points[1],points[0]),_sub(points[2],points[0]))
        if _dot(c,n)<0:points=list(reversed(points))
        start=len(vs); vs.extend(_add(p,q) for q in points)
        fs.append(tuple(range(start,start+len(points))))
    for axis in range(3):
        a,b=[j for j in range(3) if j!=axis]
        for s in [-1,1]:
            pts=[]
            for sa,sb in [(-1,-1),(1,-1),(1,1),(-1,1)]:
                q=[0,0,0];q[axis]=s*h[axis];q[a]=sa*inset[a];q[b]=sb*inset[b];pts.append(tuple(q))
            face(pts)
    for a,b in [(0,1),(0,2),(1,2)]:
        c=3-a-b
        for sa in [-1,1]:
            for sb in [-1,1]:
                pts=[]
                for t,which in [(-1,0),(1,0),(1,1),(-1,1)]:
                    q=[0,0,0];q[c]=t*inset[c]
                    q[a]=sa*(h[a] if which==0 else inset[a]);q[b]=sb*(inset[b] if which==0 else h[b]);pts.append(tuple(q))
                face(pts)
    for sx in [-1,1]:
        for sy in [-1,1]:
            for sz in [-1,1]:
                signs=(sx,sy,sz);pts=[]
                for axis in range(3):pts.append(tuple(signs[j]*(h[j] if j==axis else inset[j]) for j in range(3)))
                face(pts)
    f.mesh(vs,fs,mat)


def lathe(f, p, profile, mat, sides=14):
    """Closed or open turned profile; zero radii are single, nondegenerate tips."""
    vs=[]; rings=[];fs=[]
    for radius,z in profile:
        if radius<1e-7:
            rings.append([len(vs)]);vs.append((p[0],p[1],p[2]+z))
        else:
            ids=[]
            for k in range(sides):
                angle=k*math.tau/sides;ids.append(len(vs))
                vs.append((p[0]+radius*math.cos(angle),p[1]+radius*math.sin(angle),p[2]+z))
            rings.append(ids)
    for a,b in zip(rings,rings[1:]):
        if len(a)==1 and len(b)==1:continue
        for k in range(sides):
            j=(k+1)%sides
            fs.append((a[0],b[j],b[k]) if len(a)==1 else ((a[k],a[j],b[0]) if len(b)==1 else (a[k],a[j],b[j],b[k])))
    f.mesh(vs,fs,mat,True)


def tube(f, points, radius, mat, sides=5, closed=False, reference=(0,1,0)):
    """One swept tube, instead of disconnected capped cylinders at each bend."""
    if len(points)<2:return
    vs=[];fs=[];n=len(points)
    for i,p in enumerate(points):
        a=points[(i-1)%n] if closed or i else points[i]
        b=points[(i+1)%n] if closed or i<n-1 else points[i]
        t=_norm(_sub(b,a));u=_norm(_cross(t,reference));v=_cross(t,u)
        for k in range(sides):
            angle=k*math.tau/sides
            vs.append(_add(p,_mul(_add(_mul(u,math.cos(angle)),_mul(v,math.sin(angle))),radius)))
    for i in range(n if closed else n-1):
        j=(i+1)%n
        for k in range(sides):fs.append((i*sides+k,i*sides+(k+1)%sides,j*sides+(k+1)%sides,j*sides+k))
    if not closed:fs.extend([tuple(reversed(range(sides))),tuple(range((n-1)*sides,n*sides))])
    f.mesh(vs,fs,mat,True)


def cushion(f,p,size,mat,detail=1,seed=0):
    """Soft sewn cushion with a pinched seam and uneven top, not a cuboid."""
    w,d,h=size;r=min(w,d)*.20;steps=3 if detail>1 else 2
    outline=[]
    for cx,cy,start in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
        for j in range(steps+1):
            a=math.radians(start+j*90/steps);outline.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
    vs=[];fs=[];n=len(outline)
    for row,(sz,scale) in enumerate([(-.45,.80),(-.12,1.0),(.18,1.01),(.48,.82)]):
        for i,(x,y) in enumerate(outline):
            irregular=(.018*math.sin(i*2.1+seed) if row==3 else 0)
            vs.append((p[0]+x*scale,p[1]+y*scale,p[2]+h*sz+irregular))
    fs.append(tuple(reversed(range(n))))
    for row in range(3):
        for k in range(n):fs.append((row*n+k,row*n+(k+1)%n,(row+1)*n+(k+1)%n,(row+1)*n+k))
    # A shallow centre bulge avoids the flat polygonal top of the old cushions.
    top=len(vs);vs.append((p[0]+w*.025,p[1]-d*.03,p[2]+h*.58))
    for k in range(n):fs.append((3*n+k,3*n+(k+1)%n,top))
    f.mesh(vs,fs,mat,True)
    if detail>1:
        seam=[(p[0]+x*.99,p[1]+y*.99,p[2]-.02*h) for x,y in outline]
        tube(f,seam,.0025,'curtain_linen',4,True,(0,0,1))


def vessel(f,p,r=.075,h=.16,mat='ceramic_glaze',detail=1,kind='cup'):
    """Open ceramic cup, jar or bowl with lip thickness and a visible interior."""
    sides=14 if detail>1 else (10 if detail else 8)
    if kind=='bowl':
        prof=[(0,0),(r*.40,0),(r*.47,h*.18),(r,h*.90),(r*.98,h),(r*.87,h*.93),(r*.38,h*.22),(0,h*.22)]
    elif kind=='pot':
        prof=[(0,0),(r*.68,0),(r*.78,h*.09),(r*.94,h*.83),(r,h*.86),(r,h),(r*.84,h),(r*.76,h*.19),(0,h*.19)]
    else:
        prof=[(0,0),(r*.82,0),(r,h*.08),(r,h*.94),(r*.96,h),(r*.80,h*.96),(r*.79,h*.18),(0,h*.18)]
    lathe(f,p,prof,mat,sides)
    if kind=='cup' and detail>0:
        points=[]
        for k in range(8):
            a=-math.pi/2+math.pi*k/7
            points.append((p[0]+r*.93+math.cos(a)*r*.60,p[1],p[2]+h*.53+math.sin(a)*h*.30))
        tube(f,points,.010 if detail>1 else .012,mat,5)


def bottle(f,p,h=.28,r=.062,mat='faded_green',detail=1):
    lathe(f,p,[(0,0),(r*.77,0),(r,.035),(r,h*.66),(r*.40,h*.81),(r*.38,h*.96),(r*.43,h),(0,h)],mat,12 if detail>1 else 8)
    if detail:
        lathe(f,(p[0],p[1],p[2]+h*.28),[(r*1.006,0),(r*1.006,h*.25)],'paper',12 if detail>1 else 8)
        lathe(f,(p[0],p[1],p[2]+h*.96),[(0,0),(r*.44,0),(r*.44,.018),(0,.018)],'aluminium',8)


def plant(f,p,scale=.33,detail=1,seed=0):
    rng=random.Random(seed+5049);r=scale*.28;h=scale*.55
    vessel(f,p,r,h,'ceramic_glaze',detail,'pot')
    lathe(f,(p[0],p[1],p[2]+h*.84),[(0,0),(r*.78,0)],'soil_dark',10 if detail else 8)
    count=6 if detail>1 else (4 if detail else 3)
    for k in range(count):
        angle=k*2.4+rng.uniform(-.2,.2);length=scale*rng.uniform(.65,1.02)
        start=(p[0],p[1],p[2]+h*.88);tip=(p[0]+math.cos(angle)*length*.65,p[1]+math.sin(angle)*length*.65,p[2]+h+length*.55)
        mid=tuple((a+b)/2 for a,b in zip(start,tip));mid=(mid[0],mid[1],mid[2]+length*.16)
        if detail:f.cylinder(start,mid,.0045,'leaf_olive',5)
        tangent=(-math.sin(angle),math.cos(angle),0);width=length*.20
        ridge=_add(mid,(0,0,length*.07));left=_add(mid,_mul(tangent,width));right=_add(mid,_mul(tangent,-width))
        verts=[start,left,ridge,right,tip]
        faces=[(0,1,2),(0,2,3),(1,4,2),(2,4,3)]
        f.mesh(verts,faces+[tuple(reversed(a)) for a in faces],'leaf_olive',True)


def book(f,p,thickness=.04,depth=.20,height=.28,mat='faded_red',detail=1,lean=0):
    q=Place(f,p,lean=lean);t=thickness/2;d=depth/2
    # Paper remains visible at the top/fore-edge. Covers extend beyond it.
    q.box((0,-.003,height/2),(thickness-.006,depth-.014,height-.014),'paper')
    q.mesh([(-t,-d,0),(-t,d-.006,0),(-t,d-.006,height),(-t,-d,height),
            (t,-d,0),(t,d-.006,0),(t,d-.006,height),(t,-d,height)],
           [(0,3,2,1),(4,5,6,7),(3,7,6,2),(0,1,5,4)],mat)
    # Bowed spine catches a thin highlight from the window.
    vs=[]
    for zz in [0,height]:
        for j in range(4):
            x=-t+thickness*j/3;vs.append((x,d+.004*math.sin(j*math.pi/3),zz))
    q.mesh(vs,[(j,j+4,j+5,j+1) for j in range(3)],mat,True)
    if detail:
        for zz in [height*.15,height*.82]:
            q.quad((-t*.72,d+.005,zz),(-t*.72,d+.005,zz+.006),(t*.72,d+.005,zz+.006),(t*.72,d+.005,zz),'sign_cream')
        if detail>1:q.quad((-t*.55,d+.006,height*.50),(-t*.55,d+.006,height*.65),(t*.55,d+.006,height*.65),(t*.55,d+.006,height*.50),'paper')


def books(f,x,y,z,width,detail=1,seed=0):
    rng=random.Random(seed+772);count=8 if detail>1 else (5 if detail else 3)
    colors=['faded_green','faded_red','electric_blue','timber','curtain_beige']
    widths=[rng.uniform(.026,.060) for _ in range(count)];total=sum(widths)+.008*(count-1)
    xx=x-min(width*.82,total)/2
    for k,t in enumerate(widths):
        hh=rng.uniform(.23,.36);lean=(.10 if k==count-1 else (-.045 if k==0 else 0)) if detail else 0
        book(f,(xx+t/2,y,z),t,rng.uniform(.16,.225),hh,colors[(k+seed)%len(colors)],detail,lean)
        xx+=t+.008


def shelf(f,p,width,detail=1,mat='timber'):
    # A real board and visible brackets, not a solid cabinet block.
    if detail:bevel(f,p,(width,.25,.035),mat,.006)
    else:f.box(p,(width,.25,.035),mat)
    if detail>1:
        for xx in [p[0]-width*.33,p[0]+width*.33]:
            tube(f,[(xx,p[1]-.20,p[2]-.18),(xx,p[1]-.20,p[2]-.025),(xx,p[1]+.08,p[2]-.025)],.010,'frame',5)


def lamp(f,p,height=.63,detail=1,lit=False):
    sides=14 if detail>1 else 9
    r=.15 if height<1 else .19
    lathe(f,p,[(0,0),(r*.63,0),(r*.71,.025),(r*.61,.045),(0,.045)],'ceramic_glaze' if height<1 else 'frame',sides)
    f.cylinder((p[0],p[1],p[2]+.035),(p[0],p[1],p[2]+height-.18),.014,'timber' if height<1 else 'frame',6)
    shade_bottom=p[2]+height-.24
    # Open tapered linen shade with a pale interior, dark rim and separate bulb.
    lathe(f,(p[0],p[1],shade_bottom),[(r,0),(r*.57,.24)],'curtain_beige',sides)
    lathe(f,(p[0],p[1],shade_bottom),[(r*.53,.237),(r*.95,.004)],'offwhite',sides)
    ring=[(p[0]+math.cos(i*math.tau/sides)*r,p[1]+math.sin(i*math.tau/sides)*r,shade_bottom+.005) for i in range(sides)]
    tube(f,ring,.006,'timber',4,True,(0,0,1))
    bulb=(p[0],p[1],shade_bottom+.075)
    lathe(f,bulb,[(0,-.035),(.027,-.025),(.035,0),(.020,.037),(0,.042)],'light_warm' if lit else 'offwhite',8)
    return bulb


def stool(f,p,r=.18,height=.43,detail=1):
    lathe(f,(p[0],p[1],p[2]+height),[(0,-.04),(r*.96,-.04),(r,-.025),(r,.005),(r*.93,.014),(0,.014)],'timber',12 if detail>1 else 8)
    for k in range(3):
        a=k*math.tau/3
        low=(p[0]+math.cos(a)*r*.91,p[1]+math.sin(a)*r*.91,p[2]+.025)
        high=(p[0]+math.cos(a)*r*.66,p[1]+math.sin(a)*r*.66,p[2]+height-.03)
        floor_leg(f,low,high,.021,'timber',6,r2=.025,floor=p[2])


def chair(f,p,detail=1,yaw=0):
    q=Place(f,p,yaw=yaw)
    bevel(q,(0,0,.455),(.38,.37,.045),'timber',.016)
    for sx in [-1,1]:
        for sy in [-1,1]:floor_leg(q,(sx*.17,sy*.17,.025),(sx*.145,sy*.145,.445),.018,'timber',5,r2=.024,floor=0.)
    # Curved horseshoe back and slender uprights visibly separate from the seat.
    back=[(-.165,-.135,.455),(-.185,-.16,.82),(-.135,-.175,.94),(0,-.185,.98),(.135,-.175,.94),(.185,-.16,.82),(.165,-.135,.455)]
    tube(q,back,.021,'timber',5)
    if detail:
        for xx in [-.09,0,.09]:q.cylinder((xx,-.155,.49),(xx,-.178,.92),.009,'timber',5)
        q.cylinder((-.155,.14,.23),(.155,.14,.23),.012,'timber',5)


def round_table(f,p,r=.34,height=.77,detail=1):
    sides=18 if detail>1 else 10
    lathe(f,(p[0],p[1],p[2]+height),[(0,-.045),(r*.96,-.045),(r,-.031),(r,-.003),(r*.97,.006),(0,.006)],'timber',sides)
    # Three splayed legs and an apron leave genuine under-table space.
    lathe(f,(p[0],p[1],p[2]+height-.095),[(r*.78,0),(r*.78,.055)],'wood',sides)
    for k in range(3):
        a=k*math.tau/3+.32
        floor_leg(f,(p[0]+math.cos(a)*r*.76,p[1]+math.sin(a)*r*.76,p[2]+.025),
                   (p[0]+math.cos(a)*r*.61,p[1]+math.sin(a)*r*.61,p[2]+height-.06),.022,'timber',5,r2=.028,floor=p[2])


def sideboard(f,p,width=.72,height=.78,detail=1):
    x,y,z=p;d=.37
    # Raised plinth, thin carcass sides, recessed doors and separate handles.
    for xx in [x-width*.38,x+width*.38]:
        for yy in [y-d*.33,y+d*.33]:floor_leg(f,(xx,yy,z+.015),(xx,yy,z+.16),.018,'timber',5,r2=.026,floor=z)
    bevel(f,(x,y,z+height-.035),(width+.045,d+.04,.07),'timber',.010)
    for xx in [x-width/2+.02,x+width/2-.02]:bevel(f,(xx,y,z+height*.52),(.04,d,height-.18),'timber',.006)
    bevel(f,(x,y-d/2+.015,z+height*.52),(width,.03,height-.18),'wood',.004)
    for sign in [-1,1]:
        xx=x+sign*width*.25
        bevel(f,(xx,y+d/2-.014,z+height*.52),(width*.48,.028,height-.20),'timber',.007)
        if detail:
            f.cylinder((x+sign*.048,y+d/2+.01,z+height*.55),(x+sign*.048,y+d/2+.045,z+height*.55),.014,'rust',6)


def picture(f,p,width=.37,height=.44,detail=1,seed=0):
    x,y,z=p
    # Mat, thin moulded timber frame and quiet, original abstract botanical print.
    f.quad((x-width/2,y,z-height/2),(x-width/2,y,z+height/2),(x+width/2,y,z+height/2),(x+width/2,y,z-height/2),'paper')
    for xx in [x-width/2-.012,x+width/2+.012]:bevel(f,(xx,y+.008,z),(.025,.03,height+.05),'timber',.004)
    for zz in [z-height/2-.012,z+height/2+.012]:bevel(f,(x,y+.008,zz),(width+.05,.03,.025),'timber',.004)
    if detail:
        f.cylinder((x,y+.012,z-height*.27),(x+width*.10,y+.012,z+height*.24),.004,'leaf_olive',4)
        for k in range(3):
            zz=z-height*.15+k*height*.12;side=-1 if k%2 else 1
            f.mesh([(x,y+.014,zz),(x+side*width*.20,y+.014,zz+height*.04),(x+side*width*.13,y+.014,zz+height*.13)],[(0,2,1)],'leaf_olive')


def _cabinet_scene(f,u,floor,w,depth,detail,seed,lit,assets=None):
    x=u+w*.12;y=-depth+.27;width=min(.85,w*.72)
    sideboard(f,(x,y,floor),width,.86,detail)
    if assets is not None:assets.append({'asset':'potted_plant_02','position':(x-width*.27,y+.05,.90+floor),'height':.43,'yaw':seed*.73,'lod':'low'})
    else:plant(f,(x-width*.27,y,.90+floor),.29,detail,seed)
    bottle(f,(x+width*.24,y,floor+.90),.31,.073,'faded_red',detail)
    shelf(f,(u-w*.09,-depth+.16,floor+1.56),w*.72,detail)
    vessel(f,(u-w*.22,-depth+.18,floor+1.58),.075,.16,'ceramic_glaze',detail,'cup')
    vessel(f,(u-w*.06,-depth+.18,floor+1.58),.085,.11,'ceramic_glaze',detail,'bowl')
    if detail:books(f,u+w*.20,-depth+.15,floor+1.58,w*.25,0,seed)
    return None


def _economy_room(f,u,floor,w,depth,seed,detail,kind):
    """Distant rooms retain component silhouettes at roughly 100–350 tris.

    This is a geometry allocation based on street height, not an opaque pane
    or a texture-card replacement. Small labels, seams and hidden chair parts
    are absent, while legs, thin pages, pottery rims and lamp shapes remain.
    """
    sy=-depth+.18
    def small_pot(x,y,z,r=.07,hh=.18,mat='ceramic_glaze'):
        lathe(f,(x,y,z),[(0,0),(r*.63,0),(r,hh*.76),(r*.77,hh),(r*.58,hh*.93),(0,hh*.26)],mat,6)
    def small_plant(x,y,z):
        small_pot(x,y,z,.075,.13)
        for k in range(3 if detail==0 else 4):
            a=k*2.4;tip=(x+math.cos(a)*.13,y+math.sin(a)*.13,z+.34)
            mid=(x+math.cos(a)*.065,y+math.sin(a)*.065,z+.29)
            tangent=(-math.sin(a)*.038,math.cos(a)*.038,0)
            verts=[(x,y,z+.12),_add(mid,tangent),_add(mid,(0,0,.018)),_sub(mid,tangent),tip]
            fs=[(0,1,2),(0,2,3),(1,4,2),(2,4,3)]
            f.mesh(verts,fs+[tuple(reversed(q)) for q in fs],'leaf_olive',True)
    def small_lamp(x,y,z,hh):
        lathe(f,(x,y,z),[(0,0),(.085,0),(.085,.025),(0,.025)],'timber',6)
        f.cylinder((x,y,z+.02),(x,y,z+hh-.12),.012,'frame',4)
        lathe(f,(x,y,z+hh-.22),[(.13,0),(.075,.22)],'curtain_beige',7)
        lathe(f,(x,y,z+hh-.22),[(.070,.215),(.125,.004)],'offwhite',7)
    def slab(x,y,z,ww,dd=.24,hh=.032):f.box((x,y,z),(ww,dd,hh),'timber')
    def small_chair(x,y,z):
        lathe(f,(x,y,z+.45),[(0,-.025),(.18,-.025),(.18,.015),(0,.015)],'timber',7)
        for sx in [-1,1]:
            for sy2 in [-1,1]:floor_leg(f,(x+sx*.15,y+sy2*.15,z+.025),(x+sx*.13,y+sy2*.13,z+.44),.019,'timber',4,floor=z)
        tube(f,[(x-.15,y-.13,z+.45),(x-.18,y-.17,z+.86),(x,y-.18,z+.95),(x+.18,y-.17,z+.86),(x+.15,y-.13,z+.45)],.021,'timber',4)
    if kind==0:
        dw=min(w*.71,.96);tx=u-w*.07;ty=-depth+.42
        slab(tx,ty,floor+.76,dw,.44,.045)
        for sx in [-1,1]:
            for yy in [ty-.15,ty+.15]:floor_leg(f,(tx+sx*dw*.39,yy,floor+.03),(tx+sx*dw*.38,yy,floor+.74),.02,'timber',4,floor=floor)
        small_lamp(tx-dw*.25,ty,floor+.79,.67)
        slab(u,sy,floor+1.65,w*.70)
        books(f,u,sy,floor+1.67,w*.58,0,seed)
        if detail:small_chair(u+w*.24,ty+.31,floor)
    elif kind==1:
        small_chair(u-w*.15,-depth+.41,floor)
        small_lamp(u+w*.27,-depth+.39,floor,1.69)
        if detail:
            slab(u-w*.17,sy,floor+1.66,w*.49)
            books(f,u-w*.17,sy,floor+1.68,w*.42,0,seed)
    elif kind==2:
        tx=u-w*.11;ty=-depth+.65;r=min(.33,w*.25)
        lathe(f,(tx,ty,floor+.77),[(0,-.035),(r,-.035),(r,.005),(0,.005)],'timber',8)
        for k in range(3):
            a=k*math.tau/3;floor_leg(f,(tx+math.cos(a)*r*.78,ty+math.sin(a)*r*.78,floor+.03),(tx+math.cos(a)*r*.60,ty+math.sin(a)*r*.60,floor+.74),.023,'timber',4,floor=floor)
        slab(u,sy,floor+1.62,w*.68)
        small_plant(u-w*.18,sy,floor+1.64)
        small_pot(u+w*.15,sy,floor+1.64,.060,.24,'faded_green')
        if detail:small_chair(u+w*.27,-depth+.35,floor)
    elif kind==3:
        bw=min(.75,w*.55);bx=u-w*.18;ty=-depth+.60
        cushion(f,(bx,ty,floor+.39),(bw,1.05,.17),'curtain_beige',0,seed)
        slab(bx,ty,floor+.25,bw,1.05,.12)
        for xx in [bx-bw*.40,bx+bw*.40]:floor_leg(f,(xx,ty+.42,floor+.02),(xx,ty+.42,floor+.25),.024,'timber',4,floor=floor)
        for zz in [.72,.94]:slab(bx,-depth+.16,floor+zz,bw,.04,.07)
        for sx in [-1,1]:floor_leg(f,(bx+sx*bw*.44,-depth+.16,floor+.06),(bx+sx*bw*.44,-depth+.16,floor+1.0),.024,'timber',4,floor=floor)
        tx=u+w*.29
        slab(tx,-depth+.33,floor+.65,.31,.31,.045)
        for xx in [tx-.115,tx+.115]:floor_leg(f,(xx,-depth+.33,floor+.03),(xx,-depth+.33,floor+.63),.018,'timber',4,floor=floor)
        small_lamp(tx,-depth+.33,floor+.68,.72)
        if detail:
            cushion(f,(bx,ty-.30,floor+.51),(bw*.72,.29,.14),'curtain_linen',0,seed)
            # One small framed artwork, thin enough to read as a wall object.
            f.box((u-w*.15,-depth+.015,floor+1.70),(.39,.025,.48),'timber')
            f.quad((u-w*.15-.17,-depth+.03,floor+1.49),(u-w*.15-.17,-depth+.03,floor+1.91),(u-w*.15+.17,-depth+.03,floor+1.91),(u-w*.15+.17,-depth+.03,floor+1.49),'paper')
    elif kind==4:
        ww=min(w*.70,.85);tx=u+w*.08
        slab(tx,-depth+.30,floor+.86,ww,.38,.045)
        for sx in [-1,1]:
            f.box((tx+sx*ww*.25,-depth+.14,floor+.52),(ww*.48,.026,.59),'timber')
            floor_leg(f,(tx+sx*ww*.36,-depth+.32,floor+.025),(tx+sx*ww*.36,-depth+.32,floor+.83),.021,'timber',4,floor=floor)
        small_plant(tx-ww*.24,-depth+.29,floor+.89)
        slab(u,sy,floor+1.57,w*.69)
        small_pot(u-w*.17,sy,floor+1.59,.07,.18)
        small_pot(u+w*.13,sy,floor+1.59,.055,.28,'faded_red')
        if detail:books(f,u+w*.25,sy,floor+1.59,w*.25,0,seed)
    elif kind==5:
        sw=min(w*.76,1.09)
        for xx in [u-sw/2+.018,u+sw/2-.018]:f.box((xx,sy-.015,floor+1.08),(.035,.20,2.08),'timber')
        for i,zz in enumerate([1.33,1.83]):
            slab(u,sy,floor+zz,sw)
            books(f,u+(-.10 if i else .05),sy,floor+zz+.025,sw*.75,0,seed+i*13)
        if detail:
            slab(u,sy,floor+.83,sw)
            small_plant(u-sw*.22,sy,floor+.85)
            small_pot(u+sw*.25,sy,floor+.85,.065,.15)
    else:
        lathe(f,(u,-depth+.32,floor+.91),[(0,0),(w*.13,0),(w*.28,.12),(w*.25,.14),(w*.11,.035),(0,.035)],'ceramic_glaze',7)
        floor_leg(f,(u,-depth+.32,floor+.12),(u,-depth+.32,floor+.91),.055,'offwhite',5,floor=floor)
        tube(f,[(u,-depth+.13,floor+1.04),(u,-depth+.13,floor+1.23),(u,-depth+.28,floor+1.23)],.012,'aluminium',4)
        f.box((u,-depth+.014,floor+1.63),(w*.61,.028,.48),'frame')
        f.quad((u-w*.27,-depth+.03,floor+1.42),(u-w*.27,-depth+.03,floor+1.84),(u+w*.27,-depth+.03,floor+1.84),(u+w*.27,-depth+.03,floor+1.42),'glass_blue')
    return {'kind':['study','reading_nook','dining','bedroom','kitchen_sideboard','bookshelf','utility'][kind],
            'lamp':None,'detail':detail,'floor_m':floor}


def _pierced_worktop(f,p,width,depth,hole_x,hole_radius,mat='timber'):
    """Thin real countertop with a circular opening, including the hole edge.

    A solid board passing through a vessel would conceal the bowl interior.
    Radial bands join its opening to the rectangular outer boundary instead.
    Corner ray angles keep the outer edges rectangular at metre scale.
    """
    x,y,z=p;thickness=.035;half_w=width/2;half_d=depth/2
    angles=[round(k*math.tau/28,10) for k in range(28)]
    angles.extend(round(math.atan2(cy,cx-hole_x)%math.tau,10) for cx in [-half_w,half_w] for cy in [-half_d,half_d])
    angles=sorted(set(angles));n=len(angles);inner=[];outer=[]
    for angle in angles:
        c,s=math.cos(angle),math.sin(angle);limits=[]
        if abs(c)>1e-8:limits.append(((half_w if c>0 else -half_w)-hole_x)/c)
        if abs(s)>1e-8:limits.append((half_d if s>0 else -half_d)/s)
        radius=min(limits)
        inner.append((x+hole_x+c*hole_radius,y+s*hole_radius,z))
        outer.append((x+hole_x+c*radius,y+s*radius,z))
    middle=[tuple((a[k]+b[k])/2 for k in range(3)) for a,b in zip(inner,outer)]
    bottom_inner=[(a,b,c-thickness) for a,b,c in inner]
    bottom_outer=[(a,b,c-thickness) for a,b,c in outer]
    vs=inner+middle+outer+bottom_inner+bottom_outer;fs=[]
    for i in range(n):
        j=(i+1)%n
        for row in range(2):fs.append((row*n+i,(row+1)*n+i,(row+1)*n+j,row*n+j))
        fs.extend([(3*n+i,3*n+j,4*n+j,4*n+i),
                   (2*n+i,4*n+i,4*n+j,2*n+j),
                   (i,j,3*n+j,3*n+i)])
    f.mesh(vs,fs,mat)


def _dish_towel(f,p,width=.25,length=.35,seed=0):
    """Two hanging cloth halves joined around a real narrow towel rail."""
    x,y,z=p
    tube(f,[(x-width*.66,y-.035,z-.025),(x-width*.66,y,z),
            (x+width*.66,y,z),(x+width*.66,y-.035,z-.025)],.008,'aluminium',5)
    profile=[(-.024,-length*.56),(-.022,-.07),(-.018,.004),(0,.024),(.020,.005),(.027,-.09),(.029,-length)]
    vs=[];fs=[];nx=8
    for j,(dy,dz) in enumerate(profile):
        for i in range(nx+1):
            t=i/nx;fold=.012*math.sin(t*math.tau*2.6+seed*.4)
            vs.append((x-width/2+t*width,y+dy+fold,z+dz+.010*math.sin(t*math.tau+seed)*(abs(dz)/length)))
    for j in range(len(profile)-1):
        for i in range(nx):
            a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
    f.mesh(vs,fs+[tuple(reversed(q)) for q in fs],'curtain_linen',True)
    for i in [0,nx]:tube(f,[vs[j*(nx+1)+i] for j in range(len(profile))],.0018,'curtain_beige',4)


def _dish_rack(f,p,width=.58):
    """Open draining rack: separate wire rails, standing plates and cups."""
    x,y,z=p;d=.25
    bevel(f,(x,y,z),(width+.025,d+.02,.020),'aluminium',.007)
    for sx in [-1,1]:
        xx=x+sx*(width/2-.025)
        tube(f,[(xx,y+d/2-.02,z+.01),(xx,y+d/2-.02,z+.13),
                (xx,y-d/2+.02,z+.13),(xx,y-d/2+.02,z+.01)],.006,'aluminium',5)
    for yy in [y-d/2+.02,y+d/2-.02]:
        for zz in [z+.035,z+.105]:f.cylinder((x-width/2+.02,yy,zz),(x+width/2-.02,yy,zz),.005,'aluminium',5)
    for i in range(6):
        xx=x-width*.39+i*width*.13
        f.cylinder((xx,y-d/2+.015,z+.018),(xx,y+d/2-.015,z+.018),.0045,'aluminium',4)
    for i in range(3):
        xx=x-width*.31+i*.068
        q=Place(f,(xx,y-.014,z+.108),yaw=.23,lean=math.pi/2-.04)
        lathe(q,(0,0,0),[(0,-.006),(.064,-.006),(.105,.008),(.109,.016),
                       (.103,.022),(.061,.008),(0,.008)],'ceramic_glaze',18)
        tube(f,[(xx-.012,y-.09,z+.02),(xx-.012,y-.085,z+.10),(xx+.015,y+.04,z+.10),
                (xx+.015,y+.07,z+.02)],.004,'aluminium',4)
    vessel(f,(x+width*.23,y+.01,z+.014),.044,.085,'ceramic_glaze',2,'cup')


def _compact_workroom(f,u,floor,width,depth,seed,draw_baseboard=True):
    """A usable wash/preparation room for a shallow, constrained window bay.

    The worktop remains 0.86 m above the real storey. There is no chair or
    dining table: the front of the room is the standing working space. Real
    openings, plumbing, dish storage and cloth establish its domestic use.
    """
    work_width=min(1.66,width-.20);work_depth=.60
    back=-depth;cy=back+.36;top=floor+.86;sink_x=u-work_width*.25
    wash=seed%2==0
    _pierced_worktop(f,(u,cy,top),work_width,work_depth,sink_x-u,.216,'timber')
    # Open timber base with proper joints: the plumbing is visible between
    # the legs, rather than concealed by a featureless cabinet volume.
    for sx in [-1,1]:
        xx=u+sx*(work_width/2-.055)
        for yy in [cy-.235,cy+.235]:
            bevel(f,(xx,yy,floor+.412),(.048,.048,.824),'timber',.006)
        bevel(f,(xx,cy,floor+.26),(.038,.49,.045),'timber',.005)
    for yy in [cy-.245,cy+.245]:
        bevel(f,(u,yy,top-.087),(work_width-.055,.036,.085),'timber',.005)
        bevel(f,(u,yy,floor+.23),(work_width-.055,.030,.045),'timber',.004)
    # A small lower slatted shelf supports a cleaning pail or spare bowls.
    for i in range(3):
        xx=u+work_width*.12+i*.105
        bevel(f,(xx,cy,floor+.275),(.096,.45,.024),'timber',.004)
    sink_mat='ceramic_glaze' if wash else 'aluminium'
    lathe(f,(sink_x,cy,top),[(0,-.171),(.094,-.171),(.140,-.147),(.196,-.062),
          (.213,-.008),(.230,-.004),(.234,.010),(.227,.018),(.207,.008),
          (.187,-.057),(.130,-.131),(.082,-.143),(0,-.143)],sink_mat,28)
    lathe(f,(sink_x,cy,top-.141),[(0,0),(.023,0),(.023,.003),(0,.003)],'frame',12)
    # Supply tap, curved spout, two control levers and an actual waste trap.
    tap_y=back+.105
    lathe(f,(sink_x,tap_y,top),[(0,0),(.027,0),(.027,.012),(.017,.020),(0,.020)],'aluminium',12)
    tube(f,[(sink_x,tap_y,top+.014),(sink_x,tap_y,top+.19),
            (sink_x,tap_y+.022,top+.235),(sink_x,tap_y+.073,top+.259),
            (sink_x,tap_y+.158,top+.259),(sink_x,tap_y+.215,top+.226),
            (sink_x,tap_y+.225,top+.198)],.013,'aluminium',7)
    for sx in [-1,1]:
        f.cylinder((sink_x+sx*.065,tap_y,top),(sink_x+sx*.065,tap_y,top+.045),.013,'aluminium',7)
        f.cylinder((sink_x+sx*.065,tap_y-.020,top+.045),(sink_x+sx*.065,tap_y+.032,top+.045),.006,'aluminium',6)
    tube(f,[(sink_x,cy,top-.17),(sink_x,cy,floor+.51),(sink_x,cy+.05,floor+.44),
            (sink_x,cy+.13,floor+.44),(sink_x,cy+.18,floor+.49),
            (sink_x,cy+.18,floor+.58),(sink_x,back+.04,floor+.58)],.023,'offwhite',7)
    # A short tiled splashback sits against the rear wall. It is an actual
    # fitting, not a full-room image panel or a false view through the window.
    bevel(f,(u,back+.022,floor+1.14),(work_width,.028,.50),'tile_cream',.004)
    for zz in [floor+.892,floor+1.392]:bevel(f,(u,back+.039,zz),(work_width+.008,.020,.015),'aluminium',.003)
    # Bracketed draining shelf is deliberately offset above the washing area.
    rx=u-work_width*.20;ry=back+.17;rz=floor+1.49
    for xx in [rx-.22,rx+.22]:
        tube(f,[(xx,back+.040,rz-.18),(xx,ry+.07,rz-.02),(xx,back+.040,rz-.02)],.009,'aluminium',5)
    _dish_rack(f,(rx,ry,rz),.58)
    _dish_towel(f,(u+work_width*.32,back+.08,floor+1.39),.24,.34,seed)
    soap_x=sink_x+.25
    bottle(f,(soap_x,back+.105,top+.002),.135,.028,'faded_green',2)
    tube(f,[(soap_x,back+.105,top+.140),(soap_x,back+.105,top+.167),
            (soap_x+.045,back+.105,top+.167)],.006,'aluminium',5)
    px=u+work_width*.25
    if wash:
        vessel(f,(px,cy+.015,top+.003),.105,.038,'ceramic_glaze',2,'bowl')
        bevel(f,(px+.015,cy+.01,top+.050),(.068,.046,.022),'offwhite',.009)
        vessel(f,(px,cy,floor+.288),.135,.235,'offwhite',2,'pot')
        handle=[(px+.13*math.cos(a),cy,floor+.48+.16*math.sin(a)) for a in [k*math.pi/10 for k in range(11)]]
        tube(f,handle,.006,'aluminium',5)
    else:
        bevel(f,(px,cy+.075,top+.013),(.32,.235,.025),'timber',.015)
        vessel(f,(px+.015,cy+.065,top+.027),.075,.065,'ceramic_glaze',2,'bowl')
        vessel(f,(px-.11,back+.12,top+.004),.045,.105,'ceramic_glaze',2,'pot')
        for i in range(5):
            xx=px-.13+i*.009
            f.cylinder((xx,back+.12,top+.025),(xx+(i-2)*.010,back+.12+(i%2)*.012,top+.255),.003,'timber',5)
        for i in range(3):vessel(f,(px,cy,floor+.288+i*.028),.101,.068,'ceramic_glaze',1,'bowl')
    if draw_baseboard:bevel(f,(u,back+.014,floor+.055),(width-.025,.028,.09),'wood',.004)
    return {'kind':'utility_wash' if wash else 'compact_prep','lamp':None,'detail':2,'floor_m':floor,'assets':[],
            'fixture_dimensions_m':{'counter_width':round(work_width,4),'counter_depth':work_depth,'counter_top':.86,
                                    'basin_diameter':.468,'standing_clear_depth':round(depth-.89,4)}}


def dress_window_room(f,u,floor,w,h,depth,seed,detail=1,balcony=False,hero_assets=False,room_width=None,draw_baseboard=True):
    """Six domestic uses plus a small utility room; returns light metadata."""
    detail=max(0,min(2,detail));kind=(seed//3+seed%5)%6;lit=detail>0 and seed%3!=1
    if w<1.08:kind=6
    if detail<2:return _economy_room(f,u,floor,w,depth,seed,detail,kind)
    if kind==2 and depth<2.30:
        return _compact_workroom(f,u,floor,room_width if room_width is not None else w+.16,depth,seed,draw_baseboard)
    lamp_position=None;sy=-depth+.21;assets=[]
    if kind==0:  # Study: a real writing desk, turned chair, thin books, mug.
        dw=min(w*.75,1.04);x=u-w*.05;y=-depth+.42
        bevel(f,(x,y,floor+.76),(dw,.49,.055),'timber',.011)
        for sx in [-1,1]:
            for yy in [y-.17,y+.17]:floor_leg(f,(x+sx*dw*.41,yy,floor+.02),(x+sx*dw*.39,yy,floor+.73),.018,'timber',5,r2=.028,floor=floor)
        if hero_assets:assets.append({'asset':'chinese_armchair','position':(u+w*.18,y+.36,floor),'height':1.03,'yaw':math.radians(-14),'lod':'base'})
        elif detail:chair(f,(u+w*.18,y+.36,floor),detail,math.radians(-14))
        lamp_position=lamp(f,(x-dw*.28,y,floor+.79),.68,detail,lit)
        if detail>1:vessel(f,(x+dw*.19,y+.07,floor+.79),.048,.095,'ceramic_glaze',detail)
        shelf(f,(u,sy,floor+1.66),w*.73,detail)
        books(f,u-w*.10,sy,floor+1.68,w*.59,detail,seed)
        if detail>1:picture(f,(u+w*.28,-depth+.012,floor+1.22),.27,.29,detail,seed)
    elif kind==1:  # Reading nook, upholstered sofa and shaped floor lamp.
        sw=min(w*.78,1.22);x=u-w*.07;y=-depth+.42
        tea_corner=hero_assets>=2 and w>=1.50
        if hero_assets:
            assets.append({'asset':'chinese_armchair','position':(u-w*(.24 if tea_corner else .14),-depth+.53,floor),'height':1.03,'yaw':math.radians(9),'lod':'base'})
            if tea_corner:
                tx=u+w*.24;ty=-depth+.75
                assets.append({'asset':'chinese_tea_table','position':(tx,ty,floor),'width':.72,'yaw':0.,'lod':'base'})
                teapot(f,(tx-.10,ty,floor+.42675),.66,1)
                vessel(f,(tx+.11,ty+.05,floor+.42675),.038,.061,'ceramic_glaze',1)
        else:
            for xx in [x-sw*.38,x+sw*.38]:
                for yy in [y-.17,y+.20]:floor_leg(f,(xx,yy,floor+.02),(xx,yy,floor+.22),.025,'timber',5,floor=floor)
            bevel(f,(x,y,floor+.29),(sw,.53,.17),'timber',.022)
            cushion(f,(x,y+.02,floor+.42),(sw-.05,.49,.17),'curtain_sage',detail,seed)
            back=Place(f,(x,y-.205,floor+.72),lean=0)
            cushion(back,(0,0,0),(sw,.17,.58),'curtain_sage',detail,seed+1)
            if detail:
                q=Place(f,(x+sw*.25,y-.07,floor+.63),lean=-.18)
                cushion(q,(0,0,0),(.29,.15,.32),'curtain_beige',detail,seed+2)
        # The 19 cm shade and its rim need 20.5 cm clearance from plaster.
        lamp_position=lamp(f,(u+w*(.34 if tea_corner else .36),-depth+(.205 if tea_corner else .54),floor),1.69,detail,lit)
        if detail:picture(f,(u-w*.17,-depth+.012,floor+1.67),.49,.51,detail,seed)
        else:shelf(f,(u-w*.15,sy,floor+1.60),w*.48,0);books(f,u-w*.15,sy,floor+1.62,w*.42,0,seed)
    elif kind==2:  # Small dining corner with round table and open crockery.
        tx=u-w*.10;ty=-depth+.65;radius=min(.34,w*.25)
        round_table(f,(tx,ty,floor),radius,.77,detail)
        if hero_assets:assets.append({'asset':'chinese_armchair','position':(u+w*.23,-depth+.52,floor),'height':1.03,'yaw':math.radians(-28),'lod':'base'})
        elif detail:chair(f,(u+w*.27,-depth+.33,floor),detail,math.radians(-28))
        vessel(f,(tx-.10,ty,floor+.78),.085,.075,'ceramic_glaze',detail,'bowl')
        if detail>1:
            vessel(f,(tx+.14,ty-.05,floor+.78),.050,.09,'ceramic_glaze',detail)
            stool(f,(u-w*.32,-depth+.97,floor),.145,.43,1)
        shelf(f,(u,sy,floor+1.62),w*.68,detail)
        plant(f,(u-w*.21,sy,floor+1.64),.26,detail,seed)
        bottle(f,(u+w*.16,sy,floor+1.64),.26,.062,'ceramic_glaze',detail)
        if detail>1:vessel(f,(u+w*.29,sy,floor+1.64),.067,.13,'ceramic_glaze',detail)
    elif kind==3:  # Bedroom fragment, slatted headboard and bedside light.
        # Expanded rooms accommodate an actual single-bed length. Restricted
        # corner fragments retain the cropped end, never scale all furniture
        # proportionally to the wider room envelope.
        bed_length=1.95 if depth>=2.30 else 1.10
        bw=min(.94,w*.62) if depth>=2.30 else min(.76,w*.55)
        bx=u-w*.19;by=-depth+.14+bed_length/2
        bevel(f,(bx,by,floor+.24),(bw,bed_length,.17),'timber',.018)
        for xx in [bx-bw*.40,bx+bw*.40]:
            for yy in [by-bed_length*.40,by+bed_length*.40]:floor_leg(f,(xx,yy,floor+.02),(xx,yy,floor+.24),.025,'timber',5,floor=floor)
        cushion(f,(bx,by,floor+.40),(bw-.025,bed_length,.18),'curtain_beige',detail,seed)
        if detail:cushion(f,(bx,by-bed_length*.35,floor+.53),(bw*.76,.30,.16),'curtain_linen',detail,seed+1)
        for xx in [bx-bw*.45,bx+bw*.45]:f.cylinder((xx,-depth+.15,floor+.12),(xx,-depth+.15,floor+1.02),.026,'timber',6)
        for zz in [.71,.93]:bevel(f,(bx,-depth+.15,floor+zz),(bw,.04,.075),'timber',.010)
        tx=u+w*.30;ty=-depth+.34
        # A compact bedside stand has open space beneath the top.
        bevel(f,(tx,ty,floor+.64),(.32,.32,.045),'timber',.009)
        for sx,sy2 in [(-1,-1),(1,-1),(-1,1),(1,1)]:floor_leg(f,(tx+sx*.12,ty+sy2*.12,floor+.03),(tx+sx*.12,ty+sy2*.12,floor+.62),.017,'timber',5,floor=floor)
        lamp_position=lamp(f,(tx,ty,floor+.67),.73,detail,lit)
        picture(f,(u-w*.13,-depth+.012,floor+1.67),.43,.51,detail,seed)
    elif kind==4:lamp_position=_cabinet_scene(f,u,floor,w,depth,detail,seed,lit,assets if hero_assets else None)
    elif kind==5:  # Bookshelf: varied thin spines, open shelves and a plant.
        sw=min(w*.79,1.12);sx=u-w*.05
        levels=[.88,1.38,1.88] if detail else [1.33,1.83]
        for xx in [sx-sw/2+.018,sx+sw/2-.018]:bevel(f,(xx,sy-.02,floor+1.03),(.035,.20,1.98),'timber',.005)
        for i,zz in enumerate(levels):
            shelf(f,(sx,sy,floor+zz),sw,detail)
            if i==0 and detail:
                if hero_assets:assets.append({'asset':'potted_plant_02','position':(sx-sw*.24,sy+.08,floor+zz+.025),'height':.43,'yaw':seed*.73,'lod':'low'})
                else:plant(f,(sx-sw*.24,sy,floor+zz+.025),.28,detail,seed)
            else:books(f,sx+(-.11 if i%2 else .09),sy,floor+zz+.025,sw*.75,detail,seed+i*13)
        if detail>1:
            vessel(f,(sx+sw*.30,sy,floor+levels[0]+.025),.067,.15,'ceramic_glaze',detail)
    else:  # Narrow utility window still has a basin, tap and towel rail.
        bz=floor+.91
        vessel(f,(u,-depth+.34,bz),w*.28,.14,'ceramic_glaze',detail,'bowl')
        floor_leg(f,(u,-depth+.34,floor+.12),(u,-depth+.34,bz),.058,'offwhite',8,floor=floor)
        tube(f,[(u,-depth+.16,bz+.10),(u,-depth+.16,bz+.31),(u,-depth+.31,bz+.31)],.012,'aluminium',5)
        bevel(f,(u,-depth+.012,floor+1.62),(w*.62,.025,.52),'frame',.007)
        f.quad((u-w*.27,-depth+.029,floor+1.38),(u-w*.27,-depth+.029,floor+1.86),(u+w*.27,-depth+.029,floor+1.86),(u+w*.27,-depth+.029,floor+1.38),'glass_blue')
        if detail:
            shelf(f,(u,-depth+.16,floor+1.27),w*.70,detail)
            bottle(f,(u-w*.20,-depth+.15,floor+1.29),.19,.034,'offwhite',detail)
    # A light moulding anchors the floor/room at a believable architectural scale.
    if detail>1 and draw_baseboard:
        bevel(f,(u,-depth+.014,floor+.055),(w+.12,.028,.09),'wood',.004)
    return {'kind':['study','reading_nook','dining','bedroom','kitchen_sideboard','bookshelf','utility'][kind],
            'lamp':lamp_position if lit else None,'detail':detail,'floor_m':floor,'assets':assets}


def teapot(f,p,scale=1,detail=2):
    """Rounded tea pot with a fitted lid, shaped spout and loop handle."""
    x,y,z=p;r=.105*scale;h=.15*scale
    lathe(f,p,[(0,0),(r*.57,0),(r*.93,h*.25),(r,h*.56),(r*.70,h*.90),(r*.53,h),(0,h)],'ceramic_glaze',16 if detail>1 else 10)
    lathe(f,(x,y,z+h),[(0,0),(r*.60,0),(r*.52,.018*scale),(r*.20,.028*scale),(0,.028*scale)],'ceramic_glaze',14 if detail>1 else 10)
    lathe(f,(x,y,z+h+.025*scale),[(0,0),(.021*scale,0),(.023*scale,.019*scale),(0,.025*scale)],'timber',10)
    tube(f,[(x+r*.72,y,z+h*.32),(x+r*1.35,y,z+h*.58),(x+r*1.67,y,z+h*.96)],.022*scale,'ceramic_glaze',6)
    points=[(x-r*.79-math.cos(-math.pi/2+k*math.pi/8)*r*.65,y,z+h*.52+math.sin(-math.pi/2+k*math.pi/8)*h*.40) for k in range(9)]
    tube(f,points,.014*scale,'ceramic_glaze',6)


def printer(f,p,width=1.10):
    """Recognisable compact copier: scanner lid, paper exit, controls, wheels."""
    x,y,z=p;d=.78
    bevel(f,(x,y,z+.54),(width,d,.88),'offwhite',.035)
    bevel(f,(x,y,z+.16),(width+.035,d+.025,.12),'painted_metal',.016)
    # Move only the wheel components. Their real polygon soles meet the floor,
    # while the upper tyre still overlaps the fixed chassis by about 6.5 mm.
    wheel_z=z+.056*max(math.sin(i*math.tau/10) for i in range(10))
    for xx in [x-width*.37,x+width*.37]:
        for yy in [y-d*.34,y+d*.34]:f.cylinder((xx-.025,yy,wheel_z),(xx+.025,yy,wheel_z),.056,'black_rubber',10)
    bevel(f,(x,y-.015,z+1.015),(width+.08,d+.08,.085),'painted_metal',.021)
    bevel(f,(x,y-.055,z+1.071),(width*.88,d*.84,.055),'offwhite',.014)
    # Genuine recessed exit opening, front lip and a pair of loose paper sheets.
    f.box((x-width*.07,y+d/2+.003,z+.80),(width*.63,.014,.13),'dark')
    bevel(f,(x-width*.07,y+d/2+.11,z+.726),(width*.68,.23,.022),'painted_metal',.008)
    for k in range(2):
        zz=z+.745+k*.003
        f.quad((x-width*.26,y+d/2-.04,zz),(x+width*.13,y+d/2-.04,zz),(x+width*.13,y+d/2+.17,zz-.012),(x-width*.26,y+d/2+.17,zz-.012),'paper')
    for zz in [z+.32,z+.51]:
        bevel(f,(x,y+d/2+.009,zz),(width*.88,.026,.16),'offwhite',.006)
        f.box((x+width*.23,y+d/2+.028,zz+.022),(.13,.009,.025),'frame')
    bevel(f,(x+width*.31,y+d/2+.008,z+.995),(width*.27,.045,.12),'frame',.010)
    f.quad((x+width*.22,y+d/2+.033,z+.970),(x+width*.22,y+d/2+.033,z+1.025),(x+width*.32,y+d/2+.033,z+1.025),(x+width*.32,y+d/2+.033,z+.970),'electric_blue')
    for k in range(3):f.cylinder((x+width*.37,y+d/2+.034,z+.977+k*.020),(x+width*.37,y+d/2+.040,z+.977+k*.020),.006,'offwhite',6)
    # A shaped automatic document feeder, not another featureless white box.
    vs=[(x-width*.30,y-.22,z+1.10),(x+width*.30,y-.22,z+1.10),(x+width*.30,y+.21,z+1.10),(x-width*.30,y+.21,z+1.10),
        (x-width*.30,y-.22,z+1.24),(x+width*.30,y-.22,z+1.24),(x+width*.30,y+.21,z+1.14),(x-width*.30,y+.21,z+1.14)]
    f.mesh(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'offwhite')


def parcel(f,p,size,seed=0):
    """A carton is intentionally rectangular, but has folds, tape and a label."""
    x,y,z=p;w,d,h=size
    bevel(f,p,size,'paper',.007)
    # Fold gap and tape wrap are flush construction details, never giant blocks.
    f.quad((x-.004,y-d/2,z+h/2+.002),(x+.004,y-d/2,z+h/2+.002),(x+.004,y+d/2,z+h/2+.002),(x-.004,y+d/2,z+h/2+.002),'wood')
    f.quad((x-.025,y-d/2,z+h/2+.003),(x+.025,y-d/2,z+h/2+.003),(x+.025,y+d/2,z+h/2+.003),(x-.025,y+d/2,z+h/2+.003),'sign_cream')
    f.quad((x-.025,y+d/2+.003,z-h/2),(x-.025,y+d/2+.003,z+h/2),(x+.025,y+d/2+.003,z+h/2),(x+.025,y+d/2+.003,z-h/2),'sign_cream')
    lx=x+w*.22;ly=y+d/2+.004;lz=z+h*.15
    f.quad((lx-.065,ly,lz-.043),(lx-.065,ly,lz+.043),(lx+.065,ly,lz+.043),(lx+.065,ly,lz-.043),'offwhite')
    for k in range(7):
        xx=lx-.047+k*.014;bw=.003 if (k+seed)%2 else .006
        f.quad((xx,ly+.001,lz-.029),(xx,ly+.001,lz+.006),(xx+bw,ly+.001,lz+.006),(xx+bw,ly+.001,lz-.029),'frame')


def shop_details(f,u,width,height,style,label,seed,hero_assets=False):
    """Detailed additions/replacements inside the existing 2.4 m shop recess."""
    eatery=style=='noodle' or '家常菜' in label;assets=[]
    if eatery:
        # An eating place is legible beyond its service counter, and keeps a
        # clear route through the centre of the entrance.
        tx=u+width*.27;ty=-1.67
        round_table(f,(tx,ty,.09),.33,.75,2)
        if hero_assets:assets.append({'asset':'plastic_monobloc_chair_01','position':(tx+.22,ty+.43,.09),'height':.85,'yaw':math.pi,'lod':'base'})
        else:stool(f,(tx+.27,ty+.43,.09),.15,.43,2)
        vessel(f,(tx-.08,ty+.01,.852),.10,.076,'ceramic_glaze',2,'bowl')
        vessel(f,(tx+.13,ty-.04,.852),.045,.08,'ceramic_glaze',2)
        for xx in [tx-.052,tx-.027]:f.cylinder((xx,ty-.12,.94),(xx+.075,ty+.11,.95),.0035,'timber',5)
        # Condiments have shoulders, screw caps and paper labels; no cubes.
        for i in range(3):bottle(f,(u-width*.40+i*.17,-2.08,1.73),.22+.035*(i%2),.047,'faded_red' if i==1 else 'faded_green',2)
        cw=max(1.0,width*.33);cu=u-width*.29
        teapot(f,(cu+cw*.25,-.59,1.08),.72,2)
        # Loose folded tea towel on the counter, with a rounded textile edge.
        cushion(f,(cu+cw*.24,-.91,1.085),(.27,.19,.028),'curtain_linen',1,seed)
    elif style=='heritage' or '茶' in label:
        tx=u+width*.25;ty=-1.50
        round_table(f,(tx,ty,.09),.39,.76,2)
        if hero_assets:assets.append({'asset':'chinese_armchair','position':(tx+.18,ty-.43,.09),'height':1.03,'yaw':math.radians(-22),'lod':'base'})
        else:chair(f,(tx+.25,ty-.50,.09),2,math.radians(-22))
        stool(f,(tx+.13,ty+.50,.09),.17,.44,2)
        teapot(f,(tx-.06,ty,.858),1.,2)
        for xx,yy in [(.17,.06),(-.15,.16)]:vessel(f,(tx+xx,ty+yy,.858),.045,.065,'ceramic_glaze',2)
        plant(f,(u-width*.35,-1.29,1.0),.37,2,seed)
    elif style=='repair':
        # Visible vise jaws, screw, a tray and small hand tools on the bench.
        x=u-width*.25;y=-1.48
        bevel(f,(x,y,.97),(.25,.21,.08),'painted_metal',.012)
        for xx in [x-.065,x+.065]:bevel(f,(xx,y,1.055),(.045,.20,.12),'aluminium',.007)
        f.cylinder((x-.15,y+.065,1.02),(x+.20,y+.065,1.02),.018,'aluminium',8)
        f.cylinder((x+.19,y+.065,.94),(x+.19,y+.065,1.10),.009,'frame',6)
        for i in range(3):
            xx=u+width*.02+i*.13
            f.cylinder((xx,-1.74,.944),(xx+.06,-1.40,.944),.011,'aluminium',6)
            bevel(f,(xx+.065,-1.385,.95),(.06,.10,.022),'frame',.008)
        bottle(f,(u-width*.39,-1.91,.94),.21,.043,'faded_red',2)
        if hero_assets:assets.append({'asset':'plastic_monobloc_chair_01','position':(u+width*.24,-1.14,.09),'height':.85,'yaw':math.radians(-24),'lod':'base'})
        else:stool(f,(u+width*.24,-1.14,.09),.18,.46,2)
    elif style=='artisan':
        # Turned pottery on an open work table, with a loose linen cloth.
        tx=u+width*.25;ty=-1.44
        bevel(f,(tx,ty,.91),(.91,.62,.065),'timber',.012)
        for xx in [tx-.35,tx+.35]:
            for yy in [ty-.22,ty+.22]:floor_leg(f,(xx,yy,.10),(xx,yy,.88),.028,'timber',6,floor=.09)
        for i in range(3):vessel(f,(tx-.26+i*.24,ty,.95),.068+i*.016,.14+i*.045,'ceramic_glaze',2,'pot')
        cushion(f,(tx-.23,ty+.16,.96),(.31,.22,.03),'curtain_linen',1,seed)
        stool(f,(tx+.05,ty+.57,.09),.16,.43,2)
    return assets


PROVENANCE={
    'module':'interior_scenes.py',
    'revision':14,
    'geometry_origin':'Original authored procedural furniture components plus a small set of prepared Poly Haven CC0 furniture/plant instance markers. No photograph cards.',
    'selected_scans':['chinese_armchair','chinese_tea_table','plastic_monobloc_chair_01','potted_plant_02'],
    'scan_provenance':'scanned_assets/source_credits.json and scanned_assets/manifest.json; instances bounded to a shared budget of 36.',
    'surface_origin':'Existing district material library: CC0 wood/fabric scans and authored solid colors. Refer to material_provenance.json for source-level licenses.',
    'floor_contact':'R14: known floor-standing legs retain their upper rings, complete XY footprints and furniture positions; only their lower rings extend to a planar sole at the authored floor. Copier wheel components meet the same floor without moving the chassis. Tabletop, shelf, lamp and scanned-asset placements are unchanged.',
    'design':'Domestic room uses and specific small shop activities; shallow near-street dining bays are fitted as metre-scale wash/preparation rooms with pierced worktops, open basins, plumbing, wire dish racks and hanging cloth. Safely expanded rooms retain their reading/study layouts. Actual room planes are subdivided for independent interior sky/contact-visibility baking.',
}
