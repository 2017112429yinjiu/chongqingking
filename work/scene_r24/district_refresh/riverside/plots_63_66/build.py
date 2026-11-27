"""Build the confirmed Changbin road edges and retire only the four contradicted houses."""
import json
from math import ceil
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory

import bpy
from mathutils import Vector
import numpy as np

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
GROUPS = SCENE / "district_refresh/street_groups"
sys.path[:0] = [str(GROUPS), str(SCENE / "district_500")]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, latest_donors, load_current, read, strip_plots
from retire_plots import fingerprint
from riverside import make_strip, material, terrain_faces

PLOTS = (63, 64, 65, 66)
SOURCE = "changbin-bend-and-edge"


def centre_at(axis, east):
    for first, last in zip(axis, axis[1:]):
        if (east - first[0]) * (east - last[0]) <= 0 and first[0] != last[0]:
            return Vector(first).lerp(Vector(last), (east-first[0])/(last[0]-first[0]))
    raise ValueError(("East outside registered axis", east))


def points_on_axis(axis, start, end, step=2.5):
    distances = sorted({start, end, *(float(p[0]) for p in axis if start < p[0] < end),
                        *(start + i * step for i in range(1, ceil((end-start)/step)))})
    return [centre_at(axis, e) for e in distances]


def surface(tiles, name, points, width, finish, kerb, lift):
    obj = make_strip({"id": name, "points": points, "width_m": width,
                      "finish": 0, "raise_m": lift}, tiles, [finish, finish, kerb])
    obj.name = name
    return obj


def extended_walk(points, opening=None):
    first, second = (Vector(p) for p in points[:2])
    before = opening or list(first+(first-second).normalized()*.95)
    end, previous = (Vector(p) for p in (points[-1],points[-2]))
    after = list(end+(end-previous).normalized()*.95)
    return [before,*points,after]


def closed_sections(mesh, sections, finishes):
    """Use the same cross-section for surface, soffit, both sides and end caps."""
    mesh.face(sections[0], finishes[1])
    mesh.face(sections[-1][::-1], finishes[1])
    for start, end in zip(sections, sections[1:]):
        for i in range(len(start)):
            j = (i+1) % len(start)
            mesh.face([start[i], end[i], end[j], start[j]], finishes[i])


def graded_section(point, offset, bottom, top, half_width):
    east, north = point
    # Looking east in the local EN plane, rows turn from the south top to the north top.
    return [(east, north+offset-half_width, top), (east, north+offset+half_width, top),
            (east, north+offset+half_width, bottom), (east, north+offset-half_width, bottom)]


def process_texture(path, colors, output, writer):
    texture = bpy.data.images.load(str(path), check_existing=True)
    width, height = texture.size
    rgba = np.empty(width*height*4, dtype=np.float32)
    texture.pixels.foreach_get(rgba)
    values = rgba.reshape(height,width,4)[::2,::2,0]
    values = (values-np.mean(values))*91.0
    rgb = np.clip(np.asarray(colors)[None,None,:]+values[:,:,None],0,255).astype(np.uint8)
    writer(output,rgb[::-1])
    return output


def tinted_material(name, source, color, directory, write_png):
    path = process_texture(ASSETS.parent / ("chongqing_district_"+source), color,
                           directory / (name.replace(" ","-")+".png"), write_png)
    finish = bpy.data.materials.new(name)
    finish.diffuse_color = (*(channel/255 for channel in color), 1.)
    finish.use_nodes = True
    shader = finish.node_tree.nodes["Principled BSDF"]
    shader.inputs["Roughness"].default_value = .92
    node = finish.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = bpy.data.images.load(str(path))
    node.image.pack()
    finish.node_tree.links.new(node.outputs["Color"],shader.inputs["Base Color"])
    return finish


def upper_deck(axes, old_sections, concrete, asphalt, rail, paint):
    """Extend the inside of the photographed curve where the two mapped axes separate."""
    ax = axes["1375242615"]
    outside = axes["1256839997"]
    old_axis = [[*entry["east_north"], entry["road_game_m"]] for entry in old_sections]
    deck = Mesh("COL_Changbin_InsideBend_1375242615")
    cap = Mesh("Changbin_InsideBend_ConcreteParapet")
    shoulder = Mesh("Changbin_InsideBend_EdgePaint")
    deck_sections, curb_sections, line_sections, levels = [], [], [], []
    for p in points_on_axis(ax,-25.25,-3.0,1.55):
        east = p.x
        south = max(p.y-2.40, centre_at(outside,east).y+3.02)
        north = p.y+2.30
        end_taper = min(1.,(east+25.25)/2.6,(-3.0-east)/2.35)
        north = south + max(.18,(north-south)*max(0.,end_taper))
        z = centre_at(old_axis,east).z
        deck_sections.append([(east,south,z),(east,north,z),(east,north-.16,z-.67),(east,south,z-1.06)])
        curb_sections.append(graded_section((east,north),-.10,z-.045,z+.32,.09))
        line_sections.append(graded_section((east,north),-.30,z+.008,z+.015,.045))
        levels.append([east,south,north,z])
    closed_sections(deck,deck_sections,[asphalt,concrete,concrete,concrete])
    closed_sections(cap,curb_sections,[rail]*4)
    closed_sections(shoulder,line_sections,[paint]*4)
    return [mesh.save() for mesh in (deck,cap,shoulder)], levels


def low_ramps(axes, ground, concrete, asphalt, red, paint):
    meshes, sections = [], {}
    for way,start,end,width,lift in (("1375242613",-26,36,3.85,.83),("1324001436",-26,39,3.72,.58)):
        deck = Mesh("COL_Changbin_LowRamp_"+way)
        stripe = Mesh("Changbin_LowRamp_Edge_"+way)
        rows, low_edge, high_edge, stats = [], [], [], []
        for p in points_on_axis(axes[way],start,end,2.0):
            length = min(p.x-start,end-p.x)
            blend = min(1.,length/6.)
            up = ground(p) + .055 + blend*lift
            south, north = ground(p+Vector((0,-width/2))),ground(p+Vector((0,width/2)))
            bottom = min(south,north,up)-.15
            rows.append(graded_section(p,0,bottom,up,width/2))
            low_edge.append(graded_section(p,-width/2+.18,up+.011,up+.020,.043))
            high_edge.append(graded_section(p,width/2-.18,up+.011,up+.020,.043))
            stats.append([*p,ground(p),up])
        deck.face(rows[0],concrete)
        deck.face(rows[-1][::-1],concrete)
        for a,b in zip(rows,rows[1:]):
            red_lane = way=="1324001436" and -12.1 <= (a[0][0]+b[0][0])/2 <= 32.1
            deck.face([a[0],b[0],b[1],a[1]],red if red_lane else asphalt)
            for i,j in ((1,2),(2,3),(3,0)):
                deck.face([a[i],b[i],b[j],a[j]],concrete)
        for edge in (low_edge,high_edge):
            closed_sections(stripe,edge,[paint]*4)
        meshes.extend([deck.save(),stripe.save()])
        sections[way] = stats
    return meshes, sections


def park_curb(points, ground, curb, metal, paint):
    edge = Mesh("COL_Changbin_ParkKerb")
    grates = Mesh("Changbin_ParkEdge_DrainGrates")
    rows = []
    for point in points:
        p = Vector(point) + Vector((0,1.22))
        rows.append(graded_section(p,0,ground(p)-.17,ground(p)+.145,.093))
    closed_sections(edge,rows,[curb]*4)
    for e,n in points[2:9:2]:
        p = Vector((e,n+1.55))
        up = ground(p)+.063
        grates.solid([(e+x,p.y+y,up-.054) for x,y in ((-.31,-.21),(.31,-.21),(.31,.21),(-.31,.21))],
                     [(e+x,p.y+y,up+.025) for x,y in ((-.31,-.21),(.31,-.21),(.31,.21),(-.31,.21))],metal)
        for i in range(-4,5):
            x=e+i*.060
            grates.face([(x-.010,p.y-.168,up+.026),(x+.010,p.y-.168,up+.026),
                         (x+.010,p.y+.168,up+.026),(x-.010,p.y+.168,up+.026)],paint)
    return [edge.save(),grates.save()]


def sheltered_wall(points, ground, stone, cap):
    face = Mesh("COL_Changbin_GarageSideRetaining")
    trim = Mesh("Changbin_GarageSideStoneCoping")
    rows, caps = [], []
    for i,point in enumerate(points):
        e,n = point
        p = Vector((e,n+1.34))
        z = ground(p)
        top = z + min(.84,.18+i*.15,.14+(len(points)-1-i)*.13)
        rows.append(graded_section(p,0,z-.32,top,.175))
        caps.append(graded_section(p,0,top-.025,top+.085,.211))
    closed_sections(face,rows,[stone]*4)
    closed_sections(trim,caps,[cap]*4)
    return [face.save(),trim.save()]


def build(directory):
    if Path(bpy.data.filepath).name != "outer_district.blend":
        raise ValueError("Open outer_district.blend first.")
    controls = read(HERE/"field-controls.json")
    riverside = HERE.parent
    donors = latest_donors([
        ("west-ramp",riverside/"west_ramp/west-ramp.blend"),
        ("guoco-frontages",GROUPS/"guoco/guoco-frontages.blend"),
        ("public-edges",GROUPS/"matix/public-edges.blend"),
        ("xingchen",GROUPS/"xingchen/xingchen.blend"),
        ("pavilion62",riverside/"pavilion62/pavilion62.blend"),
        ("collectibles-market",GROUPS/"zhongxing/collectibles/collectibles-market.blend"),
        ("market-stall-row",GROUPS/"zhongxing/collectibles/stall_row/stall-row.blend"),
        ("park-plot57",riverside/"park_plot57/park-plot57.blend"),
        ("bridge-park",riverside/"bridge_58_61/bridge-park.blend"),
        ("park-plot59",riverside/"park_plot59/park-plot59.blend"),
        ("park-plot61",riverside/"park_plot61/park-plot61.blend"),
        ("park-edge-finish",riverside/"park_edge_finish/park-edge-finish.blend"),
    ])
    ownership = read(HERE/"ownership.json")
    # These two identical generator faces are absent in both the stored original and the active donor.
    furniture = "Outer500_Street_furniture"
    absent_fingerprint = "b0caadcced2ddab9f3f0e308"
    assert all(fingerprint(bpy.data.objects[furniture], face) != absent_fingerprint
               for face in bpy.data.objects[furniture].data.polygons)
    prior_furniture = load_current(furniture, donors[furniture])
    assert all(fingerprint(prior_furniture, face) != absent_fingerprint for face in prior_furniture.data.polygons)
    groups = ownership["66"][furniture]
    assert sum(piece["faces"].count(absent_fingerprint) for piece in groups) == 2
    for piece in groups:
        piece["faces"] = [face for face in piece["faces"] if face != absent_fingerprint]
    replacements, retired, removed = strip_plots(ownership,PLOTS,read(ASSETS/"layout.json"),donors)
    assert all(f"COL_Outer500_Frame_{plot}" in retired for plot in PLOTS)
    for name in sorted(n for n in donors if n.startswith("COL_Outer500_Surface_")):
        load_current(name,donors[name])
    bvh = terrain()
    tiles = list(terrain_faces())

    def ground(point):
        hit,_,_,_ = bvh.ray_cast(Vector((*point,9)),Vector((0,0,-1)),26)
        assert hit is not None, list(point)
        return hit.z

    textures = runpy.run_path(str(riverside/"park_edge_finish/build.py"),run_name="park_surface_library")
    palette = textures["finishes"](directory)
    tex = textures["png"]
    concrete = material("Changbin weathered pale bridge concrete",(.70,.68,.63),"concrete_wall_006_diff_2k.jpg")
    asphalt = tinted_material("Changbin grey road aggregate","asphalt_02_diff_1k.jpg",(88,91,89),directory,tex)
    red = tinted_material("Changbin muted red vehicle aggregate","asphalt_02_diff_1k.jpg",(153,81,66),directory,tex)
    stone = material("Changbin grey retaining ashlar",(.58,.57,.53),"stone_wall_05_diff_2k.jpg")
    paint = tinted_material("Changbin worn pale road stripe","concrete_floor_worn_001_diff_2k.jpg",(194,194,176),directory,tex)
    metal = tinted_material("Changbin drain galvanised steel","asphalt_02_diff_1k.jpg",(67,73,72),directory,tex)
    dark = tinted_material("Changbin drain narrow open slots","asphalt_02_diff_1k.jpg",(29,32,32),directory,tex)
    axes = {key:way["east_north"] for key,way in controls["osm"]["local_ways"].items()}
    bridge = read(ASSETS/"bridge-park.json")
    bend, park = (controls["routes_east_north"][k] for k in ("bend","park"))
    pieces = [
        surface(tiles,"COL_Changbin_GarageSideWalk",extended_walk(bend),2.18,palette["stone"],palette["pale"],.059),
        surface(tiles,"COL_Changbin_ParkSideWalk",extended_walk(park),1.82,palette["stone"],palette["pale"],.052),
        surface(tiles,"Changbin_ParkTreeStrip",[[e,n-2.14] for e,n in park[7:-2]],1.25,palette["grass"],palette["grass"],.024),
    ]
    for way,start,end,width in (("59146737",-16,43,9.30),("1256859184",-38,39,7.65)):
        axis = [list(p) for p in points_on_axis(axes[way],start,end)]
        pieces.append(surface(tiles,"Changbin_GroundRoad_"+way,axis,width,asphalt,paint,.032))
    parts, curve = upper_deck(axes,bridge["modeled_vehicle_ramps"]["1256839997"],concrete,asphalt,concrete,paint)
    pieces += parts
    parts, ramps = low_ramps(axes,ground,concrete,asphalt,red,paint)
    pieces += parts + park_curb(park[7:-1],ground,palette["pale"],metal,dark) + sheltered_wall(bend,ground,stone,palette["pale"])
    metas = {"retired_plots":list(PLOTS),"new_meshes":[p.name for p in pieces],
             "replacement_meshes":[p.name for p in replacements],"retired_objects":retired,
             "removed_shared_geometry":removed,"road_axes":{k:axes[k] for k in ("59146737","1256859184")},
             "upper_curve_sections_game_enu":curve,"lower_ramp_sections_game_enu":ramps,
             "routes":{key:{"stations":route,"start_ground_m":ground(route[0]),
                            "start_ray_height_m":ground(route[0])+1.5,
                            "destination_game_m":ground(route[-1])+(.059 if key=="bend" else .052),
                            "walk_mesh":"COL_Changbin_GarageSideWalk" if key=="bend" else "COL_Changbin_ParkSideWalk"}
                       for key,route in (("bend",bend),("park",park))},
             "old_plot_centres":{pid:controls["plots"][str(pid)]["center"] for pid in PLOTS}}
    keep = set(replacements+pieces)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/(SOURCE+".blend")),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/(SOURCE+".glb")),export_format="GLB",
                              export_cameras=False,export_lights=False)
    (ASSETS/(SOURCE+".json")).write_text(json.dumps(metas,ensure_ascii=False,indent=2)+"\n")
    print("CQ_CHANGBIN",json.dumps({"new":len(pieces),"removed":retired,"shared_removed":removed}))


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        build(Path(directory))
