"""Build the mapped Xingchen podium and a provisional tower in local ENU."""
import json
from math import ceil
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
GROUPS = HERE.parent
sys.path[:0] = [str(GROUPS), str(GROUPS / "guoco"), str(GROUPS.parents[1] / "district_500")]
from factory import Mesh, material, terrain
from factory_glazing import glaze_material
from refresh_geometry import ASSETS, latest_donors, read, strip_plots
from riverside import make_strip, terrain_faces


def build():
    field = read(HERE / "registration.json")
    ring = [Vector(point) for point in field["ways"]["704006725"]["east_north"]]
    nw = max(ring, key=lambda pt: pt.y)
    ne = max(ring, key=lambda pt: pt.x)
    x_axis = (ne - nw).normalized()
    y_axis = Vector((x_axis.y, -x_axis.x))
    width = (ne - nw).length
    depth = max((point - nw).dot(y_axis) for point in ring)
    bvh = terrain()

    def earth(point):
        hit, _, _, _ = bvh.ray_cast(Vector((point.x, point.y, 130)), Vector((0, 0, -1)))
        if hit is None:
            raise ValueError(f"No ground at {point}")
        return hit.z

    def point(u, v, z):
        en = nw + u * x_axis + v * y_axis
        return en.x, en.y, z

    def solid(mesh, shape, bottom, top, finish):
        area = sum(a[0]*b[1] - b[0]*a[1] for a,b in zip(shape, shape[1:] + shape[:1]))
        ccw = list(reversed(shape)) if area > 0 else shape
        mesh.solid([point(u, v, bottom) for u, v in ccw],
                   [point(u, v, top) for u, v in ccw], finish)

    def block(mesh, a, b, c, d, low, high, finish):
        solid(mesh, [(a, b), (c, b), (c, d), (a, d)], low, high, finish)

    sides = [(a, b) for a, b in zip(ring, ring[1:] + ring[:1])]
    sections = [[earth(a.lerp(b, t / 10)) for t in range(11)] for a, b in sides]
    foundation = min(z for side in sections for z in side) - .52
    street_datum = earth(nw.lerp(ne, .54))
    podium_top = street_datum + 9.15
    levels = 23
    pitch = 2.92
    cap = podium_top + levels * pitch

    cream = material("Xingchen warm square panels", (.68, .62, .53), "concrete_wall_006_diff_2k.jpg")
    white = material("Xingchen weathered white side walls", (.79, .79, .74), "concrete_wall_006_diff_2k.jpg")
    slab = material("Xingchen weathered balcony and eave", (.59, .53, .46), "concrete_floor_worn_001_diff_2k.jpg")
    foot = material("Xingchen grit and sandy plinth", (.52, .50, .43), "stone_wall_05_diff_2k.jpg")
    olive = glaze_material("Xingchen faded blue-green fascia", (.22, .37, .35), .69, .08)
    olive_shadow = glaze_material("Xingchen faded green plaque shade", (.19, .32, .31), .66, .08)
    seam = glaze_material("Xingchen panel joints", (.095, .098, .080), .91)
    glass = glaze_material("Xingchen blue-grey shaded glass", (.033, .065, .077), .46, .17)
    dark = glaze_material("Xingchen dark painted security rails", (.042, .043, .038), .83)
    machine = glaze_material("Xingchen old condenser casing", (.57, .55, .49), .70)

    base = Mesh("COL_Xingchen_704006725_Podium")
    base.solid([(p.x,p.y,foundation) for p in ring], [(p.x,p.y,podium_top) for p in ring], foot)
    for local_low, thickness, projection in ((2.75,.31,.74),(5.82,.49,1.15),(8.67,.47,.75)):
        block(base, .20, -projection, width-.20, .21, street_datum+local_low,
              street_datum+local_low+thickness, slab)

    frontage = Mesh("Xingchen_Square_Panels_and_Shaded_Shops")
    for start, end, green in ((0.14, 8.5, True), (8.5, 21.7, False), (21.7, 30.4, True), (30.4, width-.12, False)):
        count = ceil((end - start) / 1.33)
        for tier in range(8):
            low = street_datum - .75 + tier * 1.17
            for col in range(count):
                left = start + (end - start) * col / count
                right = start + (end - start) * (col + 1) / count
                panel_colour = (olive_shadow if (tier + col * 3) % 7 == 0 else olive) if green else cream
                block(frontage,left+.018,-.102,right-.018,-.019,low+.018,low+1.151,panel_colour)
        block(frontage,start-.035,-.112,start+.031,-.012,street_datum-.80,podium_top-.08,seam)
    for u in (2.17, 10.81, 15.26, 22.40, 28.31, 32.94, 35.97):
        block(frontage,u,-.131,min(u+1.22,width-.1),-.102,street_datum+.82,street_datum+2.48,glass)
    for u in (24.25, 30.08):
        block(frontage, u, -.31, u+3.37, -.113, street_datum+.15, street_datum+2.59, glass)
        block(frontage, u-.09, -.48, u+3.46, -.106, street_datum+2.59, street_datum+2.75, slab)

    profile = [(3.3,4.25),(12.9,4.25),(15.2,6.56),(24.35,6.56),(26.85,4.80),
               (width-3.1,4.80),(width-3.1,depth-3.51),(3.30,depth-3.51)]
    tower = Mesh("COL_Xingchen_704006725_Tower")
    solid(tower, profile, podium_top, cap, white)
    accents = Mesh("Xingchen_Continuous_Balconies_and_Caged_Rails")
    for storey in range(levels):
        floor = podium_top + storey * pitch
        for i, (a,b) in enumerate(zip(profile, profile[1:] + profile[:1])):
            p, q = Vector(a), Vector(b)
            direction = (q - p).normalized()
            outward = Vector((direction.y, -direction.x))
            length = (q-p).length

            def extrusion(left,right,stand_off,reach,low,high,finish):
                corners = [p+direction*u+outward*v for u,v in
                           [(left,stand_off),(right,stand_off),(right,reach),(left,reach)]]
                solid(accents, corners, low, high, finish)

            balcony = i in (1, 2, 3, 4, 6)
            if balcony:
                extrusion(.06,length-.06,-.015,.86,floor,floor+.17,slab)
                extrusion(.07,length-.07,.80,.85,floor+.99,floor+1.05,dark)
                extrusion(.08,length-.08,.81,.845,floor+.42,floor+.47,dark)
                posts = max(2, ceil(length/.57))
                for index in range(posts):
                    pos = .09 + (length-.25) * index / (posts-1)
                    extrusion(pos,pos+.024,.811,.841,floor+.15,floor+1.02,dark)
            bays = max(1, int(length/2.57))
            for bay in range(bays):
                span = length/bays
                mid = span*(bay+.50)
                extrusion(mid-.64,mid+.64,-.001,.038,floor+.78,floor+2.15,glass)
                extrusion(mid-.043,mid+.043,.039,.071,floor+.76,floor+2.19,seam)
                if not balcony:
                    extrusion(mid-.74,mid+.72,-.012,.44,floor+2.16,floor+2.27,slab)
                if (bay*3+storey+i)%5 != 0:
                    extrusion(mid+.67,mid+.99,.018,.31,floor+.56,floor+.96,machine)
                if balcony and (bay+storey+2*i)%4 != 0:
                    for offset in (-.53,-.27,.00,.27,.53):
                        extrusion(mid+offset,mid+offset+.019,.786,.816,floor+1.05,floor+2.56,dark)
    terrace = Mesh("Xingchen_Roof_Edges_and_Podium_Tubs")
    solid(terrace, profile, cap, cap+.34, slab)
    for u in (5.1,19.0,32.0):
        block(terrace,u,.62,u+1.45,2.27,podium_top,podium_top+.56,cream)
    trees = []
    for index, u, scale in ((0,5.82,.62),(1,19.72,.73),(2,32.73,.57)):
        tree = bpy.data.objects["Outer500_Plant_010"].copy()
        tree.name = f"Xingchen_Podium_Planter_Tree_{index}"
        tree.location = point(u, 1.48, podium_top+.56)
        tree.scale *= scale
        bpy.context.collection.objects.link(tree)
        trees.append(tree)

    approach = [[170.0,-121.8],[178.0,-124.3],[188.0,-128.4],[197.0,-131.5],
                [200.6,-136.1],[201.2,-141.9],[201.5,-146.1]]
    walk = make_strip(
        {"id":"xingchen_west_jiefang_verge", "points":approach, "width_m":1.8,
         "finish":0, "raise_m":.018}, list(terrain_faces()), [slab,foot,cream]
    )
    walk.name = "Xingchen_Street_Approach_830761786"

    selectors = [
        ("guoco-frontages", GROUPS / "guoco/guoco-frontages.blend"),
        ("public-edges", GROUPS / "matix/public-edges.blend"),
    ]
    replacements, retired, counts = strip_plots(
        read(HERE / "ownership.json"), (27,), read(ASSETS / "layout.json"), latest_donors(selectors)
    )
    parts = [mesh.save() for mesh in (base, frontage, tower, accents, terrace)] + [*trees, walk]
    keep = {*replacements, *parts}
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "xingchen.blend"), compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS / "xingchen.glb"), export_format="GLB",
                              export_cameras=False, export_lights=False)
    plan = {
        "replacement_meshes": [obj.name for obj in replacements],
        "retired_objects": retired, "new_meshes": [obj.name for obj in parts],
        "source_plot": 27, "way": 704006725, "removed_faces": counts,
        "model_podium_levels": 3, "model_upper_levels": levels, "nominal_storey_pitch_m": pitch,
        "ground_sections_m": sections, "foundation_m": foundation, "street_datum_m": street_datum,
        "podium_top_m": podium_top, "roof_m": cap+.34,
        "game_approach_east_north": approach,
    }
    (ASSETS / "xingchen.json").write_text(json.dumps(plan, indent=2) + "\n")
    print("CQ_XINGCHEN", json.dumps(plan))


build()
