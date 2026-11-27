"""Restore the open strip at plot 57 and repair the registered park wall seam."""
import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
SCENE=HERE.parents[2]
GROUPS=SCENE/"district_refresh/street_groups"
sys.path[:0]=[str(GROUPS),str(GROUPS/"guoco"),str(HERE.parent/"west_ramp"),str(SCENE/"district_500")]
from factory import Mesh, material, terrain
from interior_terrain import clip_polygon
from playground_grade import court
from refresh_geometry import ASSETS, latest_donors, load_current, read, strip_plots
from riverside import bounds, make_strip, terrain_faces

TILES=("COL_Outer500_Surface_01_01","COL_Outer500_Surface_02_01")
WALLS=("COL_WestPlayground_PerimeterSupport","COL_Outer500_WestCourt_Retaining")
CAP_WEST=Vector((-140.7300,-178.2785,-4.1415))
CAP_EAST=Vector((-140.3377,-178.3377,-4.1063))
PATH_END=[(-132.92,-183.14),(-129.33,-181.43),(-125.62,-179.84),(-121.90,-177.82)]
CROSS=[(-140.17,-183.70),(-137.83,-183.49),(-135.14,-183.22),*PATH_END]


def polygon_area(points):
    return (sum((a.cross(b) for a,b in zip(points,points[1:]+points[:1])),Vector())*.5).length


def remove_balanced_opening(obj, edges, finish):
    """Keep the native UVs and shape on every face outside the narrow passage."""
    retained=Mesh(obj.name+"_Abutment")
    removed=[]
    for face in obj.data.polygons:
        ring=[obj.matrix_world@obj.data.vertices[i].co for i in face.vertices]
        if abs(face.normal.z)>.35 or not any(-142.<p.x<-132.65 and -185.1<p.y<-181.5 for p in ring):
            continue
        inside=ring
        fragments=[]
        for edge in edges:
            inside,outside=clip_polygon(inside,edge)
            if len(outside)>=3 and polygon_area(outside)>1e-5:
                fragments.append(outside)
            if len(inside)<3:
                break
        if len(inside)<3 or polygon_area(inside)<1e-4:
            continue
        removed.append(face.index)
        for part in fragments:
            retained.face(part,finish)
    if not removed:
        return None,removed
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.faces[i] for i in removed],context='FACES_ONLY')
    bm.to_mesh(obj.data)
    bm.free()
    return (retained.save() if retained.faces else None),removed


def build():
    donors=latest_donors([
        ("west-ramp", HERE.parent/"west_ramp/west-ramp.blend"),
        ("guoco-frontages",GROUPS/"guoco/guoco-frontages.blend"),
        ("public-edges",GROUPS/"matix/public-edges.blend"),
        ("xingchen",GROUPS/"xingchen/xingchen.blend"),
        ("pavilion62",HERE.parent/"pavilion62/pavilion62.blend"),
        ("collectibles-market",GROUPS/"zhongxing/collectibles/collectibles-market.blend"),
    ])
    layout=read(ASSETS/"layout.json")
    replacements,retired,counts=strip_plots(read(HERE/"ownership.json"),(57,),layout,donors)
    reference_ground=terrain()
    tiles=[load_current(name,donors[name]) for name in TILES]
    old_wall=[load_current(name,donors[name]) for name in WALLS]
    ground=terrain()

    def land(point, surface=ground):
        hit,*_=surface.ray_cast(Vector((point.x,point.y,25)),Vector((0.,0.,-1.)))
        if hit is None:
            raise ValueError(f"No naturally supported garden point {list(point)}")
        return hit.z

    def rise(point):
        blend=min(1.,max(0.,(point.x+137.10)/4.23))
        if blend <= .001:
            return -5.83
        return -5.83*(1.-blend)+land(point,reference_ground)*blend

    flags=material("East park single-scale grey flags",(.67,.67,.61),"stone_floor_diff_2k.jpg")
    edge=material("East park weathered cut grey edge",(.72,.72,.67),"concrete_floor_worn_001_diff_2k.jpg")
    stone=material("East park course stone and capped ends",(.66,.65,.59),"stone_wall_05_diff_2k.jpg")
    topsoil=material("East park tree belt dry leaves and grass",(.49,.58,.35),"brown_mud_leaves_01_diff_2k.jpg")

    def middle(e):
        return -183.70+(e+141.90)*.068

    e0,e1=-141.90,-132.87
    half=1.40
    ring=[Vector((e0,middle(e0)-half)),Vector((e1,middle(e1)-half)),
          Vector((e1,middle(e1)+half)),Vector((e0,middle(e0)+half))]
    rise_patch=court.Patch("east_walk",ring,rise,0)
    surface,walls=court.Mesh(),court.Mesh()
    changed,area=court.build_terrain(tiles,[rise_patch],surface,walls,require_full_coverage=False)
    assert 6.0 < area["east_walk"] < 26.0,area
    parts=[surface.make("COL_Park57_EastWalkGrade",[flags,stone]),
           walls.make("COL_Park57_EastWalkFlank",[flags,stone])]
    replacements.extend(changed)

    trim=[lambda p:p.x-e0,lambda p:e1-p.x,
          lambda p:p.y-middle(p.x)+half,lambda p:middle(p.x)+half-p.y]
    cuts={}
    for original in old_wall:
        remainder,hits=remove_balanced_opening(original,trim,stone)
        if hits:
            replacements.append(original)
            cuts[original.name]=hits
        if remainder is not None:
            parts.append(remainder)
    assert cuts,cuts

    seam=Mesh("COL_Park57_NorthDeckWallSeal")
    a,b=CAP_WEST,CAP_EAST
    right=Vector((.011,.103,0.))
    base_a,base_b=Vector((a.x,a.y,-5.845)),Vector((b.x,b.y,-5.845))
    seam.solid([base_a,base_b,base_b+right,base_a+right],[a,b,b+right,a+right],stone)
    parts.append(seam.save())

    geo=list(terrain_faces())
    path_support=parts[0]
    points=[path_support.matrix_world@v.co for v in path_support.data.vertices]
    faces=[[points[i] for i in polygon.vertices] for polygon in path_support.data.polygons]
    geo.append((bounds(points),[(bounds(face),face) for face in faces]))
    for name,points,width,finish in (
        ("UpperPath",PATH_END,2.55,0),
        ("UpperGreenShoulder",[(-133.05,-186.2),(-129.36,-184.48),(-125.45,-182.87),(-120.04,-183.04)],2.08,1),
        ("RailWestGreenBelt",[(-130.18,-174.60),(-127.0,-173.36),(-123.3,-173.67),(-119.09,-174.45)],2.2,1),
    ):
        part=make_strip({"id":name,"points":points,"width_m":width,"finish":finish,"raise_m":.023},
                        geo,[flags,topsoil,edge])
        part.name="Park57_"+name
        parts.append(part)
    for i,(e,n,scale) in enumerate((
        (-132.5,-186.18,.46),(-129.6,-183.91,.83),(-126.48,-183.22,.70),
        (-122.74,-183.53,.83),(-119.73,-182.12,.48),(-126.55,-173.50,.86),
        (-121.62,-173.25,.57),(-117.77,-176.58,.63),
    ),1):
        plant=bpy.data.objects["Outer500_Plant_018" if i%3 else "Outer500_Plant_010"].copy()
        plant.name=f"Park57_GreenBelt_Plant_{i:02}"
        plant.location=(e,n,land(Vector((e,n)))-.045)
        plant.rotation_euler.z+=i*.68
        plant.scale*=scale
        bpy.context.scene.collection.objects.link(plant)
        parts.append(plant)
    west=read(ASSETS/"west-ramp.json")
    route=[*west["playground"]["street_access"]["route_east_north"][:6],
           [-156.0,-175.9],[-151.2,-176.6],[-147.4,-177.8],
           [-144.8,-181.4],[-141.55,-183.73],*CROSS]
    target=Vector(PATH_END[-1])
    manifest={"replaced_plot":57,"replacement_meshes":[obj.name for obj in replacements],
              "retired_objects":retired,"retired_source_faces":counts,"new_meshes":[obj.name for obj in parts],
              "route_east_north":route,"destination_y":land(target),"park_way":1499726225,
              "street_way":59146737,"grade_new_m2":area["east_walk"],
              "opening_footprint_east_north":[list(p) for p in ring],"old_wall_opening_faces":cuts,
              "seal_from_east_north_up":list(a),"seal_to_east_north_up":list(b),
              "defect_cameras":read(HERE/"field-controls.json")["defect_cameras"],
              "plot57_view":{"eye_east_north_up":[-136.15,-190.65,-4.06],
                             "target_east_north_up":[-121.98,-177.79,.22],"fov_deg":65},
              "approach_sections_east_north":[[e,middle(e)] for e in (-138.4,-137.65,-136.8,-135.85,-134.8,-133.6)]}
    keep=set(replacements+parts)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"park-plot57.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/"park-plot57.glb"),export_format="GLB",
                              export_cameras=False,export_lights=False)
    (ASSETS/"park-plot57.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print("CQ_PARK57_SOURCE",json.dumps(manifest))


build()
