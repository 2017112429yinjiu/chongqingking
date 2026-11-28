"""Add visible native leaf geometry to the registered licensed tree stems."""
from pathlib import Path
import runpy

import bpy

GROUPS=Path(__file__).resolve().parents[2]/'street_groups'


def finish_crowns(scope):
    source=runpy.run_path(str(GROUPS/'nanqu_rail_grade/build_landside.py'))
    material=scope.finish('scanned street broadleaf',(.30,.43,.16),
                          'island_tree_01_leaves_diff_2k.jpg',.21,rough=.76)
    stock={}
    for index, row in enumerate(scope.trees):
        if 'StreetTree' not in row['name'] and 'Western' not in row['name']:
            continue
        donor=bpy.context.scene.objects[row['donor']]
        if row['name'].startswith('Western3031'):
            row['scale']=max(row['scale']*1.38,.88)
            width=4.05+index%3*.43
        elif row['name'].startswith('Western49'):
            row['scale']=max(row['scale']*1.46,.93)
            width=3.18+index%3*.30
        else:
            row['scale']=max(row['scale']*1.35,.82)
            width=3.15+index%3*.29
        height=donor.dimensions.z*row['scale']
        k=index%3
        if k not in stock:
            seed=187+k*37
            stock[k]=source['canopy'](f'{scope.name.title()} broadleaf crown {k}',
                                    source['lower_lobes'](seed),seed,material,
                                    spread=1.13,leaf_size=(.042,.066),density=70)
        crown=bpy.data.objects.new(row['name']+'ScannedLeaves',stock[k])
        e,n,z=row['enu']
        lift=.58 if row['name'].startswith('Western49') else .20
        crown.location=(e,n,z+lift)
        crown.rotation_euler.z=row['yaw']
        crown.scale=(width,width*.97,height)
        bpy.context.collection.objects.link(crown)
        scope.attached_art.append(crown)
