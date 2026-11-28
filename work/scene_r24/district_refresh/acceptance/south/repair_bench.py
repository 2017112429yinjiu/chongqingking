"""Workshop furniture in the existing bay, in Plot 00 local metres."""
from math import cos, pi, sin

from mathutils import Vector

from east.textured_goods import UVSurface

TOP = (-3.80, -2.31, -.84, -.15, .850, .923)
LEGS = tuple((u, u+.096, v, v+.096, .039, .856)
             for u in (-3.73, -2.48) for v in (-.77, -.317))
EYE_FOOT = (-1.68, .46, .050)
EYE_TARGET = (-3.075, -.51, .97)


def finish(scope, label, asset, tint, metallic=0., *, diffuse=None, fill=.22, relief=.44):
    prefix = 'chongqing_district_' + asset
    mat = scope.pbr(label, tint, diffuse or prefix+'_diff_2k.jpg', prefix+'_nor_gl_2k.jpg',
                    prefix+'_rough_2k.png', ambient=fill, tint=tint, normal_strength=relief)
    mat.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = metallic
    return mat


def plated(mesh, at, ring, bottom, top, material, size):
    """A horizontal, through-thickness profile with planar and edge UVs."""
    area = sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(ring,ring[1:]+ring[:1]))
    if area<0:
        ring = ring[::-1]
    low, high = [[at(u,v,z) for u,v in ring] for z in (bottom,top)]
    planar = [(u/size,v/size) for u,v in ring]
    mesh.face(low[::-1],material,planar[::-1])
    mesh.face(high,material,planar)
    offset = 0.
    for i in range(len(ring)):
        j = (i+1)%len(ring)
        end = offset + (Vector(ring[j])-Vector(ring[i])).length/size
        mesh.face((low[i],low[j],high[j],high[i]), material,
                  ((offset,0),(end,0),(end,(top-bottom)/size),(offset,(top-bottom)/size)))
        offset = end


def block(mesh, at, bounds, material, mapping=.46, bevel=.008):
    u0,u1,v0,v1,z0,z1 = bounds
    ring = [(u0+bevel,v0),(u1-bevel,v0),(u1,v0+bevel),(u1,v1-bevel),
            (u1-bevel,v1),(u0+bevel,v1),(u0,v1-bevel),(u0,v0+bevel)]
    plated(mesh,at,ring,z0,z1,material,mapping)


def turned(mesh, at, a, b, rings, material, sides=14):
    """A round part with longitudinal and circumferential UVs."""
    start, end = Vector(a), Vector(b)
    direction = (end-start).normalized()
    hint = Vector((0,0,1)) if abs(direction.z)<.9 else Vector((0,1,0))
    x = hint.cross(direction).normalized()
    y = direction.cross(x)
    verts = []
    for distance, radius in rings:
        level = start + (end-start)*distance
        verts.append([at(*(level+(x*cos(2*pi*i/sides)+y*sin(2*pi*i/sides))*radius))
                      for i in range(sides)])
    mesh.face(verts[0][::-1],material,[(.5+cos(2*pi*i/sides)*.5,.5+sin(2*pi*i/sides)*.5)
                                     for i in reversed(range(sides))])
    mesh.face(verts[-1],material,[(.5+cos(2*pi*i/sides)*.5,.5+sin(2*pi*i/sides)*.5)
                                 for i in range(sides)])
    for index,(lower,upper) in enumerate(zip(verts,verts[1:])):
        length = (end-start).length
        v0,v1 = (rings[k][0]*length/.20 for k in (index,index+1))
        for i in range(sides):
            j = (i+1)%sides
            mesh.face((lower[i],lower[j],upper[j],upper[i]),material,
                      ((i/sides,v0),((i+1)/sides,v0),((i+1)/sides,v1),(i/sides,v1)))


def rod(mesh,at,a,b,radius,material,sides=12):
    turned(mesh,at,a,b,[(0,radius*.82),(.10,radius),(.9,radius),(1,radius*.82)],material,sides)


def pose(at, u, v, z, angle):
    c,s=cos(angle),sin(angle)
    return lambda x,y,h: at(u+c*x-s*y,v+s*x+c*y,z+h)


def vise(scope, at, cast, steel):
    mesh=scope.mesh('Review00_ViseCastBaseJawsScrewAndGuides', UVSurface)
    at=pose(at,-2.61,-.288,TOP[-1],pi)
    block(mesh,at,(-.154,.154,-.094,.140,0,.021),cast,.24,.015)
    rod(mesh,at,(0,.025,.018),(0,.025,.064),.093,cast,20)
    block(mesh,at,(-.107,.103,-.040,.124,.044,.142),cast,.22)
    block(mesh,at,(-.119,.119,-.086,-.039,.071,.164),cast,.22)
    block(mesh,at,(-.112,.112,-.067,-.041,.152,.174),steel,.15,.004)
    block(mesh,at,(-.117,.117,-.219,-.165,.080,.155),cast,.22)
    block(mesh,at,(-.112,.112,-.171,-.144,.147,.174),steel,.15,.004)
    for u in (-.058,.058):
        rod(mesh,at,(u,-.213,.101),(u,-.049,.101),.010,steel)
    rod(mesh,at,(0,-.266,.119),(0,-.047,.119),.016,steel,16)
    # One continuous helical ridge around the screw.
    levels=42
    def turn(i, radius, offset):
        angle=i*(2*pi/12)
        return at(radius*cos(angle),-.165+.107*i/levels+offset,.119+radius*sin(angle))
    for i in range(levels):
        a,b,c,d=turn(i,.016,-.002),turn(i+1,.016,-.002),turn(i+1,.020,0),turn(i,.020,0)
        e,f=turn(i,.016,.002),turn(i+1,.016,.002)
        mesh.face((a,b,c,d),steel,((0,0),(1,0),(1,.05),(0,.05)))
        mesh.face((d,c,f,e),steel,((0,.05),(1,.05),(1,.1),(0,.1)))
    rod(mesh,at,(-.081,-.244,.108),(.086,-.244,.132),.007,steel)
    for u,z in ((-.082,.108),(.086,.132)):
        rod(mesh,at,(u-.005,-.244,z),(u+.005,-.244,z),.011,steel)
    for u,v in ((-.115,-.063),(.115,-.063),(-.111,.103),(.111,.103)):
        rod(mesh,at,(u,v,.016),(u,v,.025),.014,steel,6)


def hand_tools(scope, at, steel, dark, handle):
    wrench = scope.mesh('Review00_OpenEndWrench',UVSurface)
    place = pose(at,-3.55,-.398,TOP[-1],.27)
    angles=[pi/4+i*1.5*pi/16 for i in range(17)]
    for low,high in zip(angles,angles[1:]):
        ring=[(.048+r*cos(a),r*sin(a)) for r,a in ((.025,low),(.040,low),(.040,high),(.025,high))]
        plated(wrench,place,ring,.002,.012,steel,.13)
    plated(wrench,place,[(-.169,-.010),(-.144,-.015),(.019,-.015),(.025,.012),
                         (-.145,.016),(-.169,.010)],.002,.012,steel,.13)

    pliers = scope.mesh('Review00_PliersWithGripsAndPivot',UVSurface)
    place = pose(at,-3.33,-.660,TOP[-1],-.36)
    arm=[(-.125,.050),(-.105,.052),(-.035,.034),(.011,.011),(.045,-.002),(.066,-.004),
         (.066,-.013),(.043,-.018),(.006,-.010),(-.050,.020),(-.128,.033)]
    grip=[(-.127,.053),(-.111,.056),(-.069,.044),(-.043,.032),(-.045,.016),
          (-.093,.028),(-.129,.031),(-.135,.040)]
    for sign in (1,-1):
        for shape,mat,height in ((arm,steel,.014),(grip,handle,.021)):
            ring=[(u,sign*v) for u,v in shape]
            plated(pliers,place,ring if sign==1 else ring[::-1],.001,height,mat,.16)
    rod(pliers,place,(0,0,.011),(0,0,.021),.018,dark,16)
    rod(pliers,place,(0,0,.019),(0,0,.023),.007,steel)

    driver=scope.mesh('Review00_RibbedScrewdriver',UVSurface)
    place=pose(at,-2.98,-.690,TOP[-1],.25)
    a,b=(-.102,0,.021),(.016,0,.021)
    turned(driver,place,a,b,[(0,.011),(.12,.019),(.23,.021),(.75,.018),(.96,.012),(1,.011)],handle)
    for i in range(6):
        angle=i*2*pi/6
        y,z=.018*cos(angle),.021+.018*sin(angle)
        rod(driver,place,(-.082,y,z),(-.023,y,z),.0026,dark,8)
    rod(driver,place,(.009,0,.021),(.137,0,.021),.006,steel)
    plated(driver,place,[(.126,-.005),(.153,-.006),(.153,.006),(.127,.005)],.018,.024,steel,.13)


def make(scope, at):
    wood=finish(scope,'workshop worn hardwood grain','wood_table_worn',(.81,.64,.47))
    scan='district_500/acceptance_textures/repair-workshop-steel-albedo.jpg'
    cast=finish(scope,'workshop painted cast iron','rusty_painted_metal',(.48,.62,.59),.10,
                diffuse=scan,fill=.22,relief=.28)
    steel=finish(scope,'workshop worn steel','rusty_painted_metal',(.94,.96,.93),.23,
                 diffuse=scan,fill=.32,relief=.15)
    dark=finish(scope,'workshop darkened hardware','rusty_painted_metal',(.31,.35,.33),.43)
    handle=finish(scope,'workshop worn grip','wood_table_worn',(.43,.23,.14))
    bench=scope.mesh('Review00_BayWorkbench',UVSurface)
    for leg in LEGS:
        block(bench,at,leg,cast)
        u0,u1,v0,v1,_,_=leg
        block(bench,at,(u0-.005,u1+.005,v0-.005,v1+.005,.039,.073),dark)
    for v in (-.754,-.318):
        block(bench,at,(-3.71,-2.39,v,v+.059,.799,.856),cast)
    block(bench,at,(-3.68,-2.44,-.313,-.259,.22,.284),cast)
    u0,u1,v0,v1,z0,z1=TOP
    for i in range(3):
        a=v0+(v1-v0)*i/3
        b=v0+(v1-v0)*(i+1)/3
        block(bench,at,(u0,u1,a+.001,b-.001,z0,z1),wood,.86,.012)
    vise(scope,at,cast,steel)
    hand_tools(scope,at,steel,dark,handle)
