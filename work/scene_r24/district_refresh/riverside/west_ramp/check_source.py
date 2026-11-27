"""Confirm that the ramp and wall still use the original physical supports."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import struct

import bpy

HERE = Path(__file__).resolve().parent
NAMES = ("COL_Outer500_WestCourt_Paving","COL_Outer500_WestCourt_Retaining",
         "Outer500_WestCourt_BlueFinish")
ASSETS = HERE.parents[3] / "project/chongqing_godot_v05/assets/district_500"
plan = json.loads((ASSETS / "west-ramp.json").read_bytes())


def fingerprint(obj):
    digest=hashlib.sha256()
    world=obj.matrix_world
    faces=obj.data.polygons
    for face in faces:
        digest.update(struct.pack("<I",len(face.vertices)))
        for index in face.vertices:
            digest.update(struct.pack("<fff",*(world@obj.data.vertices[index].co)))
    return len(faces),digest.hexdigest()


current = {name:bpy.context.scene.objects[name] for name in NAMES}
after = {name:fingerprint(obj) for name,obj in current.items()}
with bpy.data.libraries.load(str(HERE.parent/"west_court/west-court.blend"),link=False) as (_, donor):
    donor.objects=list(NAMES)
before = {name:fingerprint(obj) for name,obj in zip(NAMES,donor.objects)}
assert before[NAMES[0]]==after[NAMES[0]],(before,after)


def wall_faces(obj, skip):
    return Counter(tuple(sorted(tuple(round(v,5) for v in obj.matrix_world @ obj.data.vertices[i].co)
                                for i in face.vertices))
                   for face in obj.data.polygons if face.index not in skip)


removed = plan["playground"]["old_wall_internal_faces"]
assert wall_faces(donor.objects[1],removed)==wall_faces(current[NAMES[1]],()),removed
print("CQ_WEST_RAMP_PHYSICAL_SOURCE",json.dumps({"before":before,"after":after,"internal_wall_faces":removed}))
fixtures = {}
for name in ("COL_WestPlayground_PerforatedBlueClimber","COL_WestPlayground_PaleAndRoseMound",
             "WestPlayground_PairEmbeddedChutes","COL_WestPlayground_ThreeRotatingBowls"):
    obj = bpy.context.scene.objects[name]
    fixtures[name] = {"faces":len(obj.data.polygons),"size_m":list(obj.dimensions),
                      "materials":[mat.name for mat in obj.data.materials]}
    assert fixtures[name]["faces"] > 100
images = {image.name:list(image.size) for image in bpy.data.images
          if image.name.startswith("West play ") and image.packed_file}
assert len(images) == 3 and all(size == [256,256] for size in images.values()),images
print("CQ_WEST_PLAYGROUND_SOURCE",json.dumps({"fixtures":fixtures,"packed_aggregate":images}))
