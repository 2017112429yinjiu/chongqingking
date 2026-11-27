"""Fit the park-side slope and registered playground to the existing supports."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
SCENES = HERE.parents[2]
GROUPS = SCENES / "district_refresh/street_groups"
sys.path[:0] = [str(HERE), str(GROUPS), str(GROUPS / "guoco")]
from factory import Mesh, material, terrain
from factory_glazing import glaze_material
from refresh_geometry import ASSETS, load_current, read
from riverside import make_strip, terrain_faces
from playground import BLUE_DECK, build as build_playground
from playground_grade import build as fit_playground, grade, road_stations, CURB_OFFSET, SHOULDER_OFFSET

WALL = "COL_Outer500_WestCourt_Retaining"
PAVING = "COL_Outer500_WestCourt_Paving"
STREET = [-123.2,-201.93]


def street_surfaces(terrain_triangles, ground, flags, concrete):
    asphalt = material("Changbin Road worn asphalt",(.70,.70,.69),"asphalt_02_diff_1k.jpg")
    finishes = [asphalt,flags,concrete]
    easts = (-172.5,-163.5,-157.4,-153.4,-151.5)
    street = [
        ("carriageway_local",0.,CURB_OFFSET*2.0,0),
        ("south_footway",SHOULDER_OFFSET,2.08,1),
    ]
    results = []
    for name,offset,width,finish in street:
        part=make_strip({"id":name,"points":[list(p) for p in road_stations(easts,offset)],
                         "width_m":width,"finish":finish,"raise_m":.016},
                        terrain_triangles,finishes)
        part.name="WestParkStreet_"+name
        results.append(part)

    def on_ground(point,raise_m):
        hit,*_ = ground.ray_cast(Vector((point.x,point.y,25)),Vector((0.,0.,-1.)))
        return point.x,point.y,hit.z+raise_m

    kerb=Mesh("COL_WestParkStreet_SouthKerb")
    chunks=[-172.5+21.*i/21 for i in range(22)]
    low=road_stations(chunks,CURB_OFFSET-.09)
    high=road_stations(chunks,CURB_OFFSET+.08)
    for a,b,c,d in zip(low,low[1:],high[1:],high):
        ring=(a,b,c,d)[::-1]
        kerb.solid([on_ground(p,-.06) for p in ring],[on_ground(p,.089) for p in ring],concrete)
    return [*results,kerb.save()]


def build():
    site = read(ASSETS/"west-court.json")
    donor = HERE.parent/"west_court/west-court.blend"
    tiles=[]
    for tile in site["replacement_meshes"]:
        if tile.startswith("COL_Outer500_Surface_"):
            tiles.append(load_current(tile,donor))
    wall = load_current(WALL,donor)
    paving = load_current(PAVING,donor)
    blue = load_current(BLUE_DECK,donor)
    ring = [Vector(point) for point in site["ramp_polygon"]]
    mid = sum(ring,Vector((0.,0.)))/len(ring)
    terrain_index = terrain()
    stone = material("West park exposed grey masonry",(.74,.72,.66),"stone_wall_05_diff_2k.jpg")
    shader = stone.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Emission Color"].default_value=(.31,.28,.23,1.)
    shader.inputs["Emission Strength"].default_value=.12
    ramp_flags = material("West park local walking flags",(.60,.60,.55),"stone_floor_diff_2k.jpg")
    verge = material("West park leaf litter transition",(.47,.54,.39),"brown_mud_leaves_01_diff_2k.jpg")
    edge = material("West park concrete shoulder line",(.58,.59,.54),"concrete_floor_worn_001_diff_2k.jpg")
    turf = material("West park turf underbrush",(.46,.58,.34),"brown_mud_leaves_01_diff_2k.jpg")
    joint = glaze_material("West park cement setting joint",(.22,.23,.205),.92)

    # Refinish the facing hit by the fixed camera. Keep all its collision vertices.
    wall_slot = len(wall.data.materials)
    wall.data.materials.append(stone)
    facing=[]
    for face in wall.data.polygons:
        loc=wall.matrix_world@face.center
        if -145.<loc.x<-132.25 and -201.8<loc.y<-181.0 and abs(face.normal.z)<.35:
            face.material_index=wall_slot
            facing.append(face.index)
    assert {242,255,257}.issubset(facing)

    pave_slot=len(paving.data.materials)
    paving.data.materials.append(ramp_flags)
    ramp_faces=[]
    for face in paving.data.polygons:
        loc=paving.matrix_world@face.center
        q=loc.to_2d()
        crosses=[(b-a).cross(q-a) for a,b in zip(ring,ring[1:]+ring[:1])]
        if abs(face.normal.z)>.93 and (all(v>=0 for v in crosses) or all(v<=0 for v in crosses)):
            face.material_index=pave_slot
            ramp_faces.append(face.index)
    assert ramp_faces
    mesh = paving.data
    ramp_bvh = BVHTree.FromPolygons(
        [paving.matrix_world@vertex.co for vertex in mesh.vertices],
        [list(face.vertices) for face in mesh.polygons],
    )
    seams=Mesh("WestRamp_Stone_Landing_Joints")
    for d in (.035,.49,.956):
        a=ring[0].lerp(ring[3],d)
        b=ring[1].lerp(ring[2],d)
        c=ring[0].lerp(ring[3],d+.004)
        d2=ring[1].lerp(ring[2],d+.004)
        ends=(a.lerp(b,.025),a.lerp(b,.975),c.lerp(d2,.975),c.lerp(d2,.025))
        surface=[]
        for p in ends:
            hit,*_=ramp_bvh.ray_cast(Vector((p.x,p.y,2.)),Vector((0.,0.,-1.)))
            assert hit is not None
            surface.append((p.x,p.y,hit.z+.007))
        seams.face(surface,joint)

    soils=[]
    terrain_triangles=list(terrain_faces())
    for name,a,b in (("west",ring[0],ring[3]),("east",ring[1],ring[2])):
        side=(b-a).normalized()
        away=Vector((-side.y,side.x))
        if away.dot((a+b)*.5-mid)<0.:
            away=-away
        points=[list(a.lerp(b,t)+away*.76) for t in (.13,.36,.65,.87)]
        strip=make_strip({"id":f"west_ramp_verge_{name}","points":points,"width_m":1.13,"finish":0,"raise_m":.018},
                         terrain_triangles,[verge,stone,edge])
        strip.name=f"WestRamp_Verge_{name}"
        soils.append(strip)
    transitions=[
        ("deck_shoulder",[[-137.75,-187.33],[-137.51,-188.20],[-137.18,-189.35],[-136.82,-190.00]],.83),
        ("north_grass",[[-133.55,-189.10],[-133.84,-191.05],[-133.57,-194.20],[-132.85,-196.33]],1.7),
        ("west_grass",[[-144.6,-192.05],[-143.50,-194.10],[-142.34,-196.15],[-140.88,-197.65]],1.6),
    ]
    for name,points,width in transitions:
        strip=make_strip({"id":name,"points":points,"width_m":width,"finish":0,"raise_m":.022},
                         terrain_triangles,[turf,stone,verge])
        strip.name=f"WestRamp_Bank_{name}"
        soils.append(strip)
    planting=[]
    for index,(e,n,scale) in enumerate((
        (-144.34,-192.83,.27),(-143.67,-193.70,.21),(-142.63,-195.33,.32),
        (-133.53,-191.17,.29),(-133.66,-192.12,.24),(-132.82,-195.97,.39),
    )):
        hit,*_=terrain_index.ray_cast(Vector((e,n,2.)),Vector((0.,0.,-1.)))
        assert hit is not None
        collared = bpy.data.objects["Outer500_Plant_010" if index%2 else "Outer500_Plant_018"].copy()
        collared.name=f"WestRamp_Bank_Plant_{index:02}"
        collared.location=(e,n,hit.z-.05)
        collared.rotation_euler.z+=index*.73
        collared.scale*=scale
        bpy.context.scene.collection.objects.link(collared)
        planting.append(collared)
    roadside=street_surfaces(terrain_triangles,terrain_index,ramp_flags,edge)
    play_parts,blue_finish,play_plan=build_playground(blue,site["deck_elevation_m"],grade)
    changed_tiles,park_parts,park_plan=fit_playground(read(HERE/"playground-controls.json"),
        paving,blue,wall,tiles,blue_finish,bpy.data.objects["Outer500_Plant_018"],terrain_index)
    parts=[seams.save(),*soils,*planting,*play_parts,*park_parts,*roadside]
    keep={wall,paving,blue,*changed_tiles,*parts}
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"west-ramp.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/"west-ramp.glb"),export_format="GLB",
                              export_cameras=False,export_lights=False)
    plan={
        "replacement_meshes":[WALL,PAVING,BLUE_DECK,*[obj.name for obj in changed_tiles]],
        "retired_objects":[],"new_meshes":[x.name for x in parts],
        "west_wall_face_indices":facing,"ramp_continuous_faces":ramp_faces,
        "view_hit_faces":[242,255,257],
        "plant_roots_east_north_up":[list(x.location) for x in planting],
        "street_route_east_north":[STREET,[-129.38,-200.58],[-133.4,-199.90],[-135.80,-200.87],*site["walk_plan"]["ramp"]],
        "street_focus_east_north_up":[-141.61,-191.09,-4.37],
        "park_way":1499726225,"deck_elevation_m":site["deck_elevation_m"],
        "playground":{**play_plan,**park_plan},
    }
    (ASSETS/"west-ramp.json").write_text(json.dumps(plan,indent=2)+"\n")
    print("CQ_WEST_RAMP",len(facing),len(ramp_faces),len(planting))


build()
