"""District road reservations and entrances in Blender east/north metres."""
from math import cos, sin
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
ASSETS=ROOT/"work/project/chongqing_godot_v05/assets/district_500"
def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def roads(layout):
    osm=read(ASSETS.parents[1]/"source_data/geo_layout.json")
    lines=[(item["points"],3.15 if item["id"] in (49182408,1189963598,734116597,1513362409) else 4.25,str(item["id"])) for item in osm["roads"] if item["id"] in layout["osm_road_ids"]]
    lines.extend((pts,2.7 if key in ("promenade","south_link","north_link") else 4.2,key) for key,pts in layout["inferred_alignments"].items())
    return [(a,b,w,k) for pts,w,k in lines for a,b in zip(pts,pts[1:]) if a!=b]
class Streets:
    def __init__(self,segments):
        self.starts=np.array([a for a,b,w,k in segments])
        self.axis=np.array([b for a,b,w,k in segments])-self.starts
        self.sq=np.sum(self.axis*self.axis,axis=1)
        self.width=np.array([w for a,b,w,k in segments])
        self.ids=[k for a,b,w,k in segments]
    def margin(self,points):
        d=np.asarray(points)[:,None,:]-self.starts
        t=np.clip(np.sum(d*self.axis,axis=2)/self.sq,0,1)
        out=np.linalg.norm(d-t[:,:,None]*self.axis,axis=2)-self.width
        return out.min(axis=1)
def xy(p,u,v):
    c,s=cos(p["bearing"]),sin(p["bearing"]); x,y=p["east_north"]
    return [x+c*u-s*v,y+s*u+c*v]
def rectangle(p,u0,v0,u1,v1,spacing=.23):
    us=np.linspace(u0,u1,max(2,int(abs(u1-u0)/spacing)+2))
    vs=np.linspace(v0,v1,max(2,int(abs(v1-v0)/spacing)+2))
    return [xy(p,u,v) for u in us for v in vs]
def footprints(p):
    for direction,title in ((-1,"front"),(1,"back")):
        edge=direction*p["depth"]/2
        if direction==-1 and p["name"]:continue
        if direction==1 and p.get("court"):continue
        turned=p.get("kerb_stairs",{}).get(title)
        if turned:
            mid=p["door_u"];end=mid+turned["direction"]*(.97+.31*turned["steps"])
            yield title,rectangle(p,min(mid-.97,end),edge,max(mid+.97,end),edge+direction*turned["width_m"],.09)
            continue
        run=p[title+"_stair_m"]
        yield title,rectangle(p,p["door_u"]-1.25,edge,p["door_u"]+1.25,edge+direction*run)
if __name__=="__main__":
    layout=read(ASSETS/"layout.json")
    reserve=Streets(roads(layout))
    audit=[]
    for p in layout["plots"]:
        for name,points in footprints(p):
            closest=float(reserve.margin(points).min())
            audit.append({"plot":p["plot_id"],"end":name,"clearance_m":round(closest,3)})
    import sys
    Path(sys.argv[1]).write_text(json.dumps(audit,indent=2),encoding="utf-8")
    print([v for v in audit if v["clearance_m"]<.50])
