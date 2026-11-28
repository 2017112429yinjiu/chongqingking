"""Finish the market's working counter, the mapped gate and the public planter."""
from math import cos, pi, sin
from pathlib import Path
import sys

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from build import ASSETS, box, read
sys.path.insert(0,str(HERE))
from details import gate_wings, market_goods, planted_bed

STREETS = HERE.parents[1]/'street_groups'


def market(scope):
    plot = next(row for row in read(ASSETS/'district_500/layout.json')['plots'] if row['plot_id']==1)
    east,north=plot['east_north']
    s,c = sin(plot['bearing']),cos(plot['bearing'])
    def point(u,v,z):
        return (east+c*u-s*v,north+s*u+c*v,plot['height']+z)

    board=scope.mesh('Review01_MarketServingCounterAndLamps')
    tile=scope.finish('glazed celadon work counter',(.41,.65,.52),'concrete_wall_006_diff_2k.jpg',.20)
    zinc=scope.finish('rolled zinc counter edge',(.48,.51,.47),metal=.29,rough=.55)
    wood=scope.finish('worn timber edges and hooks',(.57,.41,.27),'wood_table_worn_diff_2k.jpg',.3)
    cream=scope.finish('shelf and opal reflector',(.78,.73,.58),shaded=.40)
    joint=scope.finish('dark counter grout',(.14,.168,.147))
    copper=scope.finish('market worn brass',(.31,.245,.138),metal=.25,rough=.62)
    # Two already-working counters have opposite presentation faces. These
    # fittings stay on the cabinet face and above eye height of the public aisle.
    for side in (1,-1):
        inner=plot['door_u']+side*1.91
        low,high=sorted((inner-side*.034,inner-side*.011))
        surface=tile if side>0 else wood
        box(board,point,low,high,-1.42,1.42,.052,.678,surface)
        box(board,point,low-.008,high+.008,-1.46,1.46,.064,.113,zinc)
        box(board,point,low-.009,high+.009,-1.46,1.46,.663,.710,zinc)
        if side>0:
            for k in range(15):
                y=-1.40+k*.196
                box(board,point,low-.002,high+.002,y,y+.009,.114,.66,joint)
            for z in (.275,.455):
                box(board,point,low-.003,high+.003,-1.4,1.4,z,z+.008,joint)
        else:
            for y in (-1.05,-.36,.37,1.05):
                box(board,point,low-.011,high+.011,y-.032,y+.03,.37,.49,copper)
        # Hanging reflectors are attached to a ceiling rose and thin cable.
        x=inner+side*.35
        for y in (-.86,.91):
            box(board,point,x-.06,x+.06,y-.06,y+.06,2.755,2.792,zinc)
            box(board,point,x-.009,x+.009,y-.009,y+.009,2.41,2.76,joint)
            for t in range(16):
                a,b=t*pi/8,(t+1)*pi/8
                board.face([point(x+.14*cos(a),y+.14*sin(a),2.32),point(x+.14*cos(b),y+.14*sin(b),2.32),
                            point(x+.044*cos(b),y+.044*sin(b),2.46),point(x+.044*cos(a),y+.044*sin(a),2.46)],zinc)
            board.face([point(x+.126*cos(t*pi/8),y+.126*sin(t*pi/8),2.324) for t in reversed(range(16))],cream)
    market_goods(scope,plot,point)
    scope.points['01']=[[161.1106872559,113.9294586182,38.1440849304],[166,123,39.55]]


def gate(scope):
    field=read(STREETS/'zhongxing_public_10_12_13_22/field.json')
    e,n=field['gate_control']['match_en']
    # Exact registration of the north-running opening and existing two roof tiers.
    def surface(s,d,z):
        east=e-d
        north=n-3.75+s
        return (east,north,scope.floor(east,north)+z)

    roof=scope.mesh('Review12_TwoCoursedCeramicEaves')
    trim=scope.mesh('Review12_RafterAndStoneFootContacts')
    ceramic=[scope.finish('ceramic weather tone '+str(i),color,'roof_tiles_diff.jpg',.14) for i,color in enumerate((
        (.50,.49,.46),(.58,.58,.55),(.49,.51,.54)))]
    beam=scope.finish('faded red rafter ends',(.37,.151,.112),'wood_table_worn_diff_2k.jpg',.31)
    core=scope.finish('shadow in the eaves',(.12,.104,.085))
    coping=scope.finish('grey gate stone bases',(.59,.62,.61),'concrete_floor_worn_001_diff_2k.jpg',.18)
    for a,b,c,d,h in ((2.16,5.21,-.78,1.37,2.55),(2.46,5.42,-.33,1.55,3.08)):
        ridge=(c+d)*.5
        def level(v):
            return h+.48*(1.-abs(v-ridge)/((d-c)*.5))
        for lo,hi in ((c,ridge),(ridge,d)):
            floor=[surface(s,v,level(v)) for s,v in ((a,lo),(b,lo),(b,hi),(a,hi))]
            roof.solid(floor,[(x,y,z+.058) for x,y,z in floor],core)
        divisions=int((b-a)/.108)
        for i in range(divisions):
            x0=a+(b-a)*i/divisions
            x1=a+(b-a)*(i+1)/divisions
            for lo,hi in ((c,ridge),(ridge,d)):
                for j in range(4):
                    v0,v1=lo+(hi-lo)*j/4,lo+(hi-lo)*(j+1)/4
                    for q0,q1,z0,z1 in ((0,.27,.06,.097),(.27,.68,.097,.101),(.68,1,.101,.062)):
                        u0=x0+(x1-x0)*q0; u1=x0+(x1-x0)*q1
                        roof.face([surface(u0,v0,level(v0)+z0-.013),surface(u1,v0,level(v0)+z1-.013),
                                   surface(u1,v1,level(v1)+z1),surface(u0,v1,level(v1)+z0)],ceramic[(i+3*j)%3])
            if i%3==0:
                box(trim,surface,x0,x0+.055,c-.055,c+.36,h-.075,h+.016,beam)
        for edge_position in (a,b-.045):
            for p0,p1 in ((c,ridge),(ridge,d)):
                roof.face([surface(edge_position,p0,level(p0)+.022),surface(edge_position,p1,level(p1)+.022),
                           surface(edge_position+.045,p1,level(p1)+.132),surface(edge_position+.045,p0,level(p0)+.132)],ceramic[1])
        box(trim,surface,a-.03,b+.04,ridge-.036,ridge+.036,h+.52,h+.64,ceramic[1])
    for s in (2.62,4.72):
        box(trim,surface,s-.076,s+.224,-.227,.255,.313,.371,coping)
        box(trim,surface,s-.024,s+.186,-.176,.213,1.944,2.014,beam)
    gate_wings(scope,surface)
    scope.retired.append('Zhongxing12_OverlappingTileEaves')
    route=read(ASSETS/'district_500/zhongxing-public-10-12-13-22.json')['walks']['12']
    scope.points['12']=[route[0],[e,n,scope.floor(e,n)+1.4]]


def plaza(scope):
    spec=read(STREETS/'zhongxing_plaza22_finish/field.json')['approximate_local_plan']
    e,n=spec['center']; theta=spec['bearing_degrees']*pi/180
    axis=Vector((cos(theta),sin(theta))); across=Vector((-sin(theta),cos(theta)))
    top=34.766+.021*(n-81.42)-.009*(e-112)+.55
    radius=spec['round_end_radius_m']; half=spec['straight_half_length_m']; center=Vector((e,n))
    cap=scope.mesh('Review22_FittedCopingBlocks')
    finish=[scope.finish('bush hammered coping '+str(i),color,'concrete_wall_006_diff_2k.jpg',.22)
            for i,color in enumerate(((.64,.65,.63),(.70,.70,.68),(.60,.63,.61)))]
    def shape(inset):
        return [center+axis*(sign*half+(radius-inset)*cos(angle))+across*((radius-inset)*sin(angle))
                for sign,start in ((1,-pi/2),(-1,pi/2)) for angle in (start+i*pi/23 for i in range(24))]
    outer,inner=shape(.025),shape(.235)
    for i in range(0,len(outer),3):
        j=(i+3)%len(outer)
        for k in range(3):
            x=(i+k)%len(outer); y=(x+1)%len(outer)
            start=.037 if k==0 else 0; end=.963 if k==2 else 1
            a,b=outer[x].lerp(outer[y],start),outer[x].lerp(outer[y],end)
            d,c=inner[x].lerp(inner[y],start),inner[x].lerp(inner[y],end)
            cap.solid([(*p,top-.012) for p in (a,b,c,d)],[(*p,top+.026) for p in (a,b,c,d)],finish[(i//3)%3])
    planted_bed(scope,shape,center,axis,across,half,radius,top)
    route=read(ASSETS/'district_500/zhongxing-plaza-22-finish.json')['walks']['22']
    scope.points['22']=[route[0],[e,n,top]]


def make(scope):
    market(scope)
    gate(scope)
    plaza(scope)
