"""Run with Blender 4.3.2 --background city_and_patrol.blend --python this_file."""
import json
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

directory = Path(__file__).resolve().parent
scene = bpy.context.scene
vertices = []
faces = []
for terrain in scene.objects:
    if not terrain.name.startswith("COL_Terrain_200m"):
        continue
    offset = len(vertices)
    vertices.extend(terrain.matrix_world @ v.co for v in terrain.data.vertices)
    faces.extend(tuple(offset + i for i in p.vertices) for p in terrain.data.polygons)
tree = BVHTree.FromPolygons(vertices, faces)
profiles = {}
for side in ("west", "east", "south", "north"):
    profile = []
    for index in range(-100, 101):
        x, y = {"west": (-99.98, index), "east": (99.98, index),
                "south": (index, -99.98), "north": (index, 99.98)}[side]
        hit = tree.ray_cast((max(-99.98,min(99.98,x)), max(-99.98,min(99.98,y)), 250), (0,0,-1))[0]
        profile.append(None if hit is None else round(hit.z,5))
    profiles[side] = profile
(directory / "terrain_baseline.json").write_text(json.dumps({
    "version": bpy.app.version_string, "objects": len(scene.objects),
    "bounds": [[round(fn(v[i] for v in vertices), 5) for i in range(3)] for fn in (min,max)],
    "terrain_profiles": profiles,
    "libraries": [lib.filepath for lib in bpy.data.libraries],
    "external_images": [im.filepath for im in bpy.data.images if im.source=="FILE" and not im.packed_file],
}, indent=2)+"\n")
