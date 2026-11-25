"""Use the local Overture download and original OSM map to register street-front ground controls."""
import hashlib,json,sys
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np

here=Path(__file__).resolve().parent
root=here.parents[2]
source=here/"mapped_group.json"
group=json.loads(source.read_bytes())
download=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(download).hexdigest()==group["query_sha256"]
osm=ET.parse(root/"work/assets_incoming/r22_city/osm_southwest.osm")
nodes={n.get("id"):[float(n.get("lon")),float(n.get("lat"))] for n in osm.findall("node")}
def way(wid):
    return [nodes[n.get("ref")] for n in osm.find(f".//way[@id='{wid}']").findall("nd")]
geo=json.loads((root/"work/project/chongqing_godot_v05/source_data/geo_layout.json").read_bytes())
control=np.array(way(734116601))
en=np.array(next(s["points"] for s in geo["paths"] if s["id"]==734116601))
origin=control.mean(axis=0)
def matrix(pts):return np.column_stack((np.array(pts)-origin,np.ones(len(pts))))
transform=np.linalg.lstsq(matrix(control),en,rcond=None)[0]
def local(pts):return np.round(matrix(pts)@transform,4).tolist()
records=[]
for f in json.loads(download)["features"]:
    src=f["properties"]["sources"][0]
    if src["dataset"]!="OpenStreetMap":continue
    rings=f["geometry"]["coordinates"]
    records.append({"osm":src["record_id"],"gers":f["id"],"rings":[local(p) for p in rings]})
result={"source":"mapped_group.json","license":"ODbL-1.0, © OpenStreetMap contributors via Overture Maps",
        "frontages":records,"park":{"osm":1499726225,"name":"滨江公园","boundary":local(way(1499726225))}}
(here/"frontage_controls.json").write_text(json.dumps(result,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
