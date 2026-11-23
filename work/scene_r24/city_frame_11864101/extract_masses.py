"""Extract low-detail building envelopes from transformed source vertices without importing textures."""
from pathlib import Path
import sys, os, json, numpy as np
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/"chaotianmen_9644040"))
from study_mesh import rows, geom, xform, STUDY
source="white" if here==STUDY else "river"
reg=json.loads((here/"registration.json").read_bytes())
r=reg["new_to_old_native_metres"]; mult=complex(*r["multiplier"]); offset=complex(*r["offset"])
def eastnorth(lon,lat):
    from math import radians,sin,cos,sqrt
    def ecef(l,b):
        l,b=radians(l),radians(b)
        n=6378137/sqrt(1-.00669437999014*sin(b)**2)
        return np.array([n*cos(b)*cos(l),n*cos(b)*sin(l),n*(1-.00669437999014)*sin(b)])
    l,b=map(radians,[106.56445,29.55325])
    v=ecef(lon,lat)-ecef(106.56445,29.55325)
    return complex(v@[-sin(l),cos(l),0],v@[-sin(b)*cos(l),-sin(b)*sin(l),cos(b)])
def control(num,tip=False):
    nds=[n for n in json.loads((here/f"osm_way_{num}.json").read_bytes())["elements"] if n["type"]=="node"]
    if tip:
        n=max(nds,key=lambda n:n["lat"])
        return eastnorth(n["lon"],n["lat"])
    return sum(eastnorth(n["lon"],n["lat"]) for n in nds)/len(nds)
monument=7866-552j
tip=8934+625j
m=(control(230583762,True)-control(589752618))/(tip-monument)
t=control(589752618)-m*monument
ids={r[0]:r for r in rows}
angles=np.arange(16)*np.pi/8
dirs=np.stack((np.cos(angles),np.sin(angles)))
def outline(xy):
    pts=xy[np.unique(np.argmax(xy@dirs,axis=0))]
    center=pts.mean(0)
    pts=pts[np.argsort(np.arctan2(pts[:,1]-center[1],pts[:,0]-center[0]))]
    return pts.round(2).tolist()
result=[]
for nid,meshidx,nv,nf,mid,lo,hi in json.loads((STUDY/"bounds.json").read_bytes()):
    factor=.01 if source=="river" else abs(mult)
    span=(np.array(hi)-lo)*factor
    if not (19<span[2]<415 and 7<min(span[:2]) and max(span[:2])<145 and max(span[:2])/min(span[:2])<5.0):continue
    A=xform(ids[nid]);v=geom(meshidx)[0]@A[:3,:3].T+A[:3,3]
    q=v[:,0]+1j*v[:,1]
    if source=="white":
        old=(q.conjugate() if r["conjugate"] else q)*mult+offset
        h=v[:,2]*abs(mult)+r["vertical_offset"]
    else:
        old=q*.01;h=v[:,2]*.01
    center=old.mean()
    world=old*m+t
    if not (350<abs(world.mean())<3500):continue
    near_line=min(abs(center-complex(*p["old_m"][:2])) for p in reg["pairs"])
    if source=="white" and near_line>340:continue
    xy=np.c_[world.real,world.imag]; ht=h.max()-h.min()
    lower=outline(xy)
    area=.5*abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(lower,lower[1:]+lower[:1])))
    if area<65 or len(lower)<3:continue
    crown=outline(xy[h>=h.min()+ht*.76])
    result.append(dict(src=source,node=nid,hull=lower,crown=crown,bottom=round(h.min()-183,2),top=round(h.max()-183,2),area=round(area,2),control_distance=round(near_line,1)))
(here/f"mass_{source}.json").write_text(json.dumps(result,separators=(",",":")),encoding="utf8")
(here/"world_transform.json").write_text(json.dumps(dict(old_m_to_EN=dict(multiplier=[m.real,m.imag],offset=[t.real,t.imag]),monument_old=[7866,-552],tip_old=[8934,625],origin=[106.56445,29.55325],vertical_datum_note="Old MAX river surface approximately 167, existing game water -16"),indent=2),encoding="utf8")
print("EXTRACTED",source,len(result))

