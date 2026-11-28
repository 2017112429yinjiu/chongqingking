"""Public lane section between the 46 station and the shared 45/46 pier."""
from math import ceil
from pathlib import Path
import runpy

import bpy

from build import box

GROUPS = Path(__file__).resolve().parents[2]/'street_groups'


def side_shops(scope, edge):
    facade = scope.mesh('Review46_SteppedPublicShopRevealsAndFoldingAwnings')
    brick = scope.finish('lane grey fired brick',(.55,.56,.52),'brick_wall_08_diff_2k.jpg',.14)
    cap = scope.finish('lane weathered flag lintel',(.76,.76,.72),'concrete_floor_worn_001_diff_2k.jpg',.16)
    oak = scope.finish('lane dark timber stall fittings',(.39,.31,.25),'wood_table_worn_diff_2k.jpg',.11)
    blue = scope.pbr('lane weathered blue folded awning',(.29,.48,.67),
                     'chongqing_district_rusty_painted_metal_diff_2k.jpg',
                     'district_500/acceptance_textures/washed-stone-normal.jpg',
                     'district_500/acceptance_textures/washed-stone-rough.jpg',tint=(.34,.56,.88))
    shadow = scope.finish('lane shop reveal',(.068,.083,.082))
    iron = scope.finish('lane painted metal door bars',(.125,.15,.16),metal=.45)
    for index,(a,b) in enumerate(((1.28,4.35),(4.38,6.98),(7.015,9.60),(9.65,12.19))):
        offset=.10*(index%2)
        front=1.34+offset
        back=2.29+offset
        box(facade,edge.at,a,b,front,back,-.47,-.103,brick)
        box(facade,edge.at,a,b,front-.04,back,-.103,-.043,cap)
        box(facade,edge.at,a+.04,b-.04,back-.067,back,-.09,1.78,shadow)
        for u in (a,b-.20):
            box(facade,edge.at,u,u+.20,front,back,-.12,1.83,brick)
        box(facade,edge.at,a,b,front-.064,back,1.65,1.82,brick)
        box(facade,edge.at,a+.24,b-.25,front,front+.5,.34,.445,oak)
        for j in range(1,6):
            u=a+.21+(b-a-.42)*j/6
            box(facade,edge.at,u,u+.022,front+.39,front+.43,.46,1.61,iron)
        if index%2:
            box(facade,edge.at,a+.24,b-.26,front-.004,front+.025,1.47,1.57,oak)

        top=1.94+index*.045
        high_edge=front+.47
        lip=front-.36
        folds=ceil((b-a)/.110)
        for step in range(folds):
            u=a+(b-a)*step/folds
            v=a+(b-a)*(step+1)/folds
            for start,stop,lo,hi in ((lip-.08,lip,top-.56,top-.36),(lip,high_edge,top-.36,top)):
                # Both sides face daylight when viewed from below the fold.
                profile=[edge.at(u,start,lo),edge.at(v,start,lo+.012),
                         edge.at(v,stop,hi+.012),edge.at(u,stop,hi)]
                facade.face(profile,blue)
                facade.face(profile[::-1],blue)
        for u in (a+.11,b-.095):
            box(facade,edge.at,u,u+.033,lip+.023,front+.44,top-.35,top-.319,iron)


def lane_walk_read(scope, edge):
    ground=scope.mesh('Review46_ConcreteDescentAndStoneMargins')
    concrete=[scope.finish(f'public lane grey concrete {i+1}',c,'concrete_floor_worn_001_diff_2k.jpg',.18)
              for i,c in enumerate(((.68,.67,.63),(.72,.73,.70),(.63,.65,.63)))]
    cut=scope.finish('lane grey stone threshold aggregate',(.66,.67,.64),'stone_floor_diff_2k.jpg',.12)
    # Center strip has the same grade as the installed collider. Its stone
    # margins fit inside the existing stair and parapet corridor.
    for i in range(38):
        a=.02+i*.31
        b=min(a+.31,edge.stations[-1])
        if b <= a:
            break
        for x,y,material,height in ((-.81,-.61,cut,.074),(-.61,.61,concrete[(i%9==0)+(i%13==0)],.074),
                                    (.61,.81,cut,.074)):
            ground.face([edge.at(s,t,height) for s,t in ((a,x),(b,x),(b,y),(a,y))],material)


def parapet(scope, edge):
    masonry = scope.mesh('Review46_GreyParapetWithContinuousRailAndSeat')
    gray = scope.finish('lane right grey dressed brick',(.54,.56,.54),'brick_wall_08_diff_2k.jpg',.18)
    pale = scope.finish('lane blue grey pier coping',(.78,.78,.73),'stone_wall_05_diff_2k.jpg',.16)
    iron = scope.finish('lane slim dark fence',(.13,.142,.134),metal=.42)
    timber = scope.finish('lane worn slatted seat',(.53,.40,.30),'wood_table_worn_diff_2k.jpg',.14)
    for i in range(18):
        a=.70+i*.60
        b=a+.598
        # Match and dress the old parapet collision and use the same geometry
        # along the entire visible lane rather than extending across the mouth.
        for low,high in ((-.12,.17),(.18,.383),(.394,.601)):
            box(masonry,edge.at,a,b,-1.056,-.822,low,high,gray)
        box(masonry,edge.at,a-.005,b+.004,-1.102,-.789,.602,.742,pale)
        for h in (.81,1.27):
            box(masonry,edge.at,a,b,-.956,-.908,h,h+.04,iron)
        for s in (a+.064,a+.207,a+.353,a+.502):
            box(masonry,edge.at,s,s+.022,-.942,-.920,.735,1.33,iron)
    for s in (1.00,4.41):
        box(masonry,edge.at,s,s+.143,-1.39,-1.15,-.18,.41,pale)
    for j in range(4):
        d=-1.54+j*.092
        box(masonry,edge.at,1.03,4.50,d,d+.083,.407,.465,timber)


def lane_canopies(scope, edge):
    source = runpy.run_path(str(GROUPS/'nanqu_rail_grade/build_landside.py'))
    leaf=scope.finish('lane mature leafy canopy',(.32,.45,.21),'island_tree_01_leaves_diff_2k.jpg',.16)
    for i,(s,t,width,yaw) in enumerate(((2.52,-2.11,3.60,.19),(7.24,-2.82,3.13,.84),(10.1,2.88,2.58,1.33))):
        e,n,z=edge.at(s,t,.02)
        donor='Outer500_Plant_036'
        stem=bpy.context.scene.objects[donor]
        scale=.78+i*.034
        name=f'Review46_PublicShadeTree_{i+1}'
        scope.trees.append(dict(name=name,donor=donor,enu=[e,n,z],yaw=yaw,scale=scale))
        seed=4620+i
        data=source['canopy'](name,source['lower_lobes'](seed),seed,leaf,
                              spread=1.13,leaf_size=(.046,.074),density=65)
        crown=bpy.data.objects.new(name+'Leaves',data)
        crown.location=(e,n,z+.70)
        crown.rotation_euler.z=yaw
        crown.scale=(width,width*.95,stem.dimensions.z*scale)
        bpy.context.collection.objects.link(crown)
        scope.attached_art.append(crown)


def finish_lane(scope, edge):
    side_shops(scope,edge)
    lane_walk_read(scope,edge)
    parapet(scope,edge)
    lane_canopies(scope,edge)
