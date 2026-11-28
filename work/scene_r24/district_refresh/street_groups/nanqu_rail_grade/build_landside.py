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


def leaf_material():
    leaf = material("Nanqu scanned broadleaf surfaces", (.8, .91, .75), "island_tree_01_leaves_diff_2k.jpg")
    shader = leaf.node_tree.nodes.get("Principled BSDF")
    # The mesh perimeter follows each leaf in the atlas. The atlas itself has
    # a black background and does not need an alpha or transparency pass.
    scan = next(node for node in leaf.node_tree.nodes if node.type == "TEX_IMAGE")
    leaf.node_tree.links.new(scan.outputs["Color"], shader.inputs["Base Color"])
    shader.inputs["Emission Color"].default_value = (.034, .083, .023, 1.)
    shader.inputs["Emission Strength"].default_value = .26
    return leaf


def direction(rng):
    z = rng.uniform(-1, 1)
    angle = rng.uniform(0, 2*pi)
    radius = sqrt(1-z*z)
    return Vector((radius*cos(angle), radius*sin(angle), z))


# Cut points within six different scans. (0,0) is the top left of the atlas.
LEAF_SCANS = (
    ((.091,.050),(.061,.105),(.034,.214),(.044,.284),(.071,.354),(.101,.276),(.127,.199),(.120,.105)),
    ((.277,.046),(.237,.099),(.198,.153),(.210,.274),(.274,.358),(.305,.302),(.321,.184),(.309,.093)),
    ((.418,.039),(.392,.098),(.372,.189),(.387,.264),(.416,.302),(.449,.252),(.471,.151),(.454,.098)),
    ((.589,.060),(.552,.101),(.526,.182),(.544,.260),(.592,.350),(.616,.274),(.629,.166),(.617,.091)),
    ((.274,.607),(.242,.663),(.226,.784),(.253,.870),(.286,.922),(.322,.821),(.344,.737),(.313,.662)),
    ((.482,.622),(.455,.703),(.434,.759),(.451,.819),(.476,.911),(.508,.839),(.545,.776),(.515,.721)),
)


def leaf_spray(mesh, tip, size, rng, uv_layer):
    axis = direction(rng) * size
    across = axis.cross(direction(rng)).normalized() * size
    raised = axis.cross(across).normalized() * size * .075
    for side in (-1, 1):
        outline = rng.choice(LEAF_SCANS)
        u_mid = sum(u for u, _ in outline) / len(outline)
        v_mid = sum(v for _, v in outline) / len(outline)
        center = tip + across * (.25 * side) + axis * rng.uniform(-.22, .22)
        ph = mesh.verts.new(center + raised)
        rim = [mesh.verts.new(center + axis * ((v_mid-v)*3.1) + across * ((u-u_mid)*3.2))
               for u, v in outline]
        for i, vert in enumerate(rim):
            j = (i+1) % len(rim)
            face = mesh.faces.new((ph, vert, rim[j]))
            for loop, (u, v) in zip(face.loops, ((u_mid,v_mid), outline[i], outline[j])):
                loop[uv_layer].uv = (u, 1-v)


def canopy(name, lobes, seed, leaf, *, spread, leaf_size, density):
    """Fill irregular branch volumes with overlapping scanned leaves."""
    rng = Random(seed)
    mesh = bmesh.new()
    uv = mesh.loops.layers.uv.new()
    for center, radii in lobes:
        for _ in range(density):
            u = direction(rng)
            factor = rng.uniform(.39, spread)
            point = center + Vector(tuple(a*b*factor for a,b in zip(u,radii)))
            leaf_spray(mesh, point, rng.uniform(*leaf_size), rng, uv)
    data = bpy.data.meshes.new(name)
    data.materials.append(leaf)
    mesh.to_mesh(data)
    mesh.free()
    return data


def lower_lobes(seed):
    rng = Random(seed)
    yield Vector((0.,0.,.80)), (.225,.21,.18)
    for ring, (radius, height, size) in enumerate(((.24,.68,.187), (.20,.85,.16), (.115,.58,.15))):
        for i in range(6):
            angle = pi*(i/3 + ring/9) + rng.uniform(-.22,.22)
            yield (Vector((cos(angle)*radius, sin(angle)*radius, height+rng.uniform(-.06,.06))),
                   (size*rng.uniform(.88,1.16),size*rng.uniform(.85,1.18),rng.uniform(.105,.16)))


def grown_branch(name, points, bark_material):
    mesh = Mesh(name)
    for index, (a, b) in enumerate(zip(points, points[1:])):
        axis = (b-a).normalized()
        u = axis.cross(Vector((0, 1, 0))).normalized()
        v = axis.cross(u)
        ring = [u*cos(i*pi/4)+v*sin(i*pi/4) for i in range(8)]
        r0, r1 = (.265,.122) if index == 0 else (.122,.037)
        mesh.solid([a+r*r0 for r in ring], [b+r*r1 for r in ring], bark_material)
    return mesh.save()


def high_lobes(center, size, seed):
    rng = Random(seed)
    yield center, tuple(r*.64 for r in size)
    for i in range(10):
        angle = i*pi/5 + rng.uniform(-.26,.26)
        height = rng.uniform(-.44,.59)
        point = center + Vector((.50*size[0]*cos(angle), .50*size[1]*sin(angle), size[2]*height))
        yield point, (size[0]*rng.uniform(.38,.56),size[1]*rng.uniform(.40,.57),size[2]*rng.uniform(.43,.63))


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
    leaf = leaf_material()
    canopies = [canopy(f"Nanqu low crown {seed}",lower_lobes(seed),seed,leaf,
                       spread=1.095,leaf_size=(.024,.046),density=169) for seed in (391,547,963)]
    extensions = {i: [] for i in range(len(plan["trees"]))}
    for part in plan.get("upper_lobes", []):
        extensions[part["on_tree"]].append(part)
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
        crown = bpy.data.objects.new(tree.name+"_Canopy",canopies[index % len(canopies)])
        bpy.context.collection.objects.link(crown)
        crown.scale = (record["crown_width"],record.get("crown_depth",record["crown_width"]),record["height"])
        crown.rotation_euler.z = record["yaw"]
        crown.location = (east,north,hit.z-.09)
        for part in extensions[index]:
            tip = Vector(part["centre_enu"])
            seed = part["seed"]
            base = Vector((east,north,hit.z+record["height"]*.67))
            elbow = base.lerp(tip,.51)
            elbow.z += .9
            bend = tip.lerp(elbow,.19)
            grown_branch(f"{tree.name}_UpperFork_{seed}", (base,elbow,bend), bark.materials[0])
            upper_data = canopy(f"Nanqu high crown {seed}",high_lobes(tip,part["radii"],seed),seed,
                                leaf,spread=1.09,leaf_size=(.35,.68),density=117)
            upper = bpy.data.objects.new(f"{tree.name}_UpperLeaves_{seed}", upper_data)
            bpy.context.collection.objects.link(upper)
        # Only the root and lower trunk block the player. The foliage is visual.
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=min(.55, sx*.12), depth=2.8,
                                           location=(east, north, hit.z+1.30))
        trunk = bpy.context.object
        trunk.name = f"COLH_NanquLandside_Stem_{index:02d}"
        contacts.append({"tree": tree.name, "donor": record["donor"],
                         "root_enu": list(hit), "crown_top_y": hit.z + record["height"] - .09})
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
