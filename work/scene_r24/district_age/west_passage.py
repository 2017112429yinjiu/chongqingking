"""Reconnect both surviving flights via the outside of the workers' courtyard."""
import json,math
from mathutils import Vector
from roads import scene,changed,road_record,asset
from survey import Surfaces
route=[[-75.95,17.55],[-75.70,19.15],[-74.50,20.70],[-71.80,23.0],[-69.48,25.80],[-69.40,31.90],[-71.60,34.70],[-73.95,37.60],[-74.15,39.12]]
# The first upper tread stood 43 cm above the approach. Lift the supporting terrain smoothly
# to the measured foot of that flight, tapering back under its stone and across both cheeks.
count=0
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3.-2.*t)
for o in scene.objects:
    if o.type!='MESH' or not o.name.startswith('COL_Terrain_200m'):continue
    modified=0
    for v in o.data.vertices:
        p=o.matrix_world@v.co;x,y,z=p
        if not(-77.8<x<-70.5 and 33.5<y<40.5):continue
        spine=-71.6-(min(y,38)-34.7)*.72
        weight=(1-smooth((abs(x-spine)-.93)/1.3))*smooth((y-33.5)/4.3)*(1-smooth((y-38.25)/2.05))
        if weight<=0:continue
        target=24.2797+.14*(y-38.05);dz=target-z
        if 0<dz<.75:p.z+=dz*weight;v.co=o.matrix_world.inverted()@p;modified+=1
    if modified:o.data.update();changed.add(o.name);count+=modified
road_record['west_approach_vertices']=count
(asset/'west_passage.json').write_text(json.dumps(route),'utf8')
