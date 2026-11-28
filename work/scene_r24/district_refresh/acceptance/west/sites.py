"""Reinstate readable stone courses, drains and rail feet along five west routes."""
from pathlib import Path
from random import Random
import runpy
import sys

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from build import ASSETS, apply_finish, box, read

STREETS = HERE.parents[1]/'street_groups'
Edge = runpy.run_path(str(STREETS/'north_edges/build.py'))['Edge']


def bound_point(edge, mesh):
    def point(s,d,z):
        e,n = edge.en(s,d)
        hit = mesh.ray_cast(Vector((e,n,90)),Vector((0,0,-1)),130)[0]
        return (e,n,(hit.z if hit is not None else edge.ground_y((e,n)))+z)
    return point


def paving(scope, edge, surface, name, span, rows, joint):
    seam=scope.mesh(name)
    point=bound_point(edge,surface)
    end=edge.stations[-1]-.20
    for k in range(int((end-.28)/span)+1):
        a=.25+k*span
        b=min(a+span,end)
        if b-a<.06:
            break
        box(seam,point,a,a+.013,-.605,.605,.004,.009,joint)
        for i in range(1,rows):
            d=-.61+i*(1.22/rows)+(.07 if k%2 else -.065)
            box(seam,point,a+.014,b-.015,d,d+.010,.004,.009,joint)
    return point


def slope(scope):
    directory=STREETS/'western_public_30_31_33_49'
    spec=read(directory/'field.json')['public_lines']
    walks=read(ASSETS/'district_500/western-public-30-31-33-49.json')['walks']
    soot=scope.finish('secure damp wall stones',(.48,.50,.48),'stone_wall_05_diff_2k.jpg',.13)
    join=scope.finish('raked old stone joints',(.215,.22,.20))
    steel=scope.finish('oxidised drain bars',(.24,.23,.20),metal=.38,rough=.62)
    greenery=[scope.finish('living wall vine '+str(i),c,shaded=.17) for i,c in enumerate((
        (.16,.30,.106),(.231,.36,.127),(.104,.24,.106)))]
    options={
        '30':('gray-split garden flags',(.72,.75,.73),.56,3),
        '31':('soft weathered lane flags',(.69,.71,.73),.73,2),
        '49':('lower hillside small square flags',(.64,.68,.71),.39,3),
    }
    for id,(label,color,step,rows) in options.items():
        mat=scope.finish(label,color,'concrete_floor_worn_001_diff_2k.jpg',.18)
        edge=Edge(spec[id],scope.ground)
        part=scope.donor(directory/'western-public-30-31-33-49.blend',f'COL_Western{id}_OutdoorStoneFlags')
        support=apply_finish(part,mat,soot)
        point=paving(scope,edge,support,f'Review{id}_StaggeredPublicStoneJoints',step,rows,join)
        scope.points[id]=[walks[id][0],walks[id][-1]]
        if id=='30':
            # The lane stays on the registered public path. Drain crossbars
            # sit in the street edge, beside the wall rather than underfoot.
            grate=scope.mesh('Review30_ShortStoneAndIronGully')
            for s in (1.11,4.84):
                if s+.52>=edge.stations[-1]:
                    continue
                box(grate,point,s,s+.48,.508,.639,.003,.019,join)
                for i in range(8):
                    x=s+.018+i*.056
                    box(grate,point,x,x+.018,.521,.627,.019,.029,steel)
        if id=='31':
            inset=scope.mesh('Review31_VineAndStoneCopingContacts')
            wallmat=scope.finish('leaf shaped damp stone coping',(.60,.64,.61),'stone_wall_05_diff_2k.jpg',.21)
            rng=Random(31)
            for start in (1.68,2.46,3.37,4.41):
                if start+.5>=edge.stations[-1]:
                    continue
                box(inset,edge.at,start,start+.41,-1.085,-.893,.156,.196,wallmat)
                for i in range(12):
                    a=start+rng.uniform(.02,.4); z=rng.uniform(.21,.51)
                    inset.face([edge.at(a,-.888,z-.061),edge.at(a+.063,-.872,z),
                                edge.at(a+.022,-.849,z+.058),edge.at(a-.028,-.873,z)],greenery[i%3])
        if id=='49':
            lip=scope.mesh('Review49_LowerFootwayStoneNosing')
            for i in range(int((edge.stations[-1]-.72)/.48)):
                a=.34+i*.48
                box(lip,point,a,a+.459,-.641,-.573,-.018,.019,soot)


def mati(scope):
    directory=STREETS/'matix_34_35'
    ways=read(directory/'field.json')['public_approach']
    walks=read(ASSETS/'district_500/mati-34-35.json')['walks']
    stone=scope.finish('Mati pale dressed border',(.76,.75,.72),'concrete_floor_worn_001_diff_2k.jpg',.19)
    wall=scope.finish('Mati dark face stone',(.51,.48,.426),'stone_wall_05_diff_2k.jpg',.16)
    steel=scope.finish('Mati weathered iron',(.26,.23,.20),metal=.43,rough=.61)
    rust=scope.finish('Mati fixing bolts',(.47,.32,.216),metal=.3)
    black=scope.finish('Mati wet recess',(.10,.102,.084))
    for id in ('34','35'):
        edge=Edge(ways[id]['path'],scope.ground)
        part=scope.donor(directory/'mati-34-35.blend',f'COL_Mati{id}_PublicApproach')
        surface=apply_finish(part,stone if id=='35' else scope.finish('Mati repaired asphalt',(.62,.61,.56),'asphalt_02_diff_1k.jpg',.18),wall)
        point=bound_point(edge,surface)
        scope.points[id]=[walks[id][0],walks[id][-1]]
        if id=='34':
            grate=scope.mesh('Review34_SecuredDrainCovers')
            scope.retired.append('Mati34_DrainAndKerb')
            for a in (1.30,7.70):
                box(grate,point,a,a+.62,-.685,-.441,.006,.016,black)
                for k in range(10):
                    u=a+.034+k*.055
                    box(grate,point,u,u+.022,-.667,-.455,.013,.024,steel)
                for x in (a+.012,a+.585):
                    box(grate,point,x,x+.023,-.69,-.438,.008,.030,rust)
        else:
            paving(scope,edge,surface,'Review35_DressedStepsideFlags',.61,2,black)
            fastening=scope.mesh('Review35_StoneRailFeetAndFixings')
            for a in (2.77,7.16,11.43):
                box(fastening,edge.at,a-.05,a+.16,1.006,1.217,.903,.942,steel)
                for x in (a-.026,a+.108):
                    box(fastening,edge.at,x,x+.026,1.038,1.064,.934,.959,rust)


def make(scope):
    slope(scope)
    mati(scope)
