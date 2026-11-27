"""Remove the contradicted plot volume and join the observed park edges."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
GROUPS = SCENE / "district_refresh/street_groups"
sys.path[:0] = [str(GROUPS), str(SCENE / "district_500")]
from factory import material, terrain
from refresh_geometry import ASSETS, latest_donors, load_current, read, strip_plots
from riverside import make_strip, terrain_faces


def build():
    ctl = read(HERE / "field-controls.json")
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
        ("park-plot59", riverside / "park_plot59/park-plot59.blend"),
    ])
    replacement, retired, counts = strip_plots(
        read(HERE / "ownership.json"), (61,), read(ASSETS / "layout.json"), donors
    )
    pavilion = read(ASSETS / "pavilion62.json")["new_meshes"]
    assert "COL_Outer500_Frame_61" in retired and not set(pavilion).intersection(retired)
    for name in ("COL_Outer500_Surface_02_01","COL_Outer500_Surface_03_01",
                 "COL_Outer500_Surface_03_00","COL_Outer500_Surface_04_00"):
        if name in donors:
            load_current(name,donors[name])
    bvh = terrain()
    tiles = list(terrain_faces())

    def ground(en):
        p,_,_,_ = bvh.ray_cast(Vector((*en,10)),Vector((0,0,-1)),26)
        assert p is not None, en
        return p.z

    flags = material("Park 61 worn grey stone path",(.70,.75,.74),"stone_floor_diff_2k.jpg")
    earth = material("Park 61 grass with dry leaves",(.57,.68,.42),"brown_mud_leaves_01_diff_2k.jpg")
    curb = material("Park 61 pale ground edge",(.80,.81,.76),"concrete_floor_worn_001_diff_2k.jpg")
    path = ctl["edge_path_game_east_north"]
    belt = ctl["near_tree_belt_game_east_north"]
    pieces = []
    for name,points,width,finish,raise_m in (
        ("Park61_WestParkEdgePath",path,2.04,0,.033),
        ("Park61_NearTreeBelt",belt,2.32,1,.019),
    ):
        item = make_strip({"id":name,"points":points,"width_m":width,"finish":finish,"raise_m":raise_m},
                          tiles,[flags,earth,curb if finish==0 else earth])
        item.name = name
        pieces.append(item)
    for index,(e,n,scale) in enumerate(ctl["trees_game_east_north_scale"],1):
        old = bpy.data.objects[("Outer500_Plant_024","Outer500_Plant_010","Outer500_Plant_018")[index-1]]
        tree = old.copy()
        tree.name = f"Park61_PerimeterTree_{index}"
        tree.location = (e,n,ground((e,n))-.055)
        tree.rotation_euler.z += 1.26*index
        tree.scale *= scale
        bpy.context.collection.objects.link(tree)
        pieces.append(tree)
    eye = ctl["camera"]
    e,n = eye["east_north_from_prior_registration_m"]
    data = {"replaced_plot":61,"route_east_north":path,
            "destination_game_m":ground(path[-1]),"new_meshes":[part.name for part in pieces],
            "replacement_meshes":[obj.name for obj in replacement],"retired_objects":retired,
            "removed_shared_geometry":counts,"old_center_enu":ctl["old_plot_center_east_north"],
            "street_view":{"eye_enu":[e,n,ground((e,n))+eye["device_height_m"]],
                           "heading_deg":eye["heading_deg"],"pitch_deg":eye["pitch_deg"],
                           "vertical_fov_deg":eye["vertical_fov_deg"],"frame_px":eye["frame_px"]}}
    keep = set(replacement + pieces)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "park-plot61.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS / "park-plot61.glb"),export_format="GLB",
                              export_cameras=False,export_lights=False)
    (ASSETS / "park-plot61.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print("CQ_PARK61",json.dumps(data))


build()
