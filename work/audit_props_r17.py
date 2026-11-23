import bpy,json,sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'project/chongqing_blender_v05'))
from circulation_r17 import ROUTES
import district_layout as dl
from mathutils import Vector
found=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    if any(x in ob.name.lower() for x in ['tree','well','bin','garbage','bag','crate']):
        p=ob.matrix_world.translation
        dist=min(dl.distance_segment(p[:2],a,b)[0]-width/2 for _,pts,width,_ in ROUTES for a,b in zip(pts,pts[1:]))
        if dist<2:
            found.append({'name':ob.name,'location':list(p),'dimensions':list(ob.dimensions),'route_edge_distance':dist,'properties':{k:str(ob[k]) for k in ob.keys()}})
(ROOT/'audit/r17_props_near_routes.json').write_text(json.dumps(found,indent=2),encoding='utf-8')
print('PROP_AUDIT',len(found),flush=True)
