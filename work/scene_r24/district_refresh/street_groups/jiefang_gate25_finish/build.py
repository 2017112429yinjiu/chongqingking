"""Finish the registered exterior entrance and its street-side threshold."""
import json
from pathlib import Path
import runpy
import sys

import bpy

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent/"jiefang_public_24_25_26"
prior = runpy.run_path(str(PARENT/"build.py"))
common = prior["common"]
Edge, Mesh, material, tint = (common[k] for k in ("Edge","Mesh","material","tint"))


def materials():
    mats, textures = {}, {}
    for key, label, color, image in (
        ("step","Gate25 warm grey stair tread",(.78,.80,.79),"concrete_floor_worn_001_diff_2k.jpg"),
        ("paving","Gate25 grey street flags",(.71,.73,.71),"stone_floor_diff_2k.jpg"),
        ("stone","Gate25 wide granite lintel and wings",(.59,.62,.61),"stone_wall_05_diff_2k.jpg"),
        ("joint","Gate25 darker recessed granite joints",(.46,.49,.47),"stone_wall_05_diff_2k.jpg"),
        ("nose","Gate25 pale sawn stair edges",(.88,.89,.85),"concrete_floor_worn_001_diff_2k.jpg"),
    ):
        mats[key] = material(label,color,image)
        textures[label] = "res://assets/chongqing_district_"+image
    for key,label,color,roughness in (
        ("soffit","Gate25 charcoal ceiling",(.048,.058,.059),.85),
        ("glass","Gate25 dark reflected glazing",(.038,.072,.078),.22),
        ("panel","Gate25 blackened door profiles",(.027,.032,.033),.57),
        ("rail","Gate25 black street-edge rail",(.034,.033,.030),.60),
        ("steel","Gate25 satin steel pull handles",(.54,.57,.57),.28),
    ):
        mats[key] = tint(label,color,roughness)
    return mats,textures


def build(out):
    field = json.loads((PARENT/"field.json").read_text())
    spec = json.loads((HERE/"field.json").read_text())
    base = field["stairs_25"]
    ground = common["terrain"]()
    axis = Edge([base["left"]["en"],base["right"]["en"]],ground)
    width = axis.stations[-1]
    terrain_band = spec["street_side_t"]
    front, back = spec["stone_face_t"],spec["glass_t"]
    old_screen = "COL_Jiefang25_DoorPiersAndStepReturns"
    old_steps = "COL_Jiefang25_RegisteredStoneSteps"
    for name in (old_screen,old_steps):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj,do_unlink=True)
    m,textures = materials()
    (stairs,temporary),route = prior["public_stair"](field,ground,{"step":m["step"],"beam":m["stone"]})
    bpy.data.objects.remove(temporary,do_unlink=True)
    frame = Mesh("COL_Jiefang25_StoneWingsAndHead")
    facade = Mesh("Jiefang25_SoffitVerticalsAndGlass")
    threshold = Mesh("COL_Jiefang25_JoinedFlags")
    edging = Mesh("Jiefang25_StoneTreadNoses")
    barrier = Mesh("COL_Jiefang25_StreetEdgeIronRail")

    def coord(s,t,h):
        return (*axis.en(s,t),h)

    def solid(mesh,a,b,c,d,lower,upper,finish):
        ring = [(s,t) for s,t in ((a,c),(b,c),(b,d),(a,d))]
        mesh.solid([coord(s,t,lower) for s,t in ring],[coord(s,t,upper) for s,t in ring],finish)

    def gate_top(s):
        return axis.ground_y(axis.en(s,0.))+.53

    def bottom_step(s):
        return axis.ground_y(axis.en(s,-4.90))+.06

    def sidewalk(s):
        return axis.ground_y(axis.en(s,terrain_band))+.049

    sill = max(gate_top(s) for s in (0.,width/2,width))
    head = sill+2.64
    lintel = head+1.03
    solid(frame,0.,width,front,back+.11,head,lintel,m["stone"])
    solid(facade,.40,width-.40,front+.015,back-.035,head-.055,head+.010,m["soffit"])
    solid(facade,-.04,width+.04,front-.035,front+.04,head+.02,head+.11,m["joint"])
    for side,left,right in ((0,0.,.48),(1,width-.48,width)):
        solid(frame,left,right,front-.035,back+.2,min(gate_top(left),gate_top(right))-.55,head+.02,m["stone"])
        for row in range(4):
            z = sill+.16+row*.62
            solid(facade,left+.012,right-.012,front-.043,front-.034,z,z+.012,m["joint"])
        # Only a side return visible from the public apron is reconstructed.
        a,b = (-.52,.0) if side==0 else (width,width+.52)
        solid(frame,a,b,-.46,back+.16,min(gate_top(left),gate_top(right))-.52,head+.05,m["stone"])
        solid(facade,a,b,-.51,-.45,head-.05,head+.10,m["joint"])
    # A dark closed screen sits behind the photographed line of panels.
    solid(frame,.47,width-.47,back+.028,back+.12,min(gate_top(0.),gate_top(width))-.08,head,m["soffit"])
    glazed = (width-.99)/6.
    for i in range(6):
        a,b = .495+i*glazed,.495+(i+1)*glazed
        low = min(gate_top(a),gate_top(b))+.016
        solid(facade,a+.028,b-.025,back,back+.021,low,head-.46,m["glass"])
        solid(facade,a-.018,a+.025,back-.043,back+.026,low,head-.40,m["panel"])
        solid(facade,a,b,back-.04,back+.023,low,low+.087,m["panel"])
        for offset in (.087,glazed-.095):
            s = a+offset
            solid(facade,s-.016,s+.016,back-.095,back-.071,low+.79,low+1.23,m["steel"])
            for z in (low+.82,low+1.20):
                solid(facade,s-.017,s+.017,back-.076,back-.015,z,z+.035,m["steel"])
        for j in range(9):
            x = a+glazed*(j+.4)/9
            solid(facade,x-.013,x+.013,back-.096,back-.049,head-.456,head-.008,m["panel"])
    solid(facade,width-.524,width-.476,back-.041,back+.026,gate_top(width-.49),head-.39,m["panel"])
    solid(facade,.475,width-.475,back-.069,back-.027,head-.467,head-.421,m["panel"])

    for i in range(18):
        a,b = width*i/18.,width*(i+1)/18.
        ring = [coord(a,terrain_band,sidewalk(a)),coord(b,terrain_band,sidewalk(b)),
                coord(b,-5.225,bottom_step(b)),coord(a,-5.225,bottom_step(a))]
        threshold.solid([(x,y,z-.19) for x,y,z in ring],ring,m["paving"])
        for k in range(11):
            v = -4.64+k*4.64/11
            y0 = bottom_step(a)+(gate_top(a)-bottom_step(a))*(k+1)/11.+.005
            y1 = bottom_step(b)+(gate_top(b)-bottom_step(b))*(k+1)/11.+.005
            edging.face([coord(a,v-.004,y0),coord(b,v-.004,y1),
                         coord(b,v+.044,y1),coord(a,v+.044,y0)],m["nose"])
    rail_t = spec["curb_rail_t"]
    for i in range(6):
        a,b = width*i/5,width*min(i+1,5)/5
        p = axis.ground_y(axis.en(a,rail_t))+.04
        solid(barrier,a-.06,a+.06,rail_t-.064,rail_t+.064,p-.05,p+.81,m["rail"])
        solid(barrier,a-.089,a+.089,rail_t-.084,rail_t+.084,p+.76,p+.85,m["rail"])
        if i<5:
            q = axis.ground_y(axis.en(b,rail_t))+.04
            for h in (.31,.62):
                ring = [coord(a,rail_t-.023,p+h),coord(b,rail_t-.023,q+h),
                        coord(b,rail_t+.023,q+h),coord(a,rail_t+.023,p+h)]
                barrier.solid(ring,[(x,y,z+.045) for x,y,z in ring],m["rail"])
    center=width/2.
    route.insert(0,coord(center,terrain_band+.12,sidewalk(center)
                        +(bottom_step(center)-sidewalk(center))*.12/(-5.225-terrain_band)))
    display = [x.save() for x in (frame,facade,threshold,edging,barrier)]
    for obj in list(bpy.data.objects):
        if obj not in display+[stairs]:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    name = "jiefang-gate25-finish"
    bpy.ops.wm.save_as_mainfile(filepath=str(out/f"{name}.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(out/f"{name}.glb"),export_format="GLB",export_image_format="NONE",
                              export_cameras=False,export_lights=False)
    plan = dict(replacement_meshes=[stairs.name],new_meshes=[x.name for x in display],retired_objects=[old_screen],
                surface_textures=textures,walks={"25":route},
                eye_controls={"front_t":front,"glass_t":back,"stone_head_height_m":lintel-head,"stair_risers":11,
                              "center_enu":coord(center,0.,gate_top(center))})
    (out/f"{name}.json").write_text(json.dumps(plan,indent=2)+'\n')


if __name__=="__main__":
    build(Path(sys.argv[-1]).resolve())
