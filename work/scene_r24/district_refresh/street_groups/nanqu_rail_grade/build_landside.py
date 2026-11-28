"""Build the planted bank on the landward side of the existing Nanqu roads."""
import argparse
import json
from bisect import bisect_right
from math import cos, pi, sin, sqrt
from pathlib import Path
from random import Random
import sys

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

GROUPS = Path(__file__).resolve().parents[1]
OUTER = GROUPS.parents[1] / "district_500/outer_district.blend"
sys.path.insert(0, str(GROUPS))
from factory import Mesh, material


def foliage(seed):
    """Layer small, irregular leaf sprays over shadowed interior foliage."""
    rng = Random(seed)
    mesh = Mesh(f"Nanqu canopy {seed}")
    shades = []
    for index, rgb in enumerate(((.023,.057,.016), (.029,.083,.019), (.038,.107,.023),
                                 (.047,.133,.028), (.064,.153,.036))):
        material = bpy.data.materials.new(f"Nanqu broadleaf green {seed}-{index}")
        material.diffuse_color = (*rgb, 1)
        material.use_nodes = True
        shader = material.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = (*rgb, 1)
        shader.inputs["Roughness"].default_value = .89
        shader.inputs["Emission Color"].default_value = (*rgb, 1)
        shader.inputs["Emission Strength"].default_value = .15
        shades.append(material)

    def direction():
        z = rng.uniform(-1, 1)
        angle = rng.uniform(0, 2*pi)
        radius = sqrt(1-z*z)
        return Vector((radius*cos(angle), radius*sin(angle), z))

    centres = [(0., 0., .80, .225, .21, .18)]
    for ring, (distance, z, size) in enumerate(((.24,.68,.187), (.20,.85,.16), (.115,.58,.15))):
        for i in range(6):
            a = pi*(i/3 + ring/9) + rng.uniform(-.22,.22)
            centres.append((cos(a)*distance,sin(a)*distance,z+rng.uniform(-.06,.06),
                            size*rng.uniform(.88,1.16),size*rng.uniform(.85,1.18),rng.uniform(.105,.16)))
    for e, n, h, rx, ry, rz in centres:
        # Interior leaf masses keep overlapping crowns dark and dense, with
        # individual sprays breaking up the edges and surface highlights.
        body = bmesh.new()
        bmesh.ops.create_icosphere(body,subdivisions=2,radius=1.)
        for v in body.verts:
            factor = rng.uniform(.66,.80)
            v.co = (e+v.co.x*rx*factor,n+v.co.y*ry*factor,h+v.co.z*rz*factor)
        for face in body.faces:
            mesh.face([v.co.copy() for v in face.verts],shades[rng.randrange(3)])
        body.free()
        for _ in range(320):
            u = direction()
            factor = rng.uniform(.66,1.12)
            origin = Vector((e+rx*u.x*factor,n+ry*u.y*factor,h+rz*u.z*factor))
            along = direction()*rng.uniform(.010,.020)
            across = along.cross(direction()).normalized()*rng.uniform(.007,.015)
            mesh.face((origin-along, origin-across, origin+along, origin+across),rng.choice(shades))
    return mesh.save()


def woody_mesh(mesh):
    trunk = bmesh.new()
    trunk.from_mesh(mesh)
    leaves = {i for i, mat in enumerate(mesh.materials) if "leaves" in mat.name.lower()}
    bmesh.ops.delete(trunk, geom=[f for f in trunk.faces if f.material_index in leaves], context="FACES")
    data = mesh.copy()
    trunk.to_mesh(data)
    trunk.free()
    return data


def build(plan):
    earth = material("Nanqu planted bank dark soil", (.54, .58, .48), "brown_mud_leaves_01_diff_2k.jpg")
    rock = material("Nanqu planted bank wet grey stone", (.55, .58, .54), "stone_wall_05_diff_2k.jpg")
    bank = Mesh("COL_NanquLandside_Bank")
    for a, b in zip(plan["sections"], plan["sections"][1:]):
        for index, (a0, a1, b0, b1) in enumerate(zip(a, a[1:], b, b[1:])):
            finish = rock if index in (0, 1) else earth
            bank.face((a0, b0, b1), finish)
            bank.face((a0, b1, a1), finish)
    surface = bank.save()
    ground = BVHTree.FromPolygons(
        [v.co for v in surface.data.vertices],
        [p.vertices[:] for p in surface.data.polygons], all_triangles=True)

    donors = sorted({record["donor"] for record in plan["trees"]})
    with bpy.data.libraries.load(str(OUTER), link=True, relative=False) as (archive, selected):
        assert set(donors) <= set(archive.objects)
        selected.objects = donors
    templates = {obj.name: (obj.data, woody_mesh(obj.data)) for obj in selected.objects}
    canopies = [foliage(seed) for seed in (391,547,963)]
    eastings = [row[0][0] for row in plan["sections"]]
    contacts = []
    for index, record in enumerate(plan["trees"]):
        east = record["east"]
        i = bisect_right(eastings, east) - 1
        a, b = plan["sections"][i:i+2]
        q = (east - a[0][0]) / (b[0][0] - a[0][0])
        north = a[0][1] + (b[0][1] - a[0][1]) * q + record["north_from_toe"]
        hit = ground.ray_cast(Vector((east, north, 100)), Vector((0, 0, -1)), 120)[0]
        if hit is None:
            raise ValueError(f"Tree {index} is outside the bank")
        source, bark = templates[record["donor"]]
        lo = [min(v.co[i] for v in source.vertices) for i in range(3)]
        hi = [max(v.co[i] for v in source.vertices) for i in range(3)]
        sx = record["crown_width"] / (hi[0] - lo[0])
        sy = record["crown_width"] / (hi[1] - lo[1])
        sz = record["height"] / (hi[2] - lo[2])
        tree = bpy.data.objects.new(f"NanquLandside_Tree_{index:02d}", bark)
        bpy.context.collection.objects.link(tree)
        tree.scale = (sx, sy, sz)
        tree.rotation_euler.z = record["yaw"]
        tree.location = (east, north, hit.z - lo[2] * sz - .09)
        crown = bpy.data.objects.new(tree.name+"_Canopy",canopies[index % len(canopies)].data)
        bpy.context.collection.objects.link(crown)
        crown.scale = (record["crown_width"],record.get("crown_depth",record["crown_width"]),record["height"])
        crown.rotation_euler.z = record["yaw"]
        crown.location = (east,north,hit.z-.09)
        # Only the root and lower trunk block the player. The foliage is visual.
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=min(.55, sx*.12), depth=2.8,
                                           location=(east, north, hit.z+1.30))
        trunk = bpy.context.object
        trunk.name = f"COLH_NanquLandside_Stem_{index:02d}"
        contacts.append({"tree": tree.name, "donor": record["donor"],
                         "root_enu": list(hit), "crown_top_y": hit.z + record["height"] - .09})
    for template in canopies:
        bpy.data.objects.remove(template,do_unlink=True)
    return contacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("controls", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    contacts = build(json.loads(args.controls.read_text()))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output/"nanqu-landside.blend"), compress=True)
    bpy.ops.export_scene.gltf(filepath=str(output/"nanqu-landside.glb"), export_format="GLB",
                             export_cameras=False, export_lights=False)
    (output/"root-contacts.json").write_text(json.dumps(contacts, indent=2)+"\n")


if __name__ == "__main__":
    main()
