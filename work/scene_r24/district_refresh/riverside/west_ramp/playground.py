"""Build park equipment from the registered field views on the fitted game deck."""
from math import cos, pi, sin, sqrt, tau
from random import Random

import bpy
from mathutils import Vector

from factory import Mesh
from factory_glazing import glaze_material

BLUE_DECK = "Outer500_WestCourt_BlueFinish"
ORIGIN = Vector((-148.0, -183.65))
MOUND = Vector((-170.24, -169.48))
EAST = Vector((.9888, -.1494))
NORTH = Vector((.1494, .9888))


def speckle(name, base, seed):
    image = bpy.data.images.new(name, 256, 256, alpha=False)
    rng = Random(seed)
    pixels = []
    for _ in range(256 * 256):
        value = rng.uniform(.83, 1.10)
        if rng.random() < .12:
            value *= .77
        pixels.extend([min(1., channel * value) for channel in base] + [1.])
    image.colorspace_settings.name = "Non-Color"
    image.pixels.foreach_set(pixels)
    image.pack()
    finish = glaze_material(name, base, .92)
    color = finish.node_tree.nodes.new("ShaderNodeTexImage")
    color.image = image
    shader = finish.node_tree.nodes.get("Principled BSDF")
    finish.node_tree.links.new(color.outputs["Color"], shader.inputs["Base Color"])
    return finish


def beam(mesh, start, end, radius, finish, sections=8):
    a, b = Vector(start), Vector(end)
    axis = (b-a).normalized()
    side = axis.cross(Vector((0, 0, 1)))
    if side.length < .001:
        side = axis.cross(Vector((0, 1, 0)))
    side.normalize()
    up = axis.cross(side)
    loop = [radius * (cos(tau*i/sections)*side + sin(tau*i/sections)*up) for i in range(sections)]
    mesh.solid([a+v for v in loop], [b+v for v in loop], finish)


def slide(mesh, point, x, width, section, steel, rim):
    # The shallow central tray, raised edges and rolled lip are separate surfaces.
    for (a, za), (b, zb) in zip(section, section[1:]):
        for start, end, raise_a, raise_b, finish in (
            (-.5, -.43, .115, .015, rim), (-.43, .43, .015, .015, steel),
            (.43, .5, .015, .115, rim),
        ):
            mesh.face([point(x+start*width, a, za+raise_a), point(x+end*width, a, za+raise_b),
                       point(x+end*width, b, zb+raise_b), point(x+start*width, b, zb+raise_a)], finish)
        for side in (-.5, .5):
            beam(mesh, point(x+side*width, a, za+.115), point(x+side*width, b, zb+.115), .026, rim)
    end, height = section[0]
    beam(mesh, point(x-width*.48, end, height+.015), point(x+width*.48, end, height+.015), .028, rim)


def build(blue, elevation, grade):
    def pt(u, v, z=.0):
        position = ORIGIN + u*EAST + v*NORTH
        return position.x, position.y, elevation+z

    blue_finish = speckle("West play fine blue rubber aggregate", (.18,.43,.58), 142)
    sand = speckle("West play pale aggregate", (.58,.52,.43), 143)
    rose = speckle("West play muted rose aggregate", (.53,.32,.30), 144)
    blue.data.materials.clear()
    blue.data.materials.append(blue_finish)
    uv = blue.data.uv_layers.active or blue.data.uv_layers.new(name="Aggregate UV")
    for poly in blue.data.polygons:
        poly.material_index = 0
        for loop in poly.loop_indices:
            vertex = blue.matrix_world @ blue.data.vertices[blue.data.loops[loop].vertex_index].co
            uv.data[loop].uv = (vertex.x/.38, vertex.y/.38)
    shell_finishes = [glaze_material("West climb blue panel "+str(i), color, .59) for i,color in enumerate(
        [(.048,.22,.38),(.065,.30,.49),(.080,.35,.55),(.065,.265,.44)])]
    white = glaze_material("West playground ivory border",(.82,.82,.73),.78)
    frame = glaze_material("West playground powdered pale steel",(.62,.7,.73),.40)
    net = glaze_material("West playground woven steel rope",(.17,.20,.21),.58)
    chute = glaze_material("West playground brushed stainless tray",(.52,.61,.67),.27,.48)
    edge = glaze_material("West playground rolled tray edges",(.67,.72,.74),.33,.33)
    foundation = glaze_material("West playground inset tarmac footings",(.12,.15,.15),.90)
    colours = [glaze_material("West rotator "+name, rgb, .53) for name,rgb in
               (("blue",(.026,.25,.49)),("green",(.30,.48,.075)),("red",(.54,.065,.065)))]
    handle = glaze_material("West rotator oxide-red handles",(.42,.045,.026),.49)
    ornaments = Mesh("WestPlayground_EdgeStripe")
    a = Vector((-152.8,-175.98))
    b = Vector((-141.82,-177.15))
    aside = Vector((.012,.12))
    stripe = [a,b,b+aside,a+aside]
    ornaments.face([(p.x,p.y,grade(p)+.017) for p in stripe],white)

    arch = Mesh("COL_WestPlayground_PerforatedBlueClimber")
    cx, cy = -.10, .76

    def skin(s, t, thickness=0.):
        width = 1.37+sin(pi*s)*.09+thickness
        rise = 2.00+.26*cos(tau*(s-.16))+thickness
        return pt(cx+width*cos(t), cy+(s-.5)*2.22, .045+rise*sin(t))

    # Open annular cells in the blue shell cast real silhouettes. The separate front grid stays open.
    for strip in range(12):
        t0, t1 = pi*strip/12, pi*(strip+1)/12
        finish = shell_finishes[strip%4]
        for row in range(5):
            s0,s1 = row*.2,(row+1)*.2
            outline = [(s0,t0),(s1,t0),(s1,t1),(s0,t1)]
            cell_s,cell_t = (s0+s1)*.5,(t0+t1)*.5
            hole = [(cell_s+(s-cell_s)*.40,cell_t+(t-cell_t)*.48) for s,t in outline]
            for i in range(4):
                j = (i+1)%4
                arch.face([skin(*outline[i]),skin(*outline[j]),skin(*hole[j]),skin(*hole[i])],finish)
                arch.face([skin(*hole[i]),skin(*hole[j]),skin(*hole[j],.025),skin(*hole[i],.025)],finish)
    for s in (0.,1.):
        for i in range(18):
            beam(arch,skin(s,pi*i/18),skin(s,pi*(i+1)/18),.043,frame)
        for index in range(-5,6):
            x = index*.205
            half_arc = max(0.,1-(x/1.37)**2)**.5
            height = (2.00+.26*cos(tau*(s-.16)))*half_arc
            beam(arch,pt(cx+x,cy+(s-.5)*2.22,.09),pt(cx+x,cy+(s-.5)*2.22,height),.016,net)
        for index in range(1,10):
            z = index*.206
            rise = 2.00+.26*cos(tau*(s-.16))
            if z < rise:
                half = 1.37*(1-(z/rise)**2)**.5
                beam(arch,pt(cx-half,cy+(s-.5)*2.22,z),pt(cx+half,cy+(s-.5)*2.22,z),.016,net)
    slide(arch,pt,-.43,.77,[(-2.58,.19),(-2.28,.19),(-1.84,.27),(-1.56,.47),
          (-1.22,.83),(-.86,1.16),(-.52,1.36),(-.27,1.36)],chute,edge)
    for x in (-.78,-.10):
        beam(arch,pt(x,-1.5,.07),pt(x,-1.5,.51),.034,frame)

    mound = Mesh("COL_WestPlayground_PaleAndRoseMound")
    mx, my = 0., 0.

    def sand_pt(u, v, z=.0):
        position = MOUND + u*EAST + v*NORTH
        return position.x, position.y, grade(position)+z

    def height(x, y):
        r2 = ((x-mx)/2.38)**2+((y-my)/1.78)**2
        return .026+.88*max(0.,1-r2)**1.50

    def ground(x,y):
        return sand_pt(x,y,height(x,y))

    def mound_row(y):
        half_width=2.38*sqrt(max(0.,1.-(y/1.78)**2))
        return [ground(mx+half_width*(i/9.-1.),y) for i in range(19)]

    contour=sorted({-1.78+i*3.56/28 for i in range(29)}|{-1.37,-.72})
    for y0,y1 in zip(contour,contour[1:]):
        finish = rose if -1.37 < (y0+y1)*.5 < -.72 else sand
        a,b=mound_row(y0),mound_row(y1)
        for x in range(18):
            points=list(dict.fromkeys([a[x],a[x+1],b[x+1],b[x]]))
            if len(points)>2:
                mound.face(points,finish)
    chute_mesh = Mesh("WestPlayground_PairEmbeddedChutes")
    slide_y = (-2.13,-1.88,-1.62,-1.31,-.91,-.51,-.06,.15)
    for x in (-.83,.83):
        slide(chute_mesh,sand_pt,x,.67,[(y,height(x,y)+.04) for y in slide_y],chute,edge)

    rotators = Mesh("COL_WestPlayground_ThreeRotatingBowls")
    bowl_points = [(-5.63,1.53),(-5.43,-.31),(-4.51,-2.10)]
    for (u,v), finish in zip(bowl_points,colours):
        delta = grade(Vector(pt(u,v)[:2]))-elevation

        def circle(radius, z):
            return [pt(u+radius*cos(tau*i/24),v+radius*sin(tau*i/24),z+delta) for i in range(24)]

        rotators.face(circle(.40,.027),foundation)
        beam(rotators,pt(u,v,.025+delta),pt(u,v,.50+delta),.08,net,12)
        loops = [circle(radius,z) for radius,z in ((.13,.40),(.29,.46),(.39,.58),(.42,.64),(.38,.66),(.23,.54))]
        for a,b in zip(loops,loops[1:]):
            for i in range(24):
                j = (i+1)%24
                rotators.face([a[i],a[j],b[j],b[i]],finish)
        rotators.face(loops[-1],finish)
        railing = [pt(u+.28*cos(tau*i/24),v+.28*sin(tau*i/24),.82+delta) for i in range(24)]
        for i in range(24):
            beam(rotators,railing[i],railing[(i+1)%24],.018,handle)
        for i in (1,9,17):
            x,y,z = railing[i]
            beam(rotators,(x,y,z-.22),(x,y,z),.017,handle)
    return ([piece.save() for piece in (ornaments,arch,mound,chute_mesh,rotators)], blue_finish,
            {"climber_centre":list(ORIGIN),
             "mound_centre":list(MOUND),
             "rotator_centres": [pt(u,v)[:2] for u,v in bowl_points], "rotator_radius_m":.42,
             "blue_eye_east_north_up":[-147.94,-191.,grade(Vector((-147.94,-191.)))+1.60],
             "blue_target_east_north_up":[-149.45,-182.5,elevation+.80],
             "sand_eye_east_north_up":list(sand_pt(-.4,-6.4,1.60)),
             "sand_target_east_north_up":list(sand_pt(0,0,.42))})
