"""Join the registered road levels and rebuild their visible east-side street edges."""
from collections import Counter
import json
from math import ceil, cos, pi, sin
from pathlib import Path
import runpy
import struct
import sys
from tempfile import TemporaryDirectory

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(SCENE/"district_refresh/street_groups"), str(SCENE/"district_500")]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, read
from retire_plots import fingerprint, remove_faces
from riverside import bounds, make_strip, material, terrain_faces

BASES = ("1256840000", "1324001438", "1256839997")
GRADE = {
    "1256840000": (-108., -51.1443, -6.8),
    "1324001438": (-109., -40.1927, -8.65),
    "1256839997": (2., 55.8809, -6.0),
}
LOW = ("1324001436", "1375242613")


def lerp(a, b, t):
    return a + (b-a)*t


def clamp(t):
    return max(0., min(1., t))


def grade(way, east):
    a,b,drop = GRADE[way]
    t = clamp((east-a)/(b-a))
    return drop * t*t*(3.-2.*t)


def samples(points, step=2.25):
    rows = [Vector(points[0])]
    for a,b in zip(points,points[1:]):
        a,b = Vector(a),Vector(b)
        count = max(1,ceil((b-a).length/step))
        rows.extend(a.lerp(b,j/count) for j in range(1,count+1))
    distance = 0.
    output = []
    for i,p in enumerate(rows):
        if i:
            distance += (p-rows[i-1]).length
        tangent = (rows[min(i+1,len(rows)-1)]-rows[max(i-1,0)]).normalized()
        side = Vector((-tangent.y,tangent.x))
        output.append((p,tangent,side,distance))
    return output


def glb_materials(path):
    with path.open('rb') as file:
        magic,version,_,size,tag = struct.unpack("<4sIII4s",file.read(20))
        assert (magic,version,tag)==(b"glTF",2,b"JSON")
        data = json.loads(file.read(size))
    return {node["name"]:{data["materials"][p["material"]]["name"]
            for p in data["meshes"][node["mesh"]]["primitives"]}
            for node in data["nodes"] if "mesh" in node}


def local_copy(source):
    name = source.name
    assert source.library and source.type=="MESH",name
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    bpy.data.objects.remove(source,do_unlink=True)
    obj.name = name
    assert obj.name==name
    return obj


def borrow_slots(objects, parent_materials):
    borrowed = {}
    placeholders = {}
    for obj in objects:
        donor = parent_materials[obj.name]
        names = {}
        for i,mat in enumerate(obj.data.materials):
            if mat.name not in donor:
                assert mat.library is None,(obj.name,mat.name)
                continue
            name = mat.name
            if name not in placeholders:
                label = "CQEastParentSlot%03d" % len(placeholders)
                material = bpy.data.materials.new(label)
                material.use_nodes = True
                placeholders[name] = material
            material = placeholders[name]
            obj.data.materials[i] = material
            names[material.name] = name
        borrowed[obj.name] = names
    return borrowed


def old_mesh_edits(scene, faces, bridge):
    edits = []
    for label,wanted in faces.items():
        mesh = local_copy(scene.objects[label])
        expected = Counter(wanted)
        remove = [f.index for f in mesh.data.polygons if fingerprint(mesh,f) in expected]
        assert Counter(fingerprint(mesh,mesh.data.polygons[k]) for k in remove)==expected,label
        remove_faces(mesh,remove)
        edits.append(mesh)
    for way in BASES:
        mesh = local_copy(scene.objects["COL_Raijiapo_Ramp_"+way])
        for point in mesh.data.vertices:
            point.co.z += grade(way,point.co.x)
        mesh.data.update()
        # The inherited sweeps face inward at the top. Turn the running surface up.
        turned = 0
        for face in mesh.data.polygons:
            finish = mesh.data.materials[face.material_index].name
            if face.normal.z<-.75 and finish in ("Raijiapo retained asphalt surface","Raijiapo cream lining paint"):
                face.flip()
                turned += 1
        assert turned>0,way
        mesh.data.update()
        edits.append(mesh)
    columns = local_copy(scene.objects["COL_Raijiapo_RampRoundColumns"])
    footings = [(Vector((e,n)),base,roof,grade(way,e)) for way in BASES
                for e,n,base,roof,kind in bridge["motor_ramp_footings"][way] if grade(way,e)<-.01]
    for vertex in columns.data.vertices:
        for p,base,roof,shift in footings:
            if (vertex.co.xy-p).length<1.02 and base-.7<vertex.co.z<=roof+.09:
                vertex.co.z += shift*clamp((vertex.co.z-base)/(roof-base))
                break
    columns.data.update()
    edits.append(columns)
    return edits


def garage_return(scene, stone, shadow, rail, ground):
    original = local_copy(scene.objects["COL_Raijiapo_GaragePublicEnvelope"])
    p = Vector((-38.6,-152.7))
    along_front = (p-Vector((-41.6,-158.15))).normalized()
    inward = Vector((-along_front.y,along_front.x))
    obsolete = []
    for face in original.data.polygons:
        vertices = [original.data.vertices[i].co for i in face.vertices]
        u = [(v.xy-p).dot(along_front) for v in vertices]
        direction = [(v.xy-p).dot(inward) for v in vertices]
        if max(map(abs,u))<.22 and min(direction)>.028 and max(direction)>12.0 and max(v.z for v in vertices)>10:
            obsolete.append(face.index)
    assert len(obsolete)==5,obsolete
    remove_faces(original,obsolete)
    upper = 11.06+.039*(p.x+103.)
    levels = [upper+x for x in (-10.3,-7.74,-5.08,-2.46,0.)]
    wall = Mesh("COL_EastGarage_ReturnFrame")
    detail = Mesh("EastGarage_RailsAndRecess")
    def rect(a,b,c,d,h):
        return [(*(p+u*along_front+v*inward),h) for u,v in ((a,c),(b,c),(b,d),(a,d))]
    def bar(obj,a,b,c,d,z0,z1,mat):
        obj.solid(rect(a,b,c,d,z0),rect(a,b,c,d,z1),mat)
    for v in (.29,3.29,6.47,9.61,12.78):
        foot = ground(p+v*inward)-.26
        bar(wall,-.29,.31,v-.22,v+.22,foot,upper+.08,stone)
    for level in levels:
        bar(wall,-.42,.29,.18,13.05,level-.155,level+.28,stone)
        if level<upper-.7:
            bar(detail,.08,.13,.45,12.65,level+.61,level+.658,rail)
            bar(detail,.08,.13,.45,12.65,level+.93,level+.98,rail)
            bar(detail,-1.50,-1.43,.45,12.61,level+.28,level+1.98,shadow)
    return original,[wall.save(),detail.save()],len(obsolete)


def adjacent_frontage(points, stone, recess, rail, ground):
    """Model the observed two faces beside the public forecourt at plot 68."""
    wall = Mesh("COL_EastGarage_StreetFrontage68")
    screens = Mesh("EastGarage_StreetFrontageLouvers68")
    for index, (a, b) in enumerate(zip(points, points[1:])):
        a, b = Vector(a), Vector(b)
        tangent = (b-a).normalized()
        inward = Vector((-tangent.y,tangent.x))
        length = (b-a).length
        foundation = min(ground(a.lerp(b,i/6)) for i in range(7))-.50
        soffit = 2.33

        def bar(mesh, s0, s1, d0, d1, z0, z1, material):
            points = [a+s*tangent+d*inward for s,d in ((s0,d0),(s1,d0),(s1,d1),(s0,d1))]
            mesh.solid([(*p,z0) for p in points],[(*p,z1) for p in points],material)

        bar(wall,0,length,.04,1.75,foundation,soffit,stone)
        for level in range(4):
            z = soffit+level*2.32
            bar(wall,0,length,.04,1.75,z,z+.48,stone)
            bar(wall,0,length,1.35,1.75,z+.48,z+2.32,recess)
            for row in range(6):
                blade = z+.72+row*.195
                bar(screens,.12,length-.12,.45,.50,blade,blade+.047,rail)
        roof = soffit+4*2.32
        bar(wall,0,length,.02,1.83,roof-.12,roof+.53,stone)
        bays = max(1,round(length/3.12))
        for bay in range(bays+1):
            s = bay*length/bays
            bar(wall,max(0,s-.245),min(length,s+.245),-.24,.43,foundation,
                roof+(.69 if index==0 else .63),stone)
    return [wall.save(),screens.save()]


def z_at_old(bridge, way, point):
    rows=bridge["modeled_vehicle_ramps"][way]
    hit=min(rows,key=lambda q:(Vector(q["east_north"])-Vector(point)).length_squared)
    return hit["road_game_m"]+grade(way,point[0])


def paint_polygon(mesh, row, width, depth, offsets, finish):
    p,t,l,dist,z = row
    mesh.face([(*(p+t*a+l*b),z+.023+depth*a) for a,b in offsets],finish)


def make_road(name, points, elevation, half_width, finish, fascia, pale, red=None, warm=None, split=False, arrow_dir=1):
    """Road and paint share one graded section, with no floating road markings."""
    guide=samples(points)
    rows=[(*row,elevation(row,guide[-1][3])) for row in guide]
    shape=Mesh("COL_EastRoad_"+name)
    stripes=Mesh("EastRoad_Lines_"+name)
    for j,(a,b) in enumerate(zip(rows,rows[1:])):
        def coords(row):
            p,t,side,s,z=row
            w=half_width(s,guide[-1][3]) if callable(half_width) else half_width
            return [(*(p-side*w),z),(*(p+side*w),z)]
        a0,a1=coords(a)
        b0,b1=coords(b)
        coating = red[0] if red and red[1]<=.5*(a[3]+b[3])<=red[2] else finish
        shape.face([a0,b0,b1,a1],coating)
        va0,va1,vb0,vb1=[(*p[:2],p[2]-.54) for p in (a0,a1,b0,b1)]
        shape.face([a0,va0,vb0,b0],fascia)
        shape.face([a1,b1,vb1,va1],fascia)
        shape.face([va0,va1,vb1,vb0],fascia)
        if j==0:
            shape.face([a0,a1,va1,va0],fascia)
        if j==len(rows)-2:
            shape.face([b0,vb0,vb1,b1],fascia)
        for fraction in (-.89,.89):
            ac=Vector(a0).lerp(Vector(a1),(fraction+1.)*.5)
            bc=Vector(b0).lerp(Vector(b1),(fraction+1.)*.5)
            stripes.face([ac+Vector((*(a[2]*-.042),.016)),bc+Vector((*(b[2]*-.042),.016)),
                          bc+Vector((*(b[2]*.042),.016)),ac+Vector((*(a[2]*.042),.016))],pale)
        if j%3==1 and not callable(half_width) and half_width>=2.34:
            paint_polygon(stripes,a,0.,(b[4]-a[4])/(b[3]-a[3]),
                          ((0,-.056),(1.66,-.056),(1.66,.056),(0,.056)),pale)
        if red and j%7==3 and red[1]<a[3]<red[2]:
            arrow = ((-1.60,-.115),(.35,-.115),(.35,-.445),(1.30,0),(.35,.445),(.35,.115),(-1.60,.115))
            paint_polygon(stripes,a,0.,(b[4]-a[4])/(b[3]-a[3]),
                          [(arrow_dir*x,arrow_dir*y) for x,y in arrow],pale)
        if split and 12.<a[3]<27. and j%2==0:
            paint_polygon(stripes,a,0.,(b[4]-a[4])/(b[3]-a[3]),
                          ((0,.65),(.10,.65),(1.38,1.48),(1.28,1.48)),warm)
    return [shape.save(),stripes.save()], [(list(r[0]),r[3],r[4]) for r in rows]


def columns_for(name, rows, ground, concrete, start=5):
    caps=Mesh("COL_EastRoadPiers_"+name)
    kept=[]
    for p,d,z in rows:
        if d<start or d>rows[-1][1]-3. or (kept and d<kept[-1]+9.):
            continue
        foot=ground(p)
        soffit=z-.534
        if soffit-foot<.85:
            continue
        kept.append(d)
        def ring(up, radius):
            return [(p[0]+radius*cos(i*pi/12),p[1]+radius*sin(i*pi/12),up) for i in range(24)]
        caps.solid(ring(foot-.22,.55),ring(soffit-.23,.49),concrete)
        caps.solid(ring(soffit-.23,.49),ring(soffit+.04,.72),concrete)
    return [caps.save()] if kept else []


def portal(way, tunnel, axes, bridge, ground, concrete, asphalt, pale, shade):
    start=axes[tunnel][0] if way=="1324001438" else axes[tunnel][-1]
    toward=axes[tunnel][1] if way=="1324001438" else axes[tunnel][-2]
    p=Vector(start)
    t=(Vector(toward)-p).normalized()
    l=Vector((-t.y,t.x))
    z=z_at_old(bridge,way,start)+.012
    points=[list(p-t*.21),list(p+t*12.7)]
    pieces,rows=make_road("PortalApproach_"+tunnel,points,lambda row,s:z,2.33,asphalt,concrete,pale)
    facing=Mesh("COL_EastPortal_Arch_"+tunnel)
    dark=Mesh("EastPortal_Recess_"+tunnel)
    u0,u1=7.15,12.7
    radius=2.09
    spring=z+2.29
    crown=z+4.39
    def xy(u,v,h):
        return (*(p+t*u+l*v),h)
    ground_z=min(ground(p+t*u0+l*v) for v in (-4.16,4.16))
    for a,b in ((-4.17,-radius),(radius,4.17)):
        facing.solid([xy(u,v,ground_z-.35) for u,v in ((u0,a),(u1,a),(u1,b),(u0,b))],
                     [xy(u,v,crown+.69) for u,v in ((u0,a),(u1,a),(u1,b),(u0,b))],concrete)
    for j in range(18):
        aa,bb=[pi*index/18 for index in (j,j+1)]
        ar,br=radius*cos(aa),radius*cos(bb)
        ah,bh=spring+radius*sin(aa),spring+radius*sin(bb)
        for u in (u0,u1):
            facing.face([xy(u,ar,ah),xy(u,br,bh),xy(u,br,crown+.69),xy(u,ar,crown+.69)],concrete)
        facing.face([xy(u0,ar,ah),xy(u1,ar,ah),xy(u1,br,bh),xy(u0,br,bh)],concrete)
        facing.face([xy(u0,ar,crown+.69),xy(u1,ar,crown+.69),xy(u1,br,crown+.69),xy(u0,br,crown+.69)],concrete)
    dark.face([xy(u1-.023,-radius,z-.04),xy(u1-.023,radius,z-.04),xy(u1-.023,radius,crown),
              xy(u1-.023,-radius,crown)],shade)
    return pieces+[facing.save(),dark.save()],rows


def ground_asset(kind, points, width, palette, paint, lift, tiles):
    walk=make_strip({"id":kind,"points":points,"width_m":width,"finish":0,"raise_m":lift},
                    tiles,[palette,palette,paint])
    walk.name=kind
    return walk


def ground_kerb(name, points, offset, ground, finish):
    mesh = Mesh("COL_EastRoad_Kerb_"+name)
    rows = []
    for p,t,l,s in samples(points,2.1):
        p = p+l*offset
        z = ground(p)
        row = [(*(p+l*u),z+h) for u,h in ((-.105,.078),(.105,.188),(.105,-.13),(-.105,-.13))]
        rows.append(row)
    mesh.face(rows[0],finish)
    for a,b in zip(rows,rows[1:]):
        for i in range(4):
            j=(i+1)%4
            mesh.face([a[i],b[i],b[j],a[j]],finish)
    mesh.face(rows[-1][::-1],finish)
    return mesh.save()


def ground_strokes(name, points, ground_faces, project, white):
    mesh=Mesh("EastRoad_GroundPaint_"+name)
    rows=samples(points,2.75)
    rings=[]
    for i,(p,t,l,s) in enumerate(rows[2:-2],2):
        if i%3!=0:
            continue
        rings.append([list(p+a*t+b*l) for a,b in ((-.54,-.071),(1.18,-.071),(1.18,.071),(-.54,.071))])
    for ring in rings:
        area=project["project"](mesh,project["triangle_parts"](ring),ground_faces,[],white,lift=.075)
        assert area>.09,(name,ring,area)
    return mesh.save()


def build(temp):
    assert Path(bpy.data.filepath).name in ("city_and_outer.before_east.local.blend","city_and_outer.local.blend")
    c=read(HERE/"field-controls.json")
    retired=read(HERE/"retired-faces.json")
    bridge=read(ASSETS/"bridge-park.json")
    scene=bpy.context.scene
    axes={id:item["east_north"] for id,item in c["osm"]["ways"].items()}
    prior=runpy.run_path(str(HERE.parent/"plots_63_66/build.py"),run_name="road_material_library")
    paint_path=runpy.run_path(str(HERE.parent/"park_edge_finish/build.py"),run_name="park_texture_library")
    clip=runpy.run_path(str(HERE.parent/"park_plot59/build.py"),run_name="terrain_projection_library")
    stencil=paint_path["png"]
    colors=paint_path["finishes"](temp)
    tint=prior["tinted_material"]
    asphalt=tint("East bend worn fine asphalt","asphalt_02_diff_1k.jpg",(65,68,67),temp,stencil)
    red=tint("East bend red vehicle wearing course","asphalt_02_diff_1k.jpg",(160,74,57),temp,stencil)
    white=tint("East bend weathered white direction paint","asphalt_02_diff_1k.jpg",(218,220,213),temp,stencil)
    yellow=tint("East bend ochre merge hatching","asphalt_02_diff_1k.jpg",(208,169,95),temp,stencil)
    dark=tint("East bend tunnel deep recess","asphalt_02_diff_1k.jpg",(28,33,33),temp,stencil)
    metal=tint("East bend return grille galvanized steel","asphalt_02_diff_1k.jpg",(125,133,128),temp,stencil)
    concrete=material("East bend rubbed pale concrete",(.78,.75,.70),"concrete_wall_006_diff_2k.jpg")
    shuttered=material("East bend shaded parking interior",(.44,.45,.43),"stone_wall_05_diff_2k.jpg")
    original=terrain()
    tiles=list(terrain_faces())

    def ground(p):
        point,_,_,_=original.ray_cast(Vector((*p,38)),Vector((0,0,-1)),65.)
        assert point is not None,list(p)
        return point.z

    parent=glb_materials(ASSETS/"bridge-park.glb")
    parent.update(glb_materials(ASSETS/"changbin-bend-and-edge.glb"))
    replacements=old_mesh_edits(scene,retired["faces"],bridge)
    garage,extra,cap_faces=garage_return(scene,concrete,shuttered,metal,ground)
    replacements.append(garage)
    pieces=list(extra)
    profiles={}
    for way,tunnel in (("1256840000","1256840005"),("1324001438","1256840006")):
        new,rows=portal(way,tunnel,axes,bridge,ground,concrete,asphalt,white,dark)
        pieces.extend(new)
        profiles[tunnel]=rows

    for way,old in zip(LOW,("1256840000","1324001438")):
        coords=axes[way] if way=="1324001436" else axes[way][::-1]
        endpoint=prior["centre_at"](coords,110)
        shortened=[p for p in coords if p[0]<110]+[list(endpoint)]
        anchor=z_at_old(bridge,old,shortened[0])
        def low_height(row,total,anchor=anchor):
            p,t,l,s=row
            land=ground(p)
            high=anchor-.144*s
            ease=clamp((total-s)/13.)
            return max(land+.044,lerp(land+.105,max(land+.56,high),ease))
        new,rows=make_road(way,shortened,low_height,2.10 if way=="1324001436" else 1.98,
                           asphalt,concrete,white,(red,46.,148.) if way=="1324001436" else None,yellow,way=="1375242613")
        pieces.extend(new+columns_for(way,rows,ground,concrete))
        profiles[way]=rows

    # The east outer ramp follows its registered approach to a land-supported end.
    for way,following,start_height,half in (
        ("1256840008",[],z_at_old(bridge,"1256839997",axes["1256840008"][0]),3.14),
        ("1375242615",axes["1375242616"][1:3],z_at_old(bridge,"1256839997",axes["1375242615"][0]),2.29),
        ("1375242617",[[30.46,-102.73]],15.82,2.36),
    ):
        coords=(axes[way][::-1] if way=="1375242617" else axes[way])+following
        if way=="1256840008":
            coords=coords[:4]+[list(prior["centre_at"](coords,76.2))]
        def approach(row,total,initial=start_height,way=way):
            p,t,l,s=row
            land=ground(p)
            fade=clamp((total-s)/max(14.,total*.70))
            platform=initial-.025*s
            return lerp(land+.06,platform,fade)
        def width(s,total,way=way,half=half):
            if way!="1375242615":
                return half
            return lerp(.115,half,clamp(s/11.5))
        new,rows=make_road(way,coords,approach,width if way=="1375242615" else half,asphalt,concrete,
                           white,(red,36,84) if way=="1375242617" else None,yellow,
                           way=="1375242615",arrow_dir=-1 if way=="1375242617" else 1)
        # The existing carriageway supports the shared fork until this ramp separates.
        first_pier = 28 if way=="1375242615" else 5
        pieces.extend(new+columns_for(way,rows,ground,concrete,start=first_pier))
        profiles[way]=rows

    for id,start,end,width in (("59146737",-16.,111.,9.10),("1256859184",-38.,108.,7.65)):
        points=[list(p) for p in prior["points_on_axis"](axes[id],start,end)]
        pieces.append(ground_asset("EastRoad_Ground_"+id,points,width,asphalt,white,.052,tiles))
        pieces.append(ground_strokes(id,points,tiles,clip,white))
        if id=="59146737":
            pieces.append(ground_kerb(id,points[5:-4],-width*.5-.075,ground,colors["pale"]))
        else:
            pieces.append(ground_kerb(id,points[16:-7],width*.5+.075,ground,colors["pale"]))

    walk=c["landscape"]["walk"]
    pieces.append(ground_asset("COL_EastRoad_PublicWalk",prior["extended_walk"](walk),2.10,colors["stone"],colors["pale"],.064,tiles))
    e,n=c["landscape"]["island_center"]
    ring=[[e-2.0,n-.85],[e+1.75,n-1.14],[e+2.25,n+.72],[e-1.92,n+1.08]]
    inner=[list(Vector((e,n)).lerp(Vector(p),.81)) for p in ring]
    island=Mesh("EastRoad_PlantingSurface68")
    curb=Mesh("COL_EastRoad_TreeIslandKerb68")
    clip["project"](island,clip["triangle_parts"](inner),tiles,[],colors["grass"],lift=.077)
    for a,b,d,f in zip(ring,ring[1:]+ring[:1],inner,inner[1:]+inner[:1]):
        r=[a,b,f,d]
        curb.solid([(*p,ground(p)-.075) for p in r],[(*p,ground(p)+.185) for p in r],colors["pale"])
    pieces.extend([island.save(),curb.save()])
    pieces.extend(adjacent_frontage(c["landscape"]["adjacent_frontage"]["edge_enu"],
                                    concrete,shuttered,metal,ground))
    old_suffix={"COL_Changbin_InsideBend_1375242615","Changbin_InsideBend_ConcreteParapet",
                "Changbin_InsideBend_EdgePaint","Changbin_GroundRoad_59146737","Changbin_GroundRoad_1256859184",
                *("COL_Changbin_LowRamp_"+w for w in LOW),*("Changbin_LowRamp_Edge_"+w for w in LOW)}
    assert all(name in scene.objects for name in old_suffix)
    meta={"retired_plots":[67,68,69],"retired_objects":sorted(set(retired["retired_objects"])|old_suffix),
          "replacement_meshes":[obj.name for obj in replacements],"new_meshes":[obj.name for obj in pieces],
          "garage_removed_solid_faces":cap_faces,"road_sections_enu_m":profiles,
          "tree":{"name":"EastRoad_Tree68","donor":c["landscape"]["tree_source"],"enu":[e,n,ground((e,n))+.005]},
          "old_centres":{k:p["center"] for k,p in c["plots"].items()},
          "road_axis":axes["1256859184"],"walk":{"stations":walk,"start_ray_m":ground(walk[0])+1.25,
          "finish_z_m":ground(walk[-1])+.064}}
    kept=set(replacements+pieces)
    for obj in list(bpy.data.objects):
        if obj not in kept:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"raijiapo-east-bend.blend"),relative_remap=True,compress=True)
    meta["borrowed_materials"]=borrow_slots(replacements,parent)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/"raijiapo-east-bend.glb"),export_format="GLB",
                              export_cameras=False,export_lights=False)
    (ASSETS/"raijiapo-east-bend.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
    print("CQ_EAST_BUILD",len(pieces),len(replacements),len(meta["retired_objects"]),cap_faces)


if __name__=="__main__":
    with TemporaryDirectory() as temp:
        build(Path(temp))
