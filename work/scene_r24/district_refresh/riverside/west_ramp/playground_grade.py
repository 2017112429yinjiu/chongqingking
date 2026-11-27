"""Fit the two ortho-registered surfaces outside the retained court and approaches."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import bpy
from mathutils import Vector

from factory import material

HERE = Path(__file__).resolve().parent
spec = spec_from_file_location("west_court_grade", HERE.parent / "west_court/build.py")
court = module_from_spec(spec)
sys.modules[spec.name] = court
spec.loader.exec_module(court)

CONNECTOR = [(-161.9,-176.0),(-158.3,-171.9),(-150.7,-173.0),(-147.1,-175.8),
             (-151.1,-179.1),(-157.1,-180.2)]
WEDGE = [(-171.1,-185.7),(-159.0,-178.9),(-156.9,-179.3),(-160.3,-189.9),(-169.9,-187.8)]
SAND_ROUTE = [(-144.8,-181.4),(-147.4,-177.8),(-151.2,-176.6),(-156.0,-175.9),
              (-159.5,-175.),(-164.2,-173.7),(-166.0,-173.6),(-168.15,-174.1)]
LEVEL = -5.83
ROAD_A = Vector((-304.299,-116.1645))
ROAD_B = Vector((-74.8604,-173.3728))
ROAD_DIRECTION = (ROAD_B-ROAD_A).normalized()
PARK_SIDE = Vector((ROAD_DIRECTION.y,-ROAD_DIRECTION.x))
CURB_OFFSET = 5.424
SHOULDER_OFFSET = 6.47


def road_stations(easts, offset):
    return [ROAD_A+(ROAD_B-ROAD_A)*((e-ROAD_A.x)/(ROAD_B.x-ROAD_A.x))+PARK_SIDE*offset
            for e in easts]


def grade(point):
    return LEVEL + min(0., point.x+155.)*.075


def patch(name, points, slot, slope=grade):
    ring = [Vector(point) for point in points]
    if court.area(ring) < 0:
        ring.reverse()
    assert all(court.cross(b-a,c-b) >= -1e-4 for a,b,c in
               zip(ring,ring[1:]+ring[:1],ring[2:]+ring[:2])), name
    return court.Patch(name,ring,slope,slot)


def build(control, old_deck, blue, wall, tiles, blue_finish, foliage_source, ground):
    orthophoto = control["orthophoto"]
    blue_zone = patch("blue_trapezoid",orthophoto["blue_ring_east_north"],0)
    sand_outline = [(-179.2,-165.2),(-152.48,-168.28),(-151.44,-171.38),(-174.84,-182.93)]
    sand_zone = patch("pale_play_area",sand_outline,1)
    connection = patch("connector",CONNECTOR,2)
    green = patch("planted_wedge",WEDGE,3)
    shoulder_stations = road_stations((-172.5,-163.5,-157.4,-153.4,-151.5),SHOULDER_OFFSET)
    street_start = shoulder_stations[2]
    gate = shoulder_stations[3]
    lower_gate = Vector((-154.55,-169.54))
    gate_open_left,gate_open_right = road_stations((-154.9,-151.9),SHOULDER_OFFSET+.61)
    landing_direction=(lower_gate-gate).normalized()
    wing = Vector((-landing_direction.y,landing_direction.x))*1.32

    def ground_z(p):
        hit,*_ = ground.ray_cast(Vector((p.x,p.y,25)),Vector((0.,0.,-1.)))
        assert hit is not None, list(p)
        return hit.z

    def gate_slope(p):
        path_fraction = (p-gate).dot(landing_direction)
        t = min(1.,max(0.,(path_fraction-.58)/7.70))
        original = ground_z(p)
        return original*(1-t)+grade(p)*t

    access = patch("street_public_entry",[gate_open_left,gate_open_right,
                   lower_gate+wing+landing_direction*1.35,lower_gate-wing+landing_direction*1.35],
                   4,gate_slope)
    zones = [blue_zone,sand_zone,connection,green,access]
    paving, walls = court.Mesh(), court.Mesh()
    sand = material("West terrace warm aggregate with wear",(.93,.87,.75),"concrete_floor_worn_001_diff_2k.jpg")
    sand_shader = sand.node_tree.nodes.get("Principled BSDF")
    sand_shader.inputs["Emission Color"].default_value=(.44,.35,.25,1.)
    sand_shader.inputs["Emission Strength"].default_value=.18
    shoulder = material("West playground light grey access flags",(.70,.68,.62),"stone_floor_diff_2k.jpg")
    topsoil = material("West playground planted wedge soil and grass",(.42,.54,.29),"brown_mud_leaves_01_diff_2k.jpg")
    stone = material("West playground stepped retaining stone",(.62,.61,.55),"stone_wall_05_diff_2k.jpg")
    cut, areas = court.build_terrain(tiles,zones,paving,walls,require_full_coverage=False)
    assert cut and areas["blue_trapezoid"] > 95. and areas["pale_play_area"] > 200. and areas["connector"] > 30.,areas
    finishes = [blue_finish,sand,shoulder,topsoil,shoulder]
    graded = paving.make("COL_WestPlayground_GradedSurfaces",finishes)
    new_wall = walls.make("COL_WestPlayground_PerimeterSupport",[stone,stone])

    # The collision top over the old approach stays as originally authored.
    # Dress the shared flat deck only where it overlaps the traced blue ring.
    shared = court.Mesh()
    for face in old_deck.data.polygons:
        points = [old_deck.matrix_world @ old_deck.data.vertices[i].co for i in face.vertices]
        if max(abs(v.z-LEVEL) for v in points) > .004 or abs(face.normal.z)<.8:
            continue
        inside, _ = blue_zone.partition(points)
        if inside:
            shared.face([Vector((v.x,v.y,v.z+.014)) for v in inside],0)
    shared.make(blue.name,[blue_finish],blue)
    for obj in (blue,graded):
        uv = obj.data.uv_layers.active
        for face in obj.data.polygons:
            if face.material_index != 0:
                continue
            for loop in face.loop_indices:
                point = obj.data.vertices[obj.data.loops[loop].vertex_index].co
                uv.data[loop].uv=(point.x/.38,point.y/.38)

    # An existing face becomes internal only when the new route meets the deck
    # at the same height. Keep the stair, ramp, and surrounding exposed faces.
    hidden_faces = []
    for face in wall.data.polygons:
        points = [wall.matrix_world @ wall.data.vertices[i].co for i in face.vertices]
        middle = sum(points,Vector())/len(points)
        if (any(abs(p.z-LEVEL) < .012 for p in points) and middle.y > -183.
                and (blue_zone.includes(middle.xy) or connection.includes(middle.xy))
                and abs(grade(middle)-LEVEL) < .012):
            hidden_faces.append(face.index)
            continue
    # Keep original wall UVs and topology for all unaffected faces.
    assert hidden_faces and set(hidden_faces).isdisjoint({242,255,257})
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(wall.data)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.faces[i] for i in hidden_faces],context='FACES_ONLY')
    bm.to_mesh(wall.data)
    bm.free()

    planted = []
    for i,(e,n,factor) in enumerate(((-168.8,-186.1,.62),(-165.32,-184.55,1.0),
                                  (-162.2,-184.4,.51),(-161.8,-186.24,.44),
                                  (-160.2,-181.5,.40))):
        pt = Vector((e,n))
        assert green.includes(pt),(e,n)
        plant = foliage_source.copy()
        plant.name=f"WestPlayground_Wedge_Plant_{i+1}"
        plant.location=(e,n,grade(pt)-.04)
        plant.rotation_euler.z+=i*.79
        plant.scale*=factor
        bpy.context.scene.collection.objects.link(plant)
        planted.append(plant)
    return cut,[graded,new_wall,*planted],{
           "approx_blue_outline_m2":round(court.area(blue_zone.ring),3),
           "newly_graded_m2":areas,"old_wall_internal_faces":hidden_faces,
           "sand_path_east_north":SAND_ROUTE,"sand_destination_y":grade(Vector(SAND_ROUTE[-1])),
           "street_access":{
               "osm_way":59146737,"registered_segment_east_north":[list(ROAD_A),list(ROAD_B)],
               "shoulder_east_north":[list(p) for p in shoulder_stations],
               "south_curb_offset_m":CURB_OFFSET,"shoulder_centre_offset_m":SHOULDER_OFFSET,
               "original_promenade_to_osm_axis_m":39.404,
               "route_east_north":[list(street_start),list(gate),
                   list(gate+landing_direction*2.8),list(gate+landing_direction*5.7),
                   list(lower_gate),[-158.1,-171.30],[-163.35,-172.45],[-168.15,-174.1]],
               "entry_opening_east_north":[list(gate_open_left),list(gate_open_right)],
               "street_focus_east_north_up":[lower_gate.x,lower_gate.y,grade(lower_gate)+1.05]},
           "soil_roots_east_north_up":[list(p.location) for p in planted]}
