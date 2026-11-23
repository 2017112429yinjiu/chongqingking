"""Identify the source meshes in road-eye captures before changing structures."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector
s=Path(__file__).resolve().parent/'scene_r24'
eye=Vector((51.25,-81.,11.17));aim=Vector((60.8,-87.3,9.04))
f=(aim-eye).normalized();up=Vector((0,0,1));right=f.cross(up).normalized();up=right.cross(f)
dip=math.tan(math.radians(65)*.5); deps=bpy.context.evaluated_depsgraph_get()
rows=[]
for screen in [(420,402),(401,469),(215,491),(307,374),(168,318),(198,282),(274,299),(131,255),(462,110),(275,220),(379,130),(475,126),(34,471)]:
    x,y=screen
    direction=(f+right*((x/960*2-1)*dip*16/9)+up*((1-y/540*2)*dip)).normalized()
    p=eye.copy();stack=[]
    for i in range(8):
        ok,hit,n,face,ob,_=bpy.context.scene.ray_cast(deps,p,direction,distance=120)
        if not ok:break
        stack.append([ob.name,[round(q,3) for q in hit],[round(q,2) for q in n]])
        p=hit+direction*.026
    rows.append([screen,stack])
(s/'junction_picks.json').write_text(json.dumps(rows))

