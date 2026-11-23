"""Seat each rigid covered car on its four authored tyre patches, preserving its five mesh parts."""
import math
from collections import defaultdict
import numpy as np
from mathutils import Vector,Matrix,Quaternion

def build(scene,change,spatial):
    cars=defaultdict(list)
    for o in scene.objects:
        if o.type=='MESH' and o.name.startswith('Parked_car_'):cars[o.name.rsplit('_',1)[0]].append(o)
    grounds=spatial([o for o in scene.objects if o.type=='MESH' and o.name.startswith(('COL_Terrain_200m','COL_Walk_','COL_Road_','COL_Community_court','COL_R23_Nanqu','COL_B_','COL_R24_LinkDeck')) and 'Retaining' not in o.name])
    reports={};taken=[]
    for name,parts in sorted(cars.items()):
        parts.sort(key=lambda ob:ob.name);tire=[]
        for ob in parts[1:]:
            pts=[ob.matrix_world@v.co for v in ob.data.vertices];z=min(p.z for p in pts)
            contact=[p for p in pts if p.z<z+.003]
            c=sum(contact,Vector())/len(contact);c.z=z;tire.append(c)
        assert len(tire)==4
        center=sum(tire,Vector())*.25
        def support(p):
            points=[]
            for ((xl,xh),(yl,yh),_),tree,tag in grounds:
                if not(xl<=p.x<=xh and yl<=p.y<=yh):continue
                if tag.startswith('COL_B_'):
                    if tree.ray_cast((p.x,p.y,240),(0,0,-1),260)[0] is not None:return None
                    continue
                q,_,_,_=tree.ray_cast((p.x,p.y,center.z+6),(0,0,-1),18)
                if q is not None and q.z<center.z+4:points.append((q.z,tag))

            if not points:return None
            high,tag=max(points)
            if not tag.startswith('COL_Terrain_200m') or tag.endswith(('tree_soil','planting_soil')):return None
            if any(n.startswith(('COL_Road_','COL_Walk_','COL_Community_court')) and abs(high-z)<1.8 for z,n in points):return None
            return high
        proposals=[(0.,0.)]+[(dx,dy) for dx in range(-14,15,2) for dy in range(-14,15,2) if dx or dy]
        best=None
        for dx,dy in sorted(proposals,key=lambda p:p[0]*p[0]+p[1]*p[1]):
            if best and dx*dx+dy*dy>best[0]+1:break
            xy=center+Vector((dx,dy,0))
            if any((xy-q).xy.length<5 for q in taken):continue
            for yaw in [0.,.45,-.45,1.05,-1.05,1.57]:
                rz=Quaternion((0,0,1),yaw);local=[rz@(p-center) for p in tire]
                # Grading and clear ground cover the tyres, bumpers and door clearance.
                probes=local+[p*1.46 for p in local]+[Vector((0,0,0))]
                heights=[support(xy+p) for p in probes]
                if None in heights:continue
                a=np.array([[p.x,p.y,1.] for p in local]);target=np.array(heights[:4]);solution=np.linalg.lstsq(a,target,rcond=None)[0]
                slope=math.hypot(solution[0],solution[1]);residual=max(abs(a@solution-target))
                if slope>.21 or residual>.028:continue
                score=dx*dx+dy*dy+yaw*yaw+residual*210+slope*2
                if not best or score<best[0]:best=(score,xy,rz,solution,heights[:4],yaw)
        if best is None:raise RuntimeError('No four-contact parking surface for '+name)
        _,xy,rz,sol,_,yaw=best;up=Vector((-sol[0],-sol[1],1)).normalized()
        rot=Vector((0,0,1)).rotation_difference(up)@rz
        dest=Vector((xy.x,xy.y,float(sol[2])+.003))
        matrix=Matrix.Translation(dest)@rot.to_matrix().to_4x4()@Matrix.Translation(-center)
        for ob in parts:
            change(ob);ob.matrix_world=matrix@ob.matrix_world
        actual=[matrix@p for p in tire];errors=[p.z-support(p) for p in actual]
        assert max(abs(e) for e in errors)<.042,(name,errors)
        reports[name]=dict(contacts=[list(p) for p in actual],errors_m=errors,center=list(dest),old_center=list(center),yaw_change=yaw)
        taken.append(dest)
    return reports

