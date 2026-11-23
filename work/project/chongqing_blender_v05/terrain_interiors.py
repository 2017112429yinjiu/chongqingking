"""Exact room-footprint terrain recesses, independent of Blender.

Only the terrain triangles inside the current architectural room shells can
move.  Each intersected triangle is partitioned at the real wall boundaries;
outside fragments retain their original plane.  The inside is the lower of
that plane and the room's floor minus a small construction clearance.  Vertical
faces close the discontinuity within the opaque walls.  The same mesh data is
used by the production build and the numerical verification below.
"""
from collections import defaultdict
import math

EPS = 1.e-9
CLEARANCE = .03


def area_xy(poly):
    return .5 * sum(a[0] * b[1] - b[0] * a[1]
                     for a, b in zip(poly, poly[1:] + poly[:1]))


def bounds(poly):
    return (min(p[0] for p in poly), min(p[1] for p in poly),
            max(p[0] for p in poly), max(p[1] for p in poly))


def overlap(a, b):
    return not (a[2] < b[0] - EPS or b[2] < a[0] - EPS or
                a[3] < b[1] - EPS or b[3] < a[1] - EPS)


def _lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def _clean(poly):
    result = []
    for p in poly:
        if not result or math.dist(p, result[-1]) > EPS:
            result.append(p)
    if len(result) > 1 and math.dist(result[0], result[-1]) <= EPS:
        result.pop()
    return result if len(result) >= 3 and abs(area_xy(result)) > 1.e-10 else []


def _split(poly, signed_distance):
    """Partition a 3-D polygon at a plane without moving either side."""
    positive, negative = [], []
    distances = [signed_distance(p) for p in poly]
    distances = [0. if abs(d) < EPS else d for d in distances]
    for i, (a, b) in enumerate(zip(poly, poly[1:] + poly[:1])):
        da, db = distances[i], distances[(i + 1) % len(poly)]
        if da >= 0:
            positive.append(a)
        if da <= 0:
            negative.append(a)
        if da * db < 0:
            p = _lerp(a, b, da / (da - db))
            positive.append(p)
            negative.append(p)
    return _clean(positive), _clean(negative)


def _distance(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def _ccw(poly):
    poly = [tuple(p[:2]) for p in poly]
    return poly if area_xy(poly) > 0 else list(reversed(poly))


def convex_parts(polygon):
    """Decompose concave threshold outlines; a convex room stays one piece."""
    polygon = _ccw(polygon)
    if all(inside(p, polygon, 1.e-7) for p in polygon):
        return [polygon]
    remaining = list(range(len(polygon)))
    parts = []
    while len(remaining) > 3:
        for j, index in enumerate(remaining):
            a, b, c = remaining[j - 1], index, remaining[(j + 1) % len(remaining)]
            triangle = [polygon[a], polygon[b], polygon[c]]
            if area_xy(triangle) < 1.e-10:
                continue
            if any(inside(polygon[k], triangle, 1.e-10) for k in remaining if k not in (a, b, c)):
                continue
            parts.append(triangle)
            remaining.pop(j)
            break
        else:
            raise ValueError('Cannot decompose room threshold outline')
    parts.append([polygon[i] for i in remaining])
    if abs(sum(area_xy(p) for p in parts) - area_xy(polygon)) > 1.e-7:
        raise ValueError('Room threshold decomposition changed its covered area')
    return parts


def partition_polygon(subject, boundary):
    """A convex inside polygon and disjoint outside fragments, in 3-D."""
    remaining = subject
    outside = []
    for a, b in zip(boundary, boundary[1:] + boundary[:1]):
        if not remaining:
            break
        remaining, fragment = _split(remaining, lambda p: _distance(a, b, p))
        if fragment:
            outside.append(fragment)
    return remaining, outside


def intersect_polygon(subject, boundary):
    result = subject
    for a, b in zip(boundary, boundary[1:] + boundary[:1]):
        if not result:
            break
        result, _ = _split(result, lambda p: _distance(a, b, p))
    return result


def inside(p, polygon, tolerance=EPS):
    return all(_distance(a, b, p) >= -tolerance
               for a, b in zip(polygon, polygon[1:] + polygon[:1]))


def _on_boundary(a, b, polygon):
    for p, q in zip(polygon, polygon[1:] + polygon[:1]):
        length = math.dist(p, q)
        if (abs(_distance(p, q, a)) < 2.e-8 * length and
                abs(_distance(p, q, b)) < 2.e-8 * length):
            return True
    return False


def _segment_interval(a, b, polygon, inset=0.):
    lo, hi = 0., 1.
    for p, q in zip(polygon, polygon[1:] + polygon[:1]):
        margin = inset * math.dist(p, q)
        d0, d1 = _distance(p, q, a) - margin, _distance(p, q, b) - margin
        if abs(d1 - d0) < EPS:
            if d0 < -EPS:
                return None
            continue
        t = -d0 / (d1 - d0)
        if d1 > d0:
            lo = max(lo, t)
        else:
            hi = min(hi, t)
        if hi - lo < EPS:
            return None
    lo, hi = max(0., lo), min(1., hi)
    return (lo, hi) if hi - lo > EPS else None


def _wall_segment(wall, lo, hi, cap=None):
    # a/b contain the original high endpoint; c/d the recessed low endpoint.
    a, b, c, d = wall
    out = [_lerp(a, b, lo), _lerp(a, b, hi),
           _lerp(d, c, hi), _lerp(d, c, lo)]
    if cap is not None:
        out = [(p[0], p[1], min(p[2], cap)) for p in out]
    if max(out[0][2] - out[3][2], out[1][2] - out[2][2]) < EPS:
        return None
    return out


def _lower_existing_walls(walls, polygon, cap):
    """A later overlapping room also trims previously created vertical faces."""
    result = []
    for wall in walls:
        interval = _segment_interval(wall[0], wall[1], polygon)
        if interval is None:
            result.append(wall)
            continue
        lo, hi = interval
        for a, b in ((0., lo), (hi, 1.)):
            if b - a > EPS:
                part = _wall_segment(wall, a, b)
                if part:
                    result.append(part)
        splits = [lo, hi]
        for a, b in ((wall[0], wall[1]), (wall[3], wall[2])):
            if abs(b[2] - a[2]) > EPS:
                t = (cap - a[2]) / (b[2] - a[2])
                if lo + EPS < t < hi - EPS:
                    splits.append(t)
        splits = sorted(set(splits))
        for a, b in zip(splits, splits[1:]):
            part = _wall_segment(wall, a, b, cap)
            if part:
                result.append(part)
    return result


def _resolve_wall(wall, masks, height_query):
    """Keep only a real final height discontinuity, including mask overlaps.

    A concave doorway is partitioned into convex pieces. Their internal edges
    must not leave vertical terrain fins in the room. The same rule also
    resolves two overlapping room cutouts at different floor levels.
    """
    a, b = wall[:2]
    length = math.dist(a[:2], b[:2])
    if length < 1.e-9:
        return []
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    offset = 2.e-6
    nx, ny = -(b[1] - a[1]) / length, (b[0] - a[0]) / length
    inner = (mid[0] + nx * offset, mid[1] + ny * offset)
    outer = (mid[0] - nx * offset, mid[1] - ny * offset)
    cap_in = min((m['cap'] for m in masks if inside(inner, m['polygon'])), default=math.inf)
    cap_out = min((m['cap'] for m in masks if inside(outer, m['polygon'])), default=math.inf)
    if cap_in == cap_out:
        return []
    za, zb = height_query(*a[:2]), height_query(*b[:2])
    splits = [0., 1.]
    if abs(zb - za) > EPS:
        for cap in (cap_in, cap_out):
            t = (cap - za) / (zb - za)
            if EPS < t < 1 - EPS:
                splits.append(t)
    splits = sorted(set(splits))
    result = []
    for lo, hi in zip(splits, splits[1:]):
        p, q = _lerp(a, b, lo), _lerp(a, b, hi)
        zp, zq = za + (zb - za) * lo, za + (zb - za) * hi
        poly = [(p[0], p[1], min(zp, cap_out)), (q[0], q[1], min(zq, cap_out)),
                (q[0], q[1], min(zq, cap_in)), (p[0], p[1], min(zp, cap_in))]
        if max(abs(poly[0][2] - poly[3][2]), abs(poly[1][2] - poly[2][2])) > EPS:
            result.append(poly)
    return result


def _cells(bb, size=2.):
    for x in range(math.floor(bb[0] / size), math.floor(bb[2] / size) + 1):
        for y in range(math.floor(bb[1] / size), math.floor(bb[3] / size) + 1):
            yield x, y


def prepare_cutouts(cutouts, height_query, clearance=CLEARANCE):
    records = []
    ids = set()
    for row in cutouts:
        key = row['room_id']
        if key in ids:
            raise ValueError('Duplicate architectural room id: ' + key)
        ids.add(key)
        outline = _ccw(row['cut_polygon_xy'])
        if len(outline) < 3 or area_xy(outline) < EPS:
            raise ValueError('Degenerate room footprint: ' + key)
        for polygon in convex_parts(outline):
            bb = bounds(polygon)
            # A conservative bound on the original piecewise-linear one-metre
            # terrain.  This never excludes an intersecting uphill room.
            highest = max(height_query(x, y)
                          for x in range(math.floor(bb[0]), math.ceil(bb[2]) + 1)
                          for y in range(math.floor(bb[1]), math.ceil(bb[3]) + 1))
            cap = float(row['floor_top_z']) - clearance
            records.append({'room_id': key, 'polygon': polygon, 'bounds': bb,
                            'cap': cap, 'potentially_active': highest > cap + EPS,
                            'source': row})
    return records


def recess_geometry(material_meshes, cutouts, height_query, clearance=CLEARANCE):
    """Return new material meshes and a factual summary; never edits inputs."""
    masks = prepare_cutouts(cutouts, height_query, clearance)
    grid = defaultdict(set)
    for i, mask in enumerate(masks):
        if mask['potentially_active']:
            for cell in _cells(mask['bounds']):
                grid[cell].add(i)
    result = {}
    touched = set()
    changed_source_faces = 0
    wall_faces = 0
    max_drop = 0.
    changed_area = 0.
    areas_before, areas_after = {}, {}
    for material, (vertices, faces) in material_meshes.items():
        output_vertices, output_faces = [], []
        vertex_map = {}
        emitted_walls = set()

        def emit(poly, vertical=False):
            nonlocal wall_faces
            ids = []
            for p in poly:
                key = tuple(round(v, 10) for v in p)
                if key not in vertex_map:
                    vertex_map[key] = len(output_vertices)
                    output_vertices.append(tuple(p))
                ids.append(vertex_map[key])
            if vertical:
                # A step can end in one zero-height corner.  Drop its repeated
                # index rather than leaving a zero-area triangle in the mesh.
                clean = []
                for idx in ids:
                    if not clean or clean[-1] != idx:
                        clean.append(idx)
                if len(clean) > 1 and clean[0] == clean[-1]:
                    clean.pop()
                if len(set(clean)) >= 3:
                    key = tuple(sorted(clean))
                    if key not in emitted_walls:
                        emitted_walls.add(key)
                        output_faces.append(tuple(clean))
                        wall_faces += 1
            else:
                # Source and partition fragments are convex planar surfaces.
                for i in range(1, len(ids) - 1):
                    face = (ids[0], ids[i], ids[i + 1])
                    if abs(area_xy([output_vertices[k] for k in face])) > 1.e-10:
                        output_faces.append(face)

        for face in faces:
            source_poly = [vertices[i] for i in face]
            source_bb = bounds(source_poly)
            candidates = set()
            for cell in _cells(source_bb):
                candidates.update(grid.get(cell, ()))
            candidates = sorted(i for i in candidates if overlap(source_bb, masks[i]['bounds'])
                                and max(p[2] for p in source_poly) > masks[i]['cap'] + EPS)
            pieces, walls = [source_poly], []
            changed = False
            for index in candidates:
                mask = masks[index]
                polygon, cap = mask['polygon'], mask['cap']
                walls = _lower_existing_walls(walls, polygon, cap)
                next_pieces = []
                for piece in pieces:
                    if max(p[2] for p in piece) <= cap + EPS or not overlap(bounds(piece), mask['bounds']):
                        next_pieces.append(piece)
                        continue
                    inner, outer = partition_polygon(piece, polygon)
                    if not inner or max(p[2] for p in inner) <= cap + EPS:
                        next_pieces.append(piece)
                        continue
                    changed = True
                    touched.add(mask['room_id'])
                    max_drop = max(max_drop, max(p[2] - cap for p in inner))
                    low, high = _split(inner, lambda p: cap - p[2])
                    next_pieces.extend(outer)
                    if low:
                        next_pieces.append(low)
                    if high:
                        next_pieces.append([(p[0], p[1], cap) for p in high])
                        for a, b in zip(high, high[1:] + high[:1]):
                            if _on_boundary(a, b, polygon):
                                wall = [a, b, (b[0], b[1], cap), (a[0], a[1], cap)]
                                if max(a[2], b[2]) > cap + EPS:
                                    walls.append(wall)
                pieces = next_pieces
            if changed:
                changed_source_faces += 1
                # The actual lowered area is found from the final planes;
                # overlapping room masks do not double-count it.
                for piece in pieces:
                    center = tuple(sum(p[k] for p in piece) / len(piece) for k in range(3))
                    if center[2] < height_query(*center[:2]) - 1.e-7:
                        changed_area += abs(area_xy(piece))
            for piece in pieces:
                emit(piece)
            for wall in walls:
                for resolved in _resolve_wall(wall, [masks[i] for i in candidates], height_query):
                    emit(resolved, True)
        areas_before[material] = sum(abs(area_xy([vertices[i] for i in face])) for face in faces)
        areas_after[material] = sum(abs(area_xy([output_vertices[i] for i in face])) for face in output_faces)
        result[material] = (output_vertices, output_faces)
    summary = {
        'method': 'Exact XY triangle partition; min(original surface, real room floor - clearance); vertical wall-hidden closure',
        'coordinate_system': 'Blender Z-up, metres',
        'floor_clearance_m': clearance,
        'architectural_floor_records': len(cutouts),
        'first_storey_floor_records': sum(r['storey'] == 0 for r in cutouts),
        'potentially_intersecting_floor_records': len({m['room_id'] for m in masks if m['potentially_active']}),
        'convex_mask_components': len(masks),
        'applied_room_cutouts': len(touched),
        'applied_room_ids': sorted(touched),
        'changed_original_faces': changed_source_faces,
        'lowered_surface_xy_m2': round(changed_area, 6),
        'largest_local_drop_m': round(max_drop, 6),
        'vertical_closure_faces': wall_faces,
        'area_before_xy_m2': sum(areas_before.values()),
        'area_after_xy_m2': sum(areas_after.values()),
        'area_by_material_after_xy_m2': areas_after,
        'triangle_plane_outside_cutouts_preserved': True,
        'building_floor_and_furniture_positions_changed': False,
    }
    return result, summary


def trim_context_to_exterior(vertices, faces, height_query, half_extent=100.):
    """Remove any second terrain layer inside the authored 200 m footprint.

    Context triangle fragments retain their original interpolated elevations.
    One-metre vertical seam faces join them to the core boundary, without
    moving the core's surface or creating a gap into the background terrain.
    """
    e = half_extent
    core = [(-e, -e), (e, -e), (e, e), (-e, e)]
    output_vertices, output_faces = [], []
    vertex_map = {}
    removed_area = 0.
    seam_faces = 0
    top_area = 0.
    original_area = 0.

    def emit(poly, vertical=False):
        nonlocal seam_faces
        ids = []
        for point in poly:
            key = tuple(round(v, 10) for v in point)
            if key not in vertex_map:
                vertex_map[key] = len(output_vertices)
                output_vertices.append(tuple(point))
            index = vertex_map[key]
            if not ids or ids[-1] != index:
                ids.append(index)
        if len(ids) > 1 and ids[0] == ids[-1]:
            ids.pop()
        if len(set(ids)) < 3:
            return
        for j in range(1, len(ids) - 1):
            face = (ids[0], ids[j], ids[j + 1])
            if not vertical and area_xy([output_vertices[k] for k in face]) <= 1.e-10:
                continue
            output_faces.append(face)
            if vertical:
                seam_faces += 1

    def seam(a, b):
        nonlocal seam_faces
        axis = None
        for candidate in (0, 1):
            if abs(a[candidate] - b[candidate]) < 1.e-7 and abs(abs(a[candidate]) - e) < 1.e-7:
                axis = candidate
                break
        if axis is None:
            return
        along = 1 - axis
        delta = b[along] - a[along]
        if abs(delta) < EPS:
            return
        lo, hi = sorted((a[along], b[along]))
        lo, hi = max(-e, lo), min(e, hi)
        if hi - lo < EPS:
            return
        coordinates = [lo] + [float(k) for k in range(math.floor(lo) + 1, math.ceil(hi))] + [hi]
        parameters = sorted((v - a[along]) / delta for v in coordinates)
        for t0, t1 in zip(parameters, parameters[1:]):
            p, q = _lerp(a, b, t0), _lerp(a, b, t1)
            hp, hq = height_query(*p[:2]), height_query(*q[:2])
            d0, d1 = hp - p[2], hq - q[2]
            pieces = [(p, q, hp, hq)]
            if d0 * d1 < 0:
                t = d0 / (d0 - d1)
                crossing = _lerp(p, q, t)
                hc = crossing[2]
                pieces = [(p, crossing, hp, hc), (crossing, q, hc, hq)]
            for left, right, hl, hr in pieces:
                if max(abs(hl - left[2]), abs(hr - right[2])) < EPS:
                    continue
                # The boundary edge follows the exterior fragment. Reverse
                # its side-face winding toward the lower of the two surfaces.
                emit([(left[0], left[1], hl), (right[0], right[1], hr), right, left], True)

    for face in faces:
        polygon = [vertices[k] for k in face]
        for i in range(1, len(polygon) - 1):
            triangle = [polygon[0], polygon[i], polygon[i + 1]]
            original_area += abs(area_xy(triangle))
            if overlap(bounds(triangle), (-e, -e, e, e)):
                inner, outer = partition_polygon(triangle, core)
                if inner:
                    removed_area += abs(area_xy(inner))
            else:
                outer = [triangle]
            for fragment in outer:
                top_area += abs(area_xy(fragment))
                emit(fragment)
                for a, b in zip(fragment, fragment[1:] + fragment[:1]):
                    seam(a, b)
    if abs(original_area - top_area - removed_area) > 1.e-5:
        raise ValueError('Context clipping changed projected terrain coverage')
    return (output_vertices, output_faces), {
        'method': 'Exact original context triangle subtraction of the 200 m core; original exterior planes retained',
        'original_context_area_xy_m2': original_area,
        'removed_context_overlap_xy_m2': removed_area,
        'final_context_area_xy_m2': top_area,
        'core_boundary_vertical_seam_triangles': seam_faces,
        'boundary_seam_spacing_m': 1.,
    }


class SurfaceIndex:
    """Index the actual top faces, never a surrogate terrain-height function."""
    def __init__(self, material_meshes, query_bounds=None):
        self.faces = []
        self.grid = defaultdict(set)
        self.walls = []
        self.wall_grid = defaultdict(set)
        for material, (vertices, faces) in material_meshes.items():
            for face in faces:
                polygon = [vertices[i] for i in face]
                if query_bounds is not None and not overlap(bounds(polygon), query_bounds):
                    # A conservative spatial cull: even the largest distant
                    # context triangle is retained if its bounds touch the
                    # complete district floor audit region.
                    continue
                if abs(area_xy(polygon)) <= 1.e-10:
                    # Separately retain vertical closure faces. A planar top
                    # audit alone could miss a fin left by convex decomposition.
                    columns = {}
                    for p in polygon:
                        key = (round(p[0], 9), round(p[1], 9))
                        if key not in columns or p[2] > columns[key][2]:
                            columns[key] = p
                    if len(columns) == 2:
                        a, b = columns.values()
                        wall_id = len(self.walls)
                        bb = bounds([a, b])
                        self.walls.append((a, b, bb))
                        for cell in _cells(bb):
                            self.wall_grid[cell].add(wall_id)
                    continue
                if area_xy(polygon) < 0:
                    continue
                index = len(self.faces)
                bb = bounds(polygon)
                self.faces.append((polygon, bb, material))
                for cell in _cells(bb):
                    self.grid[cell].add(index)

    def intersecting(self, polygon):
        bb = bounds(polygon)
        ids = set()
        for cell in _cells(bb):
            ids.update(self.grid.get(cell, ()))
        for index in ids:
            face, face_bb, _ = self.faces[index]
            if overlap(bb, face_bb):
                clipped = intersect_polygon(face, polygon)
                if clipped:
                    yield clipped

    def height(self, x, y):
        candidates = self.grid.get((math.floor(x / 2.), math.floor(y / 2.)), ())
        heights = []
        for index in candidates:
            polygon, bb, _ = self.faces[index]
            if not (bb[0] - EPS <= x <= bb[2] + EPS and bb[1] - EPS <= y <= bb[3] + EPS):
                continue
            a = polygon[0]
            for i in range(1, len(polygon) - 1):
                b, c = polygon[i], polygon[i + 1]
                det = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
                if abs(det) < 1.e-10:
                    continue
                u = ((x - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (y - a[1])) / det
                v = ((b[0] - a[0]) * (y - a[1]) - (x - a[0]) * (b[1] - a[1])) / det
                if u >= -EPS and v >= -EPS and u + v <= 1 + EPS:
                    heights.append(a[2] + u * (b[2] - a[2]) + v * (c[2] - a[2]))
        return max(heights) if heights else None

    def protruding_interior_walls(self, polygon, floor):
        bb = bounds(polygon)
        ids = set()
        for cell in _cells(bb):
            ids.update(self.wall_grid.get(cell, ()))
        intrusions = []
        for index in ids:
            a, b, wall_bb = self.walls[index]
            if not overlap(bb, wall_bb):
                continue
            # The exact floor boundary belongs to its architectural wall or
            # solid threshold. Only a line strictly inside the room is a fin.
            interval = _segment_interval(a, b, polygon, inset=1.e-6)
            if interval is None:
                continue
            high = max(a[2] + (b[2] - a[2]) * t for t in interval)
            if high > floor + 1.e-7:
                intrusions.append({'wall_index': index, 'height_above_floor_m': high - floor})
        return intrusions


def audit_room_surfaces(before, after, cutouts, clearance=CLEARANCE):
    """Exact maximum of every actual terrain fragment under every room.

    Rooms are convex and each terrain fragment is planar, so its maximum
    elevation occurs at a clipped vertex.  This checks the whole physical floor
    polygon, including thresholds and slab edges beneath rear walls, rather
    than a sample grid or only the visible central portion of a room.
    """
    all_floor_points = [p for r in cutouts for p in r['polygon_xy']]
    bb = bounds(all_floor_points)
    query_bounds = (bb[0] - 1., bb[1] - 1., bb[2] + 1., bb[3] + 1.)
    original = before if isinstance(before, SurfaceIndex) else SurfaceIndex(before, query_bounds)
    modified = after if isinstance(after, SurfaceIndex) else SurfaceIndex(after, query_bounds)
    records, failures = [], []
    for room in cutouts:
        polygon = _ccw(room['polygon_xy'])
        old_faces = list(original.intersecting(polygon))
        new_faces = list(modified.intersecting(polygon))
        target_area = abs(area_xy(polygon))
        covered = sum(abs(area_xy(p)) for p in new_faces)
        if not old_faces or not new_faces:
            failures.append({'room_id': room['room_id'], 'reason': 'missing terrain support'})
            continue
        floor = float(room['floor_top_z'])
        old_max = max(p[2] for poly in old_faces for p in poly)
        new_max = max(p[2] for poly in new_faces for p in poly)
        row = {k: room[k] for k in ('building_id', 'room_id', 'kind', 'storey', 'floor_top_z')}
        row.update({'physical_floor_xy_m2': target_area, 'terrain_coverage_xy_m2': covered,
                    'maximum_original_terrain_z': old_max, 'maximum_final_terrain_z': new_max,
                    'original_height_above_floor_m': old_max - floor,
                    'final_height_above_floor_m': new_max - floor,
                    'minimum_final_floor_clearance_m': floor - new_max})
        wall_intrusions = modified.protruding_interior_walls(polygon, floor)
        row['vertical_terrain_intrusions'] = len(wall_intrusions)
        records.append(row)
        if new_max > floor + 1.e-7:
            failures.append({'room_id': room['room_id'], 'reason': 'terrain protrudes above physical floor',
                             'height_m': new_max - floor})
        if abs(covered - target_area) > 2.e-6:
            failures.append({'room_id': room['room_id'], 'reason': 'terrain coverage mismatch',
                             'area_difference_m2': covered - target_area})
        if wall_intrusions:
            failures.append({'room_id': room['room_id'], 'reason': 'vertical terrain face inside physical floor',
                             'walls': wall_intrusions})
    return {'method': 'Exact clipping of all actual main/context terrain faces against every complete physical floor polygon, including thresholds and wall-covered slab edges',
            'conservative_spatial_index_bounds_xy': query_bounds,
            'all_room_records': len(cutouts), 'checked_rooms': len(records),
            'first_storey_rooms': sum(r['storey'] == 0 for r in records),
            'original_intruding_rooms': sum(r['original_height_above_floor_m'] > 1.e-7 for r in records),
            'final_intruding_rooms': sum(r['final_height_above_floor_m'] > 1.e-7 for r in records),
            'vertical_terrain_faces_checked': len(modified.walls),
            'vertical_terrain_intrusions': sum(r['vertical_terrain_intrusions'] for r in records),
            'minimum_final_clearance_m': min(r['minimum_final_floor_clearance_m'] for r in records),
            'failures': failures, 'passed': not failures, 'rooms': records}
