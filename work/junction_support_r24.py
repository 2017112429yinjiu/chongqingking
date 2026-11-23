"""Regrade the exposed terrain and replace orphaned road-edge skirts in the junction."""
import bmesh,math
from collections import defaultdict
from mathutils import Vector

def road_patch(scene,change,surface,mat,spatial,originals,roadways,edges):
    def drive(name):
        return name.endswith(('_asphalt','_pavement')) and name.startswith('COL_Road_') and name.split('_')[2] in roadways
    roads=[o for o in scene.objects if o.type=='MESH' and drive(o.name)]
    def within(x,y):
        return 5.<x<99.9 and -101.3<y<-65. and any(min(abs(edge.sample(x).y-y) for edge in pair)<9.4 for pair in edges.values())
    def cast(trees,x,y):
        hits=[]
        for ((a,b),(c,d),_),tree,_ in trees:
            if a-.002<=x<=b+.002 and c-.002<=y<=d+.002:
                p,_,_,_=tree.ray_cast((x,y,42),(0,0,-1),80)
                if p is not None:hits.append(p.z)
        return hits
    road_shapes=spatial(roads)
    ground=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Terrain_200m')]
    terrain_cuts={}
    for ob in ground:
        bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
        # Condition on face bounds so a large old triangle cannot span the new carriageway.
        def relevant(f):
            coords=[v.co for v in f.verts]
            return max(p.x for p in coords)>8 and min(p.x for p in coords)<99 and min(p.y for p in coords)<-71 and max(p.y for p in coords)>-101
        local=[f for f in bm.faces if relevant(f)]
        if not local:bm.free();continue
        for axis,planes in [(0,range(8,101,2)),(1,range(-101,-68,2))]:
            for q in planes:
                selected=[f for f in local if f.is_valid and min(v.co[axis] for v in f.verts)<q+.001 and max(v.co[axis] for v in f.verts)>q-.001]
                if not selected:continue
                geom=set(selected)
                for f in selected:geom.update(f.verts);geom.update(f.edges)
                origin=Vector((0,0,0));n=origin.copy();n[axis]=1;origin[axis]=q
                result=bmesh.ops.bisect_plane(bm,geom=list(geom),plane_co=origin,plane_no=n,dist=.00002)
                local=list({f for f in local if f.is_valid}|{f for f in result['geom'] if isinstance(f,bmesh.types.BMFace) and f.is_valid and relevant(f)})
        moved=0
        for v in bm.verts:
            p=v.co
            if not within(p.x,p.y):continue
            candidates=cast(road_shapes,p.x,p.y)
            if candidates:
                goal=max(candidates)-.11
            else:
                # Feather only at the rim. Never excavate an entire strip alongside the road.
                samples=[z for dx,dy in [(-.8,0),(.8,0),(0,-.8),(0,.8)] for z in cast(road_shapes,p.x+dx,p.y+dy)]
                if not samples:continue
                goal=max(samples)+.04
            if p.z>goal:p.z=goal;moved+=1
        if moved:
            change(ob);bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update();terrain_cuts[ob.name]=moved
        bm.free()
    terrain=spatial(ground)
    foundation=scene.objects['COL_R23_PathFoundations']
    bm=bmesh.new();bm.from_mesh(foundation.data);bm.transform(foundation.matrix_world)
    obsolete=[]
    for face in bm.faces:
        points=sorted((v.co for v in face.verts),key=lambda p:-p.z)
        p=(points[0]+points[1])*.5
        if not within(p.x,p.y):continue
        for ((xl,xh),(yl,yh),_),tree,name in originals:
            if not drive(name) or not (xl-.16<p.x<xh+.16 and yl-.16<p.y<yh+.16):continue
            hit,_,_,dist=tree.find_nearest(p,.14)
            if hit is not None:
                obsolete.append(face);break
    count=len(obsolete)
    bmesh.ops.delete(bm,geom=obsolete,context='FACES');change(foundation);bm.transform(foundation.matrix_world.inverted());bm.to_mesh(foundation.data);foundation.data.update();bm.free()
    concrete=mat('junction_stem',(.25,.257,.24));panels=0
    for ob in roads:
        perimeter=defaultdict(list);world=ob.matrix_world
        for poly in ob.data.polygons:
            if poly.normal.z<.45:continue
            pts=[world@ob.data.vertices[i].co for i in poly.vertices]
            for a,b in zip(pts,pts[1:]+pts[:1]):
                if not within((a.x+b.x)*.5,(a.y+b.y)*.5):continue
                key=tuple(sorted(tuple(round(c,4) for c in p) for p in (a,b)))
                perimeter[key].append((a,b))
        for spans in perimeter.values():
            if len(spans)!=1:continue
            a,b=spans[0];delta=b-a;out=Vector((delta.y,-delta.x,0)).normalized()
            segments=max(1,math.ceil(delta.length/.85))
            for j in range(segments):
                v=a.lerp(b,j/segments);w=a.lerp(b,(j+1)/segments);p=(v+w)*.5
                if not within(p.x,p.y):continue
                beyond=p+out*.077
                land=cast(terrain,beyond.x,beyond.y);adj=cast(road_shapes,beyond.x,beyond.y)
                if not land:continue
                support=max(land+adj)
                if p.z-support<.055:continue
                low=[]
                for point in (v,w):
                    q=point+out*.037;values=cast(terrain,q.x,q.y)+cast(road_shapes,q.x+out.x*.064,q.y+out.y*.064)
                    low.append(min(point.z-.017,max(values,default=support)-.05))
                surface('COL_R24_JunctionStem',concrete,[(v.x,v.y,low[0]),(w.x,w.y,low[1]),tuple(w),tuple(v)],[(0,1,2,3)]);panels+=1
    return dict(terrain_vertices=terrain_cuts,old_skirt_faces_removed=count,fitted_panels=panels)

