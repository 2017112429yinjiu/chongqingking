"""Keep each new ground floor clear of the far-only city built before R24."""
import re
from math import sin, cos


def conflicting_context(plots, previous_meshes, roof_records, mapped_ids):
    prefixes, roof_cuts = set(), []
    for name, spec in previous_meshes.items():
        match=re.fullmatch(r"Context_(authored_(\d+)_(\d+)|(\d+))_.+",name)
        if not match:
            continue
        alias,row,col,osm=match.groups()
        a,b=spec["bounds"]
        if not (a[0]>100 or b[0]<-100 or a[1]>100 or b[1]<-100):
            continue
        mapped=osm is not None and int(osm) in mapped_ids
        old_rect=[(x,y) for x in (a[0],b[0]) for y in (a[1],b[1])]
        def intersects(plot):
            x,y=plot["east_north"]; c,s=cos(plot["bearing"]),sin(plot["bearing"])
            half_w,half_d=plot["width"]/2+.4,plot["depth"]/2+.7
            new_rect=[(x+c*u-s*v,y+s*u+c*v) for u in (-half_w,half_w) for v in (-half_d,half_d)]
            for nx,ny in ((1,0),(0,1),(c,s),(-s,c)):
                first=[nx*px+ny*py for px,py in old_rect]
                second=[nx*px+ny*py for px,py in new_rect]
                if max(first)<min(second) or max(second)<min(first):
                    return False
            return True
        if not mapped and not any(intersects(p) for p in plots):
            continue
        seed=int(osm) if osm else 49000+100*int(row)+int(col)
        prefixes.update((f"Context_{alias}_", f"Context_v04_detail_{seed}_"))
        if osm:
            prefixes.add(f"Context_windows_{osm}_")
        if not mapped:
            roof_cuts.extend(r["position"] for r in roof_records if r["donor"]==name)
    return sorted(prefixes),roof_cuts
