"""Build the registered Zhongxing Road public arcade and retire the street-side trial shell."""
import json
from math import ceil, cos, pi, sin
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
STREETS = HERE.parent
SCENE = STREETS.parents[1]
sys.path[:0] = [str(STREETS), str(SCENE/"district_500")]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, latest_donors, load_current, read, strip_plots
from riverside import area, bounds, clip_polygon, material, part, terrain_faces

MODEL = "zhongxing-arcade10"
PREVIOUS = ("western-public-30-31-33-49", STREETS/"western_public_30_31_33_49/western-public-30-31-33-49.blend")
OLD_FRONT = ["COL_Zhongxing10_PublicPaving", "COL_Zhongxing10_PublicArcadeFace",
             "Zhongxing10_ArcadePlinthAndRecesses", "COL_Zhongxing10_WhiteAndBlueRail"]


class Frontage:
    def __init__(self, south, north):
        self.start = Vector(south)
        span = Vector(north) - self.start
        self.length = span.length
        self.axis = span.normalized()
        self.west = Vector((-self.axis.y,self.axis.x))

    def point(self, distance, offset):
        return self.start + self.axis*distance + self.west*offset

    def curb(self, distance):
        # Interpolate the observed ends. The short extensions meet street paving.
        return 7.08 - .055 * min(max(distance + 2.51, 0.), 19.8)

    def position(self, distance, offset, y):
        return (*self.point(distance,offset),y)

    def soffit(self, distance):
        return 53.16 + .063*distance


def materials():
    result, registered = {}, {}
    for k,label,tint,texture in (
        ("brick","Zhongxing10 warm coursed street brick",(.94,.80,.72),"brick_wall_08_diff_2k.jpg"),
        ("brick_shade","Zhongxing10 dark recessed brick",(.64,.52,.47),"brick_wall_08_diff_2k.jpg"),
        ("paving","Zhongxing10 grey public flagstones",(.76,.77,.80),"concrete_floor_worn_001_diff_2k.jpg"),
        ("walk","Zhongxing10 grey apron pavers",(.78,.77,.74),"concrete_floor_worn_001_diff_2k.jpg"),
        ("stone","Zhongxing10 granular pale coping and caps",(.82,.82,.76),"concrete_wall_006_diff_2k.jpg"),
        ("asphalt","Zhongxing10 weathered east asphalt shoulder",(.69,.70,.72),"asphalt_02_diff_1k.jpg"),
        ("red_paving","Zhongxing10 warm muted stop treatment",(.63,.33,.26),"concrete_floor_worn_001_diff_2k.jpg"),
    ):
        result[k] = material(label,tint,texture)
        registered[label] = "res://assets/chongqing_district_"+texture
    for k,label,rgb,rough,metal in (
        ("dark","Zhongxing10 dark anodised mullion",(.070,.081,.085),.59,.22),
        ("glazing","Zhongxing10 street blue-grey glazing",(.082,.145,.178),.32,.19),
        ("grey_glass","Zhongxing10 neutral glazing chord",(.058,.090,.105),.38,.17),
        ("shade","Zhongxing10 covered ceiling",(.115,.104,.091),.88,0.),
        ("blue","Zhongxing10 painted blue post",(.046,.235,.44),.56,.11),
        ("pale","Zhongxing10 pale galvanized rail",(.65,.69,.68),.48,.24),
        ("grate","Zhongxing10 roadside drain slots",(.065,.071,.074),.85,.15),
        ("shelter","Zhongxing10 grey station shelter",(.31,.32,.29),.61,.18),
        ("shelter_edge","Zhongxing10 painted fascia return",(.43,.43,.38),.63,.14),
        ("stop_panel","Zhongxing10 green vitreous enamel edge",(.26,.38,.32),.67,.07),
        ("threshold_dark","Zhongxing10 deep threshold shadow",(.068,.069,.058),.87,0.),
        ("sash","Zhongxing10 weathered light door frames",(.29,.30,.27),.63,.12),
        ("hinge","Zhongxing10 dark bronze door and case fittings",(.28,.24,.19),.43,.48),
        ("specular_pane","Zhongxing10 cool upper sky reflection",(.16,.24,.29),.35,.26),
        ("sill","Zhongxing10 brushed sill and pull rail",(.36,.39,.385),.52,.25),
        ("fixture","Zhongxing10 opal soffit lenses",(.72,.71,.58),.66,0.),
        ("ochre","Zhongxing10 worn ochre street marking",(.52,.38,.15),.93,0.),
    ):
        mat = bpy.data.materials.new(label)
        mat.diffuse_color = (*rgb,1.)
        mat.roughness = rough
        mat.metallic = metal
        result[k] = mat
        boost = {"dark":.20, "shade":.24, "glazing":.13, "grey_glass":.11,
                 "specular_pane":.16, "sash":.16, "shelter":.13,
                 "threshold_dark":.08, "fixture":.35}.get(k,0)
        if boost:
            mat.use_nodes = True
            shader = mat.node_tree.nodes.get("Principled BSDF")
            shader.inputs["Base Color"].default_value = (*rgb, 1)
            shader.inputs["Roughness"].default_value = rough
            shader.inputs["Metallic"].default_value = metal
            shader.inputs["Emission Color"].default_value = (*rgb, 1)
            shader.inputs["Emission Strength"].default_value = boost
    for key, label in (("name", "station name"), ("passengers", "passenger information"),
                       ("poster", "courtesy poster")):
        mat = bpy.data.materials.new(f"Zhongxing10 printed {label}")
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Roughness"].default_value = .47
        shader.inputs["Emission Strength"].default_value = .22
        texture = mat.node_tree.nodes.new("ShaderNodeTexImage")
        filename = f"arcade10-stop-{key}.png"
        texture.image = bpy.data.images.load(str(ASSETS/filename),check_existing=True)
        texture.image.pack()
        mat.node_tree.links.new(texture.outputs['Color'], shader.inputs['Base Color'])
        mat.node_tree.links.new(texture.outputs['Color'], shader.inputs['Emission Color'])
        result[key] = mat
        registered[mat.name] = f"res://assets/district_500/{filename}"
    glass = bpy.data.materials.new("Zhongxing10 glass over printed paper")
    glass.use_nodes = True
    glass.surface_render_method = 'BLENDED'
    shader = glass.node_tree.nodes.get("Principled BSDF")
    shader.inputs['Base Color'].default_value = (.47,.58,.62,1)
    shader.inputs['Alpha'].default_value = .12
    shader.inputs['Roughness'].default_value = .21
    result['panel_glass'] = glass
    return result, registered


def terrain_band(mesh, field, tiles, start, end, land, street, offset, finish):
    quad = [Vector((*field.point(t,d(t)),0.)) for t,d in ((start,land),(end,land),(end,street),(start,street))]
    zone = bounds(quad)
    edges = [(a,Vector((a.y-b.y,b.x-a.x,0.)).normalized()) for a,b in zip(quad,quad[1:]+quad[:1])]
    covered = 0.
    for tile, triangles in tiles:
        if not part(zone,tile):
            continue
        for box,triangle in triangles:
            if not part(zone,box):
                continue
            clipped = triangle
            for origin,normal in edges:
                clipped,_ = clip_polygon(clipped,lambda point: normal.dot(point-origin))
                if len(clipped) < 3:
                    break
            if len(clipped)<3 or area(clipped)<1e-6:
                continue
            covered += area(clipped)
            mesh.face([(p.x,p.y,p.z+offset) for p in clipped],finish)
    assert .996 <= covered/area(quad) <= 1.004, (mesh.name,covered,area(quad))


def block(mesh, field, s0,s1,d0,d1,foot,top,finish):
    points = [(s0,d0),(s1,d0),(s1,d1),(s0,d1)]
    mesh.solid([field.position(s,d,foot(s,d)) for s,d in points],
               [field.position(s,d,top(s,d)) for s,d in points],finish)


class PrintedFaces(Mesh):
    def board(self, field, a, b, offset, low, high, material):
        self.face([field.position(s,offset,h(s,offset))
                   for s,h in ((b,low),(a,low),(a,high),(b,high))],material)

    def save(self):
        obj = super().save()
        for face in obj.data.polygons:
            for loop, point in zip(face.loop_indices, ((0,0),(1,0),(1,1),(0,1))):
                obj.data.uv_layers.active.data[loop].uv = point
        return obj


def stop_structure(mesh, printwork, glass, field, apron, m):
    def raised(height):
        return lambda s,d: apron(s,d)+height

    # The shared shallow canopy has two glazed cases below the fascia.
    for position in (13.92,17.82,21.05):
        block(mesh,field,position-.055,position+.055,4.78,4.91,apron,raised(2.60),m['shelter'])
        block(mesh,field,position-.105,position+.105,4.73,4.96,raised(.03),raised(.12),m['hinge'])
        block(mesh,field,position-.16,position+.16,4.24,5.87,raised(2.48),raised(2.56),m['shelter_edge'])
    block(mesh,field,13.49,21.70,4.20,5.94,raised(2.57),raised(2.685),m['shelter'])
    block(mesh,field,13.49,21.70,5.91,5.99,raised(2.51),raised(2.69),m['shelter_edge'])
    block(mesh,field,13.55,21.64,5.987,6.007,raised(2.51),raised(2.55),m['dark'])
    for position in (14.62,16.26,18.71,20.32):
        block(mesh,field,position-.20,position+.20,4.88,4.98,raised(2.526),raised(2.57),m['fixture'])
    for a,b,paper in ((14.19,17.59,'poster'),(18.07,20.89,'passengers')):
        offset = 4.92
        block(mesh,field,a,b,offset-.11,offset-.026,raised(.78),raised(2.28),m['shelter'])
        for edge in (a,b-.077):
            block(mesh,field,edge,edge+.077,offset-.04,offset+.053,raised(.76),raised(2.295),m['shelter_edge'])
        for y in (.76,2.217):
            block(mesh,field,a,b,offset-.04,offset+.054,raised(y),raised(y+.078),m['shelter_edge'])
        printwork.board(field,a+.087,b-.087,offset-.012,raised(.848),raised(2.206),m[paper])
        glass.board(field,a+.086,b-.086,offset+.026,raised(.841),raised(2.211),m['panel_glass'])
        # Case hinges and a narrow lock flange sit on the outside of the glass.
        for y in (.99,1.94):
            block(mesh,field,b-.09,b-.046,offset+.05,offset+.077,raised(y),raised(y+.085),m['hinge'])
        block(mesh,field,a+.044,a+.080,offset+.049,offset+.08,raised(1.41),raised(1.57),m['hinge'])

    name_start,name_end = 17.39,19.35
    for x in (name_start+.16,name_end-.16):
        block(mesh,field,x-.027,x+.027,5.60,5.67,raised(2.61),raised(2.99),m['shelter'])
    block(mesh,field,name_start,name_end,5.58,5.685,raised(2.74),raised(3.32),m['stop_panel'])
    printwork.board(field,name_start+.021,name_end-.021,5.689,raised(2.758),raised(3.302),m['name'])


def frontage(field, ground, tiles, m):
    length = field.length
    def level(s,d):
        p = field.point(s,d)
        hit = ground.ray_cast(Vector((*p,90)),Vector((0,0,-1)),110)[0]
        assert hit is not None, (s,d)
        return hit.z
    def apron(s,d):
        return level(s,d)+.08
    def soffit(s,_d):
        return field.soffit(s)
    def up(extra):
        return lambda s,_d:field.soffit(s)+extra

    foot = Mesh("COL_Zhongxing10_ArcadePublicFlags")
    shoulder = Mesh("COL_Zhongxing10_ContinuedShoulder")
    curb = Mesh("COL_Zhongxing10_StreetKerb")
    terrace = Mesh("Zhongxing10_PavingJointsAndDrain")
    structure = Mesh("COL_Zhongxing10_RegisteredBrickPiers")
    ceiling = Mesh("COL_Zhongxing10_ArcadeSoffitAndExterior")
    frames = Mesh("Zhongxing10_ContinuousUpperWindowAndTransoms")
    rear = Mesh("COL_Zhongxing10_RecessedThresholds")
    street_rail = Mesh("COL_Zhongxing10_BlueAndWhiteRail")
    canopy = Mesh("COL_Zhongxing10_PublicStopShelter")
    printwork = PrintedFaces("Zhongxing10_StationEnamelAndPrintedNotices")
    shelter_glass = PrintedFaces("Zhongxing10_GlazedShelterCases")
    site_start,site_end = -6.15,length+3.1
    sections = ceil((site_end-site_start)/1.1)
    for i in range(sections):
        a = site_start+(site_end-site_start)*i/sections
        b = site_start+(site_end-site_start)*(i+1)/sections
        terrain_band(foot,field,tiles,a,b,lambda s:-.20,field.curb,.08,m["walk"])
        terrain_band(shoulder,field,tiles,a,b,field.curb,lambda s:15.10+.12*(s-site_start),.027,m["asphalt"])
        block(curb,field,a,b,field.curb(a)-.12,field.curb(b)+.26,level,
              lambda s,d:level(s,d)+.023+.112*min(1.,(s-site_start)/.90,(site_end-s)/.90),m["stone"])
        # Recessed-looking dark drain across the curb, split into steel slots.
        if i in (4,9,15,21):
            for j in range(5):
                x=a+.11*j
                block(terrace,field,x,x+.045,field.curb(x)+.31,field.curb(x)+.61,
                      lambda s,d:level(s,d)+.030,lambda s,d:level(s,d)+.051,m["grate"])
    terrain_band(foot,field,tiles,-3.5,length+1.25,lambda s:-3.55,lambda s:-.20,.08,m["paving"])
    terrain_band(shoulder,field,tiles,11.5,24.25,lambda s:field.curb(s)+.65,
                 lambda s:field.curb(s)+2.9,.037,m["red_paving"])
    for idx,s in enumerate([site_start+1.0+i*1.17 for i in range(25)]):
        for d in (1.,3.,5.):
            block(terrace,field,s,s+.012,d-.92,d+.92,apron,
                  lambda u,v:apron(u,v)+.008,m["paving"] if idx%4 else m["stone"])
        for d in (.20, 1.84, 3.48, 5.12):
            start = s + (.28 if idx%2 else -.28)
            block(terrace,field,start,start+.77,d-.013,d+.013,apron,
                  lambda u,v:apron(u,v)+.010,m["stone"])
    for start in (13.6,16.3,19.0,21.7):
        marks = [(start,7.02),(start+1.48,8.93),(start+1.56,8.84),(start+.08,6.93)]
        terrace.face([field.position(s,d,level(s,d)+.049) for s,d in marks],m["ochre"])

    for s in (0.,length):
        block(structure,field,s-.415,s+.415,-.64,.30,level,up(.08),m["brick"])
        for side in (-1,1):
            near,far= sorted((s+side*.24,s+side*.32))
            block(structure,field,near,far,.29,.345,level,up(-.31),m["brick_shade"])
        block(structure,field,s-.49,s+.49,-.70,.41,up(-.235),up(.068),m["stone"])
        block(structure,field,s-.48,s+.48,-.68,.36,level,
              lambda u,v:level(u,v)+.42,m["stone"])
    for a,b in ((-3.15,-.45),(length+.40,length+2.60)):
        block(ceiling,field,a,b,-.82,.16,level,up(4.54),m["brick"])
        for s in (a,b-.22):
            block(ceiling,field,s,s+.22,-3.43,-.82,level,up(4.54),m["brick_shade"])
    block(ceiling,field,-.40,length+.45,-3.42,.18,soffit,up(.29),m["shade"])
    block(ceiling,field,-3.15,length+2.60,-1.18,.19,up(.23),up(4.51),m["brick"])
    block(ceiling,field,-3.16,length+2.61,-1.31,.28,up(4.44),up(4.56),m["stone"])
    for add in (.18,.35,.51):
        block(frames,field,-2.92,length+2.31,.19,.259,up(add),up(add+.063),m["brick_shade"])
    for add in (4.3,4.55):
        block(frames,field,-3.18,length+2.64,.15,.34,up(add),up(add+.061),m["stone"])

    # The two photographed caps locate the opening. The south end of the
    # upper dark window band is independently registered 2.67 m inward.
    begin,end = 2.67,length-.55
    block(frames,field,begin,end,.16,.32,up(.83),up(3.05),m["dark"])
    for height in (.83,1.79,2.97):
        block(frames,field,begin-.035,end+.043,.31,.417,up(height),up(height+.073),m['sill'])
    block(frames,field,begin-.067,end+.09,.313,.476,up(.80),up(.865),m['stone'])
    count = 15
    for i in range(count):
        a=begin+(end-begin)*i/count
        b=begin+(end-begin)*(i+1)/count
        block(frames,field,a-.032,a+.033,.313,.420,up(.893),up(2.971),m['sill'])
        block(frames,field,a+.041,b-.041,.318,.361,up(.905),up(1.777),m['grey_glass'])
        upper = 'specular_pane' if i in (1,4,8,12) else 'glazing'
        block(frames,field,a+.041,b-.041,.318,.364,up(1.875),up(2.955),m[upper])
        if upper=='specular_pane':
            block(frames,field,a+.100,a+.156,.362,.373,up(2.03),up(2.87),m['glazing'])
    block(frames,field,end-.042,end+.032,.313,.420,up(.893),up(2.971),m['sill'])
    for i in range(5):
        y=.98+i*.37
        block(frames,field,end-2.22,end-.10,.39,.447,up(y),up(y+.07),m["dark"])

    # The frontage ends at a shallow threshold wall. It represents no tenant interior.
    a,b,d = .48,length-.49,-3.47
    block(rear,field,a,b,d-.18,d-.07,level,lambda s,o:level(s,o)+.25,m["brick_shade"])
    block(rear,field,a,b,d-.39,d-.32,lambda s,o:level(s,o)+.25,up(-.015),m["brick_shade"])
    for lamp in (1.72,5.72,9.33,14.50,18.61):
        block(frames,field,lamp-.09,lamp+.09,-1.16,-.98,up(-.065),up(-.008),m['sill'])
        block(frames,field,lamp-.057,lamp+.057,-1.13,-1.01,up(-.082),up(-.061),m['fixture'])
    for index,(gap0,gap1) in enumerate(((.82,4.42),(5.17,9.35),(10.15,14.27),(15.05,20.53))):
        def height(delta):
            return lambda s,o: level(s,o)+delta

        for jamb in (gap0,gap1-.14):
            block(rear,field,jamb,jamb+.28,d-.34,d+.26,level,up(-.035),m["brick"])
        door = gap0 + (1.18 if index%2 else .84)
        door_end = door + (1.63 if index%2 else 1.49)
        for left,right in ((gap0+.20,door),(door_end,gap1-.17)):
            sill_height = .70 if index in (0,3) else .48
            block(frames,field,left,right,d+.006,d+.075,height(sill_height),height(2.39),m['grey_glass'])
            block(rear,field,left,right,d-.19,d+.115,level,height(sill_height),m['brick_shade'])
            block(frames,field,left,right,d+.09,d+.195,height(sill_height),height(sill_height+.072),m['stone'])
            for div in (left+.045,(left+right)/2,right-.045):
                block(frames,field,div-.025,div+.025,d+.06,d+.146,height(sill_height),height(2.40),m['sill'])
            block(frames,field,left,right,d+.07,d+.139,height(1.76),height(1.82),m['sash'])
        # A framed facade has a visible return, threshold, inner frame and shallow blank reveal.
        for jamb in (door-.10,door_end-.026):
            block(rear,field,jamb,jamb+.127,d-.22,d+.24,level,height(2.47),m['stone'])
        block(frames,field,door,door_end,d-.305,d-.27,height(.076),height(2.37),m['threshold_dark'])
        block(frames,field,door+.09,door_end-.09,d-.237,d-.199,height(.44),height(2.22),m['glazing'])
        for bar in (door+.067,(door+door_end)*.5,door_end-.067):
            block(frames,field,bar-.034,bar+.034,d-.21,d-.145,height(.12),height(2.30),m['sash'])
        for hand in ((door+door_end)*.5-.15,(door+door_end)*.5+.15):
            block(frames,field,hand-.016,hand+.016,d-.15,d-.094,height(.946),height(1.20),m['sill'])
        block(frames,field,door,door_end,d-.24,d+.25,height(.074),height(.139),m['stone'])
        block(frames,field,door-.064,door_end+.064,d-.19,d+.26,height(2.29),height(2.52),m['sash'])
        block(frames,field,gap0+.23,gap1-.18,d-.16,d-.04,
              lambda s,o:level(s,o)+2.53,up(-.17),m["glazing"])
        for j in range(1,5):
            div=gap0+(gap1-gap0)*j/5
            block(frames,field,div-.032,div+.032,d-.06,d,
                  lambda s,o:level(s,o)+2.52,up(-.14),m["dark"])
        block(frames,field,gap0+.15,gap1-.15,d-.08,d+.02,
              lambda s,o:level(s,o)+2.48,lambda s,o:level(s,o)+2.61,m["dark"])

    # White guard rails with blue posts follow the two measured road-edge endpoints.
    for i in range(9):
        a = -2.51+i*(15.05/9)
        b = -2.51+(i+1)*(15.05/9)
        lateral = field.curb((a+b)/2)-.14
        for height in (.14,.91):
            block(street_rail,field,a,b,lateral-.028,lateral+.028,
                  lambda s,d,h=height:apron(s,d)+h,lambda s,d,h=height:apron(s,d)+h+.045,m["pale"])
        for j in range(1,11):
            s=a+(b-a)*j/11
            block(street_rail,field,s-.012,s+.012,lateral-.016,lateral+.016,
                  lambda u,d:apron(u,d)+.15,lambda u,d:apron(u,d)+.93,m["pale"])
    for i in range(10):
        s = -2.51+i*(15.05/9)
        d = field.curb(s)-.14
        block(street_rail,field,s-.046,s+.046,d-.049,d+.049,apron,
              lambda u,v:apron(u,v)+.985,m["blue"])
    stop_structure(canopy,printwork,shelter_glass,field,apron,m)

    local_route = [(-4.65,4.95),(-2.10,4.26),(.95,3.28),(3.75,1.55),(5.25,-1.65),
                   (9.05,-1.75),(13.0,-1.76),(17.25,-1.66),(18.80,-1.58)]
    route = [field.position(s,d,apron(s,d)) for s,d in local_route]
    layer = [mesh.save() for mesh in (foot,shoulder,curb,terrace,structure,ceiling,frames,rear,street_rail,
                                    canopy,printwork,shelter_glass)]
    return layer, route


def build(out):
    registered = read(HERE/"registration.json")
    caps = registered["first_two_independent_views"]
    field = Frontage(caps["south_cap"]["east_north"],caps["north_cap"]["east_north"])
    donors = latest_donors((PREVIOUS,))
    donors["COL_Outer500_Surface_09_07"] = STREETS/"fenghuangtai_11/fenghuangtai-11.blend"
    for name in ("COL_Outer500_Surface_09_07","COL_Outer500_Surface_09_08"):
        if name in donors:
            load_current(name,donors[name])
    finishes, textures = materials()
    geometry, routes = frontage(field,terrain(),list(terrain_faces()),finishes)
    replacements, removed, counts = strip_plots(read(HERE/"ownership-10.json"),
        (10,),read(ASSETS/"layout.json"),donors)
    aliases = read(ASSETS/(PREVIOUS[0]+".json"))["borrowed_materials"]
    materials_by_mesh = {obj.name:{k:v for k,v in aliases[obj.name].items()
                         if k in {slot.name for slot in obj.data.materials}}
                         for obj in replacements}
    keep = geometry+replacements
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(MODEL+".blend")),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(out/(MODEL+".glb")),export_format="GLB",
                              export_image_format="NONE",export_cameras=False,export_lights=False)
    plan = {"new_meshes":[x.name for x in geometry],"replacement_meshes":[x.name for x in replacements],
            "retired_objects":removed+OLD_FRONT,"retired_plots":[10],"removed_plot_faces":counts,
            "borrowed_materials":materials_by_mesh,"surface_textures":textures,"walks":{"10":routes},
            "pillar_caps_en":[list(field.point(0,0)),list(field.point(field.length,0))],
            "curb_limits_m":{"south":-6.15,"north":field.length+3.1}}
    plan["shaded_surface_fill"] = {
        finishes["brick"].name: [.59,.97,.86,.79],
        finishes["brick_shade"].name: [.34,.92,.81,.75],
        finishes["stone"].name: [.32,.98,.98,.95],
        finishes["paving"].name: [.13,.9,.92,.95],
        finishes["name"].name: [.78,1,1,1],
        finishes["passengers"].name: [.48,1,1,1],
        finishes["poster"].name: [.48,1,1,1],
    }
    (out/(MODEL+".json")).write_text(json.dumps(plan,indent=2)+"\n")
    print("CQ_ARCADE10_BUILD",counts,routes)


if __name__ == "__main__":
    build(Path(sys.argv[-1]).resolve())
