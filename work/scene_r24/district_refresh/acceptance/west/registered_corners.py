"""Public West wall return and Matix lane entrance registered to the field eyes."""
from pathlib import Path
from random import Random
import runpy

from mathutils import Vector

from build import ASSETS, box, read

HERE = Path(__file__).resolve().parent
STREETS = HERE.parents[1]/'street_groups'
Edge = runpy.run_path(str(STREETS/'north_edges/build.py'))['Edge']


def wall30(scope):
    route=read(STREETS/'western_public_30_31_33_49/field.json')['public_lines']['30']
    line=Edge([(-204.735,140.05),*route],scope.ground)
    backing=scope.mesh('Review30_PublicWallWindowReturn')
    stone=scope.mossy_wall('30 large shaded wall limestone',(.50,.53,.44))
    stone_base=scope.finish('30 wall foot with runoff stains',(.53,.55,.49),'stone_wall_05_diff_2k.jpg',.16)
    paint=scope.finish('30 pale plaster below small windows',(.76,.74,.67),'concrete_wall_006_diff_2k.jpg',.17)
    wood=scope.finish('30 worn vertical wood panels',(.47,.37,.26),'wood_table_worn_diff_2k.jpg',.11)
    dark=scope.finish('30 recessed unbranded window',(.085,.13,.105))
    glass=scope.finish('30 uneven window panes',(.30,.42,.33),metal=.28,rough=.34)
    iron=scope.finish('30 window grid and sill ends',(.155,.19,.15),metal=.36)
    curb=scope.finish('30 shaded grey flags',(.68,.69,.65),'stone_floor_diff_2k.jpg',.13)
    rng=Random(30182)
    a,b=1.68,3.52
    box(backing,line.at,a-.12,b+.12,-2.08,-1.31,-.095,.13,stone_base)
    box(backing,line.at,a-.13,b+.13,-2.09,-1.30,.13,.161,curb)
    box(backing,line.at,a,b,-2.03,-1.77,.11,.31,stone)
    box(backing,line.at,a,b,-2.01,-1.78,.28,.97,paint)
    for i in range(16):
        u=a+.026+i*.113
        box(backing,line.at,u,u+.094,-1.794,-1.747,.307,.938,wood)
    for x,y in ((a,a+.15),(b-.17,b),(a+.83,a+.98)):
        box(backing,line.at,x,y,-2.02,-1.73,.944,2.12,paint)
    box(backing,line.at,a,b,-1.96,-1.71,.945,1.015,stone_base)
    box(backing,line.at,a,b,-2.08,-1.66,1.98,2.16,stone)
    box(backing,line.at,a+.15,b-.16,-2.03,-1.97,.96,1.98,dark)
    for i in range(8):
        u=a+.173+i*.189
        h=.99+.025*(i%3)
        if i%4!=2:
            box(backing,line.at,u,u+.153,-1.953,-1.94,h,1.955,glass)
        box(backing,line.at,u,u+.021,-1.82,-1.789,1.01,1.97,iron)
    for h in (1.016,1.48,1.951):
        box(backing,line.at,a+.145,b-.157,-1.825,-1.782,h,h+.03,iron)

    # Two returns describe what can be seen from the public lane. The open
    # section between them leaves the old transport route intact.
    for row in range(6):
        for x,y in ((.69,a-.11),(b+.10,5.75)):
            u=x+.10*(row%2)
            while u<y-.10:
                v=min(y,u+rng.uniform(.38,.75))
                z=.344*row
                box(backing,line.at,u,v-.014,-2.64,-1.88+rng.uniform(-.046,.04),z-.10,z+.23,stone)
                u=v
    for start,end in ((3.92,4.21),(5.41,5.69)):
        for row in range(7):
            z=row*.268
            box(backing,line.at,start,end,2.51,2.94,z-.035,z+.221,stone_base)
    box(backing,line.at,3.87,5.73,2.45,2.98,1.82,2.065,paint)
    box(backing,line.at,3.87,5.73,2.47,2.99,2.065,2.133,stone)

    ground=scope.mesh('Review30_PublicUnderCanopyCutStone')
    for i in range(22):
        u=.19+i*.302
        for j in range(5):
            v=-1.72+j*.39+(.06 if i%2 else 0.)
            corners=[line.at(s,t,.013) for s,t in ((u,v),(u+.292,v),(u+.292,v+.374),(u,v+.374))]
            ground.face(corners,curb if j>1 else stone_base)


def entrance34(scope):
    controls=read(HERE/'corner-register.json')['34']
    target=controls['measured_top']['enu']
    grade=read(ASSETS/'district_500/mati-34-35.json')['walks']['34']
    old=grade[0]
    approach=[(-65.20,165.02),(-66.96,164.99),(-68.58,164.56),(old[0],old[1])]
    edge=Edge(approach,scope.ground)
    levels=[scope.floor(*approach[0])+.017,scope.floor(*approach[1])+.018,
            (scope.floor(*approach[1])+old[2])*.5,old[2]]
    assert .15<levels[0]-levels[-1]<2.4, levels
    pavement=scope.mesh('COL_Review34_MatixStreetLinkApron')
    flags=scope.mesh('Review34_GreyStoneStreetTurnAndStep')
    ash=scope.finish('34 close cut grey flags',(.73,.74,.70),'stone_floor_diff_2k.jpg',.17)
    granite=scope.finish('34 tread arrises and coping',(.80,.81,.76),'concrete_floor_worn_001_diff_2k.jpg',.20)
    brick=scope.finish('34 blue grey clay wall feet',(.60,.62,.59),'brick_wall_08_diff_2k.jpg',.16)
    iron=scope.finish('34 slim black uprights',(.092,.116,.103),metal=.49,rough=.53)
    def floor(s,t,offset):
        i=next((i for i,b in enumerate(edge.stations[1:]) if s<b),len(levels)-2)
        d=(s-edge.stations[i])/(edge.stations[i+1]-edge.stations[i])
        e,n=edge.en(s,t)
        return (e,n,levels[i]+(levels[i+1]-levels[i])*d+offset)
    for i,(s,t) in enumerate(zip(edge.stations,edge.stations[1:])):
        # The existing 34 walk begins at the old first post. This layer adds
        # a short physical connection from the adjacent road shoulder.
        corners=[floor(u,v,0) for u,v in ((s,-.79),(t,-.79),(t,.79),(s,.79))]
        pavement.solid([(e,n,min(h-.28,scope.floor(e,n)-.045)) for e,n,h in corners],corners,ash)
        count=1+int((t-s)/.52)
        for j in range(count):
            a=s+(t-s)*j/count
            b=s+(t-s)*(j+1)/count
            for x,y in ((-.785,-.27),(-.26,.27),(.28,.785)):
                flags.face([floor(u,v,.012) for u,v in ((a+.012,x),(b-.012,x),(b-.012,y),(a+.012,y))],ash)
        box(flags,floor,s+.024,t-.024,-.84,-.790,-.047,.052,granite)

    root=(target[0],target[1])
    rim=Edge([root,(-68.72,166.79),(-69.21,168.22)],scope.ground)
    wall=scope.mesh('COL_Review34_RegisteredStairSideWall')
    rails=scope.mesh('Review34_CloseRegisteredBlackRailCorner')
    cap=target[2]-1.08
    def curb(s,t,z):
        e,n=rim.en(s,t)
        return e,n,cap+.047*s+z
    for a,b in zip(rim.stations,rim.stations[1:]):
        f=[curb(u,v,-.08) for u,v in ((a,-.13),(b,-.13),(b,.31),(a,.31))]
        # The measured tip projects just beside the original Matix road trace.
        # Its upper coping can overhang the lower route. Put the load-bearing
        # masonry on the raised side, outside the original walking envelope.
        ledge=[(e,n,z-.22) for e,n,z in f]
        wall.solid(ledge,f,brick)
        first,last=rim.en(a,0),rim.en(b,0)
        core=[(-67.79,first.y),(-67.36,first.y),(-67.36,last.y),(-67.79,last.y)]
        foot=[(e,n,scope.floor(e,n)-.085) for e,n in core]
        wall.solid(foot,[(e,n,cap-.175+(a if i<2 else b)*.047) for i,(e,n) in enumerate(core)],brick)
        connector=[(e,n,z-.03) for e,n,z in f]
        connector[0]=(-67.38,*connector[0][1:])
        connector[1]=(-67.38,*connector[1][1:])
        wall.solid([(e,n,z-.18) for e,n,z in connector],connector,granite)
        box(wall,curb,a,b,-.17,.357,-.098,.008,granite)
        for h in (.11,1.05):
            box(rails,curb,a,b,-.026,.026,h,h+.03,iron)
        for i in range(int((b-a)/.129)):
            u=a+.058+i*.129
            box(rails,curb,u,u+.018,-.017,.017,.09,1.063,iron)
        box(rails,curb,a,a+.049,-.038,.036,.001,1.079,iron)
    for i in range(3):
        a=.12+i*.27
        box(flags,curb,a,a+.25,.312,.99-.16*i,-.62,-.44+.16*i,granite)
    scope.points['34-street']=[list(floor(.03,0,.035)),list(floor(edge.stations[-1]-.06,0,.035))]
