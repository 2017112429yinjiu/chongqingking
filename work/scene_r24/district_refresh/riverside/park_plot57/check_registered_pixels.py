"""Run in the linked checkpoint. Image origin is top left."""
import json
from math import radians,tan
from pathlib import Path
import re
import bpy
from mathutils import Vector
here=Path(__file__).resolve().parent
proof=here.parent/'west_ramp/evidence/street-native-round-trip.json'
frames={row['frame']:row for row in json.loads(proof.read_bytes())['native_frames']}
samples={
    'inside_look_back.png':[(320,203),(369,228),(419,229),(440,236),(478,240),(507,234),(548,238),
                            (566,234),(580,236),(612,242),(638,236),(719,273),(804,295),(810,306),(578,149)],
    'street_return.png':[(445,304),(480,310),(525,331),(556,339),(583,349),(628,363),(700,368),
                         (749,371),(776,379),(787,395),(600,320),(416,169),(522,176)],
    'registered_blue.png':[(592,218),(637,218),(669,231),(686,231),(705,232),(712,229),
                           (719,228),(724,229),(737,234),(763,241),(706,255),(511,134)],
}
result={}
scene=bpy.context.scene
depsgraph=bpy.context.evaluated_depsgraph_get()
for label,pixels in samples.items():
    f=frames[label]
    eye=Vector(f['eye_enu'])
    if 'target_enu' in f:
        forward=(Vector(f['target_enu'])-eye).normalized()
        fov=71
    else:
        x,y,z=map(float,re.findall(r'-?\d+(?:\.\d+)?',f['direction_xyz']))
        forward=Vector((x,-z,y)).normalized()
        fov=68
    right=forward.cross(Vector((0,0,1))).normalized()
    up=right.cross(forward).normalized()
    results=[]
    for x,y in pixels:
        rayon=tan(radians(fov/2))
        direction=(forward+right*((x+.5-430)*rayon/242)+up*((242-(y+.5))*rayon/242)).normalized()
        hit,position,normal,index,obj,_=scene.ray_cast(depsgraph,eye,direction,distance=260)
        row={'pixel':[x,y],'eye':list(eye),'fov':fov}
        if hit:
            poly=obj.data.polygons[index]
            material=obj.data.materials[poly.material_index] if obj.data.materials else None
            row.update(obj=obj.name,source=Path(obj.library.filepath).name if obj.library else None,
                       face=index,material=material.name if material else None,
                       hit_enu=[round(k,4) for k in position],normal=[round(k,4) for k in normal])
        results.append(row)
    result[label]=results
print('CQ_PARK_PIXELS',json.dumps(result))
