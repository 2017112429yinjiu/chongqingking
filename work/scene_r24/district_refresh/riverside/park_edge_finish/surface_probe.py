"""Trace the same rendered pixels and vertical surface samples in either city assembly."""
import json
from math import radians, tan

import bpy
from mathutils import Vector

scene = bpy.context.scene
graph = bpy.context.evaluated_depsgraph_get()
eye = Vector((-77.45, -181.10, 2.22))
target = Vector((-71.75, -191.86, 1.19))
forward = (target - eye).normalized()
right = forward.cross(Vector((0, 0, 1))).normalized()
up = right.cross(forward)
focal_pixels = 253 / tan(radians(67 / 2))


def trace(start, ray):
    hits = []
    for _ in range(4):
        hit, pos, _, index, obj, _ = scene.ray_cast(graph, start, ray, distance=155)
        if not hit:
            break
        mesh = obj.data
        face = mesh.polygons[index]
        material = mesh.materials[face.material_index] if mesh.materials else None
        images = []
        if material and material.use_nodes:
            images = [node.image.name for node in material.node_tree.nodes
                      if node.type == "TEX_IMAGE" and node.image]
        uv = mesh.uv_layers.active
        polygon_uv = [list(uv.data[loop].uv) for loop in face.loop_indices] if uv else []
        hits.append({"position": list(pos), "object": obj.name, "face": index,
                     "material": material.name if material else None,
                     "images": images, "polygon_uv": polygon_uv})
        start = pos + ray * .006
    return hits


observed = {}
for x, y in [(128, 283), (210, 330), (327, 370), (410, 430), (538, 475),
             (632, 445), (750, 450), (865, 390), (855, 495), (644, 352)]:
    ray = (forward + right * ((x + .5 - 450) / focal_pixels)
           + up * ((253 - y - .5) / focal_pixels)).normalized()
    observed[str((x, y))] = trace(eye, ray)
for en in [(-70.4, -194.4), (-82.14, -189.93), (-68.67, -184.52), (-64.3, -194.7),
           (-75.9, -190.02), (-59, -202.9), (-52.65, -195), (-48.3, -202.22), (-47.8, -190.7)]:
    observed[str(en)] = trace(Vector((*en, 4)), Vector((0, 0, -1)))
print("CQ_ART_BASE", json.dumps(observed))
