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
        ("dark","Zhongxing10 dark anodised mullion",(.025,.032,.036),.57,.36),
        ("glazing","Zhongxing10 street blue-grey glazing",(.040,.069,.090),.29,.24),
        ("grey_glass","Zhongxing10 neutral glazing chord",(.029,.046,.054),.38,.18),
        ("shade","Zhongxing10 covered ceiling",(.060,.056,.052),.9,0.),
        ("blue","Zhongxing10 painted blue post",(.046,.235,.44),.56,.11),
        ("pale","Zhongxing10 pale galvanized rail",(.65,.69,.68),.48,.24),
        ("grate","Zhongxing10 roadside drain slots",(.065,.071,.074),.85,.15),
        ("shelter","Zhongxing10 grey station shelter",(.23,.24,.235),.65,.18),
        ("stop_panel","Zhongxing10 pale stop sign backing",(.57,.66,.57),.75,.03),
        ("threshold_dark","Zhongxing10 deep threshold shadow",(.023,.023,.020),.88,0.),
        ("sash","Zhongxing10 weathered light door frames",(.29,.28,.24),.67,.12),
        ("ochre","Zhongxing10 worn ochre street marking",(.52,.38,.15),.93,0.),
    ):
        mat = bpy.data.materials.new(label)
        mat.diffuse_color = (*rgb,1.)
        mat.roughness = rough
        mat.metallic = metal
        result[k] = mat
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
    count = 15
    for i in range(count):
        a=begin+(end-begin)*i/count
        b=begin+(end-begin)*(i+1)/count
        finish=m["grey_glass"] if i%4 in (1,2) else m["glazing"]
        block(frames,field,a+.036,b-.038,.317,.363,up(.99),up(2.92),finish)
        block(frames,field,a+.036,b-.038,.362,.392,up(1.82),up(1.86),m["dark"])
    for i in range(5):
        y=.98+i*.37
        block(frames,field,end-2.22,end-.10,.39,.447,up(y),up(y+.07),m["dark"])

    # The frontage ends at a shallow threshold wall. It represents no tenant interior.
    a,b,d = .48,length-.49,-3.47
    block(rear,field,a,b,d-.18,d-.07,level,lambda s,o:level(s,o)+.25,m["brick_shade"])
    block(rear,field,a,b,d-.23,d-.17,lambda s,o:level(s,o)+.25,up(-.015),m["shade"])
    for index,(gap0,gap1) in enumerate(((.82,4.42),(5.17,9.35),(10.15,14.27),(15.05,20.53))):
        for jamb in (gap0,gap1-.14):
            block(rear,field,jamb,jamb+.19,d-.18,d+.23,level,up(-.035),m["brick"])
        door = gap0 + (1.18 if index%2 else .84)
        door_end = door + (1.63 if index%2 else 1.49)
        for left,right in ((gap0+.20,door),(door_end,gap1-.17)):
            block(frames,field,left,right,d+.035,d+.088,
                  lambda s,o:level(s,o)+.24,lambda s,o:level(s,o)+2.46,m["grey_glass"])
            block(frames,field,left,right,d+.082,d+.121,
                  lambda s,o:level(s,o)+.24,lambda s,o:level(s,o)+.44,m["brick_shade"])
        block(frames,field,door,door_end,d-.17,d-.135,level,
              lambda s,o:level(s,o)+2.47,m["threshold_dark"])
        for jamb in (door-.052,door_end-.052):
            block(frames,field,jamb,jamb+.105,d-.15,d+.20,level,
                  lambda s,o:level(s,o)+2.49,m["sash"])
        block(frames,field,door,door_end,d-.06,d+.20,
              lambda s,o:level(s,o)+.072,lambda s,o:level(s,o)+.139,m["stone"])
        block(frames,field,door-.055,door_end+.052,d-.08,d+.20,
              lambda s,o:level(s,o)+2.33,lambda s,o:level(s,o)+2.50,m["sash"])
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
    for station in (14.1,20.85):
        block(canopy,field,station-.065,station+.065,4.65,4.78,apron,
              lambda s,d:apron(s,d)+2.63,m["shelter"])
    block(canopy,field,13.44,21.51,4.16,5.92,lambda s,d:apron(s,d)+2.61,
          lambda s,d:apron(s,d)+2.78,m["shelter"])
    for i,(a,b) in enumerate(((14.38,15.86),(16.10,17.57),(18.43,20.39))):
        panel = m["sash"] if i==0 else m["shelter"]
        block(canopy,field,a,b,4.61,4.70,lambda s,d:apron(s,d)+.59,
              lambda s,d:apron(s,d)+2.19,panel)
        block(frames,field,a+.085,b-.075,4.695,4.722,lambda s,d:apron(s,d)+.68,
              lambda s,d:apron(s,d)+2.10,m["stop_panel"] if i==0 else m["brick_shade"])
    block(frames,field,16.2,19.35,4.55,4.75,lambda s,d:apron(s,d)+2.79,
          lambda s,d:apron(s,d)+3.08,m["stop_panel"])

    local_route = [(-4.65,4.95),(-2.10,4.26),(.95,3.28),(3.75,1.55),(5.25,-1.65),
                   (9.05,-1.75),(13.0,-1.76),(17.25,-1.66),(18.80,-1.58)]
    route = [field.position(s,d,apron(s,d)) for s,d in local_route]
    layer = [mesh.save() for mesh in (foot,shoulder,curb,terrace,structure,ceiling,frames,rear,street_rail,canopy)]
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
        finishes["brick"].name: [.36,.97,.86,.79],
        finishes["brick_shade"].name: [.20,.92,.81,.75],
        finishes["stone"].name: [.25,.98,.98,.95],
        finishes["paving"].name: [.13,.9,.92,.95],
    }
    (out/(MODEL+".json")).write_text(json.dumps(plan,indent=2)+"\n")
    print("CQ_ARCADE10_BUILD",counts,routes)


if __name__ == "__main__":
    build(Path(sys.argv[-1]).resolve())
