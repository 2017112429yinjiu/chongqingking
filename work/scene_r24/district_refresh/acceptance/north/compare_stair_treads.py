"""Verify tread and landing geometry before and after the under-stair recess."""
import json
from pathlib import Path
import sys

import bpy

name='COL_Liangtingzi_RearStair_43'
candidate=bpy.context.scene.objects[name]
base_file=Path(__file__).resolve().parents[2]/'street_groups/matix/matix_streets.blend'

with bpy.data.libraries.load(str(base_file),link=False) as (src,dst):
    assert name in src.objects
    dst.objects=[name]
base=dst.objects[0]


def top_faces(obj):
    return sorted(tuple(sorted(tuple(obj.matrix_world @ obj.data.vertices[i].co) for i in f.vertices))
                  for f in obj.data.polygons if f.normal.z>.70)


before,after=top_faces(base),top_faces(candidate)
assert before==after
report=dict(count=len(after),top_surfaces_identical=True,
   top_heights=sorted({s[0][2] for s in after}),
   underside_z=39.68,source=base_file.name,candidate=Path(bpy.data.filepath).name)
Path(sys.argv[sys.argv.index('--')+1]).write_text(json.dumps(report,indent=2)+'\n')
print('CQ_REAR_STAIR_TREADS_IDENTICAL',len(after))
