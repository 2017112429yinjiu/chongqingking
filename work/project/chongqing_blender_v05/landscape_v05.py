"""Authored urban ground and planting for the fifth district review.

The exterior terrain remains at the established height.  After architecture
is built, its actual room shells recess the hidden terrain below their floors.
Soil, tree wells and gravel are an explicit plan shared by the terrain and the
plant placement, rather than foliage being scattered over an unrelated floor.
This module can be imported without Blender for layout and clearance audits.
"""
from collections import defaultdict
from pathlib import Path
from functools import lru_cache
import json
import math
import random

from district_layout import (DATA, SUPPLEMENTAL, ground_height, raw_height,
                             distance_segment, line_distance, point_in_poly,
                             road_width, clip_line)

ROOT = Path(__file__).resolve().parent
_LAYOUT = None
_ARCH = None
_TERRAIN = None
_CONTEXT = None
REPORT = {}

INFILL = [(-33, -73, -20, -62), (-70, -54, -55, -42),
          (-94, -31, -78, -9), (-66, -30, -53, -9),
          (-46, -49, -28, -28), (-11, -49, 4, -32), (4, 8, 23, 17)]

# The three resident courts are already enclosed by urban_fabric.  Their beds
# are deliberately against the inside boundary, with the west gates left open.
COURTS = [(-12.5, -31., .8, -3., (-20., -16.)),
          (44., 31., 60., 44., (35., 38.)),
          (18., -64., 32., -53., (-60., -57.))]

BED_SPECS = [
    ('central_lower_west', [(-24.1, -48.6), (-22.7, -48.6), (-22.7, -45.4), (-24.1, -45.4)]),
    ('central_upper_west', [(-24.0, -37.2), (-22.7, -37.2), (-22.7, -31.0), (-24.0, -31.0)]),
    ('central_upper_bank', [(-16.6, -29.0), (-14.8, -29.0), (-14.5, -26.0), (-15.8, -23.7), (-16.7, -24.6)]),
    ('central_court_north', [(-10.9, -6.2), (-.6, -6.2), (-.6, -3.65), (-10.9, -3.65)]),
    ('central_court_south', [(-10.85, -29.7), (-6.0, -29.7), (-6.5, -27.1), (-10.85, -26.8)]),
    ('east_gallery_root_bed', [(53.7, -48.8), (58.4, -49.0), (59.4, -47.0), (58.5, -43.1), (55.2, -42.7), (53.7, -44.6)]),
    ('east_court_south', [(45.0, 31.65), (53.4, 31.65), (53.4, 33.6), (46.7, 33.6), (46.7, 37.3), (44.75, 37.3), (44.75, 33.0)]),
    ('east_court_north', [(46.0, 41.2), (58.85, 41.2), (58.85, 43.25), (46.0, 43.25)]),
    ('south_court_garden', [(19.3, -55.7), (26.8, -55.7), (27.0, -58.7), (30.8, -58.7), (30.8, -53.65), (19.3, -53.65)]),
    ('upper_street_west_bed', [(1.5, 84.6), (16.4, 84.6), (16.4, 87.0), (1.5, 87.0)]),
    ('upper_street_middle_bed', [(24.0, 84.35), (38.0, 84.35), (38.0, 86.8), (24.0, 86.8)]),
    ('upper_street_east_bed', [(45.9, 84.3), (51.2, 84.3), (51.2, 86.7), (45.9, 86.7)]),
    ('west_house_corner', [(-91.5, -5.9), (-84.0, -5.6), (-83.4, -2.8), (-87.0, -2.5), (-91.5, -3.0)]),
    ('east_residential_margin', [(86.3, 42.3), (92.6, 42.1), (93.8, 47.9), (91.7, 51.5), (88.0, 50.0)]),
]

# Preserve the established shade trees, with the courtyard trees shifted clear
# of masonry boundaries and the service-house doorway kept open.  Three new
# northern trees belong to the long street-side beds, not the carriageway.
TREE_POINTS = [(-45., -57.), (-9.3, -23.9), (9., -52.), (33., -51.),
               (83., -33.), (85., -20.), (47.6, 36.0), (52., 49.),
               (-13., 69.), (78., 63.), (-77.83, -64.96), (21., -60.5),
               (29.0, -57.0), (-76.36, -44.79), (14.96, -48.49),
               (27.36, -48.41), (56.14, -44.68), (15.65, -33.14),
               (33.38, -15.68), (63.78, -19.54), (-87.41, -.77),
               (-61.01, -3.79), (-1.85, -4.91), (14.91, -4.74),
               (48.93, -4.84), (59.29, -4.8), (-91.98, 10.95),
               (33.78, 14.51), (41.58, 12.35), (16.16, 29.95),
               (42.53, 29.08), (88.35, 27.7), (-88.52, 43.84),
               (-60.1, 44.96), (.34, 42.92), (44.57, 45.84),
               (61.98, 40.61), (76.71, 44.48), (90., 41.5),
               (86.4, 59.79), (-26.36, 70.02), (8.2, 85.7),
               (30.3, 85.5), (48.6, 85.45)]

PAVING_ZONES = [
    ('central_shop_apron', (-25.1, -39.0), 5.3, 19.0, 0., 2.5, 'yard_concrete'),
    ('central_workshop_apron', (-14.6, -40.0), 5.8, 18.0, 0., 2.7, 'yard_concrete'),
    ('east_gallery_forecourt', (62.9, -39.0), 22.7, 6.8, -.472, 2.4, 'yard_concrete'),
    ('upper_north_apron', (23.0, 85.0), 58.0, 10.0, -.008, 3.0, 'yard_concrete'),
    ('central_resident_court', (-6.0, -17.0), 10.5, 25.0, 0., 2.4, 'yard_concrete'),
    ('east_resident_court', (52.0, 37.4), 14.0, 11.5, 0., 2.8, 'yard_concrete'),
    ('south_resident_court', (25.0, -58.5), 11.5, 9.6, 0., 2.5, 'yard_concrete'),
    ('community_forecourt', (-2.7, 12.7), 8.0, 11.0, -.15, 1.3, 'paving_slab'),
]


def polygon_distance(p, poly):
    d = min(distance_segment(p, a, b)[0] for a, b in zip(poly, poly[1:] + poly[:1]))
    return -d if point_in_poly(p, poly) else d


def _bounds(poly):
    return (min(p[0] for p in poly), min(p[1] for p in poly),
            max(p[0] for p in poly), max(p[1] for p in poly))


def _inside_bounds(p, bb, pad=0.):
    return bb[0] - pad <= p[0] <= bb[2] + pad and bb[1] - pad <= p[1] <= bb[3] + pad


def _outline_samples(poly, spacing=.45):
    for a, b in zip(poly, poly[1:] + poly[:1]):
        n = max(1, math.ceil(math.dist(a, b) / spacing))
        for k in range(n):
            t = k / n
            yield (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _source_buildings():
    polys = [b['points'] for b in DATA['buildings']]
    polys += [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)] for x0, y0, x1, y1 in INFILL]
    return [(p, _bounds(p)) for p in polys]


BUILDING_POLYS = _source_buildings()
ROUTE_SEGMENTS = []
for _item in DATA['roads'] + DATA['paths']:
    if _item['tags'].get('tunnel') == 'yes':
        continue
    for _pts in clip_line(_item['points']):
        for _a, _b in zip(_pts, _pts[1:]):
            ROUTE_SEGMENTS.append((_a, _b, road_width(_item) * .5, _item['type']))
for _name, _pts, _width in SUPPLEMENTAL:
    for _a, _b in zip(_pts, _pts[1:]):
        ROUTE_SEGMENTS.append((_a, _b, _width * .5, 'supplemental'))


def route_clearance(p):
    return min(distance_segment(p, a, b)[0] - half for a, b, half, _ in ROUTE_SEGMENTS)


def building_clearance(p):
    best = 100.
    for poly, bb in BUILDING_POLYS:
        if not _inside_bounds(p, bb, 8.):
            continue
        best = min(best, polygon_distance(p, poly))
    return best


def door_clearance(p, buildings=None):
    buildings = buildings if buildings is not None else (_ARCH or {}).get('buildings', [])
    best = 100.
    for rec in buildings:
        for e in rec.get('entrances', []):
            a = e['position'][:2]
            b = e['approach'][:2]
            # Extend the approach another two metres into the public apron.
            dx, dy = b[0] - a[0], b[1] - a[1]
            le = max(.001, math.hypot(dx, dy))
            c = (b[0] + 2.1 * dx / le, b[1] + 2.1 * dy / le)
            best = min(best, distance_segment(p, a, c)[0] - e.get('width_m', 2.2) * .5)
    return best


def _court_wall_clearance(p):
    best = 100.
    for x0, y0, x1, y1, gate in COURTS:
        poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for ei, (a, b) in enumerate(zip(poly, poly[1:] + poly[:1])):
            if ei == 3 and gate[0] < p[1] < gate[1]:
                continue
            best = min(best, distance_segment(p, a, b)[0] - .20)
    return best


def _static_free(p, clear=.6):
    return (-98 < p[0] < 98 and -76 < p[1] < 98
            and not (-50 < p[0] < -17 and -20 < p[1] < 19)
            and building_clearance(p) >= clear
            and route_clearance(p) >= clear
            and door_clearance(p) >= clear)


def prepare_layout():
    global _LAYOUT, _ARCH
    if _LAYOUT is not None:
        return _LAYOUT
    manifest = ROOT / 'architecture_manifest.json'
    if manifest.is_file():
        _ARCH = json.loads(manifest.read_text())
    beds = []
    omitted = []
    for name, poly in BED_SPECS:
        # No planted polygon can extend across a route or a front-door apron.
        samples = list(_outline_samples(poly))
        if all(_static_free(p, .45) for p in samples):
            beds.append({'name': name, 'poly': poly, 'bounds': _bounds(poly)})
        else:
            omitted.append(name)
    trees = []
    for i, p in enumerate(TREE_POINTS):
        r = 1.13 if i % 3 else 1.24
        boundary = [(p[0] + (r + .21) * math.cos(k * math.tau / 24),
                     p[1] + (r + .21) * math.sin(k * math.tau / 24)) for k in range(24)]
        if not all(_static_free(q, .5) and _court_wall_clearance(q) >= .06 for q in boundary):
            omitted.append('tree_%02d' % (i + 1))
            continue
        trees.append({'name': 'tree_%02d' % (i + 1), 'point': p, 'radius': r,
                      'seed': 8000 + (i + 1) * 19, 'height': 9.2 + ((i * 37) % 31) / 10.})
    _LAYOUT = {'beds': beds, 'trees': trees, 'omitted_for_clearance': omitted}
    REPORT.update({'layout_version': 5, 'terrain_extent_m': [200, 200],
                   'continuous_collision_terrain': True,
                   'ground_height_function_changed': False,
                   'beds': [{'name': b['name'], 'points': b['poly']} for b in beds],
                   'tree_wells': trees, 'omitted_for_clearance': omitted,
                   'plant_support_records': []})
    return _LAYOUT


def soil_distance(p):
    plan = prepare_layout()
    best = 20.
    for b in plan['beds']:
        if _inside_bounds(p, b['bounds'], 1.):
            best = min(best, polygon_distance(p, b['poly']))
    for t in plan['trees']:
        q = t['point']
        if abs(p[0] - q[0]) < t['radius'] + 1. and abs(p[1] - q[1]) < t['radius'] + 1.:
            best = min(best, math.dist(p, q) - t['radius'])
    return best


@lru_cache(maxsize=None)
def _terrain_vertex_height(x, y):
    # Twelve millimetres of bounded variation, always below the established
    # road/stair level.  This changes neither the grade nor route elevation.
    micro = .006 * math.sin(x * 1.7 + y * .47) * math.sin(y * 1.13)
    micro += .004 * math.sin(x * .56 - y * 1.83)
    return ground_height(x, y) - .045 + micro


def surface_height(x, y):
    # Sample the exact triangle plane used by the 1 m terrain grid.  The
    # overlay soil/aggregate therefore cannot float on a locally graded bank
    # even when ground_height is non-linear between the grid vertices.
    ix, iy = math.floor(x), math.floor(y)
    u, v = x - ix, y - iy
    a = _terrain_vertex_height(ix, iy)
    if u < 1e-9 and v < 1e-9:
        return a
    c = _terrain_vertex_height(ix + 1, iy + 1)
    if v <= u:
        b = _terrain_vertex_height(ix + 1, iy)
        return a * (1 - u) + b * (u - v) + c * v
    b = _terrain_vertex_height(ix, iy + 1)
    return a * (1 - v) + b * (v - u) + c * u


def _hard_material(p):
    if route_clearance(p) < 1.15 or building_clearance(p) < 1.1:
        return 'pavement'
    # Only the unoccupied infrastructure setback and thin district margins
    # are unbound aggregate.  The inhabited yards remain concrete.
    if (p[1] < -77 or abs(p[0]) > 94 or p[1] > 96) and building_clearance(p) > 2.2:
        return 'gravel_ground'
    return 'yard_concrete'


def build_ground(geo, ground_collection, context_collection):
    global _TERRAIN, _CONTEXT
    prepare_layout()
    batch = geo.Batch('COL_Terrain_200m', ground_collection)
    n = 200
    vertices = [(-100. + i, -100. + j, surface_height(-100. + i, -100. + j))
                for j in range(n + 1) for i in range(n + 1)]
    values = [soil_distance(p[:2]) for p in vertices]
    parts = defaultdict(list)
    cache = {}
    # Keep the established 1 m surface planes everywhere.  Only planting
    # boundary cells gain quarter-metre vertices, so a 24 cm gravel transition
    # is a narrow continuous strip instead of disconnected metre-grid shards.
    vertex_lookup = {(v[0], v[1]): i for i, v in enumerate(vertices)}
    terrain_triangles = []
    refined_cells = 0

    def vertex_at(x, y):
        key = (x, y)
        if key not in vertex_lookup:
            vertex_lookup[key] = len(vertices)
            vertices.append((x, y, surface_height(x, y)))
            values.append(soil_distance((x, y)))
        return vertex_lookup[key]

    for j in range(n):
        for i in range(n):
            a = j * (n + 1) + i
            corners = [a, a + 1, a + n + 2, a + n + 1]
            near_boundary = min(abs(values[k]) for k in corners) < .90
            if not near_boundary:
                near_boundary = abs(soil_distance((-99.5 + i, -99.5 + j))) < .90
            if near_boundary:
                refined_cells += 1
                for sy in range(4):
                    for sx in range(4):
                        x, y = -100. + i + sx * .25, -100. + j + sy * .25
                        aa, bb = vertex_at(x, y), vertex_at(x + .25, y)
                        cc, dd = vertex_at(x + .25, y + .25), vertex_at(x, y + .25)
                        terrain_triangles.extend([(aa, bb, cc), (aa, cc, dd)])
            else:
                terrain_triangles.extend([(a, a + 1, a + n + 2), (a, a + n + 2, a + n + 1)])

    def clip(ids, limit, below):
        out = []
        for a, b in zip(ids, ids[1:] + ids[:1]):
            da, db = values[a] - limit, values[b] - limit
            ia, ib = (da <= 0, db <= 0) if below else (da >= 0, db >= 0)
            if ia:
                out.append(a)
            if ia != ib:
                key = (min(a, b), max(a, b), limit)
                if abs(da) < 1e-9:
                    out.append(a)
                    continue
                if abs(db) < 1e-9:
                    out.append(b)
                    continue
                if key not in cache:
                    t = da / (da - db)
                    pa, pb = vertices[a], vertices[b]
                    cache[key] = len(vertices)
                    vertices.append(tuple(pa[k] + (pb[k] - pa[k]) * t for k in range(3)))
                    values.append(limit)
                out.append(cache[key])
        # Boundary vertices belong to both materials, but each individual
        # face must not repeat the same corner or become a degenerate face.
        clean = []
        for idx in out:
            if not clean or clean[-1] != idx:
                clean.append(idx)
        if len(clean) > 1 and clean[0] == clean[-1]:
            clean.pop()
        return clean

    for tri in terrain_triangles:
        for lo, hi, key in [(None, 0., 'ground_dirt'), (0., .24, 'gravel_ground'), (.24, None, None)]:
            # A whole triangle can coincide with a contour at a sharp
            # bed corner.  Its lower interval owns it exclusively.
            if lo is not None and max(values[v] for v in tri) <= lo + 1e-10:
                continue
            ids = list(tri)
            if lo is not None:
                ids = clip(ids, lo, False)
            if hi is not None and ids:
                ids = clip(ids, hi, True)
            if len(ids) < 3:
                continue
            p = tuple(sum(vertices[v][k] for v in ids) / len(ids) for k in range(3))
            material = key or _hard_material(p[:2])
            if -49 < p[0] < -20.3 and -18.5 < p[1] < 18.5:
                v0, v1, v2 = [vertices[k] for k in ids[:3]]
                u = [v1[k] - v0[k] for k in range(3)]
                v = [v2[k] - v0[k] for k in range(3)]
                normal = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
                if math.hypot(normal[0], normal[1]) > abs(normal[2]) * .65:
                    material = 'stone'
            parts[material].append(tuple(ids))
    areas = {}
    material_meshes = {}
    for key, faces in parts.items():
        # Remap each material's vertices; a repeated whole district vertex
        # array is unnecessary for every material and slows collision imports.
        used = sorted({v for f in faces for v in f})
        remap = {v: i for i, v in enumerate(used)}
        mesh_vertices = [vertices[v] for v in used]
        mesh_faces = [tuple(remap[v] for v in f) for f in faces]
        material_meshes[key] = (mesh_vertices, mesh_faces)
        batch.mesh(mesh_vertices, mesh_faces, key)
        areas[key] = round(sum(abs(sum(vertices[f[k]][0] * vertices[f[(k + 1) % len(f)]][1]
                                            - vertices[f[(k + 1) % len(f)]][0] * vertices[f[k]][1]
                                            for k in range(len(f)))) * .5 for f in faces), 3)
    terrain_objects = batch.finish()
    # Retain the exact generated input for the later architecture-aware cut.
    # No stale manifest or changed height function controls room/furniture
    # placement; root calls recess_terrain_for_interiors after arch.build().
    _TERRAIN = {'meshes': material_meshes, 'original_meshes': material_meshes,
                'batch': batch, 'objects': terrain_objects or [], 'recessed': False}
    REPORT['terrain_surface_area_xy_m2'] = areas
    REPORT['terrain_vertex_count'] = len(vertices)
    REPORT['terrain_faces'] = sum(len(f) for f in parts.values())
    REPORT['surface_max_microrelief_m'] = .010
    REPORT['locally_refined_planting_cells_m2'] = refined_cells
    REPORT['local_planting_grid_spacing_m'] = .25
    REPORT['unmodified_base_grid_spacing_m'] = 1.
    _pavement_detail(geo, ground_collection)

    outer = geo.Batch('Outer_ground_context', context_collection)
    size = 700.
    n = 100
    vv = [(-size + i * size * 2 / n, -size + j * size * 2 / n,
           raw_height(-size + i * size * 2 / n, max(-240, min(240, -size + j * size * 2 / n))) - .20)
          for j in range(n + 1) for i in range(n + 1)]
    ff = []
    for j in range(n):
        for i in range(n):
            x, y = -size + (i + .5) * size * 2 / n, -size + (j + .5) * size * 2 / n
            if abs(x) < 95 and abs(y) < 95:
                continue
            a = j * (n + 1) + i
            ff.append((a, a + 1, a + n + 2, a + n + 1))
    import terrain_interiors
    exterior, context_summary = terrain_interiors.trim_context_to_exterior(vv, ff, surface_height)
    outer.mesh(*exterior, 'ground_dirt')
    context_objects = outer.finish() or []
    _CONTEXT = {'meshes': {'ground_dirt': exterior},
                'original_meshes': {'ground_dirt': (vv, ff)},
                'batch': outer, 'objects': context_objects, 'summary': context_summary}
    REPORT['exterior_context_terrain'] = context_summary


def recess_terrain_for_interiors(geo, ground_collection, architecture, audit_path=None):
    """Replace only this build's terrain, after the real room geometry exists.

    Exact clipping and all-floor verification are pure Python; Blender is used
    only to swap the previous terrain objects for the verified new geometry.
    Street/path meshes, the shared design height, buildings and furniture are
    untouched.  The replacement keeps its original COL_ names and materials.
    """
    import terrain_interiors
    if _TERRAIN is None:
        raise RuntimeError('build_ground must run before interior terrain recesses')
    if _TERRAIN['recessed']:
        raise RuntimeError('Interior terrain recesses were already applied to this build')
    cutouts = architecture.get('interior_floor_cutouts')
    if not cutouts:
        raise RuntimeError('The current architecture did not supply real room floor cutouts')
    by_id = {str(b['id']): b['points'] for b in architecture['buildings']}
    threshold_exceptions = set()
    for room in cutouts:
        footprint = by_id[room['building_id']]
        for p in _outline_samples(room['cut_polygon_xy'], .25):
            outside_distance = polygon_distance(p, footprint)
            if outside_distance > 1.e-6:
                # Only the existing solid entrance floor's 2.5 cm projection
                # can extend outside the building. This is not a building-
                # wide buffer or an excavation into the adjoining footway.
                projection = room.get('floor_covered_threshold_projection_m', 0.)
                if (room['kind'] not in ('shop', 'entry') or projection != .025
                        or outside_distance > projection + 1.e-6
                        or polygon_distance(p, room['polygon_xy']) > 1.e-6):
                    raise RuntimeError('Room terrain cut exceeds its actual building/floor support: ' + room['room_id'])
                threshold_exceptions.add(room['room_id'])
    meshes, summary = terrain_interiors.recess_geometry(
        _TERRAIN['original_meshes'], cutouts, surface_height)
    summary['existing_floor_covered_threshold_projection_m'] = .025
    summary['existing_floor_covered_threshold_rooms'] = sorted(threshold_exceptions)
    before = {'core_' + key: value for key, value in _TERRAIN['original_meshes'].items()}
    after = {'core_' + key: value for key, value in meshes.items()}
    if _CONTEXT is None:
        raise RuntimeError('The exterior context terrain has not been built/verified')
    before.update({'context_' + key: value for key, value in _CONTEXT['original_meshes'].items()})
    after.update({'context_' + key: value for key, value in _CONTEXT['meshes'].items()})
    summary['exterior_context'] = _CONTEXT['summary']
    audit = terrain_interiors.audit_room_surfaces(before, after, cutouts)
    audit['terrain_layers_checked'] = ['COL_Terrain_200m', 'Outer_ground_context']
    audit['geometry'] = summary
    if audit_path is not None:
        audit_path = Path(audit_path)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2))
    if not audit['passed']:
        raise RuntimeError('Room terrain clipping failed exact geometry verification: ' +
                           json.dumps(audit['failures'][:8], ensure_ascii=False))
    if abs(summary['area_before_xy_m2'] - summary['area_after_xy_m2']) > 2.e-5:
        raise RuntimeError('Interior terrain recess lost projected surface coverage')
    old_objects = _TERRAIN['objects']
    if old_objects:
        import bpy
        for obj in old_objects:
            old_mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)
    # Clearing the original Batch also makes the headless audit's registry
    # represent only meshes actually retained in the final production scene.
    _TERRAIN['batch'].data.clear()
    replacement = geo.Batch('COL_Terrain_200m', ground_collection)
    for material, (vertices, faces) in meshes.items():
        replacement.mesh(vertices, faces, material)
    objects = replacement.finish() or []
    for obj in objects:
        obj['cq_room_terrain_recessed'] = True
        obj['cq_room_terrain_clearance_m'] = terrain_interiors.CLEARANCE
        obj['cq_room_terrain_cutouts'] = len(cutouts)
    _TERRAIN.update({'meshes': meshes, 'batch': replacement, 'objects': objects,
                     'recessed': True, 'interior_audit': audit})
    REPORT['interior_terrain_recess'] = {**summary, **{key: audit[key] for key in (
        'checked_rooms', 'original_intruding_rooms', 'final_intruding_rooms',
        'minimum_final_clearance_m', 'passed')}}
    REPORT['terrain_surface_area_xy_m2'] = {
        key: round(area, 6) for key, area in summary['area_by_material_after_xy_m2'].items()}
    REPORT['terrain_vertex_count'] = sum(len(v) for v, _ in meshes.values())
    REPORT['terrain_faces'] = sum(len(f) for _, f in meshes.values())
    return audit


def _ribbon(batch, points, width, material, zfun, lift=0.):
    vv = []
    for i, p in enumerate(points):
        a, b = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        le = max(.001, math.hypot(dx, dy))
        nx, ny = -dy / le, dx / le
        for side in [-1, 1]:
            q = (p[0] + nx * side * width * .5, p[1] + ny * side * width * .5)
            vv.append((q[0], q[1], zfun(*q) + lift))
    batch.mesh(vv, [(2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1) for i in range(len(points) - 1)], material)


def _triangulate_polygon(poly):
    """Small simple polygons only; deterministic ear clipping keeps this pure Python."""
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))
    ids = list(range(len(poly))) if area > 0 else list(reversed(range(len(poly))))
    triangles = []
    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    while len(ids) > 3:
        found = False
        for k, b in enumerate(ids):
            a, c = ids[k - 1], ids[(k + 1) % len(ids)]
            if cross(poly[a], poly[b], poly[c]) <= 1e-10:
                continue
            inside = False
            for v in ids:
                if v in [a, b, c]:
                    continue
                if (cross(poly[a], poly[b], poly[v]) >= -1e-9
                    and cross(poly[b], poly[c], poly[v]) >= -1e-9
                    and cross(poly[c], poly[a], poly[v]) >= -1e-9):
                    inside = True
                    break
            if inside:
                continue
            triangles.append([poly[a], poly[b], poly[c]])
            ids.pop(k)
            found = True
            break
        if not found:
            raise ValueError('Cannot triangulate planting polygon: ' + repr(poly))
    if len(ids) == 3:
        triangles.append([poly[i] for i in ids])
    return triangles


def _convex_clip(subject, boundary):
    points = subject
    for a, b in zip(boundary, boundary[1:] + boundary[:1]):
        if not points:
            break
        def signed(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        out = []
        for p, q in zip(points, points[1:] + points[:1]):
            dp, dq = signed(p), signed(q)
            ip, iq = dp >= -1e-9, dq >= -1e-9
            if ip:
                out.append(p)
            if ip != iq:
                t = dp / (dp - dq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
        points = []
        for p in out:
            if not points or math.dist(p, points[-1]) > 1e-8:
                points.append(p)
        if len(points) > 1 and math.dist(points[0], points[-1]) < 1e-8:
            points.pop()
    return points


def _surface_polygon(batch, poly, material, lift=.012, spacing=.55):
    """Clip to the existing terrain triangles, so soil fits the slope exactly.

    No plane or independently tessellated patch can intersect or float over a
    road-grade blend.  Every patch face shares the underlying triangle plane.
    """
    vertices, faces = [], []
    for triangle in _triangulate_polygon(poly):
        x0, y0, x1, y1 = _bounds(triangle)
        for ix in range(math.floor(x0), math.ceil(x1)):
            for iy in range(math.floor(y0), math.ceil(y1)):
                for terrain_tri in [[(ix, iy), (ix + 1, iy), (ix + 1, iy + 1)],
                                    [(ix, iy), (ix + 1, iy + 1), (ix, iy + 1)]]:
                    clipped = _convex_clip(triangle, terrain_tri)
                    if len(clipped) < 3:
                        continue
                    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(clipped, clipped[1:] + clipped[:1]))
                    if area < 1e-9:
                        continue
                    start = len(vertices)
                    vertices.extend((x, y, surface_height(x, y) + lift) for x, y in clipped)
                    faces.append(tuple(start + i for i in range(len(clipped))))
    batch.mesh(vertices, faces, material)


def _pavement_detail(geo, collection):
    paving = geo.Batch('Urban_paving_joints_and_repairs', collection)
    rng = random.Random(55239)
    slabs = 0
    zone_counts = {}
    for name, origin, width, depth, yaw, pitch, material in PAVING_ZONES:
        zone_start = slabs
        cs, sn = math.cos(yaw), math.sin(yaw)
        nx, ny = max(1, int(width / pitch)), max(1, int(depth / pitch))
        sx, sy = width / nx, depth / ny
        def world(u, v):
            return (origin[0] + u * cs - v * sn, origin[1] + u * sn + v * cs)
        for j in range(ny):
            for i in range(nx):
                u, v = -width / 2 + (i + .5) * sx, -depth / 2 + (j + .5) * sy
                p = world(u, v)
                corners = [world(u + dx * (sx * .5 - .014), v + dy * (sy * .5 - .014))
                           for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
                footprint = list(_outline_samples(corners, .42))
                footprint.extend(world(u + sx * dx, v + sy * dy)
                                 for dx in [-.3, 0., .3] for dy in [-.3, 0., .3])
                if not all(building_clearance(q) > .12 and route_clearance(q) > .18
                           and soil_distance(q) > .28 for q in footprint):
                    continue
                _surface_polygon(paving, corners, material, .011 + rng.uniform(0, .004), .95)
                # The joints are only 12 mm wide; the supporting terrain is
                # continuous beneath them, so this detail cannot create pits.
                for a, b in zip(corners[:2], corners[1:3]):
                    le = math.dist(a, b)
                    points = [(a[0] + (b[0] - a[0]) * k / max(1, math.ceil(le / .4)),
                               a[1] + (b[1] - a[1]) * k / max(1, math.ceil(le / .4)))
                              for k in range(max(1, math.ceil(le / .4)) + 1)]
                    _ribbon(paving, points, .012, 'soil_dark', surface_height, .017)
                if (i * 3 + j * 5) % 13 == 0:
                    # Fine irregular old repair cracks, never stripes across
                    # a whole road or disconnected debris floating in space.
                    points = [world(u - sx * .31 + k * sx * .10,
                                    v + .09 * math.sin(k * 1.9 + i)) for k in range(7)]
                    _ribbon(paving, points, .009, 'soil_dark', surface_height, .019)
                slabs += 1
        zone_counts[name] = slabs - zone_start
    paving.finish()
    REPORT['detailed_paving_slabs'] = slabs
    REPORT['detailed_paving_slabs_by_zone'] = zone_counts


def _edging(batch, poly, height=.085, width=.115, closed=True):
    """Low masonry kerbs, top and bottom individually fitted to the terrain."""
    pairs = zip(poly, poly[1:] + poly[:1]) if closed else zip(poly, poly[1:])
    for a, b in pairs:
        length = math.dist(a, b)
        n = max(1, math.ceil(length / .50))
        dx, dy = (b[0] - a[0]) / max(.001, length), (b[1] - a[1]) / max(.001, length)
        for k in range(n):
            t0, t1 = (k + .012) / n, (k + .988) / n
            p, q = ((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for t in [t0, t1])
            shape = [(p[0] + dy * width / 2, p[1] - dx * width / 2),
                     (q[0] + dy * width / 2, q[1] - dx * width / 2),
                     (q[0] - dy * width / 2, q[1] + dx * width / 2),
                     (p[0] - dy * width / 2, p[1] + dx * width / 2)]
            vv = [(x, y, surface_height(x, y) - .075) for x, y in shape]
            vv += [(x, y, surface_height(x, y) + height) for x, y in shape]
            batch.mesh(vv, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                            (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], 'stone')


def _pebble(batch, p, rng, lift=.02):
    x, y = p
    z = surface_height(x, y) + lift
    r = rng.uniform(.018, .065)
    a = rng.random() * math.tau
    points = [(x + math.cos(a + k * math.tau / 5) * r,
               y + math.sin(a + k * math.tau / 5) * r * .71, z) for k in range(5)]
    points.append((x + r * .1, y, z + r * .42))
    batch.mesh(points, [(k, (k + 1) % 5, 5) for k in range(5)], 'gravel_ground')


def _leaf(batch, p, rng, lift=.026):
    x, y = p
    z = surface_height(x, y) + lift
    a = rng.random() * math.tau
    dx, dy = math.cos(a) * rng.uniform(.035, .085), math.sin(a) * rng.uniform(.035, .085)
    batch.mesh([(x - dx, y - dy, z), (x - dy * .35, y + dx * .35, z + .004),
                (x + dx, y + dy, z + .001), (x + dy * .35, y - dx * .35, z + .004)],
               [(0, 2, 1), (0, 3, 2)], 'wood')


def _grass(batch, p, rng, height=.14, lift=.013):
    x, y = p
    z = surface_height(x, y) + lift
    for _ in range(rng.randint(3, 5)):
        a = rng.random() * math.tau
        dx, dy = math.cos(a), math.sin(a)
        h, w = height * rng.uniform(.6, 1.), rng.uniform(.004, .008)
        xx, yy = x + rng.uniform(-.025, .025), y + rng.uniform(-.025, .025)
        batch.mesh([(xx - dy * w, yy + dx * w, z), (xx + dy * w, yy - dx * w, z),
                    (xx + dx * h * .22, yy + dy * h * .22, z + h)], [(0, 1, 2)], 'leaf_olive')


def _root_height(p, root_radius):
    # Scan assets have a flat source base.  Seat that base at the low side of
    # its actual root footprint, so downhill roots cannot hang above a slope.
    heights = [surface_height(*p)]
    heights.extend(surface_height(p[0] + root_radius * math.cos(k * math.tau / 8),
                                  p[1] + root_radius * math.sin(k * math.tau / 8)) for k in range(8))
    return min(heights) + .007


def build_planting(geo, scanned, props, arch, free_land, occupied,
                   land_collection, prop_collection, revision):
    global _ARCH
    plan = prepare_layout()
    _ARCH = arch
    edging = geo.Batch('COL_Planting_low_masonry_edges', land_collection)
    soil = geo.Batch('Planting_soil_fitted_to_slope', land_collection)
    details = geo.Batch('Planting_leaf_litter_gravel_and_seedlings', land_collection)
    rng = random.Random(668205)
    trees = []
    shrubs = []
    root_records = REPORT['plant_support_records']
    for i, tree in enumerate(plan['trees']):
        x, y = tree['point']
        r = tree['radius']
        if not free_land((x, y), r + .55) or door_clearance((x, y)) < r + .5:
            continue
        outline = [(x + r * math.cos(k * math.tau / 32), y + r * math.sin(k * math.tau / 32)) for k in range(32)]
        # A tree already inside a continuous garden needs no redundant ring.
        in_bed = any(polygon_distance((x, y), b['poly']) < -.45 for b in plan['beds'])
        if not in_bed:
            _surface_polygon(soil, outline, 'soil_dark', .012, .40)
            _edging(edging, outline, .078, .12)
        z = _root_height((x, y), .48)
        seed = tree['seed']
        scan_support = None
        if revision >= 5:
            lod = 'hero' if tree['name'] in ['tree_01', 'tree_09', 'tree_17', 'tree_22'] else 'medium'
            # Keep proper leaf silhouettes on every large island tree in the
            # accessible district. Other species retain their current LOD.
            if seed % 3 == 0 and tree['height'] >= 9.:
                lod = 'hero'
                from tree_root_support import fit_island_base
                z, scan_support = fit_island_base(
                    ROOT, (x, y), tree['height'], seed, z,
                    surface_height, soil_distance, .009 if in_bed else .012)
            scanned.make_tree('Planted_' + tree['name'], (x, y, z), height=tree['height'],
                              seed=seed, collection=land_collection, lod=lod)
        else:
            props.make_tree((x, y, z), scale=tree['height'] / 10., seed=seed, collection=land_collection)
        trees.append((x, y))
        support_record = {'name': tree['name'], 'kind': 'tree', 'point': [x, y, z],
                          'support': 'soil bed' if in_bed else 'slope fitted soil tree well',
                          'soil_clearance_m': round(-soil_distance((x, y)), 3),
                          'route_clearance_m': round(route_clearance((x, y)), 3)}
        if scan_support is not None:
            support_record.update({'asset_key': 'island_tree_01', 'foliage_variant': lod,
                                   'stem_variant': 'hero', 'scan_base_support': scan_support})
        root_records.append(support_record)
        for k in range(32):
            a, rr = rng.random() * math.tau, r * math.sqrt(rng.uniform(.08, .94))
            p = (x + math.cos(a) * rr, y + math.sin(a) * rr)
            (_leaf if k % 3 else _pebble)(details, p, rng)
            if k % 7 == 0 and rr > .38:
                _grass(details, p, rng, .10)
    for bi, bed in enumerate(plan['beds']):
        poly = bed['poly']
        _surface_polygon(soil, poly, 'ground_dirt', .009, .55)
        # The public edges receive restrained masonry; the court borders end
        # against their existing walls.  No high edging crosses an entrance.
        _edging(edging, poly, .060 if 'court' in bed['name'] else .085, .10)
        bb = bed['bounds']
        accepted = []
        count = max(2, int((bb[2] - bb[0]) * (bb[3] - bb[1]) / 2.5))
        count = min(count, 16)
        for attempt in range(count * 18):
            p = (rng.uniform(bb[0], bb[2]), rng.uniform(bb[1], bb[3]))
            h = rng.uniform(.40, .66)
            # Canopy is about 1.56 times height in the normalized source.
            canopy_r = h * .82
            if polygon_distance(p, poly) > -(canopy_r + .10):
                continue
            if not free_land(p, canopy_r + .55) or door_clearance(p) < canopy_r + .55:
                continue
            if any(math.dist(p, q) < .95 for q in trees) or any(math.dist(p, q) < 1.0 for q in accepted):
                continue
            if any(math.dist(p, q) < .85 for q in shrubs):
                continue
            z = _root_height(p, h * .57)
            name = 'Soil_bed_%s_shrub_%02d' % (bed['name'], len(accepted))
            if revision >= 5:
                scanned.make_shrub(name, (*p, z), height=h, seed=32000 + bi * 101 + len(accepted),
                                   collection=land_collection, lod='low')
            accepted.append(p)
            shrubs.append(p)
            root_records.append({'name': name, 'kind': 'shrub', 'point': [*p, z], 'support': bed['name'],
                                 'soil_clearance_m': round(-polygon_distance(p, poly), 3),
                                 'canopy_radius_m': round(canopy_r, 3),
                                 'route_clearance_m': round(route_clearance(p), 3)})
            if len(accepted) >= count:
                break
        for _ in range(max(20, count * 15)):
            p = (rng.uniform(bb[0], bb[2]), rng.uniform(bb[1], bb[3]))
            if polygon_distance(p, poly) > -.07:
                continue
            if not free_land(p, .3) or door_clearance(p) < .55:
                continue
            chance = rng.random()
            if chance < .25:
                _grass(details, p, rng, rng.uniform(.09, .17))
            elif chance < .62:
                _leaf(details, p, rng)
            else:
                _pebble(details, p, rng)
        # Small accumulations sit in the gravel transition outside the curb,
        # rather than evenly distributed stones across the whole concrete.
        for p in _outline_samples(poly, .40):
            center = ((bb[0] + bb[2]) * .5, (bb[1] + bb[3]) * .5)
            dx, dy = p[0] - center[0], p[1] - center[1]
            le = max(.01, math.hypot(dx, dy))
            q = (p[0] + dx / le * .15, p[1] + dy / le * .15)
            if .03 < soil_distance(q) < .30 and route_clearance(q) > .3 and not occupied(q, .1):
                _pebble(details, q, rng, .013)
                if rng.random() < .45:
                    _leaf(details, q, rng, .014)
    _gutter_litter(details, rng, occupied)
    edging.finish(.008)
    soil.finish()
    details.finish()
    REPORT['trees_placed'] = len(trees)
    REPORT['soil_bed_shrub_clusters'] = len(shrubs)
    REPORT['random_hardscape_shrub_clusters'] = 0
    REPORT['random_hardscape_grass_tufts'] = 0
    fitted_scans = [r['scan_base_support'] for r in root_records if 'scan_base_support' in r]
    REPORT['scan_tree_base_fitting'] = {
        'fitted_trees': len(fitted_scans),
        'method': 'Actual prepared hero-stem base faces and open scan-cut edges placed below unchanged soil',
        'minimum_burial_m': min((r['minimum_scan_base_burial_m'] for r in fitted_scans), default=None),
        'maximum_additional_burial_m': max((r['additional_burial_m'] for r in fitted_scans), default=None),
        'minimum_visible_contact_soil_margin_m': min((r['minimum_visible_contact_soil_margin_m'] for r in fitted_scans), default=None),
        'terrain_tree_wells_and_routes_changed': False,
    }
    return {'trees': len(trees), 'planted_beds': len(plan['beds']),
            'scanned_shrub_clusters': len(shrubs), 'slope_fitted_tree_wells': len(trees),
            'random_hardscape_shrub_clusters': 0}


def _gutter_litter(batch, rng, occupied):
    for _, points, width in SUPPLEMENTAL:
        for a, b in zip(points, points[1:]):
            length = math.dist(a, b)
            n = max(1, int(length / 1.7))
            dx, dy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            for k in range(n):
                t = (k + .5) / n
                for side in [-1, 1]:
                    distance = width / 2 + rng.uniform(.23, .40)
                    p = (a[0] + (b[0] - a[0]) * t - dy * side * distance,
                         a[1] + (b[1] - a[1]) * t + dx * side * distance)
                    if occupied(p, .2) or soil_distance(p) < .3:
                        continue
                    if rng.random() < .65:
                        _leaf(batch, p, rng, .018)
                    else:
                        _pebble(batch, p, rng, .013)


def build_stairside_planters(geo, scanned, free_land, collection, landcollection, revision):
    """Actual open masonry troughs, stepped along the central grade.

    Planting stops at the workshop doorway axis; its former 14 m unbroken
    hedge is replaced with three deliberate short resident-managed groups.
    """
    if revision < 7:
        return {}
    body = geo.Batch('COL_Stairside_resident_planter', collection)
    trim = geo.Batch('Stairside_planter_topsoil_and_leaf_litter', landcollection)
    # All roots sit in a complete soil tray.  Full solid boxes with a black
    # cap are avoided: four real low walls surround the visible soil volume.
    runs = [(-15.65, -46.3, -43.1), (-15.65, -33.8, -30.1)]
    count = 0
    sections = 0
    for ri, (x, y0, y1) in enumerate(runs):
        n = max(1, math.ceil((y1 - y0) / 1.30))
        length = (y1 - y0) / n
        for k in range(n):
            y = y0 + (k + .5) * length
            corners = [(x + dx, y + dy) for dx in [-.56, .56] for dy in [-length / 2, length / 2]]
            if not all(free_land(p, .60) and door_clearance(p) > .65 for p in corners):
                continue
            top = max(ground_height(*p) for p in corners) + .31
            bottom = min(ground_height(*p) for p in corners) - .06
            # Horizontal soil trays have a real front retaining wall and
            # separate stepped modules; their underside never floats uphill.
            for xx in [x - .50, x + .50]:
                body.box((xx, y, (top + bottom) / 2), (.13, length - .018, top - bottom), 'stone')
                trim.box((xx, y, top + .028), (.17, length - .010, .055), 'concrete')
            for yy in [y - length / 2 + .055, y + length / 2 - .055]:
                body.box((x, yy, (top + bottom) / 2), (.88, .11, top - bottom), 'stone')
            soil_z = top - .065
            body.box((x, y, soil_z - .04), (.88, length - .23, .08), 'soil_dark')
            height = .47 + .06 * math.sin(k * 2.7 + ri)
            scanned.make_shrub('Resident_trough_shrub_%s_%s' % (ri, k), (x, y, soil_z),
                               height=height, seed=31001 + ri * 53 + k, collection=landcollection, lod='low')
            REPORT['plant_support_records'].append({'name': 'Resident_trough_shrub_%s_%s' % (ri, k),
                'kind': 'shrub', 'point': [x, y, soil_z], 'support': 'stepped masonry trough with recessed topsoil',
                'soil_clearance_m': .44, 'canopy_radius_m': round(height * .82, 3),
                'route_clearance_m': round(route_clearance((x, y)), 3)})
            sections += 1
            count += 1
    body.finish(.012)
    trim.finish()
    REPORT['stepped_planter_sections'] = sections
    REPORT['raised_planter_shrub_clusters'] = count
    return {'continuous_hedge_clusters': count, 'stairside_planter_sections': sections}


def write_report(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2))

