"""Street-evidence finish for the market, red eaves and shallow planter."""
from math import cos, pi, sin, sqrt
from random import Random
from pathlib import Path

import bmesh
from mathutils import Vector

from build import ASSETS, box, read


def blade(mesh, anchor, angle, length, width, lift, mats):
    """A tapered rounded leaf with a raised vein and visible abaxial material."""
    along=Vector((cos(angle),sin(angle),0))
    across=Vector((-sin(angle),cos(angle),0))
    verts=[]
    for t,spread,camber in ((0,.055,0),(.19,.59,.43),(.4,.96,.74),(.61,1,1),(.79,.74,.96),(.92,.39,.87),(1,.015,.68)):
        p=anchor+along*(t*length)+Vector((0,0,camber*lift))
        w=width*spread
        ripple=.12*width*sin(t*36+angle)
        verts.append([p-across*w+Vector((0,0,ripple-w*.31)),p,p+across*w+Vector((0,0,-ripple-w*.44))])
    for i,(a,b) in enumerate(zip(verts,verts[1:])):
        for j in (0,1):
            points=(a[j],b[j],b[j+1],a[j+1])
            mesh.face(points,mats[(i+j)%2])
            mesh.face([p-Vector((0,0,.0008)) for p in points[::-1]],mats[-1])
    for a,b in zip(verts[1:-1],verts[2:]):
        mesh.face([a[1]+Vector((0,0,.0012)),b[1]+Vector((0,0,.0012)),
                   b[1]+across*.003,a[1]+across*.003],mats[1])


def canopy(scope, name, positions, rng, tone):
    mesh=scope.mesh(name)
    for center,radius,height,leaf_size,amount in positions:
        e,n,h=center
        for i in range(amount):
            a=rng.random()*2*pi
            r=radius*sqrt(rng.uniform(.03,.95))
            y=height*(.25+.65*sqrt(1-(r/radius)**2))*rng.uniform(.56,1.06)
            root=Vector((e+r*cos(a),n+r*sin(a),h+y))
            blade(mesh,root,a+rng.uniform(-.9,.9),leaf_size*rng.uniform(.5,1.2),
                  leaf_size*rng.uniform(.21,.35),rng.uniform(-.04,.05),tone)
    return mesh


def market_goods(scope, plot, at):
    scope.required_group = 'ZhongxingArcade10'
    scope.retired.append('Outer500_MarketProduce')
    source=Path(__file__).resolve().parents[2]/'street_groups/zhongxing_arcade10/zhongxing-arcade10.blend'
    part=scope.donor(source,'Outer500_Street_furniture')
    mesh=bmesh.new()
    mesh.from_mesh(part.data)
    e,n=plot['east_north'];c,s=cos(plot['bearing']),sin(plot['bearing'])
    slots=read(ASSETS/'district_500/zhongxing-arcade10.json')['borrowed_materials'][part.name]
    leaf_slots={i for i,mat in enumerate(part.data.materials) if mat and slots[mat.name].startswith('Canopy ')}
    old_leaf=[]
    for face in mesh.faces:
        p=part.matrix_world @ face.calc_center_median()
        u=c*(p.x-e)+s*(p.y-n)
        v=-s*(p.x-e)+c*(p.y-n)
        if face.material_index in leaf_slots and .94 < u < 2.28 and abs(v)<1.67 and .75<p.z-plot['height']<1.01:
            old_leaf.append(face)
    assert old_leaf,'No original countertop leaves found'
    bmesh.ops.delete(mesh,geom=old_leaf,context='FACES')
    mesh.to_mesh(part.data)
    mesh.free()
    scope.borrowed[part.name]=slots
    baskets=scope.mesh('Review01_PartitionedMarketTraysAndCrates')
    fruit=scope.mesh('Review01_MixedProduceSkins')
    scope.smooth.add(fruit.name)
    leaves=scope.mesh('Review01_BunchedGreensRoundedLeaves')
    wood=scope.finish('market basket staves',(.63,.45,.30),'wood_table_worn_diff_2k.jpg',.2)
    enamel=scope.finish('market wet goods blue enamel',(.21,.44,.53),metal=.22,rough=.65)
    paper=scope.finish('market folded pale kraft liners',(.60,.54,.37))
    wire=scope.finish('brushed shallow basin edge',(.57,.60,.55),metal=.62,rough=.42)
    colors=[[scope.finish('fruit colour %d %d'%(i,j),rgb,rough=.51 if i<3 else .74)
             for j,rgb in enumerate(row)] for i,row in enumerate((
        ((.76,.30,.037),(.64,.17,.026),(.76,.43,.078),(.54,.23,.069)),
        ((.28,.076,.14),(.40,.098,.126),(.31,.19,.056),(.17,.054,.113)),
        ((.60,.13,.065),(.82,.325,.061),(.42,.37,.044),(.69,.45,.22)),
        ((.57,.45,.31),(.69,.57,.39),(.54,.35,.174),(.47,.41,.30))))]
    stem=scope.finish('market stems and calyx',(.23,.37,.11))
    greens=[scope.finish('vegetable leaf tone %d'%i,t,rough=.73) for i,t in enumerate(
        ((.21,.41,.09),(.43,.59,.23),(.12,.28,.085),(.31,.49,.17),(.66,.70,.36)))]
    rng=Random(12101)

    def rings(dest,u,v,z,rad,kind,phase):
        profiles=(((.02,.28),(.18,.69),(.43,.96),(.67,1),(.86,.75),(.98,.35),(1.01,.06)),
                  ((.02,.15),(.16,.52),(.39,.59),(.73,.48),(1.16,.32),(1.59,.20),(1.69,.03)),
                  ((.02,.25),(.15,.69),(.42,.97),(.65,.90),(.79,.68),(.76,.05)),
                  ((.01,.20),(.19,.68),(.36,.91),(.54,.65),(.68,.45),(.74,.05)))[kind]
        detail=16
        deformation=rng.uniform(.8,1.2)
        appearance=rng.choice(colors[kind])
        rows=[]
        for height,ratio in profiles:
            row=[]
            for j in range(detail):
                a=j*2*pi/detail
                rr=rad*ratio*(1+(.078 if kind==2 else .047)*cos(a*(7 if kind==2 else 3)+phase))
                dx=rr*cos(a)+.56*rad*height if kind==1 else rr*cos(a)*deformation
                dy=rr*sin(a)
                row.append(at(u+dx*cos(phase)-dy*sin(phase),v+dx*sin(phase)+dy*cos(phase),
                              z+rad*(height*deformation+.065*ratio*sin(a))))
            rows.append(row)
        dest.face(rows[0][::-1],appearance)
        for old,new in zip(rows,rows[1:]):
            for j in range(detail):
                k=(j+1)%detail
                dest.face([old[j],old[k],new[k],new[j]],appearance)
        dest.face(rows[-1],stem if kind<3 else appearance)

    def bowl(u,v,z,rx,ry,profile,mat):
        for (r0,h0),(r1,h1) in zip(profile,profile[1:]):
            for k in range(20):
                a,b=k*pi/10,(k+1)*pi/10
                baskets.face([at(u+r*rx*cos(t),v+r*ry*sin(t),z+h) for r,h,t in
                              ((r0,h0,a),(r0,h0,b),(r1,h1,b),(r1,h1,a))],mat)
    front=-plot['depth']/2
    left=-plot['width']/2+.32
    right=-left
    trays=[(left+2,front+2.4),(left+2,front+5.25),(2.85,front+3.6),(right-2,front+2.5)]
    for stall,(x,y) in enumerate(trays):
        for j in range(3):
            u=x-.75+j*.75
            if j==0:
                bowl(u,y,.879,.29,.37,((.05,.011),(.60,.016),(1,.098),(.98,.12),(.80,.105),(.53,.036),(.03,.034)),(enamel,wire)[stall%2])
            elif j==1:
                box(baskets,at,u-.32,u+.32,y-.39,y+.39,.879,.893,paper)
                for n in (-.38,.38):
                    box(baskets,at,u-.317,u+.317,y+n-.016,y+n+.014,.882,.992,wood)
            else:
                box(baskets,at,u-.25,u+.25,y-.34,y+.34,.881,.903,wood)
            kind=(stall+j)%4
            for i in range(9 if kind in (1,2) else 15):
                t=i*(pi*(3-sqrt(5)))+stall*.64
                r=sqrt((i+.3)/(15 if kind in (0,3) else 11))
                rings(fruit,u+.22*r*cos(t),y+.305*r*sin(t),.905,
                      rng.uniform(.064,.108)*(1.14 if kind==2 else 1),kind,rng.uniform(0,pi))
    for i in range(5):
        v=-1.22+i*.56
        u=1.35+.37*(i%2)
        bowl(u,v,.762,.205,.245,((.05,.012),(.71,.014),(1,.057),(1.01,.071),(.91,.084),(.63,.026),(.02,.026)),(enamel,wire,wood)[i%3])
        for b in range(6):
            root=Vector(at(u+rng.uniform(-.126,.126),v+rng.uniform(-.133,.133),.814))
            for j in range(4):
                blade(leaves,root,j*pi/2+rng.uniform(-.7,.7),rng.uniform(.13,.25),
                      rng.uniform(.032,.062),rng.uniform(.055,.155),greens[i%2:i%2+3])
    # Distinct stock remains near the front window without intruding into the walkway.
    for i,u in enumerate((-2.6,1.1,5.9)):
        for j in range(7):
            t=j*2.399
            rings(fruit,u+.17*cos(t),front-1.28+.108*sin(t),.880,.073+(j%3)*.010,(i+j)%4,t)
    print('CQ_MARKET_OLD_LEAVES',len(old_leaf))


def gate_wings(scope, at):
    masonry=[scope.finish('brick gate wing warm course %d'%i,col,'brick_wall_08_diff_2k.jpg',.20)
             for i,col in enumerate(((.67,.43,.32),(.57,.35,.26),(.61,.41,.34)))]
    cast=scope.finish('worn grey gate wall top',(.60,.61,.53),'concrete_floor_worn_001_diff_2k.jpg',.27)
    shade=scope.finish('red beam gate depth',(.40,.155,.116),'wood_table_worn_diff_2k.jpg',.33)
    dirt=scope.finish('planting pocket soil',(.28,.30,.19),'leaf_scattered_gravel_diff_2k.jpg',.1)
    pale=scope.finish('weathered light washed wing wall',(.73,.72,.65),'plastered_wall_04_diff_1k.jpg',.33)
    walls=scope.mesh('Review12_SteppedBrickWingWallsAndGateDepth')
    for a,b,d0,d1,h in ((.10,2.68,.14,.64,1.34),(4.85,6.78,.04,.60,2.04),(6.78,7.65,.04,.53,1.68),
                       (5.04,5.53,.62,1.81,1.69)):
        box(walls,at,a,b,d0,d1,-.19,h,pale if a<1 else masonry[0])
        box(walls,at,a-.023,b+.026,d0-.035,d1+.043,h,h+.089,cast)
        for i in range(round((h+.14)/.18)) if a>=1 else range(0):
            u=(a+.019*(i%2))
            box(walls,at,u,b,d0-.015,d0+.004,.046+i*.18,.060+i*.18,masonry[(i+1)%3])
    for s in (2.66,4.73):
        box(walls,at,s,s+.126,.12,.91,2.26,2.41,shade)
    for i in range(5):
        s=2.83+i*.412
        box(walls,at,s,s+.055,.18,1.07,2.37,2.48,shade)
    for s0,s1,d,h in ((.42,2.38,.94,1.15),(5.04,7.36,.88,1.77)):
        box(walls,at,s0,s1,d,d+.35,h-.29,h,cast)
        box(walls,at,s0+.024,s1-.022,d+.035,d+.322,h-.04,h+.009,dirt)
    plant=[scope.finish('gate leaf colour %d'%i,c,rough=.75) for i,c in enumerate(
          ((.18,.35,.10),(.29,.43,.14),(.15,.30,.105)))]
    sites=[(at(u,d,h),r,ht,.095,count) for u,d,h,r,ht,count in
           ((.76,1.02,1.17,.42,.46,130),(1.57,1.10,1.16,.47,.54,130),
            (5.38,1.13,1.78,.50,.58,145),(6.04,1.16,1.82,.53,.71,170),(7.16,1.08,1.73,.47,.64,145),
            (6.32,2.10,2.72,.91,.78,200),(5.69,2.29,3.10,.62,.61,140))]
    canopy(scope,'Review12_CappedWallFoliage',sites,Random(1205),plant)
    for i,(s,d,scale) in enumerate(((1.24,2.43,.57),(6.61,2.70,.75)),1):
        scope.trees.append({'donor':'Outer500_Plant_001','name':f'Zhongxing12_WallCrown{i}',
                            'enu':list(at(s,d,-.02)),'scale':scale,'yaw':.74*i})


def planted_bed(scope, topology, center, axis, across, half, radius, top):
    edges=topology(.002)
    stone=scope.mesh('Review22_LargeVerticalStoneFacing')
    soil=scope.mesh('Review22_ClippedTurfAndPaleMineralBed')
    blades=scope.mesh('Review22_LowDenseGrassAndRadialLeaves')
    tan=[scope.finish('warm limestone block %d'%i,col,rough=.83) for i,col in enumerate(
         ((.53,.47,.39),(.60,.55,.45),(.53,.48,.41),(.47,.45,.40),(.59,.53,.46)))]
    edge=scope.finish('cool dressed coping edge',(.73,.71,.64),'concrete_floor_worn_001_diff_2k.jpg',.36)
    joint=scope.finish('fine weathered vertical pointing',(.37,.34,.29))
    stone_seed=Random(2208)
    for i in range(len(edges)):
        next_i=(i+1)%len(edges)
        a,b=edges[i],edges[next_i]
        j=i%24
        edge_normal=Vector(((b-a).y,-(b-a).x)).normalized()
        divisions=9 if j==23 else 1
        for k in range(divisions):
            p=a.lerp(b,k/divisions)
            q=a.lerp(b,(k+1)/divisions)
            widen=edge_normal*.011
            p,q=p+widen,q+widen
            p,q=p.lerp(q,.016),q.lerp(p,.016)
            low=lambda m:34.766+.021*(m.y-81.42)-.009*(m.x-112)-.012
            high=top-.071
            face=[(*p,low(p)),(*q,low(q)),(*q,high),(*p,high)]
            tone=tan[(i//2+k)%len(tan)]
            stone.face(face,tone)
            stone.face([*face[:2],(*q,low(q)+.022),(*p,low(p)+.022)],joint)
            for _ in range(5):
                t=stone_seed.uniform(.077,.87);u=stone_seed.uniform(.14,.88)
                p0=p.lerp(q,t)+edge_normal*.001
                z=low(p0)+(high-low(p0))*u
                stone.face([(*p0,z),(*(p0.lerp(q,.079)),z+.007),(*(p0.lerp(q,.045)),z+.019)],tan[3])
        a,b=a+edge_normal*.012,b+edge_normal*.012
        stone.face([(*a,top-.068),(*b,top-.068),(*b,top-.012),(*a,top-.012)],edge)
    bottom=top-.121
    grass=[scope.finish('mown turf %d'%i,col,rough=.90) for i,col in enumerate(
        ((.20,.31,.079),(.29,.41,.118),(.17,.29,.084),(.25,.36,.10),(.26,.34,.13)))]
    pale=[scope.finish('light garden gravel %d'%i,col,rough=.91) for i,col in enumerate(
        ((.67,.64,.55),(.84,.81,.72),(.77,.75,.66),(.59,.57,.51)))]
    inner=topology(.263)
    for a,b in zip(inner,inner[1:]+inner[:1]):
        soil.face([(*center,bottom),(*a,bottom),(*b,bottom)],grass[0])
    def xy(u,v):
        return center+axis*u+across*v
    def inside(u,v):
        return (max(abs(u)-half,0))**2+v*v < (radius-.32)**2
    def gravel(u,v):
        return .20 < v+.14*sin(u*2.12) < .72
    rng=Random(2261)
    for i in range(47):
        u=-2.66+i*.115
        v=.14*sin(u*2.12)
        for j in range(5):
            w=.22-v+j*.105
            ps=[(u,w),(u+.115,w),(u+.115,w+.105),(u,w+.105)]
            if all(inside(*point) for point in ps):
                soil.face([(*xy(*point),bottom+.011) for point in ps],rng.choice(pale))
    for i in range(1500):
        u,v=rng.uniform(-2.81,2.81),rng.uniform(-1.43,1.43)
        if not inside(u,v):
            continue
        p=xy(u,v)
        a=rng.random()*2*pi
        if gravel(u,v):
            width=rng.uniform(.012,.031)
            soil.face([(*(p+Vector((cos(k*pi/2+a),sin(k*pi/2+a)))*width),bottom+.014+rng.uniform(.006,.011))
                       for k in range(4)],rng.choice(pale))
        else:
            r=Vector((cos(a),sin(a)))*rng.uniform(.009,.017)
            q=p+Vector((cos(a+.89),sin(a+.89)))*rng.uniform(.018,.044)
            blade_points=[(*(p-r),bottom+.014),(*(p+r),bottom+.014),(*q,bottom+rng.uniform(.04,.079))]
            blades.face(blade_points,rng.choice(grass))
            blades.face(blade_points[::-1],grass[2])
    purple=[scope.finish('purple shrub leaf %d'%i,col,rough=.73) for i,col in enumerate(
        ((.28,.105,.23),(.41,.18,.32),(.22,.083,.18)))]
    centers=[((*xy(u,v),bottom),r,h,.078,270) for u,v,r,h in ((-1.68,.87,.45,.51),(1.41,.86,.39,.42))]
    canopy(scope,'Review22_TwoPurpleRoundedShrubs',centers,rng,purple)
    agave=[scope.finish('radial planting leaf %d'%i,col,rough=.58) for i,col in enumerate(
        ((.28,.50,.22),(.52,.65,.31),(.21,.39,.15)))]
    for i,(u,v) in enumerate(((-2.10,-.62),(-.69,-.94),(.65,-.77),(2.08,-.44))):
        for j in range(15):
            blade(blades,Vector((*xy(u,v),bottom+.016)),j*2.399+i*.73,
                  rng.uniform(.23,.45),rng.uniform(.027,.051),rng.uniform(.08,.29),agave)
    scope.retired.append('Zhongxing22_TurfAndLowShrubs')
