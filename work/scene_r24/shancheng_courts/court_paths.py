"""Stone courses from the public lane to the Renai threshold and the Jinma court."""
import numpy as np

def pave(buildings,elevation,Mesh,flags,stone):
    by_id={p["id"]:p for p in buildings}
    long=by_id["renai_long"]
    school=by_id["jinma_classrooms"]
    pavement=Mesh("COL_Court_FlagstoneApproaches")
    stones=Mesh("Court_FlagstoneCourses")
    lane=[-162.0907,37.8547]
    def approach(rec,lead,width):
        entry=np.array(rec["entry"])
        inward=np.array(rec["inward"])
        coords=[np.array(p,dtype=float) for p in lead]+[entry-inward*1.1,entry+inward*.24]
        heights=[elevation(p)+.055 for p in coords[:-2]]+[rec["floor"]+.012,rec["floor"]+.012]
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
        "school":approach(school,[lane,[-157.0,39.5],[-152.8,41.8],[-147.9,40.1],[-142.2,39.5],[-138.1,41.0]],1.23)}
    # The school photo shows stone to both ends of the facade, with shade trees
    # either side of the entry. The larger garden to the west remains permeable.
    a,b,c,d=np.asarray(school["ring"])
    facade=b-a
    inward=np.asarray(school["inward"])
    outward=-inward
    pits=[a+facade*t+outward*4.65 for t in (.27,.82)]
    rows=8
    width=5.4
    count=int(np.linalg.norm(facade)/.91)
    for row in range(rows):
        for i in range(-1,count):
            l=max(0,(i+(row%2)*.5)/count);r=min(1,(i+1+(row%2)*.5)/count)
            if l>=r:continue
            centre=a+facade*((l+r)/2)+outward*width*((row+.5)/rows)
            if any(np.linalg.norm(centre-p)<.72 for p in pits):continue
            pts=[]
            for f,v in [(l+.0003,(row+.012)/rows),(r-.0003,(row+.012)/rows),(r-.0003,(row+.988)/rows),(l+.0003,(row+.988)/rows)]:
                q=a+facade*f+outward*v*width
                h=elevation(q)+.078
                pts.append([*q,h])
            if np.cross(np.subtract(pts[1],pts[0]),np.subtract(pts[2],pts[0]))[2]<0:pts.reverse()
            stones.face(pts,flags[(row+i)%len(flags)])
    # A stone border keeps the planted earth in the two photographed tree wells.
    for centre in pits:
        for j in range(16):
            l=2*np.pi*j/16;r=2*np.pi*(j+1)/16
            pts=[]
            for angle,radius in ((l,.56),(l,.73),(r,.73),(r,.56)):
                q=centre+radius*np.array([np.cos(angle),np.sin(angle)])
                pts.append([*q,elevation(q)+.089])
            if np.cross(np.subtract(pts[1],pts[0]),np.subtract(pts[2],pts[0]))[2]<0:pts.reverse()
            stones.face(pts,stone)
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
    rear_rec=dict(school,entry=rear.tolist(),inward=(-inward).tolist())
    apron=approach(rear_rec,[rear+inward*6.2,rear+inward*3.8],.99)
    results["school_back"]=apron
    pavement.save()
    stones.save()
    return results
