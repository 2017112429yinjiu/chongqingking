"""Measure selected editable surfaces in a Blender scene in project ENU metres."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

PREFIXES = ('COL_Nanjimen_', 'Nanjimen_North', 'COL_R24_Link', 'COL_R24_Flyover', 'R24_Flyover', 'R24_LinkCaps',
            'COL_Nanqu', 'COL_Road_59146775_', 'COL_Road_1189963598_', 'COL_Road_49182408_',
            'COL_Road_176034707_', 'COL_Raijiapo_Ramp', 'COL_Changbin_', 'COL_Outer500_Surface_',
            'COL_Landing53_', 'COL_Terrain_200m', 'COL_Fenghuangtai11_', 'COL_Houci16_', 'COL_EastRoad_')


def main():
    arguments=sys.argv[sys.argv.index('--')+1:]
    guide, output = map(Path,arguments[:2])
    if len(arguments)==3 and arguments[2]=='--retain-core-reference':
        parent=Path(__file__).resolve().parents[3]/'district_patrol/city_and_patrol.blend'
        names=('COL_R24_LinkDeck_R24_link_asphalt','COL_Road_59146775_0_asphalt','COL_Road_59146775_1_asphalt',
               'R24_FlyoverBox_R24_link_concrete','COL_R24_LinkPiers_R24_link_concrete')
        with bpy.data.libraries.load(str(parent),link=True,relative=False) as (source, selected):
            assert set(names)<=set(source.objects)
            selected.objects=list(names)
        for obj in selected.objects:
            if obj.name not in bpy.context.scene.objects:
                bpy.context.collection.objects.link(obj)
    samples = json.loads(guide.read_text())['samples']
    objects = []
    index = []
    dependency = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or not obj.name.removeprefix("Grade__").startswith(PREFIXES):
            continue
        eval_obj = obj.evaluated_get(dependency)
        mesh = eval_obj.data
        if not mesh.polygons:
            continue
        coords = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
        bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]
        bvh = BVHTree.FromPolygons(coords, [polygon.vertices[:] for polygon in mesh.polygons])
        objects.append((obj.name, bounds, bvh))
        index.append({'mesh':obj.name,'bounds_enu':bounds,'vertices':len(coords),'faces':len(mesh.polygons),
                      'uv_layers':list(mesh.uv_layers.keys()),'materials':[mat.name for mat in mesh.materials if mat],
                      'library':bpy.path.abspath(obj.library.filepath) if obj.library else None})
    result={}
    for family, coords in samples.items():
        values=[]
        for e,n in coords:
            surface=[]
            for name,bounds,bvh in objects:
                if not (bounds[0][0]<=e<=bounds[0][1] and bounds[1][0]<=n<=bounds[1][1]):
                    continue
                down=bvh.ray_cast(Vector((e,n,100)),Vector((0,0,-1)),130)
                up=bvh.ray_cast(Vector((e,n,-30)),Vector((0,0,1)),130)
                if down[0] is not None:
                    surface.append({'mesh':name,'top':down[0].z,'soffit':up[0].z,'face_top':down[2],'face_soffit':up[2]})
            values.append({'en':[e,n],'meshes':sorted(surface,key=lambda row:row['top'],reverse=True)})
        result[family]=values
    output.write_text(json.dumps({'blender':bpy.app.version_string,'source':bpy.data.filepath,'objects':index,'samples':result},indent=2)+'\n')
    print('Nanqu editable survey',len(objects),sum(len(v) for v in result.values()))


main()
