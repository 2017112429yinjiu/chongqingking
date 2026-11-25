"""Bake short contact shadows on occupied floors from the saved geometry, in metres."""
from math import sin,cos,pi
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bpy


def bake(floor_mats):
    points=[];polys=[]
    for obj in bpy.context.scene.objects:
        if obj.type!="MESH" or not obj.name.startswith(("COL_Outer500_Frame_","COL_Outer500_Court_",
                "COL_Outer500_Building_envelopes","Outer500_CourtDetails_","Outer500_Street_furniture","Outer500_Household_")):continue
        offset=len(points);matrix=obj.matrix_world
        points.extend(matrix@v.co for v in obj.data.vertices)
        polys.extend(tuple(offset+j for j in poly.vertices) for poly in obj.data.polygons)
    tree=BVHTree.FromPolygons(points,polys)
    # Restrict the radius to nearby supports and furnishings; preserve broad daylight.
    directions=[Vector((cos(a*pi/4+phase),sin(a*pi/4+phase),rise)).normalized()
                for rise,phase in ((.38,.13),(1.25,.36)) for a in range(8)]
    for mat in floor_mats:
        graph=mat.node_tree;bs=graph.nodes.get("Principled BSDF");previous=bs.inputs["Base Color"].links[0].from_socket
        color=graph.nodes.new("ShaderNodeVertexColor");color.layer_name="Contact"
        mix=graph.nodes.new("ShaderNodeMixRGB");mix.blend_type="MULTIPLY";mix.inputs[0].default_value=1
        graph.links.new(previous,mix.inputs[1]);graph.links.new(color.outputs["Color"],mix.inputs[2])
        graph.links.new(mix.outputs[0],bs.inputs["Base Color"])
    total=0;low=1.0;dark=0
    for obj in bpy.context.scene.objects:
        if not obj.name.startswith("Outer500_InteriorFloor_"):continue
        mesh=obj.data
        colors=mesh.color_attributes.new(name="Contact",type="BYTE_COLOR",domain="POINT")
        mesh.color_attributes.active_color=colors
        cache={}
        for vertex in mesh.vertices:
            v=vertex.co; key=tuple(round(a,4) for a in v)
            if key not in cache:
                start=Vector((v.x,v.y,v.z+.027))
                occlusion=0.
                for direction in directions:
                    distance=tree.ray_cast(start,direction,1.15)[3]
                    if distance is not None:occlusion+=(1-distance/1.15)**1.25
                value=1-.80*occlusion/len(directions)
                cache[key]=value;low=min(low,value);dark+=int(value<.90);total+=1
            val=cache[key];colors.data[vertex.index].color=(val,val,val,1)
    print("OCCUPIED_FLOOR_CONTACT",total,dark,low,flush=True)
    return {"sample_positions":total,"below_90_percent":dark,"darkest_linear_multiplier":low,
            "rays_per_position":len(directions),"radius_m":1.15}
