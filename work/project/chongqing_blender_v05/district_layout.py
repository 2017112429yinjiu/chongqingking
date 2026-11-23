"""OSM XY + explicitly authored terrain and circulation for the 200 m sample."""
from pathlib import Path
import json, math
ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'source_data/geo_layout.json').read_text())
SPINE=[(16.,-66.),(-20.,-52.),(-20.,-30.),(-18.,-8.),(-18.,14.),(-40.,38.),(-37.,43.),(-33.1,50.),(-28.7,57.),(-25.,64.),(-17.,77.),(-27.,90.)]
SUPPLEMENTAL=[
 ('Main hillside lane',SPINE,3.8),
 ('West residential link',[(-93.,-45.),(-74.,-34.),(-73.,-8.),(-76.,17.),(-74.,40.),(-77.,61.),(-75.,86.)],2.7),
 ('Courtyard approach',[(-18.,-8.),(-18.5,-19.7),(-49.,-19.7),(-50.,-33.),(-70.,-33.),(-73.,-8.)],2.8),
 ('Upper courtyard walk',[(-18.,14.),(0.,5.),(26.,5.),(28.,14.),(34.,38.),(42.,56.),(60.,56.),(66.,56.)],3.1),
 ('Old school approach',[(-25.,64.),(-12.,59.),(6.,59.),(20.,59.),(42.,56.)],2.5),
 ('East photo alley',[(52.,-61.7),(48.,-49.),(52.,-35.),(49.,-19.),(35.,5.),(28.,14.)],2.5),
]
def raw_height(x,y):
    return 5.5+.148*(y+100)+.022*x+.6*math.sin(x/32)*math.sin((y+30)/44)
def distance_segment(p,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];d=dx*dx+dy*dy
    t=max(0.,min(1.,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d)) if d else 0.
    q=(a[0]+t*dx,a[1]+t*dy)
    return math.dist(p,q),q,t
def line_distance(p,pts):
    return min(distance_segment(p,a,b)[0] for a,b in zip(pts,pts[1:]))
def point_in_poly(p,poly):
    x,y=p;inside=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside
def clip_segment(a,b,limit=100.):
    dx=b[0]-a[0];dy=b[1]-a[1];t0=0.;t1=1.
    for p,q in [(-dx,a[0]+limit),(dx,limit-a[0]),(-dy,a[1]+limit),(dy,limit-a[1])]:
        if abs(p)<1e-9:
            if q<0:return None
            continue
        r=q/p
        if p<0:t0=max(t0,r)
        else:t1=min(t1,r)
        if t0>t1:return None
    return ((a[0]+dx*t0,a[1]+dy*t0),(a[0]+dx*t1,a[1]+dy*t1))
def clip_line(points,limit=100.):
    out=[];current=[]
    for a,b in zip(points,points[1:]):
        s=clip_segment(a,b,limit)
        if not s:
            if len(current)>1:out.append(current)
            current=[];continue
        if current and math.dist(current[-1],s[0])>.01:
            if len(current)>1:out.append(current)
            current=[]
        if not current:current.append(s[0])
        current.append(s[1])
    if len(current)>1:out.append(current)
    return out
def clipped_polygon(poly,limit=100.):
    for axis,bound,greater in [(0,-limit,True),(0,limit,False),(1,-limit,True),(1,limit,False)]:
        result=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            ia=a[axis]>=bound if greater else a[axis]<=bound
            ib=b[axis]>=bound if greater else b[axis]<=bound
            if ia:result.append(a)
            if ia!=ib:
                t=(bound-a[axis])/(b[axis]-a[axis]);result.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
        poly=result
        if not poly:return []
    return poly
def road_width(item):
    return item.get('width') or {'secondary':6.4,'secondary_link':5.2,'tertiary':6.,'residential':5.2,'primary_link':4.4,'footway':2.5,'steps':2.6}.get(item['type'],2.6)
GRADE=[]
for item in DATA['roads']+DATA['paths']:
    if item['tags'].get('tunnel')=='yes' or item['tags'].get('bridge')=='yes':continue
    for pts in clip_line(item['points']):
        for a,b in zip(pts,pts[1:]):GRADE.append((a,b,road_width(item)))
for _,pts,w in SUPPLEMENTAL:
    for a,b in zip(pts,pts[1:]):GRADE.append((a,b,w))
def ground_height(x,y):
    z=raw_height(x,y);best=None
    for a,b,w in GRADE:
        r=w*.5+1.
        if not (min(a[0],b[0])-r<x<max(a[0],b[0])+r and min(a[1],b[1])-r<y<max(a[1],b[1])+r):continue
        d,q,t=distance_segment((x,y),a,b);f=max(0.,min(1.,r-d))
        if f and (best is None or d<best[0]):best=(d,raw_height(*q),f)
    if best:z=z*(1-best[2])+best[1]*best[2]
    # An authored level community court. Not a measured terrain source.
    if -48<x<-20 and -17<y<17:
        edge=min(x+48,-20-x,y+17,17-y)
        fac=max(0.,min(1.,edge/2.))
        z=z*(1-fac)+20.45*fac
    return z
def godot(p):return [round(p[0],4),round(p[2],4),round(-p[1],4)]
