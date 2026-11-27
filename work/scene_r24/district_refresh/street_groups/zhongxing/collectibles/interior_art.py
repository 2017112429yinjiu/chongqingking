"""Author the playable market's fixtures, worn flooring and masonry details."""
from math import cos, pi, sin, tau
from random import Random

import bpy
from mathutils import Vector

from factory import Mesh, material
from factory_glazing import glaze_material


class Fixture:
    def __init__(self, host, e, n, floor, heading=0.):
        self.host=host
        self.e=e
        self.n=n
        self.floor=floor
        self.c=cos(heading)
        self.s=sin(heading)

    def p(self,x,y,z):
        return self.e+x*self.c-y*self.s,self.n+x*self.s+y*self.c,self.floor+z

    def face(self,pts,finish):
        self.host.face([self.p(*p) for p in pts],finish)

    def box(self,x0,x1,y0,y1,z0,z1,m):
        plan=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        self.host.solid([self.p(x,y,z0) for x,y in plan],[self.p(x,y,z1) for x,y in plan],m)

    def round(self,x,y,z,r,theta):
        return x+r*cos(theta),y,z+r*sin(theta)

    def hoop(self,x,z,profile,finish,segments=32):
        loops=[[self.round(x,y,z,r,-tau*i/segments) for i in range(segments)]
               for y,r in profile]
        for a,b in zip(loops,loops[1:]):
            for i in range(segments):
                j=(i+1)%segments
                self.face([a[i],a[j],b[j],b[i]],finish)

    def disc(self,x,y,z,r,finish,segments=32):
        self.face([self.round(x,y,z,r,-tau*i/segments) for i in range(segments)],finish)

    def bar(self,start,end,r,finish,sides=8):
        a,b=Vector(self.p(*start)),Vector(self.p(*end))
        axis=(b-a).normalized()
        side=axis.cross(Vector((0,0,1)))
        if side.length<.01:
            side=axis.cross(Vector((0,1,0)))
        side.normalize()
        up=axis.cross(side)
        ring=[r*(side*cos(i*tau/sides)+up*sin(i*tau/sides)) for i in range(sides)]
        self.host.solid([a+v for v in ring],[b+v for v in ring],finish)


def textured(name,tint,image,roughness,normal=None):
    finish=material(name,tint,image)
    tree=finish.node_tree
    shader=tree.nodes.get("Principled BSDF")
    shader.inputs["Roughness"].default_value=roughness
    if normal:
        from refresh_geometry import ASSETS
        node=tree.nodes.new("ShaderNodeTexImage")
        node.image=bpy.data.images.load(str(ASSETS.parent/("chongqing_district_"+normal)),check_existing=True)
        node.image.colorspace_settings.name="Non-Color"
        node.image.pack()
        normalmap=tree.nodes.new("ShaderNodeNormalMap")
        normalmap.inputs["Strength"].default_value=.54
        tree.links.new(node.outputs["Color"],normalmap.inputs["Color"])
        tree.links.new(normalmap.outputs["Normal"],shader.inputs["Normal"])
    return finish


def terrazzo_materials():
    from refresh_geometry import ASSETS
    base=bpy.data.images.load(str(ASSETS.parent/"chongqing_district_concrete_floor_worn_001_diff_2k.jpg"),
                              check_existing=True)
    from array import array
    source=array('f',[0.])*len(base.pixels)
    base.pixels.foreach_get(source)
    width,height=base.size[:]
    size=256
    image=bpy.data.images.new("Market terrazzo authored from worn concrete",size,size,alpha=False)
    rng=Random(5412)
    pixels=[]
    for v in range(size):
        for u in range(size):
            i=(((v*height//size+137)%height)*width+((u*width//size+349)%width))*4
            luma=sum(source[i:i+3])/3
            chip=rng.choices((-.11,-.045,.01,.08,.15),weights=(16,18,33,25,8))[0]
            shade=.26+luma*.16+chip+.007*sin(tau*u/size)+.009*sin(tau*v/size)
            pixels.extend((shade*.87,shade*.98,shade*.88,1.))
    image.colorspace_settings.name="Non-Color"
    image.pixels.foreach_set(pixels)
    image.pack()
    finishes=[]
    for i,tint in enumerate(((.93,.98,.96),(.82,.91,.86),(.96,.91,.87),(1.,1.,.95))):
        m=glaze_material(f"Market terrazzo panel finish {i}",tint,.59)
        tree=m.node_tree
        shader=tree.nodes.get("Principled BSDF")
        tex=tree.nodes.new("ShaderNodeTexImage")
        tex.image=image
        mix=tree.nodes.new("ShaderNodeMix")
        mix.data_type="RGBA"
        mix.blend_type="MULTIPLY"
        mix.inputs[0].default_value=1.
        mix.inputs[7].default_value=(*tint,1.)
        tree.links.new(tex.outputs["Color"],mix.inputs[6])
        tree.links.new(mix.outputs[2],shader.inputs["Base Color"])
        finishes.append(m)
    return finishes


def hall_floor(floor):
    tile=.95
    surface=Mesh("Huihuigou_TerrazzoPaving")
    finishes=terrazzo_materials()
    for iy in range(14):
        south=187.82+iy*tile
        north=min(200.61,south+tile)
        for ix in range(11):
            west=223.36+ix*tile
            east=min(233.61,west+tile)
            if north-south<.035 or east-west<.035:
                continue
            sid=(ix*19+iy*37+ix*iy)%17
            finish=finishes[1 if sid in (0,6) else 2 if sid in (5,11) else 3 if sid==3 else 0]
            o=.005
            surface.face([(west+o,south+o,floor+.008),(east-o,south+o,floor+.008),
                          (east-o,north-o,floor+.008),(west+o,north-o,floor+.008)],finish)
    obj=surface.save()
    uv=obj.data.uv_layers.active
    for loop in obj.data.loops:
        point=obj.data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=((point.x-223.36)/tile,(point.y-187.82)/tile)
    return obj


def washer(f,w,d,h,body,m,z=0.):
    f.box(-w/2,w/2,0,d,z,z+h-.055,body)
    f.box(-w*.51,w*.51,.018,d+.014,z+h-.065,z+h,m["cream"])
    f.box(-w*.452,w*.452,d+.002,d+.017,z+h-.192,z+h-.060,m["porcelain"])
    f.box(-w*.405,-w*.055,d+.019,d+.026,z+h-.136,z+h-.098,m["graphite"])
    for ix in range(3):
        f.disc(-w*.28+ix*.048,d+.03,z+h-.115,.006,m["lamps"],10)
    f.hoop(w*.30,z+h-.127,[(d+.011,.046),(d+.047,.041),(d+.061,.031)],m["rim"],20)
    f.disc(w*.30,d+.062,z+h-.127,.030,m["cream"],20)
    eye=z+.40*h
    radius=min(w*.36,h*.305)
    f.hoop(0.,eye,[(d+.005,radius*1.10),(d+.046,radius*1.09),(d+.066,radius*.91),
                  (d+.070,radius*.74)],m["rim"])
    f.disc(0.,d+.024,eye,radius*.86,m["black"])
    glass=m["washer_glass"]
    f.hoop(0.,eye,[(d+.047,radius*.74),(d+.013,radius*.514),(d+.009,radius*.245)],glass)
    f.disc(0.,d+.01,eye,radius*.245,glass)
    f.box(w*.21,w*.30,d+.047,d+.08,eye-.041,eye+.036,m["cream"])


def condenser(f,w,d,h,body,m,z=0.):
    f.box(-w*.50,w*.50,0,d,z,z+h,body)
    f.box(-w*.45,w*.45,d,d+.003,z+.048,z+h-.054,m["black"])
    cx=-w*.12
    cz=z+h*.48
    r=min(w*.33,h*.40)
    f.hoop(cx,cz,[(d+.005,r*1.09),(d+.023,r*1.06),(d+.036,r)],m["rim"])
    f.disc(cx,d+.016,cz,r*.93,m["graphite"])
    for i in range(5):
        angle=i*tau/5
        f.face([f.round(cx,d+.021,cz,.032,angle),f.round(cx,d+.021,cz,r*.77,angle+.18),
                f.round(cx,d+.021,cz,r*.74,angle+.58)],m["rust"])
    for v in range(-7,8):
        dx=r*v/8
        dy=(r*r-dx*dx)**.5
        f.bar((cx+dx,d+.053,cz-dy),(cx+dx,d+.053,cz+dy),.006,m["cream"],6)
    for dz in (-r*.63,0.,r*.63):
        dx=(r*r-dz*dz)**.5
        f.bar((cx-dx,d+.057,cz+dz),(cx+dx,d+.057,cz+dz),.006,m["cream"],6)
    for i in range(8):
        z0=z+.071+i*(h-.14)/9
        f.box(w*.26,w*.41,d+.015,d+.042,z0,z0+.010,m["rim"])
    for x in (-w*.42,w*.28):
        f.box(x,x+.106,.02,d-.018,z-.018,z+.024,m["black"])


def crt(f,w,d,h,body,m,z=0.):
    back=[(-w*.41,z+h*.07),(w*.41,z+h*.07),(w*.39,z+h*.88),(-w*.39,z+h*.88)]
    front=[(-w*.48,z), (w*.48,z), (w*.50,z+h),(-w*.50,z+h)]
    f.host.solid([f.p(x,0,a) for x,a in back],[f.p(x,d,a) for x,a in front],body)
    def frame(wide,high,depth,finish):
        x=w*wide*.5
        lo,hi=z+h*(.5-high*.5),z+h*(.5+high*.5)
        k=.035
        points=[(-x+k,lo),(x-k,lo),(x,lo+k),(x,hi-k),(x-k,hi),(-x+k,hi),(-x,hi-k),(-x,lo+k)]
        f.face([(u,depth,a) for u,a in points],finish)
    frame(.87,.82,d+.008,m["rim"])
    frame(.79,.72,d+.015,m["black"])
    frame(.72,.61,d+.020,m["crt_glass"])
    frame(.60,.49,d+.023,m["crt_reflect"])
    for i in range(4):
        f.box(w*.12+i*.024,w*.12+i*.024+.010,d+.01,d+.029,z+.025,z+.044,m["cream"])


def receiver(f,w,d,h,body,m,z=0.):
    f.box(-w/2,w/2,0,d,z,z+h,body)
    f.box(-w*.48,w*.48,d,d+.013,z+.004,z+h-.004,m["graphite"])
    f.box(-w*.43,-w*.10,d+.016,d+.021,z+h*.26,z+h*.77,m["radio_screen"])
    f.hoop(w*.32,z+h*.52,[(d+.01,h*.28),(d+.045,h*.24)],m["rim"],16)
    f.disc(w*.32,d+.047,z+h*.52,h*.23,m["porcelain"],16)
    for x in (-w*.03,w*.08,w*.16):
        f.box(x,x+.016,d+.015,d+.028,z+.018,z+.036,m["cream"])


def disc_player(f,w,d,h,body,m,z=0.):
    f.box(-w/2,w/2,0,d,z,z+h,body)
    f.box(-w*.47,w*.47,d,d+.013,z+.006,z+h-.007,m["graphite"])
    f.box(-w*.365,w*.20,d+.013,d+.019,z+h*.48,z+h*.62,m["black"])
    f.box(-w*.34,w*.18,d+.014,d+.023,z+h*.66,z+h*.79,m["rust"])
    for i in range(4):
        f.disc(w*.156+i*.042,d+.024,z+h*.27,.010,m["rim"],10)


def fan(f,w,d,h,body,m,z=0.):
    f.box(-w*.32,w*.32,d*.05,d*.84,z,z+.046,m["graphite"])
    shaft=d*.65
    centre=z+h*.71
    f.bar((0,shaft,z+.04),(0,shaft,centre),.021,m["rim"],12)
    r=w*.49
    f.hoop(0,centre,[(shaft-.063,r*.97),(shaft-.004,r*1.02),(shaft+.057,r)],m["rim"])
    f.hoop(0,centre,[(shaft+.064,r*.92),(shaft+.074,r*.915)],m["graphite"])
    for i in range(5):
        a=i*tau/5
        f.face([f.round(0.,shaft+.055,centre,.023,a),
                f.round(0.,shaft+.055,centre,r*.81,a+.15),
                f.round(0.,shaft+.055,centre,r*.74,a+.72),
                f.round(0.,shaft+.055,centre,r*.30,a+.93)],body)
    for i in range(24):
        a=i*tau/24
        f.bar(f.round(0.,shaft+.092,centre,r*.13,a),f.round(0.,shaft+.073,centre,r*.96,a),
              .0037,m["rim"],5)
    f.disc(0,shaft+.105,centre,r*.135,m["cream"],16)


def rack(f,w,d,h,m,bays):
    for x in (-w/2,w/2-.044):
        for y in (.018,d-.045):
            f.box(x,x+.042,y,y+.040,0.,h,m["frame"])
    for z in bays:
        f.box(-w*.50,w*.50,0,d,z,z+.052,m["timber"])
        f.box(-w*.50,w*.50,d-.022,d+.008,z-.062,z+.052,m["frame"])
    f.bar((-w*.46,.027,.10),(w*.46,.027,h-.13),.012,m["frame"],6)


def case(f,w,d,h,m,lid):
    for x in (-w/2,w/2-.04):
        f.box(x,x+.039,.02,d,.012,h,m["frame"])
    for z in (.16,.49,h-.034):
        finish=m["timber"] if z<.5 else lid
        f.box(-w*.47,w*.47,.016,d,z,z+.020,finish)
        f.box(-w/2,w/2,d-.04,d+.007,z-.021,z+.028,m["frame"])
    f.box(-w*.48,w*.48,d-.018,d-.011,.20,h-.043,m["case_glass"])


def build(floor):
    stock=Mesh("COL_Huihuigou_MarketFurnishings")
    ducts=Mesh("Huihuigou_SuspendedDuctsAndConduit")
    partitions=Mesh("Huihuigou_WainscotAndShutters")
    stock_collections={
        "timber":textured("Market scuffed varnished wood",(.78,.59,.38),"wood_table_worn_diff_2k.jpg",.74),
        "rust":textured("Market oxidised painted steel",(.62,.55,.47),"rusty_painted_metal_diff_2k.jpg",.69,
                        "rusty_painted_metal_nor_gl_2k.jpg"),
        "frame":glaze_material("Market aged charcoal rack angles",(.102,.109,.108),.60,.23),
        "graphite":glaze_material("Market graphite speaker and case grilles",(.055,.061,.06),.75),
        "black":glaze_material("Market cable and shadow recess",(.021,.027,.025),.65),
        "rim":glaze_material("Market brushed and worn aluminium",(.52,.56,.53),.32,.31),
        "cream":glaze_material("Market tea-stained ivory enamel",(.79,.76,.64),.45),
        "porcelain":glaze_material("Market warm white acrylic",(.64,.66,.64),.56),
        "washer_glass":glaze_material("Market curved washer porthole glass",(.050,.096,.106),.265,.30),
        "crt_glass":glaze_material("Market leaded CRT glass",(.081,.112,.107),.27,.29),
        "crt_reflect":glaze_material("Market CRT curved highlight",(.127,.154,.146),.30,.23),
        "radio_screen":glaze_material("Market amber smoked radio indicator",(.21,.17,.086),.34,.18),
        "lamps":glaze_material("Market switch indicators",(.50,.284,.09),.52),
        "green":glaze_material("Market sage enamel fan blades",(.22,.37,.27),.55),
        "tobacco":glaze_material("Market smoked brown TV shell",(.24,.19,.14),.64),
    }
    m=stock_collections
    pane=glaze_material("Market counter clear glass",(.59,.74,.71),.22)
    pane.surface_render_method="BLENDED"
    pane.node_tree.nodes.get("Principled BSDF").inputs["Alpha"].default_value=.31
    m["case_glass"]=pane
    inventory=[]
    shapes={"washer":washer,"air_conditioner":condenser,"television":crt,
            "audio_receiver":receiver,"fan":fan,"dvd_player":disc_player}

    def device(kind,e,n,width,depth,height,colour,heading=0.,shelf=0.):
        f=Fixture(stock,e,n,floor,heading)
        shapes[kind](f,width,depth,height,m[colour],m,shelf)
        inventory.append({"item":kind,"origin_east_north_up":[e,n,floor+shelf],
                          "size_m":[width,depth,height],"heading_rad":heading})

    for x,n,w,d,h,shelves in (
        (231.52,188.17,3.84,.60,2.26,(.93,1.56,2.10)),
        (232.77,199.98,1.43,.52,2.25,(.11,.69,1.39,2.00)),
        (227.23,199.96,2.89,.49,2.18,(.45,1.13,1.72)),
    ):
        rack(Fixture(stock,x,n,floor,pi if n>195 else 0),w,d,h,m,shelves)
        inventory.append({"item":"wall_rack","origin_east_north_up":[x,n,floor],
                          "size_m":[w,d,h], "shelf_heights_m":shelves})
    device("washer",229.98,188.24,.63,.55,.85,"porcelain")
    device("washer",230.80,188.20,.58,.57,.88,"cream")
    device("air_conditioner",231.58,188.19,.77,.48,.59,"porcelain")
    device("air_conditioner",232.57,188.23,.87,.50,.66,"cream")
    device("television",230.22,188.24,.60,.48,.43,"graphite",shelf=.985)
    device("television",232.34,188.23,.69,.455,.52,"tobacco",shelf=.985)
    device("audio_receiver",231.25,188.26,.45,.37,.132,"rim",shelf=.985)
    device("audio_receiver",231.25,188.25,.43,.33,.143,"graphite",shelf=1.12)
    device("fan",229.97,188.24,.44,.34,.57,"green",shelf=1.615)
    device("fan",233.00,188.25,.53,.35,.64,"cream",shelf=1.615)
    device("audio_receiver",231.00,188.22,.48,.43,.17,"porcelain",shelf=1.615)
    device("air_conditioner",225.29,199.37,.79,.46,.59,"cream",heading=pi)
    device("washer",228.95,199.40,.67,.59,.94,"porcelain",heading=pi)
    device("television",226.63,199.91,.59,.42,.46,"tobacco",pi,1.185)
    device("audio_receiver",227.57,199.89,.48,.35,.139,"porcelain",pi,1.18)
    device("fan",228.24,199.88,.46,.36,.59,"green",pi,1.185)
    device("television",232.64,199.90,.56,.42,.43,"graphite",pi,.745)
    device("air_conditioner",232.66,199.92,.78,.45,.52,"porcelain",pi,.16)

    rack(Fixture(stock,233.49,192.77,floor,pi/2),2.63,.56,2.09,m,(.29,.86,1.48))
    inventory.append({"item":"wall_rack","origin_east_north_up":[233.49,192.77,floor],
                      "size_m":[2.63,.56,2.09],"shelf_heights_m":[.29,.86,1.48],"heading_rad":pi/2})
    device("air_conditioner",233.45,192.13,.82,.47,.52,"cream",pi/2,.342)
    device("television",233.43,193.55,.64,.48,.50,"tobacco",pi/2,.915)
    device("audio_receiver",233.40,192.52,.43,.39,.145,"rim",pi/2,1.535)
    for i in range(4):
        device("dvd_player",233.42,191.86+(i%2)*.022,.44-i*.022,.37,.058,
               "rim" if i%2 else "graphite",pi/2,.915+i*.060)

    cases = [
        (228.70,190.66,1.04,.60,.94,"case_glass",.10),
        (231.38,190.40,1.26,.62,.91,"case_glass",-.12),
        (232.49,191.84,1.20,.50,1.00,"timber",pi/2),
    ]
    for x,y,w,d,h,finish,angle in cases:
        case(Fixture(stock,x,y,floor,angle),w,d,h,m,m[finish])
        inventory.append({"item":"case_counter","origin_east_north_up":[x,y,floor],
                          "size_m":[w,d,h], "heading_rad":angle})
    device("audio_receiver",228.65,190.76,.39,.29,.11,"rim",.10,.94)
    device("dvd_player",228.47,190.77,.38,.32,.062,"graphite",.10,.50)
    device("dvd_player",228.88,190.79,.32,.30,.055,"rim",.10,.50)
    device("fan",231.40,190.48,.45,.36,.58,"green",-.12,.91)
    device("audio_receiver",231.47,190.52,.48,.37,.12,"tobacco",-.12,.50)
    device("television",232.40,191.89,.55,.43,.42,"graphite",pi/2,1.00)

    wall_tile=textured("Market wall exposed plaster and grout",(.71,.76,.70),"plastered_wall_04_diff_2k.jpg",
                       .88,"plastered_wall_04_nor_gl_2k.jpg")
    damp=textured("Market green-grey worn lower wall",(.51,.55,.46),"concrete_wall_006_diff_2k.jpg",
                  .81,"concrete_wall_006_nor_gl_2k.jpg")
    enamel=glaze_material("Market scrubbed olive skirting cap",(.20,.29,.24),.57,.08)
    for south,start,end in ((True,224.18,226.26),(True,228.20,233.56),(False,224.18,233.56)):
        y=187.931 if south else 200.544
        for i in range(max(1,round((end-start)/.62))):
            n=max(1,round((end-start)/.62))
            a,b=start+(end-start)*i/n,start+(end-start)*(i+1)/n
            Partition=Fixture(partitions,(a+b)*.5,y,floor,0. if south else pi)
            Partition.box(-(b-a)*.5+.004,(b-a)*.5-.004,0.,.024,.068,1.34,damp)
        span=end-start
        rail=Fixture(partitions,(start+end)*.5,y,floor,0. if south else pi)
        rail.box(-span*.5,span*.5,0.,.033,1.34,1.377,enamel)
        rail.box(-span*.5,span*.5,0.,.028,.022,.068,enamel)
        rail.face([(-span*.5,.018,1.38),(span*.5,.018,1.38),(span*.5,.018,2.68),
                   (-span*.5,.018,2.68)],wall_tile)
    shutter=Fixture(partitions,233.552,197.90,floor,pi/2)
    shutter.box(-1.09,1.09,0.,.048,.16,2.58,m["frame"])
    for i in range(35):
        h=.215+i*.0667
        shutter.box(-1.04,1.04,.042,.069,h,h+.043,m["rust"])
    for x in (-1.07,1.02):
        shutter.box(x,x+.051,0.,.087,.12,2.65,m["rim"])

    pipe=Fixture(ducts,224.18,191.05,floor)
    pipe_finish=textured("Market old green-grey service conduit",(.60,.67,.60),"rusty_painted_metal_diff_2k.jpg",.80)
    pipe.box(.23,9.05,-.18,.20,3.04,3.34,pipe_finish)
    pipe.box(8.71,9.08,-.17,3.14,3.04,3.34,pipe_finish)
    for e in (.35,2.12,3.88,5.63,7.37,8.97):
        pipe.box(e,e+.035,-.202,.223,3.015,3.36,m["frame"])
        for y in (-.20,.215):
            pipe.bar((e,y,3.03),(e,y,3.44),.011,m["rim"])
    for y,z,start,end,r in ((.56,3.228,.20,8.98,.04),(.66,3.288,.29,9.11,.025),
                            (.78,3.212,.49,8.88,.017),(6.12,3.20,.37,9.04,.032)):
        pipe.bar((start,y,z),(end,y,z),r,pipe_finish,12)
        pipe.bar((end,y,z),(end,y,z-.29),r,pipe_finish,12)
    light=glaze_material("Market frosted strip light",(.80,.87,.85),.51)
    shader=light.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Emission Color"].default_value=(.75,.83,.79,1.)
    shader.inputs["Emission Strength"].default_value=1.45
    for x,y in ((.62,2.07),(3.71,2.03),(6.42,2.06),(2.26,6.12),(5.53,6.10)):
        pipe.box(x,x+1.12,y,y+.15,3.22,3.31,m["frame"])
        pipe.box(x+.035,x+1.085,y+.039,y+.103,3.203,3.23,light)
        for e in (x+.15,x+.97):
            pipe.bar((e,y+.07,3.31),(e,y+.07,3.45),.010,m["rim"],6)

    return [hall_floor(floor),stock.save(),partitions.save(),ducts.save()],inventory


def entrance_finish(grade, start, end, step_count, step_floor, floor):
    surface=Mesh("Huihuigou_EntryShoulderAndNosing")
    kerb=textured("Market entry grey cut stone coping",(.82,.81,.75),"stone_floor_diff_2k.jpg",.72,
                  "stone_floor_nor_gl_2k.jpg")
    setts=textured("Market shoulder narrow transverse setts",(.65,.65,.59),"stone_floor_diff_2k.jpg",.86)
    noses=textured("Market grey stair nose water wear",(.74,.78,.74),"concrete_wall_006_diff_2k.jpg",.74,
                   "concrete_wall_006_nor_gl_2k.jpg")
    gutter=glaze_material("Market narrow dark drainage joint",(.10,.11,.10),.83)
    drain=glaze_material("Market worn drain and door track",(.21,.24,.23),.65,.28)

    for i in range(step_count):
        rise=(floor-step_floor)/step_count
        edge=start+(end-start)*i/step_count
        up=step_floor+rise*(i+1)
        for j in range(6):
            left=191.682+j*.659
            right=left+.650
            surface.face([(edge,left,up-rise+.016),(edge,right,up-rise+.016),
                          (edge,right,up-.004),(edge,left,up-.004)],noses)
            surface.face([(edge,left,up+.008),(edge+.091,left,up+.008),
                          (edge+.091,right,up+.008),(edge,right,up+.008)],kerb)
    for j in range(6):
        left=191.683+j*.657
        right=left+.648
        surface.face([(222.46,left,floor+.009),(223.53,left,floor+.009),
                      (223.53,right,floor+.009),(222.46,right,floor+.009)],kerb)
    for i in range(5):
        e0=217.87+i*.288
        e1=e0+.275
        for j in range(9):
            n0=191.68+j*.443
            n1=n0+.437
            surface.face([(e,n,grade(e,n)+.015) for e,n in ((e0,n0),(e1,n0),(e1,n1),(e0,n1))],setts)
    for i in range(7):
        e0=216.59+i*.394
        e1=e0+.39
        for n0,n1 in ((191.56,191.70),(195.64,195.76)):
            surface.face([(e,n,grade(e,n)+.020) for e,n in ((e0,n0),(e1,n0),(e1,n1),(e0,n1))],kerb)
    gutter_n=191.48
    xs=[217.38+i*.23 for i in range(9)]
    for a,b in zip(xs,xs[1:]):
        surface.face([(e,n,grade(e,n)+.024) for e,n in ((a,gutter_n),(b,gutter_n),
            (b,gutter_n+.063),(a,gutter_n+.063))],gutter)
        surface.face([(e,n,grade(e,n)+.027) for e,n in ((a+.087,gutter_n),(a+.110,gutter_n),
            (a+.110,gutter_n+.063),(a+.087,gutter_n+.063))],drain)
    f=Fixture(surface,223.39,193.67,floor)
    for x in (-.065,-.025,.075):
        f.box(x,x+.017,-1.963,1.946,.004,.014,drain)
    return surface.save()
