"""Cut only the verified ridge wall across the Zhongxing street approaches."""
import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector


here = Path(__file__).resolve().parent
output = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
evidence = json.loads((here.parent / 'run/northeast-wall.json').read_bytes())
contacts = evidence['contacts']
edge = bpy.data.objects[evidence['object']]
mesh = bmesh.new()
mesh.from_mesh(edge.data)
mesh.normal_update()
tag = mesh.faces.layers.int.new('registered_opening')
stations = [Vector(row['nearest_point_east_north_up']) for row in contacts]
along = (stations[0] - stations[1]).xy.normalized()
centre = (stations[0].xy + stations[1].xy) * .5
normal = Vector((along.y, -along.x))
width = 10.0

scope = []
for face in mesh.faces:
    if abs(face.normal.z) > .001 or face.normal.xy.dot(normal) < .999:
        continue
    if not edge.data.materials[face.material_index].name.startswith('Coursed retaining masonry'):
        continue
    points = [v.co for v in face.verts]
    if not all(abs((v.xy - centre).dot(normal)) < .004 for v in points):
        continue
    if min(v.z for v in points) < 48.2 or max(v.z for v in points) > 51.0:
        continue
    offsets = [(v.xy - centre).dot(along) for v in points]
    if min(offsets) <= width * .5 and max(offsets) >= -width * .5:
        scope.append(face)
        face[tag] = 1
for pin in contacts:
    target = [Vector(value) for value in pin['face_vertices_east_north_up']]
    assert any(len(face.verts) == len(target)
               and all(any((v.co - point).length < .0002 for v in face.verts) for point in target)
               for face in scope), pin['face_index']

for sign in (-1, 1):
    faces = [face for face in mesh.faces if face[tag]]
    geometry = set(faces)
    geometry.update(v for face in faces for v in face.verts)
    geometry.update(x for face in faces for x in face.edges)
    cut = centre + sign * width * .5 * along
    bmesh.ops.bisect_plane(mesh, geom=list(geometry), dist=.00001,
                          plane_co=(*cut, 0), plane_no=(*along,0))
removal = [face for face in mesh.faces if face[tag]
           and abs((face.calc_center_median().xy - centre).dot(along)) < width * .5]
assert removal
bmesh.ops.delete(mesh, geom=removal, context='FACES')
mesh.faces.layers.int.remove(tag)
mesh.to_mesh(edge.data)
mesh.free()
edge.data.update()

for obj in list(bpy.data.objects):
    if obj != edge:
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(output/'zhongxing-retaining.blend'), compress=True)
bpy.ops.export_scene.gltf(filepath=str(output/'zhongxing-retaining.glb'), export_format='GLB')
(output/'zhongxing-retaining.json').write_text(json.dumps({'way':176034707,'opening_span_m':width,
    'replacement_meshes':[edge.name], 'retired_objects':[],
    'retained_face_contacts':contacts, 'centre_east_north':list(centre), 'source_faces_in_scope':len(scope),
    'removed_fragments':len(removal)}, ensure_ascii=False, indent=2)+'\n')
