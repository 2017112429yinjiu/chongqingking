"""Clip the adjoining walk and paving to the actual tread perimeter at two path junctions."""
import bmesh, math
from mathutils import Vector
from collections import defaultdict

def footprints(step):
    tops=[f for f in step.data.polygons if f.normal.z>.998]
    for first,second in zip(tops[::2],tops[1::2]):
        pts={tuple(round(k,5) for k in step.matrix_world@step.data.vertices[i].co) for f in (first,second) for i in f.vertices}
        if len(pts)!=4 or max(p[2] for p in pts)-min(p[2] for p in pts)>.001:continue
        center=sum((Vector(p) for p in pts),Vector())/4
        ring=sorted([Vector(p) for p in pts],key=lambda pt:math.atan2(pt.y-center.y,pt.x-center.x))
        yield center,ring

def cut(ob,loops):
    bm=bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    total=0
    for c,ring in loops:
        x0,x1=min(p.x for p in ring)-.002,max(p.x for p in ring)+.002
        y0,y1=min(p.y for p in ring)-.002,max(p.y for p in ring)+.002
        # Check full face extents, including large slabs whose centres lie outside a tread.
        def may_hit(f):
            vs=[v.co for v in f.verts]
            return not (all(v.x<x0 for v in vs) or all(v.x>x1 for v in vs) or all(v.y<y0 for v in vs) or all(v.y>y1 for v in vs) or all(v.z<c.z-.43 for v in vs) or all(v.z>c.z+.65 for v in vs))
        faces=[f for f in bm.faces if may_hit(f)]
        if not faces:continue
        # Only split faces that still can be inside the convex footprint.
        for a,b in zip(ring,ring[1:]+ring[:1]):
            n=Vector((a.y-b.y,b.x-a.x,0)).normalized()
            inside=[]
            for f in faces:
                if not f.is_valid:continue
                ds=[(v.co-a).dot(n) for v in f.verts]
                if max(ds)<-.00001:continue
                if min(ds)<-.00001 and max(ds)>.00001:
                    g=[f,*f.edges,*f.verts]
                    change=bmesh.ops.bisect_plane(bm,geom=g,dist=.000002,plane_co=a,plane_no=n)
                    fragments={k for k in change['geom'] if isinstance(k,bmesh.types.BMFace) and k.is_valid}
                    if f.is_valid:fragments.add(f)
                    inside.extend(piece for piece in fragments if (piece.calc_center_median()-a).dot(n)>=-.00001)
                elif min(ds)>=-.00001:
                    inside.append(f)
            faces=list(set(inside))
            if not faces:break
        def covered(f):
            for a,b in zip(ring,ring[1:]+ring[:1]):
                n=Vector((a.y-b.y,b.x-a.x,0)).normalized()
                if any((v.co-a).dot(n)<-.00003 for v in f.verts):return False
            return True
        remove=[f for f in faces if f.is_valid and c.z-.43<=f.calc_center_median().z<=c.z+.65 and covered(f)]
        if remove:
            total+=len(remove)
            bmesh.ops.delete(bm,geom=remove,context='FACES')
    if total:
        bm.transform(ob.matrix_world.inverted())
        bm.to_mesh(ob.data)
        ob.data.update()
    bm.free()
    return total

def repair(scene):
    central=list(footprints(scene.objects['COL_Walk_Central_stair_lane_step_concrete']))
    west=list(footprints(scene.objects['COL_Walk_West_residential_link_step_concrete']))
    ax=[t for t in central if -26<t[0].y<-16 and -25<t[0].x<-14]
    ax += [t for t in west if -28<t[0].y<-12 and -77<t[0].x<-66]
    stone=[t for t in central if -18<t[0].y<-10 and -25<t[0].x<-14]
    lower=[t for t in central if -65<t[0].y<-52 and -11<t[0].x<17]
    assert len(ax)>5 and len(stone)>1
    work={"COL_Walk_Courtyard_approach_pavement":ax,"Walk_details_Courtyard_approach_stone":ax,"COL_Terrain_200m_stone":stone,"COL_Terrain_200m_yard_concrete":lower,"COL_Terrain_200m_pavement":lower}
    work["COL_R23_PathFoundations"]=ax+stone+lower
    return {name:n for name,loops in work.items() if scene.objects.get(name) and (n:=cut(scene.objects[name],loops))}

