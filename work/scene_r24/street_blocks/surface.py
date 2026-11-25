"""Pave occupied frontage and the registered Shancheng Lane; keep garden and river soils."""
import numpy as np
import json
from pathlib import Path

def apply(plots,source,segments,mx,my,rgba):
    path=next(r for r in source["paths"] if r["id"]==734116601)
    # The preserved center carries its own material layer; use the outer terrain only.
    outer=np.maximum(abs(mx),abs(my))>100
    strip=np.zeros_like(mx)
    def rectangle(p,cx,cy,w,h):
        x,y=p["east_north"];a=p["bearing"];c,s=np.cos(a),np.sin(a)
        u=(mx-x)*c+(my-y)*s-cx;v=-(mx-x)*s+(my-y)*c-cy
        return np.clip((.28-np.maximum(abs(u)-w,abs(v)-h))/.55,0,1)
    for p in plots:
        w,d=p["width"]*.5,p["depth"]*.5
        strip=np.maximum(strip,rectangle(p,0,-1.0,w+2.10,d+3.20))
        if p.get("court"):
            court=p["court"]
            strip=np.maximum(strip,rectangle(p,court["center_u"],d+6.25,court["half_width"]+1.3,7.55))
        for stair in p.get("kerb_stairs",{}).values():
            u,v=stair["toe"];mid,v0=stair["pad"]
            strip=np.maximum(strip,rectangle(p,(u+mid)*.5,v,(abs(u-mid)*.5)+1.45,stair["width_m"]*.5+1.2))
    def band(points,width):
        nonlocal strip
        for a,b in zip(points,points[1:]):
            dx,dy=b[0]-a[0],b[1]-a[1];sq=dx*dx+dy*dy
            if sq<.001:continue
            f=np.clip(((mx-a[0])*dx+(my-a[1])*dy)/sq,0,1)
            distance=np.hypot(mx-a[0]-f*dx,my-a[1]-f*dy)
            strip=np.maximum(strip,np.clip((width+.22-distance)/.44,0,1))
    # Identifiable west course, between verified clear points along the OSM way.
    band(path["points"][:47],1.65)
    for line,width,key in segments:
        if isinstance(key,int):band(line,width+2.8)
    controls=json.loads(Path(__file__).with_name("frontage_controls.json").read_bytes())
    def boundary_field(ring,margin):
        ring=np.asarray(ring)
        low=ring.min(axis=0)-margin-.5;high=ring.max(axis=0)+margin+.5
        xs=np.flatnonzero((mx[0]>=low[0])&(mx[0]<=high[0]))
        ys=np.flatnonzero((my[:,0]>=low[1])&(my[:,0]<=high[1]))
        if not (len(xs) and len(ys)):return None
        sl=np.s_[ys[0]:ys[-1]+1,xs[0]:xs[-1]+1];x=mx[sl];y=my[sl]
        inside=np.zeros(x.shape,dtype=bool);dist=np.full(x.shape,np.inf)
        for a,b in zip(ring[:-1],ring[1:]):
            dx,dy=b-a
            if dx*dx+dy*dy<1e-6:continue
            t=np.clip(((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy),0,1)
            dist=np.minimum(dist,np.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
            if abs(dy)>1e-8:inside^=((a[1]>y)!=(b[1]>y))&(x<a[0]+dx*(y-a[1])/dy)
        return sl,np.where(inside,0.,dist)
    # These are frontage-ground inferences bounded by mapped buildings. Distinct courtyards
    # within outlines with holes and the designated river park keep their existing treatment.
    ground=np.zeros_like(mx)
    for item in controls["frontages"]:
        q=boundary_field(item["rings"][0],4.0)
        if q is None:continue
        sl,dist=q
        ground[sl]=np.maximum(ground[sl],np.clip((4.0-dist)*2.,0,1))
        for hole in item["rings"][1:]:
            q=boundary_field(hole,0)
            if q:
                hs,hd=q;ground[hs]=np.where(hd==0,0,ground[hs])
    # Join the actual lane to the facing walls of the four registered homes. The
    # projection is capped so a distant home cannot consume an entire hillside.
    group=json.loads(Path(__file__).with_name("mapped_group.json").read_bytes())
    trace=np.array(path["points"][:47]);segments=trace[1:]-trace[:-1]
    for feature in group["buildings"]:
        ring=np.array(feature["points"])
        for a,b in zip(ring,np.roll(ring,-1,axis=0)):
            if np.linalg.norm(b-a)<10:continue
            for pt in np.linspace(a,b,max(3,int(np.linalg.norm(b-a))+1)):
                t=np.clip(np.sum((pt-trace[:-1])*segments,axis=1)/np.sum(segments*segments,axis=1),0,1)
                nearest=trace[:-1]+t[:,None]*segments
                p=nearest[np.argmin(np.linalg.norm(nearest-pt,axis=1))]
                if np.linalg.norm(p-pt)>12.0:continue
                lo=np.minimum(p,pt)-1.5;hi=np.maximum(p,pt)+1.5
                xs=np.flatnonzero((mx[0]>=lo[0])&(mx[0]<=hi[0]));ys=np.flatnonzero((my[:,0]>=lo[1])&(my[:,0]<=hi[1]))
                if not len(xs) or not len(ys):continue
                sl=np.s_[ys[0]:ys[-1]+1,xs[0]:xs[-1]+1]
                x=mx[sl];y=my[sl];dx,dy=p-pt
                f=np.clip(((x-pt[0])*dx+(y-pt[1])*dy)/max(.001,dx*dx+dy*dy),0,1)
                ground[sl]=np.maximum(ground[sl],np.clip((1.3-np.hypot(x-pt[0]-f*dx,y-pt[1]-f*dy))*2,0,1))
    sl,dist=boundary_field(controls["park"]["boundary"],.5)
    ground[sl]*=np.clip(dist*2.,0,1)
    strip=np.maximum(strip,ground)
    greens_before=rgba[:,:,1].copy()
    rgba[:,:,1]=np.maximum(greens_before,strip*outer)
    return {"way":path["id"],"survey_vertex_range":[0,46],"designed_half_width_m":1.65,
        "new_paving_m2":round(float(np.maximum(0,rgba[:,:,1]-greens_before).sum())*(500/mx.shape[1])**2,1)}
