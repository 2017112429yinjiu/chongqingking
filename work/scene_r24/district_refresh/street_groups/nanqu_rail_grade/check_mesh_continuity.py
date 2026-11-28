"""Measure exact gaps in the horizontal projection of the two Blender meshes."""
import json
import math
from pathlib import Path
import sys

import bpy


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def projection_intervals(triangles, a, b):
    line = sub(b, a)
    for tri in triangles:
        x, y, z = tri
        orientation = cross(sub(y, x), sub(z, x))
        if abs(orientation) < 1e-9:
            continue
        if orientation < 0:
            tri = (x, z, y)
        low, high = 0.0, 1.0
        for start, finish in zip(tri, tri[1:] + tri[:1]):
            edge = sub(finish, start)
            side = cross(edge, sub(a, start))
            slope = cross(edge, line)
            if abs(slope) < 1e-9:
                if side < -1e-8:
                    low, high = 1.0, 0.0
                    break
                continue
            limit = -side / slope
            if slope > 0:
                low = max(low, limit)
            else:
                high = min(high, limit)
        if high >= low:
            yield low, high


def gaps(triangles, a, b):
    end = 0.0
    missing = []
    for low, high in sorted(projection_intervals(triangles, a, b)):
        if low - end > 1e-6:
            missing.append((end, low))
        end = max(end, high)
    if 1 - end > 1e-6:
        missing.append((end, 1.0))
    return [{'ratio_range': [x, y], 'length_m': (y - x) * math.dist(a, b)} for x, y in missing]


def main():
    guide, output = map(Path, sys.argv[sys.argv.index('--') + 1:])
    data = json.loads(guide.read_text())
    names = ('Grade__COL_Nanjimen_NorthRailSteelBox', 'Grade__Nanjimen_NorthAcousticHood')
    owner_triangles = {}
    for name in names:
        obj = bpy.context.scene.objects[name]
        obj.data.calc_loop_triangles()
        xy = [tuple((obj.matrix_world @ v.co)[:2]) for v in obj.data.vertices]
        owner_triangles[name] = [tuple(xy[k] for k in p.vertices) for p in obj.data.loop_triangles]
    rows = []
    for station in range(1, 7):
        land = data['samples'][f'rail-span-{station}-landside']
        river = data['samples'][f'rail-span-{station}-riverside']
        for step, (a, b) in enumerate(zip(land, river, strict=True), 1):
            rows.append({'station': station, 'step': step, 'landside_enu': a, 'riverside_enu': b,
                         'length_m': math.dist(a, b), 'gaps_by_mesh': {name: gaps(t, a, b) for name, t in owner_triangles.items()}})
    result = {'blender': bpy.app.version_string, 'source': bpy.data.filepath, 'crossings': rows,
              'continuous_by_mesh': {name: sum(not row['gaps_by_mesh'][name] for row in rows) for name in names}}
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(result['continuous_by_mesh'])


if __name__ == '__main__':
    main()
