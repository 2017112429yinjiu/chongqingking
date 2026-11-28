"""Refinish the verified public pull-off without extending under the hidden house."""
from pathlib import Path
import sys

from mathutils import Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
sys.path.insert(0,str(HERE.parent/"west"))
from scanned_crowns import finish_crowns
from build import ASSETS, apply_finish, box, read

STREETS=HERE.parents[1]/'street_groups'


def make(scope):
    d=STREETS/'jiefang_public_24_25_26'
    data=read(ASSETS/'district_500/jiefang-public-02-24-25-26.json')
    route=data['walks']['26']; scope.points['26']=[route[0],route[-1]]
    granite=scope.finish('pale patched granite',(.78,.755,.72),'concrete_floor_worn_001_diff_2k.jpg',.16)
    edge=scope.finish('stone curb face',(.64,.645,.62),'stone_wall_05_diff_2k.jpg',.16)
    joint=scope.finish('pulled sanded seams',(.23,.233,.21))
    flush=scope.finish('wet iron at the layby',(.22,.23,.225),metal=.40)
    original=d/'jiefang-public-02-24-25-26.blend'
    for name in ('COL_Jiefang26_PublicFlags','COL_Jiefang26_LowerRoadLayBy'):
        cover=scope.donor(original,name)
        tree=apply_finish(cover,granite,edge)
        if name.endswith('PublicFlags'):
            curb_hit=tree
    mesh=scope.mesh('Review26_StaggeredLayByFlagsAndDrainStrips')
    for start,end in zip(route,route[1:]):
        a,b=Vector(start[:2]),Vector(end[:2]); along=(b-a).normalized(); side=Vector((-along.y,along.x))
        def point(u,v,z):
            e,n=a+along*u+side*v
            hit=curb_hit.ray_cast(Vector((e,n,80)),Vector((0,0,-1)),90)[0]
            return (e,n,(hit.z if hit is not None else scope.floor(e,n))+z)
        for i in range(1,5):
            s=(b-a).length*i/5
            box(mesh,point,s,s+.012,-.568,.568,.004,.010,joint)
            if i==1:
                for k in range(5):
                    box(mesh,point,s+k*.038,s+k*.038+.014,.52,.62,.006,.018,flush)
    # The dated views support a planted public street edge. The private shell
    # and the construction screens belong to different evidence scopes.
    from math import atan2
    cut=scope.mesh('Review26_GroundedStreetTreePockets')
    curb=scope.finish('Jiefang street pale tree edging',(.65,.67,.64),'stone_floor_diff_2k.jpg',.21)
    earth=scope.finish('Jiefang tree bed grit',(.43,.45,.35),'leaf_scattered_gravel_diff_2k.jpg',.11)
    for i,idx in enumerate((1,3,5)):
        if idx>=len(route)-1:
            continue
        a,b=Vector(route[idx][:2]),Vector(route[idx+1][:2])
        along=(b-a).normalized()
        across=Vector((-along.y,along.x))
        center=a+1.16*across+.13*along
        def world(u,v,h):
            e,n=center+u*along+v*across
            return e,n,scope.floor(e,n)+h
        box(cut,world,-.43,.43,-.33,.33,-.022,.040,curb)
        box(cut,world,-.39,.39,-.29,.29,.04,.047,earth)
        scope.trees.append({'donor':'Outer500_Plant_001','name':f'Jiefang26StreetTree_{i}',
                            'enu':list(world(0,0,.045)),'scale':.39+i*.04,'yaw':atan2(along.y,along.x)})
    finish_crowns(scope)
