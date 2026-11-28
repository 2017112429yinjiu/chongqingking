"""Independent public fragments identified in the 2019 field panoramas."""

from mathutils import Vector

from build import box
from east.textured_goods import UVSurface, plant_material


def basis(scope, a, end, level=None):
    origin = Vector(a)
    along = (Vector(end) - origin).normalized()
    inward = Vector((-along.y, along.x))
    def at(u, v, z):
        e, n = origin + u*along + v*inward
        return (e, n, (scope.floor(e,n) if level is None else level)+z)
    return at


TEXTURE = 'district_500/acceptance_textures/'


def placard(scope, mesh, at, key, ua, ub, v, za, zb):
    face = scope.finish(key, (.86,.86,.86), TEXTURE+'north-'+key+'.jpg', .11)
    mesh.face([at(ua,v,za),at(ub,v,za),at(ub,v,zb),at(ua,v,zb)],face,
              [(0,0),(1,0),(1,1),(0,1)])


def hedge(scope, at, u0, u1, depth, bottom):
    # Keep the clipped outline continuous, with separate complete leaves at
    # the sun-facing lip and exposed returns.
    from random import Random
    rng = Random(42)
    m = scope.mesh('Review42_TrimmedSchoolHedge', UVSurface)
    foliage = plant_material(scope,'school clipped broadleaf',(.55,.72,.31))
    for i in range(round((u1-u0)*360)):
        u = rng.uniform(u0,u1)
        v = depth+rng.uniform(-.235,.235)
        z = bottom+.40*rng.random()
        if .065 < z-bottom < .33 and abs(v-depth)<.16:
            continue
        w=rng.uniform(.021,.038)
        h=rng.uniform(.035,.062)
        lean=rng.uniform(-.031,.031)
        corners = [at(u-w,v,z),at(u+w,v+lean,z+.014),at(u+w*.45,v+.032,z+h),
                   at(u-w*.54,v+.028,z+h*.82)]
        uv=[(.33,.32),(.56,.32),(.56,.57),(.33,.57)]
        m.face(corners, foliage, uv)
        m.face(corners[::-1], foliage, uv[::-1])


def school(scope):
    a = (89.55, 188.28)
    at = basis(scope, a, (91.67, 189.98), scope.floor(*a)-.02)
    url = 'district_r21/terraces_washed_sandstone.jpg'
    maps = (TEXTURE+'washed-stone-normal.jpg', TEXTURE+'washed-stone-rough.jpg')
    granite = scope.pbr('school blue-grey dressed stone',(.62,.72,.72),url,*maps,tint=(.64,.74,.75))
    thin = scope.pbr('school pale grey cap and three treads',(.83,.87,.86),url,*maps,tint=(.88,.92,.89))
    dark = scope.pbr('school shaded lower masonry',(.56,.64,.63),url,*maps,tint=(.57,.69,.68))
    rail = scope.finish('school slender black iron', (.112,.139,.132), metal=.54)
    fan = scope.finish('school green-white fan mosaic',(.68,.74,.65),TEXTURE+'north-school-fan-flags.jpg',.15)
    soil=scope.finish('school bed leaf litter',(.39,.42,.31),'leaf_scattered_gravel_diff_2k.jpg',.14)
    iron = scope.mesh('Review42_SchoolGatePiersAndBentRail')
    stair = scope.mesh('Review42_SchoolThreeStoneStepsAndFanFlags', UVSurface)
    signs = scope.mesh('Review42_OriginalSchoolNameAndPlaque', UVSurface)
    for u in (-.27, 3.09):
        for j in range(6):
            box(iron,at,u,u+.51,.42,.96,-.18+j*.325,.136+j*.325,(granite,dark)[j==0])
        for relief, base, top in ((.055,1.76,1.855),(.087,1.855,1.94),(.112,1.94,2.045)):
            box(iron,at,u-relief,u+.51+relief,.42-relief,.96+relief,base,top,thin)
    for i in range(3):
        start=.31+i*.29
        box(stair,at,.25,3.06,start,1.74,-.26,.148*(i+1),thin)
    box(stair,at,-.05,3.39,1.18,3.43,-.64,.446,thin)
    stair.face([at(x,y,.449) for x,y in ((-.045,1.18),(3.38,1.18),(3.38,3.42),(-.045,3.42))],
               fan,[(0,0),(2.12,0),(2.12,1.36),(0,1.36)])
    box(iron,at,-2.34,-.22,.44,.87,-.29,.99,granite)
    box(iron,at,-2.38,-.20,.40,.92,.99,1.095,thin)
    placard(scope,signs,at,'xinglin-school',-2.19,-.36,.432,.31,.90)
    placard(scope,signs,at,'xinglin-placard',-.202,.166,.409,.19,1.65)
    for u0,u1,v0,v1 in ((.04,3.04,2.91,3.05),(.04,.17,3.05,3.47),(2.91,3.04,3.05,3.47)):
        box(iron,at,u0,u1,v0,v1,.44,.80,granite)
        box(iron,at,u0-.018,u1+.018,v0-.018,v1+.018,.80,.846,thin)
    box(iron,at,.17,2.91,3.05,3.47,.45,.77,soil)
    hedge(scope,at,.17,2.91,3.26,.77)
    # Keep the wall on one side of the narrow public lane as it turns east.
    for i in range(23):
        u=3.43+i*.305
        v=.82+.011*i*i
        end=.82+.011*(i+1)**2
        def bend(x,y,z):
            return at(x,y+(end-v)*(x-u)/.305,z)
        for j in range(3):
            box(iron,bend,u,u+.303,v,v+.31,-.19+j*.157,-.039+j*.157,dark if j==0 else granite)
        box(iron,bend,u-.005,u+.307,v-.033,v+.353,.287,.359,thin)
        for height in (.40,.91):
            box(iron,bend,u,u+.305,v+.126,v+.17,height,height+.038,rail)
        for x in (u+.069,u+.216):
            box(iron,bend,x,x+.018,v+.13,v+.165,.346,.945,rail)
    scope.points['42'] = [[85.825789,188.995499,43.0015], [89.54,190.05,scope.floor(89.54,190.05)+.04]]


def liangting_storefront(scope):
    left=(105.56,164.43)
    right=(108.85,166.05)
    floor=scope.floor(107.30,164.62)+.03
    at=basis(scope,left,right,floor)
    masonry=scope.finish('grey stair-side shop brick', (.55,.54,.50), 'brick_wall_08_diff_2k.jpg', .22)
    ashlar=scope.finish('grey worn dressed stone caps', (.76,.75,.73), 'concrete_floor_worn_001_diff_2k.jpg', .24)
    shade=scope.finish('dark recessed unregistered shop', (.10,.129,.107))
    mint=scope.finish('celadon mosaic tiles',(.53,.68,.60),TEXTURE+'north-celadon-mosaic.jpg',.16)
    stall_door=scope.finish('dark enamel gate with weathered steel',(.14,.22,.20),'rusty_painted_metal_diff_2k.jpg',.10,metal=.58)
    plaster=scope.finish('soft grey balcony slab face', (.71,.72,.64), 'concrete_wall_006_diff_2k.jpg', .27)
    rod=scope.finish('black metal protection rails', (.14,.17,.16), metal=.51)
    canopy=scope.finish('aged cyan canopy metal', (.30,.46,.41), 'rusty_painted_metal_diff_2k.jpg', .27)
    frontage=scope.mesh('Review43_SouthRecessedBrickFrontage')
    upper=scope.mesh('Review43_MosaicReturnBalconiesAndWindowGuards')
    paving=scope.mesh('Review43_SouthStepsAndBrickPublicEdge')
    signs=scope.mesh('Review43_RegisteredGreenFascia', UVSurface)
    # The registered sign span fixes the public frontage. The landing above
    # keeps its original treads. Joinery follows the visible bay proportions.
    for a,b in ((-2.18,-1.37),(-.78,-.13),(3.74,4.32),(5.69,6.17)):
        box(frontage,at,a,b,.08,.49,-.20,2.44,masonry)
        box(frontage,at,a-.048,b+.048,.025,.53,2.42,2.55,ashlar)
    box(frontage,at,-.092,3.677,.052,.31,2.01,2.53,masonry)
    box(frontage,at,-.018,3.693,-.015,.072,2.032,2.473,rod)
    placard(scope,signs,at,'liangting-shop',0,3.667,-.022,2.064,2.444)
    for u in (.01,3.61):
        box(frontage,at,u,u+.065,.003,1.10,1.94,2.027,ashlar)
    for a,b in ((.18,.89),(.96,1.67)):
        box(frontage,at,a,b,.77,.832,.32,1.20,stall_door)
        for z in (.34,1.198,2.01):
            box(frontage,at,a,b,.743,.79,z,z+.032,rod)
        for i in range(7):
            u=a+(b-a)*i/6
            box(frontage,at,u,u+.026,.734,.784,1.19,2.04,rod)
    for u in (.838,1.015):
        box(frontage,at,u-.016,u+.016,.701,.755,1.103,1.278,ashlar)
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
            # The printed joint pattern has a 16 mm tile pitch at this UV scale.
            box(upper,at,u0,u1,-depth-.038,-depth+.008,low+.735,low+.797,ashlar)
    scope.points['43'] = [[105.06,162.10,scope.floor(105.06,162.10)+.04], list(at(1.4,.15,1.45))]
