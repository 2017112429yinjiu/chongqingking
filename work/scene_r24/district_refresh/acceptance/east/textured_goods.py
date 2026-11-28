"""The native scan and mapped surfaces used at the market counters."""
from hashlib import sha256
from math import radians
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
import numpy as np

from build import Mesh, read

HERE=Path(__file__).resolve().parent
G=HERE.parents[3]/'assets_incoming/r24_noodle/ginger'
TEXTURE='district_500/acceptance_textures/'
STOCK='chongqing_district_'


class UVSurface(Mesh):
    def __init__(self,name):
        super().__init__(name)
        self.coordinates=[]

    def face(self,points,finish,uv=None):
        super().face(points,finish)
        self.coordinates.append(uv)

    def save(self):
        obj=super().save()
        layer=obj.data.uv_layers.active.data
        for face,coordinates in zip(obj.data.polygons,self.coordinates,strict=True):
            if coordinates is not None:
                for i,uv in zip(face.loop_indices,coordinates,strict=True):
                    layer[i].uv=uv
        return obj


def food_material(scope,name,colours,kind):
    root=TEXTURE+kind
    return scope.pbr(name,colours,root+'-albedo.jpg',root+'-normal.jpg',root+'-rough.jpg',
                     ambient=.12,tint=colours)


def plant_material(scope,name,colours,*,purple=False):
    diffuse=(TEXTURE+'purple-leaf-dusk-albedo.jpg' if purple else STOCK+'shrub_01_diff_2k.jpg')
    return scope.pbr(name,colours,diffuse,STOCK+'shrub_01_nor_gl_2k.jpg',STOCK+'shrub_01_arm_2k.jpg',
                     ambient=.18 if purple else .20,tint=colours,packed_roughness=True,
                     normal_strength=.32 if purple else .78,specular=.17 if purple else .50)


def ginger(scope,at,center_u,center_v,base_z,bearing):
    record=read(G/'PROVENANCE.json')
    for sample in record['files']:
        f=G/sample['file']
        assert f.stat().st_size==sample['size'] and sha256(f.read_bytes()).hexdigest()==sample['sha256'],f
    bpy.ops.import_scene.gltf(filepath=str(G/'food_ginger_01.gltf'))
    stamp=next(o for o in bpy.context.selected_objects if o.type=='MESH')
    geometry=stamp.data
    geometry.transform(stamp.matrix_world)
    assert geometry.uv_layers.active
    # Same principal-axis registration used in district_connections/ginger.py.
    points=np.array([list(v.co) for v in geometry.vertices])
    axes=np.linalg.eigh(np.cov(points.T))[1][:,::-1].T.copy()
    if np.linalg.det(axes)<0:
        axes[1]*=-1
    geometry.transform(Matrix.Rotation(.62,4,'Z')@Matrix(axes).to_4x4())
    lo=np.array([min(v.co[i] for v in geometry.vertices) for i in range(3)])
    hi=np.array([max(v.co[i] for v in geometry.vertices) for i in range(3)])
    width=max(hi[0]-lo[0],hi[1]-lo[1])
    center=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
    for vert in geometry.vertices:
        vert.co=(vert.co-center)/width
    geometry.update()
    material=TEXTURE+'ginger-scan-'
    finish=scope.pbr('ginger scan with original UVs',(1.,.89,.73),material+'albedo.jpg',
                     material+'normal.jpg',material+'rough.jpg',ambient=.24,tint=(1.,.91,.78),
                     normal_strength=.25,specular=.13)
    geometry.materials.clear()
    geometry.materials.append(finish)
    for face in geometry.polygons:
        face.material_index=0
    geometry.name='Review01_GingerOwnedUV'
    positions=(
        (-.17,-.20,.161,20,-5),(.03,-.22,.189,-39,3),(.17,-.08,.143,84,6),
        (-.13,.01,.198,111,4),(.065,.04,.212,-70,-4),
        (-.09,.19,.162,153,7),(.13,.20,.174,19,-3),
    )
    for i,(u,v,length,turn,tilt) in enumerate(positions):
        frame=Matrix.Rotation(bearing+radians(turn),4,'Z')@Matrix.Rotation(radians(tilt),4,'X')@Matrix.Scale(length,4)
        bottom=min((frame@v.co).z for v in geometry.vertices)
        target=Vector(at(center_u+u,center_v+v,base_z))
        frame.translation=target-Vector((0,0,bottom))
        item=bpy.data.objects.new(f'Review01_Ginger_{i+1:02d}',geometry)
        bpy.context.collection.objects.link(item)
        item.matrix_world=frame
        scope.attached_art.append(item)
    bpy.data.objects.remove(stamp,do_unlink=True)
