"""Model the visible finish of the existing Changbin Road garage frontage."""
from math import ceil
from pathlib import Path
import runpy

from mathutils import Vector

GROUP = Path(__file__).resolve().parents[2]/'riverside/bridge_58_61/build.py'
MAP = 'district_500/acceptance_textures/'


def finish_public_garage(scope):
    # Keep the original visible slab, columns and collision owner. This finish
    # follows the actual outward edge, including the turn visible from eyes 2–4.
    source=runpy.run_path(str(GROUP),init_globals={'CQ_RAIL_FUNCTIONS_ONLY': True})
    sweep=source['sweep']
    front=[Vector(p) for p in source['GARAGE_FRONT']]
    points=[front[0]]
    for a,b in zip(front,front[1:]):
        count=ceil((b-a).length/5.55)
        points.extend(a.lerp(b,i/count) for i in range(1,count+1))
    points=[p for p in points if -146. < p.x < -64.]
    levels=[(p,11.06+.039*(p.x+103.)) for p in points]
    assert len(levels)>12,len(levels)
    maps=(MAP+'washed-stone-normal.jpg',MAP+'washed-stone-rough.jpg')
    stone='district_r21/terraces_washed_sandstone.jpg'
    pale=scope.pbr('visible garage pale buff fascia',(.87,.79,.64),stone,*maps,tint=(.93,.85,.70),ambient=.22)
    sill=scope.pbr('visible garage pale sill return',(.69,.65,.56),stone,*maps,tint=(.78,.71,.56))
    concrete=scope.finish('visible garage recessed dark soffit',(.23,.25,.25),'concrete_wall_006_diff_2k.jpg',.09)
    dark=scope.finish('visible lower garage recessed louvre channel',(.115,.134,.13),'rusty_painted_metal_diff_2k.jpg',.08,metal=.3)
    iron=scope.finish('visible garage weathered grey louvre blades',(.34,.38,.35),'rusty_painted_metal_diff_2k.jpg',.12,metal=.4)
    reveal=scope.mesh('Review56_ChangbinRoadVisibleFasciaAndDeepOpenings')
    louvres=scope.mesh('Review56_ChangbinRoadLowerRecessedLouvres')
    offsets=(-7.74,-5.08,-2.46)
    for offset in offsets:
        # Face the installed front at -0.36 m. The former trim at -0.395 m
        # sits behind the new fine grooves, which are the visible seam edges.
        for lower, upper in ((-.226,-.058),(-.039,.089),(.108,.244),(.263,.452)):
            sweep(reveal,levels,[(-.465,offset+lower),(-.335,offset+lower),
                                 (-.335,offset+upper),(-.465,offset+upper)],pale)
        for joint in (-.048,.099,.254):
            sweep(reveal,levels,[(-.434,offset+joint-.009),(-.388,offset+joint-.009),
                                 (-.388,offset+joint+.009),(-.434,offset+joint+.009)],sill)
        sweep(reveal,levels,[(-.447,offset+.452),(.12,offset+.452),
                             (.12,offset+.50),(-.415,offset+.50)],sill)
    for i,((a,za),(b,zb)) in enumerate(zip(levels,levels[1:])):
        direction=(b-a).normalized()
        normal=Vector((-direction.y,direction.x))
        def point(u,v,delta):
            e,n=a.lerp(b,u)+normal*v
            return e,n,za+(zb-za)*u+delta
        def slab(mesh, ua, ub, va, vb, lo, hi, mat):
            corners=((ua,va),(ub,va),(ub,vb),(ua,vb))
            mesh.solid([point(u,v,lo) for u,v in corners],[point(u,v,hi) for u,v in corners],mat)
        width=(b-a).length
        jamb=.20/width
        for offset in offsets:
            # Pale heads and paired returns separate the real dark openings.
            slab(reveal,.03,1-.03,-.18,.35,offset+2.34,offset+2.43,pale)
            slab(reveal,.03,1-.03,.34,1.02,offset+2.29,offset+2.34,concrete)
            for u in (.05,.96-jamb):
                slab(reveal,u,u+jamb,-.17,.82,offset+.47,offset+2.36,pale)
        # Lower slatted face follows the street-confirmed reach. It is set
        # behind jambs and keeps the bands, cast columns and vehicle opening.
        if i<len(levels)-3:
            for left,right in ((.05,.466),(.515,.946)):
                slab(louvres,left,right,.46,.498,-9.75,-8.01,dark)
                for j in range(14):
                    z=-9.72+j*.119
                    slab(louvres,left,right,.276,.325,z,z+.037,iron)
                slab(louvres,left-.012,left+.022,.254,.369,-9.77,-8.003,sill)
                slab(louvres,right-.023,right+.010,.254,.369,-9.77,-8.003,sill)
