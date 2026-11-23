"""Tools returned to a fixed place along the repairer's wall after use."""
import math
from mathutils import Vector
def build(tube,box,ground):
    model='Yard20_RepairTools';points=[]
    def pipe(a,b,r,mat,segments=12):tube(model,a,b,r,mat,segments)
    def chain(path,r,mat):
        for a,b in zip(path,path[1:]):pipe(a,b,r,mat,8)
    x,y=-62.32,-54.32
    for sx in [-.115,.115]:
        for sy in [-.049,.049]:
            xx,yy=x+sx,y+sy;z=ground(xx,yy)
            box(model,(xx,yy,z+.009),(.041,.035,.020),'rubber');points.append((xx,yy,z))
    floor=max(p[2] for p in points)
    for side in (-1,1):pipe((x-.121,y+side*.05,floor+.024),(x+.121,y+side*.05,floor+.024),.014,'rail')
    box(model,(x,y,floor+.035),(.16,.121,.031),'rail')
    pipe((x,y,floor+.04),(x,y,floor+.48),.029,'green',20)
    for height,r,mat in [(.046,.036,'rail'),(.077,.032,'galv'),(.443,.031,'oxide'),(.465,.034,'galv')]:
        pipe((x,y,floor+height),(x,y,floor+height+.015),r,mat,18)
    pipe((x,y,floor+.486),(x,y,floor+.658),.012,'chrome')
    pipe((x-.12,y,floor+.664),(x+.12,y,floor+.664),.014,'rail')
    for sign in [-1,1]:pipe((x+sign*.06,y,floor+.664),(x+sign*.132,y,floor+.664),.020,'rubber')
    hose=[(0,.0,.095),(.045,-.025,.098),(.088,-.042,.139),(.116,-.043,.272),(.130,-.034,.432),(.122,-.025,.587),(.096,-.013,.639),(.064,0,.648),(.062,.018,.610),(.089,.029,.527),(.10,.028,.423)]
    chain([(x+a,y+b,floor+c) for a,b,c in hose],.008,'rubber')
    pipe((x+.10,y+.028,floor+.423),(x+.093,y+.031,floor+.395),.013,'chrome')
    # Spare tyre and folded inner tube hang from wall plugs at different heights.
    for cx,height,rx,rz,rad in [(-62.94,.96,.317,.323,.023),(-63.37,.88,.098,.215,.015)]:
        z=ground(cx,-54.22)+height
        top=z+rz;front=-54.119
        box(model,(cx,-54.016,top+.026),(.046,.035,.085),'oxide')
        chain([(cx,-54.033,top+.04),(cx,front-.016,top-.028),(cx,front-.024,top+.012)],.012,'rail')
        path=[]
        for j in range(73):
            a=2*math.pi*j/72;path.append((cx+rx*math.sin(a),front+.010*math.cos(a*2),z+rz*math.cos(a)))
        chain(path,rad,'rubber')
        if rx>.2:
            for j in range(32):
                a=2*math.pi*j/32
                p=Vector((cx+rx*math.sin(a),front-.018+.01*math.cos(2*a),z+rz*math.cos(a)))
                side=Vector((math.cos(a),0,-math.sin(a)))*.008
                pipe(tuple(p-side),tuple(p+side),.0035,'saddle',5)
    return points
