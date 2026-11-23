"""Reopen the whole editable neighbourhood and verify contact on the authored surfaces."""
from pathlib import Path
import bpy, json, runpy
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
project = here.parents[1] / 'project/chongqing_godot_v05'
plan = json.loads((project / 'assets/lane_connection_r24/layout.json').read_text('utf8'))
scene = bpy.context.scene
nodes = {name: scene.objects[name] for name in plan['source_nodes'] + plan['new_nodes']}
stairs = nodes['COL_East17_TerraceSteps']
main = nodes['COL_Walk_Upper_courtyard_walk_pavement']
assert len(stairs.data.uv_layers) >= 2
surfaces = {}
for kind, obj in [('stair', stairs), ('landing', main)]:
    surfaces[kind] = BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],
                                         [p.vertices[:] for p in obj.data.polygons])
deviations = []
for x, z, neg_y, kind in plan['floor_probes']:
    hit = surfaces[kind].ray_cast((x,-neg_y,z+.25), (0,0,-1), .51)[0]
    assert hit is not None, (x,z,neg_y)
    deviations.append(abs(hit.z-z))
assert max(deviations) < .004
rigs = [bpy.path.abspath(lib.filepath) for lib in bpy.data.libraries if lib.filepath.endswith('.blend')]
assert len(rigs) >= 3 and all(Path(file).is_file() for file in rigs)
runpy.run_path(str(here / 'pick.py'), run_name='__main__')
photo_rays = json.loads((here/'picks.json').read_text('utf8'))['joint'][:3]
assert all(hits and hits[0][0]<12 and hits[0][1]=='COL_East17_CourtyardPaving' for pixel,hits in photo_rays)
report = {'opened':bpy.data.filepath,'blender':bpy.app.version_string,'linked_libraries':rigs,
          'changed_nodes':list(nodes),'floor_samples':len(deviations),'max_floor_error_m':max(deviations),
          'tread_uvs':[l.name for l in stairs.data.uv_layers],'registered_ray_hits':photo_rays}
(here/'reopen.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),'utf8')
print('EAST17_REOPEN',len(nodes),len(deviations),max(deviations),len(rigs))
