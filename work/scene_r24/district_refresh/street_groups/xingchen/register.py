"""Project Xingchen's open outline and two carriageways into production metres."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from xml.etree import ElementTree

from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from register import SOURCE, outline, registration

WAYS = (704006725, 830761786, 49182416)
PINS = [
    ("星辰花园", "d52831f909be0ea72efaa73c", (188.0, -158.0)),
    ("星辰花园-16栋", "40e009d0ca5107ccd6b74e00", (186.9, -156.5)),
]


def register(path):
    source = path.read_bytes()
    osm = ElementTree.fromstring(source)
    nodes = {node.get('id'): (float(node.get('lon')), float(node.get('lat'))) for node in osm.findall('node')}
    project, _ = registration()
    ways = {}
    for way in osm.findall('way'):
        wid = int(way.get('id'))
        if wid not in WAYS:
            continue
        points = project([nodes[node.get('ref')] for node in way.findall('nd')])
        feature = orient(Polygon(points), sign=1) if wid == WAYS[0] else LineString(points)
        assert feature.is_valid
        ways[wid] = {
            "tags": {tag.get("k"): tag.get("v") for tag in way.findall("tag")},
            "east_north": list(feature.exterior.coords)[:-1] if wid == WAYS[0] else list(feature.coords),
        }
    assert ways.keys() == set(WAYS)
    buildings = Polygon(ways[WAYS[0]]["east_north"])
    layout = HERE.parents[4] / 'work/project/chongqing_godot_v05/assets/district_500/layout.json'
    plot = next(plot for plot in json.loads(layout.read_bytes())["plots"] if plot["plot_id"] == 27)
    centre = Point(plot["east_north"])
    return {
        "osm_source": SOURCE,
        "osm_bytes": len(source),
        "osm_sha256": hashlib.sha256(source).hexdigest(),
        "attribution": "© OpenStreetMap contributors, ODbL 1.0",
        "projection_way": 734116601,
        "ways": ways,
        "old_plot": {"id": 27, "centre_east_north": plot["east_north"],
                     "overlap_m2": round(outline(plot).intersection(buildings).area, 3),
                     "centre_to_footprint_m": round(centre.distance(buildings), 3)},
        "map_pins": [{"name": name, "uid": uid, "approx_east_north_m": en,
                      "covered": buildings.covers(Point(en)),
                      "centre_distance_m": round(centre.distance(Point(en)), 3)} for name, uid, en in PINS],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('osm', type=Path)
    args = parser.parse_args()
    (HERE / 'registration.json').write_text(
        json.dumps(register(args.osm), ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
