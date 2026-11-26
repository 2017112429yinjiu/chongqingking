"""Shape the slope under the documented footprints and pave the public approaches."""
import numpy as np

def margin(x, y, ring):
    sides = []
    center = ring.mean(axis=0)
    for a,b in zip(ring,np.roll(ring,-1,axis=0)):
        edge = b-a
        normal = np.array([edge[1],-edge[0]]) / np.linalg.norm(edge)
        if (center-a) @ normal > 0:
            normal = -normal
        sides.append((x-a[0])*normal[0]+(y-a[1])*normal[1])
    return np.maximum.reduce(sides)

def door_fraction(key):
    return {"renai_long":2.5/21, "renai_cross":4.5/9, "jinma_classrooms":6.5/13}[key]

def prepare(spec, height, xx, yy, levels, mx, my, rgba):
    grades = {}
    for feature in spec["buildings"]:
        key = feature["id"]
        ring = np.array(feature["points"])
        a,b,c,d = ring
        fraction = door_fraction(key)
        door = a + (b-a)*fraction
        outward = (a-d)/np.linalg.norm(a-d)
        grades[key] = round(height(*(door+outward*.9))+.05,4)
    # The two touching wings have a common floor datum.
    grades["renai_cross"] = grades["renai_long"]
    for feature in spec["buildings"]:
        key=feature["id"]
        ring=np.array(feature["points"])
        distance=margin(xx, yy, ring)
        blend=np.clip(1-np.maximum(distance,0)/.85,0,1)
        levels-=np.maximum(levels-(grades[key]-.16),0)*blend
        edge=margin(mx,my,ring)
        rgba[:,:,1]=np.maximum(rgba[:,:,1], np.clip((1.6-edge)*1.5,0,1))
    school=np.asarray(next(f["points"] for f in spec["buildings"] if f["id"]=="jinma_classrooms"))
    a,b,c,d=school
    rear=(c+d)*.5
    axis=rear-(a+b)*.5
    axis/=np.linalg.norm(axis)
    along=(xx-rear[0])*axis[0]+(yy-rear[1])*axis[1]
    across=np.abs((xx-rear[0])*axis[1]-(yy-rear[1])*axis[0])
    far=height(*(rear+axis*6.2))
    grade=(1-np.clip(along/6.2,0,1))*(grades["jinma_classrooms"]-.08)+np.clip(along/6.2,0,1)*far
    blend=np.clip(2.6-across,0,1)*np.clip(along+1,0,1)*np.clip(7.2-along,0,1)
    levels+=(grade-levels)*blend
    return grades

def fit_school_perimeter(batch, school, floor, landing):
    """Refine only high triangles at the library boundary, keeping the outer slope intact."""
    ring=np.asarray(school,dtype=float)
    rear=(ring[2]+ring[3])*.5
    direction=rear-(ring[0]+ring[1])*.5
    direction/=np.linalg.norm(direction)
    across=np.array([-direction[1],direction[0]])
    head=rear+direction*6.75
    bounds=np.vstack([ring,head+2*across,head-2*across])
    lower,upper=bounds.min(axis=0)-1.4,bounds.max(axis=0)+1.4
    plane=floor-.16
    replacement=type(batch)(batch.name)
    for face,slot,uv in zip(batch.faces,batch.slots,batch.uvs):
        points=[batch.vertices[i] for i in face]
        if (max(p[2] for p in points)<=plane+.00001 or
            any(max(p[k] for p in points)<lower[k] or min(p[k] for p in points)>upper[k] for k in (0,1))):
            replacement.face(points,slot,uv)
            continue
        p,q,r=np.asarray(points)
        # Sample the original triangle plane. At the outside seam every new
        # vertex lies exactly on the original edge, including the UV projection.
        steps=10  # The largest parent diagonal is sqrt(8) metres. Shared edges use identical cuts.
        lattice={(i,j):p+(q-p)*(i/steps)+(r-p)*(j/steps)
                 for i in range(steps+1) for j in range(steps+1-i)}
        coords=np.asarray(list(lattice.values()))
        distance=margin(coords[:,0],coords[:,1],ring)
        fade=np.clip((distance-.32)/(1.30-.32),0,1)
        fade=fade*fade*(3-2*fade)
        drop=np.maximum(0.,coords[:,2]-plane)*(1.-fade)
        # Keep the entire width of the existing rear exit below the individual
        # treads. The landing rejoins the same native uphill ground at 6.2 m.
        along=(coords[:,:2]-rear)@direction
        width=np.abs((coords[:,:2]-rear)@across)
        fraction=np.clip((along-.54)/(6.2-.54),0,1)
        bed=floor+.012+(landing-floor-.012)*fraction-.12
        apron=np.clip((1.76-width)/.44,0,1)*np.clip((6.85-along)/.37,0,1)*np.clip((along+.4)/.3,0,1)
        drop=np.maximum(drop,np.maximum(0.,coords[:,2]-bed)*apron)
        if max(drop)<1e-7:
            replacement.face(points,slot,uv)
            continue
        for vertex,cut in zip(lattice.values(),drop):
            vertex[2]-=cut
        def emit(keys):
            tri=[lattice[key] for key in keys]
            replacement.face(tri,slot,[(v[0]/2.4,v[1]/2.4) for v in tri])
        for i in range(steps):
            for j in range(steps-i):
                emit(((i,j),(i+1,j),(i,j+1)))
                if i+j+1<steps:
                    emit(((i+1,j),(i+1,j+1),(i,j+1)))
    return replacement
