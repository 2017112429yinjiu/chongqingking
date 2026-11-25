"""Use the original district's condenser geometry on bearings at occupied bay walls."""
from math import cos,sin,pi
from mathutils import Vector
import bpy
import sys


def place(library,plots,geometry,make_box,frame_at,tube,colors):
    sys.path.insert(0,str(library))
    from architecture_full import _aircon
    templates={}
    identity=lambda x,y,z:(x,-y,z)
    class Parts:
        def box(self,center,size,mat):
            a,b=[tuple(center[i]+k*size[i]/2 for i in range(3)) for k in (-1,1)]
            make_box(self.geo,identity,*a,*b,colors[mat])
        def mesh(self,points,faces,mat):
            for indices in faces:self.geo.face([identity(*points[i]) for i in indices][::-1],colors[mat])
        def cylinder(self,a,b,r,mat,n=8):
            def face(pts,key):self.geo.face(pts,key)
            tube(face,identity(*a),identity(*b),r,colors[mat],n)
            u=Vector(identity(*b))-Vector(identity(*a));u.normalize()
            v=u.cross(Vector((1,0,0)) if abs(u.x)<.8 else Vector((0,1,0))).normalized()
            w=u.cross(v)
            for center,rev in ((a,True),(b,False)):
                pts=[tuple(Vector(identity(*center))+r*(v*cos(i*2*pi/n)+w*sin(i*2*pi/n))) for i in range(n)]
                self.geo.face(pts[::-1] if rev else pts,colors[mat])
        def pipe(self,points,r,mat,n=8):
            for a,b in zip(points,points[1:]):tube(self.geo.face,identity(*a),identity(*b),r,colors[mat],n)
    for p in plots:
        p["facade_work"]["condensers"]=[]
        face=frame_at(*p["east_north"],p["bearing"])
        axes=p["frame"]["u"]
        index=max(range(1,len(axes)-1),key=lambda j:min(axes[j]-axes[j-1],axes[j+1]-axes[j]))
        for floor in range(1,p["floors"],2 if p["name"] else 3):
            key=(floor+p["plot_id"])%3
            if key not in templates:
                parts=Parts();parts.geo=geometry("Outer500_CondenserPrototype")
                _aircon(parts,0,0,key)
                wide=.76+key*.055;high=.51+key*.025
                for side in (-1,1):
                    x=side*wide*.33
                    parts.box((x,.043,-high/2+.10),(.064,.10,.24),"frame")
                    parts.box((x,.28,-high/2-.012),(.073,.21,.027),"dark")
                donor=parts.geo.finish();templates[key]=donor.data
                bpy.data.objects.remove(donor,do_unlink=True)
            obj=bpy.data.objects.new("Outer500_Condenser_%02d_%02d"%(p["plot_id"],floor),templates[key])
            bpy.context.collection.objects.link(obj)
            u=axes[index];z=p["height"]+floor*2.95+1.37
            obj.location=face(u,-p["depth"]/2,z);obj.rotation_euler.z=p["bearing"]
            p["facade_work"]["condensers"].append({"u":u,"floor":floor,"template":key})
