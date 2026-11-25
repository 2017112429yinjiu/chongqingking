"""Model the paved school forecourt visible in the two on-site photographs."""
from math import ceil, cos, sin, tau, radians
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector


# Saved positions of the two stand-ins in the parent outer_district layer.
# Match by position so a future reordering of that layer cannot hide a different tree.
PARENT_TREE_ROOTS = [[-144.08095,45.08089],[-127.48580,38.14908]]


class Forecourt:
    def __init__(self, ring, floor, elevation):
        a, b, c, d = np.asarray(ring)
        self.a = a
        self.length = float(np.linalg.norm(b - a))
        self.along = (b - a) / self.length
        self.out = np.array([self.along[1], -self.along[0]])
        if self.out @ (d - a) > 0:
            self.out *= -1
        self.floor = floor
        self.elevation = elevation
        self.depth = 8.0
        self.pits = [(self.length * .39, 2.65), (self.length * .91, 3.35)]
        self.half_pit = .57

    def xy(self, x, y):
        return self.a + x*self.along + y*self.out

    def local(self, q):
        delta = np.asarray(q) - self.a
        return float(delta @ self.along), float(delta @ self.out)

    def height(self, x, y):
        earth = self.elevation(self.xy(x, y))
        # The short porch falls gently away from the threshold. At the garden
        # edge the crossfall returns flush to the existing delivery approach.
        porch = self.floor + .008 - .018*max(0., y)
        t = np.clip((y - 2.) / (self.depth - 2.), 0., 1.)
        t = t*t*(3.-2.*t)
        return float(max(earth+.027, (1.-t)*porch + t*(earth+.036)))

    def xyz(self, x, y, offset=0.):
        return [*self.xy(x, y), self.height(x, y)+offset]

    def surface(self, q):
        return self.height(*self.local(q))


def paving(court, Mesh, mortar, flags, soil):
    base = Mesh("COL_Court_Jinma_Apron")
    finish = Mesh("Court_Jinma_Flagstone")
    xs = [0., court.length]
    ys = [0., court.depth]
    for x,y in court.pits:
        xs.extend((x-court.half_pit,x+court.half_pit))
        ys.extend((y-court.half_pit,y+court.half_pit))
    # Keep the cut stones and earth on the same edges, including half-bond rows.
    def cuts(controls, target):
        edges = sorted(controls)
        return [float(v) for a,b in zip(edges,edges[1:]) for v in np.linspace(a,b,max(1,ceil((b-a)/target))+1)[:-1]] + edges[-1:]
    rows = cuts(ys, .61)
    for row,(y0,y1) in enumerate(zip(rows,rows[1:])):
        vertical = sorted(xs)
        breaks = sorted(set(vertical + [float(x) for x in np.arange(.55 if row%2 else 1.11, court.length, 1.11)
                                        if min(abs(x-u) for u in vertical)>.21]))
        for col,(x0,x1) in enumerate(zip(breaks,breaks[1:])):
            centre = ((x0+x1)/2,(y0+y1)/2)
            pit = any(abs(centre[0]-x)<court.half_pit and abs(centre[1]-y)<court.half_pit for x,y in court.pits)
            def face(mesh,xl,yl,xr,yr,z,material):
                points=[court.xyz(xl,yl,z),court.xyz(xr,yl,z),court.xyz(xr,yr,z),court.xyz(xl,yr,z)]
                if np.cross(np.subtract(points[1],points[0]),np.subtract(points[2],points[0]))[2] < 0:
                    points.reverse()
                mesh.face(points, material)
            face(base,x0,y0,x1,y1,0.,soil if pit else mortar)
            if not pit:
                face(finish,x0+.006,y0+.006,x1-.006,y1-.006,.012,flags[(col*7+row*3+int(x0*4))%len(flags)])
    # Bed the paving on the return at the downhill corner.
    for x in (0.,court.length):
        for y0,y1 in zip(rows,rows[1:]):
            a,b=court.xyz(x,y0),court.xyz(x,y1)
            lower=[[p[0],p[1],court.elevation(p[:2])-.03] for p in (a,b)]
            rise=max(a[2]-lower[0][2], b[2]-lower[1][2])
            courses=max(1,ceil(rise/.19))
            for j in range(courses):
                def edge(p,ground,ratio):
                    return np.array(p) + ratio*(np.array(ground)-p)
                points=[edge(a,lower[0],j/courses),edge(b,lower[1],j/courses),
                        edge(b,lower[1],(j+1)/courses),edge(a,lower[0],(j+1)/courses)]
                base.face(points,mortar)
                inset=np.mean(points,axis=0)
                direction=court.along*(-1. if x==0 else 1.)
                stones=[inset+(p-inset)*.973+np.array([*direction*.012,0.]) for p in points]
                finish.face(stones,flags[j%len(flags)])
                finish.face(list(reversed(stones)),flags[j%len(flags)])
    base.save()
    finish.save()


def entrance_planters(court, Mesh, material):
    library = Path(__file__).resolve().parents[2]/"project/chongqing_blender_v05/scanned_assets/prepared_assets.blend"
    with bpy.data.libraries.load(str(library)) as (_, selected):
        selected.objects = [f"PH_potted_plant_02_base_{i:02}" for i in range(3)]
    # Small pots flank the entrance and the seating end in the 2022 photograph.
    # Keep them against the wall outside the route across the windows.
    collision=Mesh("COLH_Court_Jinma_PlanterBases")
    for i,(station,offset,scale,angle) in enumerate(((.405,.52,.70,40),(.447,.54,.85,165),(.576,.53,.76,80),(.962,.56,1.03,230))):
        x=station*court.length
        root=Vector(court.xyz(x,offset,.009))
        matrix=Matrix.Translation(root) @ Matrix.Rotation(radians(angle),4,'Z') @ Matrix.Scale(scale,4)
        for part,donor in enumerate(selected.objects):
            obj=donor.copy()
            obj.name=f"Court_Jinma_EntryPot_{i+1}_{part}"
            obj.parent=None
            bpy.context.collection.objects.link(obj)
            obj.hide_set(False)
            obj.hide_viewport=False
            obj.hide_render=False
            obj.matrix_world=matrix
        rings=[[matrix @ Vector((r*cos(t),r*sin(t),z)) for t in np.arange(10)*tau/10]
               for r,z in ((.105,0.),(.15,.29))]
        collision.solid(*rings,material)
    collision.save()


def shade_trees(court, Mesh, bark):
    library = Path(__file__).resolve().parents[2]/"project/chongqing_blender_v05/scanned_assets/prepared_assets.blend"
    names = [f"PH_tree_small_02_medium_{i:02}" for i in range(3)]
    with bpy.data.libraries.load(str(library)) as (_, selected):
        selected.objects = names
    trunk = selected.objects[0]
    vertices = np.array([tuple(v.co) for v in trunk.data.vertices])
    foot = vertices[vertices[:,2] < .055,:2]
    centre = (foot.max(axis=0) + foot.min(axis=0)) / 2
    proxy = Mesh("COLH_Court_Jinma_Trunks")
    trees = []
    for i,((x,y),angle,scale) in enumerate(zip(court.pits,(32.,166.),((2.85,2.35,2.10),(2.55,2.40,2.24)))):
        origin = Vector(court.xyz(x,y,-.03))
        transform = (Matrix.Translation(origin) @ Matrix.Rotation(radians(angle),4,'Z')
                     @ Matrix.Diagonal(Vector((*scale,1))) @ Matrix.Translation(Vector((-centre[0],-centre[1],0.))))
        for part,source in enumerate(selected.objects):
            tree = source.copy()
            tree.name = f"Court_Jinma_Tree_{i+1}_{part}"
            tree.parent = None
            bpy.context.collection.objects.link(tree)
            tree.hide_set(False)
            tree.hide_render = False
            tree.hide_viewport = False
            tree.matrix_world = transform
        # The photos show an upper fork carrying foliage on both sides of the
        # trunk. Rotate one linked crown around a scanned branch junction.
        joint = np.median(vertices[np.abs(vertices[:,2]-1.7)<.08],axis=0)
        fork = (transform @ Matrix.Translation(Vector(joint)) @ Matrix.Rotation(radians(119.-15*i),4,'Z')
                @ Matrix.Diagonal(Vector((.93,.96,.90,1.))) @ Matrix.Translation(-Vector(joint)))
        for part in (1,2):
            crown = selected.objects[part].copy()
            crown.name = f"Court_Jinma_Crown_{i+1}_{part}"
            crown.parent=None
            bpy.context.collection.objects.link(crown)
            crown.hide_set(False)
            crown.hide_render=False
            crown.hide_viewport=False
            crown.matrix_world=fork
        # Ground the physics trunk on the scan itself. Limit collision to the
        # pedestrian envelope; the individual leaves and twigs remain visual.
        rings=[]
        for h in (.05,.52,1.05):
            band=vertices[np.abs(vertices[:,2]-h)<.065,:2]
            middle=np.median(band,axis=0)
            radius=float(np.median(np.linalg.norm(band-middle,axis=1)))
            ring=[transform @ Vector((*(middle + radius*np.array([cos(t),sin(t)])),h if len(rings) else -.04))
                  for t in np.arange(8)*tau/8]
            rings.append(ring)
        for low,high in zip(rings,rings[1:]):
            proxy.solid(low,high,bark)
        trees.append({"root":[*origin],"height_m":round(float(max(v.co.z for v in selected.objects[2].data.vertices)*scale[2]),2)})
    proxy.save()
    return trees
