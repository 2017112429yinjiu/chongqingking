"""Original eye articulation and relaxed eyebrow fit for the core CC0 head."""
import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def build(rig,human):
    eyes=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'low-poly' in o.name)
    brow=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'eyebrow' in o.name)
    # Lift the inner brow smoothly rather than preserving a permanent frown.
    for v in brow.data.vertices:
        x=abs((brow.matrix_world@v.co).x)
        v.co.z+=.0025*math.exp(-((x-.018)/.022)**2)-.001*math.exp(-((x-.061)/.016)**2)
    bpy.context.view_layer.update()
    evaluated=human.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    skin=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons])
    evaluated.to_mesh_clear()
    for v in brow.data.vertices:
        world=brow.matrix_world@v.co
        hit=skin.ray_cast(Vector((world.x,-1,world.z)),Vector((0,1,0)),2)[0]
        if hit:
            world.y=hit.y-.0006;v.co=brow.matrix_world.inverted()@world
    centers={}
    for side,sign in [('l',1),('r',-1)]:
        points=[eyes.matrix_world@v.co for v in eyes.data.vertices if v.co.x*sign>0]
        centers[side]=Vector(tuple((min(p[i] for p in points)+max(p[i] for p in points))*.5 for i in range(3)))
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='EDIT')
    for side,center in centers.items():
        bone=rig.data.edit_bones.new('eye_'+side)
        bone.head=center;bone.tail=center+Vector((0,-.025,0));bone.parent=rig.data.edit_bones['head']
    bpy.ops.object.mode_set(mode='OBJECT')
    eyes.vertex_groups.clear()
    for side,sign in [('l',1),('r',-1)]:
        group=eyes.vertex_groups.new(name='eye_'+side)
        group.add([v.index for v in eyes.data.vertices if v.co.x*sign>0],1,'REPLACE')
    print('FACE_EYE_RIG',centers,flush=True)
