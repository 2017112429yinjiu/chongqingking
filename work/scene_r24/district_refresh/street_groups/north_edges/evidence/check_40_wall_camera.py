import bpy,json,sys,math
from mathutils import Vector
v=json.load(open(sys.argv[-1]))[2:4]
scene=bpy.context.scene; deps=bpy.context.evaluated_depsgraph_get()
for i,row in enumerate(v):
 eye=Vector(row['eye_enu']); aim=Vector(row['target_enu']); rot=(aim-eye).to_track_quat('-Z','Y'); vf=math.tan(math.radians(row['fov_deg']/2))
 for x,y in ([(560,205),(600,383),(518,490),(800,231),(489,185),(757,50)] if i==0 else [(381,229),(390,125),(357,198),(399,319),(350,325),(459,342)]):
  direction=rot @ Vector((((x+.5)/900*2-1)*vf*900/506,(1-(y+.5)/506*2)*vf,-1.)).normalized()
  cursor=eye.copy(); hits=[]
  for depth in range(5):
   found,p,normal,index,obj,matrix=scene.ray_cast(deps,cursor,direction,distance=80.)
   if not found: break
   hits.append((obj.name,tuple(round(t,4) for t in p),index,tuple(round(t,3) for t in normal)));cursor=p+direction*.025
  print('CQ_RAY_40',row['file'],x,y,hits)
