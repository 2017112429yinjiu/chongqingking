"""Summarize a single completed native survey; keep every underlying trial intact."""
import json
import sys
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


run = Path(sys.argv[1])
ground = read(run / 'ground/district.json')
surface_ids = {i for i, route in enumerate(ground['routes']) if not route['tunnel']}
patrol = read(run / 'ride/patrol.json')
mentor_legs = [leg for route in patrol for leg in route['legs']]
players = {}
for direction in ('out', 'back'):
    legs = [leg for part in range(3) for leg in read(run / f'player_{direction}_{part}/drives.json')]
    assert {row['id'] for row in legs} == surface_ids and all(row['state'] == 'passed' for row in legs)
    players[direction] = len(legs)
assert len(mentor_legs) == 28 and all(leg['completed'] for leg in mentor_legs)

detail = read(run / 'junction_profiles/corner.json')['checks']
assert all(check['pass'] for check in detail)
gates = [c['detail'] for c in detail if c['name'].startswith('full_width_')]
north = read(run / 'north/north.json')
assert all(c['pass'] for c in north['checks'])
surface_counts = {key: len(ground[key]) for key in ('sections', 'grid')}
short_misses = sum(row[-2] is None for key in surface_counts for row in ground[key])
assert short_misses == len(north['measurements'])
report = {
    'source_and_export': read(Path(__file__).resolve().parents[1] / 'reopened.json'),
    'mentor_routes': len(patrol), 'mentor_legs': len(mentor_legs),
    'mentor_distance_m': round(sum(leg['metres'] for leg in mentor_legs), 2),
    'player_surface_routes_completed': players, 'historical_underground_alignments_excluded': len(ground['routes'])-len(surface_ids),
    'walk_return_trips_at_six_junctions': sum(c['name'].startswith('both_directions_') for c in detail),
    'additional_street_entry_return_trips': sum(c['name'].startswith('mentor_both_ways_') for c in detail),
    'inner_surface_points': sum(c['detail']['points'] for c in detail if c['name'].startswith('turn_interior_')),
    'gate_cross_sections': sum(g['samples'] for g in gates), 'max_gate_error_m': max(g['max_error'] for g in gates),
    'east_stair_edge_points': next(c['detail']['points'] for c in detail if c['name']=='east_stair_outer_edge'),
    'district_probes': surface_counts, 'old_height_misses_rechecked': short_misses,
    'north_edge_max_difference_m_over_13cm': max(north['edge_differences_m']),
    'native_scene': 'first_shift.tscn', 'engine': ground['engine']
}
(run / 'survey_summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
