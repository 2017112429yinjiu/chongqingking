"""Replace the contradicted upper 56 trial slab and stage the measured public return."""
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

from build import box, read


def remove_upper_trial(scope):
    # The parent meshes are identity-baked. The lower room, attached courtyard
    # and existing shared contact remain separate components in the game.
    for name in ('COL_Outer500_Frame_56','Outer500_Joinery_56'):
        obj=bpy.context.scene.objects[name]
        assert obj.matrix_world.is_identity
        mesh=bmesh.new()
        mesh.from_mesh(obj.data)
        count=len(mesh.faces)
        bmesh.ops.bisect_plane(mesh,geom=list(mesh.verts)+list(mesh.edges)+list(mesh.faces),
                              dist=.00004,plane_co=(0,0,6.84),plane_no=(0,0,1),
                              clear_outer=True,clear_inner=False)
        assert 0<len(mesh.faces)<count,(name,count,len(mesh.faces))
        mesh.to_mesh(obj.data)
        mesh.free()
        scope.replacement.append(obj)
        scope.preserve_finishes(obj)


def finish(scope, at, plot):
    remove_upper_trial(scope)
    source=read(Path(__file__).with_name('56-opening-plan.json'))
    slab=scope.mesh('Review56_WeatheredTopOfRetainedGameBase')
    cement=scope.finish('old 56 low concrete top',(.51,.53,.49),'concrete_wall_006_diff_2k.jpg',.25)
    grey=scope.finish('garage muted inner concrete',(.44,.45,.41),'concrete_wall_006_diff_2k.jpg',.19)
    sand=scope.finish('garage sand coloured bands',(.68,.62,.49),'plastered_wall_04_diff_1k.jpg',.24)
    rail=scope.finish('garage dark louvre blades',(.22,.24,.23),metal=.42)
    h=6.839-plot['height']
    u=plot['width']/2-.205
    v=plot['depth']/2-.205
    box(slab,at,-u,u,-v,v,h,h+.019,cement)
    model=scope.mesh('Review56_ObservedGarageWestFold')
    louvre=scope.mesh('Review56_OpenBaysAndLowerLouvres')
    features=source['features']
    for i,a,b in ((0,features['V'],features['W']),(1,features['W'],features['A'])):
        origin=Vector(a)
        run=Vector(b)-origin
        length=run.length
        unit=run.normalized()
        normal=Vector((-unit.y,unit.x))
        def q(u,v,z):
            e,n=origin+unit*u+normal*v
            return (e,n,z)
        for z0,z1 in ((5.43,5.69),(7.24,7.86),(10.21,10.82)):
            box(model,q,0,length,-.14,.32,z0,z1,sand)
            for j in range(3):
                high=z0+.09+j*(z1-z0)*.24
                box(louvre,q,0,length,-.174,-.137,high,high+.019,grey)
        for offset in (0,length*.54,length):
            box(model,q,max(offset-.14,-.15),min(offset+.15,length+.14),-.115,.28,5.57,10.33,sand)
        for u0,u1 in ((.16,length*.54-.17),(length*.54+.16,length-.17)):
            for j in range(5):
                z0=5.73+j*.225
                box(louvre,q,u0,u1,.095,.16,z0,z0+.040,rail)
            box(louvre,q,u0,u1,.33,.38,7.82,8.02,rail)
            box(louvre,q,u0,u1,.34,.42,9.57,9.65,rail)
    # These are photo-controlled fragments. The longer current parking decks,
    # ramp piers and the lower blocked private trial entrance are left intact.
