"""Bake local ambient visibility from the actual shelves, neighbouring books and tables."""
from math import cos,sin,tau
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def bake():
    owners=[obj for obj in bpy.context.scene.objects if obj.name.startswith(("Court_Jinma_Books_","COL_Court_Jinma_Casework_"))]
    supports=[bpy.data.objects["COL_Court_Structure_jinma_classrooms"]]
    pts,faces=[],[]
    for obj in owners+supports:
        offset=len(pts)
        pts.extend(vertex.co.copy() for vertex in obj.data.vertices)
        faces.extend(tuple(offset+i for i in face.vertices) for face in obj.data.polygons)
    tree=BVHTree.FromPolygons(pts,faces)
    materials={mat for obj in owners for mat in obj.data.materials}
    for mat in materials:
        graph=mat.node_tree
        base=graph.nodes.get("Principled BSDF").inputs["Base Color"]
        previous=base.links[0].from_socket
        colors=graph.nodes.new("ShaderNodeVertexColor")
        colors.layer_name="Shelf contact"
        multiply=graph.nodes.new("ShaderNodeMixRGB")
        multiply.blend_type="MULTIPLY"
        multiply.inputs[0].default_value=1.
        graph.links.new(previous,multiply.inputs[1])
        graph.links.new(colors.outputs["Color"],multiply.inputs[2])
        graph.links.new(multiply.outputs[0],base)
    raysets={}
    for obj in owners:
        mesh=obj.data
        colors=mesh.color_attributes.new(name="Shelf contact",type="BYTE_COLOR",domain="CORNER")
        mesh.color_attributes.active_color=colors
        samples={}
        values=[]
        for face in mesh.polygons:
            normal=face.normal
            key=tuple(round(v*20) for v in normal)
            if key not in raysets:
                tangent=normal.cross(Vector((0,0,1)) if abs(normal.z)<.92 else Vector((1,0,0))).normalized()
                bitangent=normal.cross(tangent)
                raysets[key]=[(normal*rise+tangent*cos(a)+bitangent*sin(a)).normalized()
                              for rise,phase in ((.49,.17),(1.45,.57))
                              for a in [phase+i*tau/5 for i in range(5)]]
            for i in face.vertices:
                p=mesh.vertices[i].co
                sample=(*key,*(round(v*220) for v in p))
                if sample not in samples:
                    start=p+normal*.0011
                    shade=0.
                    for direction in raysets[key]:
                        hit=tree.ray_cast(start,direction,.28)[3]
                        if hit is not None:
                            shade+=(1-hit/.28)**1.4
                    samples[sample]=1.-.69*shade/len(raysets[key])
                value=samples[sample]
                values.extend((value,value,value,1.))
        colors.data.foreach_set("color",values)
        obj["contact_range_m"]=.28
        obj["contact_samples"]=len(samples)
        print("JINMA_CONTACT",obj.name,len(samples),round(min(samples.values()),3),flush=True)
