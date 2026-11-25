"""Turn existing estate steps along their facade where a straight flight occupies asphalt."""
from math import ceil
import numpy as np

def stair_frontage(p,draw,ground,stone,edge,direction,reserve,world):
    z=p["height"]+.025
    mid=p["door_u"]
    key="front" if direction<0 else "back"
    def corners(a,b,v0,v1):
        return [world(p,u,v) for u in np.linspace(a,b,max(2,ceil(abs(b-a)/.35)+1))
                for v in np.linspace(v0,v1,max(2,ceil(abs(v1-v0)/.35)+1))]
    def clearance(a,b,v0,v1):
        return float(reserve.margin(corners(a,b,v0,v1)).min())
    for count in range(1,34):
        old_run=1.40+count*.32
        if p["height"]-ground(mid,edge+direction*old_run)<=count*.155:break
    original=clearance(mid-1.25,mid+1.25,edge,edge+direction*old_run)
    if original>=.50:return None
    candidates=[]
    for width in (1.62,1.32,1.04,.76):
        v0=edge
        v1=edge+direction*width
        vm=(v0+v1)/2
        for side in (-1,1):
            begin=mid+side*.97
            for count in range(1,43):
                end=begin+side*count*.31
                low=ground(end+side*.14,vm)
                if z-low<=count*.16:break
            margin=clearance(min(mid-.97,end),max(mid+.97,end),v0,v1)
            if margin<.16:continue
            overhang=max(0,abs(end)-p["width"]/2)
            candidates.append((overhang*.9+count*.085-width*2,-margin,side,width,count,end,low))
    if not candidates:raise ValueError(("No roadside entrance clearance",p["plot_id"],key))
    _,neg_margin,side,width,count,end,low=min(candidates)
    vm=edge+direction*width*.5
    v0,v1=sorted((edge,edge+direction*width))
    def block(a,b,level):
        a,b=sorted((a,b))
        floor=min(ground(u,v) for u in (a,b) for v in (v0,v1))
        draw(a,v0,min(floor-.15,level-.17),b,v1,level,stone)
    block(mid-.97,mid+.97,z)
    rise=max(0,z-low)/count
    for i in range(count):
        start=mid+side*(.97+i*.31)
        block(start,start+side*.31,z-rise*(i+1))
    p.setdefault("kerb_stairs",{})[key]={"pad":[mid,vm],"toe":[end+side*.24,vm],
        "direction":side,"width_m":width,"steps":count,"riser_m":rise,"road_clearance_m":-neg_margin,
        "original_road_clearance_m":original,"edge":edge}
    return width
