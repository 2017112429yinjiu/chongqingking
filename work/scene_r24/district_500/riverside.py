"""Build the park paving directly on the existing dry collision triangles."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[1] / "project/chongqing_godot_v05/assets"
sys.path.insert(0, str(HERE))
from interior_terrain import clip_polygon


def area(points):
    return sum(a.x*b.y - a.y*b.x for a, b in zip(points, points[1:] + points[:1])) * .5


def part(bounds, tile):
    return all(lo <= hi2 and hi >= lo2 for (lo, hi), (lo2, hi2) in zip(bounds, tile))


def bounds(points):
    return [(min(v[i] for v in points), max(v[i] for v in points)) for i in (0, 1)]


def terrain_faces():
    for obj in bpy.context.scene.objects:
        if not obj.name.startswith("COL_Outer500_Surface_"):
            continue
        verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
        faces = [[verts[i] for i in f.vertices] for f in obj.data.polygons]
        yield bounds(verts), [(bounds(f), f) for f in faces]


def strip(points, left, right):
    tangents = [(b-a).normalized() for a, b in zip(points, points[1:])]
    normals = [Vector((-v.y, v.x, 0)) for v in tangents]
    cuts = [normals[0]]
    for a, b in zip(normals, normals[1:]):
        direction = (a+b).normalized()
        projection = direction.dot(b)
        assert projection > .71, "Promenade turns require separate rounded paving points."
        cuts.append(direction / projection)
    cuts.append(normals[-1])
    border_a = [point - left*cut for point, cut in zip(points, cuts)]
    border_b = [point - right*cut for point, cut in zip(points, cuts)]
    for a, b, c, d in zip(border_a, border_a[1:], border_b[1:], border_b):
        quad = [a, b, c, d]
        assert area(quad) > 0, quad
        yield quad


def material(name, tint, texture):
    finish = bpy.data.materials.new(name)
    finish.diffuse_color = (*tint, 1)
    finish.use_nodes = True
    tree = finish.node_tree
    shader = tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*tint, 1)
    shader.inputs["Roughness"].default_value = .88
    color = tree.nodes.new("ShaderNodeTexImage")
    color.image = bpy.data.images.load(str(ASSETS / ("chongqing_district_" + texture)),
                                       check_existing=True)
    color.image.pack()
    tint_node = tree.nodes.new("ShaderNodeMix")
    tint_node.data_type = "RGBA"
    tint_node.blend_type = "MULTIPLY"
    tint_node.inputs[0].default_value = 1.0
    tint_node.inputs[7].default_value = (*tint, 1)
    tree.links.new(color.outputs["Color"], tint_node.inputs[6])
    tree.links.new(tint_node.outputs[2], shader.inputs["Base Color"])
    return finish


def make_strip(route, terrain, materials):
    points = [Vector((e, n, 0)) for e, n in route["points"]]
    half = route["width_m"]*.5
    border = .11
    verts, faces, slots = [], [], []
    paved, expected = 0., 0.
    for left, right, slot in [(half, half-border, 2), (half-border, -half+border, route["finish"]),
                              (-half+border, -half, 2)]:
        for quad in strip(points, left, right):
            zone = bounds(quad)
            expected += area(quad)
            edges = []
            for a, b in zip(quad, quad[1:] + quad[:1]):
                line = b-a
                edges.append((a, Vector((-line.y, line.x, 0)).normalized()))
            for tile, triangles in terrain:
                if not part(zone, tile):
                    continue
                for candidate, tri in triangles:
                    if not part(zone, candidate):
                        continue
                    fragment = tri
                    for a, normal in edges:
                        fragment, _ = clip_polygon(fragment, lambda p: normal.dot(p-a))
                        if len(fragment) < 3:
                            break
                    surface = area(fragment)
                    if surface < 0.000002:
                        continue
                    paved += surface
                    base = len(verts)
                    verts.extend((v.x, v.y, v.z + route["raise_m"]) for v in fragment)
                    faces.append(tuple(range(base, len(verts))))
                    slots.append(slot)
    ratio = paved / expected
    if not .995 < ratio < 1.003:
        raise ValueError((route["id"], "unsupported paving", paved, expected))
    mesh = bpy.data.meshes.new(route["id"])
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for mat in materials:
        mesh.materials.append(mat)
    uv = mesh.uv_layers.new()
    for face, index in zip(mesh.polygons, slots):
        face.material_index = index
        span = 3.4 if index == 1 else 2.8
        for i in face.loop_indices:
            x, y, _ = verts[mesh.loops[i].vertex_index]
            uv.data[i].uv = (x / span, y / span)
    obj = bpy.data.objects.new("Outer500_Riverside_" + route["id"], mesh)
    bpy.context.scene.collection.objects.link(obj)
    print("CQ_RIVERSIDE_STRIP", route["id"], len(faces), round(paved, 2), round(ratio, 5))
    return obj


def main():
    if Path(bpy.data.filepath).name != "outer_district.blend":
        raise RuntimeError("Open outer_district.blend before building the riverside layer.")
    plan = json.loads((ASSETS / "district_500/riverside.json").read_bytes())
    triangles = list(terrain_faces())
    materials = [material("Longbin muted terracotta", (.61, .40, .36), "stone_floor_diff_2k.jpg"),
                 material("Longbin garden grey", (.63, .72, .86), "stone_floor_diff_2k.jpg"),
                 material("Longbin pale curb bands", (.75, .71, .62), "concrete_floor_worn_001_diff_2k.jpg")]
    objects = [make_strip(route, triangles, materials) for route in plan["routes"] if "finish" in route]
    for obj in list(bpy.data.objects):
        if obj not in objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "riverside.blend"), compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS / "district_500/riverside.glb"),
                              export_format="GLB", export_cameras=False, export_lights=False)


if __name__ == "__main__":
    main()
