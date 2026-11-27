"""Check registered Baidu sky pixels against the editable district in Blender 4.3.2."""
from collections import Counter
from itertools import product
import json
from math import atan2, cos, degrees, hypot, radians, sin, tan
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
CONTROL = json.loads((HERE / "field-controls.json").read_bytes())
CAMERA = CONTROL["camera"]
RING = CONTROL["old_footprint_east_north"]
PIXELS = [tuple(row["pixel"]) for row in CONTROL["sky_samples"]]
scene = bpy.context.scene
graph = bpy.context.evaluated_depsgraph_get()


def cross(a, b):
    return a[0]*b[1]-a[1]*b[0]


def footprint_interval(eye, ray):
    distances = []
    for a,b in zip(RING,RING[1:]+RING[:1]):
        edge = (b[0]-a[0],b[1]-a[1])
        if abs(cross(ray,edge)) < 1e-7:
            continue
        delta = (a[0]-eye.x,a[1]-eye.y)
        t,u = cross(delta,edge)/cross(ray,edge),cross(delta,ray)/cross(ray,edge)
        if t>0 and -.00001<=u<=1.00001:
            distances.append(t)
    if len(distances)!=2:
        return {}
    a,b = sorted(distances)
    run = hypot(ray.x,ray.y)
    return {"near_far_horizontal_m":[a*run,b*run],"near_far_game_height_m":[eye.z+a*ray.z,eye.z+b*ray.z],
            "near_far_above_camera_street_m":[eye.z+a*ray.z-floor,eye.z+b*ray.z-floor]}


def sight(pixel, heading, pitch, angle):
    yaw,pitch = radians(heading),radians(pitch)
    center = Vector((sin(yaw)*cos(pitch),cos(yaw)*cos(pitch),sin(pitch)))
    right = Vector((cos(yaw),-sin(yaw),0))
    up = right.cross(center)
    width,height = CAMERA["frame_px"]
    focal = (height/2)/tan(radians(angle/2))
    x,y = pixel
    return (center+right*((x+.5-width/2)/focal)+up*((height/2-y-.5)/focal)).normalized()


def surface(eye, position, normal, index, obj):
    material = obj.data.materials[obj.data.polygons[index].material_index] if obj.data.materials else None
    alpha = None
    if material and material.use_nodes:
        shader = next((node for node in material.node_tree.nodes if node.type=="BSDF_PRINCIPLED"),None)
        if shader:
            color_alpha = shader.inputs["Alpha"]
            alpha = "texture" if color_alpha.is_linked else round(color_alpha.default_value,4)
    return {"object":obj.name,"game_enu":list(position),"normal":list(normal),
            "distance_from_eye_m":(position-eye).length,"material":material.name if material else None,
            "shader_alpha":alpha}


def cast(eye, ray):
    hit,position,normal,index,obj,_ = scene.ray_cast(graph,eye,ray,distance=330)
    return surface(eye,position,normal,index,obj) if hit else {}


def status(hit):
    if not hit:
        return "open"
    if hit["object"] in ("COL_Outer500_Frame_61","Outer500_Joinery_61","Outer500_InteriorFloor_61"):
        return "old_61"
    return "other:"+hit["object"]


frame = scene.objects.get("COL_Outer500_Frame_61")
frame = frame.evaluated_get(graph) if frame else None


def against_frame(eye, ray):
    if frame is None:
        return {}
    transform = frame.matrix_world
    local = transform.inverted()
    hit,point,normal,index = frame.ray_cast(local@eye,local.to_3x3()@ray,distance=70)
    if not hit:
        return {}
    return surface(eye,transform@point,transform.to_3x3()@normal,index,frame)


e,n = CAMERA["east_north_from_prior_registration_m"]
cursor = Vector((e,n,20))
for _ in range(16):
    ground,position,_,_,obj,_ = scene.ray_cast(graph,cursor,Vector((0,0,-1)),distance=45)
    assert ground, "Missing registered street support"
    if obj.name.startswith("COL_Outer500_Surface_"):
        floor = position.z
        break
    cursor = position-Vector((0,0,.014))
else:
    raise ValueError("Street datum not found")
eye = Vector((e,n,floor+CAMERA["device_height_m"]))

variables = (
    ("east_m",.90),("north_m",.90),("street_height_m",.75),
    ("heading_deg",2.),("pitch_deg",1.),("vertical_fov_deg",2.),
)
combined = list(product((-1,0,1),repeat=len(variables)))
results = []
for pixel in PIXELS:
    nominal = sight(pixel,CAMERA["heading_deg"],CAMERA["pitch_deg"],CAMERA["vertical_fov_deg"])
    hit = cast(eye,nominal)
    one_at_a_time = {}
    totals = Counter()
    opaque_frame = 0
    for signs in combined:
        de,dn,dh,dy,dp,df = [value*sign for (_,value),sign in zip(variables,signs)]
        shifted = eye+Vector((de,dn,dh))
        ray = sight(pixel,CAMERA["heading_deg"]+dy,CAMERA["pitch_deg"]+dp,CAMERA["vertical_fov_deg"]+df)
        result = cast(shifted,ray)
        direct = against_frame(shifted,ray)
        opaque_frame += bool(direct and direct["shader_alpha"] == 1.0)
        label = status(result)
        totals[label] += 1
        if sum(s!=0 for s in signs)==1:
            chosen = next(i for i,sign in enumerate(signs) if sign)
            key,value = variables[chosen]
            one_at_a_time.setdefault(key,{})[str(value*signs[chosen])] = result
    results.append({"pixel_xy":pixel,"unit_ray_east_north_up":list(nominal),
                    "azimuth_deg":degrees(atan2(nominal.x,nominal.y))%360,
                    "elevation_deg":degrees(atan2(nominal.z,hypot(nominal.x,nominal.y))),
                    "footprint_crossing":footprint_interval(eye,nominal),
                    "hit":hit,"direct_old_frame_hit":against_frame(eye,nominal),
                    "primary_class":status(hit),"joint_perturbation":dict(sorted(totals.items())),
                    "variants_hitting_opaque_old_frame_independently_of_leaves":opaque_frame,
                    "one_variable_at_a_time":one_at_a_time})

print("CQ_PARK61_RAYS",json.dumps({
    "blender":bpy.app.version_string,"street_game_height_m":floor,"camera_enu_m":list(eye),
    "camera_model":"rectilinear, 80 degree vertical field, top-left pixel center plus half",
    "variables_with_positive_amplitude":dict(variables),"joint_variants_per_pixel":len(combined),
    "rays":results,
}))
