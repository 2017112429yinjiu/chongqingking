"""Replace the old plot with the open public park visible in the aligned photographs."""
from math import cos, pi, sin
from pathlib import Path
import json
import sys

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
GROUPS = SCENE / "district_refresh/street_groups"
sys.path[:0] = [str(GROUPS), str(SCENE / "district_500")]
from factory import Mesh, material, terrain
from interior_terrain import clip_polygon
from refresh_geometry import ASSETS, latest_donors, load_current, read, strip_plots
from riverside import area, bounds, part, strip, terrain_faces

LIFT = .061
TREE_OLD = ["BridgePark_Plant_11", "BridgePark_Plant_12"]


def xy(ring):
    return [Vector((p[0], p[1], 0)) for p in ring]


def triangle_parts(ring):
    points = xy(ring)
    if area(points) < 0:
        points.reverse()
    return [[points[index] for index in item] for item in tessellate_polygon([points])]


def clip_at_edges(polygon, boundary):
    inside = polygon
    outside = []
    for a, b in zip(boundary, boundary[1:] + boundary[:1]):
        edge = b-a
        normal = Vector((-edge.y, edge.x, 0)).normalized()
        inside, cut = clip_polygon(inside, lambda point: normal.dot(point-a))
        if len(cut) >= 3 and area(cut) > .000002:
            outside.append(cut)
        if len(inside) < 3 or area(inside) <= .000002:
            return [], outside
    return inside, outside


def project(layer, targets, terrain, previous, finish, lift=LIFT):
    covered = 0.
    for target in targets:
        if area(target) < 0:
            target.reverse()
        zone = bounds(target)
        for tile, faces in terrain:
            if not part(zone, tile):
                continue
            for source_box, face in faces:
                if not part(zone, source_box):
                    continue
                inside, _ = clip_at_edges(face, target)
                if not inside:
                    continue
                fragments = [inside]
                for earlier_box, earlier in previous:
                    if not part(earlier_box, bounds(inside)):
                        continue
                    fragments = [cut for ring in fragments for cut in clip_at_edges(ring, earlier)[1]]
                    if not fragments:
                        break
                for ring in fragments:
                    covered += area(ring)
                    layer.face([(p.x, p.y, p.z+lift) for p in ring], finish)
        previous.append((zone,target))
    return round(covered, 3)


def circle(e, n, radius):
    return [(e+radius*cos(i*pi/8), n+radius*sin(i*pi/8)) for i in range(16)]


def build():
    ctl = read(HERE / "field-controls.json")
    bridges = read(ASSETS / "bridge-park.json")
    riverside = HERE.parent
    donors = latest_donors([
        ("west-ramp", riverside / "west_ramp/west-ramp.blend"),
        ("guoco-frontages", GROUPS / "guoco/guoco-frontages.blend"),
        ("public-edges", GROUPS / "matix/public-edges.blend"),
        ("xingchen", GROUPS / "xingchen/xingchen.blend"),
        ("pavilion62", riverside / "pavilion62/pavilion62.blend"),
        ("collectibles-market", GROUPS / "zhongxing/collectibles/collectibles-market.blend"),
        ("market-stall-row", GROUPS / "zhongxing/collectibles/stall_row/stall-row.blend"),
        ("park-plot57", riverside / "park_plot57/park-plot57.blend"),
        ("bridge-park", riverside / "bridge_58_61/bridge-park.blend"),
    ])
    replacements, retired, counts = strip_plots(
        read(HERE/"ownership.json"), (59,), read(ASSETS/"layout.json"), donors
    )
    assert all(name in bridges["new_meshes"] for name in TREE_OLD)
    retired.extend(TREE_OLD)
    for name in ("COL_Outer500_Surface_02_01","COL_Outer500_Surface_03_01","COL_Outer500_Surface_03_00"):
        if name in donors:
            load_current(name,donors[name])
    lands = terrain()
    tiles = list(terrain_faces())

    def ground(point):
        e,n = point
        hit,*_ = lands.ray_cast(Vector((e,n,15)),Vector((0,0,-1)),30)
        assert hit is not None, point
        return hit.z

    sand = material("Park 59 pale warm compacted sand",(.93,.87,.73),"concrete_floor_worn_001_diff_2k.jpg")
    blue = material("Park 59 desaturated pale blue park paving",(.50,.69,.78),"tile_blue_v4_diff.jpg")
    pale = material("Park 59 pale mineral edge",(.92,.93,.88),"concrete_floor_worn_001_diff_2k.jpg")
    flags = material("Park 59 gray modular flagstones",(.70,.73,.72),"stone_floor_diff_2k.jpg")
    muted = material("Park 59 blue-gray sand skirt",(.70,.77,.85),"concrete_floor_worn_001_diff_2k.jpg")
    grass = material("Park 59 grass and planted tree well",(.45,.61,.36),"brown_mud_leaves_01_diff_2k.jpg")
    mesh = Mesh("COL_Park59_PublicPaving")
    rounds = Mesh("Park59_TreeWellStoneRims")
    zones = ctl["registered_zones_game_en"]
    paths = ctl["paving_paths_game_en"]
    placed = []
    coverage = {}

    for e,n,radius in ctl["tree_wells_east_north_radius"]:
        ring = circle(e,n,radius)
        project(mesh,triangle_parts(ring),tiles,placed,grass,lift=.027)
        inside = circle(e,n,radius-.12)
        for index,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
            inner_a,inner_b = inside[index],inside[(index+1)%len(inside)]
            top = [(*p,ground(p)+.074) for p in (a,b,inner_b,inner_a)]
            footing = [(*p,ground(p)-.024) for p in (a,b,inner_b,inner_a)]
            rounds.solid(footing,top,pale)

    for name,finish in (("sand",sand),("blue",blue),("grass_wedge",grass)):
        coverage[name] = project(mesh,triangle_parts(zones[name]),tiles,placed,finish)
    for name,width in (("folded_walk",2.40),("sand_walk",2.18),("plaza_join",1.72)):
        line = xy(paths[name])
        half = width*.5
        coverage[name] = project(mesh,list(strip(line,half-.14,-half+.14)),tiles,placed,flags)
        for left,right in ((half,half-.14),(-half+.14,-half)):
            project(mesh,list(strip(line,left,right)),tiles,placed,pale)
    for name,finish in (("blue_skirt",pale),("sand_skirt",muted),("plaza",flags)):
        coverage[name] = project(mesh,triangle_parts(zones[name]),tiles,placed,finish)
    assert coverage["sand"]>55 and coverage["plaza"]>47 and coverage["blue"]>24, coverage
    parts = [mesh.save(),rounds.save()]
    for index,(e,n,_) in enumerate(ctl["tree_wells_east_north_radius"]):
        tree = bpy.data.objects[("Outer500_Plant_018","Outer500_Plant_010")[index]].copy()
        tree.name = f"Park59_PlazaTree_{index+1}"
        tree.location = (e,n,ground((e,n))-.025)
        tree.rotation_euler.z += .54+index*1.51
        tree.scale *= .69+index*.16
        bpy.context.collection.objects.link(tree)
        parts.append(tree)

    old_view = bridges["street_views"]["59"]
    # Start inside the already built park-side footway before making the south turn.
    start = [-75.64, -181.016]
    destination = paths["sand_walk"][-1]
    stations = [start,[-75.0,-183.0],[-75.37,-185.55],*paths["sand_walk"][1:]]
    data = {
        "replaced_plot":59,"independent_adjacent_plot":61,
        "old_footprint_east_north":ctl["old_plot"]["footprint"],
        "new_meshes":[obj.name for obj in parts],
        "replacement_meshes":[obj.name for obj in replacements],
        "retired_objects":retired,"removed_shared_geometry":counts,
        "registered_view":old_view,
        "route_east_north":stations,"destination_game_m":ground(destination)+LIFT,
        "sections":[[-75.0,-183.0],[-75.37,-185.55],[-74.83,-187.55],[-73.64,-189.63],
                    [-71.75,-191.86],destination,[-68.67,-184.52],[-82.14,-189.93]],
        "finish_area_m2":coverage,"tree_wells":ctl["tree_wells_east_north_radius"],
        "paving_raised_from_existing_ground_m":LIFT,
    }
    keep = set(replacements+parts)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"park-plot59.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/"park-plot59.glb"),export_format="GLB",
                              export_cameras=False,export_lights=False)
    (ASSETS/"park-plot59.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print("CQ_PARK59",json.dumps(data))


if __name__ == "__main__":
    build()
