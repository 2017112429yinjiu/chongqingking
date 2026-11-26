"""Fit a playable park terrace and two approaches into the existing game grade."""
from dataclasses import dataclass
import json
from math import ceil, cos, sin
from pathlib import Path
import sys
from typing import Callable

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
SCENES = HERE.parents[2]
sys.path.insert(0, str(SCENES / 'district_500'))
from interior_terrain import clip_polygon
from riverside import material, strip

ASSETS = SCENES.parent / 'project/chongqing_godot_v05/assets/district_500'
TILES = ('COL_Outer500_Surface_01_01', 'COL_Outer500_Surface_02_01')
FURNITURE = 'Outer500_Street_furniture'
MATIX_SOURCE = HERE.parents[1] / 'street_groups/matix/matix_streets.blend'
CENTRE = Vector((-145.7, -184.0))
BEARING = -.15
LEVEL = -5.83
EPS = 1e-5


def cross(a, b):
    return a.x * b.y - a.y * b.x


def area(ring):
    return .5 * sum(cross(a, b) for a, b in zip(ring, ring[1:] + ring[:1]))


def bounds(ring):
    return tuple((min(p[i] for p in ring), max(p[i] for p in ring)) for i in (0, 1))


def intersects(a, b):
    return all(lo <= end + EPS and start <= hi + EPS for (lo, hi), (start, end) in zip(a, b))


def octagon(half_width, half_depth, corner):
    w, d = half_width, half_depth
    return [site(x, y) for x, y in [(-w + corner, -d), (w - corner, -d), (w, -d + corner), (w, d - corner),
                                  (w - corner, d), (-w + corner, d), (-w, d - corner), (-w, -d + corner)]]


def site(u, v):
    return CENTRE + Vector((u * cos(BEARING) - v * sin(BEARING), u * sin(BEARING) + v * cos(BEARING)))


@dataclass
class Patch:
    name: str
    ring: list
    grade: Callable
    material: int

    def __post_init__(self):
        assert area(self.ring) > 0, self.name
        self.bounds = bounds(self.ring)
        self.edges = [(a, Vector((a.y - b.y, b.x - a.x)).normalized())
                      for a, b in zip(self.ring, self.ring[1:] + self.ring[:1])]

    def includes(self, point):
        return all(normal.dot(point - start) >= -EPS for start, normal in self.edges)

    def on_edge(self, a, b):
        return any(max(abs(normal.dot(a - start)), abs(normal.dot(b - start))) < EPS * 5
                   for start, normal in self.edges)

    def partition(self, polygon):
        pieces = []
        for start, normal in self.edges:
            polygon, outside = clip_polygon(polygon, lambda p: normal.dot(p.xy - start))
            if area(outside) > EPS:
                pieces.append(outside)
            if area(polygon) <= EPS:
                return [], []
        return polygon, pieces


class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.indices = []

    def face(self, points, material_index, vertical=False):
        points = [p for i, p in enumerate(points) if (p - points[i - 1]).length > EPS]
        if len(points) < 3:
            return
        origin = len(self.vertices)
        self.vertices.extend(points)
        self.faces.append(tuple(range(origin, origin + len(points))))
        self.indices.append((material_index, vertical))

    def make(self, name, materials, original=None):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(self.vertices, [], self.faces)
        for finish in materials:
            mesh.materials.append(finish)
        uv = mesh.uv_layers.new()
        for face, (slot, vertical) in zip(mesh.polygons, self.indices):
            face.material_index = slot
            axis = 1 if vertical and abs(face.normal.x) > abs(face.normal.y) else 0
            for i in face.loop_indices:
                point = self.vertices[mesh.loops[i].vertex_index]
                uv.data[i].uv = (point[axis] / 2.4, (point.z if vertical else point.y) / 2.4)
        if original is not None:
            original.data = mesh
            return original
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return obj


def xyz(point, elevation):
    return Vector((point.x, point.y, elevation))


def trail_join(east):
    plan = json.loads((ASSETS / 'riverside.json').read_bytes())
    route = next(r for r in plan['routes'] if r['id'] == 'upper_promenade')
    points = [Vector((e, n, 0)) for e, n in route['points']]
    # End inside the north stone border by 12 cm to share the walkable paving.
    edge = -route['width_m'] * .5 + .12
    for polygon in strip(points, 0., edge):
        a, b = polygon[3].xy, polygon[2].xy
        if a.x <= east <= b.x:
            return a.lerp(b, (east - a.x) / (b.x - a.x))
    raise ValueError(f'No north edge at {east} m')


def approaches(ground):
    west = (trail_join(-159.1), trail_join(-156.7), site(-4, -6.4), site(-6.4, -6.4))
    east = (trail_join(-137.1), trail_join(-134.5), site(6.4, -6.4), site(3.8, -6.4))

    def incline(quad, end_height):
        a, b, c, d = quad
        base, high = (b - a).normalized(), (c - d).normalized()

        def grade(p):
            rise = max(0., cross(base, p - a))
            fall = max(0., cross(high, c - p))
            start = a + base * min((b - a).length, max(0., (p - a).dot(base)))
            initial = ground(start)
            return initial + (end_height - initial) * rise / (rise + fall)

        return grade

    a, b, c, d = west
    shoulder_a, shoulder_b = a.lerp(d, .12), b.lerp(c, .12)
    shoulder_grade = (ground(shoulder_a) + ground(shoulder_b)) * .5
    count = ceil((LEVEL - shoulder_grade) / .156)
    west_patches = [Patch('west_landing', [a, b, shoulder_b, shoulder_a],
                          incline((a, b, shoulder_b, shoulder_a), shoulder_grade), 0)]
    for i in range(count):
        lo, hi = i / count, (i + 1) / count
        level = shoulder_grade + (LEVEL - shoulder_grade) * hi
        west_patches.append(Patch(f'tread_{i + 1:02d}', [shoulder_a.lerp(d, lo), shoulder_b.lerp(c, lo),
                                                        shoulder_b.lerp(c, hi), shoulder_a.lerp(d, hi)],
                                  lambda p, h=level: h, 0))
    ramp = Patch('east_ramp', list(east), incline(east, LEVEL), 0)
    mid = lambda a, b: (a + b) * .5
    return west_patches, ramp, mid(a, b), mid(d, c), mid(east[0], east[1]), mid(east[3], east[2]), shoulder_grade, count


def retaining(edges, a, b, low_a, low_b, top_a, top_b, slot):
    da, db = top_a - low_a, top_b - low_b
    if max(abs(da), abs(db)) < EPS:
        return
    if da * db < 0:
        t = da / (da - db)
        joint = a.lerp(b, t)
        z = low_a + t * (low_b - low_a)
        edges.face([xyz(a, low_a), xyz(joint, z), xyz(a, top_a)], slot, True)
        edges.face([xyz(joint, z), xyz(b, low_b), xyz(b, top_b)], slot, True)
    else:
        edges.face([xyz(a, low_a), xyz(b, low_b), xyz(b, top_b), xyz(a, top_a)], slot, True)



def build_retaining_edge(walls, patch, patches, a, b):
    horizontal = b.xy - a.xy
    length = horizontal.length
    if length < EPS or not patch.on_edge(a.xy, b.xy):
        return
    tangent = horizontal / length
    splits = {0., 1.}
    for other in patches:
        if other is patch or not intersects(bounds([a, b]), other.bounds):
            continue
        for p in other.ring:
            distance = (p - a.xy).dot(tangent)
            if EPS < distance < length - EPS and abs(cross(tangent, p - a.xy)) < EPS * 5:
                splits.add(distance / length)
    cuts = sorted(splits)
    for start, finish in zip(cuts, cuts[1:]):
        p, q = a.lerp(b, start), a.lerp(b, finish)
        mid = (p.xy + q.xy) * .5
        neighbor = next((other for other in patches if other is not patch and other.includes(mid)), None)
        if neighbor and patch.grade(mid) <= neighbor.grade(mid) + EPS:
            continue
        base_p, base_q = (neighbor.grade(p.xy), neighbor.grade(q.xy)) if neighbor else (p.z, q.z)
        retaining(walls, p.xy, q.xy, base_p, base_q, patch.grade(p.xy), patch.grade(q.xy), 1)


def rim(mesh):
    def beam(u0, u1, v0, v1, lo, hi, material_index):
        ring = [site(u, v) for u, v in [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]]
        mesh.face([xyz(p, hi) for p in ring], material_index)
        for a, b in zip(ring, ring[1:] + ring[:1]):
            mesh.face([xyz(a, lo), xyz(b, lo), xyz(b, hi), xyz(a, hi)], material_index, True)

    # The two openings stay aligned with the ramp and stair clear widths.
    for left, right in [(-7.19, -6.46), (-3.94, 3.74), (6.46, 7.19)]:
        beam(left, right, -6.39, -6.22, LEVEL, LEVEL + .23, 1)
        beam(left, right, -6.34, -6.26, LEVEL + .94, LEVEL + 1., 3)
        rail_count = ceil((right - left) / .18)
        for i in range(rail_count):
            u = left + (i + .5) * (right - left) / rail_count
            beam(u - .019, u + .019, -6.33, -6.27, LEVEL + .22, LEVEL + .95, 3)

def build_terrain(tiles, patches, path, walls):
    objects = []
    support = {patch.name: 0. for patch in patches}
    for tile in tiles:
        old = tile.data
        terrain = Mesh()
        vertices = [v.co.copy() for v in old.vertices]
        changed = False
        for face in old.polygons:
            polygon = [vertices[i] for i in face.vertices]
            box = bounds(polygon)
            remaining = [polygon]
            for patch in patches:
                if not intersects(box, patch.bounds):
                    continue
                new = []
                for piece in remaining:
                    inside, outside = patch.partition(piece)
                    if not inside:
                        new.append(piece)
                        continue
                    changed = True
                    support[patch.name] += area(inside)
                    new.extend(outside)
                    graded = [patch.grade(p.xy) for p in inside]
                    path.face([xyz(p.xy, h) for p, h in zip(inside, graded)], patch.material)
                    for a, b in zip(inside, inside[1:] + inside[:1]):
                        build_retaining_edge(walls, patch, patches, a, b)
                remaining = new
            for piece in remaining:
                terrain.face(piece, face.material_index)
        if changed:
            objects.append(terrain.make(tile.name + '_CourtCut', old.materials[:], tile))
    for patch in patches:
        assert abs(support[patch.name] - area(patch.ring)) < .018, (patch.name, support[patch.name], area(patch.ring))
    return objects, support



def fit_lamp(ground, patches):
    # The reverse camera hits the original 18-face lamp at this registered root.
    old = Vector((-145.74298, -182.67073, -5.4584))
    current = Vector((-131.7, -198.25))
    assert patches[0].includes(old.xy) and not any(p.includes(current) for p in patches)

    bpy.data.objects.remove(bpy.data.objects[FURNITURE], do_unlink=True)
    with bpy.data.libraries.load(str(MATIX_SOURCE), link=False) as (source, local):
        assert FURNITURE in source.objects
        local.objects = [FURNITURE]
    obj = local.objects[0]
    assert obj.name == FURNITURE
    bpy.context.scene.collection.objects.link(obj)
    mesh = obj.data
    corners = [vertex.co for vertex in mesh.vertices]
    selected = [face for face in mesh.polygons if all(
        abs(corners[i].x - old.x) < .4 and abs(corners[i].y - old.y) < .42
        and old.z - .001 <= corners[i].z <= old.z + 4.881 for i in face.vertices)]
    assert len(selected) == 18
    assert all(len(face.vertices) == 4 for face in selected)
    vertices = {i for face in selected for i in face.vertices}
    assert sum(any(i in vertices for i in face.vertices) for face in mesh.polygons) == len(selected)
    z = min(corners[i].z for i in vertices)
    assert abs(z - old.z) < .001
    previous = Vector((old.x, old.y, z))
    final = xyz(current, ground(current))
    for i in vertices:
        mesh.vertices[i].co += final - previous
    mesh.update()
    return obj, {'source': MATIX_SOURCE.name, 'faces': len(selected),
                 'old_east_north_up': list(previous), 'new_east_north_up': list(final)}


def main():
    assert bpy.app.version[:3] == (4, 3, 2)
    target = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    original = [bpy.data.objects[name] for name in TILES]
    trees = [BVHTree.FromObject(bpy.data.objects[f'COL_Outer500_Surface_{east}_{north}'],
                              bpy.context.evaluated_depsgraph_get()) for east in ('01', '02') for north in ('00', '01')]

    def ground(p):
        hits = [tree.ray_cast(xyz(p, 30.), Vector((0., 0., -1.)), 65.)[0] for tree in trees]
        return max(hit.z for hit in hits if hit is not None)

    deck = Patch('deck', octagon(8.0, 6.4, .8), lambda p: LEVEL, 0)
    steps, ramp, west_start, west_end, east_start, east_end, shoulder, count = approaches(ground)
    surfaces = [deck, *steps, ramp]
    paving, walls, inset, guard = Mesh(), Mesh(), Mesh(), Mesh()
    objects, areas = build_terrain(original, surfaces, paving, walls)
    lamp, lamp_record = fit_lamp(ground, surfaces)
    objects.append(lamp)
    materials = [material('Park fine exposed aggregate', (.66, .63, .56), 'concrete_floor_worn_001_diff_2k.jpg'),
                 material('Park grey green stone support', (.40, .45, .42), 'stone_wall_05_diff_2k.jpg'),
                 material('Park muted blue play finish', (.16, .405, .62), 'concrete_floor_worn_001_diff_2k.jpg'),
                 material('Park painted steel kerb guard', (.19, .22, .22), 'rusty_painted_metal_diff_2k.jpg')]
    inset.face([xyz(p, LEVEL + .009) for p in octagon(6.9, 5.25, 1.05)], 2)
    rim(guard)
    objects += [guard.make('COL_Outer500_WestCourt_Rim', materials), paving.make('COL_Outer500_WestCourt_Paving', materials), walls.make('COL_Outer500_WestCourt_Retaining', materials),
                inset.make('Outer500_WestCourt_BlueFinish', materials)]
    for obj in list(bpy.data.objects):
        if obj not in objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    plan = {
        'osm_park': 1499726225, 'surface_classification': 'observed blue; independent game terrace',
        'replacement_meshes': [obj.name for obj in objects if obj.name in (*TILES, FURNITURE)], 'retired_objects': [],
        'new_meshes': [obj.name for obj in objects if obj.name not in (*TILES, FURNITURE)],
        'relocated_lamp': lamp_record,
        'deck_east_north': list(CENTRE), 'deck_elevation_m': LEVEL, 'areas_m2': areas, 'stair_count': count,
        'walk_plan': {name: [list(p) for p in points] for name, points in
                      {'ramp': [east_start, east_end, CENTRE], 'stair': [west_start, west_end, CENTRE],
                       'through': [west_start, west_end, CENTRE, east_end, east_start]}.items()},
        'approach_levels_m': {'east_join': ground(east_start), 'west_join': ground(west_start), 'west_stair_base': shoulder},
        'baseline_terrace_corner_heights_m': [ground(p) for p in deck.ring],
        'deck_ring_east_north': [list(p) for p in deck.ring],
        'blue_ring_east_north': [list(p) for p in octagon(6.9, 5.25, 1.05)],
        'ramp_polygon': [list(p) for p in ramp.ring],
        'stair_polygons': [[list(p) for p in tread.ring] for tread in steps],
    }
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(target / 'west-court.blend'), compress=True)
    bpy.ops.export_scene.gltf(filepath=str(target / 'west-court.glb'), export_format='GLB', export_cameras=False, export_lights=False)
    (target / 'west-court.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
