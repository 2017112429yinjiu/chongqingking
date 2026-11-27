"""Build the Zhongxing Road market frontage and playable high-side hall."""
import json
from math import ceil, cos, sin, tau
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
GROUPS = HERE.parents[1]
sys.path[:0] = [str(GROUPS), str(GROUPS / "guoco")]
from factory import Mesh, material, terrain
from factory_glazing import glaze_material
from refresh_geometry import ASSETS, latest_donors, read, strip_plots

FRONT, LOWER, UPPER = 223.45, 173.15, 214.0
ENTRY_LOW, ENTRY_HIGH = 191.75, 195.75
FLOOR, CAP = 53.30, 60.95
ROUTE = [[216.50, 184.50], [217.85, 189.42], [218.90, 193.65],
         [220.85, 193.65], [223.78, 193.65], [226.65, 193.65],
         [230.65, 193.65], [231.52, 195.86]]


def box(mesh, west, east, south, north, low, high, finish):
    ring = [(west,south), (east,south), (east,north), (west,north)]
    mesh.solid([(e,n,low) for e,n in ring], [(e,n,high) for e,n in ring], finish)


def build():
    surface = terrain()

    def grade(east, north):
        hit, *_ = surface.ray_cast(Vector((east, north, 125)), Vector((0, 0, -1)))
        if hit is None:
            raise ValueError(f"No market ground at {east}, {north}")
        return hit.z

    brick = material("Huihuigou warm course brick", (.88,.63,.52), "brick_wall_08_diff_2k.jpg")
    worn = material("Huihuigou damp base brick", (.67,.55,.50), "brick_wall_08_diff_2k.jpg")
    concrete = material("Huihuigou ivory cap bands", (.87,.86,.79), "concrete_wall_006_diff_2k.jpg")
    walls = material("Huihuigou worn interior plaster", (.78,.78,.70), "plastered_wall_04_diff_2k.jpg")
    flags = material("Huihuigou blue grey street flags", (.58,.62,.61), "stone_floor_diff_2k.jpg")
    inside = material("Huihuigou cement hall and side lane", (.57,.59,.54), "concrete_floor_worn_001_diff_2k.jpg")
    slate = material("Huihuigou recessed side rubble", (.52,.56,.55), "stone_wall_05_diff_2k.jpg")
    steel = glaze_material("Huihuigou charcoal coated steel", (.065,.081,.083), .63)
    glass = glaze_material("Huihuigou blue grey shop glazing", (.054,.103,.125), .38, .22)
    trim = glaze_material("Huihuigou aluminium trim", (.22,.26,.26), .63)
    warm = glaze_material("Huihuigou fluorescent tubes", (.78,.77,.66), .53)
    shader = warm.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Emission Color"].default_value = (.82,.81,.74,1.0)
    shader.inputs["Emission Strength"].default_value = 1.1
    brick_shader = brick.node_tree.nodes.get("Principled BSDF")
    brick_shader.inputs["Emission Color"].default_value = (.34,.23,.17,1)
    brick_shader.inputs["Emission Strength"].default_value = .075

    facade = Mesh("COL_Huihuigou_SharedPodium")
    detail = Mesh("Huihuigou_Recessed_Glazing_Louvers_and_Plinths")
    hall = Mesh("COL_Huihuigou_HighStreetHall")
    steps = Mesh("COL_Huihuigou_StreetSteps")
    displays = Mesh("COL_Huihuigou_MarketFurnishings")
    tower = Mesh("Huihuigou_Registered_Tower_Outlines")
    balconies = Mesh("Huihuigou_Recessed_Balconies")
    bands = [LOWER,176.75,180.45,184.05,188.00,ENTRY_LOW,ENTRY_HIGH,199.8,203.45,207.2,210.8,UPPER]
    for index,(south,north) in enumerate(zip(bands,bands[1:])):
        base = min(grade(FRONT,south),grade(FRONT,north)) - .42
        # The two visible facade tiers share one continuous capped brick face.
        box(facade,FRONT,FRONT+.65,south,north,56.82,CAP,brick)
        box(detail,FRONT-.18,FRONT+.72,south,north,60.64,60.95,concrete)
        box(detail,FRONT-.12,FRONT+.70,south,north,56.60,56.83,concrete)
        box(facade,FRONT-.28,FRONT+.64,south,south+.47,base,56.82,brick)
        box(detail,FRONT-.39,FRONT+.65,south-.025,south+.50,55.93,56.18,concrete)
        box(detail,FRONT-.34,FRONT+.66,south-.05,south+.53,55.87,55.98,brick)
        if south != ENTRY_LOW:
            window_base = min(54.16, base+1.21)
            box(facade,FRONT,FRONT+.64,south+.46,north,base,window_base,worn)
            box(facade,FRONT+.58,FRONT+.72,south+.47,north,window_base,56.60,steel)
            box(detail,FRONT+.33,FRONT+.43,south+.54,north-.15,window_base+.08,56.46,glass)
            for n in (south+.57, (south+north)*.5, north-.18):
                box(detail,FRONT+.23,FRONT+.45,n-.025,n+.027,window_base+.03,56.52,trim)
            box(detail,FRONT+.22,FRONT+.48,south+.49,north-.11,55.18,55.26,steel)
        if index in (0,1,2,7,8,10):
            box(detail,FRONT-.11,FRONT+.02,south+.47,north-.20,57.40,59.02,steel)
            box(detail,FRONT-.143,FRONT-.10,south+.54,north-.28,57.49,58.42,glass)
            for slat in range(8):
                level=58.42+.069*slat
                box(detail,FRONT-.159,FRONT-.08,south+.54,north-.28,level,level+.035,trim)
    box(facade,FRONT-.22,FRONT+.64,UPPER-.45,UPPER,grade(FRONT,UPPER)-.33,56.86,brick)
    # Framed sign and a shallow entry canopy read from the bus-stop side.
    for lo,hi in ((57.53,57.67),(59.43,59.57)):
        box(detail,FRONT-.28,FRONT-.08,185.50,201.75,lo,hi,concrete)
    for south in (185.50,201.61):
        box(detail,FRONT-.28,FRONT-.08,south,south+.14,57.53,59.57,concrete)
    box(detail,FRONT-.169,FRONT-.066,185.66,201.59,57.66,59.45,steel)
    for row in range(22):
        z=57.72+row*.077
        box(detail,FRONT-.199,FRONT-.156,185.69,201.55,z,z+.024,trim)
    box(hall,FRONT-.78,233.84,187.65,200.82,56.76,57.11,concrete)
    box(hall,FRONT-.12,233.82,187.80,200.82,FLOOR-.28,FLOOR,inside)
    box(hall,233.59,233.84,187.65,200.82,FLOOR,56.80,walls)
    box(hall,FRONT+.57,233.62,200.57,200.82,FLOOR,56.76,walls)
    # The inset southern opening faces a side walk. Its game layout ends on this public grade.
    for start,end in ((FRONT+.57,226.32),(228.15,233.61)):
        box(hall,start,end,187.65,187.91,FLOOR,56.79,walls)
    box(hall,226.32,228.15,187.65,187.91,55.82,56.79,concrete)
    for y in (188.99,197.91):
        box(hall,FRONT+.65,233.62,y-.19,y+.19,56.28,56.79,concrete)
        for x in (228.85,232.77):
            box(hall,x-.22,x+.22,y-.22,y+.22,FLOOR,56.31,concrete)
        for x in (225.5,229.9,232.25):
            box(detail,x,x+.98,y-.075,y+.075,56.23,56.33,warm)
    for y in (191.57,195.73):
        box(hall,FRONT-.16,FRONT+.33,y,y+.17,FLOOR,56.65,steel)
    box(detail,FRONT-.16,FRONT+.42,191.57,195.90,56.61,56.73,trim)

    # Nine sorted stations form a continuous stone threshold from the street shelf.
    entry_start, entry_end = 219.35, 222.45
    step_floor = max(grade(entry_start,191.68),grade(entry_start,195.67)) + .025
    step_count = ceil((FLOOR-step_floor)/.155)
    for step in range(step_count):
        west=entry_start+(entry_end-entry_start)*step/step_count
        east=entry_start+(entry_end-entry_start)*(step+1)/step_count
        z=step_floor+(FLOOR-step_floor)*(step+1)/step_count
        box(steps,west,east,191.67,195.66,step_floor-.48,z,flags)
        box(detail,west+.022,west+.049,191.77,195.56,z,z+.005,trim)
    box(steps,entry_end,FRONT+.16,191.67,195.66,step_floor-.48,FLOOR,flags)
    for n in (191.49,195.66):
        box(steps,entry_start+.17,FRONT-.04,n,n+.18,step_floor-.35,FLOOR+.46,brick)
        box(detail,entry_start+.15,FRONT-.01,n-.025,n+.205,FLOOR+.46,FLOOR+.54,concrete)

    # Grounded street strip and the outside path visible beside the shared podium.
    for south,north in zip(range(174,214),range(175,215)):
        e0,e1=221.52,223.12
        if 191 <= south <= 195:
            continue
        paving=[(e0,south),(e1,south),(e1,north),(e0,north)]
        detail.face([(e,n,grade(e,n)+.025) for e,n in paving],flags)
    side_east,side_west = 228.14,226.33
    side_floor = grade(227.23,184.0)+.025
    side_steps=ceil((FLOOR-side_floor)/.15)
    for step in range(side_steps):
        south=184.0+3.75*step/side_steps
        north=184.0+3.75*(step+1)/side_steps
        z=side_floor+(FLOOR-side_floor)*(step+1)/side_steps
        box(steps,side_west,side_east,south,north,side_floor-.42,z,flags)
    for east in (225.58,228.16):
        box(steps,east,east+.20,184.23,187.74,side_floor-.5,FLOOR+.27,slate)
        box(detail,east-.04,east+.24,184.23,187.74,FLOOR+.27,FLOOR+.34,concrete)
    for i in range(7):
        n=184.42+i*.43
        box(detail,228.15,228.38,n,n+.20,FLOOR+.34,FLOOR+.55,concrete)
    box(detail,228.13,228.41,184.38,187.25,FLOOR+.55,FLOOR+.63,concrete)
    for south,north in ((181.0,182.0),(182.0,183.0),(183.0,184.0)):
        ring=[(225.65,south),(229.15,south),(229.15,north),(225.65,north)]
        detail.face([(e,n,grade(e,n)+.021) for e,n in ring],inside)

    shelf = glaze_material("Huihuigou enamel shelves and old appliance shells", (.47,.48,.44), .72)
    old_blue = glaze_material("Huihuigou old enamel blue", (.18,.26,.31), .62)
    timber = material("Huihuigou plywood display stands", (.64,.54,.40), "wood_table_worn_diff_2k.jpg")
    for index,x in enumerate((225.41,226.65,227.91,229.35,230.66,232.0)):
        y=198.82+(.18 if index%2 else 0)
        box(displays,x,x+.93,y,y+.78,FLOOR,FLOOR+.27,timber)
        box(displays,x+.08,x+.84,y+.11,y+.69,FLOOR+.26,FLOOR+.96+.09*(index%3),shelf if index%2 else old_blue)
        box(detail,x+.15,x+.77,y+.085,y+.115,FLOOR+.48,FLOOR+.78,glass if index%3 else steel)
        box(detail,x+.20,x+.66,y+.078,y+.111,FLOOR+.88,FLOOR+.93,trim)
    for x,y in ((225.82,189.12),(230.19,189.22),(232.11,190.60)):
        box(displays,x,x+1.02,y,y+.59,FLOOR,FLOOR+.93,timber)
        box(detail,x-.025,x+1.04,y-.025,y+.61,FLOOR+.88,FLOOR+.99,steel)
        box(detail,x+.04,x+.98,y+.05,y+.53,FLOOR+.99,FLOOR+1.013,glass)
    # Rear stock sits outside the continuous passage to the side stair.
    for i,x in enumerate((229.29,230.15,231.03,231.93,232.80)):
        box(displays,x,x+.72,188.01,188.67,FLOOR,FLOOR+.95,shelf if i%2 else old_blue)
        box(detail,x+.055,x+.665,188.666,188.695,FLOOR+.75,FLOOR+.865,steel)
        middle = x+.355
        ring = [(middle+.247*cos(tau*k/20),188.71,FLOOR+.44+.247*sin(tau*k/20)) for k in range(20)]
        detail.face(ring,trim)
        detail.face([(middle+(x0-middle)*.79,188.716,FLOOR+.44+(z-FLOOR-.44)*.79)
                     for x0,_,z in ring],glass)
    box(detail,229.23,233.54,188.03,188.80,FLOOR+1.40,FLOOR+1.46,steel)
    for x in (229.44,230.50,231.87,232.75):
        box(detail,x,x+.51,188.12,188.67,FLOOR+1.46,FLOOR+1.88,old_blue)
        box(detail,x+.045,x+.465,188.669,188.691,FLOOR+1.53,FLOOR+1.81,glass)

    registered = read(GROUPS/"guoco/field-registration.json")["ways"]
    tower_finish = material("Huihuigou faded pale tower elevations", (.78,.80,.76), "plastered_wall_04_diff_2k.jpg")
    # Registration defines the residential envelopes; the upper storey count and bay rhythm are estimates.
    for way,storeys in ((809889619,13),(809889620,12)):
        ring = [Vector(p) for p in registered[str(way)]["east_north"]]
        area = sum(p.x*q.y-q.x*p.y for p,q in zip(ring,ring[1:]+ring[:1]))
        if area < 0:
            ring.reverse()
        datum=CAP-1.15 if way==809889619 else 54.5
        roof=datum+storeys*2.82
        foundation = min(grade(min(249.8,p.x),p.y) for p in ring) - .35
        tower.solid([(p.x,p.y,foundation) for p in ring],[(p.x,p.y,datum) for p in ring],worn)
        tower.solid([(p.x,p.y,datum) for p in ring],[(p.x,p.y,roof) for p in ring],tower_finish)
        for a,b in zip(ring,ring[1:]+ring[:1]):
            span = (b-a).length
            if span<2.8 or min(a.x,b.x)>253.5:
                continue
            side=(b-a).normalized()
            outward=Vector((side.y,-side.x))
            count=max(1,int(span/3.17))
            for index in range(count):
                left=(a+side*((index+.11)*span/count))
                right=(a+side*((index+.79)*span/count))
                footprint=[right,right+outward*.78,left+outward*.78,left]
                for floor in range(storeys):
                    z=datum+floor*2.82
                    balconies.solid([(p.x,p.y,z+.16) for p in footprint],
                                    [(p.x,p.y,z+.35) for p in footprint],concrete)
                    for base,height,finish in ((.42,.82,concrete),(1.04,2.30,glass)):
                        for depth in ((.72,) if base<1 else (.016,)):
                            p,q=left+outward*depth,right+outward*depth
                            balconies.face([(p.x,p.y,z+base),(q.x,q.y,z+base),(q.x,q.y,z+height),(p.x,p.y,z+height)],finish)

    donor_groups = [
        ("guoco-frontages", GROUPS/"guoco/guoco-frontages.blend"),
        ("public-edges", GROUPS/"matix/public-edges.blend"),
        ("xingchen", GROUPS/"xingchen/xingchen.blend"),
        ("pavilion62", GROUPS.parent/"riverside/pavilion62/pavilion62.blend"),
    ]
    layout=read(ASSETS/"layout.json")
    replacement, retired, counts = strip_plots(
        read(HERE/"ownership.json"), (8,9),layout,latest_donors(donor_groups)
    )
    sites = [mesh.save() for mesh in (facade,detail,hall,steps,displays,tower,balconies)]
    # Text is editable in the production source. The normal scene installs its matching vector label.
    note = bpy.data.objects.new("Huihuigou_Sign_Anchor",None)
    note.location=(FRONT-.23,193.62,58.46)
    note["text"]="中兴路收藏品交易市场"
    bpy.context.collection.objects.link(note)
    keep={*replacement,*sites,note}
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"collectibles-market.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/"collectibles-market.glb"),export_format="GLB",
                              export_cameras=False,export_lights=False)
    plan={
        "replacement_meshes":[obj.name for obj in replacement],"retired_objects":retired,
        "new_meshes":[obj.name for obj in sites],"source_plots":[8,9],"removed_faces":counts,
        "mapped_residential_ways":[809889619,809889620],"street_way":176034707,"bus_stop_node":11049229719,
        "north_south_frontage_m":[LOWER,UPPER], "hall_floor_m":FLOOR,"ridge_cap_m":CAP,
        "entrance_rises":step_count,"entrance_rise_m":(FLOOR-step_floor)/step_count,
        "side_rises":side_steps,"route_east_north":ROUTE,
        "side_route_east_north":[*ROUTE[:6],[227.22,190.56],[227.22,187.98],[227.22,185.84],[227.22,184.15]],
        "side_landing_floor_m":side_floor+(FLOOR-side_floor)/side_steps,
        "street_eye_target_east_north_up":[FRONT,193.62,55.83],
        "return_eye_target_east_north_up":[219.6,192.7,54.10],
        "sign_east_north_up":[FRONT-.238,193.62,58.46],
        "parking_access_outside_east_north":[287.652,167.043],"parking_lot_outside_east_north":[285.811,194.422],
    }
    (ASSETS/"collectibles-market.json").write_text(json.dumps(plan,indent=2)+"\n")
    print("CQ_COLLECTIBLES_MARKET",json.dumps(plan))


build()
