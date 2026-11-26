"""Build the editable Match Factory exterior from OSM and field photographs."""
import json
from math import cos, pi, sin
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / "district_500")]
from riverside import make_strip, material, terrain_faces
from retire_plots import replace_shared_geometry


class Mesh:
    def __init__(self, name):
        self.name = name
        self.vertices = []
        self.faces = []
        self.finishes = []

    def face(self, points, finish):
        start = len(self.vertices)
        self.vertices.extend(points)
        self.faces.append(tuple(range(start, len(self.vertices))))
        self.finishes.append(finish)

    def solid(self, bottom, top, finish):
        self.face(bottom[::-1], finish)
        self.face(top, finish)
        for i, j in zip(range(len(bottom)), (*range(1, len(bottom)), 0)):
            self.face([bottom[i], bottom[j], top[j], top[i]], finish)

    def save(self):
        data = bpy.data.meshes.new(self.name)
        data.from_pydata(self.vertices, [], self.faces)
        data.update()
        finishes = list(dict.fromkeys(self.finishes))
        for finish in finishes:
            data.materials.append(finish)
        indices = {finish: i for i, finish in enumerate(finishes)}
        texture = data.uv_layers.new()
        for poly, finish in zip(data.polygons, self.finishes):
            poly.material_index = indices[finish]
            normal = poly.normal
            for loop in poly.loop_indices:
                point = data.vertices[data.loops[loop].vertex_index].co
                if abs(normal.z) > .45:
                    texture.data[loop].uv = (point.x / 2.0, point.y / 2.0)
                else:
                    texture.data[loop].uv = ((point.y*normal.x-point.x*normal.y)/1.44, point.z/1.44)
        obj = bpy.data.objects.new(self.name, data)
        bpy.context.collection.objects.link(obj)
        return obj


def terrain():
    vertices, faces = [], []
    for ob in bpy.context.scene.objects:
        if not ob.name.startswith(("COL_Outer500_Surface_", "Outer500_Background_transition")):
            continue
        start = len(vertices)
        vertices.extend(ob.matrix_world @ v.co for v in ob.data.vertices)
        faces.extend(tuple(start+i for i in face.vertices) for face in ob.data.polygons)
    return BVHTree.FromPolygons(vertices, faces)


def build(spec, ground):
    wall = material("Match Factory grey coursed bricks", (.84, .86, .88), "brick_wall_08_diff_2k.jpg")
    piers = material("Match Factory raised brick piers", (.94, .90, .85), "brick_wall_08_diff_2k.jpg")
    stone = material("Match Factory grey stone sills", (.61, .64, .66), "stone_wall_05_diff_2k.jpg")
    tile = material("Match Factory dark small roof tiles", (.72, .78, .81), "roof_tiles_diff.jpg")
    flags = material("Match Factory stone kerb and sill", (.67, .69, .67), "concrete_floor_worn_001_diff_2k.jpg")
    paving = material("Match Factory dressed stone pavement", (.71, .75, .75), "stone_floor_diff_2k.jpg")
    glazing = bpy.data.materials.new("Match Factory shaded blue glazing")
    glazing.diffuse_color = (.035, .083, .101, 1)
    sash = bpy.data.materials.new("Match Factory oxidised red casements")
    sash.diffuse_color = (.12, .041, .025, 1)
    ring = [Vector(v) for v in spec["east_north"]]
    levels = spec["game_levels_m"]
    shell = Mesh("COL_Guoco_MatchFactory_704006706")
    trim = Mesh("Guoco_MatchFactory_BrickPiersAndCasements")
    roof = Mesh("Guoco_MatchFactory_HippedGableSmallTiles")

    def ground_height(point):
        hit, _, _, _ = ground.ray_cast(Vector((point.x, point.y, 120)), Vector((0, 0, -1)))
        if hit is None:
            raise ValueError(f"No ground below Match Factory at {point!r}")
        return hit.z

    contact_heights = []
    for index, (a, b) in enumerate(zip(ring, ring[1:] + ring[:1])):
        side = b-a
        width = side.length
        inward = Vector((-side.y, side.x)).normalized()
        direction = side.normalized()

        def point(u, v, h):
            q = a + direction*u + inward*v
            return (q.x, q.y, h)

        def profile(mesh, curve, near, far, finish):
            lower = [point(u, near, h) for u, h in curve]
            upper = [point(u, far, h) for u, h in curve]
            mesh.solid(upper, lower, finish)

        def block(mesh, x0, z0, x1, z1, near, far, finish):
            profile(mesh, [(x0,z0), (x1,z0), (x1,z1), (x0,z1)], near, far, finish)

        count = 9 if index % 2 == 0 else 4
        pitch = width / count
        for bay in range(count):
            left = bay*pitch
            right = left+pitch
            centre = (left+right)/2
            block(trim, left+.04, levels[0]-.1, left+.46, levels[-1]+.19, -.19, .038, piers)
            block(trim, left+.015, levels[-1]-.13, left+.49, levels[-1]+.25, -.23, .03, flags)
            for story, (base, top) in enumerate(zip(levels, levels[1:])):
                door = index == 2 and bay in (3, 4) and story == 1
                spring = base+2.04
                sill = base+.63 if not door else base+.07
                span = min(pitch*.29, 1.12) if story != 2 else min(pitch*.24, .91)
                low, high = centre-span, centre+span
                head = base+2.17 if story == 2 else base+2.39
                block(shell, left, base, low, top, 0, .40, wall)
                block(shell, high, base, right, top, 0, .40, wall)
                block(shell, low, base, high, sill, 0, .40, wall)
                if story == 1:
                    arc = [(centre+span*cos(pi-i*pi/12), spring+.45*sin(pi-i*pi/12)) for i in range(13)]
                    for i, ((x0,z0),(x1,z1)) in enumerate(zip(arc, arc[1:])):
                        profile(shell, [(x0,z0),(x1,z1),(x1,top),(x0,top)], 0, .40, wall)
                        t0, t1 = pi-(i+.025)*pi/12, pi-(i+.975)*pi/12
                        curve = [(centre+(span+r)*cos(t), spring+(.45+r)*sin(t))
                                 for r,t in [(0,t0),(0,t1),(.14,t1),(.14,t0)]]
                        profile(trim, curve, -.084, .018, piers)
                    profile(shell, [(low,sill), (high,sill), *reversed(arc)], .30, .385, glazing)
                    head = spring
                else:
                    block(shell, low, head, high, top, 0, .40, wall)
                    block(trim, low-.065, head-.02, high+.065, head+.08, -.07, .13, piers)
                    block(shell, low, sill, high, head, .30, .385, glazing)
                for x in (low+.034, centre-span*.57, centre, centre+span*.57, high-.034):
                    block(trim, x-.028, sill, x+.028, head, .245, .308, sash)
                for h in (sill+.04, sill+(head-sill)*.37, sill+(head-sill)*.69, head-.025):
                    block(trim, low, h-.022, high, h+.022, .241, .310, sash)
                block(trim, low-.083, sill-.098, high+.083, sill-.016, -.15, .072, flags)
                block(trim, left, top-.16, right, top-.052, -.079, .07, piers)
            for j in range(4):
                u0 = left + pitch*j/4
                u1 = left + pitch*(j+1)/4
                gauge = [ground_height(Vector(point(u, 0, 0)[:2])) for u in (u0,u1)]
                bottom = min(*gauge, levels[0])-.19
                contact_heights.extend(gauge)
                block(shell, u0, bottom, u1, levels[0], 0, .43, stone)

    w, d = (ring[1]-ring[0]).length, (ring[3]-ring[0]).length
    u_axis, v_axis = (ring[1]-ring[0]).normalized(), (ring[3]-ring[0]).normalized()

    def local(u, v, z):
        p = ring[0]+u_axis*u+v_axis*v
        return (p.x, p.y, z)

    eave = levels[-1] + .24
    low = [local(u,v,eave) for u,v in [(-.40,-.47),(w+.40,-.47),(w+.40,d+.47),(-.40,d+.47)]]
    shoulder = [local(u,v,eave+1.05) for u,v in [(2.6,2.5),(w-2.6,2.5),(w-2.6,d-2.5),(2.6,d-2.5)]]
    ridge = [local(u, d/2, eave+3.12) for u in (2.6,w-2.6)]
    for i, j in ((0,1),(1,2),(2,3),(3,0)):
        roof.face([low[i], low[j], shoulder[j], shoulder[i]], tile)
    roof.face([shoulder[0], shoulder[1], ridge[1], ridge[0]], tile)
    roof.face([shoulder[2], shoulder[3], ridge[0], ridge[1]], tile)
    trim.face([shoulder[3], shoulder[0], ridge[0]], wall)
    trim.face([shoulder[1], shoulder[2], ridge[1]], wall)
    roof.solid([local(u,v,eave+3.06) for u,v in [(2.5,d/2-.11),(w-2.5,d/2-.11),(w-2.5,d/2+.11),(2.5,d/2+.11)]],
               [local(u,v,eave+3.20) for u,v in [(2.5,d/2-.11),(w-2.5,d/2-.11),(w-2.5,d/2+.11),(2.5,d/2+.11)]], tile)
    print("CQ_MATCH_FACTORY", w, d, "foundation elevations", min(contact_heights), max(contact_heights))
    return [shell.save(), trim.save(), roof.save()], (flags, paving, stone), local


def main():
    if Path(bpy.data.filepath).name != "outer_district.blend":
        raise ValueError("Open outer_district.blend first.")
    spec = json.loads((HERE / "factory.json").read_bytes())
    support = terrain()
    patches = list(terrain_faces())
    objects, finishes, local = build(spec, support)
    pts = [list(local(u, -2.03, 0)[:2]) for u in (1, 7, 14, 22, 29.0)]
    plan = {"id": "match_factory_flagstones", "points": pts, "width_m": 2.36, "finish": 1, "raise_m": .021}
    walkway = make_strip(plan, patches, finishes)
    walkway.name = "Guoco_MatchFactory_PublicFrontage"
    objects.append(walkway)
    args = sys.argv[sys.argv.index("--")+1:]
    destination, ownership_path = map(Path, args)
    project = HERE.parents[2] / "project/chongqing_godot_v05"
    layout = json.loads((project / "assets/district_500/layout.json").read_bytes())
    owners = json.loads(ownership_path.read_bytes())
    replacement, retired = replace_shared_geometry(owners, spec["replaced_trial_plots"], layout,
        HERE.parents[1] / "district_500/interior_terrain.blend")
    walks = {"lower_frontage": pts,
             "uphill_wall": [list(local(u, 21.40, 0)[:2]) for u in (1, 8, 16, 24)],
             "west_to_both_grades": [list(local(-2.5,v,0)[:2]) for v in (-2.03, 1, 5, 11, 17, 21.40)]}
    manifest = {
        "way": spec["way"], "retired_trials": spec["replaced_trial_plots"], "retired_objects": retired,
        "replacement_meshes": [obj.name for obj in replacement], "new_meshes": [obj.name for obj in objects],
        "walks_east_north": walks,
    }
    objects += replacement
    for obj in list(bpy.data.objects):
        if obj not in objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.scene["source"] = "OpenStreetMap way 704006706 and the Guoco 18T Match Factory photographs"
    bpy.context.scene["grade_basis"] = "Existing trial terrain and its background collar, measured in game metres"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(destination / "match_factory.blend"), compress=True)
    bpy.ops.export_scene.gltf(filepath=str(destination / "match_factory.glb"), export_format="GLB",
                              export_cameras=False, export_lights=False)
    (destination / "match_factory.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
