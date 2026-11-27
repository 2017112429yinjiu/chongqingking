"""Reopen the source in Blender 4.3.2 and measure the loaded road surfaces."""
import json
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[3] / "project/chongqing_godot_v05/assets/district_500"
PLAN = json.loads((ASSETS / "raijiapo-east-bend.json").read_bytes())
SCENE = bpy.context.scene
GRAPH = bpy.context.evaluated_depsgraph_get()
OBJECTS = SCENE.objects
NAMES = PLAN["replacement_meshes"] + PLAN["new_meshes"]
ASSEMBLED = Path(bpy.data.filepath).name == "city_and_outer.local.blend"


def surface(name, point, height, window=.65):
    world = OBJECTS[name].matrix_world
    local = world.inverted()
    mesh = OBJECTS[name].evaluated_get(GRAPH)
    start = local @ Vector((*point, height+window))
    down = local.to_3x3() @ Vector((0, 0, -1))
    hit, at, normal, _ = mesh.ray_cast(start, down, distance=2*window)
    if hit and (world.to_3x3() @ normal).normalized().z > .22:
        return round((world @ at).z, 5)
    return None


def section_report():
    sections = {}
    for way, rows in PLAN["road_sections_enu_m"].items():
        name = "COL_EastRoad_" + ("PortalApproach_" if way in ("1256840005", "1256840006") else "") + way
        results = []
        for index, (a, b) in enumerate(zip(rows, rows[1:])):
            start, end = Vector(a[0]), Vector(b[0])
            tangent = (end-start).normalized()
            cross = Vector((-tangent.y, tangent.x))
            height = (a[2]+b[2])*.5
            offsets = (0.,) if way == "1375242615" and index < 3 else (-.60, 0., .60)
            for offset in offsets:
                point = start.lerp(end,.5)+cross*offset
                hit = surface(name, point, height)
                assert hit is not None and abs(hit-height)<.17,(way,index,offset,hit,height)
                results.append({"enu": [round(k,4) for k in point], "offset":offset,
                                "height":hit, "rise_per_m":round((b[2]-a[2])/(b[1]-a[1]),4)})
        sections[way] = {"name":name,"count":len(results),"samples":results}
    return sections


def shared_road(way, ramp, portal=False):
    rows = PLAN["road_sections_enu_m"][way]
    a,b = [Vector(row[0]) for row in rows[:2]]
    direction = (b-a).normalized()
    left = Vector((-direction.y,direction.x))
    z = rows[0][2]
    result = []
    next_road = "COL_EastRoad_" + ("PortalApproach_" if portal else "") + way
    names = ["COL_Raijiapo_Ramp_"+ramp, next_road]
    for ofs in (-.65,0.,.65):
        for step in (-.55,-.32,-.13,.06,.25,.46,.68):
            point = a+direction*step+left*ofs
            heights = {name:surface(name,point,z) for name in names}
            covered = [h for h in heights.values() if h is not None]
            assert covered and max(abs(h-z) for h in covered)<.25,(way, step, ofs, heights, z)
            result.append({"along_m":step,"across_m":ofs,"heights":heights})
    assert all(any(item["heights"][name] is not None for item in result) for name in names)
    return result


def reports():
    for name in NAMES:
        assert OBJECTS.get(name) and OBJECTS[name].data.uv_layers.active, name
        assert all(OBJECTS[name].data.materials), name
    for name, slots in PLAN["borrowed_materials"].items():
        donor_names = {mat.name for mat in OBJECTS[name].data.materials}
        assert set(slots.values()) <= donor_names, (name, sorted(donor_names))
    assert PLAN["garage_removed_solid_faces"] == 5
    report = {"blender":bpy.app.version_string, "assembly":ASSEMBLED,
              "authored_meshes":len(PLAN["new_meshes"]), "replacements":len(PLAN["replacement_meshes"]),
              "retired_objects":len(PLAN["retired_objects"]),"sections":section_report(),
              "portal_joins": {"1256840005":shared_road("1256840005","1256840000",portal=True),
                               "1256840006":shared_road("1256840006","1324001438",portal=True)},
              "upper_ramp_join": {"1256840008":shared_road("1256840008","1256839997")}}
    if ASSEMBLED:
        assert all(OBJECTS.get(name) is None for name in PLAN["retired_objects"])
        assert OBJECTS.get("COL_Outer500_Frame_70")
        assert OBJECTS[PLAN["tree"]["name"]].data == OBJECTS[PLAN["tree"]["donor"]].data
    return report


print("CQ_EAST_SOURCE", json.dumps(reports(), ensure_ascii=False))
