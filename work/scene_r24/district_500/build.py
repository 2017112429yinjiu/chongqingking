"""Blender 4.3.2: blender -b -t 4 -P build.py. Coordinates are east, north, up."""
from bisect import bisect_right
import json
from math import atan2, cos, hypot, pi, sin
from pathlib import Path
from random import Random
import sys

from mathutils import Vector
from mathutils.geometry import tessellate_polygon

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
GAME = HERE.parents[1] / "project/chongqing_godot_v05"
ASSETS = GAME / "assets"
OUT = ASSETS / "district_500"
OUT.mkdir(exist_ok=True)
baseline = json.loads((HERE / "terrain_baseline.json").read_text(encoding="utf-8-sig"))["terrain_profiles"]
osm = json.loads((GAME / "source_data/geo_layout.json").read_text(encoding="utf-8-sig"))
river = json.loads((GAME / "source_data/river_r22/river_plan.json").read_text(encoding="utf-8-sig"))
water_z = json.loads((ASSETS / "river_r22/layout.json").read_text(encoding="utf-8-sig"))["river_level_m"]
rings = [r["points"] for r in river["rings"] if r["role"] == "outer"]

# OSM lines are retained whole here and clipped by the playable terrain. The
# twin western carriageways are independent. No tunnel or elevated deck is inferred.
mapped_ids = [49182408, 1189963598, 176034707, 734116597, 1513362409, 830761786]
mapped = {item["id"]: item["points"] for item in osm["roads"] if item["id"] in mapped_ids}
design = {
    "ridge": [(-229,92),(-215,121),(-188,153),(-151,171),(-106,178),(-58,165),(-37,145),
              (-12,149),(37,160),(71,181),(117,190),(164,183),(217,169)],
    "west": [(-218,-13),(-218,25),(-233,58),(-229,92)],
    "south": [(-189,-43),(-178,-75),(-154,-109),(-138,-140),(-103,-171),(-61,-179),
              (-16,-172),(23,-153),(60,-137),(105,-124),(146,-113)],
    "south_link": [(16,-99),(16,-111),(18,-130),(23,-153)],
    "east": [(146,-113),(166,-91),(195,-78),(221,-55),(228,-18),(222,20),(205,48)],
    "promenade": [(-156,-107),(-164,-135),(-153,-168),(-123,-195),(-74,-205),
                  (-25,-204),(28,-211),(82,-207),(114,-189),(148,-160),(160,-116)],
    "north_link": [(-55.95,135.83),(-48,150),(-37,145)],
}
# Measured inner road edge elevations are optionally supplied by the native
# baseline probe. Outside those edge corridors the mesh meets the terrain.
tie_file = HERE / "road_ties.json"
ties = json.loads(tie_file.read_text(encoding="utf-8-sig")) if tie_file.exists() else []
roads = [(mapped[k], 3.15 if k in (49182408,1189963598,734116597,1513362409) else 4.25, k) for k in mapped_ids]
roads += [(pts, 2.7 if key in ("promenade", "south_link", "north_link") else 4.2, key)
          for key,pts in design.items()]
segments = [(np.array(a), np.array(b), width, key) for points,width,key in roads
            for a,b in zip(points,points[1:])]

bpy.ops.wm.read_factory_settings(use_empty=True)
rng = Random(52425)
materials = []
def material(name, color, scan=None, relief=False):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = m.diffuse_color
    shader.inputs["Roughness"].default_value = .83
    if scan:
        tex = m.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(ASSETS / ("chongqing_district_"+scan)), check_existing=True)
        tex.image.pack()
        m.node_tree.links.new(tex.outputs["Color"], shader.inputs["Base Color"])
        if relief:
            for suffix in ("nor_gl", "rough"):
                path = scan.replace("_diff_", "_"+suffix+"_").replace("_col_1_", "_"+suffix+"_")
                if suffix == "rough":
                    path = str(Path(path).with_suffix(".png"))
                channel = m.node_tree.nodes.new("ShaderNodeTexImage")
                channel.image = bpy.data.images.load(str(ASSETS / ("chongqing_district_"+path)),check_existing=True)
                channel.image.colorspace_settings.name = "Non-Color"
                channel.image.pack()
                if suffix == "rough":
                    m.node_tree.links.new(channel.outputs["Color"], shader.inputs["Roughness"])
                else:
                    normal = m.node_tree.nodes.new("ShaderNodeNormalMap")
                    normal.inputs["Strength"].default_value = .60
                    m.node_tree.links.new(channel.outputs["Color"],normal.inputs["Color"])
                    m.node_tree.links.new(normal.outputs["Normal"],shader.inputs["Normal"])
            if relief=="weave":
                m.node_tree.links.remove(shader.inputs["Base Color"].links[0])
                m.node_tree.nodes.remove(tex)
    materials.append(m)
    return len(materials)-1

asphalt = material("Asphalt aggregate", (.21,.22,.22), "asphalt_02_diff_1k.jpg")
stone = material("Grey stone walkway", (.40,.37,.32), "stone_floor_diff_2k.jpg")
soil = material("Leaf litter and earth", (.34,.25,.14), "brown_mud_leaves_01_diff_2k.jpg")
grass = material("Scrub bank", (.17,.24,.10))
rock = material("Coursed retaining masonry", (.40,.37,.32), "stone_wall_05_diff_2k.jpg")
cream = material("Aged stucco", (.65,.57,.44), "plastered_wall_04_diff_1k.jpg")
brick = material("Red infill brick", (.38,.21,.15), "brick_wall_08_diff_2k.jpg")
tile = material("Glazed blue tile", (.23,.43,.46), "tile_blue_v4_diff.jpg")
concrete = material("Concrete bands", (.48,.45,.40), "concrete_wall_006_diff_2k.jpg")
roof = material("Grey overlapping roof tiles", (.22,.22,.21), "roof_tiles_diff.jpg")
glass = material("Blue grey street reflection", (.038,.061,.072))
window_shades=[glass,material("Shaded window beyond mesh",(.025,.029,.027)),
               material("Flax curtain behind glazing",(.19,.16,.115)),material("Cloud reflection",(.14,.18,.19))]
cream_metal = material("Painted window and rail trim", (.63,.66,.57))
rust = material("Red painted steel", (.33,.07,.035))
green = material("Jade painted steel", (.08,.22,.18))
ochre = material("Ochre canvas", (.66,.28,.075))
white = material("Off-white road pigment", (.74,.70,.57))
dark = material("Door and shutter recess", (.092,.086,.074))
leaf = [material("Canopy " + str(i), col) for i,col in enumerate(((.13,.23,.089),(.20,.30,.12),(.26,.32,.12)))]
waterfront = material("Washed bank aggregate", (.47,.40,.29), "leaf_scattered_gravel_diff_2k.jpg")
frame_concrete = material("Formed concrete frame",(.48,.45,.40),"concrete_wall_006_diff_2k.jpg",relief=True)
room_finish = {"lime":cream,"dado":material("Cream glazed wall skirting",(.46,.43,.34),"tile_cream_v4_diff.jpg"),
               "stone":concrete,"tile":roof,"wood":material("Worn timber joinery",(.23,.14,.071),"wood_table_worn_diff_2k.jpg",relief=True),
               "iron":dark,"zinc":material("Weathered sheet metal",(.20,.21,.195)),
               "canopy":material("Faded covered market roofing",(.18,.22,.17)),
               "rubber":material("Used tyre casing",(.022,.022,.020)),
               "clay":material("Brown earthenware",(.31,.115,.051)),"china":cream_metal,
               "jade":green,"greens":leaf[1],"leaf_light":leaf[2],"leaf_dark":leaf[0],"gourd":ochre,"linen":cream_metal}
from runpy import run_path
front_tools = run_path(str(HERE/"occupied_fronts.py"))
finish_tools = run_path(str(HERE/"house_finishes.py"))
shop_shade = run_path(str(HERE/"shop_shades.py"))["shade"]
metal=material("Aged galvanized drain pipe",(.31,.32,.30))
bs=materials[metal].node_tree.nodes.get("Principled BSDF")
bs.inputs["Metallic"].default_value=.67
bs.inputs["Roughness"].default_value=.53
facing=dict(room_finish,trim=cream_metal,metal=metal,panes=window_shades,
            canvas=material("Sun washed market canvas",(.53,.43,.28)))
facing.update(wallstone=rock,flags=stone,aged_metal=material("Salvaged service-door steel",(.27,.29,.25),"rusty_painted_metal_diff_2k.jpg",relief=True))
facing["glass"]=material("Thin residential window glass",(.40,.49,.48))
glass_bs=materials[facing["glass"]].node_tree.nodes.get("Principled BSDF")
glass_bs.inputs["Alpha"].default_value=.23
glass_bs.inputs["Roughness"].default_value=.22
materials[facing["glass"]].surface_render_method="DITHERED"
facing["cotton"]=material("Undyed window netting",(.42,.39,.31),"fabric_pattern_07_col_1_2k.jpg",relief="weave")
facing.update(finish_tools["finishes"](ASSETS,materials,material))
indoor_floor=material("Worn concrete floors",(.36,.34,.31),"concrete_floor_worn_001_diff_2k.jpg")

class Geometry:
    def __init__(self, name):
        self.name = name
        self.vertices = []
        self.faces = []
        self.slots = []
        self.uvs = []

    def face(self, points, mat, uvs=None):
        offset = len(self.vertices)
        self.vertices.extend(points)
        self.faces.append(tuple(range(offset,offset+len(points))))
        self.slots.append(mat)
        if uvs is None:
            a,b,c = points[:3]
            u = np.array(b)-a
            v = np.cross(np.cross(u,np.array(c)-a),u)
            u /= max(np.linalg.norm(u),.001)
            v /= max(np.linalg.norm(v),.001)
            uvs = [(float(np.dot(np.array(p)-a,u))/2,float(np.dot(np.array(p)-a,v))/2) for p in points]
        self.uvs.append(uvs)

    def finish(self):
        if not self.faces:
            return
        mesh = bpy.data.meshes.new(self.name)
        mesh.from_pydata(self.vertices, [], self.faces)
        used = {key:i for i,key in enumerate(sorted(set(self.slots)))}
        for key in used:
            mesh.materials.append(materials[key])
        coords = mesh.uv_layers.new()
        for face, slot, uv in zip(mesh.polygons,self.slots,self.uvs):
            face.material_index = used[slot]
            for index,pair in zip(face.loop_indices,uv):
                coords.data[index].uv = pair
        obj = bpy.data.objects.new(self.name,mesh)
        bpy.context.collection.objects.link(obj)
        return obj

def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)

def edge_height(x,y):
    ex,ey = np.clip((x,y),-100,100)
    side,key = ("east" if x>0 else "west",ey) if abs(x)>=abs(y) else ("north" if y>0 else "south",ex)
    slot = min(199,int(key+100))
    row = baseline[side]
    base = row[slot] + (row[slot+1]-row[slot])*(key+100-slot)
    return base, ex,ey

def inland(x,y):
    for ring in rings:
        inside = False
        for (ax,ay),(bx,by) in zip(ring,ring[1:]+ring[:1]):
            if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:
                inside=not inside
        if inside:
            return False
    return True

def terrain_height(x,y,distance):
    base,ex,ey = edge_height(x,y)
    amount = hypot(x-ex,y-ey)
    hill = 4.6*sin(x/48+y/59)+2.2*cos(y/29-x/63)+1.1*sin((x-y)/19)
    target = max(water_z+1.25,20.1+.127*y+.018*x+hill)
    level = base+(target-base)*smooth(amount/90)
    if amount < 50:
        side,key = ("east" if x>0 else "west",ey) if abs(x)>=abs(y) else ("north" if y>0 else "south",ex)
        samples = [tie for tie in ties if tie["side"]==side and abs(tie["center"]-key)<6]
        if samples:
            tie=min(samples,key=lambda t:abs(t["center"]-key))
            cross=tie["profile"]
            at=int(np.searchsorted([r[0] for r in cross],key))
            if 0<at<len(cross):
                left,right=cross[at-1:at+1]
                shoulder=np.interp(key,[left[0],right[0]],[left[1],right[1]])
                transition=50 if side=="south" else 27
                blend=(1-smooth(amount/transition))*smooth((6-abs(tie["center"]-key))/1.3)
                grade=tie["grade_out"]*min(amount,8)
                level=level*(1-blend)+(shoulder+grade)*blend
    level += smooth(amount/24)*smooth((distance-6)/9)*(.46*sin(x/9+y/14)+.29*cos(y/5-x/6))
    if not inland(x,y):
        return min(level,water_z-.65)
    return level

# Refinement at the join keeps the road-edge and height samples at 1 m.
axis = list(range(-250,-112,2))+list(range(-112,113))+list(range(114,251,2))
axis = sorted(set(axis + [tie["center"] for tie in ties]))
xx, yy = np.meshgrid(axis, axis, indexing="ij")
nearest = np.full(xx.shape,np.inf)
nearest_width = np.zeros(xx.shape)
for a,b,width,key in segments:
    dx,dy=b-a
    t=np.clip(((xx-a[0])*dx+(yy-a[1])*dy)/(dx*dx+dy*dy),0,1)
    distance=np.hypot(xx-a[0]-t*dx,yy-a[1]-t*dy)
    selected=distance<nearest
    nearest[selected]=distance[selected]
    nearest_width[selected]=width
heights = np.array([[terrain_height(x,y,nearest[i,j]) for j,y in enumerate(axis)] for i,x in enumerate(axis)])
def height(x,y):
    i = min(len(axis)-2,max(0,bisect_right(axis,x)-1))
    j = min(len(axis)-2,max(0,bisect_right(axis,y)-1))
    u=(x-axis[i])/(axis[i+1]-axis[i])
    v=(y-axis[j])/(axis[j+1]-axis[j])
    a,b,c,d = heights[i,j],heights[i+1,j],heights[i+1,j+1],heights[i,j+1]
    return float(a+u*(b-a)+v*(c-b) if u>=v else a+u*(c-d)+v*(d-a))

def road_distance(x,y):
    i=min(len(axis)-1,bisect_right(axis,x)-1)
    j=min(len(axis)-1,bisect_right(axis,y)-1)
    return float(nearest[i,j]),float(nearest_width[i,j])

def patch(x,y):
    if abs(x)<100 and abs(y)<100:
        return False
    return -250<=x<=250 and -250<=y<=250 and inland(x,y)

# Tile the collision mesh into neighbourhood-sized chunks. Roads and their
# walkable shoulders use the same triangles as the earth under them.
chunks = {}
for i,(x,nx) in enumerate(zip(axis,axis[1:])):
    for j,(y,ny) in enumerate(zip(axis,axis[1:])):
        mx,my=(x+nx)/2,(y+ny)/2
        if not patch(mx,my):
            continue
        key=(int((mx+250)//50),int((my+250)//50))
        if key not in chunks:
            chunks[key] = Geometry("COL_Outer500_Surface_%02d_%02d" % key)
        batch=chunks[key]
        points=[(x,y,heights[i,j]),(nx,y,heights[i+1,j]),(nx,ny,heights[i+1,j+1]),(x,ny,heights[i,j+1])]
        d=float(nearest[i:i+2,j:j+2].mean())
        w=float(nearest_width[i:i+2,j:j+2].mean())
        mat = asphalt if d<w else stone if d<w+2 else waterfront if min(p[2] for p in points)<water_z+3 else grass if sin(mx/13+my/21)+cos(my/17)>.35 else soil
        for ids in ((0,1,2),(0,2,3)):
            batch.face([points[k] for k in ids],mat,[(points[k][0]/2.4,points[k][1]/2.4) for k in ids])

# Bake a world-coordinate road / sidewalk mask for the engine. Pixel centres
# are south-to-north in Blender; Godot flips V when sampling the exported PNG.
size=1024
mask_axis=(np.arange(size,dtype=np.float32)+.5)*500/size-250
mx,my=np.meshgrid(mask_axis,mask_axis)
md=np.full(mx.shape,1e5,dtype=np.float32)
mw=np.zeros(mx.shape,dtype=np.float32)
for a,b,width,key in segments:
    dx,dy=b-a
    t=np.clip(((mx-a[0])*dx+(my-a[1])*dy)/(dx*dx+dy*dy),0,1)
    d=np.hypot(mx-a[0]-t*dx,my-a[1]-t*dy)
    selected=d<md
    md[selected]=d[selected]
    mw[selected]=width
rgba=np.empty((size,size,4),dtype=np.float32)
rgba[:,:,0]=np.clip((mw-md)*2+.5,0,1)
rgba[:,:,1]=np.clip((mw+1.75-md)*2+.5,0,1)
rgba[:,:,2]=np.clip(.55+.55*np.sin(mx/13+my/21)+.45*np.cos(my/17),0,1)
rgba[:,:,3]=1
for tie in ties:
    sign=-1 if tie["side"] in ("west","south") else 1
    along = my if tie["side"] in ("east","west") else mx
    across = mx if tie["side"] in ("east","west") else my
    depth=across*sign-100
    profile=tie["profile"]
    keys=[r[0] for r in profile]
    # Carry the measured section along its own centreline, including oblique roads.
    normal_axis = 0 if tie["side"] in ("east", "west") else 1
    tangent_axis = 1 - normal_axis
    crossings = []
    for a, b, _, _ in segments:
        delta = b - a
        if abs(delta[normal_axis]) < 1e-6:
            continue
        t = (100 * sign - a[normal_axis]) / delta[normal_axis]
        if 0 <= t <= 1:
            centre = a[tangent_axis] + t * delta[tangent_axis]
            crossings.append((abs(centre - tie["center"]), sign * delta[tangent_axis] / delta[normal_axis]))
    closest = min(crossings, default=(float("inf"), 0.0))
    slope = closest[1] if closest[0] < 2.0 else 0.0
    registered = along - slope * depth
    ak=np.interp(registered,keys,[float(r[2].endswith("asphalt")) for r in profile])
    walk=np.interp(registered,keys,[float("pavement" in r[2] or "curb" in r[2]) for r in profile])
    blend=(depth>=0)*np.clip(1-depth/8,0,1)*np.clip(6-np.abs(registered-tie["center"]),0,1)
    # At the very last centimetres a physics ray can hit the substrate below an
    # old road lip. Keep the mapped carriageway wherever its centreline continues.
    rgba[:,:,0]=np.maximum(rgba[:,:,0],ak*blend)
    rgba[:,:,1]=rgba[:,:,1]*(1-blend)+np.maximum(ak,walk)*blend
def save_surface_mask():
    mask=bpy.data.images.new("Street surface mask",width=rgba.shape[1],height=rgba.shape[0],alpha=False)
    mask.colorspace_settings.name="Non-Color"
    mask.pixels.foreach_set(rgba.ravel())
    mask.filepath_raw=str(OUT/"surface_mask.png")
    mask.file_format="PNG"
    mask.save()
    bpy.data.images.remove(mask)

# Geometry modules are placed on sampled ground, with foundations that follow
# all four corners. Open storefront profiles are recessed and each row has
# varied window bays, balcony occupation and roof furniture.
blocks = Geometry("COL_Outer500_Building_envelopes")
facades = Geometry("Outer500_Facades_and_storefronts")
street = Geometry("Outer500_Street_furniture")
solid = Geometry("COL_Outer500_Retaining_and_boundaries")
tree_sites = []
verges = Geometry("Outer500_Road_details")
skirt = Geometry("Outer500_Background_transition")

def local_frame(x,y,angle):
    c,s=cos(angle),sin(angle)
    def world(u,v,z):
        return (x+c*u-s*v,y+s*u+c*v,z)
    return world

def box(batch, frame, x0,y0,z0,x1,y1,z1,mat):
    points=[frame(x,y,z) for z in (z0,z1) for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))]
    for face in ((3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        batch.face([points[i] for i in face],mat)

def default_frame(x,y,z):
    return x,y,z

def band(batch, a,b, za,zb,width,mat):
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=hypot(dx,dy)
    sx,sy=-dy/length*width/2,dx/length*width/2
    batch.face([(a[0]-sx,a[1]-sy,za),(b[0]-sx,b[1]-sy,zb),
                (b[0]+sx,b[1]+sy,zb),(a[0]+sx,a[1]+sy,za)],mat)

def post(batch,x,y,bottom,top,r,mat,sides=6):
    points=[(x+r*cos(i*2*pi/sides),y+r*sin(i*2*pi/sides)) for i in range(sides)]
    for a,b in zip(points,points[1:]+points[:1]):
        batch.face([(a[0],a[1],bottom),(b[0],b[1],bottom),(b[0],b[1],top),(a[0],a[1],top)],mat)

def ellipsoid(batch,x,y,z,radius,depth,height_radius,mat):
    def point(theta,phi):
        return (x+radius*cos(theta)*cos(phi),y+depth*sin(theta)*cos(phi),z+height_radius*sin(phi))
    for i in range(10):
        a,b=i*2*pi/10,(i+1)*2*pi/10
        lower,upper=-pi/2,pi/2
        for j in range(5):
            p=lower+(upper-lower)*j/5
            q=lower+(upper-lower)*(j+1)/5
            if j==0:
                batch.face([point(a,p),point(b,q),point(a,q)],mat)
            elif j==4:
                batch.face([point(a,p),point(b,p),point(a,q)],mat)
            else:
                batch.face([point(a,p),point(b,p),point(b,q),point(a,q)],mat)

def tree(x,y,r):
    z=height(x,y)
    # Preserve the cloud trial's seeded layout. Its five crown samples now set
    # the orientation and proportions of the scanned donor at the same root.
    crown = [(rng.uniform(-1.35,1.35), rng.uniform(-1.35,1.35),
              rng.uniform(3.4,5.0), rng.uniform(.8,1.65)) for _ in range(5)]
    mean = np.mean(crown, axis=0)
    tree_sites.append({"east_north_up":[float(x),float(y),float(z)-.025],
                       "rotation_deg":float(np.degrees(atan2(mean[1],mean[0]))),
                       "species":int(mean[0]>0), "width_scale":float(r*mean[3]),
                       "height_scale":float(r*mean[2]/4.1)})

ground_floors = run_path(str(HERE / "ground_floors.py"))
through_floor = ground_floors["through_floor"]
build_frame = run_path(str(HERE / "building_frame.py"))["build"]
furnish = run_path(str(HERE / "shop_rooms.py"))["furnish"]
floor_batches = {}
street_windows=run_path(str(HERE/"street_windows.py"))
plinth=run_path(str(HERE/"street_plinth.py"))["build"]
plots = []
lamp_sites = []
flyover_reserves = []
occupied=[]
destinations=[]
def building(x,y,angle,w,d,floors,kind,named=""):
    frame=local_frame(x,y,angle)
    corners=[frame(a,b,0)[:2] for a in (-w/2,w/2) for b in (-d/2,d/2)]
    if any(not patch(a,b) or max(abs(a),abs(b))<113 or max(abs(a),abs(b))>245 for a,b in corners):
        return
    if any(road_distance(a,b)[0]<road_distance(a,b)[1]+1.8 for a,b in corners+[(x,y)]):
        return
    if any(hypot(x-a,y-b)<.48*(w+ow)+2 for a,b,ow in occupied):
        return
    levels=[height(a,b) for a,b in corners]
    base=max(levels)+.17
    if max(levels)-min(levels)>5.8:
        return
    occupied.append((x,y,w))
    # The native hall sweeps met the existing R24 flyover deck here at chest
    # height. Keep its two reservations open and preserve the seeded neighbours.
    if (round(x,2),round(y,2)) in ((158.02,-17.24),(136.40,-33.39)):
        flyover_reserves.append([x,y])
        rng.random()
        return
    facade=(brick,cream,tile,concrete)[kind]
    ry=-d/2
    top=base+floors*2.95
    box(blocks,frame,-w/2,ry,min(levels)-.35,w/2,d/2,base,rock)
    portal = {"南区路车棚修理铺":0.0,"照相巷便民市场":-.78,"江岸茶摊":-1.65}.get(named, (.14 if kind%2 else -.14)*w)
    plot = {"east_north":[float(x),float(y)], "bearing":angle, "width":w, "depth":d,
            "height":base, "roof":top, "floors":floors, "kind":kind, "name":named, "door_u":portal}
    plot["plot_id"]=len(plots)+len(flyover_reserves)
    plots.append(plot)
    def draw(*dims):
        box(blocks,frame,*dims)
    def ground(u,v):
        return height(*frame(u,v,0)[:2])
    structure = Geometry("COL_Outer500_Frame_%02d" % plot["plot_id"])
    def member(*dims):
        box(structure,frame,*dims)
    plot["facade_work"]={"windows":0,"clipped_balconies":0,"enclosed_galleries":0}
    detail = Geometry("Outer500_Joinery_%02d" % plot["plot_id"])
    def trim(*dims):
        box(detail,frame,*dims)
    floors_geo=Geometry("Outer500_InteriorFloor_%02d"%plot["plot_id"])
    floor_batches[plot["plot_id"]]=floors_geo
    def panel(points,mat,uvs=None):
        (floors_geo if mat in facing["floors"] else detail).face([frame(*pt) for pt in points],mat,uvs)
    build_frame(plot,member,frame_concrete)
    plot["street_windows"]=street_windows["plan"](plot)
    through_floor(plot,draw,ground,(facade,stone,rock,concrete,indoor_floor),street_windows["wall_pieces"])
    street_windows["install"](plot,trim,panel,facing)
    for level in range(1,floors):
        lower=base+2.95*level
        front_tools["upper_storey"](plot,level,lower,lower+2.80,member,trim,panel,facade,facing)
    front_tools["rainwater"](plot,trim,panel,facing)
    finish_tools["main_room"](plot,trim,panel,facing,street_windows["wall_pieces"])
    shop_shade(plot,panel,facing)
    detail.finish()
    structure.finish()
    def fitting(*dims):
        box(street,frame,*dims)
    def fit_face(local,mat):
        street.face([frame(*p) for p in local],mat)
    furnish(plot,fitting,draw,fit_face,room_finish)
    box(facades,frame,-w/2-.21,ry-.22,top-.12,w/2+.21,d/2+.22,top+.20,concrete)
    if floors<=3 and kind!=2:
        for side in (-1,1):
            polygon=[frame(-w/2-.38,0,top+1.65),frame(w/2+.38,0,top+1.65),
                     frame(w/2+.38,side*(d/2+.45),top+.15),frame(-w/2-.38,side*(d/2+.45),top+.15)]
            facades.face(polygon if side<0 else polygon[::-1],roof)
        for u in (-w/2,w/2):
            facades.face([frame(u,ry,top),frame(u,d/2,top),frame(u,0,top+1.64)],facade)
    else:
        for u in (-w/2,w/2-.22):
            box(facades,frame,u,ry,top,u+.22,d/2,top+.75,facade)
        for v in (ry,d/2-.22):
            box(facades,frame,-w/2,v,top,w/2,v+.22,top+.75,facade)
        box(facades,frame,-w/4,-1.7,top,-w/4+2.5,1.5,top+2.1,cream)

    # Keep the same downstream seeded plot and planting layout.
    rng.random()
    if named:
        front = ry-2.35
        plinth(plot,frame,solid,box,ground,facing)
        # Two distinct entrances lead to the common sheltered landing.
        for lane in (-w*.27,w*.22):
            span=1.15
            foot=frame(lane,front-6.25,0)[:2]
            foot_level=height(*foot)
            count=max(1,min(28,round((base-foot_level)/.153)))
            if base-foot_level>.13:
                step_depth=min(.315,6.20/count)
                for n in range(count):
                    outer=front-(count-n)*step_depth
                    at=frame(lane,outer,0)[:2]
                    step_level=foot_level+(base-foot_level)*(n+1)/count
                    bottom=min(height(*at)-.12,step_level-.15)
                    left,right=lane-span,lane+span
                    inner=outer+step_depth
                    corners=[(left,outer),(right,outer),(right,inner),(left,inner)]
                    solid.face([frame(u,v,step_level) for u,v in corners],stone,[(u/2.0,v/2.0) for u,v in corners])
                    for j,(aa,bb) in enumerate(zip(corners,corners[1:]+corners[:1])):
                        quad=[(*aa,bottom),(*bb,bottom),(*bb,step_level),(*aa,step_level)]
                        solid.face([frame(*q) for q in quad],concrete if j==0 else rock,
                                   [(q[0 if j%2==0 else 1]/2.20,q[2]/2.20) for q in quad])

        board=room_finish["wood"] if named.endswith("茶摊") else room_finish["iron"] if named.endswith("修理铺") else room_finish["canopy"]
        box(facades,frame,-2.85,ry-2.21,base+2.19,2.85,ry-2.115,base+2.61,board)
        for u in (-2.66,2.66):
            box(street,frame,u-.025,ry-2.16,base+2.54,u+.025,ry-2.08,base+2.66,room_finish["iron"])
        display_z=base+.02
        if named.endswith("市场"):
            for u,cloth in ((-2.6,ochre),(1.1,green),(5.9,rust)):
                for a in (-.84,.84):
                    for b in (-1.60,-.81):
                        box(street,frame,u+a-.045,ry+b-.045,display_z,u+a+.045,ry+b+.045,display_z+.76,dark)
                box(street,frame,u-1,ry-1.73,display_z+.72,u+1,ry-.69,display_z+.80,concrete)
                box(street,frame,u-.98,ry-1.74,display_z+.39,u+.99,ry-1.72,display_z+.80,cloth)
                for j in range(3):
                    cx=u-.73+j*.56
                    box(street,frame,cx-.26,ry-1.54,display_z+.80,cx+.26,ry-.91,display_z+.85,ochre)
                    for b in range(3):
                        box(street,frame,cx-.27,ry-1.54,display_z+.85+b*.045,cx+.27,ry-1.51,display_z+.88+b*.045,ochre)
            run_path(str(HERE/"market_goods.py"))["create"](plot,frame,materials,material)
        elif named.endswith("茶摊"):
            for u in (-3.6,.32,4.9):
                for a in (-.41,.41):
                    for b in (-1.48,-.92):
                        box(street,frame,u+a-.05,ry+b-.05,display_z,u+a+.05,ry+b+.05,display_z+.60,green)
                box(street,frame,u-.52,ry-1.59,display_z+.59,u+.52,ry-.82,display_z+.66,roof)
                px,py,_=frame(u,ry-1.28,0)
                ellipsoid(street,px,py,display_z+.79,.11,.10,.105,cream_metal)
        elif named.endswith("服务站"):
            for u in (-3.4,2.6):
                box(street,frame,u-.60,ry-1.33,display_z,u+.60,ry-.69,display_z+.45,rock)
                box(street,frame,u-.59,ry-1.32,display_z+.45,u+.59,ry-.70,display_z+.51,grass)
        destinations.append({"name":named,"east_north":[x,y],"height":round(base,3),"bearing":angle,"front_offset":ry})

# Rebuild selected licensed exterior footprints. Retire their far-only
# representations in this variant, so the plot has one editable owner.
mapped_elevation=run_path(str(HERE/"mapped_elevations.py"))["elevation"]
mapped_buildings = []
# R21's shared rooftop service structures remain visible at their surveyed
# donor elevations. Rebuild each replaced OSM footprint up to that roof.
legacy_roofs = json.loads((ASSETS / "district_r21/layout.json").read_text(encoding="utf-8-sig"))["rooftops"]
registered_roofs = {int(row["donor"].split("_")[1]): row["position"][1]
                    for row in legacy_roofs if row["donor"].split("_")[1].isdigit()}
mapped_footprints = {809889593,809889594,809889602,809889621,809889631,809889632,809889635,704006706}
for spec in osm["context_buildings"]:
    if spec["id"] not in mapped_footprints:
        continue
    polygon=spec["points"]
    if polygon[0]==polygon[-1]:
        polygon=polygon[:-1]
    if any(not patch(*p) or max(map(abs,p))<109 or max(map(abs,p))>248 for p in polygon):
        continue
    if any(road_distance(*p)[0] < road_distance(*p)[1]+1.8 for p in polygon):
        continue
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1]))
    if area<0:
        polygon=polygon[::-1]
    cx,cy=np.mean(polygon,axis=0)
    levels=[height(x,y) for x,y in polygon]
    level=float(max(levels))+.22
    floors=int(spec.get("tags",{}).get("building:levels", str(4+(spec["id"]%4))))
    top=registered_roofs.get(spec["id"],level+2.92*floors)
    floors=max(1,round((top-level)/2.92))
    storey=(top-level)/floors
    mat=(tile,brick,cream)[spec["id"]%3]
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        az,bz=height(*a)-.28,height(*b)-.28
        blocks.face([(a[0],a[1],az),(b[0],b[1],bz),(b[0],b[1],level),(a[0],a[1],level)],rock)
        length=hypot(b[0]-a[0],b[1]-a[1])
        if length<.001:
            continue
        yaw=atan2(b[1]-a[1],b[0]-a[0])
        frame=local_frame(*a,yaw)
        for floor in range(floors):
            mapped_elevation(spec,floor,level+floor*storey,storey,length,frame,facades,blocks,box,mat,facing)
        box(facades,frame,0,-.13,top,length,.15,top+.60,concrete)
    roof_points=[Vector((x,y,top)) for x,y in polygon]
    for triangle in tessellate_polygon([roof_points]):
        blocks.face([tuple(roof_points[v]) if isinstance(v,int) else tuple(v) for v in triangle],concrete)
    size=max(hypot(x-cx,y-cy)*2 for x,y in polygon)
    occupied.append((cx,cy,size))
    mapped_buildings.append(spec["id"])

# A few larger anchors, with several scales of residential infill.
for args in [
    (-122,163,-.12,19,11,3,2,"马蹄街社区服务站"),
    (-187,-12,.27,25,13,3,0,"南区路车棚修理铺"),
    (166,123,.12,22,13,3,0,"照相巷便民市场"),
    (79,-170,.3,21,12,2,1,"江岸茶摊"),
]:
    building(*args)

for pts,width,key in roads:
    if key=="south_link" or key=="north_link":
        continue
    for a,b in zip(pts,pts[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=hypot(dx,dy)
        if length<12:
            continue
        angle=atan2(dy,dx)
        for index in range(max(1,int(length/21))):
            t=(index+rng.uniform(.32,.68))/max(1,int(length/21))
            cx,cy=a[0]+dx*t,a[1]+dy*t
            for side in (-1,1):
                setback=width+rng.uniform(9,14)
                bx,by=cx-sin(angle)*setback*side,cy+cos(angle)*setback*side
                if rng.random()<.80 and key!="promenade":
                    building(bx,by,angle+(pi if side<0 else 0),rng.uniform(9,20),rng.uniform(7,13),
                             rng.choice((2,3,4,4,5,6)),rng.randrange(4))
                tx,ty=cx-sin(angle)*(width+3.35)*side,cy+cos(angle)*(width+3.35)*side
                if patch(tx,ty) and max(abs(tx),abs(ty))>109 and road_distance(tx,ty)[0]>width+2.5:
                    if rng.random()<.72:
                        tree(tx,ty,rng.uniform(.65,1.17))
                    else:
                        z=height(tx,ty)
                        lamp_sites.append((tx,ty,z,angle))

for _ in range(970):
    x,y=rng.uniform(-246,246),rng.uniform(-246,246)
    if not patch(x,y) or max(abs(x),abs(y))<108:
        continue
    distance,width=road_distance(x,y)
    if distance<width+5 or any(hypot(x-a,y-b)<w*.72 for a,b,w in occupied):
        continue
    if sin(x/37+y/51)+cos(y/34-x/57)<-.1:
        continue
    tree(x,y,rng.uniform(.52,1.25))

yards=run_path(str(HERE/"hillside_courts.py"))
courts=yards["select_courts"](plots,patch,road_distance)
retired_lamps=[]
for tx,ty,z,angle in lamp_sites:
    occupied_by=[]
    for p in plots:
        u,v=yards["local"](p,tx,ty)
        if abs(u)<p["width"]/2+.40 and abs(v)<p["depth"]/2+.40 and z+4.88>p["height"] and z<p["roof"]:
            occupied_by.append(p["plot_id"])
    if occupied_by:
        retired_lamps.append({"east_north":[tx,ty],"plots":occupied_by})
        continue
    post(street,tx,ty,z,z+4.8,.07,dark)
    frame=local_frame(tx,ty,angle)
    box(street,frame,-.13,-.39,z+4.66,.17,.39,z+4.88,dark)
    box(street,frame,-.09,-.33,z+4.62,.13,.30,z+4.66,white)
rail_return = run_path(str(HERE/"rail_return.py"))["fit"](HERE.parent/"district_patrol/city_and_patrol.blend",
                                                        next(p for p in plots if p["plot_id"]==4))
court_mats=dict(room_finish,flags=stone,wallstone=rock,brick=brick,
               cloth=material("Woven household cotton",(.36,.30,.26),"fabric_pattern_07_col_1_2k.jpg"),linen=cream_metal)
for key,color in (("oat",(.38,.34,.26)),("denim",(.115,.15,.17)),("sage",(.24,.30,.23))):
    court_mats[key]=material("Washed cotton "+key,color,"fabric_pattern_07_col_1_2k.jpg",relief="weave")
court_mats.update({key:facing[key] for key in ("paint","floors")})
for p in courts:
    yards["terrace_ground"](p,xx,yy,heights)
for p in plots:
    frame=local_frame(*p["east_north"],p["bearing"])
    pocket=Geometry("COL_Outer500_Court_%02d"%p["plot_id"]) if p.get("court") else solid
    fixtures=Geometry("Outer500_CourtDetails_%02d"%p["plot_id"]) if p.get("court") else street
    def yard_box(x0,y0,z0,x1,y1,z1,mat,physical=True):
        box(pocket if physical else fixtures,frame,x0,y0,z0,x1,y1,z1,mat)
    def yard_face(verts,mat,uvs=None):
        batch=floor_batches[p["plot_id"]] if mat in facing["floors"] else fixtures
        batch.face([frame(*point) for point in verts],mat,uvs)
    def plot_ground(u,v):
        return height(*frame(u,v,0)[:2])
    if p.get("court"):
        yards["build_court"](p,yard_box,yard_face,plot_ground,court_mats)
        pocket.finish()
        fixtures.finish()
    else:
        p["back_stair_m"]=ground_floors["apron"](p,yard_box,plot_ground,stone,p["depth"]/2,1)
paths=yards["connect_lanes"](plots,segments,patch,road_distance,mx,my,rgba)
save_surface_mask()
if "--surface-mask-only" in sys.argv:
    raise SystemExit(0)
lookup={a:i for i,a in enumerate(axis)}
for batch in chunks.values():
    batch.vertices=[(x,y,float(heights[lookup[x],lookup[y]])) for x,y,_ in batch.vertices]
    batch.finish()
for p in courts:
    def outside_court(tree):
        x,y,_=tree["east_north_up"]
        u,v=yards["local"](p,x,y)
        return abs(u-p["court"]["center_u"])>p["court"]["half_width"]+1.0 or not p["depth"]/2-.5<v<p["depth"]/2+13.6
    tree_sites=list(filter(outside_court,tree_sites))

# Surveyed rectangle has a physical boundary. Landward routes turn back
# inside the boundary. Waterfront land cuts use the licensed river polygon.
for side in range(4):
    boundary = [(t,-250) if side==0 else (250,t) if side==1 else
                (-t,250) if side==2 else (-250,-t) for t in range(-250,251,2)]
    for a,b in zip(boundary,boundary[1:]):
        if not inland(*a) or not inland(*b):
            continue
        za,zb=height(*a),height(*b)
        solid.face([(a[0],a[1],za-.50),(b[0],b[1],zb-.50),
                    (b[0],b[1],zb+.86),(a[0],a[1],za+.86)],rock)
        prior = [(a[0],a[1],za-.03),(b[0],b[1],zb-.03)]
        for dist in (8,18,37,65):
            next_row=[]
            for p,z in ((a,za),(b,zb)):
                # Radial displacement also seals each corner of the collar.
                fx,fy=p[0]*(1+dist/250),p[1]*(1+dist/250)
                ty=z-2-dist*.19
                if not inland(fx,fy):
                    ty=min(ty,water_z-.6)
                next_row.append((fx,fy,ty))
            skirt.face([prior[1],prior[0],next_row[0],next_row[1]],soil)
            prior=next_row

# Ground-level approach under the original bridge, away from the bridge rail.
# Tap into the asphalt at its southern edge and fade onto the new south lane.
apron = Geometry("COL_Outer500_South_underpass_apron")
last = None
for index in range(37):
    y=-96.0-index*.5
    length=-y-96
    x=16+max(0,length-10)*.055
    if length<=3:
        build_height=7.129-length*.13
    else:
        build_height=6.739-(length-3)*.105
    pitch=smooth((length-7)/11)
    top=build_height*(1-pitch)+(height(x,y)-.018)*pitch
    row=[(x+d,y,top if abs(d)<=1.95 else min(top-.04,height(x+d,y))) for d in (-3.2,-1.95,1.95,3.2)]
    if last:
        for column in range(3):
            apron.face([row[column],row[column+1],last[column+1],last[column]],asphalt if column==1 else rock)
    last=row
apron.finish()

# Retaining faces flank the steeper pedestrian riverside descents.
for pts in [design["promenade"], design["ridge"]]:
    for a,b in zip(pts,pts[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=hypot(dx,dy)
        ox,oy=-dy/length*6.6,dx/length*6.6
        for k in range(int(length/2)):
            t,v=k*2/length,(k+1)*2/length
            p=(a[0]+dx*t+ox,a[1]+dy*t+oy)
            q=(a[0]+dx*v+ox,a[1]+dy*v+oy)
            if max(abs(p[0]),abs(p[1]))<111 or not (patch(*p) and patch(*q)):
                continue
            zp,zq=height(*p),height(*q)
            solid.face([(p[0],p[1],zp-.8),(q[0],q[1],zq-.8),
                        (q[0],q[1],zq+.55),(p[0],p[1],zp+.55)],rock)

for key in (49182408,1189963598,176034707,830761786):
    for a,b in zip(mapped[key],mapped[key][1:]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=hypot(dx,dy)
        count=max(1,int(length))
        for n in range(count):
            t,v=n/count,(n+1)/count
            p=(a[0]+dx*t,a[1]+dy*t)
            q=(a[0]+dx*v,a[1]+dy*v)
            if max(map(abs,p))<100.25 or max(map(abs,q))<100.25 or not (patch(*p) and patch(*q)):
                continue
            if n%7>=3:
                continue
            band(verges,p,q,height(*p)+.025,height(*q)+.025,.12,white)

run_path(str(HERE / "planting.py"))["place_trees"](ASSETS, tree_sites, materials, material)
kit=GAME.parent/"chongqing_blender_v05/scanned_assets/prepared_assets.blend"
household=run_path(str(HERE/"household.py"))["place"](kit,plots,yards["world"],ASSETS/"courtyard_r24/courtyard.glb")
ac_palette={"offwhite":cream_metal,"painted_metal":green,"aluminium":metal,"dark":dark,
            "frame":dark,"rust":rust,"paper":cream_metal}
run_path(str(HERE/"condenser_instances.py"))["place"](GAME.parent/"chongqing_blender_v05",plots,
    Geometry,box,local_frame,front_tools["tube"],ac_palette)
contact=Geometry("COLH_Outer500_Household_contact")
footprints={"potted_plant_02":(.17,.17,.29),"plastic_crate_01":(.146,.20,.26),
            "Court14_BackBasket_and_greens":(.17,.15,.43),
            "chinese_armchair":(.36,.30,.44),"plastic_monobloc_chair_01":(.25,.24,.42),"chinese_tea_table":(.38,.38,.499)}
for item in household:
    x,y,z=item["origin"]
    w,d,h=[t*item["scale"] for t in footprints[item["asset"]]]
    box(contact,local_frame(x,y,item["yaw"]),-w,-d,z,w,d,z+h,dark)
contact.finish()
for batch in (blocks,facades,street,solid,verges,skirt):
    batch.finish()
for batch in floor_batches.values():
    batch.finish()
bpy.context.view_layer.update()
contact_bake=run_path(str(HERE/"interior_occlusion.py"))["bake"]([materials[i] for i in facing["floors"]])
bpy.context.scene["scope"] = "500 m local east/north, R24 build 25b centre; see README"
bpy.context.scene["source_license"] = "ODbL-1.0, © OpenStreetMap contributors"
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "outer_district.blend"),compress=True)
bpy.ops.export_scene.gltf(filepath=str(OUT / "outer_district.glb"),export_format="GLB",
                          export_yup=True,export_cameras=False,export_lights=False,export_vertex_color="ACTIVE")
old_meshes=json.loads((HERE.parents[1] / "scene_r21/district_rays.json").read_text(encoding="utf-8-sig"))["meshes"]
owned=plots+[dict(p,east_north=yards["world"](p,p["court"]["center_u"],p["depth"]/2+6.4),
                 width=p["court"]["half_width"]*2,depth=12.8) for p in courts]
prefixes, roof_cuts = run_path(str(HERE/"context_owners.py"))["conflicting_context"](owned,old_meshes,legacy_roofs,mapped_buildings)
(OUT / "layout.json").write_text(json.dumps({
    "bounds_east_north_m":[-250,-250,250,250],
    "projection_origin_wgs84":[osm["center_lon"],osm["center_lat"]],
    "baseline_bounds_east_north_m":[-100,-100,100,100],
    "osm_road_ids":mapped_ids,"river_relation":river["river_relation"],
    "attribution":"© OpenStreetMap contributors, ODbL-1.0",
    "inferred_alignments":design,"registered_ties":ties,"destinations":destinations,
    "osm_building_ids":mapped_buildings,"plots":plots,"lanes":paths,"retired_context_prefixes":prefixes,"retired_roof_positions":roof_cuts,
    "building_count":len(plots)+len(mapped_buildings),"flyover_reserves":flyover_reserves,"household":household,"collidable_surface_tiles":len(chunks),"planting":tree_sites,
    "floor_contact_bake":contact_bake,"interior_rail_return":rail_return,"lamps_in_buildings":retired_lamps,
},ensure_ascii=False,indent=2)+"\n")
