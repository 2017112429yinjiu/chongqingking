from pathlib import Path
import bpy,math,json
from mathutils import Vector
W=Path(__file__).resolve().parent; S=W/'scene_r23'
d=json.loads((S/'assets/block.json').read_text())['views']; out={}
for key,points in {'main_road':[(.68,.94),(.64,.88),(.52,.86),(.39,.94),(.34,.93),(.75,.97),(.53,.73),(.15,.92)],'street_support':[(.84,.88),(.80,.96),(.90,.93),(.97,.94),(.69,.81),(.81,.78),(.62,.84),(.46,.83)]}.items():
    eye,t=(Vector((x,-z,y)) for x,y,z in d[key]);direction=(t-eye).normalized();right=direction.cross(Vector((0,0,1))).normalized();up=right.cross(direction).normalized()
    h=math.tan(math.radians(67)/2);data=[]
    for u,v in points:
        ray=(direction+right*((u*2-1)*h*16/9)+up*((1-v*2)*h)).normalized()
        hit,pos,n,_,ob,_=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),eye,ray,distance=170)
        data.append([u,v,ob.name if hit else None,[round(x,3) for x in pos]])
    out[key]=data
(S/'pixel_meshes.json').write_text(json.dumps(out,indent=1))

