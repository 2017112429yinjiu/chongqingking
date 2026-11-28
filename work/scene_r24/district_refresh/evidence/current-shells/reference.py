"""Index original trial-shell face triangles in ENU using the original plot-owner hashes."""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import struct
import sys

import bpy

SHARED = 'COL_Outer500_Building_envelopes'


def key(values):
    return ';'.join(sorted(','.join(str(round(c*1000)) for c in v) for v in values))


def main():
    owners_path, out_path = map(Path,sys.argv[sys.argv.index('--')+1:])
    owners = json.loads(owners_path.read_text())
    by_fingerprint = defaultdict(set)
    for pid, meshes in owners.items():
        for piece in meshes.get(SHARED, []):
            for fingerprint in piece['faces']:
                by_fingerprint[fingerprint].add(pid)
    original = bpy.context.scene.objects[SHARED]
    original.data.calc_loop_triangles()
    tessellation = defaultdict(list)
    for face in original.data.loop_triangles:
        tessellation[face.polygon_index].append(face.vertices[:])
    result = defaultdict(set)
    expected = defaultdict(int)
    for face in original.data.polygons:
        points = sorted(tuple(original.data.vertices[index].co) for index in face.vertices)
        fingerprint = sha256(b''.join(struct.pack('<fff',*v) for v in points)).hexdigest()[:24]
        plots = by_fingerprint.get(fingerprint)
        if not plots:
            continue
        for pid in plots:
            expected[pid] += len(tessellation[face.index])
        # Either quad diagonal can be chosen when a retained face is re-exported.
        tris = combinations(face.vertices,3) if len(points)==4 else tessellation[face.index]
        for indices in tris:
            result[key([original.matrix_world @ original.data.vertices[i].co for i in indices])].update(plots)
    out_path.write_text(json.dumps({'owner':SHARED,'triangles':{k:sorted(v) for k,v in result.items()},
                                    'expected':dict(expected),'ownership_plots':sorted(owners)}))
    print(len(result), 'triangle candidates covering', len(expected), 'legacy shells')


if __name__ == '__main__':
    main()
