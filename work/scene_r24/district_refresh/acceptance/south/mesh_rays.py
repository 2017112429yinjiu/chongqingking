"""Intersect registered low-street rays with the exact layer and shell faces."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
R24 = HERE.parents[2]
BRIDGE = HERE.parents[1]/'riverside/bridge_58_61/bridge-park.blend'

PLOT = ('COL_Outer500_Frame_56', 'Outer500_Joinery_56', 'COL_Outer500_Court_56',
        'Outer500_CourtDetails_56', 'Outer500_InteriorFloor_56')
GARAGE = ('COL_Raijiapo_GaragePublicEnvelope','COL_Raijiapo_GarageParkingSlabs',
          'COL_Raijiapo_RampRoundColumns','Raijiapo_GarageRecessedCoursesAndRails')


def collect():
    with bpy.data.libraries.load(str(BRIDGE), link=False) as (src, dst):
        assert all(n in src.objects for n in GARAGE), (BRIDGE, src.objects[:8])
        dst.objects = list(GARAGE)
    garage = {ob.name:ob for ob in dst.objects}
    scene = bpy.context.scene.objects
    return {**garage, **{name:scene[name] for name in PLOT if name in scene}}


def casting(obj, rays):
    vertices = [obj.matrix_world @ x.co for x in obj.data.vertices]
    faces = [tuple(face.vertices) for face in obj.data.polygons]
    tree = BVHTree.FromPolygons(vertices, faces)
    rows = []
    for ray in rays:
        origin, target = (Vector(ray[k]) for k in ('from','projected_target'))
        axis = (target-origin).normalized()
        length = (target-origin).length
        offset = 0.
        hits = []
        while offset <= length:
            p, n, poly, d = tree.ray_cast(origin+offset*axis,axis,length-offset)
            if p is None:
                break
            face = obj.data.polygons[poly]
            mat = obj.data.materials[face.material_index]
            hits.append({'face':poly,'material':mat.name if mat else '',
                'enu':list(p),'normal':list(n),'offset_m':offset+d,'before_feature_m':length-offset-d,
                'face_z_span_m':[min(vertices[v].z for v in face.vertices),max(vertices[v].z for v in face.vertices)]})
            if len(hits)>80:
                raise ValueError((obj.name, ray['station'], ray['feature'], hits[-2:]))
            offset += d+.002
        if hits:
            rows.append({'station':ray['station'],'feature':ray['feature'],'hits':hits})
    return rows


def main():
    rays_file, output = map(Path, sys.argv[sys.argv.index('--')+1:])
    rays = json.loads(rays_file.read_text())['hits']
    result = {name:casting(obj,rays) for name,obj in collect().items()}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print({name:(len(rows),sum(len(r['hits']) for r in rows)) for name,rows in result.items()})


if __name__=='__main__':
    main()
