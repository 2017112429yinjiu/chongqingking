"""Digitized roof eaves on the published district plan, using the existing local registration."""
from pathlib import Path
import json
import numpy as np

here = Path(__file__).resolve().parent
controls = json.loads((here.parent / "shancheng_courts/registered.json").read_bytes())["buildings"]
pixels = np.concatenate([b["plan_pixels"] for b in controls])
points = np.concatenate([b["points"] for b in controls])
affine = np.linalg.lstsq(np.column_stack([pixels, np.ones(len(pixels))]), points, rcond=None)[0]
rings = {
    "front_west": [[350.7,420.7],[376.8,438.6],[387.6,422.4],[363.1,405.7]],
    "front_east": [[376.8,438.6],[411.8,459.7],[422,442],[387.6,422.4]],
    "upper": [[381,390],[419,412],[425,405],[386,382]],
    "west_return": [[374,407],[381,411],[391,392],[383,388]],
    "east_return": [[408,423],[416,425],[427,406],[419,402]],
}
def project(ring):
    return np.column_stack([ring, np.ones(len(ring))]) @ affine
rows = {k: {"plan_pixels": v, "en": project(v).round(4).tolist()} for k,v in rings.items()}
left, right = project(rings["front_west"]), project(rings["front_east"])
axis = right[1]-left[0]
width = np.linalg.norm(axis)
axis /= width
normal = np.array([-axis[1],axis[0]])
depth = np.mean([(left[3]-left[0])@normal,(right[2]-right[1])@normal])
center = (right[1]+left[0])/2 + normal*depth/2
geo = json.loads((here.parents[2]/"work/project/chongqing_godot_v05/source_data/geo_layout.json").read_bytes())
way = np.array(next(w["points"] for w in geo["paths"] if w["id"]==734116598))
def nearest(point):
    a,b=way[:-1],way[1:]
    v=b-a
    t=np.clip(((point-a)*v).sum(axis=1)/(v*v).sum(axis=1),0,1)
    q=a+t[:,None]*v
    return q[np.argmin(np.linalg.norm(q-point,axis=1))]
street = nearest(center-normal*depth/2)
site = dict(legacy_plot=0,roof_rings=rows,center=center.round(4).tolist(),
            width=round(width,4),depth=round(depth,4),bearing=float(np.arctan2(axis[1],axis[0])),
            tree_en=project([[401,414]])[0].round(4).tolist(),
            boardwalk_en=way[(np.linalg.norm(way-street,axis=1)<50)].round(4).tolist(),
            street_en=street.round(4).tolist(),street_way=734116598,
            court_en=project([[400,408]])[0].round(4).tolist(),
            plan_sha256="44f8f50e7905a800477aae5e1bd7eaa71ee1e8544c3197433a86083dbc9c79b0")
(here/"site.json").write_text(json.dumps(site,indent=2)+"\n",encoding="utf-8")
