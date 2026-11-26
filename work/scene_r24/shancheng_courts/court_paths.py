"""Stone courses from the public lane to the Renai threshold and the Jinma court."""
import numpy as np

def pave(buildings,elevation,Mesh,flags,stone,court,rear_landing):
    by_id={p["id"]:p for p in buildings}
    long=by_id["renai_long"]
    school=by_id["jinma_classrooms"]
    pavement=Mesh("COL_Court_FlagstoneApproaches")
    stones=Mesh("Court_FlagstoneCourses")
    lane=[-162.0907,37.8547]
    def approach(rec,lead,width, joins_court=False):
        entry=np.array(rec["entry"])
        inward=np.array(rec["inward"])
        coords=[np.array(p,dtype=float) for p in lead]+[entry-inward*1.1,entry+inward*.24]
        heights=[elevation(p)+.055 for p in coords[:-2]]+[rec["floor"]+.012,rec["floor"]+.012]
        if joins_court:
            for j,q in enumerate(coords):
                x,y=court.local(q)
                if 0<=x<=court.length and 0<=y<=court.depth:
                    heights[j]=court.height(x,y)
            for j,(a,b) in enumerate(zip(coords,coords[1:])):
                first,last=court.local(a)[1],court.local(b)[1]
                if first>court.depth and last<=court.depth:
                    q=a+(b-a)*((first-court.depth)/(first-last))
                    coords.insert(j+1,q)
                    heights.insert(j+1,court.surface(q))
                    break
        # At the junction the paving is flush with the native stones. As the
        # ground climbs the school court, narrow courses turn with its perimeter.
        edges=np.diff(coords,axis=0)
        lens=np.linalg.norm(edges,axis=1)
        tangents=edges/lens[:,None]
        normals=np.column_stack((-tangents[:,1],tangents[:,0]))
        bisectors=[normals[0]]
        for n,m in zip(normals,normals[1:]):
            bis=n+m
            bisectors.append(bis/max(.85,float(bis@n)))
        bisectors.append(normals[-1])
        for i,length in enumerate(lens):
            if joins_court and court.local(coords[i])[1]<=court.depth+.0001:
                continue
            n=max(1,round(length/.69))
            def xyz(t,w,visual):
                q=coords[i]+t*edges[i]+w*((1-t)*bisectors[i]+t*bisectors[i+1])
                h=heights[i]*(1-t)+heights[i+1]*t
                if i<len(lens)-2:
                    h=max(h,elevation(q)+.03)
                return [*q,h+.008*visual]
            def tile(t0,t1,w0,w1,mesh,mat,visual):
                ps=[xyz(t0,w0,visual),xyz(t1,w0,visual),xyz(t1,w1,visual),xyz(t0,w1,visual)]
                if np.cross(np.subtract(ps[1],ps[0]),np.subtract(ps[2],ps[0]))[2]<0:ps.reverse()
                mesh.face(ps,mat)
            for step in range(n):
                for row in range(4):
                    w0=width*(row/2-1);w1=w0+width/2
                    tile(step/n,(step+1)/n,w0,w1,pavement,stone,0)
                    tile((step+.009)/n,(step+.991)/n,w0+.006,w1-.006,stones,flags[(i+row+step)%len(flags)],1)
        return [[float(q[0]),float(q[1]),float(h)] for q,h in zip(coords,heights)]
    results={
        "renai":approach(long,[lane,[-161.05,33.98]],1.05),
        "school":approach(school,[lane,[-157.0,39.5],[-152.8,41.8],[-147.9,40.1],[-142.2,39.5],[-138.1,41.0]],1.23,joins_court=True)}
    inward=np.asarray(school["inward"])
    # Carry the existing lane stones around the downhill end of the long wing.
    # The two mapped footways enclose additional parcels beyond this narrow frontage.
    a,b,c,d=np.asarray(long["ring"])
    for j,(left,right) in enumerate(((a,b),(b,c))):
        v=right-left
        outward=np.array([v[1],-v[0]])/np.linalg.norm(v)
        if np.dot((a+b+c+d)/4-left,outward)>0:outward=-outward
        count=int(np.ceil(np.linalg.norm(v)/.74))
        for i in range(count):
            for row in range(4):
                l=(i+.008)/count;r=(i+.992)/count
                near=.06+row*.46;far=near+.447
                pts=[]
                for t,w in ((l,near),(r,near),(r,far),(l,far)):
                    q=left+t*v+w*outward
                    pts.append([*q,elevation(q)+.046])
                if np.cross(np.subtract(pts[1],pts[0]),np.subtract(pts[2],pts[0]))[2]<0:pts.reverse()
                stones.face(pts,stone if row==3 else flags[(i+row+j)%len(flags)])
    rear=np.array(school["back"])
    side=np.array([-inward[1],inward[0]])
    foot=school["floor"]+.012
    count=int(np.ceil((rear_landing-foot)/.165))
    going=(6.2-.54)/count
    rise=(rear_landing-foot)/count
    def step_point(t,w,h):
        return [*(rear+inward*t+side*w),h]
    def top(mesh,t0,t1,w0,w1,low,high,mat):
        mesh.face([step_point(t0,w0,low),step_point(t1,w0,high),
                   step_point(t1,w1,high),step_point(t0,w1,low)],mat)
    top(pavement,-.20,.54,-1.0,1.0,foot,foot,stone)
    for i in range(count):
        t=.54+going*i
        h=foot+rise*(i+1)
        top(pavement,t,t+going,-1.11,1.11,h,h,stone)
        pavement.face([step_point(t,1.11,h-rise),step_point(t,-1.11,h-rise),
                       step_point(t,-1.11,h),step_point(t,1.11,h)],flags[i%3])
        joint=(-.20 if i%2 else .20)
        for j,(l,r) in enumerate(((-.985,joint),(joint,.985))):
            top(stones,t+.002,t+going-.004,l+.003,r-.003,h+.003,h+.003,flags[(i+j)%3])
        for sign in (-1,1):
            l,r=sorted((sign*.991,sign*1.11))
            top(stones,t,t+going,l,r,h+.012,h+.012,stone)
            w=sign*1.11
            pts=[step_point(t,w,h-.38),step_point(t+going,w,h-.38),
                 step_point(t+going,w,h+.012),step_point(t,w,h+.012)]
            if sign>0:pts.reverse()
            pavement.face(pts,stone)
    # Beyond the last tread, stitch the complete landing width into the old grade.
    for j in range(4):
        l=-1.11+j*.555
        r=l+.555
        near=[step_point(6.2,w,rear_landing) for w in (l,r)]
        far=[step_point(6.88,w,elevation(rear+inward*6.88+side*w)+.016) for w in (l,r)]
        pavement.face([near[0],far[0],far[1],near[1]],stone)
    results["school_back"]=[step_point(6.20,0,rear_landing),step_point(.54+going*(count//2+.5),0,foot+rise*(count//2+1)),
                            step_point(.30,0,foot),step_point(-.20,0,foot)]
    pavement.save()
    stones.save()
    return results
