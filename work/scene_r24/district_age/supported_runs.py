"""Remove connected, fully supported pavement runs and feather the terrain to their retained abutments."""
import math,bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def trim_supported(scene,terrain,changed,rings,support_gaps):
    # Limits stop before the structural cut-outs of the south market apron and the east steps.
    windows={'OSM_734116601_0':[(-102,-18)],'OSM_734116598_0':[(-102,-89),(-46,-28)],'Upper_courtyard_walk':[(-22,19),(37,70)]}
    joints=[];report={}
    for key,bands in windows.items():
        ob=scene.objects['COL_Walk_'+key+'_pavement'];mesh=ob.data
        remove=[];keep=[];run=[]
        def edges(pts):
            for a,b in zip(pts,pts[1:]+pts[:1]):
                k=tuple(sorted([tuple(round(t,4) for t in v) for v in (a,b)]))
                yield k,(a,b)
        for f in mesh.polygons:
            pts=[ob.matrix_world@mesh.vertices[k].co for k in f.vertices]
            if not any(all(lo<=p.x<=hi for p in pts) for lo,hi in bands):keep.append(pts);continue
            c=sum(pts,Vector())/len(pts)
            for v in [c]+[p.lerp(c,.02) for p in pts]+[(v+pts[(i+1)%len(pts)])*.49+c*.02 for i,v in enumerate(pts)]:
                if abs(v.x)>=99.999:continue
                q=terrain.down(v.x,v.y,v.z+.65,1.48)
                assert q and abs(q[0][0]-v.z)<.54,(key,list(v),q)
                support_gaps.append(v.z-q[0][0])
            remove.append(f.index);run.append(pts)
        rim={k:v for ps in keep for k,v in edges(ps)}
        abut={k:v for ps in run for k,v in edges(ps) if k in rim}
        assert abut,(key,'missing border')
        joints.extend(abut.values());rings.extend(run)
        bm=bmesh.new();bm.from_mesh(mesh);bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm,geom=[bm.faces[i] for i in remove],context='FACES')
        bm.to_mesh(mesh);bm.free();mesh.update();changed.add(ob.name)
        vs=[];fs=[]
        for ring in run:
            n=len(vs);vs.extend([(p.x,p.y,0) for p in ring]);fs.append(tuple(range(n,len(vs))))
        flat=BVHTree.FromPolygons(vs,fs)
        trim=scene.objects['Walk_details_'+key+'_stone'];bm=bmesh.new();bm.from_mesh(trim.data)
        gone=[f for f in bm.faces if flat.find_nearest((*f.calc_center_median()[:2],0),.20)[0] is not None]
        bmesh.ops.delete(bm,geom=gone,context='FACES');bm.to_mesh(trim.data);bm.free();trim.data.update();changed.add(trim.name)
        report[key]={'removed_faces':len(run),'trim_faces':len(gone),'abutments':[[list(a),list(b)] for a,b in abut.values()]}
    # Sample the *old* grade on the retained abutment before changing shared terrain vertices.
    bank=[]
    for a,b in joints:
        if (a-b).length<.5:continue
        delta=b.xy-a.xy;length=delta.length;u=delta.normalized()
        old=[]
        for i in range(9):
            p=a.lerp(b,i/8);h=terrain.down(p.x,p.y,p.z+.65,1.45)
            assert h
            old.append(p.z-h[0][0])
        bank.append((a,b,u,length,old))
    def fall(v):
        v=min(1.,max(0.,v));return 1-v*v*(3-2*v)
    updates={}
    for ob in scene.objects:
        if ob.type!='MESH' or not ob.name.startswith('COL_Terrain_200m'):continue
        count=0
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co;best=0.;dz=0.
            for a,b,u,length,profile in bank:
                delta=p.xy-a.xy
                if abs(delta.x)>length+3.4 or abs(delta.y)>length+3.4:continue
                t=delta.dot(u);perp=abs(delta.x*u.y-delta.y*u.x)
                w=fall(perp/2.95)*fall(max(-t,t-length,0)/1.10)
                if w<=best:continue
                ix=min(8.,max(0.,t/length*8));k=min(7,int(ix))
                if abs(p.z-(a.z+(b.z-a.z)*ix/8))>1.25:continue
                dz=w*(profile[k]+(profile[k+1]-profile[k])*(ix-k));best=w
            if abs(dz)>.0001:p.z+=dz;v.co=ob.matrix_world.inverted()@p;count+=1
        if count:ob.data.update();changed.add(ob.name);updates[ob.name]=count
    report['terrain_vertices']=updates
    return report
