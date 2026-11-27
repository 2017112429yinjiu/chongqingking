"""Build the small east-side stall increment using the market's existing stock mesh."""
import json
from math import pi
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
MARKET = HERE.parent
GROUPS = MARKET.parents[1]
sys.path[:0] = [str(MARKET), str(GROUPS), str(GROUPS / "guoco")]

from factory import Mesh
from factory_glazing import glaze_material
from interior_art import Fixture, build_stock, textured
from refresh_geometry import ASSETS, read

STOCK = "COL_Huihuigou_MarketFurnishings"
HEADERS = [
    ("旧电器回收", 232.971, 192.84, 2.397, .259),
    ("音响寄售", 233.216, 195.53, 2.387, .198),
]
PRICE_LABELS = [
    ("台扇 35 元", 232.911, 192.87, 1.465, .097),
    ("碟机 45 元", 232.911, 192.18, .823, .097),
    ("音响 60 元", 232.911, 193.57, .823, .097),
]
MOVES = {
    ("television",233.43,193.55,.915):(233.48,193.53,pi/2,.915),
    ("audio_receiver",233.40,192.52,1.535):(233.45,193.55,pi/2,1.535),
    ("dvd_player",233.42,191.86,.915):(233.46,192.22,pi/2,.915),
    ("dvd_player",233.42,191.882,.975):(233.46,192.212,pi/2,.975),
    ("dvd_player",233.42,191.86,1.035):(233.46,191.79,pi/2,.915),
    ("dvd_player",233.42,191.882,1.095):(233.46,191.79,pi/2,.977),
}
ADDITIONS = [
    ("fan",233.45,192.90,.41,.32,.54,"green",pi/2,1.535),
    ("audio_receiver",233.45,192.94,.40,.36,.12,"tobacco",pi/2,.915),
    ("audio_receiver",233.46,191.84,.41,.36,.13,"rim",pi/2,1.535),
    ("audio_receiver",233.46,193.04,.47,.38,.11,"graphite",pi/2,.344),
    ("dvd_player",233.43,193.56,.38,.32,.068,"graphite",pi/2,.344),
    ("dvd_player",233.43,193.56,.34,.30,.065,"rim",pi/2,.415),
    ("audio_receiver",231.12,190.51,.43,.35,.113,"rim",-.12,.181),
    ("dvd_player",231.62,190.53,.39,.33,.067,"graphite",-.12,.181),
    ("dvd_player",231.62,190.53,.35,.29,.063,"rim",-.12,.251),
    ("audio_receiver",232.44,191.94,.43,.34,.134,"tobacco",pi/2,.181),
    ("dvd_player",232.44,191.48,.34,.31,.073,"graphite",pi/2,.50),
    ("audio_receiver",228.45,190.83,.34,.31,.125,"tobacco",.10,.181),
    ("dvd_player",228.88,190.83,.33,.29,.068,"rim",.10,.181),
    ("dvd_player",228.88,190.84,.29,.26,.063,"graphite",.10,.255),
]


def put_text(font, string, e, n, z, size, finish):
    curve = bpy.data.curves.new("Market stall " + string, "FONT")
    curve.font = font
    curve.body = string
    curve.size = size
    curve.align_x = "CENTER"
    curve.extrude = .00035
    curve.materials.append(finish)
    obj = bpy.data.objects.new(curve.name, curve)
    bpy.context.collection.objects.link(obj)
    basis = Matrix(((0.,0.,-1.),(-1.,0.,0.),(0.,1.,0.))).to_4x4()
    basis.translation = Vector((e,n,z))
    obj.matrix_world = basis
    return obj


def wire_field(mesh, x, n0, n1, z0, z1, floor, steel, rust):
    fixture = Fixture(mesh,x,0,floor)
    width = n1-n0
    height = z1-z0
    for tilt in (-1,1):
        for step in range(-30,64):
            start = step*.105
            if tilt > 0:
                low,high = max(0.,-start),min(width,height-start)
            else:
                low,high = max(0.,start-height),min(width,start)
            if high-low > .018:
                fixture.bar((-.005,n0+low,z0+start+tilt*low),
                            (-.005,n0+high,z0+start+tilt*high),
                            .0035,rust if step%6 in (0,1) else steel,4)


def make_finishes(floor, font):
    wall = Mesh("Huihuigou_EastRowGreenGlaze")
    shop = Mesh("Huihuigou_EastRowSteelShopfront")
    cards = Mesh("Huihuigou_EastRowPrintedCards")
    plaster = textured("Market row old oyster plaster",(.82,.86,.77),"plastered_wall_04_diff_2k.jpg",.82)
    glazes = [textured("Market row old green glaze %d" % i,tint,"concrete_wall_006_diff_2k.jpg",roughness)
              for i,(tint,roughness) in enumerate([((.31,.54,.43),.36),((.27,.46,.37),.43),
                                                    ((.35,.57,.46),.39),((.38,.56,.46),.47)])]
    grout = glaze_material("Market row aged green grout",(.155,.197,.159),.87)
    frame = textured("Market row exposed rust on angle iron",(.59,.60,.51),"rusty_painted_metal_diff_2k.jpg",.71)
    painted = glaze_material("Market row worn grey-green paint",(.242,.296,.269),.62)
    wire = glaze_material("Market row black steel wire",(.114,.138,.12),.61,.18)
    rust = glaze_material("Market row brown corrosion",(.26,.155,.085),.78)
    roller = textured("Market row dirty galvanised shutter",(.72,.74,.68),"concrete_wall_006_diff_2k.jpg",.54)
    slat_edge = glaze_material("Market row worn shutter lower fold",(.328,.348,.323),.59,.18)
    red = textured("Market row brick-red painted sign",(.72,.139,.092),"wood_table_worn_diff_2k.jpg",.69)
    piping = glaze_material("Market row red sign painted edge",(.55,.101,.06),.75)
    yellow = glaze_material("Market row hand-painted ochre lettering",(.96,.73,.23),.72)
    straw = glaze_material("Market row paper price stock",(.83,.68,.41),.80)
    ink = glaze_material("Market row dark price ink",(.066,.067,.045),.78)
    wall_fix = Fixture(wall,233.56,0,floor)
    wall_fix.box(-.008,.014,190.94,196.74,.075,1.39,grout)
    wall_fix.box(-.006,.014,190.94,196.74,1.39,3.09,plaster)
    for row in range(5):
        z = .103+row*.251
        for index in range(19):
            n = 190.96+index*.303
            tip = min(n+.298,196.72)
            wall_fix.box(-.018,-.009,n,tip,z,z+.244,glazes[(index*9+row*13)%17%4])
    wall_fix.box(-.034,-.006,190.94,196.74,1.356,1.411,glazes[1])
    wall_fix.box(-.029,-.006,190.96,196.74,.043,.11,glazes[1])

    iron = Fixture(shop,233.24,0,floor)
    for n in (191.22,192.88,194.35,196.77):
        iron.box(-.022,.045,n-.022,n+.022,1.61,2.97,frame)
    iron.box(-.041,.055,191.21,196.77,2.674,2.716,painted)
    iron.box(-.032,.055,191.21,196.77,2.950,2.983,frame)
    for n0,n1 in ((191.26,192.85),(192.91,194.31),(194.41,196.74)):
        wire_field(shop,233.25,n0,n1,2.715,2.948,floor,wire,rust)
    wire_field(shop,233.25,191.34,191.72,1.65,2.286,floor,wire,rust)
    wire_field(shop,233.25,193.96,194.31,1.65,2.286,floor,wire,rust)

    shutter = Fixture(shop,233.25,0,floor)
    for i in range(14):
        z = 1.748+i*.043
        shutter.box(-.023,.012,194.46,196.61,z,z+.035,roller)
        shutter.box(-.026,-.017,194.46,196.61,z,z+.008,slat_edge)
    for n in (194.46,196.61):
        shutter.box(-.039,.025,n-.018,n+.021,1.63,2.686,frame)
    shutter.box(-.047,.025,194.42,196.65,1.686,1.757,slat_edge)
    shutter.box(-.045,.32,194.81,196.52,1.107,1.154,glazes[1])

    sign = Fixture(cards,232.984,0,floor)
    sign.box(-.006,.025,191.51,194.09,2.303,2.656,red)
    for z in (2.31,2.636):
        sign.box(-.009,-.005,191.53,194.07,z,z+.011,yellow)
    for n in (191.522,194.067):
        sign.box(-.009,-.005,n,n+.011,2.31,2.643,piping)
    secondary = Fixture(cards,233.229,0,floor)
    secondary.box(-.01,.013,194.61,196.46,2.325,2.627,red)
    for string,e,n,z,size in PRICE_LABELS:
        price = Fixture(cards,e+.006,n,floor)
        price.box(-.004,.004,-.265,.265,z-.012,z+.128,straw)
    text = [put_text(font,string,e,n,floor+z,size,yellow) for string,e,n,z,size in HEADERS]
    text.extend(put_text(font,string,e,n,floor+z,size,ink) for string,e,n,z,size in PRICE_LABELS)
    return [wall.save(),shop.save(),cards.save(),*text],text


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    font_path = sys.argv[sys.argv.index("--")+1]
    font = bpy.data.fonts.load(font_path)
    font.pack()
    market=read(ASSETS/"collectibles-market.json")
    floor=market["hall_floor_m"]
    stock,inventory,_=build_stock(floor,MOVES,ADDITIONS)
    old_inventory=market["interior_art"]["inventory"]
    moved=sum(before["origin_east_north_up"]!=after["origin_east_north_up"] or
              before.get("heading_rad")!=after.get("heading_rad")
              for before,after in zip(old_inventory,inventory))
    assert moved==len(MOVES) and len(inventory)==len(old_inventory)+len(ADDITIONS)
    finishes,glyphs=make_finishes(floor,font)
    stock=stock.save()
    extras={"replacement_meshes":[STOCK],"retired_objects":[],"new_meshes":[o.name for o in finishes],
            "local_bounds_east_north":[[[230.85,233.59],[190.40,196.77]],[[228.18,229.21],[190.62,191.28]]],
            "field_photo_sha256":"ddc2889f761e5c920ebdd6236fdc83f5d2e4496ef4194940ee161220284eb5b7",
            "stock_moved":moved,"stock_added":len(ADDITIONS),"inventory":inventory,
            "header_text":[x[0] for x in HEADERS],"original_price_labels":[x[0] for x in PRICE_LABELS]}
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"stall-row.blend"),compress=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in glyphs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=glyphs[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/"market-stall-row.glb"),export_format="GLB",
                              export_cameras=False,export_lights=False)
    (ASSETS/"market-stall-row.json").write_text(json.dumps(extras,ensure_ascii=False,indent=2)+"\n")
    print("CQ_MARKET_STALL_ROW",len(stock.data.polygons),len(finishes),len(inventory))


main()
