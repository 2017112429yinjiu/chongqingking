"""Street-facing wall, canopy and public footing in the west groups."""
from math import cos, sin, pi
from pathlib import Path
from random import Random
import runpy

from mathutils import Vector

from build import ASSETS, box, read

STREETS=Path(__file__).resolve().parents[2]/'street_groups'
Edge=runpy.run_path(str(STREETS/'north_edges/build.py'))['Edge']


def trees(scope, edge, entries, prefix, donor='Outer500_Plant_001'):
    for number,(station,offset,scale) in enumerate(entries,1):
        e,n,z=edge.at(station,offset,-.025)
        scope.trees.append({'donor':donor,'name':prefix+'%02d'%number,'enu':[e,n,z],
                            'scale':scale,'yaw':.62+number*1.72})


def paving(mesh, edge, length, low, high, finish, seam=None, step=.62):
    runs=int(length/step)
    for i in range(runs):
        a,b=i*step+.012,(i+1)*step-.012
        box(mesh,edge.at,a,b,low,high,-.025,.019,finish)
        if seam:
            box(mesh,edge.at,b,b+.021,low,high,-.026,.012,seam)


def western_wall(scope):
    walk=read(ASSETS/'district_500/western-public-30-31-33-49.json')['walks']
    stations=[(-204.93,140.44)]+[p[:2] for p in walk['31']]
    edge=Edge(stations,scope.ground)
    rng=Random(3031)
    rough=[scope.mossy_wall('green retaining stone '+str(i),c) for i,c in enumerate(
        ((.55,.59,.49),(.47,.49,.43),(.61,.59,.52)))]
    cement=scope.finish('weathered grey flag shore',(.65,.63,.60),'concrete_floor_worn_001_diff_2k.jpg',.24)
    dark=scope.finish('stone foot runoff sediment',(.27,.30,.20),'leaf_scattered_gravel_diff_2k.jpg',.12)
    moist=scope.finish('dark damp foundation stone',(.30,.34,.26), 'moss_grime_diff.png', .21)
    green=[scope.finish('hanging vine leaflet %d'%i,c,rough=.70) for i,c in enumerate(
        ((.21,.37,.10),(.28,.46,.13),(.15,.29,.080),(.35,.49,.19)))]
    wall=scope.mesh('COL_Review3031_GroundedMossRetainingCourse')
    ivy=scope.mesh('Review3031_RootedHangingVineAndDripEdge')
    step=scope.mesh('Review3031_StoneWallSidePavingAndLanding')
    a,b=.12,edge.stations[-1]-.22
    # Leave an unobstructed side strip beside the registered public traces.
    for row in range(6):
        s=a+.12*(row%2)
        while s<b-.10:
            t=min(b,s+rng.uniform(.48,1.31))
            height=.43*row
            box(wall,edge.at,s,t-.016,-2.24,-1.69-rng.uniform(.0,.10),height-.13,height+.304,rough[(row+rng.randrange(4))%3])
            s=t
    paving(step,edge,b,-1.63,-.73,cement,dark,.63)
    for s in (.24,3.08,5.86,9.39):
        if s+.68>b: continue
        box(ivy,edge.at,s,s+.66,-1.70,-1.66,.015,.32,moist)
    for anchor in (1.9,3.7,5.9,7.62,9.83):
        if anchor>b-.1:continue
        for i in range(16):
            s=max(.09,min(b-.02,anchor+rng.uniform(-.62,.59)))
            start=rng.uniform(.21,.9)
            end=2.48+rng.uniform(-.14,.23)
            for j in range(11):
                h=start+(end-start)*j/10
                p=edge.at(s+.06*sin(j*.92+i),-1.637+.063*sin(j*.53),h)
                width=rng.uniform(.030,.062)
                v=Vector(p)
                points=[(v.x-width,v.y,v.z),(v.x-width*.24,v.y+.055,v.z-.049),
                        (v.x+width,v.y,v.z+.012),(v.x+width*.27,v.y+.028,v.z+.046)]
                ivy.face(points,green[(i+j)%4])
                ivy.face([(x,y-.001,z)for x,y,z in points[::-1]],green[2])
    trees(scope,edge,[(.6,-2.65,.54),(4.0,-2.81,.62),(7.0,-2.94,.57),(10.2,-2.87,.63)],'Western3031Overhang_')
    for i,(e,n) in enumerate(((-202.27,136.68),(-209.87,137.28)),5):
        z=scope.floor(e,n)-.025
        scope.trees.append({'donor':'Outer500_Plant_001','name':f'Western3031Overhang_{i:02d}',
                            'enu':[e,n,z],'scale':.84,'yaw':.59*i})



def mati(scope):
    spec=read(STREETS/'matix_34_35/field.json')['public_approach']
    concrete=scope.finish('Mati street dressed flags',(.73,.73,.70),'concrete_floor_worn_001_diff_2k.jpg',.28)
    stone=scope.finish('Mati street low blue grey bricks',(.57,.59,.55),'brick_wall_08_diff_2k.jpg',.18)
    trim=scope.finish('Mati street stone seam',(.26,.269,.258))
    iron=scope.finish('Mati street black bars',(.094,.118,.113),metal=.42)
    green=scope.finish('Mati wall earth and leaf edges',(.32,.37,.22),'leaf_scattered_gravel_diff_2k.jpg',.12)
    for id in ('34','35'):
        road=Edge(spec[id]['path'],scope.ground)
        # The two public blocks use a common roadside detail. Their obscured
        # rear buildings and the yards on the other side keep the prior bulk.
        extent=road.stations[-1]-.14
        holder=scope.mesh('COL_Review'+id+'_PublicGrayWallAndStoneCoping')
        foot=scope.mesh('Review'+id+'_PublicFlagsAndLinearDrain')
        rails=scope.mesh('Review'+id+'_FineBlackRails')
        for k in range(int(extent/.77)):
            a=k*.77;b=a+.743
            box(holder,road.at,a,b,1.39,1.92,-.125,.645,stone)
            box(holder,road.at,a-.009,b+.009,1.344,1.95,.646,.712,concrete)
            box(rails,road.at,a+.047,a+.085,1.57,1.626,.703,1.584,iron)
            box(rails,road.at,a+.05,b+.027,1.583,1.621,1.517,1.555,iron)
            box(rails,road.at,a+.06,b+.027,1.582,1.624,.792,.821,iron)
            for i in range(1,7):
                s=a+.09+i*.082
                box(rails,road.at,s,s+.016,1.589,1.610,.803,1.534,iron)
        paving(foot,road,extent,.74,1.32,concrete,trim,.45)
        for i in range(int(extent/.51)):
            s=.14+i*.51
            if s+.43>=extent:break
            box(foot,road.at,s,s+.41,.64,.741,-.026,.006,trim)
            for k in range(8):
                t=s+.02+k*.047
                box(foot,road.at,t,t+.019,.663,.723,.002,.015,iron)
        box(foot,road.at,.12,extent,1.92,2.09,-.051,.011,green)
        trees(scope,road,[(i,2.39,.40+(i%2)*.07) for i in (1.3,5.8,9.9) if i<extent],
              'MatiStreetTree'+id+'_')


def lower_49(scope):
    stored=read(ASSETS/'district_500/western-public-30-31-33-49.json')['walks']['49']
    road=Edge([(-242.67,9.65),(-241.60,12.80)]+[p[:2] for p in stored],scope.ground)
    stone=scope.finish('49 low street grey pavers',(.69,.70,.68),'concrete_floor_worn_001_diff_2k.jpg',.30)
    grit=scope.finish('49 tree pit leaf gravel',(.44,.44,.35),'leaf_scattered_gravel_diff_2k.jpg',.18)
    kerb=scope.finish('49 readably cut curb stone',(.70,.69,.64),'stone_floor_diff_2k.jpg',.22)
    wall=scope.mossy_wall('49 low slope toe grey masonry',(.49,.51,.45))
    white=scope.finish('49 worn tree trunk whitewash',(.68,.70,.64),rough=.93)
    bins=[scope.finish('49 public blue bin',(.17,.36,.48),metal=.13),scope.finish('49 public dark bin',(.16,.24,.22))]
    black=scope.finish('49 recessed lid slot',(.077,.094,.087))
    paving_mesh=scope.mesh('Review49_LowerStreetPavingAndGravelEdges')
    retaining=scope.mesh('COL_Review49_LowSlopeFooting')
    street_furniture=scope.mesh('Review49_PairedBinsAndTrunkWhitewash')
    end=road.stations[-1]-.055
    paving(paving_mesh,road,end,-.88,.86,stone,grit,.58)
    paving(paving_mesh,road,end,-.99,-.86,kerb,grit,.54)
    pacing=[(s,1.30,.45+((i%3)*.035)) for i,s in enumerate((1.21,4.61,8.17,11.4,14.75)) if s<end-.23]
    for k in range(int(end/.78)):
        a=k*.78;b=a+.754
        box(retaining,road.at,a,b,1.83,2.15,-.19,.68,wall)
        box(retaining,road.at,a-.005,b+.011,1.81,2.19,.68,.744,kerb)
    trees(scope,road,pacing,'Western49FootwayTree_')
    for s,d,_ in pacing:
        e,n,z=road.at(s,d,.015)
        for i in range(12):
            a,b=i*pi/6,(i+1)*pi/6
            part=[(e+.063*cos(t),n+.063*sin(t),z+h) for t,h in ((a,0),(b,0),(b,.69),(a,.69))]
            street_furniture.face(part,white)
    for i in range(2):
        s=4.27+i*.49
        box(street_furniture,road.at,s,s+.42,1.01,1.43,.027,.828,bins[i])
        box(street_furniture,road.at,s+.029,s+.390,1.003,1.048,.655,.775,black)
        box(street_furniture,road.at,s-.013,s+.425,1.0,1.46,.816,.875,bins[i])
