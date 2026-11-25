"""Crop the former hillside rail at the walls of the surveyed laundry."""
from math import cos, sin
import bmesh
import bpy
from mathutils import Matrix, Vector


def fit(source, plot):
    name = "R24_LinkRail_R24_link_painted_rail"
    with bpy.data.libraries.load(str(source), link=False) as (_, wanted):
        wanted.objects = [name]
    obj = wanted.objects[0]
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    mesh.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    u = Vector((cos(plot["bearing"]), sin(plot["bearing"]), 0))
    v = Vector((-u.y, u.x, 0))
    z = Vector((0, 0, 1))
    center = Vector((*plot["east_north"], plot["height"]))
    bounds = [(u,-plot["width"]/2+.10,plot["width"]/2-.10),
              (v,-plot["depth"]/2+.10,plot["depth"]/2-.10),(z,-.17,2.83)]
    for axis, lo, hi in bounds:
        for at in (lo,hi):
            bmesh.ops.bisect_plane(mesh, geom=list(mesh.verts)+list(mesh.edges)+list(mesh.faces),
                                   plane_co=center+axis*at, plane_no=axis,dist=.00001)
    inside = [face for face in mesh.faces if all(lo-.00002 < (face.calc_center_median()-center).dot(axis) < hi+.00002
                                                  for axis,lo,hi in bounds)]
    assert inside, "The registered rail must enter the laundry"
    count = len(inside)
    bmesh.ops.delete(mesh,geom=inside,context="FACES")
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.name = "Outer500_LaundryRailReturn"
    bpy.context.scene.collection.objects.link(obj)
    return {"original":name,"replacement":obj.name,"plot":plot["plot_id"],"cut_faces":count}
