"""Place reduced meshes from the existing R24 scanned-tree library at the trial's surveyed roots."""
from math import radians

import bpy


def place_trees(assets, sites, materials, material):
    library = assets / "neighborhood_r24/tree_distances.glb"
    existing = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(library))
    imported = set(bpy.data.objects) - existing
    species = {
        "tree_small_02": ("tree_small_02", "tree_small_02_branch", "tree_small_02_leaves"),
        "island_tree_01": ("island_tree_01_branches", "island_tree_01", "island_tree_01_leaves"),
    }
    donors = []
    for kind, textures in species.items():
        parts = []
        for group, texture in enumerate(textures):
            obj = bpy.data.objects["Canopy_%s_low_%d" % (kind, group)]
            obj.data.materials.clear()
            slot = material("Scan " + texture, (0.45, 0.48, 0.38), texture + "_diff_2k.jpg")
            obj.data.materials.append(materials[slot])
            budget = 1500
            if not texture.endswith("leaves") and len(obj.data.polygons) > budget:
                modifier = obj.modifiers.new("Street tree triangle budget", "DECIMATE")
                modifier.ratio = budget / len(obj.data.polygons)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            parts.append(obj)
        bpy.ops.object.select_all(action="DESELECT")
        for part in parts:
            part.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        # Joining the three material groups retains their scan UVs.
        for other in parts[1:]:
            imported.discard(other)
        bpy.ops.object.join()
        mesh = parts[0].data
        mesh.name = "StreetTree_" + kind
        donors.append(mesh)
    for i, row in enumerate(sites):
        mesh = donors[row["species"]]
        obj = bpy.data.objects.new("Outer500_Plant_%03d" % i, mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = row["east_north_up"]
        obj.rotation_euler.z = radians(row["rotation_deg"])
        obj.scale = (row["width_scale"], row["width_scale"], row["height_scale"])
    for source in imported:
        bpy.data.objects.remove(source, do_unlink=True)
