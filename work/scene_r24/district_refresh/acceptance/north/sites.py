"""Finish the public retaining, door and stair edges in the northern group."""
from math import cos, sin
from pathlib import Path
from random import Random
import runpy
import sys

from mathutils import Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from build import ASSETS, apply_finish, box, read
sys.path.insert(0, str(HERE))
from public_edges import school, liangting_storefront

STREETS=HERE.parents[1]/'street_groups'
Edge=runpy.run_path(str(STREETS/'north_edges/build.py'))['Edge']


def east_north(plot,u,v):
    e,n=plot['east_north']; c,s=cos(plot['bearing']),sin(plot['bearing'])
    return e+c*u-s*v,n+s*u+c*v


def walls(scope):
    d=STREETS/'north_edges'
    f=read(d/'field.json')
    walk=read(ASSETS/'district_500/north-38-40-41.json')['walks']
    point=next(r['en'] for r in f['records'] if r['pano']=='0902920012230515132237063AU')
    chain={'40':[point]+[x['east_north'] for x in reversed(f['road_chains']['40']['stations'])][:3],
           '41':[x['east_north'] for x in f['road_chains']['41']['stations'][:4]]}
    pale=scope.finish('honed stone coping',(.73,.72,.67),'concrete_floor_worn_001_diff_2k.jpg',.27)
    warm=scope.finish('faded pink stone',(.75,.62,.55),'stone_wall_05_diff_2k.jpg',.21)
    damp=scope.finish('lower wet course',(.39,.45,.41),'stone_wall_05_diff_2k.jpg',.21)
    rough=[scope.finish('rough grey wall stone '+str(i),v,'stone_wall_05_diff_2k.jpg',.34) for i,v in enumerate((
        (.62,.63,.57),(.73,.69,.63),(.55,.59,.57),(.66,.65,.62)))]
    crease=scope.finish('deep wall weather seam',(.165,.176,.161))
    for id in ('40','41'):
        edge=Edge(chain[id],scope.ground)
        trim=scope.mesh(f'Review{id}_CopingAndGroundedWallDetails')
        scope.points[id]=[walk[id][0],walk[id][-1]]
        part=scope.donor(d/'north-38-40-41.blend',f'North{id}_CoursesAndWeathering')
        mats=([warm,rough[1],rough[3],damp] if id=='40' else rough+[damp])
        part.data.materials.clear()
        for mat in mats:part.data.materials.append(mat)
        for face in part.data.polygons:
            face.material_index=(face.index//6)%len(mats)
        if id=='40':
            # The top pieces follow the surveyed turnover line and retain their
            # settled elevations; the cap has separate end joints and drip edge.
            for i in range(18):
                a=.77+i*1.05; b=a+1.022
                box(trim,edge.at,a,b,1.348,1.834,1.793,1.846,pale)
                box(trim,edge.at,a+.012,b-.09,1.344,1.354,1.779,1.791,crease)
        else:
            # The real upper edge has square voids. Keep the installed openings
            # and bring out their masonry at the measured front face.
            for i in range(3,18):
                a=8.75+i*.63;b=a+.63
                for x in (a+.11,b-.153):
                    box(trim,edge.at,x,x+.057,2.654,2.705,3.182,3.487,rough[i%4])
                box(trim,edge.at,a+.134,b-.129,2.657,2.705,3.175,3.212,damp)
            rng=Random(41)
            for t in range(30):
                s=rng.uniform(9,21.8); wide=rng.uniform(.024,.105)
                trim.face([edge.at(s-wide,2.622,.086),edge.at(s+wide,2.625,.081),
                           edge.at(s+wide*.44,2.624,.25+rng.uniform(0,.13)),edge.at(s-wide*.25,2.626,.174)],damp)


def stairs(scope):
    cfg=read(ASSETS/'district_500/matix_streets.json')['rear_stair']['path_east_north_up']
    source=STREETS/'matix/matix_streets.blend'
    stone=scope.finish('dressed stair step aggregate',(.68,.7,.70),'concrete_floor_worn_001_diff_2k.jpg',.22)
    strata=scope.finish('old stair side strata',(.56,.55,.51),'stone_wall_05_diff_2k.jpg',.2)
    part=scope.donor(source,'COL_Liangtingzi_RearStair_43')
    open_south_stair_bay(part)
    support=apply_finish(part,stone,strata)
    shoe=scope.mesh('Review43_TreadNosesAndMidLandingJoints')
    edge=scope.finish('worn stair tread noses',(.72,.71,.675),'concrete_floor_worn_001_diff_2k.jpg',.25)
    # Walk the real strip of treads and only place a nosing beside a riser
    # where the reopened collision mesh demonstrates the next height remains lower.
    a,b=Vector(cfg[3][:2]),Vector(cfg[-1][:2]); axis=(b-a).normalized(); side=Vector((-axis.y,axis.x))
    prev=None
    for i in range(1,int((b-a).length/.061)):
        p=a+axis*(i*.061)
        hit=support.ray_cast(Vector((*p,49)),Vector((0,0,-1)),22)[0]
        if hit is None:continue
        if prev is not None and .08<prev-hit.z<.22:
            rear=p-.063*axis
            corners=[rear-.747*side,rear+.747*side,rear-.039*axis+.747*side,rear-.039*axis-.747*side]
            shoe.face([(*q,prev+.004) for q in corners],edge)
        prev=hit.z
    scope.points['43']=[cfg[-1],cfg[-2]]


def open_south_stair_bay(part):
    # The registered south eye hits the landing side (44 and 49) and the
    # first downstream tread skirt (52). Recess the underside through the
    # short flight, turn and first two treads of the long flight. The original
    # door platform and the remaining long-flight foundation support the ends.
    faces = part.data.polygons
    assert len(faces) == 134
    assert all(abs(faces[i].normal.z) < .01 for i in (44, 49, 52))
    lower_vertices = {i for face in faces[6:62] for i in face.vertices if part.data.vertices[i].co.z < 37.7}
    assert lower_vertices
    for i in lower_vertices:
        part.data.vertices[i].co.z = 39.68
    part.data.update()


def door42(scope):
    item=next(p for p in read(ASSETS/'district_500/layout.json')['plots'] if p['plot_id']==42)
    u=item['door_u']; front=-item['depth']*.5
    base=item['height']
    grey=scope.finish('unnamed dwelling threshold limestone',(.76,.74,.69),'concrete_floor_worn_001_diff_2k.jpg',.27)
    grayblue=scope.finish('unnamed dwelling weathered casing',(.28,.35,.34),'wood_table_worn_diff_2k.jpg',.30)
    trim=scope.mesh('Review42_UndesignatedThresholdAndCasing')
    def position(l,t,z):
        e,n=east_north(item,l,t)
        return e,n,base+z
    for w in (u-1.02,u+.92):
        box(trim,position,w,w+.102,front-.099,front+.016,.06,2.24,grayblue)
    box(trim,position,u-1.02,u+1.022,front-.101,front+.013,2.20,2.34,grayblue)
    box(trim,position,u-.93,u+.91,front-.102,front+.016,.05,.085,grey)
    scope.points['42']=[[*east_north(item,u,front-1),base+.048],[*east_north(item,u,front),base+.9]]


def liangting(scope):
    d=STREETS/'liangtingzi_45_46'
    f=read(d/'field.json'); cfg=read(ASSETS/'district_500/liangtingzi-45-46.json')
    timber=scope.finish('oiled public sitting rails',(.60,.42,.26),'wood_table_worn_diff_2k.jpg',.36)
    base=scope.finish('tree well cut stone',(.64,.62,.58),'concrete_floor_worn_001_diff_2k.jpg',.22)
    hinge=scope.finish('bronze shop track attachments',(.37,.30,.24),metal=.34)
    paint=scope.finish('edged weathered low shop wood',(.42,.37,.30),'wood_table_worn_diff_2k.jpg',.25)
    e,n=f['tree_anchor']; z=scope.floor(e,n)+.052
    tree=scope.mesh('Review45_CastTreePitAndPublicSeatSupports')
    def point(u,v,h):
        return (e+u,n+v,z+h)
    # Support at both ends follows the existing public game-side tree apron.
    # The site-register tree is inside the old frame and has its own open issue.
    for u in (-.414,.408):
        if u<0: limits=(-.47,-.397)
        else: limits=(.397,.469)
        for v in (-.277,-.095,.091):
            box(tree,point,*limits,v,v+.168,.036,.113,base)
    for h0,h1 in ((.08,.40),(.335,.424)):
        for u in (.72,1.31):
            box(tree,point,u,u+.081,-.284,.031,h0,h1,base)
    for i in range(3):
        v=-.313+i*.12
        box(tree,point,.66,1.47,v,v+.106,.407,.467,timber)
    shop=scope.mesh('Review46_LowShopEdgeTransomsAndReveals')
    edge=Edge(f['geometry']['46']['path'],scope.ground)
    for a,b in ((4.4,7.0),(7.0,9.62),(9.62,12.22)):
        for v in (a+.24,b-.30):
            box(shop,edge.at,v,v+.065,1.282,1.340,-.383,.932,paint)
            box(shop,edge.at,v+.019,v+.044,1.271,1.287,.387,.521,hinge)
        box(shop,edge.at,a+.225,b-.22,1.271,1.335,.592,.691,paint)
        for i in range(1,5):
            u=a+.25+i*(b-a-.50)/5
            box(shop,edge.at,u,u+.027,1.276,1.329,.632,1.035,hinge)
    for id in ('45','46'):
        r=cfg['walks'][id]; scope.points[id]=[r[0],r[-1]]


def make(scope):
    walls(scope)
    stairs(scope)
    door42(scope)
    liangting(scope)
    school(scope)
    liangting_storefront(scope)
