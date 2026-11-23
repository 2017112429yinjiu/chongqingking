from pathlib import Path
from collections import defaultdict
import json,math,re,bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parent
project=root.parents[1]/'project/chongqing_godot_v05'
scene=bpy.context.scene
def extent(o):
    pts=[o.matrix_world@Vector(x) for x in o.bound_box]
    return tuple(tuple(fn(v[i] for v in pts) for i in range(3)) for fn in (min,max))
class Surfaces:
    def __init__(self,obs):
        self.cells=defaultdict(list);self.trees={};self.deps=bpy.context.evaluated_depsgraph_get()
        for o in obs:
            low,high=extent(o)
            for x in range(math.floor(low[0]/8),math.floor(high[0]/8)+1):
                for y in range(math.floor(low[1]/8),math.floor(high[1]/8)+1):
                    self.cells[(x,y)].append((low,high,o))
    def tree(self,o):
        if o not in self.trees:
            # Work in world metres for both distance tests and slope normals.
            self.trees[o]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons],all_triangles=False)
        return self.trees[o]
    def down(self,x,y,top=65,depth=80):
        results=[]
        for low,high,o in self.cells.get((math.floor(x/8),math.floor(y/8)),[]):
            if low[0]-.0001<=x<=high[0]+.0001 and low[1]-.0001<=y<=high[1]+.0001 and low[2]<=top:
                h,n,i,d=self.tree(o).ray_cast((x,y,top),(0,0,-1),depth)
                if h is not None and abs(n.z)>.48:results.append((h.z,o.name,n if n.z>0 else -n))
        return sorted(results,key=lambda r:-r[0])
def visible_ground(o):
    n=o.name
    return o.type=='MESH' and not o.hide_render and n.startswith(('COL_Terrain','COL_Walk_','COL_Road_','COL_Community','COL_Court','COL_R19_Stair_retaining','R21_Dressed','COL_R23_Nanqu','COL_R23_PathFoundations','COL_R24_MarketStairs','COL_R21_Footing','Walk_details_','COL_R24_Stone','COL_R24_Median','COL_Stairside','Outer_ground','COL_Ground','COL_R20_Upper','COL_R24_LinkDeck')) and not any(k in n.lower() for k in ('rail','fence','paint_line','lamp','garden','post','planter'))
ground=Surfaces([o for o in scene.objects if visible_ground(o)])
def floors(x,y,hi=63):
    return ground.down(x,y,hi)
def tread_rows(name):
    ob=scene.objects[name];faces=[p for p in ob.data.polygons if p.normal.z>.998]
    rows=[]
    for a,b in zip(faces[::2],faces[1::2]):
        points={tuple(round(k,5) for k in (ob.matrix_world@ob.data.vertices[v].co)) for face in (a,b) for v in face.vertices}
        if len(points)!=4:continue
        c=sum((Vector(p) for p in points),Vector((0,0,0)))/4
        ring=sorted([Vector(p) for p in points],key=lambda p:math.atan2(p.y-c.y,p.x-c.x))
        rows.append((c,ring))
    return rows

