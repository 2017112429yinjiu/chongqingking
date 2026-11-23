"""Retriangulate the open courtyard around the junction with shared boundaries."""
import bmesh,math
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

BOUNDS=(24.35,36.45,6.45,19.85)

def patch(scene,main,old_steps,rows,sections,marks,H,east,west,side_at,height,tree,ground_height,make_mesh,changed):
    xmin,xmax,ymin,ymax=BOUNDS
    def inside(x,y):return xmin-1e-5<=x<=xmax+1e-5 and ymin-1e-5<=y<=ymax+1e-5
    def cross(f,axis,d):
        vals=[v.co[axis]-d for v in f.verts];return min(vals)<-1e-6 and max(vals)>1e-6
    def close(f):
        vs=[v.co for v in f.verts]
        return not (all(p.x<xmin-.004 for p in vs) or all(p.x>xmax+.004 for p in vs) or all(p.y<ymin-.004 for p in vs) or all(p.y>ymax+.004 for p in vs))
    rim={};removed={}
    for name in ['COL_Terrain_200m_pavement','COL_Terrain_200m_yard_concrete']:
        ob=scene.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
        region=[f for f in bm.faces if close(f)]
        for axis,d in [(0,xmin),(0,xmax),(1,ymin),(1,ymax)]:
            selected=[f for f in region if f.is_valid and close(f) and cross(f,axis,d)]
            if not selected:continue
            geom=set(selected)
            for face in selected:geom.update(face.verts);geom.update(face.edges)
            at=Vector((0,0,0));normal=at.copy();at[axis]=d;normal[axis]=1.
            result=bmesh.ops.bisect_plane(bm,geom=list(geom),plane_co=at,plane_no=normal,dist=.000001)
            region=list(set([f for f in region if f.is_valid]+[f for f in result['geom'] if isinstance(f,bmesh.types.BMFace) and f.is_valid]))
        faces=[f for f in region if inside(f.calc_center_median().x,f.calc_center_median().y)]
        for f in faces:
            for v in f.verts:
                p=v.co
                if min(abs(p.x-xmin),abs(p.x-xmax),abs(p.y-ymin),abs(p.y-ymax))<.00006:
                    k=(round(p.x,5),round(p.y,5));rim[k]=max(rim.get(k,-100),p.z)
        removed[name]=len(faces)
        if faces:
            bmesh.ops.delete(bm,geom=faces,context='FACES');bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update()
            changed.append(ob)
        bm.free()
    v2=[];ids={};edges=set();forced={};outline=[]
    def vert(p,z=None):
        k=(round(float(p[0]),5),round(float(p[1]),5))
        if k not in ids:ids[k]=len(v2);v2.append(Vector(k))
        if z is not None:forced[k]=z
        return ids[k]
    def link(a,b):
        ia,ib=vert(a),vert(b)
        if ia!=ib:edges.add((min(ia,ib),max(ia,ib)))
    rect=[(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax)]
    for a,b in zip(rect,rect[1:]+rect[:1]):
        chain=[a]+[p for p in rim if min(a[0],b[0])-.00002<=p[0]<=max(a[0],b[0])+.00002 and min(a[1],b[1])-.00002<=p[1]<=max(a[1],b[1])+.00002]+[b]
        chain.sort(key=lambda p:(p[0]-a[0])**2+(p[1]-a[1])**2)
        for q,r in zip(chain,chain[1:]):link(q,r)
    for p,z in rim.items():vert(p,z)
    def clip_line(a,b):
        # Liang-Barsky in XY, retaining every intersection with the existing rim.
        ax,ay=a[:2];bx,by=b[:2];dx=bx-ax;dy=by-ay;lo,hi=0.,1.
        for k,q in [(-dx,ax-xmin),(dx,xmax-ax),(-dy,ay-ymin),(dy,ymax-ay)]:
            if abs(k)<1e-9:
                if q<0:return
            elif k<0:lo=max(lo,q/k)
            else:hi=min(hi,q/k)
        if lo>hi:return
        link((ax+lo*dx,ay+lo*dy),(ax+hi*dx,ay+hi*dy))
    for line in [east,west]:
        ys=sorted(set([ymin,ymax]+[v for v,x in line if ymin<=v<=ymax]+[v for v in marks if ymin<=v<=ymax]))
        for a,b in zip(ys,ys[1:]):
            clip_line((side_at(a,line),a),(side_at(b,line),b))
    def polygon(poly):
        for a,b in zip(poly,poly[1:]+poly[:1]):clip_line(a,b)
        outline.append(poly)
    # Preserve the full existing gravel/dirt tree bed, right up to its surveyed outside ring.
    gravel=scene.objects['COL_Terrain_200m_gravel_ground']
    vertices=[gravel.matrix_world@v.co for v in gravel.data.vertices]
    samples=sorted(set((round(p.x,5),round(p.y,5),round(p.z,5)) for p in vertices if inside(p.x,p.y)))
    def turn(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def half(sequence):
        ans=[]
        for p in sequence:
            while len(ans)>=2 and turn(ans[-2],ans[-1],p)<=1e-9:ans.pop()
            ans.append(p)
        return ans
    hull=half(samples)[:-1]+half(list(reversed(samples)))[:-1]
    assert len(hull)>=20
    polygon([(p[0],p[1]) for p in hull])
    for p in hull:vert(p,p[2])
    for row in rows:polygon(row)
    for face in old_steps.data.polygons:
        if face.normal.z<.99:continue
        pts=[old_steps.matrix_world@old_steps.data.vertices[i].co for i in face.vertices]
        if max(p.x for p in pts)<xmin or min(p.x for p in pts)>xmax or min(p.y for p in pts)>ymax or max(p.y for p in pts)<ymin:continue
        polygon([(p.x,p.y) for p in pts])
    for j in range(1,25):
        for i in range(1,27):
            x=xmin+i*(xmax-xmin)/27.;y=ymin+j*(ymax-ymin)/25.
            vert((x,y))
    vnew,_,faces,*_=delaunay_2d_cdt(v2,list(edges),[],0,.000006)
    def in_poly(x,y,poly):
        hits=0
        for a,b in zip(poly,poly[1:]+poly[:1]):
            if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hits+=1
        return hits%2==1
    graded=[]
    def guide(a,b,za,zb):
        ax,ay=a[0],a[1];dx=b[0]-ax;dy=b[1]-ay
        graded.append((ax,ay,dx,dy,dx*dx+dy*dy,za,zb))
    for i,(near,far) in enumerate(zip(sections,sections[1:])):
        top=H-(4-i)*.169265
        for k in (0,-1):guide(near[k],far[k],top-.169265-.055,top-.055)
    for line in [east,west]:
        ys=sorted(set([ymin,ymax]+[y for y,x in line if ymin<y<ymax]+[v for v in marks if ymin<v<ymax]))
        for a,b in zip(ys,ys[1:]):
            if line is east and marks[0]<(a+b)*.5<marks[-1]:continue
            x=side_at(a,line);u=side_at(b,line);offset=-.012 if line is east else .012
            za=height(tree,x+offset,a);zb=height(tree,u+offset,b)
            if za is not None and zb is not None:guide((x,a),(u,b),za-.08,zb-.08)
    def surface(x,y):
        k=(round(x,5),round(y,5))
        if k in forced:return forced[k]
        z=ground_height(x,y)-.055
        # Preserve the grade of neighbouring terrain right up to the seam.
        distances=sorted(((x-a)**2+(y-b)**2,h) for (a,b),h in rim.items())[:4]
        if distances:
            w=[1/max(d,.0000001) for d,h in distances]
            rim_z=sum(weight*item[1] for weight,item in zip(w,distances))/sum(w)
            t=min(1.,math.sqrt(distances[0][0])/1.20);t=t*t*(3-2*t)
            z=rim_z*(1-t)+z*t
        nearest=1.55**2;target=z
        for ax,ay,dx,dy,l2,za,zb in graded:
            if l2<.000001:continue
            t=max(0.,min(1.,((x-ax)*dx+(y-ay)*dy)/l2))
            d=(x-ax-t*dx)**2+(y-ay-t*dy)**2
            if d<nearest:nearest=d;target=za+(zb-za)*t
        fade=1-min(1,math.sqrt(nearest)/1.55);fade=fade*fade*(3-2*fade)
        boundary=min(x-xmin,xmax-x,y-ymin,ymax-y)
        return z+(target-z)*fade*min(1.,max(0.,boundary/.35))
    ps=[(q.x,q.y,surface(q.x,q.y)) for q in vnew];keep=[]
    for face in faces:
        x=sum(ps[i][0] for i in face)/len(face);y=sum(ps[i][1] for i in face)/len(face)
        if not inside(x,y) or side_at(y,west)-.00001<x<side_at(y,east)+.00001:continue
        if any(in_poly(x,y,poly) for poly in outline):continue
        keep.append(face)
    ob=make_mesh('COL_East17_CourtyardPaving',[(ps,keep)],scene.objects['COL_Terrain_200m_pavement'].data.materials[0])
    # A cut in a hillside exposes the uphill subgrade as well as the downhill stair flank.
    # Seal each interior rim using the very same constrained vertices as the paving above.
    uses={}
    for face in keep:
        for a,b in zip(face,face[1:]+face[:1]):
            uses.setdefault((min(a,b),max(a,b)),[]).append((a,b))
    returns=[]
    for items in uses.values():
        if len(items)!=1:continue
        a,b=items[0];p,q=ps[a],ps[b]
        if any(abs(p[k]-d)<.00007 and abs(q[k]-d)<.00007 for k,d in [(0,xmin),(0,xmax),(1,ymin),(1,ymax)]):continue
        returns.append(([q,p,(p[0],p[1],p[2]-.94),(q[0],q[1],q[2]-.94)],[(0,1,2,3)]))
    make_mesh('COL_East17_ShoulderReturns',returns,scene.objects['COL_R23_PathFoundations'].data.materials[0])
    return {'tree_rim_points':len(hull),'sealed_edges':len(returns),'old_faces':removed,'new_triangles':len(keep),'rim_samples':len(rim),'bounds':BOUNDS}
