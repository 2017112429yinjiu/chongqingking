"""Portable PBR surfaces for the complete Chongqing district.

All runtime inputs are standard image textures supported by Blender's glTF
exporter. Source scans and original mathematically-authored materials are
distinguished in materials/material_provenance.json.
"""
from pathlib import Path
import json
import bpy

ROOT=Path(__file__).resolve().parent
MAT_ROOT=ROOT/'materials'


def build_materials():
    manifest=json.loads((MAT_ROOT/'material_provenance.json').read_text())
    result={}
    for key,spec in manifest['assets'].items():
        mat=bpy.data.materials.get('CQ03_PBR_'+key) or bpy.data.materials.new('CQ03_PBR_'+key)
        mat.use_nodes=True
        mat.use_backface_culling=True
        mat.diffuse_color=(.45,.45,.43,1.)
        mat['uv_meters']=float(spec['meters'])
        mat['source_url']=spec.get('source_url','')
        mat['license']=spec['license']
        mat['authors']=', '.join(spec['authors'])
        mat['origin']=spec['origin']
        if spec.get('alpha'):
            mat.use_backface_culling=False
            mat.surface_render_method='DITHERED'
            mat['is_weathering_overlay']=True
        nt=mat.node_tree;nt.nodes.clear()
        out=nt.nodes.new('ShaderNodeOutputMaterial');out.location=(600,40)
        bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.location=(280,40)
        bs.inputs['Metallic'].default_value=float(spec.get('metallic',0.))
        bs.inputs['Roughness'].default_value=float(spec.get('roughness',.84))
        bs.inputs['Specular IOR Level'].default_value=.35
        nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
        for i,(role,rel) in enumerate(spec['maps'].items()):
            path=MAT_ROOT/rel
            if not path.is_file():raise FileNotFoundError(path)
            img=bpy.data.images.load(str(path),check_existing=True)
            img.colorspace_settings.name='sRGB' if role=='diff' else 'Non-Color'
            tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img
            tex.label=role;tex.location=(-400,320-i*260)
            tex.interpolation='Linear';tex.extension='REPEAT'
            if role=='diff':
                nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
                if spec.get('alpha'):nt.links.new(tex.outputs['Alpha'],bs.inputs['Alpha'])
            elif role=='rough':nt.links.new(tex.outputs['Color'],bs.inputs['Roughness'])
            elif role=='nor_gl':
                normal=nt.nodes.new('ShaderNodeNormalMap');normal.location=(0,-240)
                normal.inputs['Strength'].default_value=float(spec.get('normal_strength',.6))
                nt.links.new(tex.outputs['Color'],normal.inputs['Color'])
                nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
        result[key]=mat
    return result
