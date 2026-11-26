"""Review registered Overture footprints without inferring a building's use or grade."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

from shapely import Polygon, make_valid
from shapely.strtree import STRtree

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "street_blocks"
sys.path[:0] = [str(TOOLS), str(HERE.parent)]
from source_ground import osm_frontages, registration


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("geojson", type=Path)
    cli.add_argument("output", type=Path)
    args = cli.parse_args()
    raw = args.geojson.read_bytes()
    group = json.loads((TOOLS / "mapped_group.json").read_bytes())
    features = json.loads(raw)["features"]
    local, _ = registration()
    donor = json.loads((TOOLS / "frontage_controls.json").read_bytes())["frontages"]
    expected = {r["gers"]: r for r in donor}
    registered = {r["gers"]: r for r in osm_frontages(features, local)}
    assert registered == expected, "Overture OSM controls differ from the registered project inputs."
    shapes, metadata = [], []
    for feature in features:
        source = feature["properties"]["sources"][0]
        geom = feature["geometry"]
        assert geom["type"] == "Polygon", geom["type"]
        shell, *holes = (local(ring) for ring in geom["coordinates"])
        shapes.append(make_valid(Polygon(shell, holes)))
        metadata.append({"gers": feature["id"], "dataset": source["dataset"], "license": source["license"],
                         "source_record_id": source["record_id"],
                         "mapped_storeys": feature["properties"].get("num_floors")})
    index = STRtree(shapes)
    offsets = json.loads((HERE.parent / "evidence/plot-sources.json").read_bytes())
    records = []
    for plot in offsets["plots"]:
        working = Polygon(plot["footprint"])
        matches = []
        for candidate in index.query(working, predicate="intersects"):
            overlap = working.intersection(shapes[candidate]).area
            if overlap < .001:
                continue
            proportion = overlap / (working.area + shapes[candidate].area - overlap)
            matches.append({**metadata[candidate], "overlap_m2": round(overlap, 3),
                            "intersection_over_union": round(proportion, 5)})
        records.append({"id": plot["id"], "cell": plot["sector"],
                        "matches": sorted(matches, key=lambda match: -match["intersection_over_union"])})
    inputs = {"release": group["release"], "bbox": group["bounds"],
              "input_sha256": hashlib.sha256(raw).hexdigest(), "prior_cli_sha256": group["query_sha256"],
              "exact_osm_control_matches": len(expected),
              "source_feature_counts": Counter(x["dataset"] for x in metadata)}
    args.output.write_text(json.dumps({"input": inputs, "plots": records}, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")


if __name__ == "__main__":
    main()
