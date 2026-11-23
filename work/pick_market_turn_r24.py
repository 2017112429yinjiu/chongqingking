"""Identify the source meshes in road-eye captures before changing structures."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector
s=Path(__file__).resolve().parent/'scene_r24'
eye=Vector((25.3,-78.8,10.69));aim=Vector((40.0,-89.9,8.45))
f=(aim-eye).normalized();up=Vector((0,0,1));right=f.cross(up).normalized();up=right.cross(f)
dip=math.tan(math.radians(65)*.5); deps=bpy.context.evaluated_depsgraph_get()
rows=[]
for screen in [(69,215),(127,213),(329,228),(249,305),(308,371),(366,401),(428,316),(469,258),(700,314),(683,323),(304,438),(192,345),(120,302),(223,280),(490,259)]:
    x,y=screen
    direction=(f+right*((x/830*2-1)*dip*16/9)+up*((1-y/467*2)*dip)).normalized()
    p=eye.copy();stack=[]
    for i in range(8):
        ok,hit,n,face,ob,_=bpy.context.scene.ray_cast(deps,p,direction,distance=120)
        if not ok:break
        stack.append([ob.name,[round(q,3) for q in hit],[round(q,2) for q in n]])
        p=hit+direction*.026
    rows.append([screen,stack])
(s/'junction_view_picks.json').write_text(json.dumps(rows))

