"""Cut a ground ribbon between two actual, x-monotone surveyed boundaries."""
import bmesh
from mathutils import Vector

def cut_strip(objects,low,high,change):
    start=max(low.x[0],high.x[0]);end=min(low.x[-1],high.x[-1])
    ymin=min(v.y for v in low.pts)-.05;ymax=max(v.y for v in high.pts)+.05
    removed=0
    for ob in objects:
        bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
        def cut(origin,normal,x0,x1,y0,y1):
            faces=[f for f in bm.faces if max(v.co.x for v in f.verts)>=x0-.018 and min(v.co.x for v in f.verts)<=x1+.018 and max(v.co.y for v in f.verts)>=y0-.018 and min(v.co.y for v in f.verts)<=y1+.018]
            if not faces:return
            geom=set(faces)
            for face in faces:geom.update(face.verts);geom.update(face.edges)
            bmesh.ops.bisect_plane(bm,geom=list(geom),plane_co=origin,plane_no=normal,dist=.00001)
        for x in [start,end]:cut(Vector((x,0,0)),Vector((1,0,0)),x,x,ymin,ymax)
        for edge in [low,high]:
            for a,b in edge.bends():
                d=b-a;cut(a,Vector((-d.y,d.x,0)).normalized(),a.x,b.x,min(a.y,b.y),max(a.y,b.y))
        inside=[]
        for face in bm.faces:
            p=face.calc_center_median()
            if start<p.x<end and low.sample(p.x).y<p.y<high.sample(p.x).y:inside.append(face)
        if inside:
            removed+=len(inside);change(ob);bmesh.ops.delete(bm,geom=inside,context='FACES')
            bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update()
        bm.free()
    return removed

