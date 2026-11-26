"""Register the local Overture download and original OSM map in game metres."""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def registration():
    osm = ET.parse(ROOT / "work/assets_incoming/r22_city/osm_southwest.osm")
    nodes = {n.get("id"): [float(n.get("lon")), float(n.get("lat"))] for n in osm.findall("node")}

    def way(wid):
        return [nodes[n.get("ref")] for n in osm.find(f".//way[@id='{wid}']").findall("nd")]

    geo_path = ROOT / "work/project/chongqing_godot_v05/source_data/geo_layout.json"
    geo = json.loads(geo_path.read_bytes())
    control = np.array(way(734116601))
    en = np.array(next(s["points"] for s in geo["paths"] if s["id"] == 734116601))
    origin = control.mean(axis=0)

    def matrix(pts):
        return np.column_stack((np.array(pts) - origin, np.ones(len(pts))))

    transform = np.linalg.lstsq(matrix(control), en, rcond=None)[0]

    def local(pts):
        return np.round(matrix(pts) @ transform, 4).tolist()

    return local, way


def osm_frontages(features, local):
    records = []
    for feature in features:
        source = feature["properties"]["sources"][0]
        if source["dataset"] != "OpenStreetMap":
            continue
        rings = feature["geometry"]["coordinates"]
        records.append({"osm": source["record_id"], "gers": feature["id"],
                        "source_storeys": feature["properties"].get("num_floors"),
                        "rings": [local(r) for r in rings]})
    return records


def main():
    group = json.loads((HERE / "mapped_group.json").read_bytes())
    download = Path(sys.argv[1]).read_bytes()
    assert hashlib.sha256(download).hexdigest() == group["query_sha256"]
    local, way = registration()
    records = osm_frontages(json.loads(download)["features"], local)
    result = {"source": "mapped_group.json", "license": "ODbL-1.0, © OpenStreetMap contributors via Overture Maps",
              "frontages": records, "park": {"osm": 1499726225, "name": "滨江公园",
                                             "boundary": local(way(1499726225))}}
    (HERE / "frontage_controls.json").write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
