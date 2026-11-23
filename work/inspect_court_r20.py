"""Survey candidate resting places around actual existing tree wells."""
import bpy,math
from mathutils import Vector
from pathlib import Path
dg=bpy.context.evaluated_depsgraph_get()
for name,x,y,z in [('upper',-26.36,70.02,30),('court',-9.3,-23.9,16),('upper2',-13,69,30)]:
    print('SITE',name)
    for k in range(16):
        a=math.tau*k/16
        p=Vector((x+1.61*math.cos(a),y+1.61*math.sin(a),z+4))
        hit,where,_,_,obj,_=bpy.context.scene.ray_cast(dg,p,Vector((0,0,-1)),distance=12)
        print(k,round(math.degrees(a)),tuple(round(c,3) for c in where),obj.name if hit else None)
