"""Reconcile the heights at the Zhongxing / Nanqu road mouths and cut competing road sheets."""
import math,bisect,bmesh
from mathutils import Vector

PRIMARY={'west':(1189963547,49182408),'east':(1189963598,830761786)}
CONNECTORS=(176034707,1375242616,1375242618,1256840008)

def ease(a,b,u):
    t=min(1.,max(0.,(u-a)/(b-a)));return t*t*(3-2*t)

def sections(scene,ids):
    sections=[]
    for way in ids:
        ob=scene.objects['COL_Road_%s_0_asphalt'%way]
        verts=[ob.matrix_world@v.co for v in ob.data.vertices]
        for a,b in zip(verts[::2],verts[1::2]):
            a,b=sorted((a,b),key=lambda p:p.y)
            sections.append((a,b))
    return sorted(sections,key=lambda row:row[0].x)

class Edge:
    def __init__(self,points):
        self.pts=sorted(points,key=lambda p:p.x)
        self.x=[p.x for p in self.pts]
    def sample(self,x):
        i=max(0,min(len(self.x)-2,bisect.bisect_right(self.x,x)-1));a,b=self.pts[i:i+2]
        u=min(1.,max(0.,(x-a.x)/max(.00001,b.x-a.x)))
        return a.lerp(b,u)
    def bends(self):
        points=[self.pts[0]]
        for q in self.pts[1:]:
            if (q-points[-1]).xy.length<.01:continue
            if len(points)>1:
                direction=(q-points[-2]).xy.normalized()
                if abs(direction.cross((points[-1]-points[-2]).xy))<.001:points.pop()
            points.append(q)
        return list(zip(points,points[1:]))

def build(scene,s,change,surface,box,rod,mat,spatial):
    ids={str(i) for i in PRIMARY['west']+PRIMARY['east']+CONNECTORS}
    original=spatial([o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Road_') and o.name.split('_')[2] in ids and o.name.endswith(('_asphalt','_pavement'))])
    rows={k:sections(scene,roads) for k,roads in PRIMARY.items()}
    high=Edge([(a+b)*.5 for a,b in rows['west']]);low=Edge([(a+b)*.5 for a,b in rows['east']])
    def delta(x):
        return max(0.,high.sample(x).z-low.sample(x).z-.12)*ease(6.,31.,x)*(1.-ease(59.,84.,x))
    # Lift the existing lower carriageway and its markings together only around
    # the at-grade merge. Both mapped ways retain their plan and UV coordinates.
    shifted={}
    for ob in list(scene.objects):
        if ob.type!='MESH' or not any(ob.name.startswith(('COL_Road_%s_'%i,'Road_paint_%s_'%i)) for i in PRIMARY['east']):continue
        world=ob.matrix_world; inv=world.inverted()
        if not any(delta((world@v.co).x)>.0001 for v in ob.data.vertices):continue
        change(ob);peak=0.
        for v in ob.data.vertices:
            p=world@v.co;dz=delta(p.x);peak=max(peak,dz);p.z+=dz;v.co=inv@p
        ob.data.update();shifted[ob.name]=peak
    decks={k:[Edge([r[s] for r in sections(scene,ids)]) for s in (0,1)] for k,ids in PRIMARY.items()}
    boundaries=[e for edges in decks.values() for e in edges]
    def level(x,y):
        result=[]
        for l,r in decks.values():
            a=l.sample(x);b=r.sample(x)
            offset=max(a.y-y,y-b.y,0.)
            t=max(0.,min(1.,(y-a.y)/max(b.y-a.y,.001)))
            result.append((offset,a.z+(b.z-a.z)*t))
        return min(result)
    cuts={}
    for ob in list(scene.objects):
        if ob.type!='MESH' or not any(ob.name.startswith(('COL_Road_%s_'%i,'Road_paint_%s_'%i)) for i in CONNECTORS):continue
        bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
        for e in boundaries:
            for a,b in e.bends():
                if b.x<20 or a.x>100:continue
                x0,x1=sorted((a.x,b.x));y0,y1=sorted((a.y,b.y))
                faces=[f for f in bm.faces if max(v.co.x for v in f.verts)>=x0-.02 and min(v.co.x for v in f.verts)<=x1+.02 and max(v.co.y for v in f.verts)>=y0-.02 and min(v.co.y for v in f.verts)<=y1+.02]
                if not faces:continue
                geom=set(faces)
                for face in faces:geom.update(face.edges);geom.update(face.verts)
                d=b-a
                bmesh.ops.bisect_plane(bm,geom=list(geom),plane_co=a,plane_no=Vector((-d.y,d.x,0)).normalized(),dist=.00001)
        cut=[]
        for f in bm.faces:
            p=f.calc_center_median()
            median=decks['east'][1].sample(p.x).y<p.y<decks['west'][0].sample(p.x).y
            if 18<p.x<100.01 and (median or level(p.x,p.y)[0]<.0001):cut.append(f)
        count=len(cut)
        if count:bmesh.ops.delete(bm,geom=cut,context='FACES')
        moved=0
        for v in bm.verts:
            p=v.co
            if not 18<p.x<100.01:continue
            gap,z=level(p.x,p.y)
            if gap>6:continue
            offset=.013 if 'paint_' in ob.name else 0.
            # Curb and pavement taper flush at the mouth, retaining their full profile away from it.
            v.co.z+=(z+offset-p.z)*(1.-ease(0.,6.,gap));moved+=1
        if count or moved:
            change(ob);bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update()
            cuts[ob.name]=[count,moved]
        bm.free()
    from junction_support_r24 import road_patch
    repaired=road_patch(scene,change,surface,mat,spatial,original,{str(i) for i in PRIMARY['west']+PRIMARY['east']+CONNECTORS},decks)
    from median_frontage_r24 import build as close_median
    median=close_median(s,decks,original,surface,mat,box,rod)
    return dict(raised_existing=shifted,connector_changes=cuts,ground=repaired,median=median)
