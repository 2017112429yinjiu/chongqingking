"""Refinish the verified public pull-off without extending under the hidden house."""
from pathlib import Path
import sys

from mathutils import Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
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
