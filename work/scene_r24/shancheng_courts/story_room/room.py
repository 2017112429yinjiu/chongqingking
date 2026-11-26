"""Fit the photographed classroom display corner to the existing Jinma window bays."""
from pathlib import Path
from math import pi,sin,cos,tau,radians
from mathutils import Vector
from runpy import run_path
import bpy

here=Path(__file__).resolve().parent
Batch=run_path(str(here/"mesh.py"))["Batch"]
f=run_path(str(here/"furniture.py"))
o=run_path(str(here/"objects.py"))
extra=run_path(str(here/"details.py"))

def finish(name,color,rough=.65,metal=0,alpha=1):
    mat=bpy.data.materials.new("Story hall "+name)
    mat.use_nodes=True
    p=mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    if alpha<1:
        p.inputs["Alpha"].default_value=alpha
        mat.surface_render_method="BLENDED"
    mat.diffuse_color=(*color,alpha)
    return mat

def build(point,slab,structure,mats,scan,chalk,wood,walnut,length,depth,storey):
    m={"wood":mats[wood],"walnut":mats[walnut]}
    lacquer=scan("Old ink-dark school desktop",(.19,.15,.13),"wood_table_worn_diff_2k.jpg")
    m["lacquer"]=mats[lacquer]
    m["lacquer"].node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value=.54
    tint=next(n for n in m["lacquer"].node_tree.nodes if n.bl_idname=="ShaderNodeMix")
    tint.inputs[7].default_value=(.27,.32,.34,1.)
    m.update(black=finish("Bakelite",(.022,.026,.024),.37),
             peg=finish("Endgrain pegs",(.075,.039,.019)),
             brass=finish("Oxidized brass",(.40,.26,.118),.38,.66),
             honey=finish("Ochre radio enamel",(.64,.363,.071),.48),
             steel=finish("Brushed aluminium",(.52,.52,.46),.30,.69),
             red=finish("Crimson enamel",(.45,.025,.021),.46),
             lining=finish("Felt and case liner",(.075,.084,.068),.92),
             enamel=finish("Celadon glaze",(.55,.63,.50),.29),
             paper=finish("Paper cut edges",(.69,.63,.48),.88),
             label=finish("Paper label",(.58,.25,.07),.82),
             cloth=finish("Woven pale rose cloth",(.53,.30,.34),.92),
             green=finish("Desk lamp green enamel",(.08,.30,.20),.35),
             glass=finish("Thin clear cabinet glazing",(.73,.88,.87),.18,.04,.13))
    printed=finish("Original printed ephemera",(1,1,1),.76)
    image=printed.node_tree.nodes.new("ShaderNodeTexImage")
    image.image=bpy.data.images.load(str(here/"printwork.jpg"),check_existing=True)
    image.image.pack()
    printed.node_tree.links.new(image.outputs['Color'],printed.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    m['print']=printed
    join=Batch("Court_Jinma_Story_Trim",point)
    supports=Batch("COL_Court_Jinma_Story_Furniture",point)
    detail=Batch("Court_Jinma_Story_Collection",point)
    glass=Batch("Court_Jinma_Story_Glass",point)
    back=10*length/13
    flank=.32*depth
    # The archive views place the sign and shelves on a solid end wall; another
    # picture shows cupboards between two doorways opposite the exterior windows.
    # The bays, opening widths and offset from the playable stair are fitted here.
    slab(structure,back-.10,.30,0,back+.10,flank+.092,storey-.19,chalk)
    for lo,hi in ((18.33,18.54),(19.99,22.96),(24.10,back-.10)):
        slab(structure,lo,flank-.085,0,hi,flank+.085,storey-.19,chalk)
    for lo,hi in ((18.54,19.99),(22.96,24.10)):
        slab(structure,lo,flank-.085,2.86,hi,flank+.085,storey-.19,chalk)
        for x in (lo+.028,hi-.028):
            join.board(x,flank,0,.056,.194,2.86,m['walnut'])
        for z in (2.21,2.81):join.board((lo+hi)/2,flank,z,hi-lo,.18,.048,m['walnut'])
        join.board((lo+hi)/2,flank,2.25,.031,.06,.56,m['wood'])
        glass.face([(lo+.05,flank,2.26),(hi-.05,flank,2.26),(hi-.05,flank,2.81),(lo+.05,flank,2.81)],m['glass'])
    join.board(back-.111,(.31+flank)/2,0,.026,flank-.31,.102,m['walnut'])
    def place(x,y,angle):
        for g in (supports,detail,glass):g.place(x,y,angle)
    place(back-.298,2.55,-pi/2)
    f["back_shelves"](supports,detail,m)
    # The two glazed cupboards sit between the doorways. Their lower cupboards
    # take the weight, with the shallow shelves and pulls modelled on both leaves.
    place(21.49,flank-.319,0)
    for k in (-1,1):f["tall_case"](supports,glass,detail,k*.647,0,1.26,m,k+2)
    # Two separate reused desks underneath the windows; turntable to the left
    # of the yellow boombox when facing the windows, as in the 2023 press view.
    place(22.13,.723,pi)
    for u,w in ((-.86,1.45),(.74,1.73)):f['desk'](supports,u,0,w,.616,.776,m,True)
    o['record_player'](detail,-.73,-.019,.776,m)
    o['radio'](detail,.47,.027,.776,m)
    extra["earthenware"](detail,-.31,.12,.776,m)
    extra["small_radio"](detail,1.30,.025,.776,m)
    extra["lamp"](detail,.84,.197,.776,m)
    f['sheet'](detail,-.21,-.16,.776,.235,.13,1,m,.055)
    f['sheet'](detail,.91,-.15,.776,.196,.116,2,m,-.04)
    for u,tile in ((-.52,4),(-.19,1),(.12,2)):
        f['plaque'](detail,u,.235,.776,.29,.25,tile,m)
    # The square wood/glass case stands at the far end of the window desks,
    # beside the open record player. The isolated close-up of phones does not
    # establish their position in this view.
    place(23.40,.735,pi)
    detail.board(0,0,.776,.543,.397,.029,m['wood'])
    for u in (-.251,.251):
        for v in (-.179,.179):supports.board(u,v,.803,.023,.023,.388,m['wood'])
    for v in (-.179,.179):
        supports.board(0,v,1.176,.529,.023,.026,m['wood'])
        q=[(-.24,v,.809),(.24,v,.809),(.24,v,1.177),(-.24,v,1.177)]
        glass.face(q if v<0 else q[::-1],m['glass'])
    for u in (-.251,.251):
        supports.board(u,0,1.176,.023,.360,.026,m['wood'])
        q=[(u,-.166,.809),(u,.166,.809),(u,.166,1.176),(u,-.166,1.176)]
        glass.face(q if u>0 else q[::-1],m['glass'])
    glass.face([(-.24,-.166,1.192),(.24,-.166,1.192),(.24,.166,1.192),(-.24,.166,1.192)],m['glass'])
    f['sheet'](detail,-.07,-.018,.805,.191,.112,3,m,.038,.003)
    extra["earthenware"](detail,.12,.055,.805,m)
    f['booklet'](detail,.14,-.181,.776,.099,.069,4,m,.036)
    # The open fare box has its own cloth-covered stand beside the window pier.
    place(8*length/13,.693,pi)
    stand_z=extra["stand"](supports,0,0,m)
    extra["cloth"](detail,0,0,stand_z,.375,.333,m)
    o['fare_box'](detail,0,0,stand_z+.005,m)
    # The desks meet end to end, with low, narrow benches running alongside.
    place(0,0,0)
    for x in (19.85,21.41):
        f['desk'](supports,x,2.44,1.556,.77,.769,m)
        f['bench'](supports,x,3.115,1.31,m)
    o['stamp_tray'](detail,19.73,2.46,.769,m)
    f['sheet'](detail,21.53,2.42,.769,.267,.202,14,m,.088)
    f['sheet'](detail,21.85,2.56,.769,.139,.084,3,m,-.14)
    detail.tube((21.6,2.30,.774),(21.74,2.32,.774),.004,m['black'])
    # Low stool under the left cubby table.
    place(back-.36,3.45,-pi/2)
    f['bench'](supports,0,-.13,.49,m)
    join.place(0,0,0)
    # The volunteer's room-wide view shows short black track spots and a white fan.
    for i,(x,y,tx,ty,tz) in enumerate(((23.58,2.76,24.88,2.54,1.58),(21.96,2.40,22.12,.72,.91))):
        source=Vector(point(x,y,storey-.39));target=Vector(point(tx,ty,tz))
        end=Vector((x,y,storey-.39));start=end-(Vector((tx,ty,tz))-end).normalized()*.15
        join.board(x,y,storey-.095,.63,.035,.037,m['black'])
        join.tube((x,y,storey-.063),start,.012,m['black'])
        join.tube(start,end,.040,m['black'],.055,18)
        join.tube(end,end+(end-start).normalized()*.003,.046,m['paper'],sides=18)
        light=bpy.data.lights.new("Story exhibit spot %d"%(i+1),"SPOT")
        light.energy=6.5
        light.color=(1.,.89,.75)
        light.spot_size=radians(88)
        light.spot_blend=.76
        light.use_custom_distance=True
        light.cutoff_distance=4.2
        obj=bpy.data.objects.new(light.name,light)
        bpy.context.collection.objects.link(obj)
        obj.location=source
        obj.rotation_euler=(target-source).to_track_quat('-Z','Y').to_euler()
    x,y,z=21.15,2.66,storey-.42
    join.tube((x,y,z+.07),(x,y,storey-.065),.013,m['enamel'])
    join.turn(x,y,z,[(0,.067),(.028,.094),(.069,.083),(.084,.042)],m['enamel'])
    for j in range(3):
        a=j*tau/3
        points=[(x+u*cos(a)-v*sin(a),y+u*sin(a)+v*cos(a),z+.019+v*.12) for u,v in
                ((.050,-.024),(.23,-.058),(.58,-.077),(.62,-.039),(.60,.051),(.25,.036),(.050,.017))]
        join.face(points,m['enamel']);join.face([(u,v,h-.004) for u,v,h in points[::-1]],m['enamel'])
    for g in (join,supports,detail,glass):g.save()
