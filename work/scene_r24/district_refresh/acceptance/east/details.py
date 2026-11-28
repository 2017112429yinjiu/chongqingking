"""Street-evidence finish for the market, red eaves and shallow planter."""
from math import cos, pi, sin, sqrt
from random import Random
from pathlib import Path

import bmesh
from mathutils import Vector

from build import ASSETS, box, read
from textured_goods import STOCK, TEXTURE, UVSurface, food_material, ginger, plant_material


def blade(mesh, anchor, angle, length, width, lift, mats):
    """A tapered rounded leaf with a raised vein and visible abaxial material."""
    along=Vector((cos(angle),sin(angle),0))
    across=Vector((-sin(angle),cos(angle),0))
    verts=[]
    uvs=[]
    profile=((0,.055,0),(.19,.59,.43),(.4,.96,.74),(.61,1,1),(.79,.74,.96),(.92,.39,.87),(1,.015,.68))
    for t,spread,camber in profile:
        p=anchor+along*(t*length)+Vector((0,0,camber*lift))
        w=width*spread
        ripple=.12*width*sin(t*36+angle)
        verts.append([p-across*w+Vector((0,0,ripple-w*.31)),p,p+across*w+Vector((0,0,-ripple-w*.44))])
        uvs.append([(.574+side*.083*spread,.688+.290*t) for side in (-1,0,1)])
    for i,(a,b) in enumerate(zip(verts,verts[1:])):
        c,d=uvs[i:i+2]
        for j in (0,1):
            points=(a[j],b[j],b[j+1],a[j+1])
            texture=(c[j],d[j],d[j+1],c[j+1])
            mesh.face(points,mats[(i+j)%2],texture)
            mesh.face([p-Vector((0,0,.0008)) for p in points[::-1]],mats[-1],texture[::-1])


def canopy(scope, name, positions, rng, tone):
    mesh=scope.mesh(name,UVSurface)
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
    fruit=scope.mesh('Review01_MixedProduceSkins',UVSurface)
    scope.smooth.add(fruit.name)
    leaves=scope.mesh('Review01_BunchedGreensRoundedLeaves',UVSurface)
    wood=scope.finish('market basket staves',(.63,.45,.30),'wood_table_worn_diff_2k.jpg',.2)
    enamel=scope.finish('market wet goods blue enamel',(.21,.44,.53),metal=.22,rough=.65)
    paper=scope.finish('market folded pale kraft liners',(.60,.54,.37))
    wire=scope.finish('brushed shallow basin edge',(.57,.60,.55),metal=.62,rough=.42)
    kinds=('mandarin','aubergine','squash','potato')
    colors=[[food_material(scope,f'{kind} skin {j}',tint,kind) for j,tint in enumerate(row)]
            for kind,row in zip(kinds,(
        ((1.,.85,.79),(.93,.69,.62),(1.,.98,.86),(.85,.72,.74)),
        ((.88,.79,.92),(.98,.94,.89),(.74,.82,.88),(.81,.67,.80)),
        ((1.,.94,.81),(1.,.78,.70),(.84,.91,.73),(.97,.91,.78)),
        ((.91,.82,.70),(1.,.96,.88),(.89,.72,.58),(.81,.79,.69)),
    ),strict=True)]
    stem=plant_material(scope,'market stems and calyx',(.47,.64,.32))
    greens=[plant_material(scope,'vegetable leaf tone %d'%i,t) for i,t in enumerate(
        ((.78,.96,.64),(.91,1.,.78),(.65,.84,.58),(.80,.90,.61),(.94,.97,.78)))]
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
        dest.face(rows[0][::-1],appearance,[(.5+.29*cos(k*2*pi/detail),.5+.29*sin(k*2*pi/detail))
                                            for k in reversed(range(detail))])
        for i,(old,new) in enumerate(zip(rows,rows[1:])):
            a,b=i/(len(rows)-1),(i+1)/(len(rows)-1)
            for j in range(detail):
                k=(j+1)%detail
                u0,u1=j/detail,(j+1)/detail
                dest.face([old[j],old[k],new[k],new[j]],appearance,[(u0,a),(u1,a),(u1,b),(u0,b)])
        dest.face(rows[-1],stem if kind<3 else appearance,
                  [(.574+.04*cos(k*2*pi/detail),.83+.065*sin(k*2*pi/detail)) for k in range(detail)])

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
                if stall==2:
                    ginger(scope,at,u,y,.895,plot['bearing'])
                    continue
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
    stone=scope.mesh('Review22_LargeVerticalStoneFacing',UVSurface)
    soil=scope.mesh('Review22_ClippedTurfAndPaleMineralBed')
    blades=scope.mesh('Review22_RadialLeaves',UVSurface)
    tan=[scope.pbr('washed sandstone panel %d'%i,col,TEXTURE+'washed-stone-buff-albedo.jpg',
                  TEXTURE+'washed-stone-normal.jpg',TEXTURE+'washed-stone-rough.jpg',
                  ambient=.34,tint=col,normal_strength=.36,specular=.21) for i,col in enumerate(
         ((.94,.90,.80),(.99,.93,.82),(.89,.89,.84),(.84,.84,.80),(.98,.91,.79)))]
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
            phase=stone_seed.uniform(0,1)
            rise=(high-(low(p)+low(q))*.5)*1.29
            tex=(phase,phase+(q-p).length*1.29)
            stone.face(face,tone,[(tex[0],.21),(tex[1],.21),(tex[1],.21+rise),(tex[0],.21+rise)])
            stone.face([*face[:2],(*q,low(q)+.022),(*p,low(p)+.022)],joint)
        a,b=a+edge_normal*.012,b+edge_normal*.012
        stone.face([(*a,top-.068),(*b,top-.068),(*b,top-.012),(*a,top-.012)],edge)
    bottom=top-.121
    grass=scope.pbr('dense mown turf',(.83,.92,.76),TEXTURE+'turf-albedo.jpg',TEXTURE+'turf-normal.jpg',
                    TEXTURE+'turf-rough.jpg',ambient=.14,tint=(.83,.92,.76))
    pale=[scope.pbr('light gravel %d'%i,col,TEXTURE+'pale-gravel-albedo.jpg',
                    STOCK+'leaf_scattered_gravel_nor_gl_2k.jpg',STOCK+'leaf_scattered_gravel_rough_2k.png',
                    ambient=.19,tint=col) for i,col in enumerate(
        ((.89,.86,.81),(1.,.97,.91),(.94,.91,.86),(.82,.79,.74)))]
    inner=topology(.263)
    for a,b in zip(inner,inner[1:]+inner[:1]):
        soil.face([(*center,bottom),(*a,bottom),(*b,bottom)],grass)
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
    purple=[plant_material(scope,'purple shrub leaf %d'%i,col,purple=True) for i,col in enumerate(
        ((.83,.72,.83),(.95,.88,.91),(.70,.64,.76)))]
    centers=[((*xy(u,v),bottom),r,h,.102,340) for u,v,r,h in ((-1.68,.87,.45,.51),(1.41,.86,.39,.42))]
    canopy(scope,'Review22_TwoPurpleRoundedShrubs',centers,rng,purple)
    agave=[plant_material(scope,'radial planting leaf %d'%i,col) for i,col in enumerate(
        ((.81,.90,.68),(.95,.97,.78),(.67,.83,.59)))]
    for i,(u,v) in enumerate(((-2.10,-.62),(-.69,-.94),(.65,-.77),(2.08,-.44))):
        for j in range(15):
            blade(blades,Vector((*xy(u,v),bottom+.016)),j*2.399+i*.73,
                  rng.uniform(.23,.45),rng.uniform(.027,.051),rng.uniform(.08,.29),agave)
    scope.retired.append('Zhongxing22_TurfAndLowShrubs')
