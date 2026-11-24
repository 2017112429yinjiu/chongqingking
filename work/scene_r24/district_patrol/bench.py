from pathlib import Path
import sys,bpy,bmesh
from mathutils import Vector
here=Path(__file__).resolve().parent

def bench_parts(obj,bounds=(-75,-70,-37,-33)):
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    free=set(bm.verts)
    groups=[]
    while free:
        part=[free.pop()]
        for v in part:
            for e in v.link_edges:
                other=e.other_vert(v)
                if other in free:
                    free.remove(other)
                    part.append(other)
        centre=sum((v.co for v in part),Vector())/len(part)
        if bounds[0]<centre.x<bounds[1] and bounds[2]<centre.y<bounds[3]:
            groups.append((part,centre))
    return bm,groups

if '--bench-survey' in sys.argv:
    for key in ('frame','timber'):
        ob=bpy.context.scene.objects['Street_small_furniture_'+key]
        bm,groups=bench_parts(ob)
        for vs,c in groups:
            print('BENCH',key,list(c),[round(min(v.co[i] for v in vs),3) for i in range(3)],
                  [round(max(v.co[i] for v in vs),3) for i in range(3)])
        bm.free()

if '--posts' in sys.argv:
    for key in ('frame','paint_yellow'):
        ob=bpy.context.scene.objects['Street_small_furniture_'+key]
        bm,groups=bench_parts(ob,(14,18,-65,-62))
        for vs,c in groups:
            print('POST',key,list(c),[round(min(v.co[i] for v in vs),3) for i in range(3)],
                  [round(max(v.co[i] for v in vs),3) for i in range(3)])
        bm.free()

def move_bench(scene,ground,finish):
    dx,dy=2.18,-1.08
    x,y=-72.+dx,-35.+dy
    floor=ground.down(x,y,15.,3.)[0][0]
    dz=floor+.46-14.02628
    parts=0
    for key in ('frame','timber'):
        obj=scene.objects['Street_small_furniture_'+key]
        bm,groups=bench_parts(obj)
        for vs,c in groups:
            for v in vs:
                foot=key=='frame' and v.co.z<13.74
                v.co+=Vector((dx,dy,dz))
                if foot:v.co.z=ground.down(v.co.x,v.co.y,15.,3.)[0][0]-.003
            parts+=1
        finish(obj,bm)
    assert parts==9
    return {'centre':[x,y,floor],'pieces':parts}
