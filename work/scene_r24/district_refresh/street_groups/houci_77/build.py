"""Build the observed Houci surface bend against the composed district in Blender 4.3.2."""
from collections import Counter
import json
from math import ceil
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
DISTRICT = HERE.parents[2] / "district_500"
sys.path[:0] = [str(HERE.parent), str(DISTRICT)]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, read
from retire_plots import STATIC_FIXTURE, fingerprint, remove_faces
from riverside import material


def station_rows(coords):
    """Interpolate the surveyed plan vertices densely through the bend."""
    points = [Vector(point) for point in coords]
    centers = []
    for i, (a, b) in enumerate(zip(points, points[1:])):
        prior = points[max(i - 1, 0)]
        following = points[min(i + 2, len(points) - 1)]
        steps = ceil((b - a).length / .44)
        for step in range(steps):
            t = step / steps
            centers.append((2*a + (-prior+b)*t + (2*prior-5*a+4*b-following)*t*t
                            + (-prior+3*a-3*b+following)*t*t*t) * .5)
    centers.append(points[-1])
    distance = 0.
    rows = []
    for i, p in enumerate(centers):
        previous = centers[max(0, i-1)]
        tangent = (centers[min(i+1, len(centers)-1)] - previous).normalized()
        distance += (p-previous).length
        rows.append((p, Vector((-tangent.y, tangent.x)), distance))
    return rows


def build_surface(rows, ground, materials):
    asphalt, paving, verge, cut_stone, gutter, light_flags = materials
    road = Mesh("COL_Houci_1306489251_Asphalt")
    walk = Mesh("COL_Houci_Public_Flagstones")
    curbs = Mesh("COL_Houci_Street_Kerbs")
    grass = Mesh("Houci_Inside_Turf_Verger")
    apron = Mesh("COL_Houci_Guoco_Outer_Apron")

    def at(row, offset, raise_m):
        center, normal, distance = row
        p = center + normal*offset
        # Taper raised elements at the two existing road tie-ins.
        factor = max(.18, min(1., distance/3., (rows[-1][2]-distance)/3.))
        return p.x, p.y, ground(p) + raise_m*factor

    def strip(mesh, a, b, low, high, height_low, height_high, finish, subdivisions=1):
        for i in range(subdivisions):
            left, right = i/subdivisions, (i+1)/subdivisions
            va, vb = low+(high-low)*left, low+(high-low)*right
            za, zb = height_low+(height_high-height_low)*left, height_low+(height_high-height_low)*right
            mesh.face([at(a, va, za), at(b, va, za), at(b, vb, zb), at(a, vb, zb)], finish)

    for a, b in zip(rows, rows[1:]):
        strip(road,a,b,-3.40,0.,.050,.085,asphalt,8)
        strip(road,a,b,0.,3.40,.085,.050,asphalt,8)
        strip(road,a,b,-3.57,-3.40,.041,.050,gutter)
        strip(road,a,b,3.40,3.57,.050,.041,gutter)
        strip(curbs,a,b,-3.72,-3.57,.147,.147,cut_stone)
        strip(curbs,a,b,3.57,3.72,.147,.147,cut_stone)
        # Two oppositely wound face strips close the step between the road and the cap.
        strip(curbs,a,b,-3.57,-3.57,.147,.042,cut_stone)
        strip(curbs,a,b,3.57,3.57,.042,.147,cut_stone)
        strip(walk,a,b,-6.77,-3.72,.098,.147,paving,8)
        strip(walk,a,b,3.72,5.86,.147,.111,paving,6)
        strip(curbs,a,b,-6.77,-6.77,.028,.098,cut_stone)
        strip(curbs,a,b,5.86,5.86,.111,.028,cut_stone)

        # The imaged inner green pocket is along the bottom of the bend.
        if a[0].x > 190. and b[0].x < 224. and b[0].y < -28.:
            strip(grass,a,b,5.86,8.5,.032,.012,verge,7)

        # Outside the bend, the pale public edge widens toward the existing tower base.
        if a[0].x > 194. and b[0].x < 225. and b[0].y < -28.:
            width = max(0., min(1., (a[0].x-194.)/7., (225.-b[0].x)/9.))
            if width > .10:
                strip(apron,a,b,-6.77-2.65*width,-6.77,.032,.098,light_flags,6)

    return [mesh.save() for mesh in (road, walk, curbs, grass, apron)], at


def remove_77():
    scene = bpy.context.scene
    stock = read(ASSETS/"layout.json")
    meta = read(HERE/"ownership.json")["77"]
    wanted = {name: Counter(ident for block in values for ident in block["faces"])
              for name, values in meta.items()}
    whose = [i for i, item in enumerate(stock["household"]) if item["plot"] == 77]
    # Read the fixtures' per-house fingerprints from the original layout assembly.
    with bpy.data.libraries.load(str(DISTRICT/"outer_district.blend"),link=True) as (_, data):
        data.objects = [STATIC_FIXTURE]
    original = data.objects[0]
    assert len(original.data.polygons) == 6*len(stock["household"])
    if whose:
        wanted[STATIC_FIXTURE] = Counter(fingerprint(original, original.data.polygons[k])
                    for i in whose for k in range(6*i, 6*i+6))

    prior = runpy.run_path(str(HERE.parents[1]/"riverside/east_bend/build.py"))
    replacements, counts = [], {}
    for name, desired in sorted(wanted.items()):
        if not desired:
            continue
        ob = prior["local_copy"](scene.objects[name])
        indices = [face.index for face in ob.data.polygons if fingerprint(ob,face) in desired]
        assert Counter(fingerprint(ob,ob.data.polygons[k]) for k in indices) == desired, name
        remove_faces(ob,indices)
        replacements.append(ob)
        counts[name] = len(indices)
    prefixes = ("Outer500_Condenser_77_",) + tuple(f"Outer500_Household_{i:03d}_" for i in whose)
    old = {"COL_Outer500_Frame_77","Outer500_InteriorFloor_77","Outer500_Joinery_77"}
    retired = sorted(ob.name for ob in scene.objects if ob.name in old or ob.name.startswith(prefixes))
    assert old.issubset(retired), retired
    return replacements, retired, counts, prior["borrow_slots"]


def move_street_lamp(street, rows, ground):
    # The original post falls inside the newly registered carriageway.
    origin = Vector((218.09656, -29.73168, 16.65849))
    selected = set()
    for face in street.data.polygons:
        points = [street.data.vertices[i].co for i in face.vertices]
        if all((p.xy - origin.xy).length < .52 and -.010 < p.z-origin.z < 4.90 for p in points):
            selected.update(face.vertices)
    faces = [face for face in street.data.polygons if selected.intersection(face.vertices)]
    assert len(faces) == 18 and all(selected.issuperset(face.vertices) for face in faces), len(faces)
    center, normal, _ = min(rows, key=lambda row: (row[0]-origin.xy).length_squared)
    plinth = center + normal*6.24
    landing = Vector((*plinth, ground(plinth)+.026))
    for i in selected:
        street.data.vertices[i].co += landing - origin
    street.data.update()
    return {"original_enu":list(origin),"on_grass_side_enu":list(landing),"faces":len(faces)}


def borrowed_finishes(folder, file, names):
    with bpy.data.libraries.load(str(folder/file), link=False) as (source, result):
        assert all(name in source.materials for name in names)
        result.materials = names
    return result.materials


def main(output):
    assembly = Path(bpy.data.filepath)
    assert assembly.name == "city_and_outer.before_houci.local.blend", assembly
    spec = read(HERE/"field-registration.json")
    source_ground = terrain()

    def ground(p):
        contact, _, _, _ = source_ground.ray_cast(Vector((*p,100.)),Vector((0,0,-1)),200.)
        assert contact is not None, tuple(p)
        return contact.z

    riverside = HERE.parents[1]/"riverside"
    asphalt, light_flags = borrowed_finishes(riverside/"binjiang","binjiang-70-73.blend",
                                            ["Binjiang entry asphalt wear","Binjiang Small grey street flags"])
    paving, grass = borrowed_finishes(riverside/"park_edge_finish","park-edge-finish.blend",
                                     ["Park Edge neutral grey stone slabs","Park Edge mixed green turf"])
    mats = (asphalt, paving, grass,
        material("Houci sawn grey granite kerb",(.78,.78,.74),"concrete_floor_worn_001_diff_2k.jpg"),
        material("Houci dark concrete gutter",(.42,.43,.43),"concrete_floor_worn_001_diff_2k.jpg"),
        light_flags,
    )

    rows = station_rows(spec["design"]["west_to_east_road_east_north"])
    objects, point = build_surface(rows, ground, mats)
    replacements, retired, counts, borrow = remove_77()
    lamp = move_street_lamp(next(ob for ob in replacements if ob.name=="Outer500_Street_furniture"), rows, ground)

    def row_at(target):
        return min(rows,key=lambda row: (row[0]-Vector(target)).length_squared)

    stations = [point(row_at(en),4.77,.126) for en in
                ([192.,-31.1],[195.,-31.8],[199.,-32.9],[202.,-33.53],
                 [205.1,-33.8],[208.2,-34.0],[211.,-34.1])]
    sections = [[point(row_at(en), offset,0.)[:2] for offset in [-6.,-4.3,-3.65,-3.,0.,3.,3.65,4.65,5.40]]
                for en in ([189.,-30.],[196.,-31.8],[202.,-33.5],[207.,-34.],[212.,-33.85],
                           [218.,-32.5],[224.,-29.9],[230.,-26.3],[238.,-19.4])]
    origin, terminus = stations[0], stations[-1]
    record = {"way":1306489251,"retired_plots":[77],"retired_objects":retired,
              "retired_face_counts":counts,"new_meshes":[ob.name for ob in objects],
              "replacement_meshes":[ob.name for ob in replacements],
              "road_length_m":rows[-1][2],"road_axis":[list(row[0]) for row in rows],"relocated_lamp":lamp,
              "sections_east_north":sections,
              "walk":{"stations":[list(p[:2]) for p in stations],"start_ray_y":origin[2]+1.,
                      "destination_y":terminus[2],"start_y":origin[2],
                      "start_aim_enu":list(stations[2])}}
    # Keep editable, local replacements and surface meshes. Prior city libraries supply the shared materials.
    retained = set(objects+replacements)
    for ob in list(bpy.data.objects):
        if ob not in retained:
            bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    for ob in retained:
        if ob.name not in bpy.context.scene.objects:
            bpy.context.scene.collection.objects.link(ob)
    bpy.context.preferences.filepaths.save_version=0
    output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output/"houci-77.blend"),relative_remap=True,compress=True)
    parents = read(ASSETS/"binjiang-70-73.json")["borrowed_materials"]
    names = {name:set(slots.values()) for name, slots in parents.items()}
    record["borrowed_materials"] = borrow(replacements,names)
    bpy.ops.export_scene.gltf(filepath=str(output/"houci-77.glb"),export_format="GLB",
                             export_cameras=False,export_lights=False)
    (output/"houci-77.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    print("CQ_HOUCI_BUILD",len(rows),record["road_length_m"],counts,retired)


if __name__=="__main__":
    main(Path(sys.argv[-1]).resolve())
