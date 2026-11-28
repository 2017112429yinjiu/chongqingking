"""Finish the supported 53 stair and the separate upper public bridge path."""
from math import cos, sin
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from build import box

GROUP = Path(__file__).resolve().parents[2]/'street_groups'
MAP = 'district_500/acceptance_textures/'


def low_stairs(scope, plot):
    e,n=plot['east_north']
    c,s=cos(plot['bearing']),sin(plot['bearing'])
    def at(u,v,z):
        return e+c*u-s*v,n+s*u+c*v,z
    def local(point):
        x,y,z=point
        return (x-e)*c+(y-n)*s, -(x-e)*s+(y-n)*c, z
    stone='district_r21/terraces_washed_sandstone.jpg'
    maps=(MAP+'washed-stone-normal.jpg',MAP+'washed-stone-rough.jpg')
    treads=[scope.pbr('53 stone tread '+str(i),color,stone,*maps,tint=color) for i,color in enumerate(
        ((.69,.74,.75),(.72,.76,.77),(.60,.66,.69),(.78,.80,.77),(.66,.71,.72)))]
    nose=scope.pbr('53 evenly worn granite nose',(.83,.85,.83),stone,*maps,tint=(.85,.90,.86))
    seam=scope.finish('53 ash grey mortar',(.37,.40,.38),'concrete_wall_006_diff_2k.jpg',.15)
    wall=scope.mossy_wall('53 weathered sidewall stone',(.56,.58,.52))
    tread=scope.mesh('Review53_OriginalStoneTreadsAndWornNoses')
    side=scope.mesh('Review53_StoneBlockSidewallFaces')
    existing=bpy.data.objects['COL_Outer500_Retaining_and_boundaries']
    u0=plot['door_u']-1.25
    u1=plot['door_u']+1.25
    start=plot['depth']*.5
    finish=start+plot['back_stair_m']
    profiles=[]
    for face in existing.data.polygons:
        if abs(face.normal.z-1.)>.01:
            continue
        bounds=[local(existing.matrix_world@existing.data.vertices[i].co) for i in face.vertices]
        near=min(v for _,v,_ in bounds)
        far=max(v for _,v,_ in bounds)
        if not (start-.01<near<finish and .20<far-near<.39):
            continue
        if abs(min(u for u,_,_ in bounds)-u0)>.01 or abs(max(u for u,_,_ in bounds)-u1)>.01:
            continue
        profiles.append((near,far,max(z for _,_,z in bounds)))
    profiles.sort()
    assert len(profiles)>=22,profiles
    for row,(near,far,z) in enumerate(profiles):
        section=[u0]+[u0+i*.50+(row%3-1)*.085 for i in range(1,5)]+[u1]
        for i,(a,b) in enumerate(zip(section,section[1:])):
            box(tread,at,a+.004,b-.004,near+.005,far-.003,z-.011,z+.009,treads[(i+2*row)%len(treads)])
            box(tread,at,a+.006,b-.006,far-.031,far+.001,z-.023,z+.013,nose)
        box(tread,at,u0+.006,u1-.006,far-.005,far+.003,z-.119,z-.021,seam)
        for edge,direction in ((u0,-1),(u1,1)):
            middle=(near+far)*.5
            ground=scope.floor(*at(edge,middle,z)[:2])
            bottom=min(z-.07,ground-.045)
            for k in range(1+int((z-bottom)/.25)):
                za=bottom+k*.23
                zb=min(za+.22,z-.016)
                if zb>za:
                    x=edge+direction*.014
                    corners=[at(x,near+.004,za),at(x,far-.004,za),at(x,far-.004,zb),at(x,near+.004,zb)]
                    side.face(corners if direction>0 else corners[::-1],wall if k%3 else seam)


def upper_public_way(scope):
    # The corrected deck source owns the route above the low 53 game stair.
    # Terminate the textured inset at the existing public stop.
    model=GROUP/'nanqu_rail_grade/nanqu-rail-grade.blend'
    name='Grade__COL_Nanqu_RiverFootway'
    rail_name='Grade__Nanqu_GalvanizedVerticals'
    with bpy.data.libraries.load(str(model),link=False) as (source, loaded):
        assert name in source.objects and rail_name in source.objects
        loaded.objects=[name,rail_name]
    support,rail=loaded.objects
    ground=BVHTree.FromPolygons([support.matrix_world@v.co for v in support.data.vertices],
                                [tuple(f.vertices) for f in support.data.polygons])
    west,east=map(Vector,[[-162.25,-75.24],[-156.93,-77.39]])
    direction=(east-west).normalized()
    perpendicular=Vector((-direction.y,direction.x))
    flags=scope.finish('53 upper blue grey rectangular flags',(.72,.74,.74),'stone_floor_diff_2k.jpg',.16)
    tactile=scope.finish('53 muted pale tactile strip',(.68,.64,.53),'concrete_floor_worn_001_diff_2k.jpg',.17)
    lighter=scope.finish('53 chamfered tactile ribs',(.75,.71,.60),'concrete_floor_worn_001_diff_2k.jpg',.16)
    mesh=scope.mesh('Review53_ExistingUpperPublicFlagsAndTactileStrip')
    def point(s,t,extra):
        e,n=west+direction*s+perpendicular*t
        hit=ground.ray_cast(Vector((e,n,95)),Vector((0,0,-1)),130)[0]
        return (e,n,hit.z+extra) if hit is not None else None
    ntiles=0
    for i in range(15):
        a=i*.33
        b=a+.321
        for x,y in ((-.92,-.45),(-.444,.02),(.027,.50),(.507,.94)):
            coords=[point(s,t,.014) for s,t in ((a,x),(b,x),(b,y),(a,y))]
            if all(v is not None for v in coords):
                mesh.face(coords,flags)
                ntiles+=1
        coords=[point(s,t,.020) for s,t in ((a,.45),(b,.45),(b,.75),(a,.75))]
        if all(v is not None for v in coords):
            mesh.face(coords,tactile)
            for t in (.50,.565,.63,.695):
                ribs=[point(s,d,.027) for s,d in ((a+.021,t),(b-.019,t),(b-.019,t+.016),(a+.021,t+.016))]
                mesh.face(ribs,lighter)
    assert ntiles>20, ntiles
    grey=scope.finish('53 upper aged galvanized rail',(.48,.52,.49),metal=.61,rough=.44)
    blue=scope.finish('53 upper alternating blue tube',(.24,.46,.62),metal=.32,rough=.69)
    white=scope.finish('53 worn upper white pipe paint',(.78,.79,.76),metal=.22,rough=.60)
    trim=scope.mesh('Review53_ExistingUpperRailingFinishes')
    for f in rail.data.polygons:
        center=rail.matrix_world@f.center
        if not (-163.0<center.x<-152.5 and -82.<center.y<-72.):
            continue
        surface=rail.data.materials[f.material_index]
        paint=grey
        if surface and 'blue-grey' in surface.name:
            paint=blue if int((center.x+163.)/.71)%5<3 else white
        outward=rail.matrix_world.to_3x3()@f.normal*.003
        trim.face([rail.matrix_world@rail.data.vertices[i].co+outward for i in f.vertices],paint)
    assert trim.faces
    bpy.data.objects.remove(support)
    bpy.data.objects.remove(rail)
