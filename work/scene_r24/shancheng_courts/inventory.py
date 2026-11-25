"""Measure the original 75 sites against both delivery routes using the old wall polygons."""
from pathlib import Path
from math import cos,sin
import json
import numpy as np

here=Path(__file__).resolve().parent
game=here.parents[2]/"work/project/chongqing_godot_v05"
old=json.loads((here.parent/"street_blocks/legacy_sites.json").read_bytes())
batch=json.loads((here/"registered.json").read_bytes())
walks=json.loads((game/"assets/district_500/shancheng_lane.json").read_bytes())
current=json.loads((game/"assets/district_500/layout.json").read_bytes())
actual={x["plot_id"] for x in current["plots"]}
ways=[np.array(walks[k])[:,:2] for k in ("primary","branch")]
def point_segment(p,a,b):
    delta=b-a
    t=np.clip(np.dot(p-a,delta)/np.dot(delta,delta),0.,1.)
    return float(np.linalg.norm(p-a-t*delta))
def distance(a,b,c,d):
    def cross(v,w):return v[0]*w[1]-v[1]*w[0]
    denominator=cross(b-a,d-c)
    if abs(denominator)>1e-8:
        s=cross(c-a,d-c)/denominator
        t=cross(c-a,b-a)/denominator
        if 0<=s<=1 and 0<=t<=1:return 0.
    return min(point_segment(a,c,d),point_segment(b,c,d),point_segment(c,a,b),point_segment(d,a,b))
rows=[]
for key,(center,ang,width,depth) in old.items():
    if key=="32":continue
    tr=np.array([[cos(ang),sin(ang)],[-sin(ang),cos(ang)]])
    ring=np.array([[-width,-depth],[width,-depth],[width,depth],[-width,depth]])/2@tr+center
    near=min(distance(a,b,c,d) for a,b in zip(ring,np.roll(ring,-1,axis=0)) for path in ways for c,d in zip(path,path[1:]))
    rows.append({"legacy_plot":int(key),"center_en":center,"wall_to_delivery_centreline_m":round(near,2),
                 "state":"withdrawn" if key in batch["retired"] else "pending",
                 "observation":batch["retired"].get(key)})
assert len(rows)==75 and actual=={r["legacy_plot"] for r in rows if r["state"]=="pending"}
rows.sort(key=lambda r:r["wall_to_delivery_centreline_m"])
(here/"evidence/inventory.json").write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8")
