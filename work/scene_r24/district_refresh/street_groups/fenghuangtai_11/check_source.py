"""Check projected running surfaces and the public stone turn after reopening."""
from pathlib import Path
import json

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
assets = here.parents[4] / 'work/project/chongqing_godot_v05/assets/district_500'
plan = json.loads((assets / 'fenghuangtai-11.json').read_text())
stations = plan['drive_stations']
scene = bpy.context.scene
graph = bpy.context.evaluated_depsgraph_get()
assert all(name in scene.objects for name in plan['replacement_meshes'])
assert all(name not in scene.objects for name in plan['retired_objects'])
assert all(scene.objects[name].data.uv_layers for name in plan['new_meshes'])
assert stations['1017606351'][-1][2] < stations['1017606351'][0][2] - 1.0

sections = {}
for way, points in stations.items():
    mesh = scene.objects[f'COL_Fenghuangtai11_Road_{way}']
    surface = BVHTree.FromObject(mesh, graph)
    tangent = (Vector(points[-1][:2]) - Vector(points[0][:2])).normalized()
    rows = []
    for e, n, z in points[1:-1]:
        for shift in (-1.4, 0., 1.4):
            x, y = e - tangent.y*shift, n + tangent.x*shift
            hit, normal, _, _ = surface.ray_cast(Vector((x,y,z+1.6)), Vector((0,0,-1)), 3.2)
            assert hit is not None and normal.z > .80, (way, x, y)
            rows.append({'enu':list(hit),'normal_up':normal.z})
    sections[way] = rows

surface = BVHTree.FromObject(scene.objects['COL_Fenghuangtai11_StoneTurn'], graph)
for e, n, z in plan['site_walk']:
    hit, normal, _, _ = surface.ray_cast(Vector((e,n,z+.5)),Vector((0,0,-1)),1.)
    assert hit is not None and abs(hit.z-z)<.012 and normal.z>.84, (e,n,z)

retaining = BVHTree.FromObject(scene.objects['COL_Fenghuangtai11_CutRetaining'],graph)
south = stations['1017606351']
tangent = (Vector(south[-1][:2])-Vector(south[0][:2])).normalized()
flanks = []
for e,n,z in south[5:-1:2]:
    for side in (-1,1):
        direction = Vector((-side*tangent.y,side*tangent.x,0.))
        hit,normal,_,gap = retaining.ray_cast(Vector((e,n,z+.55)),direction,2.80)
        assert hit is not None and normal.dot(direction)<-.90 and abs(gap-2.40)<.025, (e,n,z,side)
        flanks.append({'enu':list(hit),'flank':side,'gap_m':gap,'normal':list(normal)})

print('CQ_FENGHUANGTAI_SOURCE ' + json.dumps({'source':bpy.data.filepath,'engine':bpy.app.version_string,
      'sections':sections,'stone_sites':plan['site_walk'],'cut_flanks':flanks,'retired':plan['retired_objects']}))
