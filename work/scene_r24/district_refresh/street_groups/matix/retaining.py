"""Keep the original wall sections outside the two registered street crossings."""
import bmesh
import bpy
from mathutils import Vector

from retire_plots import RETAINING, fingerprint


def open_crossings(ways, sites, ownership):
    old_steps = {value for piece in ownership['43'][RETAINING] for value in piece['faces']}
    wall = bpy.data.objects[RETAINING]
    mesh = bmesh.new()
    mesh.from_mesh(wall.data)
    selected = mesh.faces.layers.int.new('cq_crossing')
    mesh.faces.index_update()
    mesh.normal_update()
    source = {f: fingerprint(wall, wall.data.polygons[f.index]) for f in mesh.faces}
    previous_run = [face for face in mesh.faces if source[face] in old_steps]
    assert len(previous_run) == len(old_steps) == 204
    bmesh.ops.delete(mesh, geom=previous_run, context='FACES')

    report = []
    for way, station, half_width in [('1025797980', 0, 1.30), ('1025797976', 2, 1.40)]:
        pin = sites[way][station]
        hit = Vector(pin['point_east_north_up'][:2])
        points = [Vector(p) for p in ways[way]['east_north']]
        segments = []
        for a, b in zip(points, points[1:]):
            direction = (b - a).normalized()
            close = a + max(0., min((b - a).length, (hit - a).dot(direction))) * direction
            segments.append(((close - hit).length, close, direction))
        _, center, along = min(segments, key=lambda item: item[0])
        across = Vector((-along.y, along.x))
        cuts = [(along, 3.1), (across, half_width)]

        def intersects(face):
            for direction, radius in cuts:
                offsets = [(v.co.xy - center).dot(direction) for v in face.verts]
                if min(offsets) > radius or max(offsets) < -radius:
                    return False
            return True

        scope = [f for f in mesh.faces if abs(f.normal.z) < .02 and intersects(f)
                 and wall.data.materials[f.material_index].name.split('.')[0] == 'Coursed retaining masonry']
        assert any(source.get(face) == pin['signature'] for face in scope), pin
        for face in scope:
            face[selected] = 1
        for direction, radius in cuts:
            for sign in (-1, 1):
                faces = [f for f in mesh.faces if f[selected]]
                geometry = set(faces)
                geometry.update(e for f in faces for e in f.edges)
                geometry.update(v for f in faces for v in f.verts)
                point = center + sign * radius * direction
                bmesh.ops.bisect_plane(mesh, geom=list(geometry), dist=.00001,
                                      plane_co=(*point, 0), plane_no=(*direction, 0))
        removal = [f for f in mesh.faces if f[selected] and all(
            abs((f.calc_center_median().xy - center).dot(direction)) < radius for direction, radius in cuts)]
        assert removal
        bmesh.ops.delete(mesh, geom=removal, context='FACES')
        for face in mesh.faces:
            face[selected] = 0
        report.append({'way': way, 'face': pin['face'], 'width_m': 2 * half_width,
                       'centre_east_north': list(center), 'removed_fragment_count': len(removal)})
    mesh.faces.layers.int.remove(selected)
    mesh.to_mesh(wall.data)
    mesh.free()
    wall.data.update()
    return report
