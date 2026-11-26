"""Register OSM road crossings and building evidence against the trial plots."""
import argparse
import hashlib
import json
from math import cos, sin
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from shapely.geometry import LineString, Point, Polygon

HERE = Path(__file__).resolve().parent
SCENES = HERE.parents[1]
sys.path.insert(0, str(SCENES / "street_blocks"))
from source_ground import registration

SOURCE = "https://api.openstreetmap.org/api/0.6/map?bbox=106.56130,29.55067,106.56756,29.55576"
REQUESTED_SHA256 = "8e5c2d8882c918460a8139b3fe4a6a75602905f5aef7de85b74ed61ccf4ab4a0"
ROADS = {2: [1256859184], 11: [59146751, 1017606351], 23: [59146654],
         37: [59146654], 39: [59146654], 55: [59146737], 62: [59146737],
         66: [1256859184, 1324001436, 1375242613], 77: [1306489251]}
BUILDINGS = {28: [704006706], 29: [704006706], 70: [1128648941],
             74: [1374780311, 1374780313], 75: [1374780311, 1374780314],
             76: [1374780311, 1374780314]}
WALK_LINES = [59146654, 1513362409, 1025797976, 1025797980, 1025797982,
              176034707, 176034697, 1189963552]


def outline(plot):
    x, y = plot["east_north"]
    a = plot["bearing"]
    w, d = plot["width"] / 2, plot["depth"] / 2
    return Polygon([(x + cos(a)*u - sin(a)*v, y + sin(a)*u + cos(a)*v)
                    for u, v in [(-w, -d), (w, -d), (w, d), (-w, d)]])


def stations(line, count):
    return [[round(point.x, 4), round(point.y, 4)]
            for point in (line.interpolate(i/(count-1), normalized=True) for i in range(count))]


def register(osm_path):
    source = osm_path.read_bytes()
    osm = ET.fromstring(source)
    nodes = {n.attrib["id"]: [float(n.attrib["lon"]), float(n.attrib["lat"])]
             for n in osm.findall("node")}
    local, _ = registration()
    wanted = {way for group in (*ROADS.values(), *BUILDINGS.values(), WALK_LINES) for way in group}
    ways = {}
    for w in osm.findall("way"):
        wid = int(w.attrib["id"])
        if wid not in wanted:
            continue
        refs = [n.attrib["ref"] for n in w.findall("nd")]
        ways[wid] = {"version": int(w.attrib["version"]), "osm_nodes": refs,
                     "tags": {t.attrib["k"]: t.attrib["v"] for t in w.findall("tag")},
                     "east_north": local([nodes[n] for n in refs])}
    missing = wanted - ways.keys()
    if missing:
        raise ValueError(f"OSM ways missing from the supplied map: {sorted(missing)}")
    layout = SCENES.parent / "project/chongqing_godot_v05/assets/district_500/layout.json"
    findings = []
    for p in json.loads(layout.read_bytes())["plots"]:
        pid = p["plot_id"]
        if pid not in ROADS and pid not in BUILDINGS:
            continue
        poly = outline(p)
        centre = Point(p["east_north"])
        roads = []
        buildings = []
        for wid in ROADS.get(pid, []):
            line = LineString(ways[wid]["east_north"])
            hit = poly.intersection(line)
            parts = [hit] if hit.geom_type == "LineString" else list(getattr(hit, "geoms", ()))
            roads.append({"way": wid, "centre_distance_m": round(centre.distance(line), 3),
                          "crossing_m": round(hit.length, 3),
                          "east_north": [point for part in parts if part.length for point in stations(part, 5)]})
        for wid in BUILDINGS.get(pid, []):
            ring = Polygon(ways[wid]["east_north"])
            corners = list(ring.exterior.coords)
            sides = [LineString([a, b]) for a, b in zip(corners, corners[1:])]
            buildings.append({"way": wid, "overlap_m2": round(poly.intersection(ring).area, 3),
                              "centre_in_outline": ring.covers(centre),
                              "centre_distance_m": round(centre.distance(ring), 3),
                              "side_stations_east_north": [stations(side, 4) for side in sides] if wid == 704006706 else []})
        findings.append({"plot": pid, "centre_east_north": p["east_north"],
                         "existing_floor_m": round(p["height"], 3), "existing_roof_m": round(p["roof"], 3),
                         "roads": roads, "buildings": buildings})
    return {"source": SOURCE, "source_bytes": len(source), "source_sha256": hashlib.sha256(source).hexdigest(),
            "comparison_source_sha256": REQUESTED_SHA256, "project_registration_way": 734116601,
            "attribution": "© OpenStreetMap contributors, ODbL 1.0", "ways": ways, "plots": findings}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("osm", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(register(args.osm), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
