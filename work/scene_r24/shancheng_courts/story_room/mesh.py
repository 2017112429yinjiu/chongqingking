"""Metric board, turned profile and print surfaces in a furniture maker's local frame."""
from math import sin, cos, tau
from mathutils import Vector
import bpy

class Batch:
    def __init__(self,name,point):
        self.name,self.point=name,point
        self.verts,self.faces,self.uv,self.slots,self.materials=[],[],[],[],[]
        self.place(0,0,0)

    def place(self,x,y,angle):
        self.x,self.y=x,y
        self.c,self.s=cos(angle),sin(angle)

    def face(self,points,mat,uv=None):
        if mat not in self.materials:self.materials.append(mat)
        off=len(self.verts)
        self.verts.extend(self.point(self.x+u*self.c-v*self.s,self.y+u*self.s+v*self.c,h) for u,v,h in points)
        self.faces.append(tuple(range(off,off+len(points))))
        self.slots.append(self.materials.index(mat))
        if uv is None:
            a,b,c=map(Vector,points[:3])
            normal=(b-a).cross(c-a)
            axis=max(range(3),key=lambda k:abs(normal[k]))
            dims=((1,2),(0,2),(0,1))[axis]
            uv=[(p[dims[0]],p[dims[1]]) for p in points]
        self.uv.extend(uv)

    def board(self,x,y,z,w,d,h,mat,edge=.004,foot=None):
        # Three-dimensional rounded arrises, with a narrower foot for tapered joinery.
        e=min(edge,h*.21,w*.12,d*.12)
        def section(dw,dd,height):
            a,b=dw*.5,dd*.5;r=min(e,a*.19,b*.19)
            return [(x+u,y+v,height) for u,v in ((-a+r,-b),(a-r,-b),(a,-b+r),(a,b-r),
                        (a-r,b),(-a+r,b),(-a,b-r),(-a,-b+r))]
        fw,fd=foot if foot else (w,d)
        rings=[section(fw-e,fd-e,z),section(fw,fd,z+e),section(w,d,z+h-e),section(w-e,d-e,z+h)]
        long=max(range(3),key=lambda i:(w,d,h)[i])
        offset=((x*.71+y*.27+z*.33)%1,(y*.69+z*.14)%1)
        def face(pts):
            a,b,c=map(Vector,pts[:3]);n=(b-a).cross(c-a)
            side=max(range(3),key=lambda i:abs(n[i]))
            u=long if side!=long else (side+1)%3
            v=next(i for i in range(3) if i not in (u,side))
            self.face(pts,mat,[(offset[0]+p[u]*.82,offset[1]+p[v]*.82) for p in pts])
        face(rings[0][::-1]);face(rings[-1])
        for ra,rb in zip(rings,rings[1:]):
            for i in range(8):
                j=(i+1)%8;face([ra[i],ra[j],rb[j],rb[i]])

    def tube(self,a,b,r,mat,end=None,sides=12):
        a,b=Vector(a),Vector(b)
        along=(b-a).normalized()
        ref=Vector((0,0,1)) if abs(along.z)<.88 else Vector((0,1,0))
        u=along.cross(ref).normalized();v=along.cross(u)
        rings=[]
        for p,rad in ((a,r),(b,r if end is None else end)):
            rings.append([tuple(p+rad*(u*cos(tau*i/sides)+v*sin(tau*i/sides))) for i in range(sides)])
        ra,rb=rings
        self.face(ra[::-1],mat);self.face(rb,mat)
        for i in range(sides):
            j=(i+1)%sides;self.face([ra[i],ra[j],rb[j],rb[i]],mat)

    def turn(self,x,y,z,profile,mat):
        for (h,r),(hh,rr) in zip(profile,profile[1:]):
            self.tube((x,y,z+h),(x,y,z+hh),r,mat,rr,20)

    def print(self,corners,tile,mat,rect=(.004,.006,.996,.994)):
        l,b,r,t=rect
        u,v=tile%4,3-tile//4
        self.face(corners,mat,[((u+a)/4,(v+c)/4) for a,c in ((l,b),(r,b),(r,t),(l,t))])

    def save(self):
        mesh=bpy.data.meshes.new(self.name)
        mesh.from_pydata(self.verts,[],self.faces)
        for m in self.materials:mesh.materials.append(m)
        mesh.polygons.foreach_set("material_index",self.slots)
        mesh.uv_layers.new(name="Story room UV").data.foreach_set("uv",[n for p in self.uv for n in p])
        mesh.update()
        obj=bpy.data.objects.new(self.name,mesh)
        bpy.context.collection.objects.link(obj)
        return obj
