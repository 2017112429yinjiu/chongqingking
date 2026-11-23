"""Create the first-shift scooter box in the original vehicle's metre coordinates."""
from pathlib import Path
import bpy, bmesh, math
from mathutils import Vector

here=Path(__file__).resolve().parent
game=here.parents[2]/'project/chongqing_godot_v05'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(game/'assets/vehicles/scooter_r18.glb'))
rubber=bpy.data.objects['Scooter_Body_rubber']
rubber.parent=None
rubber.name='FixedRubber'
bm=bmesh.new();bm.from_mesh(rubber.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z>1.30 and -.84<v.co.y<-.32],context='VERTS')
# Match the lowered opening, including the donor's top edging and four corner posts.
for vertex in bm.verts:
    if -.84 < vertex.co.y < -.32 and abs(vertex.co.x)<.28 and 1.25 < vertex.co.z < 1.302:
        vertex.co.z-=.060
bm.to_mesh(rubber.data);bm.free()
rubber.data.materials.clear()
for o in list(bpy.context.scene.objects):
    if o!=rubber: bpy.data.objects.remove(o,do_unlink=True)
def mat(name,colour):
    m=bpy.data.materials.new(name);m.diffuse_color=(*colour,1);return m
outer=mat('BoxOrange',(.60,.28,.045)); liner=mat('InsulatedLiner',(.15,.16,.15)); dark=mat('LidStrap',(.024,.025,.022))
def part(name,pos,dims,material,parent=None,r=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel=o.modifiers.new('Rounded seams','BEVEL');bevel.width=r;bevel.segments=3
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    normals=o.modifiers.new('Corner normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=normals.name)
    o.data.materials.append(material)
    if parent:
        o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
    return o
part('Base',(0,-.58,.833),(.52,.46,.036),outer)
for x in [-.25,.25]:part('Side',(x,-.58,1.030),(.02,.46,.36),outer)
for y in [-.80,-.36]:part('End',(0,y,1.030),(.482,.02,.36),outer)
part('InnerFloor',(0,-.58,.857),(.48,.42,.018),liner)
for x in [-.236,.236]:part('InnerSide',(x,-.58,1.023),(.009,.421,.326),liner)
for y in [-.785,-.375]:part('InnerEnd',(0,y,1.023),(.465,.009,.326),liner)
hinge=bpy.data.objects.new('LidHinge',None);bpy.context.collection.objects.link(hinge)
hinge.location=(0,-.817,1.219);bpy.context.view_layer.update()
part('Lid',(0,-.58,1.230),(.55,.49,.045),outer,hinge,.006)
part('LidLining',(0,-.58,1.204),(.48,.416,.010),liner,hinge)
for x in [-.16,.16]:part('Band',(x,-.58,1.256),(.031,.46,.008),dark,hinge,.001)
# Two friction hinges hold the opened lid. The near tab can be operated one-handed.
for x in [-.19,.19]:
    part('HingeBracket',(x,-.812,1.188),(.08,.019,.053),dark)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.015,depth=.09,location=(x,-.817,1.219),rotation=(0,math.pi/2,0))
    pin=bpy.context.object
    pin.name='FrictionHinge'
    pin.data.materials.append(dark)
part('SidePull',(.257,-.662,1.252),(.054,.073,.016),dark,hinge)
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'insulated_box.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(game/'assets/vehicles/first_shift_box.glb'),export_format='GLB',export_animations=False,export_extras=False)
