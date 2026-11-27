"""Finish only the registered park surfaces and tree belt next to 59 and 61."""
import json
from pathlib import Path
import re
import runpy
import struct
import sys
from tempfile import TemporaryDirectory
import zlib

import bpy
from mathutils import Vector
import numpy as np

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(SCENE / "district_refresh/street_groups"), str(SCENE / "district_500")]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, load_current, read
from riverside import area, bounds, make_strip, part, terrain_faces

WEST_FOLD = [[-78.50,-183.29],[-76.20,-182.82],[-75.46,-183.75],[-75.70,-185.05],
             [-76.86,-186.92],[-77.87,-188.08],[-78.36,-187.26],[-78.03,-185.10],[-78.77,-184.05]]
TURF_JOIN = [[-61.8,-191.65],[-59.3,-191.0],[-56.0,-191.85],[-54.55,-192.18]]
TEXTURE_SCALE = {"sand":3.6, "bluegreen":2.8, "pale":1.26, "stone":1.24, "grass":3.4, "skirt":2.6}
TREE_GROWTH = {
    "Park59_PlazaTree_1":(1.36,1.30,1.32),"Park59_PlazaTree_2":(1.31,1.28,1.28),
    "Park61_PerimeterTree_1":(1.28,1.27,1.29),"Park61_PerimeterTree_2":(1.17,1.22,1.23),
    "Park61_PerimeterTree_3":(1.29,1.26,1.22),
}


def png(path, colors):
    def chunk(name, body):
        return struct.pack(">I",len(body))+name+body+struct.pack(">I",zlib.crc32(name+body))
    rows = b"".join(b"\0"+line.tobytes() for line in colors)
    header = struct.pack(">2I5B",colors.shape[1],colors.shape[0],8,2,0,0,0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",header)+chunk(b"IDAT",zlib.compress(rows,8))+chunk(b"IEND",b""))


def finishes(directory):
    size = 512
    rng = np.random.default_rng(59161)
    y,x = np.mgrid[:size,:size]/size
    grain = rng.normal(0.,3.,(size,size))
    def mottling(cells):
        lattice = rng.normal(0., 1., (cells, cells))
        row, col = np.floor(y*cells).astype(int), np.floor(x*cells).astype(int)
        v, u = y*cells-row, x*cells-col
        v, u = v*v*(3-2*v), u*u*(3-2*u)
        upper = (1-u)*lattice[row,col] + u*lattice[row,(col+1)%cells]
        lower = (1-u)*lattice[(row+1)%cells,col] + u*lattice[(row+1)%cells,(col+1)%cells]
        return (1-v)*upper + v*lower

    natural = .32*mottling(5) + .40*mottling(13) + .56*mottling(31)
    small_grain = mottling(97) + .28*grain
    # Stone courses run along the shorter side of the repeating metre-scale tile.
    vx = (x+.25*(y>=.5)) % .5
    vy = y % .5
    joint = (np.minimum.reduce([vx,.5-vx,vy,.5-vy])<.0045)
    slab = np.where(((x>=.5) ^ (y>=.5)),2.8,-1.5)
    recipes = {
        "sand":("Park Edge fine unjointed pale sand",(199,183,150),3.7*small_grain+2.6*natural,.95),
        "bluegreen":("Park Edge matte blue-green aggregate",(94,152,151),3.4*small_grain+2.6*natural,.89),
        "pale":("Park Edge pale mineral kerb",(181,187,177),3.3*small_grain+2.8*natural,.90),
        "stone":("Park Edge neutral grey stone slabs",(144,149,147),grain+5.4*natural+slab-29.*joint,.93),
        "grass":("Park Edge mixed green turf",(67,108,51),5.6*small_grain+14.5*natural,.98),
        "skirt":("Park Edge grey blue-green surround",(129,164,162),3.2*small_grain+2.8*natural,.91),
    }
    materials = {}
    for key,(name,color,delta,roughness) in recipes.items():
        path = directory/(key+"-park-edge.png")
        rgb = np.round(np.clip(np.asarray(color)[None,None,:]+delta[:,:,None],0,255)).astype(np.uint8)
        png(path,rgb)
        image = bpy.data.images.load(str(path))
        image.pack()
        finish = bpy.data.materials.new(name)
        finish.diffuse_color = (*(float(v)/255 for v in color),1)
        finish.use_nodes = True
        nodes = finish.node_tree.nodes
        shader = nodes.get("Principled BSDF")
        shader.inputs["Roughness"].default_value = roughness
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = image
        finish.node_tree.links.new(texture.outputs["Color"],shader.inputs["Base Color"])
        materials[key]=finish
    return materials


def paint(obj, materials, by_suffix, east_limit=None):
    mesh = obj.data
    originals = list(mesh.materials)
    choices = {}
    for key,material in materials.items():
        choices[key] = len(mesh.materials)
        mesh.materials.append(material)
    uv = mesh.uv_layers.active
    changed = {}
    for face in mesh.polygons:
        points = [obj.matrix_world @ mesh.vertices[index].co for index in face.vertices]
        if east_limit is not None and min(p.x for p in points)<east_limit:
            continue
        name = re.sub(r"\.\d{3}$","",originals[face.material_index].name)
        finish = next((key for suffix,key in by_suffix if name.endswith(suffix)),None)
        if finish is None:
            continue
        face.material_index = choices[finish]
        period = TEXTURE_SCALE[finish]
        for i,point in zip(face.loop_indices,points):
            uv.data[i].uv=(point.x/period,point.y/period)
        changed[finish] = changed.get(finish,0)+1
    assert changed, obj.name
    used = {face.material_index for face in mesh.polygons}
    for index in reversed(range(len(mesh.materials))):
        if index not in used:
            mesh.materials.pop(index=index)
    return changed


def build(directory):
    raw = HERE.parent
    from59 = raw / "park_plot59/park-plot59.blend"
    from61 = raw / "park_plot61/park-plot61.blend"
    bridge = raw / "bridge_58_61/bridge-park.blend"
    maps = (
        ("COL_Park59_PublicPaving",from59,(
            ("compacted sand","sand"),("blue park paving","bluegreen"),("planted tree well","grass"),
            ("modular flagstones","stone"),("mineral edge","pale"),("sand skirt","skirt"),
        ),None),
        ("Park59_TreeWellStoneRims",from59,(("mineral edge","pale"),),None),
        ("Park61_WestParkEdgePath",from61,(("grey stone path","stone"),("ground edge","pale")),None),
        ("Park61_NearTreeBelt",from61,(("dry leaves","grass"),),None),
        ("BridgePark_EastGroundWalk",bridge,(("saw-cut slab","stone"),("curb band","pale")),-88.0),
        ("BridgePark_ChangbinParkFootway",bridge,(("saw-cut slab","stone"),("curb band","pale")),-87.),
    )
    materials = finishes(directory)
    replacement, counts = [], {}
    for name,donor,mapping,edge in maps:
        obj = load_current(name,donor)
        counts[name] = paint(obj,materials,mapping,edge)
        replacement.append(obj)
    park57_plan = read(ASSETS / "park-plot57.json")
    for name in ("COL_Outer500_Surface_02_01","COL_Outer500_Surface_03_01","COL_Outer500_Surface_03_00",
                 "COL_Outer500_Surface_04_00","COL_Outer500_Surface_04_01"):
        if name in park57_plan["replacement_meshes"]:
            load_current(name,raw / "park_plot57/park-plot57.blend")
    tiles = list(terrain_faces())
    ground = terrain()
    geometry = runpy.run_path(str(raw / "park_plot59/build.py"),run_name="park59_surface_projection")
    paved = replacement[0]
    retained_faces = []
    fill_bounds = bounds(geometry["xy"](WEST_FOLD))
    for poly in paved.data.polygons:
        ring = [paved.matrix_world@paved.data.vertices[index].co for index in poly.vertices]
        box = bounds(ring)
        if area(ring)>.000002 and part(box,fill_bounds):
            retained_faces.append((box,ring))
    fill = Mesh("ParkEdge_WestFoldGreyReturn")
    filled = geometry["project"](fill,geometry["triangle_parts"](WEST_FOLD),tiles,
                                 retained_faces,materials["stone"],lift=.061)
    assert 2.<filled<14.,filled
    patch = fill.save()
    for face in patch.data.polygons:
        for index in face.loop_indices:
            point = patch.data.vertices[patch.data.loops[index].vertex_index].co
            patch.data.uv_layers.active.data[index].uv=(point.x/TEXTURE_SCALE["stone"],point.y/TEXTURE_SCALE["stone"])
    seeded = make_strip({"id":"ParkEdge_TreeBandTurf","points":TURF_JOIN,"width_m":2.20,"finish":0,"raise_m":.039},
                        tiles,[materials["grass"],materials["pale"],materials["grass"]])
    seeded.name="ParkEdge_TreeBandTurf"
    grass_uv = seeded.data.uv_layers.active
    for loop in seeded.data.loops:
        point = seeded.data.vertices[loop.vertex_index].co
        grass_uv.data[loop.index].uv=(point.x/TEXTURE_SCALE["grass"],point.y/TEXTURE_SCALE["grass"])
    new_parts = [patch,seeded]
    tree_roots = ((-59.2,-190.8,1.10,18),(-56.13,-191.9,1.11,10),(-51.21,-193.77,.89,18))
    trees = []
    for index,(e,n,scale,donor) in enumerate(tree_roots,1):
        ground_z,*_ = ground.ray_cast(Vector((e,n,9)),Vector((0,0,-1)),20)
        assert ground_z is not None,(e,n)
        trees.append({"name":f"ParkEdge_MatureBeltTree_{index}","donor":f"Outer500_Plant_{donor:03d}",
                      "east_north_up":[e,n,ground_z.z-.044],"scale":scale,"yaw_offset_rad":.84+index*1.13})

    manifest={"new_meshes":[obj.name for obj in new_parts],
              "replacement_meshes":[obj.name for obj in replacement],
              "retired_objects":[],"painted_faces":counts,"uv_tile_m":TEXTURE_SCALE,
              "tree_local_scale":TREE_GROWTH,"planted_trees":trees,
              "west_fold_game_en":WEST_FOLD,"exposed_substrate_covered_m2":filled}
    keep=set(replacement+new_parts)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"park-edge-finish.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/"park-edge-finish.glb"),export_format="GLB",
                              export_cameras=False,export_lights=False)
    (ASSETS/"park-edge-finish.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print("CQ_PARK_EDGE_FINISH",json.dumps(manifest))


if __name__ == "__main__":
    if Path(bpy.data.filepath).name != "outer_district.blend":
        raise ValueError("Open outer_district.blend before running this script.")
    with TemporaryDirectory() as directory:
        build(Path(directory))
