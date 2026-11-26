"""Register the Guoco, Zhongxing and Caijiashibao controls in project metres."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from xml.etree import ElementTree

from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from register import outline, registration

WAYS = (1374780311, 1374780313, 1374780314, 1374780315, 1374780309,
        704006706, 809889619, 809889620, 809889631, 809889613, 176034707, 59146751, 1017606351)
LINES = {809889613, 176034707, 59146751, 1017606351}
PLOTS = (8, 9, 11, 28, 29, 43, 44, 74, 75, 76)


def run(source, output):
    data = source.read_bytes()
    root = ElementTree.fromstring(data)
    nodes = {int(node.get('id')): (float(node.get('lon')), float(node.get('lat'))) for node in root.findall('node')}
    project, _ = registration()
    project_extent = box(-250, -250, 250, 250)
    ways, shapes = {}, {}
    for element in root.findall('way'):
        way = int(element.get('id'))
        if way not in WAYS:
            continue
        coords = project([nodes[int(item.get('ref'))] for item in element.findall('nd')])
        feature = LineString(coords) if way in LINES else orient(Polygon(coords), sign=1.)
        assert feature.is_valid, way
        ways[way] = {'tags': {tag.get('k'): tag.get('v') for tag in element.findall('tag')},
                     'bounds_east_north': feature.bounds,
                     'outside_area_m2': round(feature.difference(project_extent).area, 4),
                     'east_north': list(feature.coords) if way in LINES else list(feature.exterior.coords)[:-1]}
        shapes[way] = feature
    assert ways.keys() == set(WAYS)
    layout = json.loads((HERE.parents[4] / 'work/project/chongqing_godot_v05/assets/district_500/layout.json').read_bytes())
    plots = {}
    for plan in layout['plots']:
        plot = plan['plot_id']
        if plot not in PLOTS:
            continue
        poly = outline(plan)
        plots[plot] = {'center_east_north': plan['east_north'], 'intersections': {
            way: round(poly.intersection(shape).length if way in LINES else poly.intersection(shape).area, 4)
            for way, shape in shapes.items() if poly.intersects(shape)}}
    school_pin = project([(106.565332, 29.554874)])[0]
    result = {
        'osm_sha256': sha256(data).hexdigest(), 'projection_way': 734116601,
        'attribution': '© OpenStreetMap contributors, ODbL 1.0', 'ways': ways, 'plots': plots,
        'zhongxing_bus': {'node': 11049229719, 'east_north': project([nodes[11049229719]])[0]},
        'xinglin_gate': {'approximate_east_north': school_pin,
                         'distance_to_way_809889631_m': round(Point(school_pin).distance(shapes[809889631].boundary), 4),
                         'distance_to_trial_43_centre_m': round(Point(school_pin).distance(Point(plots[43]['center_east_north'])),4)},
    }
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('osm', type=Path)
    cli.add_argument('output', type=Path)
    args = cli.parse_args()
    run(args.osm, args.output)
