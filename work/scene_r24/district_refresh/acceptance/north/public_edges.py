"""Independent public fragments identified in the 2019 field panoramas."""
from math import cos, radians, sin

from mathutils import Vector

from build import box


def basis(scope, a, end, level=None):
    origin = Vector(a)
    along = (Vector(end) - origin).normalized()
    inward = Vector((-along.y, along.x))
    def at(u, v, z):
        e, n = origin + u*along + v*inward
        return (e, n, (scope.floor(e,n) if level is None else level)+z)
    return at


def school(scope):
    # This short independent scene edge records the 2019 school gate typology.
    # Its footprint is a game fit beside the public lane, outside the old 42 door.
    a = (89.55, 188.28)
    at = basis(scope, a, (91.67, 189.98), scope.floor(*a)-.02)
    granite = scope.finish('school grey ledge stone', (.68,.70,.68), 'stone_wall_05_diff_2k.jpg', .22)
    thin = scope.finish('school worn light stone step', (.78,.78,.725), 'concrete_floor_worn_001_diff_2k.jpg', .26)
    brick = scope.finish('school grey-green small paving', (.52,.67,.50), 'stone_floor_diff_2k.jpg', .21)
    rail = scope.finish('school dark slender rail', (.19,.23,.20), metal=.45)
    iron = scope.mesh('Review42_SchoolGatePiersAndBentRail')
    stair = scope.mesh('Review42_SchoolThreeStoneStepsAndFanFlags')
    for u in (-.27, 3.09):
        box(iron,at,u,u+.51,.42,.96,-.20,1.84,granite)
        box(iron,at,u-.065,u+.585,.37,1.021,1.84,1.985,thin)
        for j in range(5):
            box(iron,at,u,u+.52,.413,.431,.14+j*.309,.166+j*.309,thin)
    for i in range(3):
        start=.31+i*.29
        box(stair,at,.25,3.06,start,1.74,-.26,.148*(i+1),thin)
    box(stair,at,-.05,3.39,1.18,3.43,-.64,.446,thin)
    box(iron,at,-1.22,-.22,.44,.79,-.20,1.05,granite)
    box(iron,at,-1.24,-.20,.42,.84,1.05,1.123,thin)
    box(iron,at,2.85,3.27,1.25,3.38,.44,.78,granite)
    # Sector lines in the small gate apron. Tile texture is project artwork.
    center=1.46
    for r in range(1,6):
        a=.27*r; b=a+.22
        for k in range(10):
            t=radians(24+k*13.2); w=t+radians(11.9)
            corners=[at(center+rad*cos(v),1.29+rad*sin(v),.449) for rad,v in ((a,t),(b,t),(b,w),(a,w))]
            stair.face(corners,brick if (k+r)%3 else thin)
    for i in range(8):
        u=3.43+i*.29
        v=.82+.033*i*i
        box(iron,at,u,u+.287,v,v+.31,-.11,.36,(granite,thin)[i % 3 == 1])
        box(iron,at,u+.06,u+.092,v+.12,v+.16,.36,.88,rail)
        box(iron,at,u,u+.279,v+.115,v+.166,.82,.86,rail)
    scope.points['42'] = [[85.825789,188.995499,43.0015], [89.54,190.05,scope.floor(89.54,190.05)+.04]]


def liangting_storefront(scope):
    left=(105.56,164.43)
    right=(108.85,166.05)
    floor=scope.floor(107.30,164.62)+.03
    at=basis(scope,left,right,floor)
    masonry=scope.finish('grey stair-side shop brick', (.55,.54,.50), 'brick_wall_08_diff_2k.jpg', .22)
    ashlar=scope.finish('grey worn dressed stone caps', (.76,.75,.73), 'concrete_floor_worn_001_diff_2k.jpg', .24)
    shade=scope.finish('dark recessed unregistered shop', (.10,.129,.107))
    mint=scope.finish('small celadon mosaic', (.53,.68,.60), 'stone_floor_diff_2k.jpg', .28)
    plaster=scope.finish('soft grey balcony slab face', (.71,.72,.64), 'concrete_wall_006_diff_2k.jpg', .27)
    rod=scope.finish('black metal protection rails', (.14,.17,.16), metal=.51)
    canopy=scope.finish('aged cyan canopy metal', (.30,.46,.41), 'rusty_painted_metal_diff_2k.jpg', .27)
    frontage=scope.mesh('Review43_SouthRecessedBrickFrontage')
    upper=scope.mesh('Review43_MosaicReturnBalconiesAndWindowGuards')
    paving=scope.mesh('Review43_SouthStepsAndBrickPublicEdge')
    # Use the observed fascia span as a locating reference. Offset features
    # are game fits within the visible frontage, with an unsigned lintel.
    for a,b in ((-2.18,-1.37),(-.78,-.13),(3.74,4.32),(5.69,6.17)):
        box(frontage,at,a,b,.08,.49,-.20,2.44,masonry)
        box(frontage,at,a-.048,b+.048,.025,.53,2.42,2.55,ashlar)
    box(frontage,at,-.08,3.66,.07,.30,2.19,2.54,plaster)
    box(frontage,at,-.09,3.68,1.16,1.26,.04,2.19,shade)
    for i in range(3):
        box(paving,at,.12,3.40,.11+i*.255,1.12,-.12,.13*(i+1),ashlar)
    for a,b in ((-1.34,-.79),(4.35,5.02),(5.04,5.64)):
        box(frontage,at,a,b,.17,.25,.08,2.27,shade)
        for k in range(6):
            x=a+(k+.30)*(b-a)/6
            box(frontage,at,x,x+.025,.134,.168,.09,2.26,rod)
    for i in range(36):
        u=-2.04+i*.23
        verts=[at(x,y,z) for x,y,z in ((u,-.38,.018),(u+.215,-.38,.018),(u+.215,-.14,.018),(u,-.14,.018))]
        # Conform paving only. Its contact comes from the already walked lane.
        paving.face([(e,n,scope.floor(e,n)+.009) for e,n,_ in verts],masonry if i%5 else ashlar)
    for low in (2.58,5.04):
        for u0,u1,depth in ((-2.21,.43,.56),(.44,3.19,.81),(3.20,6.08,.44)):
            box(upper,at,u0,u1,-depth,.92,low,low+.16,plaster)
            box(upper,at,u0,u1,-depth,-depth+.16,low+.15,low+.79,mint)
            box(upper,at,u0,u0+.15,-depth,.69,low+.16,low+.79,mint)
            box(upper,at,u0+.19,u1-.17,.32,.41,low+.76,low+1.93,shade)
            box(upper,at,u0+.10,u1-.11,-depth-.12,.46,low+1.98,low+2.04,canopy)
            for j in range(1,9):
                u=u0+(u1-u0)*j/9
                box(upper,at,u,u+.021,.28,.30,low+.77,low+1.90,rod)
            for high in (.84,1.27,1.85):
                box(upper,at,u0+.17,u1-.15,.272,.311,low+high,low+high+.028,rod)
            for i in range(round((u1-u0)/.13)):
                u=u0+i*.128
                box(upper,at,u,u+.009,-depth-.004,-depth+.005,low+.16,low+.78,ashlar)
    scope.points['43'] = [[105.06,162.10,scope.floor(105.06,162.10)+.04], list(at(1.4,.15,1.45))]
