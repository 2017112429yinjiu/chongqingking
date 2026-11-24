"""Use the actual tread perimeter to shape the landings where two old streets meet."""
from mathutils.geometry import convex_hull_2d

def clip_side(points,axis,at,sign):
    result=[]
    for a,b in zip(points,points[1:]+points[:1]):
        da=(a[axis]-at)*sign
        db=(b[axis]-at)*sign
        if da>=0:result.append(a)
        if (da>=0)!=(db>=0):result.append(a.lerp(b,da/(da-db)))
    return result

def join_flights(key,bounds,ceiling):
    x0,x1,y0,y1=bounds
    cx,cy=(x0+x1)*.5,(y0+y1)*.5
    points=[]
    heights=[]
    for obj in floors:
        if not obj.name.startswith(('COL_Walk_','COL_D18_StoneFlights')):continue
        lo,hi=extent(obj)
        if hi[0]<x0 or lo[0]>x1 or hi[1]<y0 or lo[1]>y1:continue
        for f in obj.data.polygons:
            if f.normal.z<.88:continue
            coords=[obj.matrix_world@obj.data.vertices[i].co for i in f.vertices]
            if any(max(p[k] for p in coords)<low or min(p[k] for p in coords)>high for k,low,high in [(0,x0,x1),(1,y0,y1)]):continue
            for axis,edge,sign in [(0,x0,1),(0,x1,-1),(1,y0,1),(1,y1,-1)]:
                coords=clip_side(coords,axis,edge,sign)
            if len(coords)<3:continue
            for p in coords:points.append(p.xy.copy())
            centre=sum(coords,Vector())/len(coords)
            heights.append([centre.x-cx,centre.y-cy,centre.z])
    rows=np.asarray(heights)
    fit=np.linalg.lstsq(np.column_stack((rows[:,:2],np.ones(len(rows)))),rows[:,2],rcond=None)[0]
    def z(p):return float(fit@[p.x-cx,p.y-cy,1.])
    hull=[points[i] for i in convex_hull_2d(points)]
    # Suppress sub-millimetre remnants left by the neighbouring paving batches.
    ring=[]
    for p in hull:
        if not ring or (p-ring[-1]).length>.006:ring.append(p)
    if (ring[0]-ring[-1]).length<.006:ring.pop()
    if sum(a.x*b.y-a.y*b.x for a,b in zip(ring,ring[1:]+ring[:1]))<0:ring.reverse()
    # A bounded plane makes a broad landing read as a continuous slab. Any
    # slight level difference at a retained tread is taken up by a true riser.
    name='COL_Patrol25_'+key
    levels=[z(p) for p in ring]
    domain=[(ring,min(levels)-1.35,max(levels)+.68)]
    clipped={}
    for obj in floors:
        lo,hi=extent(obj)
        if hi[0]<x0 or lo[0]>x1 or hi[1]<y0 or lo[1]>y1:continue
        removed=solid_clip(obj,domain)
        if removed:clipped[obj.name]=removed
    top=[Vector((p.x,p.y,z(p))) for p in ring]
    face(name,top,'tread')
    for a,b in zip(top,top[1:]+top[:1]):
        n=max(1,math.ceil((a-b).length/.45))
        for step in range(n):
            u=a.lerp(b,step/n);v=a.lerp(b,(step+1)/n)
            face(name,[u,Vector((u.x,u.y,u.z-1.35)),Vector((v.x,v.y,v.z-1.35)),v],'edge')
    measure['street_landings'].append({'name':key,'perimeter':[[p.x,p.y,z(p)] for p in ring],
        'tread_samples':len(rows),'gradient':list(fit[:2]),'removed':clipped})
