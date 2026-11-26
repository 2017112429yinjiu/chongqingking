"""Replace only plot 62 and attach the field pavilion to the game's measured ground."""
import json
import os
from pathlib import Path
import sys
import bpy

here=Path(__file__).resolve().parent
scene=here.parents[2]
staging=Path(os.environ['CQ_PAVILION62_STAGING'])
groups=scene/'district_refresh/street_groups'
sys.path[:0]=[str(groups),str(scene/'district_500')]
from refresh_geometry import ASSETS, latest_donors, read, strip_plots
from riverside import make_strip, material, terrain_faces

layout=read(ASSETS/'layout.json')
owners=read(here/'ownership.json')
donors=latest_donors([
    ('guoco-frontages', groups/'guoco/guoco-frontages.blend'),
    ('public-edges', groups/'matix/public-edges.blend'),
    ('xingchen', groups/'xingchen/xingchen.blend'),
])
replacements,retired,counts=strip_plots(owners,(62,),layout,donors)
with bpy.data.libraries.load(str(staging/'pavilion62-body.blend'),link=False) as (source,out):
    out.objects=source.objects[:]
for building in out.objects:
    bpy.context.scene.collection.objects.link(building)

pedestrian=[[-19.0,-188.68],[-16.2,-188.76],[-14.02,-188.94],[-12.78,-189.19]]
terrains=list(terrain_faces())
finish=[
    material('Park 62 grey approach paving',(.56,.51,.47),'stone_floor_diff_2k.jpg'),
    material('Park 62 sanded verge stone',(.61,.57,.53),'stone_wall_05_diff_2k.jpg'),
    material('Park 62 pale stone edge',(.64,.64,.56),'concrete_floor_worn_001_diff_2k.jpg'),
]
strip=make_strip({'id':'park_pavilion_street_approach','points':pedestrian,'width_m':1.86,'raise_m':.018,'finish':0},
                 terrains,finish)
strip.name='Riverside_62_StreetSideApproach'
parts=[*out.objects,strip]
keep=replacements+parts
for obj in list(bpy.data.objects):
    if obj not in keep:
        bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'pavilion62.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(ASSETS/'pavilion62.glb'),export_format='GLB',
                          export_cameras=False,export_lights=False)
record={'replacement_meshes':[o.name for o in replacements],'retired_objects':retired,
        'new_meshes':[o.name for o in parts],'removed_face_counts':counts,'source_plot':62,'approach':pedestrian}
(ASSETS/'pavilion62.json').write_text(json.dumps(record,indent=2)+'\n')
print('CQ_RIVERSIDE_62_IN_GAME',record)
