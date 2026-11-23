"""Identify roof decks, existing equipment and shop fixtures in the saved R21 city."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

work = Path(__file__).resolve().parent
source = work/'project/chongqing_blender_v05/architecture_manifest.json'
records = json.loads(source.read_text(encoding='utf8'))['buildings']
dg = bpy.context.evaluated_depsgraph_get()
scene = bpy.context.scene

def hit(origin,direction,distance):
    ok,point,normal,idx,obj,_ = scene.ray_cast(dg,Vector(origin),Vector(direction),distance=distance)
    return [obj.name,[round(k,4) for k in point],round(normal.z,4)] if ok else None

roofs={}
for b in records:
    if b['roof_form'] not in ['flat','terrace']:continue
    top=b['base_m']+b['height_m']
    floor_hits={}
    for obj in scene.objects:
        if obj.type!='MESH' or ('B_'+str(b['id'])+'_') not in obj.name:continue
        tris=0;area=0
        for poly in obj.data.polygons:
            if poly.normal.z>.999 and abs((obj.matrix_world@poly.center).z-top)<.03 and poly.area>.1:
                tris+=1;area+=poly.area
        if area>2:floor_hits[obj.name]=[round(area,2),tris]
    roofs[str(b['id'])]={'top':top,'decks':floor_hits,'bounds':b['points'],'center':b['center'],'form':b['roof_form']}
mounts={}
for x in [-32.27,-31.94,-31.52,-30.51,-29.56,-28.38,-28.10]:
    mounts[str(x)]={str(z):hit((x,-59.0,z),(0,-1,0),4.7) for z in [13.79,13.87,13.98,14.04,14.16]}
tables={}
for x in [-30.78,-30.53,-30.17,-29.96]:
    for y in [-60.95,-60.74,-60.53]:
        tables[f'{x},{y}']=hit((x,y,13.03),(0,0,-1),2.8)
out=work/'scene_r22/survey.json'
out.write_text(json.dumps({'roofs':roofs,'mounts':mounts,'table':tables},indent=2),encoding='utf8')
print('Surveyed',len(roofs),'flat or terraced roofs')
