"""Build one proposed district region from its independent site controls."""
import json
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[1]
ASSETS = SCENE.parent / 'project/chongqing_godot_v05/assets'
sys.path.insert(0, str(HERE.parent / 'street_groups'))
from factory import Mesh, terrain


def read(path):
    return json.loads(path.read_bytes())


class Region:
    def __init__(self, name):
        self.name = name
        self.meshes = []
        self.textures = {}
        self.fill = {}
        self.images = {}
        self.retired = []
        self.replacement = []
        self.points = {}
        self.ground = terrain()

    def finish(self, name, color, texture=None, shaded=0., metal=0., rough=.84):
        label = self.name.title() + ' review ' + name
        mat = bpy.data.materials.new(label)
        mat.diffuse_color = (*color, 1)
        mat.use_nodes = True
        surface = mat.node_tree.nodes.get('Principled BSDF')
        surface.inputs['Base Color'].default_value = (*color, 1)
        surface.inputs['Metallic'].default_value = metal
        surface.inputs['Roughness'].default_value = rough
        if texture:
            asset = 'chongqing_district_' + texture
            tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
            if asset not in self.images:
                image = bpy.data.images.load(str(ASSETS / asset), check_existing=False)
                image.filepath = '//../../../project/chongqing_godot_v05/assets/' + asset
                self.images[asset] = image
            tex.image = self.images[asset]
            mat.node_tree.links.new(tex.outputs['Color'], surface.inputs['Base Color'])
            self.textures[label] = 'res://assets/' + asset
            if shaded:
                self.fill[label] = [shaded, *color]
                mat.node_tree.links.new(tex.outputs['Color'], surface.inputs['Emission Color'])
                surface.inputs['Emission Strength'].default_value = shaded
        elif shaded:
            surface.inputs['Emission Color'].default_value = (*color, 1)
            surface.inputs['Emission Strength'].default_value = shaded
        return mat

    def mesh(self, name):
        mesh = Mesh(name)
        self.meshes.append(mesh)
        return mesh

    def floor(self, e, n):
        hit = self.ground.ray_cast(Vector((e, n, 95)), Vector((0, 0, -1)), 130)[0]
        assert hit is not None, (e, n)
        return hit.z

    def donor(self, library, name):
        previous = bpy.data.objects.get(name)
        if previous is not None:
            bpy.data.objects.remove(previous, do_unlink=True)
        with bpy.data.libraries.load(str(library), link=False) as (source, linked):
            assert name in source.objects, (library,name)
            linked.objects = [name]
        part = linked.objects[0]
        bpy.context.collection.objects.link(part)
        self.replacement.append(part)
        return part

    def save(self, output):
        made = [mesh.save() for mesh in self.meshes] + self.replacement
        for obj in list(bpy.data.objects):
            if obj not in made:
                bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.orphans_purge(do_recursive=True)
        model = 'acceptance-' + self.name
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(output/(model+'.blend')), compress=True, relative_remap=False)
        bpy.ops.export_scene.gltf(filepath=str(output/(model+'.glb')), export_format='GLB',
                                  export_image_format='NONE', export_cameras=False, export_lights=False)
        plan = {'new_meshes':[m.name for m in self.meshes], 'retired_objects':self.retired,
                'replacement_meshes':[m.name for m in self.replacement],
                'surface_textures':self.textures,'shaded_surface_fill':self.fill,
                'player_points':self.points}
        (output/(model+'.json')).write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
        print('CQ_ACCEPTANCE_REGION',self.name,[(obj.name,len(obj.data.polygons)) for obj in made])


def box(mesh, point, u0, u1, v0, v1, z0, z1, finish):
    ring = ((u0,v0),(u1,v0),(u1,v1),(u0,v1))
    mesh.solid([point(u,v,z0) for u,v in ring], [point(u,v,z1) for u,v in ring],finish)


def apply_finish(part, top, side):
    """Use existing collision positions and UVs for a new visible finish."""
    part.data.materials.clear()
    part.data.materials.append(top)
    part.data.materials.append(side)
    for face in part.data.polygons:
        face.material_index = int(face.normal.z < .6)
    vertices = [part.matrix_world @ v.co for v in part.data.vertices]
    faces = [f.vertices[:] for f in part.data.polygons]
    return BVHTree.FromPolygons(vertices, faces)


def main():
    region, folder = sys.argv[sys.argv.index('--')+1:]
    out = Path(folder)
    scope = Region(region)
    runpy.run_path(str(HERE/region/'sites.py'))['make'](scope)
    scope.save(out)


if __name__ == '__main__':
    main()
