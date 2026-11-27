"""Restore only the photographed margins of the existing Zhongxing Road flyover."""
import json
from math import cos, pi, sin
from bisect import bisect_right
from pathlib import Path
from random import Random
import runpy
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(HERE.parent), str(SCENE / "district_500")]
from factory import Mesh, terrain
from riverside import make_strip, material, terrain_faces
from refresh_geometry import ASSETS, read

PLACES = {18: Vector((176.040, -2.234)), 21: Vector((121.422, -44.846))}
AXIS = Vector((183.4542 - 97.459, 3.5575 + 63.5479)).normalized()
NORMAL = Vector((-AXIS.y, AXIS.x))


def en(plot, station, lateral):
    return PLACES[plot] + AXIS * station + NORMAL * lateral


def level(index, point):
    hit = index.ray_cast(Vector((*point, 110)), Vector((0, 0, -1)), 125)[0]
    if hit is None:
        raise ValueError(f"No measured support at {tuple(point)}")
    return hit.z


def rail_box(mesh, plot, a, b, c, d, base, depth, finish):
    points = [en(plot, s, cross) for s, cross in ((a, c), (b, c), (b, d), (a, d))]
    bottom = [(*p, base(p)) for p in points]
    mesh.solid(bottom, [(x, y, z + depth) for x, y, z in bottom], finish)


def tint(name, rgb):
    ink = bpy.data.materials.new(name)
    ink.diffuse_color = (*rgb, 1)
    return ink


def leaves(mesh, center, height, reach, rng, colors, number):
    # Independently authored small polygonal leaves, used at player viewing distance.
    for i in range(number):
        angle = rng.random() * (2 * pi)
        turn = Vector((cos(angle), sin(angle)))
        side = Vector((-turn.y, turn.x))
        reach_here = reach * rng.uniform(.20, 1.00)
        midpoint = center.xy + turn * reach_here
        h = center.z + height * rng.uniform(.30, 1.00)
        span = reach * rng.uniform(.16, .40)
        points = [midpoint - turn * span, midpoint + side * span * .64,
                  midpoint + turn * span, midpoint - side * span * .64]
        tip = (*midpoint, h + span * .36)
        for j, k in enumerate((1, 2, 3, 0)):
            mesh.face([(*points[j],h-span*.17),(*points[k],h-span*.17),tip], colors[i % len(colors)])


def lower_margin(ground, finishes):
    axis = [list(en(21, s, 4.90)) for s in range(-16, 13, 2)]
    strips = {"id": "Zhongxing21_public_margin", "points": axis, "width_m": 1.84, "finish": 1, "raise_m": .036}
    footway = make_strip(strips, list(terrain_faces()), [finishes["stone"], finishes["flags"], finishes["edge"]])
    footway.name = "COL_Zhongxing21_Public_Footway"
    stations = [x * .5 for x in range(-32,25)]
    probes = [((v.co.xy-PLACES[21]).dot(AXIS),(v.co.xy-PLACES[21]).dot(NORMAL),v.co.z)
              for v in footway.data.vertices]
    # The original embankment has a short crossfall above the player limit. Seat a
    # shallow stone cap on it, following the longitudinal grade above local peaks.
    center = [max(z - (c - 4.90)*.034 - abs(s - u)*.19 for u,c,z in probes) for s in stations]

    def graded(point):
        vector = point - PLACES[21]
        s, c = vector.dot(AXIS), vector.dot(NORMAL)
        i = min(max(bisect_right(stations,s)-1,0),len(stations)-2)
        part = min(max((s - stations[i]) / .5, 0),1)
        return center[i]*(1-part)+center[i+1]*part+(c-4.90)*.034

    raise_to_clear = max(0.0,max(v.co.z-graded(v.co.xy) for v in footway.data.vertices)) + .008

    def paved(point):
        s = (point - PLACES[21]).dot(AXIS)
        blend = min(1,max(0,min(s-stations[0],stations[-1]-s)/2.0))
        existing = level(ground,point) + .036
        return existing*(1-blend)+(graded(point)+raise_to_clear)*blend

    for vertex in footway.data.vertices:
        height = paved(vertex.co.xy)
        assert height >= vertex.co.z - .012, (tuple(vertex.co), height)
        vertex.co.z = height
    footway.data.update()
    curb = Mesh("COL_Zhongxing21_GreenRailCurb")
    rail = Mesh("COL_Zhongxing21_PaintedGreenRail")
    shrub = Mesh("Zhongxing21_LowUndercroftLeaves")
    edging = Mesh("Zhongxing21_StoneShoulderEnds")
    rng = Random(59146775)
    base = lambda p: paved(p) - .075
    for a,b in zip(stations,stations[1:]):
        for c in (3.98,5.82):
            p, q = en(21,a,c),en(21,b,c)
            face = [(*p,level(ground,p)-.045),(*q,level(ground,q)-.045),(*q,paved(q)),(*p,paved(p))]
            edging.face(face if c < 4.9 else face[::-1], finishes["edge"])
    for s in (stations[0], stations[-1]):
        p, q = en(21,s,3.98),en(21,s,5.82)
        face = [(*p,level(ground,p)-.045),(*q,level(ground,q)-.045),(*q,paved(q)),(*p,paved(p))]
        edging.face(face[::-1] if s == stations[0] else face, finishes["edge"])
    # The narrow line remains outside the foliage and existing piers.
    for i in range(-14, 10):
        rail_box(curb, 21, i, i + 1, 3.78, 3.99, base, .15, finishes["edge"])
        rail_box(rail, 21, i, i + 1, 3.85, 3.90, lambda p: base(p) + .76, .047, finishes["green"])
        rail_box(rail, 21, i, i + 1, 3.85, 3.89, lambda p: base(p) + .24, .028, finishes["green"])
        for delta in (0.0, .22, .44, .66, .88):
            s = i + delta
            rail_box(rail, 21, s, s + .028, 3.85, 3.89, lambda p: base(p) + .25, .51, finishes["green"])
        at = en(21, i + rng.uniform(.15, .85), rng.uniform(2.67, 3.23))
        leaves(shrub, Vector((*at, level(ground, at))), rng.uniform(.39,.62),rng.uniform(.27,.53),rng,finishes["leaf"],19)
    walk = [list(en(21, s, c)) for s, c in ((-13.5,4.90),(-10,4.92),(-6,4.85),(-2,4.82),(2,4.94),(6,5.05),(9.3,4.93))]
    return [footway, curb.save(), rail.save(), shrub.save(), edging.save()], [(*p,paved(Vector(p))) for p in walk]


def deck_index():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ASSETS.parent / "frontage_r24/frontage.glb"))
    imported = set(bpy.data.objects) - before
    deck, = [ob for ob in imported if ob.name.startswith("COL_R24_LinkDeck")]
    vertices = [deck.matrix_world @ v.co for v in deck.data.vertices]
    faces = [tuple(face.vertices) for face in deck.data.polygons]
    bounds = BVHTree.FromPolygons(vertices, faces)
    for ob in imported:
        bpy.data.objects.remove(ob, do_unlink=True)
    return bounds


def upper_edge(deck, finishes):
    planters = Mesh("Zhongxing18_ShoulderPlanterBoxes")
    flowers = Mesh("Zhongxing18_PlantedUpperEdge")
    rng = Random(180591)
    support_points = []
    # The running surface and its original collision stay underneath the planted margins.
    for side in (-1,1):
        def sill(point):
            return level(deck, point - NORMAL * (.32 * side)) - .037
        for i in range(-9, 12, 2):
            a, b = sorted((side*2.58, side*2.81))
            rail_box(planters, 18, i, i + 1.86, a, b, sill, .25, finishes["stone"])
            for j in range(4):
                at = en(18, i + .27 + j*.44, side*2.70)
                base = sill(at) + .25
                support_points.append([*at,base])
                leaves(flowers, Vector((*at,base)), rng.uniform(.21,.37), .27, rng, finishes["flowers"], 25)
    return [planters.save(),flowers.save()],support_points


def main(directory):
    assert Path(bpy.data.filepath).name in ("city_and_outer.local.blend", "city_and_outer.before_zhongxing_18_21.local.blend")
    previous = runpy.run_path(str(SCENE / "district_refresh/riverside/east_bend/build.py"))
    panda = runpy.run_path(str(HERE.parent / "panda_15_17/build.py"))
    ground = terrain()
    deck = deck_index()
    finishes = {
        "stone": material("Zhongxing pale worn bridge concrete", (.72,.74,.77), "concrete_wall_006_diff_2k.jpg"),
        "flags": material("Zhongxing lower roadside pale flags", (.69,.72,.72), "stone_floor_diff_2k.jpg"),
        "edge": material("Zhongxing lower ash stone edge", (.64,.69,.66), "concrete_floor_worn_001_diff_2k.jpg"),
        "green": tint("Zhongxing worn green barrier enamel", (.044,.124,.091)),
        "leaf": [tint(f"Zhongxing broad leaf {i}", rgb) for i,rgb in enumerate(((.094,.143,.049),(.117,.179,.058),(.060,.115,.048),(.153,.194,.044)))],
    }
    finishes["flowers"] = [*finishes["leaf"],*[tint(f"Zhongxing flower color {i}", rgb) for i,rgb in enumerate(((.37,.058,.23),(.56,.086,.33),(.43,.104,.39)))]]
    built, walk = lower_margin(ground, finishes)
    on_bridge, roots = upper_edge(deck, finishes)
    built.extend(on_bridge)
    # Both stock occurrences are already absent in the retained outer source and A1 parent.
    absent = {"Outer500_Street_furniture": {"dfea339f7f61a41f4c0ac3e3": 2}}
    replacements, retired, counts = panda["retire"](previous, (18,21), HERE / "ownership.json", absent)
    lower = walk
    upper = [(*p, level(deck,p)) for p in (en(18, s,0.0) for s in range(-11,13,3))]
    plan = {"retired_plots":[18,21], "retired_objects":retired, "removed_face_counts":counts,
            "new_meshes":[item.name for item in built],"replacement_meshes":[item.name for item in replacements],
            "lower_walk_21":lower,"upper_scooter_18":upper,"upper_planter_contact_enu":roots,
            "lower_existing_terrain_21":[[e,n,level(ground,Vector((e,n)))] for e,n,_ in lower],
            "route_scope":"21 roadside walking strip; 18 carriageway with bike controls only",
            "lower_width_m":1.84, "osm_way":59146775,"already_absent_furniture_faces":absent}
    contents = set(built + replacements)
    for ob in list(bpy.data.objects):
        if ob not in contents:
            bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "zhongxing-bridge-18-21.blend"), compress=True,relative_remap=True)
    donor=read(ASSETS / "panda-15-17.json")["borrowed_materials"]
    plan["borrowed_materials"] = previous["borrow_slots"](replacements,{name:set(values.values()) for name,values in donor.items()})
    bpy.ops.export_scene.gltf(filepath=str(directory / "zhongxing-bridge-18-21.glb"),export_format="GLB",export_cameras=False,export_lights=False)
    (directory / "zhongxing-bridge-18-21.json").write_text(json.dumps(plan,indent=2)+"\n")
    print("CQ_ZHONGXING_18_21",counts,len(upper),len(lower),len(roots))


if __name__ == "__main__":
    main(Path(sys.argv[-1]).resolve())
