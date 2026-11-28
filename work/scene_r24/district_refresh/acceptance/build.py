"""Build one proposed district region from its independent site controls."""
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys

import bmesh
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
        self.borrowed = {}
        self.smooth = set()
        self.trees = []
        self.attached_art = []
        self.pbr_maps = {}
        self.tints = {}
        self.required_group = ''
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
            asset = texture if '/' in texture or texture.startswith('chongqing_district_') else 'chongqing_district_' + texture
            tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex.image = self.image(asset)
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

    def image(self, asset, data=False):
        if asset not in self.images:
            image = bpy.data.images.load(str(ASSETS / asset), check_existing=False)
            image.filepath = '//../../../project/chongqing_godot_v05/assets/' + asset
            if data:
                image.colorspace_settings.name = 'Non-Color'
            self.images[asset] = image
        return self.images[asset]

    def mossy_wall(self, name, color):
        base = 'district_r21/terraces_mossy_stone_wall_'
        normal, roughness = (base + suffix for suffix in ('nor_gl_2k.jpg', 'rough_2k.png'))
        return self.pbr(name, color, base + 'diff_2k.jpg', normal, roughness, ambient=.17)

    def pbr(self, name, color, albedo, normal, roughness, *, ambient=.17, tint=None,
            packed_roughness=False, normal_strength=.78, specular=.50):
        surface = self.finish(name, color, albedo, ambient)
        self.map_pbr(surface, normal, roughness, packed_roughness, normal_strength, specular)
        if tint is not None:
            self.tints[surface.name] = tint
            nodes = surface.node_tree.nodes
            links = surface.node_tree.links
            shader = nodes['Principled BSDF']
            base_color = shader.inputs['Base Color']
            image_output = base_color.links[0].from_socket
            mix = nodes.new('ShaderNodeMixRGB')
            mix.blend_type = 'MULTIPLY'
            mix.inputs[0].default_value = 1.
            mix.inputs[2].default_value = (*tint,1.)
            links.new(image_output,mix.inputs[1])
            links.new(mix.outputs['Color'],base_color)
        return surface

    def map_pbr(self, surface, normal, roughness, packed_roughness=False, normal_strength=.78, specular=.50):
        nodes = surface.node_tree.nodes
        links = surface.node_tree.links
        maps = [nodes.new('ShaderNodeTexImage') for _ in range(2)]
        for node, asset in zip(maps, (normal, roughness)):
            node.image = self.image(asset, data=True)
        bump = nodes.new('ShaderNodeNormalMap')
        bump.inputs['Strength'].default_value = normal_strength
        links.new(maps[0].outputs['Color'], bump.inputs['Color'])
        links.new(bump.outputs['Normal'], nodes['Principled BSDF'].inputs['Normal'])
        rough_output = maps[1].outputs['Color']
        if packed_roughness:
            channels = nodes.new('ShaderNodeSeparateColor')
            links.new(rough_output, channels.inputs['Color'])
            rough_output = channels.outputs['Green']
        links.new(rough_output, nodes['Principled BSDF'].inputs['Roughness'])
        nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = specular
        channels = ['res://assets/' + normal, 'res://assets/' + roughness, packed_roughness]
        if (normal_strength, specular) != (.78, .50):
            channels.extend((normal_strength, specular))
        self.pbr_maps[surface.name] = channels

    def mesh(self, name, mesh_class=Mesh):
        mesh = mesh_class(name)
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

    def preserve_finishes(self, part):
        self.borrowed[part.name] = {mat.name: mat.name for mat in part.data.materials if mat}

    def save(self, output):
        made = [mesh.save() for mesh in self.meshes] + self.attached_art + self.replacement
        for obj in made:
            if obj.name in self.smooth:
                geometry = bmesh.new()
                geometry.from_mesh(obj.data)
                bmesh.ops.remove_doubles(geometry, verts=list(geometry.verts), dist=.00001)
                geometry.to_mesh(obj.data)
                geometry.free()
                for face in obj.data.polygons:
                    face.use_smooth = True
        for obj in list(bpy.data.objects):
            if obj not in made:
                bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.orphans_purge(do_recursive=True)
        self.use_existing_donor_images()
        model = 'acceptance-' + self.name
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(output/(model+'.blend')), compress=True, relative_remap=False)
        bpy.ops.export_scene.gltf(filepath=str(output/(model+'.glb')), export_format='GLB',
                                  export_image_format='NONE', export_cameras=False, export_lights=False)
        plan = {'new_meshes':[m.name for m in self.meshes + self.attached_art], 'retired_objects':self.retired,
                'replacement_meshes':[m.name for m in self.replacement],
                'borrowed_materials':self.borrowed,
                'trees':self.trees, 'pbr_maps':self.pbr_maps, 'surface_tints':self.tints,
                'surface_textures':self.textures,'shaded_surface_fill':self.fill,
                'player_points':self.points}
        if self.required_group:
            plan['required_group'] = self.required_group
        (output/(model+'.json')).write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
        print('CQ_ACCEPTANCE_REGION',self.name,[(obj.name,len(obj.data.polygons)) for obj in made])

    def use_existing_donor_images(self):
        for image in bpy.data.images:
            marker = '/chongqing_godot_v05/assets/'
            if image.source != 'FILE' or marker not in image.filepath:
                continue
            asset = image.filepath.split(marker, 1)[1]
            target = ASSETS / asset
            if not target.is_file():
                continue
            if image.packed_file:
                match = sha256(image.packed_file.data).digest() == sha256(target.read_bytes()).digest()
                if not match:
                    continue
                image.unpack(method='REMOVE')
            image.filepath = '//../../../project/chongqing_godot_v05/assets/' + asset


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
