"""Compare inherited gameplay plots to the 56 OSM building polygons in this query."""
from pathlib import Path
from math import cos,sin,hypot
import json

here=Path(__file__).resolve().parent
layout=json.loads((here.parents[2]/"work/project/chongqing_godot_v05/assets/district_500/layout.json").read_bytes())
reference=json.loads((here/"frontage_controls.json").read_bytes())
def area(points):
    if len(points)<3:return 0.
    return abs(sum(x*b-a*y for (x,y),(a,b) in zip(points,points[1:]+points[:1])))*.5
def clip(poly,axis,sign,limit):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        aa=sign*a[axis]-limit;bb=sign*b[axis]-limit
        if (aa<=0)!=(bb<=0):
            t=aa/(aa-bb)
            out.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t))
        if bb<=0:out.append(b)
    return out
def segment_distance(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    t=min(1,max(0,-(a[0]*dx+a[1]*dy)/max(1e-20,dx*dx+dy*dy)))
    return hypot(a[0]+t*dx,a[1]+t*dy)
results=[]
for p in layout["plots"]:
    x,y=p["east_north"];c,s=cos(p["bearing"]),sin(p["bearing"])
    width,depth=p["width"],p["depth"]
    best=(0.,0.,None);nearest=(float("inf"),None)
    for f in reference["frontages"]:
        areas=[];cuts=[]
        for ring in f["rings"]:
            points=[((a-x)*c+(b-y)*s,-(a-x)*s+(b-y)*c) for a,b in ring[:-1]]
            nearest=min(nearest,(min(segment_distance(a,b) for a,b in zip(points,points[1:]+points[:1])),f["osm"]))
            areas.append(area(points))
            for axis,lim in ((0,width/2),(1,depth/2)):
                for sign in (-1,1):points=clip(points,axis,sign,lim)
            cuts.append(area(points))
        overlap=cuts[0]-sum(cuts[1:])
        if overlap<=1e-5:continue
        union=width*depth+areas[0]-sum(areas[1:])-overlap
        best=max(best,(overlap/union,overlap,f["osm"]))
    results.append({"plot_id":p["plot_id"],"nearest_mapped_edge_to_plot_center_m":round(nearest[0],2),"nearest_osm":nearest[1],"overlap_osm":best[2],"best_iou":round(best[0],4),"intersect_m2":round(best[1],2)})
out={"scope":"Only the 56 identified OSM footprints from this query. A missing or overlapping footprint alone does not identify the building. OSM outline data are incomplete. Compare occupied rectangles only, excluding stairs and courtyards.","plots":results}
(here/"evidence/legacy_coverage.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print("Legacy",len(results),"with some overlap",sum(bool(a["overlap_osm"]) for a in results),"best IoU",max(a["best_iou"] for a in results))
