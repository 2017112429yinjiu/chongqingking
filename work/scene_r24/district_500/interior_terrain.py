"""Create the terrain correction layer from the unmodified outer district."""
import json
import os
from math import cos, sin
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[1] / "project/chongqing_godot_v05/assets/district_500"
EPSILON = 1e-6
EDGE_EPSILON = 5e-5
CLEARANCE = .06


def read(name):
    return json.loads((ASSETS / name).read_bytes())


def interior_regions():
    for building in read("shancheng_lane.json")["buildings"]:
        yield building["osm"], building["wall_base_corners"], building["floor_z"]
    for building in read("historic_courts.json")["buildings"]:
        if building["id"] in ("renai_long", "renai_cross"):
            yield building["id"], building["ring"], building["floor"]
    for plot in read("layout.json")["plots"]:
        if plot["plot_id"] not in (54, 56):
            continue
        x, y = plot["east_north"]
        c, s = cos(plot["bearing"]), sin(plot["bearing"])
        w, d = plot["width"] / 2, plot["depth"] / 2
        ring = [(x + u*c - v*s, y + u*s + v*c)
                for u, v in [(-w, -d), (w, -d), (w, d), (-w, d)]]
        yield f"plot_{plot['plot_id']}", ring, plot["height"]


def clip_polygon(points, distance):
    """Partition a convex polygon into positive and negative half-planes."""
    kept, rejected = [], []
    for a, b in zip(points, points[1:] + points[:1]):
        da, db = distance(a), distance(b)
        if da >= 0:
            kept.append(a)
        else:
            rejected.append(a)
        if (da < 0) != (db < 0):
            hit = a.lerp(b, da / (da - db))
            kept.append(hit)
            rejected.append(hit)
    return kept, rejected


def area(points):
    if len(points) < 3:
        return 0
    origin = points[0]
    return sum((a - origin).cross(b - origin).length
               for a, b in zip(points[1:], points[2:])) / 2


def subtract_building(points, edges, cap):
    """Retain exterior geometry at its original grade and lower the interior."""
    pieces = []
    for start, normal in edges:
        inside, outside = clip_polygon(points, lambda p: normal.dot(p - start))
        if area(outside) > EPSILON:
            pieces.append(outside)
        points = inside
        if area(points) <= EPSILON:
            return None
    if max(p.z for p in points) <= cap + EPSILON:
        return None

    def lowered(p):
        return Vector((p.x, p.y, min(p.z, cap)))

    level = [lowered(p) for p in points]
    pieces.append(level)
    for index, (a, b) in enumerate(zip(points, points[1:] + points[:1])):
        if not any(abs(normal.dot(a - start)) < EDGE_EPSILON and abs(normal.dot(b - start)) < EDGE_EPSILON
                   for start, normal in edges):
            continue
        seam = [a, b, level[(index + 1) % len(level)], level[index]]
        if area(seam) > EPSILON:
            pieces.append(seam)
    return pieces


def replace_terrain(obj, regions, counts):
    mesh = obj.data
    assert obj.matrix_world == Matrix.Identity(4), obj.name
    vertices = [vertex.co.copy() for vertex in mesh.vertices]
    bounds = [(min(p[axis] for p in vertices), max(p[axis] for p in vertices)) for axis in (0, 1)]
    nearby = [r for r in regions if all(a <= hi and b >= lo for (a, b), (lo, hi) in zip(r[3], bounds))]
    if not nearby:
        return False
    output, faces, slots = [], [], []
    changed = False
    for face in mesh.polygons:
        original = [vertices[i] for i in face.vertices]
        parts = [original]
        for name, cap, edges, rectangle in nearby:
            if max(p.z for p in original) <= cap or any(
                    max(p[axis] for p in original) < lo or min(p[axis] for p in original) > hi
                    for axis, (lo, hi) in enumerate(rectangle)):
                continue
            clipped = []
            for part in parts:
                replacement = subtract_building(part, edges, cap)
                if replacement:
                    counts[name] += 1
                    changed = True
                    clipped.extend(replacement)
                else:
                    clipped.append(part)
            parts = clipped
        for part in parts:
            indices = []
            for point in part:
                if not indices or (output[indices[-1]] - point).length > EPSILON:
                    indices.append(len(output))
                    output.append(point)
            if len(indices) > 2 and (output[indices[0]] - output[indices[-1]]).length <= EPSILON:
                indices.pop()
            for i in range(1, len(indices) - 1):
                tri = (indices[0], indices[i], indices[i + 1])
                if area([output[j] for j in tri]) > EPSILON:
                    faces.append(tri)
                    slots.append(face.material_index)
    if not changed:
        return False
    amended = bpy.data.meshes.new(obj.name + "_InteriorGrade")
    amended.from_pydata(output, [], faces)
    for material in mesh.materials:
        amended.materials.append(material)
    uv = amended.uv_layers.new(name=mesh.uv_layers.active.name)
    for face, slot in zip(amended.polygons, slots):
        face.material_index = slot
        for loop in face.loop_indices:
            p = output[amended.loops[loop].vertex_index]
            uv.data[loop].uv = (p.x / 2.4, p.y / 2.4)
    obj.data = amended
    return True


def trim_stair_wall():
    plot = next(p for p in read("layout.json")["plots"] if p["plot_id"] == 37)
    origin = Vector((*plot["east_north"], 0))
    c, s = cos(plot["bearing"]), sin(plot["bearing"])
    across = Vector((c, s, 0))
    inward = Vector((-s, c, 0))
    # The recorded collision runs across the lower flight, 27 mm from its toe.
    toe = -plot["depth"] / 2 - plot["front_stair_m"]
    wall_line = toe - .027
    left, right = plot["door_u"] - 1.25, plot["door_u"] + 1.25
    obj = bpy.data.objects["COL_Outer500_Retaining_and_boundaries"]
    mesh = obj.data
    assert obj.matrix_world == Matrix.Identity(4), obj.name
    bm = bmesh.new()
    bm.from_mesh(mesh)
    panels = [f for f in bm.faces
              if all(abs(inward.dot(v.co - origin) - wall_line) < .004 for v in f.verts)
              and min(across.dot(v.co - origin) for v in f.verts) < right
              and max(across.dot(v.co - origin) for v in f.verts) > left
              and min(v.co.z for v in f.verts) < plot["height"]
              and max(v.co.z for v in f.verts) > plot["height"] - 3]
    assert len(panels) == 2, len(panels)
    for boundary in (left, right):
        geometry = set(panels)
        for panel in panels:
            geometry.update(panel.edges)
            geometry.update(panel.verts)
        result = bmesh.ops.bisect_plane(
            bm, geom=list(geometry), dist=EDGE_EPSILON,
            plane_co=origin + across * boundary, plane_no=across)
        panels = list({f for f in panels + result["geom"] if isinstance(f, bmesh.types.BMFace) and f.is_valid})
    removed = [f for f in panels
               if left + EDGE_EPSILON < across.dot(f.calc_center_median() - origin) < right - EDGE_EPSILON]
    assert removed
    bmesh.ops.delete(bm, geom=removed, context="FACES")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    print("PLOT_37_STAIR_WALL", wall_line, left, right, len(removed))
    return obj


def relocate_window_tree():
    plot = next(p for p in read("layout.json")["plots"] if p["plot_id"] == 42)
    tree = bpy.data.objects["Outer500_Plant_036"]
    origin = Vector((*plot["east_north"], 0))
    c, s = cos(plot["bearing"]), sin(plot["bearing"])
    new = origin + Vector((c, s, 0)) * -12 + Vector((-s, c, 0)) * -1.3
    tile = bpy.data.objects["COL_Outer500_Surface_06_08"]
    hit, point, _, _ = tile.ray_cast((new.x, new.y, 120), (0, 0, -1))
    assert hit
    tree.location = (new.x, new.y, point.z - .025)
    bpy.context.view_layer.update()
    print("PLOT_42_TREE", list(tree.location))
    return tree


def apply():
    regions, counts = [], {}
    for name, ring, floor in interior_regions():
        points = [Vector((x, y, 0)) for x, y in ring]
        center = sum(points, Vector()) / len(points)
        edges = []
        for a, b in zip(points, points[1:] + points[:1]):
            vector = b - a
            normal = Vector((-vector.y, vector.x, 0)).normalized()
            edges.append((a, normal if normal.dot(center - a) > 0 else -normal))
        assert all(normal.dot(p - a) >= -EDGE_EPSILON for a, normal in edges for p in points), name
        bounds = [(min(p[i] for p in points), max(p[i] for p in points)) for i in (0, 1)]
        regions.append((name, floor - CLEARANCE, edges, bounds))
        counts[name] = 0
    changed = [obj for obj in bpy.context.scene.objects
               if obj.name.startswith("COL_Outer500_Surface_") and replace_terrain(obj, regions, counts)]
    print("INTERIOR_TERRAIN", json.dumps({"parts": counts, "tiles": [obj.name for obj in changed]}))
    assert changed
    return changed


if __name__ == "__main__":
    assert Path(bpy.data.filepath).name == "outer_district.blend"
    changed = apply()
    changed.append(trim_stair_wall())
    tree = relocate_window_tree()
    bpy.context.view_layer.update()
    if os.environ.get("CQ_SAVE_PATCH") == "1":
        for obj in list(bpy.data.objects):
            if obj not in changed and obj != tree:
                bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.orphans_purge(do_recursive=True)
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "interior_terrain.blend"), compress=True)
        (ASSETS / "interior_terrain.json").write_text(
            json.dumps({"tiles_and_wall": [obj.name for obj in changed],
                        "tree_east_north_up": list(tree.location)}, indent=2) + "\n")
        bpy.ops.object.select_all(action="DESELECT")
        for obj in changed:
            obj.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(ASSETS / "interior_terrain.glb"),
                                  export_format="GLB", use_selection=True, export_cameras=False, export_lights=False)
