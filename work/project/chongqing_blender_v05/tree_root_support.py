"""Seat the existing island-tree scan's cut base below its unchanged soil.

The small geometry file comes from the prepared hero stem, in normalized
Blender metres.  It is tied to the unchanged prepared-library SHA.  Only the
tree instance's vertical translation changes; the terrain and tree well do
not.  Every source base face is split at the existing terrain triangle edges
so the reported burial clearance is an extremum over real faces, not a root
radius guess.  The higher stem band establishes an actual soil contact line.
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import math
import random


@lru_cache(maxsize=None)
def _geometry(root):
    root = Path(root)
    profile = json.loads((root / 'scanned_assets/tree_root_geometry.json').read_text())
    library = root / 'scanned_assets/prepared_assets.blend'
    digest = hashlib.sha256()
    with library.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    if digest.hexdigest() != profile['source_library_sha256']:
        raise ValueError('Island-tree root geometry does not match the prepared model library')
    if profile['source_object'] != 'PH_island_tree_01_hero_01':
        raise ValueError('Root fitting requires the verified hero island-tree stem')
    return profile


def _clip(poly, signed):
    """Keep 3-D polygon coordinates, including vertical projected edges."""
    result = []
    if not poly:
        return result
    for a, b in zip(poly, poly[1:] + poly[:1]):
        da, db = signed(a), signed(b)
        if da >= 0.:
            result.append(a)
        if (da < 0. <= db) or (db < 0. <= da):
            t = da / (da - db)
            result.append(tuple(a[k] + (b[k] - a[k]) * t for k in range(3)))
    return result


def _terrain_pieces(poly):
    """Intersect a root face with each of the unchanged 1 m terrain planes."""
    lo = [math.floor(min(p[k] for p in poly)) for k in (0, 1)]
    hi = [math.floor(max(p[k] for p in poly)) for k in (0, 1)]
    for ix in range(lo[0], hi[0] + 1):
        for iy in range(lo[1], hi[1] + 1):
            cell = poly
            for axis, bound, sign in ((0, ix, 1), (0, ix + 1, -1),
                                      (1, iy, 1), (1, iy + 1, -1)):
                cell = _clip(cell, lambda p, a=axis, b=bound, s=sign: s * (p[a] - b))
            if not cell:
                continue
            for sign in (1, -1):
                part = _clip(cell, lambda p, s=sign: s * ((p[0] - ix) - (p[1] - iy)))
                if part:
                    yield part


def fit_island_base(root, point, height, seed, reference_z, surface_height,
                    soil_distance, soil_lift):
    profile = _geometry(str(Path(root)))
    factor = height / profile['source_height_m']
    angle = random.Random(seed).random() * math.tau
    cs, sn = math.cos(angle), math.sin(angle)

    def transform(p):
        return (point[0] + factor * (cs * p[0] - sn * p[1]),
                point[1] + factor * (sn * p[0] + cs * p[1]), factor * p[2])

    def pieces(vertices, triangles):
        vv = [transform(p) for p in vertices]
        for face in triangles:
            yield from _terrain_pieces([vv[i] for i in face])

    base = list(pieces(profile['vertices'], profile['triangles']))
    # The scan has a few genuine open boundary edges rising above the .13 m
    # skirt band.  Bury those real cut edges as well, rather than hiding only
    # the horizontal base patch and leaving a sliced stem edge exposed.
    boundary = [transform(p) for p in profile['boundary_vertices']]
    for edge in profile['boundary_edges']:
        base.extend(_terrain_pieces([boundary[i] for i in edge]))
    samples = {tuple(p) for poly in base for p in poly}
    if not samples:
        raise ValueError('No actual island-tree scan-base faces to fit')
    clearance = .012
    target_z = min(surface_height(p[0], p[1]) + soil_lift - p[2] - clearance
                   for p in samples)
    origin_z = min(reference_z, target_z)
    before = max(reference_z + p[2] - surface_height(p[0], p[1]) - soil_lift
                 for p in samples)
    after = max(origin_z + p[2] - surface_height(p[0], p[1]) - soil_lift
                for p in samples)

    contacts = set()
    top_witness = -math.inf
    contact_pieces = 0
    for poly in pieces(profile['contact_vertices'], profile['contact_triangles']):
        values = [origin_z + p[2] - surface_height(p[0], p[1]) - soil_lift for p in poly]
        top_witness = max(top_witness, max(values))
        if min(values) > 0. or max(values) < 0.:
            continue
        contact_pieces += 1
        for a, b, da, db in zip(poly, poly[1:] + poly[:1], values, values[1:] + values[:1]):
            if abs(da) < 1.e-10:
                contacts.add((a[0], a[1]))
            if da * db < 0.:
                t = da / (da - db)
                contacts.add((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    if after > -clearance + 1.e-8 or not contacts or top_witness < .05:
        raise ValueError('Island-tree base is not buried with an emerging stem')
    contact_margin = min(-soil_distance(p) for p in contacts)
    if contact_margin < .02:
        raise ValueError('The island-tree visible soil contact reaches outside its existing planting area')
    support = {
        'method': 'Actual hero scan-base triangles below the unchanged slope-fitted soil; only instance Z changes',
        'source_object': profile['source_object'],
        'source_library_sha256': profile['source_library_sha256'],
        'source_base_height_limit_m': profile['base_z_max_m'],
        'source_base_triangles': len(profile['triangles']),
        'source_open_base_edges': len(profile['boundary_edges']),
        'source_open_base_maximum_z_m': max(p[2] for p in profile['boundary_vertices']),
        'source_contact_band_triangles': len(profile['contact_triangles']),
        'placed_scale': factor,
        'soil_overlay_lift_m': soil_lift,
        'nominal_asset_height_m': height,
        'instance_origin_z_m': origin_z,
        'reference_origin_z_m': reference_z,
        'additional_burial_m': reference_z - origin_z,
        'origin_below_center_soil_m': surface_height(*point) + soil_lift - origin_z,
        'maximum_scan_base_above_soil_before_m': before,
        'maximum_scan_base_above_soil_after_m': after,
        'minimum_scan_base_burial_m': -after,
        'base_projected_radius_m': max(math.dist(point, p[:2]) for p in samples),
        'base_terrain_plane_extrema': len(samples),
        'contact_surface_pieces': contact_pieces,
        'contact_point_count': len(contacts),
        'minimum_visible_contact_soil_margin_m': contact_margin,
        'stem_band_above_soil_witness_m': top_witness,
        'actual_contact_xy': [list(p) for p in sorted(contacts)],
        'actual_base_terrain_samples_xy': [list(p) for p in sorted({p[:2] for p in samples})],
        'point_meaning': 'The recorded point is the buried asset origin, not a claim that the origin lies on the soil surface',
    }
    return origin_z, support
