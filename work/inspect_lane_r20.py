"""Find the finished faces bounding the stepped lane. All coordinates in Blender metres."""
import bpy, math, json
from mathutils import Vector
from pathlib import Path
W = Path(__file__).resolve().parent
p = Vector((-39.5608,40.9019,0))
u = (Vector((-31.5071,55.1011,0))-p).normalized()
v = Vector((u.y,-u.x,0))
dg = bpy.context.evaluated_depsgraph_get()
def ray(start, direction, distance):
    hit, loc, normal, _, ob, _ = bpy.context.scene.ray_cast(dg,start,direction,distance=distance)
    return (round(loc.z,3),round((loc-start).length,3),ob.name) if hit else None
for i in range(1,17):
    foot = p+u*i+v*1
    f = ray(foot+Vector((0,0,33)),Vector((0,0,-1)),12)
    if not f:continue
    z=f[0]
    print('LANE',i,'xy',tuple(round(x,2) for x in foot[:2]),'ground',f,'wall/rise')
    for h in [0.55,1.35,2.15,3.25]:
        start=foot+Vector((0,0,z+h))
        print(h,ray(start,-v,3),ray(start,v,4))
