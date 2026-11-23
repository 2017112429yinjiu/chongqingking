"""Shared corner-room domains and exact clipping of their actual surfaces.

Pure Python. The original window and doorway rectangles are retained as the
floor coverage plan. Overlapping near-street rectangles form one physical
room, with one furnishing owner and no partitions across their intersection.
No proxy, opaque card, shifted floor, or external geometry package is used.
"""
import math

EPS=1.e-8


def area_xy(poly):
    return .5*sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))


def ccw(poly):
    p=[tuple(v[:2]) for v in poly]
    return p if area_xy(p)>=0 else list(reversed(p))


def _clean(poly):
    out=[]
    for p in poly:
        if not out or math.dist(p,out[-1])>EPS:out.append(tuple(p))
    if len(out)>1 and math.dist(out[0],out[-1])<=EPS:out.pop()
    if len(out)<3:return []
    # Remove collinear clipping vertices in 3-D, including vertical polygons.
    changed=True
    while changed and len(out)>3:
        changed=False
        for i,b in enumerate(out):
            a=out[i-1];c=out[(i+1)%len(out)]
            ab=tuple(b[k]-a[k] for k in range(3));bc=tuple(c[k]-b[k] for k in range(3))
            cross=(ab[1]*bc[2]-ab[2]*bc[1],ab[2]*bc[0]-ab[0]*bc[2],ab[0]*bc[1]-ab[1]*bc[0])
            if sum(q*q for q in cross)<1.e-20:
                out.pop(i);changed=True;break
    a=out[0];normal=[0.,0.,0.]
    for b,c in zip(out[1:],out[2:]):
        ab=tuple(b[k]-a[k] for k in range(3));ac=tuple(c[k]-a[k] for k in range(3))
        normal[0]+=ab[1]*ac[2]-ab[2]*ac[1]
        normal[1]+=ab[2]*ac[0]-ab[0]*ac[2]
        normal[2]+=ab[0]*ac[1]-ab[1]*ac[0]
    return out if sum(v*v for v in normal)>1.e-20 else []


def _split(poly,plane):
    distances=[sum(plane[k]*p[k] for k in range(3))+plane[3] for p in poly]
    distances=[0. if abs(d)<EPS else d for d in distances]
    if not any(d<0 for d in distances):return poly,[]
    if not any(d>0 for d in distances):return [],poly
    inside=[];outside=[]
    for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
        da=distances[i];db=distances[(i+1)%len(poly)]
        if da>=0:inside.append(a)
        if da<=0:outside.append(a)
        if da*db<0:
            t=da/(da-db);p=tuple(a[k]+(b[k]-a[k])*t for k in range(3))
            inside.append(p);outside.append(p)
    return _clean(inside),_clean(outside)


def prism_planes(mask):
    p=ccw(mask['polygon']);planes=[]
    for a,b in zip(p,p[1:]+p[:1]):
        dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
        if length<=EPS:continue
        planes.append((-dy/length,dx/length,0.,(dy*a[0]-dx*a[1])/length))
    if math.isfinite(mask.get('bottom',-math.inf)):planes.append((0.,0.,1.,-mask['bottom']))
    if math.isfinite(mask.get('top',math.inf)):planes.append((0.,0.,-1.,mask['top']))
    return planes


def clip_face_outside_prisms(vertices,masks):
    """Subtract convex volumes from a real 3-D polygon, retaining winding.

    keep_boundary belongs only to an earlier member of the same room: if its
    face lies in a peer boundary plane, it keeps that surface. The later
    member removes its coincident coverage, preventing a double face or hole.
    """
    first=_clean([tuple(v) for v in vertices]);parts=[first] if first else []
    for mask in masks:
        planes=prism_planes(mask);next_parts=[]
        for part in parts:
            if mask.get('keep_boundary') and any(all(abs(sum(plane[k]*p[k] for k in range(3))+plane[3])<EPS for p in part) for plane in planes):
                next_parts.append(part);continue
            remaining=part
            for plane in planes:
                if not remaining:break
                remaining,outside=_split(remaining,plane)
                if outside:next_parts.append(outside)
        parts=next_parts
        if not parts:break
    return parts


def convex_intersection(a,b):
    remaining=[(v[0],v[1],0.) for v in ccw(a)]
    for plane in prism_planes({'polygon':b}):
        if not remaining:break
        remaining,_=_split(remaining,plane)
    return [p[:2] for p in remaining]


def overlap_pairs(rooms):
    boxes=[(min(p[0] for p in r['polygon_xy']),min(p[1] for p in r['polygon_xy']),
            max(p[0] for p in r['polygon_xy']),max(p[1] for p in r['polygon_xy'])) for r in rooms]
    pairs=[]
    for i,a in enumerate(rooms):
        ab=boxes[i]
        for j in range(i+1,len(rooms)):
            b=rooms[j];bb=boxes[j]
            if abs(a['floor_top_z']-b['floor_top_z'])>.15:continue
            if ab[2]<=bb[0] or bb[2]<=ab[0] or ab[3]<=bb[1] or bb[3]<=ab[1]:continue
            intersection=convex_intersection(a['polygon_xy'],b['polygon_xy'])
            area=abs(area_xy(intersection)) if intersection else 0.
            if area>1.e-5:pairs.append((a['room_id'],b['room_id'],area))
    return pairs


def shared_room_groups(rooms):
    by_id={r['room_id']:r for r in rooms};adj={}
    for a,b,_ in overlap_pairs(rooms):adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
    groups=[];seen=set()
    for room in rooms:
        first=room['room_id']
        if first not in adj or first in seen:continue
        stack=[first];seen.add(first);members=[]
        while stack:
            current=stack.pop();members.append(current)
            for other in sorted(adj[current]):
                if other not in seen:seen.add(other);stack.append(other)
        if any(by_id[name].get('detail',0)==2 for name in members):groups.append(members)
    return groups


class ClipFrame:
    """A facade mesh sink that trims actual material geometry, not a proxy."""
    def __init__(self,frame,masks):self.frame=frame;self.masks=masks

    def mesh(self,vertices,faces,material,smooth=False):
        if not self.masks:return self.frame.mesh(vertices,faces,material,smooth)
        vs=[];fs=[]
        for face in faces:
            for polygon in clip_face_outside_prisms([vertices[i] for i in face],self.masks):
                first=len(vs);vs.extend(polygon);fs.append(tuple(range(first,len(vs))))
        if fs:self.frame.mesh(vs,fs,material,smooth)
