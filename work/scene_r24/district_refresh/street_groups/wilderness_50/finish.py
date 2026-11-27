"""Refinish the public-side walls and stone seats without changing the path."""
from math import ceil, cos, radians, sin, tau
from pathlib import Path
from random import Random
import json
import runpy
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(HERE.parent), str(SCENE / "district_500")]
from factory import Mesh, terrain
from refresh_geometry import read
from riverside import material

WALL = "COL_Renai50_LowRelicFragments"
COPING = "Renai50_WeatheredCoping"
SEATS = "COL_Renai50_ReusedStoneSeats"
STONE_HEIGHTS = (
    [.82,.93,.86,.75,.69,.79,.54],
    [.82,.66,.48], [.75,.65,.48], [.79,.47],
)


def simple(name, rgb):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1.)
    return mat


def stone(mesh, points, base, top, rng, finish):
    """Give the individual stones low chips, worn corners and a dressed face."""
    z = [base(p) for p in points]
    up = [top(p) for p in points]
    side_bottom = [(*p, b) for p,b in zip(points,z)]
    center = sum(points, Vector((0,0)))/len(points)
    middle = [(*p, h-rng.uniform(.025,.040)) for p,h in zip(points,up)]
    crown = [(*(p.lerp(center,rng.uniform(.035,.075))), h) for p,h in zip(points,up)]
    mesh.face(side_bottom[::-1],finish)
    for i in range(len(points)):
        j=(i+1)%len(points)
        mesh.face([side_bottom[i],side_bottom[j],middle[j],middle[i]],finish)
        mesh.face([middle[i],middle[j],crown[j],crown[i]],finish)
    for i in range(1,len(crown)-1):
        mesh.face([crown[0],crown[i],crown[i+1]],finish)


def rock_outline(a, b, span, rng):
    run = (b-a).normalized()
    normal=Vector((-run.y,run.x))
    length=(b-a).length
    bevel=min(.073,length*.21)
    d=span/2.
    spots=[(0,-d+bevel),(bevel,-d),(length-bevel,-d),(length,-d+bevel),
           (length,d-bevel),(length-bevel,d),(bevel,d),(0,d-bevel)]
    return [a+run*x+normal*(s+rng.uniform(-.018,.018)) for x,s in spots]


def ruins(walls, crowns, field, land, colors, backing, rng):
    controls=[]
    for group,(anchors,heights) in enumerate(zip(field["walls_en"],STONE_HEIGHTS)):
        path=list(map(Vector,anchors))
        # Keep the full-height core and close its turns, as in the previous build.
        core=[h-.075 for h in heights]
        backing(walls,path,field["ground_bvh"],.436,[-.15]*len(path),core,colors[0])
        for i,(a,b) in enumerate(zip(path,path[1:])):
            length=(b-a).length
            levels=heights[i:i+2]
            axis=(b-a).normalized()
            def h(p):
                return levels[0]+(levels[1]-levels[0])*min(1.,max(0.,(p-a).dot(axis)/length))
            for row,(low,high) in enumerate(((.025,.325),(.337,.656),(.667,.985))):
                offset=0.
                while offset<length-.035:
                    initial=[.84,.39,.63][(row+i+group)%3] if offset==0 else rng.uniform(.54,1.04)
                    size=min(length-offset,initial)
                    residue=length-offset-size
                    if residue<.24:
                        size+=residue
                    depth=rng.uniform(.487,.555)
                    p,q=a+axis*(offset+.012),a+axis*(offset+size-.013)
                    color=colors[1+rng.randrange(len(colors)-1)]
                    points=rock_outline(p,q,depth,rng)
                    stone(walls,points,lambda p:land(p)+low*h(p)-(.07 if row==0 else 0.),
                          lambda p:land(p)+high*h(p)+rng.uniform(-.018,.015),rng,color)
                    offset+=size
            for index in range(max(1,ceil(length/.87))):
                pieces=max(1,ceil(length/.87))
                low=length*index/pieces+(0. if index==0 else .012)
                high=length*(index+1)/pieces-(0. if index==pieces-1 else .012)
                points=rock_outline(a+axis*low,a+axis*high,rng.uniform(.54,.61),rng)
                stone(crowns,points,lambda p:land(p)+h(p)-.036,
                      lambda p:land(p)+h(p)+rng.uniform(.048,.093),rng,colors[2+rng.randrange(3)])
                controls.append([*a.lerp(b,(low+high)/(2*length))])


def seats(mesh, specs, land, colors, rng):
    measured=[]
    for i,(e,n,yaw) in enumerate(specs):
        start=Vector((e,n))
        forward=Vector((cos(radians(yaw)),sin(radians(yaw))))
        length=(1.58,1.32,1.80,1.22)[i]
        width=(.43,.41,.47,.38)[i]
        ring=rock_outline(start-forward*length*.5,start+forward*length*.5,width,rng)
        # Conform the lower stone edge to the supporting hillside and give the
        # block a sloping worn top, with the nearer corner especially rounded.
        height=max(land(p) for p in ring)+(.36,.33,.39,.31)[i]
        stone(mesh,ring,lambda p:land(p)-.055,
              lambda p:height+(p-start).dot(forward)*.037+rng.uniform(-.026,.015),rng,colors[2+i%3])
        measured.append([e,n,land(start)])
    return measured


def edge_plantings(mesh, points, land, random, colors):
    """Tuck coarse grass and broad leaves behind the existing wall and seats."""
    for i,(x,y,reach) in enumerate(points):
        center=Vector((x,y))
        for j in range(29):
            reach_here=reach*random.uniform(.08,1.)
            azimuth=random.random()*tau
            axis=Vector((cos(azimuth),sin(azimuth)))
            across=Vector((-axis.y,axis.x))
            root=center+axis*reach_here
            h=random.uniform(.075,.21) if i%3 else random.uniform(.12,.34)
            z0=land(root)-.011
            width=random.uniform(.017,.047)
            low=[(*(root-across*width),z0),(*(root+across*width),z0)]
            middle=root+axis*h*.30
            high=[(*(middle+across*width*.60),z0+h*.68),
                  (*(middle-across*width*.60),z0+h*.68)]
            tip=(*(root+axis*h*.59),z0+h)
            part=low+high
            color=colors[(j+i)%len(colors)]
            mesh.face(part,color)
            mesh.face(part[::-1],color)
            mesh.face([high[0],tip,high[1]],color)
            mesh.face([high[0],high[1],tip],color)


def main(out):
    source=runpy.run_path(str(HERE/"build.py"))
    field=read(HERE/"field.json")
    hill=terrain()
    land=lambda p:source["land"](hill,p)
    field["ground_bvh"]=hill
    rng=Random(734116600)
    shades=[(.64,.63,.57),(.78,.74,.65),(.76,.745,.686),(.85,.816,.72),(.69,.671,.62),(.72,.73,.647)]
    surfaces=["stone_wall_05_diff_2k.jpg","stone_wall_05_diff_2k.jpg",
              "concrete_floor_worn_001_diff_2k.jpg","concrete_floor_worn_001_diff_2k.jpg",
              "stone_wall_05_diff_2k.jpg","concrete_floor_worn_001_diff_2k.jpg"]
    colors=[material(f"Renai split stone shade {i}",rgb,surfaces[i])
            for i,rgb in enumerate(shades)]
    plants=[simple(f"Renai local verge leaf {i}",rgb) for i,rgb in enumerate(
        ((.075,.127,.044),(.119,.183,.066),(.172,.224,.079),(.24,.261,.088),(.152,.146,.067)))]
    old=bpy.context.scene.objects
    for name in (WALL,COPING,SEATS):
        bpy.data.objects.remove(old[name],do_unlink=True)
    wall,crown,seat,tufts=(Mesh(name) for name in (WALL,COPING,SEATS,"Renai50_WallAndSeatVerge"))
    ruins(wall,crown,field,land,colors,source["band_mesh"],rng)
    seat_contacts=seats(seat,field["seats_en"],land,colors,rng)
    spots=[(-220.72,82.05,.38),(-219.68,82.94,.36),(-218.2,81.50,.37),(-217.78,81.48,.41),
           (-216.44,80.47,.32),(-215.92,79.98,.38),(-214.42,76.25,.31),(-213.83,75.53,.28),
           (-212.64,74.29,.26),(-223.65,71.03,.27),(-221.22,73.92,.23),(-221.61,80.60,.43),
           (-216.70,84.28,.44),(-218.51,80.88,.30),(-217.06,79.55,.29),
           (-216.77,77.99,.24),(-214.90,75.70,.28),(-212.98,73.54,.34)]
    edge_plantings(tufts,spots,land,rng,plants)
    keep={mesh.save() for mesh in (wall,crown,seat,tufts)}
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"wilderness-50-finish.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(out/"wilderness-50-finish.glb"),
                              export_format="GLB",export_image_format="NONE",
                              export_cameras=False,export_lights=False)
    plan={"replacement_meshes":[WALL,COPING,SEATS],"retired_objects":[],
          "new_meshes":[tufts.name],"seat_contacts":seat_contacts,"planted_spots":spots,
          "surface_textures":{mat.name:f"res://assets/chongqing_district_{tex}" for mat,tex in zip(colors,surfaces)}}
    (out/"wilderness-50-finish.json").write_text(json.dumps(plan,indent=2)+"\n")
    print("CQ_RENAI50_PUBLIC_FINISH",len(wall.faces),len(crown.faces),len(tufts.faces))


if __name__=="__main__":
    main(Path(sys.argv[-1]).resolve())
