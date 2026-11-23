"""Seat the existing service grates on actual already-built ground meshes.

Only this small fixture family uses this sampler.  No analytic ground-height
fallback is permitted.  The math is ordinary Python; Blender is imported only
when a production build snapshots evaluated scene meshes.
"""
from collections import defaultdict
from pathlib import Path
import array
import hashlib
import json
import math

SURFACE_PREFIXES = (
    'COL_Terrain_200m_', 'Outer_ground_context',
    'Urban_paving_joints_and_repairs_', 'COL_Road_', 'COL_Walk_',
    'COL_Community_court_', 'COL_Court_east_entry_steps_',
)
BASE_BOTTOM = -.0115
BASE_TOP = .0015
BAR_CENTER = .0065
BAR_RADIUS = .009
BAR_SIDES = 4
EPS = 1.e-9
AREA_EPS = 1.e-11
MAX_SURFACE_STEP = .002
MAX_NUMERIC_SEAM = .00001
MAX_AUTHORIZED_FOLD_STEP = .016
MAX_AUTHORIZED_BASE_FOLD_STEP = .018


class SupportError(RuntimeError):
    pass


def area(poly):
    if len(poly) < 3:
        return 0.
    origin = poly[0]
    return .5 * sum((a[0]-origin[0])*(b[1]-origin[1]) -
                    (a[1]-origin[1])*(b[0]-origin[0])
                    for a, b in zip(poly, poly[1:] + poly[:1]))


def clean(poly):
    result = []
    for p in poly:
        p = tuple(float(x) for x in p)
        if not result or math.dist(p, result[-1]) > 1.e-10:
            result.append(p)
    if len(result) > 1 and math.dist(result[0], result[-1]) <= 1.e-10:
        result.pop()
    return result if len(result) >= 3 and abs(area(result)) > AREA_EPS else []


def ccw(poly):
    p = clean(list(poly))
    return list(reversed(p)) if area(p) < 0 else p


def split(poly, signed):
    yes, no = [], []
    if not poly:
        return yes, no
    previous = poly[-1]
    previous_value = signed(previous)
    for current in poly:
        value = signed(current)
        if (value >= 0) != (previous_value >= 0):
            t = previous_value / (previous_value-value)
            q = tuple(a + t*(b-a) for a, b in zip(previous, current))
            yes.append(q); no.append(q)
        (yes if value >= 0 else no).append(current)
        previous, previous_value = current, value
    return clean(yes), clean(no)


def side(a, b, p):
    return (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0])


def intersect(subject, boundary):
    result = ccw(subject)
    clip = ccw(boundary)
    for a, b in zip(clip, clip[1:] + clip[:1]):
        result, _ = split(result, lambda p, a=a, b=b: side(a, b, p))
        if not result:
            break
    return result


def subtract(subject, convex_boundary):
    inside = ccw(subject)
    outside = []
    clip = ccw(convex_boundary)
    for a, b in zip(clip, clip[1:] + clip[:1]):
        inside, piece = split(inside, lambda p, a=a, b=b: side(a, b, p))
        if piece:
            outside.append(piece)
        if not inside:
            break
    return outside


def bbox(poly):
    return (min(p[0] for p in poly), min(p[1] for p in poly),
            max(p[0] for p in poly), max(p[1] for p in poly))


def overlaps(a, b):
    return not (a[2] < b[0]-EPS or b[2] < a[0]-EPS or
                a[3] < b[1]-EPS or b[3] < a[1]-EPS)


def plane(vertices):
    a, b, c = vertices
    ux, uy, uz = (b[i]-a[i] for i in range(3))
    vx, vy, vz = (c[i]-a[i] for i in range(3))
    nx, ny, nz = uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx
    if abs(nz) <= 1.e-10:
        return None
    return (-nx/nz, -ny/nz, (nx*a[0]+ny*a[1]+nz*a[2])/nz)


def z_on(coeff, p):
    return coeff[0]*p[0] + coeff[1]*p[1] + coeff[2]


def closest_boundary(poly, p):
    result = None
    for a, b in zip(poly, poly[1:] + poly[:1]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        length2 = dx*dx+dy*dy
        if length2 == 0:
            continue
        t = max(0., min(1., ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length2))
        q = (a[0]+t*dx, a[1]+t*dy)
        item = (math.dist(p, q), q)
        if result is None or item[0] < result[0]:
            result = item
    return result


def float32_half_ulp(value):
    value = abs(float(value))
    return math.ldexp(1., max(-149, math.frexp(value)[1]-24)-1) if value else math.ldexp(1., -150)


def numeric_seam_patch(gap, candidates):
    """Complete only a proven float32 T-junction seam between real surfaces.

    Keep the original positive missing area in metadata. A missing edge, a
    genuine hole, or height discontinuity is not eligible for this treatment.
    """
    widths = []
    for a, b in zip(gap, gap[1:] + gap[:1]):
        length = math.dist(a, b)
        if length:
            normal = (-(b[1]-a[1])/length, (b[0]-a[0])/length)
            width = max(abs(side(a, b, p))/length for p in gap)
            widths.append((width, normal))
    width, normal = min(widths, key=lambda value:value[0])
    ulp_bound = max(sum(abs(normal[i])*float32_half_ulp(p[i]) for i in range(2)) for p in gap)
    allowed = min(MAX_NUMERIC_SEAM, ulp_bound)
    if width > allowed or abs(area(gap)) <= AREA_EPS:
        return None
    center = tuple(sum(p[i] for p in gap)/len(gap) for i in range(2))
    nearby = []
    for _, triangle, _ in candidates:
        distance, q = closest_boundary(triangle['polygon_xy'], center)
        max_distance = max(closest_boundary(triangle['polygon_xy'], p)[0] for p in gap)
        if distance <= allowed and max_distance <= allowed:
            nearby.append((triangle, q, max_distance))
    for i, (first, qa, da) in enumerate(nearby):
        for second, qb, db in nearby[i+1:]:
            va = tuple(qa[k]-center[k] for k in range(2))
            vb = tuple(qb[k]-center[k] for k in range(2))
            lengths = math.hypot(*va)*math.hypot(*vb)
            if lengths <= 1.e-25 or sum(va[k]*vb[k] for k in range(2))/lengths > -.5:
                continue
            height_difference = max(abs(z_on(first['plane_z_coeff'], p)-z_on(second['plane_z_coeff'], p)) for p in gap)
            if height_difference > MAX_NUMERIC_SEAM:
                continue
            owner = first if z_on(first['plane_z_coeff'], center) >= z_on(second['plane_z_coeff'], center) else second
            return {'polygon_xy': gap, 'surface_name': owner['surface_name'],
                    'triangle_index': owner['triangle_index'], 'plane_z_coeff': owner['plane_z_coeff'],
                    'numeric_seam': {
                        'treatment': 'Extend one adjacent actual plane only across a measured float32 T-junction seam; ground itself is unchanged',
                        'original_missing_polygon_xy': gap, 'original_missing_area_m2': abs(area(gap)),
                        'maximum_strip_width_m': width, 'float32_half_ulp_normal_bound_m': ulp_bound,
                        'allowed_width_m': allowed, 'maximum_plane_extension_m': max(da, db),
                        'adjacent_plane_height_difference_m': height_difference,
                        'adjacent_surfaces': [{'surface_name': t['surface_name'], 'triangle_index': t['triangle_index']}
                                              for t in (first, second)],
                    }}
    return None


def authorized_fold(grate_id, building_id, edge_index, anchor_xy):
    return (grate_id == 'Drain_grate_101' and building_id == 'A05' and edge_index == 1 and
            math.dist(anchor_xy, (-28., -35.2)) <= 1.e-6)


def fold_surface_pair(first, second):
    names = (first['surface_name'], second['surface_name'])
    return (any(name.startswith('Urban_paving_joints_and_repairs_') for name in names) and
            all(name.startswith(('COL_Terrain_200m_', 'Urban_paving_joints_and_repairs_')) for name in names))


def common_edges(first, second):
    """Positive length portions of exactly shared convex-patch boundaries."""
    for a, b in zip(first, first[1:] + first[:1]):
        length = math.dist(a, b)
        if length <= 1.e-9:
            continue
        ux, uy = (b[0]-a[0])/length, (b[1]-a[1])/length
        for c, d in zip(second, second[1:] + second[:1]):
            if max(abs(side(a, b, p))/length for p in (c, d)) > 1.e-8:
                continue
            ends = sorted((p[0]-a[0])*ux+(p[1]-a[1])*uy for p in (c, d))
            lo, hi = max(0., ends[0]), min(length, ends[1])
            if hi-lo > 1.e-8:
                yield ((a[0]+ux*lo, a[1]+uy*lo), (a[0]+ux*hi, a[1]+uy*hi))


def append_step_folds(vertices, faces, patches, allowed):
    folds, seen = [], set()
    for i, first in enumerate(patches):
        for second in patches[i+1:]:
            for a, b in common_edges(first['polygon_xy'], second['polygon_xy']):
                deltas = [z_on(second['plane_z_coeff'], p)-z_on(first['plane_z_coeff'], p) for p in (a, b)]
                if max(abs(v) for v in deltas) <= MAX_SURFACE_STEP:
                    continue
                if (not allowed or not fold_surface_pair(first, second) or
                        max(abs(v) for v in deltas) > MAX_AUTHORIZED_BASE_FOLD_STEP or deltas[0]*deltas[1] < 0):
                    raise SupportError('A base plate crosses an unauthorized real ground step')
                key = tuple(sorted(tuple(round(v, 8) for v in p) for p in (a, b)))
                if key in seen:
                    continue
                seen.add(key)
                low, high = (first, second) if sum(deltas) > 0 else (second, first)
                thickness = BASE_TOP-BASE_BOTTOM
                gaps = [z_on(high['plane_z_coeff'], p)-z_on(low['plane_z_coeff'], p)-thickness for p in (a, b)]
                web_a, web_b = a, b
                if min(gaps) < 0 < max(gaps):
                    t = gaps[0]/(gaps[0]-gaps[1])
                    crossing = tuple(a[k]+t*(b[k]-a[k]) for k in range(2))
                    if gaps[0] < 0: web_a = crossing
                    else: web_b = crossing
                indices, web = [], []
                if max(gaps) > 1.e-9:
                    raw = [(*web_a,z_on(low['plane_z_coeff'],web_a)+BASE_TOP),
                           (*web_b,z_on(low['plane_z_coeff'],web_b)+BASE_TOP),
                           (*web_b,z_on(high['plane_z_coeff'],web_b)+BASE_BOTTOM),
                           (*web_a,z_on(high['plane_z_coeff'],web_a)+BASE_BOTTOM)]
                    for p in raw:
                        if not any(math.dist(p, q) <= 1.e-9 for q in web): web.append(p)
                    if len(web) >= 3:
                        start = len(vertices); vertices.extend(web)
                        face = tuple(start+k for k in range(len(web)))
                        if low is first: face = tuple(reversed(face))
                        indices.append(len(faces)); faces.append(face)
                folds.append({'edge_xy': [list(a),list(b)], 'step_height_m_range': [min(abs(v) for v in deltas),max(abs(v) for v in deltas)],
                              'low_surface_name': low['surface_name'], 'high_surface_name': high['surface_name'],
                              'low_plane_z_coeff': low['plane_z_coeff'], 'high_plane_z_coeff': high['plane_z_coeff'],
                              'construction': 'Existing thin plate sidewalls overlap, or a same-XY vertical web closes their remaining height interval',
                              'source_web_face_indices': indices, 'web_vertices_xyz': web,
                              'numeric_seam': False})
    return folds


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


def geometry_hash(vertices, faces):
    h = hashlib.sha256()
    h.update(array.array('d', (v for p in vertices for v in p)).tobytes())
    h.update(json.dumps(faces, separators=(',', ':')).encode())
    return h.hexdigest()


def line_interval(a, b, polygon):
    lo, hi = 0., 1.
    poly = ccw(polygon)
    for p, q in zip(poly, poly[1:] + poly[:1]):
        first, last = side(p, q, a), side(p, q, b)
        delta = last-first
        if abs(delta) <= 1.e-14:
            if first < -EPS:
                return None
            continue
        crossing = -first/delta
        if delta > 0:
            lo = max(lo, crossing)
        else:
            hi = min(hi, crossing)
        if hi-lo <= 1.e-10:
            return None
    lo, hi = max(0., lo), min(1., hi)
    return (lo, hi) if hi-lo > 1.e-10 else None


class ActualSurfaceSampler:
    def __init__(self, triangles, query_bounds=None, cell_size=1.):
        self.cell_size = cell_size
        self.triangles = []
        self.grid = defaultdict(list)
        all_xy = [p[:2] for t in triangles for p in t['vertices']]
        if not all_xy:
            raise SupportError('No evaluated ground triangles were supplied')
        self.query_bounds = tuple(query_bounds or bbox(all_xy))
        counts = defaultdict(int)
        for item in triangles:
            vertices = [tuple(float(v) for v in p) for p in item['vertices']]
            coeff = plane(vertices)
            poly = ccw([p[:2] for p in vertices])
            if coeff is None or not poly:
                continue
            bb = bbox(poly)
            if not overlaps(bb, self.query_bounds):
                continue
            record = {'polygon_xy': poly, 'plane_z_coeff': coeff, 'bounds': bb,
                      'surface_name': item['surface_name'],
                      'triangle_index': int(item.get('triangle_index', 0)),
                      'vertices': vertices}
            index = len(self.triangles)
            self.triangles.append(record)
            counts[item['surface_name']] += 1
            xmin, ymin = max(bb[0], self.query_bounds[0]), max(bb[1], self.query_bounds[1])
            xmax, ymax = min(bb[2], self.query_bounds[2]), min(bb[3], self.query_bounds[3])
            for x in range(math.floor((xmin-EPS)/cell_size), math.floor((xmax+EPS)/cell_size)+1):
                for y in range(math.floor((ymin-EPS)/cell_size), math.floor((ymax+EPS)/cell_size)+1):
                    self.grid[x, y].append(index)
        if not self.triangles:
            raise SupportError('No nonvertical evaluated ground intersects the grate region')
        self.snapshot = {
            'source_kind': 'actual_evaluated_mesh_triangles',
            'query_bounds_xy': list(self.query_bounds),
            'surface_triangle_counts': dict(sorted(counts.items())),
            'triangles_in_query_region': len(self.triangles),
            'geometry_sha256': canonical_hash(self.triangles),
            'analytic_ground_height_used': False,
        }

    @classmethod
    def from_triangles(cls, triangles, names=None, query_bounds=None):
        items = []
        for i, triangle in enumerate(triangles):
            if isinstance(triangle, dict):
                items.append(triangle)
            else:
                items.append({'vertices': triangle, 'surface_name': names[i] if names else 'fixture_ground',
                              'triangle_index': i})
        return cls(items, query_bounds=query_bounds)

    @classmethod
    def from_scene(cls, query_bounds):
        import bpy
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        triangles, objects = [], []
        for obj in sorted(bpy.context.scene.objects, key=lambda x: x.name):
            if obj.type != 'MESH' or not obj.name.startswith(SURFACE_PREFIXES):
                continue
            # Match the later export modifier after all existing bevels. Merely
            # calc_loop_triangles() may choose another non-planar quad diagonal.
            temporary = None
            if not obj.get('scanned_asset', False) and not obj.modifiers.get('Final_export_triangulation'):
                temporary = obj.modifiers.new('Drain_sampling_export_triangulation', 'TRIANGULATE')
                temporary.quad_method = 'BEAUTY'; temporary.ngon_method = 'BEAUTY'
                temporary.keep_custom_normals = True
            bpy.context.view_layer.update()
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                mesh.calc_loop_triangles()
                matrix = evaluated.matrix_world
                vertices = [tuple(matrix @ vertex.co) for vertex in mesh.vertices]
                count = len(mesh.loop_triangles)
                objects.append({'name': obj.name, 'evaluated_triangles': count,
                                'matrix_world_rows': [list(row) for row in matrix],
                                'modifier_types': [modifier.type for modifier in obj.modifiers],
                                'sampling_triangulation': 'Equivalent final BEAUTY/BEAUTY modifier after existing geometry modifiers',
                                'temporary_modifier_removed_after_read': temporary is not None})
                for i, triangle in enumerate(mesh.loop_triangles):
                    points = [vertices[j] for j in triangle.vertices]
                    if overlaps(bbox([p[:2] for p in points]), query_bounds):
                        triangles.append({'vertices': points, 'surface_name': obj.name, 'triangle_index': i})
            finally:
                evaluated.to_mesh_clear()
                if temporary is not None:
                    obj.modifiers.remove(temporary)
                    bpy.context.view_layer.update()
        sampler = cls(triangles, query_bounds=query_bounds)
        sampler.snapshot['source_kind'] = 'already_built_blender_evaluated_mesh'
        sampler.snapshot['surface_objects'] = objects
        sampler.snapshot['surface_prefixes'] = list(SURFACE_PREFIXES)
        return sampler

    def candidates(self, footprint):
        bb = bbox(footprint)
        if (bb[0] < self.query_bounds[0]-EPS or bb[1] < self.query_bounds[1]-EPS or
                bb[2] > self.query_bounds[2]+EPS or bb[3] > self.query_bounds[3]+EPS):
            raise SupportError('Grate footprint is outside the evaluated sampler region')
        ids = set()
        for x in range(math.floor((bb[0]-EPS)/self.cell_size), math.floor((bb[2]+EPS)/self.cell_size)+1):
            for y in range(math.floor((bb[1]-EPS)/self.cell_size), math.floor((bb[3]+EPS)/self.cell_size)+1):
                ids.update(self.grid.get((x, y), ()))
        return sorted(i for i in ids if overlaps(bb, self.triangles[i]['bounds']))

    def surface_patches(self, footprint):
        footprint = ccw(footprint)
        if not footprint:
            raise SupportError('Empty or degenerate grate footprint')
        candidates = []
        for index in self.candidates(footprint):
            triangle = self.triangles[index]
            poly = intersect(footprint, triangle['polygon_xy'])
            if poly:
                candidates.append((index, triangle, poly))
        patches = []
        for index, triangle, poly in candidates:
            pieces = [poly]
            for other_index, other, other_poly in candidates:
                if other_index == index or not pieces or not overlaps(bbox(poly), bbox(other_poly)):
                    continue
                region = intersect(poly, other_poly)
                if not region:
                    continue
                delta = tuple(other['plane_z_coeff'][i]-triangle['plane_z_coeff'][i] for i in range(3))
                values = [z_on(delta, p) for p in region]
                if max(abs(v) for v in values) <= 1.e-8:
                    dominant = region if other_index < index else []
                elif max(values) <= 0:
                    dominant = []
                else:
                    dominant, _ = split(region, lambda p, delta=delta: z_on(delta, p))
                if dominant:
                    pieces = [part for piece in pieces for part in subtract(piece, dominant)]
            for piece in pieces:
                patches.append({'polygon_xy': piece, 'surface_name': triangle['surface_name'],
                                'triangle_index': triangle['triangle_index'],
                                'plane_z_coeff': triangle['plane_z_coeff']})
        requested = abs(area(footprint))
        covered = sum(abs(area(p['polygon_xy'])) for p in patches)
        if covered < requested-1.e-8:
            missing = [footprint]
            # First determine missing *actual projected support*, independent
            # of the highest-surface partition. Never hide a clipping failure.
            for _, _, candidate_polygon in candidates:
                missing = [piece for region in missing for piece in subtract(region, candidate_polygon)]
            if abs(sum(abs(area(gap)) for gap in missing)-(requested-covered)) <= 1.e-8:
                repaired = [numeric_seam_patch(gap, candidates) for gap in missing]
                if repaired and all(p is not None for p in repaired):
                    patches.extend(repaired)
                    covered = sum(abs(area(p['polygon_xy'])) for p in patches)
        if abs(covered-requested) > max(1.e-8, requested*1.e-7):
            raise SupportError('Actual highest surfaces do not cover the complete grate: %.12g of %.12g m2' % (covered, requested))
        return patches

    def line_profile(self, patches, a, b, explicit_fold=False):
        intervals = []
        for patch in patches:
            interval = line_interval(a, b, patch['polygon_xy'])
            if interval:
                intervals.append((*interval, patch))
        cuts = sorted(set(round(t, 12) for lo, hi, _ in intervals for t in (lo, hi)))
        if not cuts or cuts[0] > 1.e-8 or cuts[-1] < 1.-1.e-8:
            raise SupportError('A complete bar line has no actual ground support')
        segments = []
        for lo, hi in zip(cuts, cuts[1:]):
            if hi-lo <= 1.e-10:
                continue
            mid = (lo+hi)*.5
            available = [p for start, end, p in intervals if start-1.e-9 <= mid <= end+1.e-9]
            if not available:
                raise SupportError('An interior bar interval is unsupported')
            xy_mid = tuple(a[i]+mid*(b[i]-a[i]) for i in range(2))
            patch = max(available, key=lambda p:z_on(p['plane_z_coeff'], xy_mid))
            xy_a = tuple(a[i]+lo*(b[i]-a[i]) for i in range(2))
            xy_b = tuple(a[i]+hi*(b[i]-a[i]) for i in range(2))
            p_a = (*xy_a, z_on(patch['plane_z_coeff'], xy_a)+BAR_CENTER)
            p_b = (*xy_b, z_on(patch['plane_z_coeff'], xy_b)+BAR_CENTER)
            if segments and abs(p_a[2]-segments[-1]['b_xyz'][2]) > MAX_SURFACE_STEP:
                step = abs(p_a[2]-segments[-1]['b_xyz'][2])
                previous = segments[-1]
                if not explicit_fold or step > MAX_AUTHORIZED_FOLD_STEP or not fold_surface_pair(previous, patch):
                    raise SupportError('Grate bar crosses a real ground height step of %.6gm; no floating interpolation is allowed' % step)
                segments.append({'a_xyz': list(previous['b_xyz']), 'b_xyz': list(p_a),
                                 'role': 'vertical_riser', 'surface_name': patch['surface_name'],
                                 'triangle_index': patch['triangle_index'],
                                 'from_surface_name': previous['surface_name'], 'to_surface_name': patch['surface_name'],
                                 'ground_step_m': step, 'allowed_explicit_step': True,
                                 'from_segment_index': len(segments)-1, 'to_segment_index': len(segments)+1})
            if (segments and segments[-1]['surface_name'] == patch['surface_name'] and
                    segments[-1].get('role') != 'vertical_riser' and
                    segments[-1]['triangle_index'] == patch['triangle_index'] and
                    abs(p_a[2]-segments[-1]['b_xyz'][2]) < 1.e-8):
                segments[-1]['b_xyz'] = list(p_b)
            else:
                segments.append({'a_xyz': list(p_a), 'b_xyz': list(p_b),
                                 'role': 'ground_following',
                                 'surface_name': patch['surface_name'],
                                 'triangle_index': patch['triangle_index']})
        return segments


def base_mesh(patches):
    vertices, faces = [], []
    for patch in patches:
        poly = ccw(patch['polygon_xy'])
        n = len(poly); start = len(vertices)
        vertices.extend((p[0], p[1], z_on(patch['plane_z_coeff'], p)+BASE_BOTTOM) for p in poly)
        vertices.extend((p[0], p[1], z_on(patch['plane_z_coeff'], p)+BASE_TOP) for p in poly)
        faces.append(tuple(start+i for i in reversed(range(n))))
        faces.append(tuple(start+n+i for i in range(n)))
        for i in range(n):
            j = (i+1) % n
            faces.append((start+i, start+j, start+n+j, start+n+i))
    return vertices, faces


def plan_grate(sampler, grate_id, building_id, building_index, edge_index,
               anchor_xy, tangent_xy, outward_xy, footprint_xy, bar_lines):
    try:
        patches = sampler.surface_patches(footprint_xy)
    except SupportError as error:
        raise SupportError('%s / building %s edge %s: %s' %
                           (grate_id, building_id, edge_index, error)) from error
    vertices, faces = base_mesh(patches)
    explicit_fold = authorized_fold(grate_id, building_id, edge_index, anchor_xy)
    folds = append_step_folds(vertices, faces, patches, explicit_fold)
    bars = []
    for i, (a, b) in enumerate(bar_lines):
        segments = sampler.line_profile(patches, a, b, explicit_fold=explicit_fold)
        centerline = [segments[0]['a_xyz']] + [s['b_xyz'] for s in segments]
        bars.append({'index': i, 'line_xy': [list(a), list(b)],
                     'centerline_xyz': centerline, 'segments': segments,
                     'radius_m': BAR_RADIUS, 'sides': BAR_SIDES,
                     'center_offset_m': BAR_CENTER})
    record = {
        'grate_id': grate_id, 'building_id': building_id,
        'building_index': building_index, 'edge_index': edge_index,
        'anchor_xy': list(anchor_xy), 'tangent_xy': list(tangent_xy), 'outward_xy': list(outward_xy),
        'footprint_xy': [list(p) for p in footprint_xy],
        'mesh_names': {'base': grate_id+'_dark', 'bars': grate_id+'_frame'},
        'base': {'bottom_offset_m': BASE_BOTTOM, 'top_offset_m': BASE_TOP,
                 'thickness_m': BASE_TOP-BASE_BOTTOM, 'vertex_count': len(vertices),
                 'face_count': len(faces), 'geometry_sha256': geometry_hash(vertices, faces),
                 'step_folds': folds},
        'explicit_step_authorization': {'allowed': explicit_fold, 'maximum_bar_riser_step_m': MAX_AUTHORIZED_FOLD_STEP,
                                        'maximum_base_fold_step_m': MAX_AUTHORIZED_BASE_FOLD_STEP,
                                        'scope': 'Only Drain_grate_101 / A05 edge1 anchor(-28,-35.2), measured existing paving boundary; never a numerical seam'},
        'bars': bars,
        'support': {'surface_names': sorted(set(p['surface_name'] for p in patches)),
                    'footprint_area_m2': abs(area(list(footprint_xy))),
                    'covered_area_m2': sum(abs(area(p['polygon_xy'])) for p in patches),
                    'raw_covered_area_m2': sum(abs(area(p['polygon_xy'])) for p in patches if 'numeric_seam' not in p),
                    'numerical_seam_area_m2': sum(abs(area(p['polygon_xy'])) for p in patches if 'numeric_seam' in p),
                    'numerical_seam_repairs': [p['numeric_seam'] for p in patches if 'numeric_seam' in p],
                    'patches': patches, 'coverage_failures': [], 'analytic_ground_height_used': False},
        'source_geometry_passed': True,
    }
    return record, vertices, faces


def add_grate(batch, plan):
    record, vertices, faces = plan
    batch.mesh(vertices, faces, 'dark')
    for bar in record['bars']:
        for segment in bar['segments']:
            batch.cylinder(segment['a_xyz'], segment['b_xyz'], BAR_RADIUS, 'frame', BAR_SIDES)
    frame_vertices, frame_faces, _ = batch.data['frame']
    record['bar_geometry'] = {
        'vertex_count': len(frame_vertices), 'face_count': len(frame_faces),
        'geometry_sha256': geometry_hash(frame_vertices, frame_faces),
    }
    objects = batch.finish()
    for obj in objects:
        obj['drain_grate_id'] = record['grate_id']
        obj['drain_part_role'] = 'base' if obj.name.endswith('_dark') else 'bars'
        obj['drain_support_kind'] = 'actual_evaluated_ground_mesh'
    record['generated_object_names'] = [obj.name for obj in objects]
    return record


def record_curb_relocation(sampler, record, old_anchor, old_footprint):
    """Audit the sole authorized 17 cm cover move, keeping its wall fixture."""
    if not (record['grate_id'] == 'Drain_grate_041' and record['building_id'] == 809889629 and record['edge_index'] == 1):
        raise SupportError('The curb-clearance placement exception was used on another grate')
    delta = [record['anchor_xy'][i]-old_anchor[i] for i in range(2)]
    if not .16999 <= math.hypot(*delta) <= .17001:
        raise SupportError('The measured curb-clearance move must remain 17 cm')
    if record['support']['surface_names'] != ['COL_Road_734116597_0_asphalt']:
        raise SupportError('The moved cover is not entirely on its measured asphalt surface')
    footprint = record['footprint_xy']; bb = bbox(footprint)
    query = [(bb[0]-.1,bb[1]-.1),(bb[2]+.1,bb[1]-.1),(bb[2]+.1,bb[3]+.1),(bb[0]-.1,bb[3]+.1)]
    clearance = None
    for index in sampler.candidates(query):
        triangle = sampler.triangles[index]
        if 'curb' not in triangle['surface_name']:
            continue
        poly = triangle['polygon_xy']
        distance = (0. if intersect(footprint, poly) else
                    min([closest_boundary(poly,p)[0] for p in footprint]+
                        [closest_boundary(footprint,p)[0] for p in poly]))
        clearance = distance if clearance is None else min(clearance,distance)
    if clearance is None or clearance < .01:
        raise SupportError('The moved cover does not retain a measured 1 cm visible margin from the kerb')
    line_margin = min(closest_boundary(footprint,p)[0] for b in record['bars'] for p in b['line_xy'])
    if line_margin-BAR_RADIUS < .01:
        raise SupportError('A complete moved bar section extends beyond the cover margin')
    record['placement_adjustment'] = {
        'kind': 'sole_measured_curb_clearance_041', 'original_anchor_xy': list(old_anchor),
        'new_anchor_xy': record['anchor_xy'], 'delta_xy': delta, 'distance_m': math.hypot(*delta),
        'maximum_authorized_distance_m': .25, 'original_footprint_xy': [list(p) for p in old_footprint],
        'new_footprint_xy': footprint, 'actual_support_surface_names': record['support']['surface_names'],
        'minimum_curb_projection_clearance_m': clearance, 'minimum_required_curb_margin_m': .01,
        'minimum_complete_bar_section_footprint_margin_m': line_margin-BAR_RADIUS,
        'wall_fixture_anchor_unchanged': True,
        'reason': 'Original footprint climbed an actual 120.907 mm bevelled road kerb; only this cover moves along the facade outward normal onto the same asphalt plane',
    }


def write_audit(path, revision, records, sampler):
    if path is None:
        return
    root = Path(__file__).resolve().parent
    source_files = ['drain_support.py', 'urban_fabric.py', 'district_geometry.py']
    failures = []
    if not records or len({r['grate_id'] for r in records}) != len(records):
        failures.append('No grate records or duplicate grate identifiers')
    for r in records:
        if len(r['bars']) != 13 or not all(b['segments'] for b in r['bars']):
            failures.append(r['grate_id']+': incomplete thirteen-bar geometry')
        if set(r.get('generated_object_names', [])) != set(r['mesh_names'].values()):
            failures.append(r['grate_id']+': actual generated base/bar object names do not match')
    result = {
        'schema_version': 1, 'revision': revision, 'passed': not failures,
        'status': 'PASS_SOURCE_BUILT_SURFACE_FIT' if not failures else 'FAIL_SOURCE_BUILT_SURFACE_FIT',
        'source_kind': 'already_built_blender_mesh',
        'fresh_glb_measurement': False,
        'scope': 'All service grates generated by urban_fabric.micro_dressing; 111 retain XY and only041 has the measured 17 cm kerb-clearance move',
        'grate_count': len(records), 'bar_count': sum(len(r['bars']) for r in records),
        'source_sha256': {f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in source_files},
        'surface_snapshot': sampler.snapshot,
        'construction': {'base_bottom_offset_m': BASE_BOTTOM, 'base_top_offset_m': BASE_TOP,
                         'bar_center_offset_m': BAR_CENTER, 'bar_radius_m': BAR_RADIUS,
                         'maximum_allowed_surface_step_m': MAX_SURFACE_STEP,
                         'sole_101_bar_riser_limit_m': MAX_AUTHORIZED_FOLD_STEP,
                         'sole_101_base_fold_limit_m': MAX_AUTHORIZED_BASE_FOLD_STEP,
                         'numeric_seam_limit_m': MAX_NUMERIC_SEAM,
                         'numeric_seam_additional_limit': 'Actual float32 half-ULP bound projected on the measured seam normal',
                         'missing_support_policy': 'Raise SupportError and abort build; no analytic fallback'},
        'records': records, 'failures': failures,
        'limits': ['Source/built-mesh placement audit, not an exported-GLB clearance measurement.',
                   'New exported base and bar geometry must pass the independent actual-GLB checker.',
                   '%d grates add %d individually named material meshes; no separate optimization is attempted.' % (len(records),len(records)*2)],
    }
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    if failures:
        raise SupportError('; '.join(failures))

