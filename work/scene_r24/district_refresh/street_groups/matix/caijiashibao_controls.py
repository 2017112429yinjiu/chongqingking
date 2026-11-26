"""Register nearby OSM footprints without assigning their buildings from POIs."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from xml.etree import ElementTree

from shapely.geometry import Point, Polygon

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from register import outline, registration

SOURCE = 'https://api.openstreetmap.org/api/0.6/map?bbox=106.56130,29.55067,106.56756,29.55576'
WAYS = ('809889603', '809889604', '809889631', '809889635')
# The oblique gate photo records an exposure location and has no GPS datum tag.
OBLIQUE_CAMERA_LON_LAT = (106 + 33 / 60 + 55.1304 / 3600, 29 + 33 / 60 + 17.71559 / 3600)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('osm', type=Path)
    cli.add_argument('output', type=Path)
    args = cli.parse_args()
    raw = args.osm.read_bytes()
    root = ElementTree.fromstring(raw)
    nodes = {node.get('id'): (float(node.get('lon')), float(node.get('lat'))) for node in root.findall('node')}
    local, _ = registration()
    ways = {}
    tags = {}
    for way in root.findall('way'):
        way_id = way.get('id')
        if way_id in WAYS:
            coords = local([nodes[item.get('ref')] for item in way.findall('nd')])
            ways[way_id] = Polygon(coords)
            tags[way_id] = {item.get("k"): item.get("v") for item in way.findall("tag")}
    assert ways.keys() == set(WAYS) and all(p.is_valid for p in ways.values())
    layout_path = HERE.parents[4] / 'work/project/chongqing_godot_v05/assets/district_500/layout.json'
    layouts = json.loads(layout_path.read_bytes())['plots']
    camera = Point(local([OBLIQUE_CAMERA_LON_LAT])[0])
    outer = ways['809889635']
    result = {
        'osm_source': SOURCE,
        'osm_sha256': sha256(raw).hexdigest(),
        'attribution': '© OpenStreetMap contributors, ODbL 1.0',
        'projection_control_way': 734116601,
        'oblique_photo_camera': {'east_north': [camera.x, camera.y], 'datum_tag': None,
                                 'distance_to_way_boundary_m': {i: round(camera.distance(ways[i].boundary), 3) for i in WAYS}},
        'way_809889635': {'area_m2': round(outer.area, 3), 'bounds_east_north': outer.bounds, 'tags': tags['809889635']},
        'plots': [{'id': p['plot_id'], 'overlap_with_809889635_m2': round(outline(p).intersection(outer).area, 3),
                   'centre_distance_to_809889635_m': round(Point(p['east_north']).distance(outer), 3),
                   'camera_distance_to_plot_centre_m': round(camera.distance(Point(p['east_north'])), 3)}
                  for p in layouts if p['plot_id'] in (41, 42, 43)],
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
