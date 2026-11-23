"""Original metre-scale batched geometry for the full Chongqing sample."""
from pathlib import Path
from collections import defaultdict
import bpy, math, random
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parent
ORIGIN=Vector((0.,0.,0.))
MATS={}
FONT=None
FONT_BOLD=None
details=None
def world(p): return tuple(Vector(p))
def col(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
def setup(mats):
    global MATS,FONT,FONT_BOLD,details
    MATS=mats
    FONT=bpy.data.fonts.load(str(ROOT/'fonts/NotoSansSC-Regular.otf'))
    FONT_BOLD=bpy.data.fonts.load(str(ROOT/'fonts/NotoSansSC-Bold.otf'))
    details=col('03_Architectural_details')

def solid(key, rgba, rough=.7, metallic=0., emission=0.):
    mat = bpy.data.materials.new('CQ03_' + key)
    mat.use_nodes = True; mat.diffuse_color = (*rgba[:3], 1.)
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgba[:3], 1.)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metallic
    if emission:
        bs.inputs['Emission Color'].default_value = (*rgba[:3],1.)
        bs.inputs['Emission Strength'].default_value = emission
    mat['uv_meters'] = 1.
    MATS[key] = mat
    return mat

class Batch:
    """Metre-scaled batched geometry with physical box-projected UVs."""
    def __init__(self, name, collection, origin=(0,0,0), tangent=(1,0), outward=(0,1)):
        self.name=name; self.collection=collection
        self.origin=ORIGIN + Vector(origin)
        self.u=Vector((*tangent,0)); self.v=Vector((*outward,0))
        self.mirrored=self.u.cross(self.v).z < 0
        self.data=defaultdict(lambda: [[],[],[]])
    def transform(self,p):
        return tuple(self.origin+self.u*p[0]+self.v*p[1]+Vector((0,0,p[2])))
    def mesh(self,vertices,faces,mat,smooth=False):
        vs,fs,ss=self.data[mat]; start=len(vs)
        vs.extend(self.transform(p) for p in vertices)
        fs.extend(tuple(start+i for i in (reversed(f) if self.mirrored else f)) for f in faces)
        ss.extend([smooth]*len(faces))
    def box(self,center,size,mat):
        x,y,z=center; a,b,c=[s/2 for s in size]
        if min(a,b,c)<=0:return
        verts=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
               (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
        self.mesh(verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
    def cylinder(self,a,b,r,mat,segments=12,r2=None):
        a=Vector(a); b=Vector(b); d=b-a
        if d.length < 1e-5:return
        n=d.normalized(); aux=Vector((0,0,1)) if abs(n.z)<.9 else Vector((1,0,0))
        u=n.cross(aux).normalized(); v=n.cross(u).normalized()
        vertices=[]
        for p,rr in ((a,r),(b,r if r2 is None else r2)):
            for i in range(segments):
                t=2*math.pi*i/segments
                vertices.append(tuple(p+rr*(u*math.cos(t)+v*math.sin(t))))
        faces=[tuple(reversed(range(segments))),tuple(range(segments,segments*2))]
        self.mesh(vertices,faces,mat)
        self.mesh(vertices,[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)],mat,True)
    def pipe(self,points,r,mat,segments=10):
        for a,b in zip(points,points[1:]):self.cylinder(a,b,r,mat,segments)
    def quad(self,a,b,c,d,mat):
        self.mesh([a,b,c,d],[(0,1,2,3)],mat)
    def finish(self,bevel=0.):
        objects=[]
        for key,(vs,fs,ss) in self.data.items():
            if not fs:continue
            mesh=bpy.data.meshes.new(self.name+'_'+key)
            mesh.from_pydata(vs,[],fs); mesh.update()
            obj=bpy.data.objects.new(self.name+'_'+key,mesh)
            self.collection.objects.link(obj)
            mat=MATS[key]; mesh.materials.append(mat)
            uv=mesh.uv_layers.new(name='UVMap')
            repeat=float(mat.get('uv_meters',2.))
            for poly in mesh.polygons:
                poly.use_smooth=ss[poly.index]
                n=poly.normal; dominant=max(range(3),key=lambda j:abs(n[j]))
                axes=(1,2) if dominant==0 else ((0,2) if dominant==1 else (0,1))
                for li in poly.loop_indices:
                    p=mesh.vertices[mesh.loops[li].vertex_index].co
                    uv.data[li].uv=(p[axes[0]]/repeat,p[axes[1]]/repeat)
            obj['design_origin']='Original authored district geometry, metres; no surveyed facade claim'
            if bevel:
                mod=obj.modifiers.new('Worn edge highlight','BEVEL'); mod.width=bevel; mod.segments=2
                mod.limit_method='ANGLE'; mod.angle_limit=.62
                mod.affect='EDGES'
                obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
            objects.append(obj)
        return objects

def lettering(body, pos, tangent=(1,0), outward=(0,-1), size=.4, mat='sign_cream', name=None, bold=True):
    curve=bpy.data.curves.new('Type_'+body,'FONT'); curve.body=body
    curve.align_x='CENTER'; curve.align_y='CENTER'; curve.size=size
    curve.extrude=.0015; curve.resolution_u=2; curve.font=FONT_BOLD if bold else FONT
    ob=bpy.data.objects.new(name or 'Type_'+body,curve); details.objects.link(ob)
    basis=Matrix(((tangent[0],0,outward[0]),(tangent[1],0,outward[1]),(0,1,0)))
    ob.rotation_euler=basis.to_euler(); ob.location=world(pos)
    curve.materials.append(MATS[mat])
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH'); ob.select_set(False)
    return ob

def label_local(body,b,loc,size=.3,mat='sign_cream',bold=True):
    p=Vector(b.transform(loc))-ORIGIN
    return lettering(body,p,tuple(b.u)[:2],tuple(b.v)[:2],size,mat,bold=bold)

def panel_wall(b,width,height,holes,mat='tile',thickness=.28):
    """Front facade with real rectangular openings, no solid box behind it."""
    xs=sorted(set([0.,width]+[v for h in holes for v in h[:2]]))
    zs=sorted(set([0.,height]+[v for h in holes for v in h[2:]]))
    for a,c in zip(xs,xs[1:]):
        for lo,hi in zip(zs,zs[1:]):
            midx=(a+c)*.5; midz=(lo+hi)*.5
            if any(x0-1e-6<=midx<=x1+1e-6 and z0-1e-6<=midz<=z1+1e-6 for x0,x1,z0,z1 in holes):continue
            b.box((midx,-thickness*.5,midz),(c-a,thickness,hi-lo),mat)

def add_window(b,u,z,w=1.65,h=1.55,cage=False,seed=0):
    rng=random.Random(seed)
    # Layered reveal: interior curtain, panes, perimeter frame, opening sash.
    b.box((u,-.19,z),(w-.06,.035,h-.06),rng.choice(['glass','glass_blue','glass']))
    for xx in [u-w/2+.035,u+w/2-.035,u]:b.box((xx,-.075,z),(.065,.13,h),'aluminium')
    for zz in [z-h/2+.035,z+h/2-.035]:b.box((u,-.075,zz),(w,.13,.07),'aluminium')
    b.box((u,.06,z-h/2-.07),(w+.22,.35,.14),'concrete')
    b.box((u,-.055,z+.24),(w,.10,.045),'aluminium')
    if seed%4==0:
        b.box((u-w*.27,-.13,z),(.22,.035,h-.1),'curtain')
        b.box((u+w*.26,-.13,z),(.19,.035,h-.1),'curtain')
    if cage:
        depth=.45
        for yy in [.08,depth]:
            for zz in [z-h/2-.10,z+h/2+.10]:b.cylinder((u-w/2-.11,yy,zz),(u+w/2+.11,yy,zz),.023,'frame',8)
        for xx in [u-w/2-.11,u+w/2+.11]:
            for zz in [z-h/2-.1,z+h/2+.1]:b.cylinder((xx,.08,zz),(xx,depth,zz),.022,'frame',8)
        for k in range(11):
            x=u-w/2-.11+(w+.22)*k/10
            b.cylinder((x,depth,z-h/2-.1),(x,depth,z+h/2+.1),.016,'frame',6)
        b.cylinder((u-w/2-.11,depth,z-.12),(u+w/2+.11,depth,z-.12),.019,'frame',8)
        # Thin pitched rain cover, with a narrow rusty edge.
        b.quad((u-w/2-.18,-.03,z+h/2+.18),(u+w/2+.18,-.03,z+h/2+.18),
               (u+w/2+.18,.62,z+h/2+.08),(u-w/2-.18,.62,z+h/2+.08),'painted_metal')
    if seed%3==0:
        add_aircon(b,u+w/2+.62,z-.56)

def add_aircon(b,u,z):
    b.box((u,.26,z),(.88,.51,.57),'offwhite')
    b.box((u,.522,z),(.76,.018,.45),'aluminium')
    b.cylinder((u-.13,.54,z),(u-.13,.562,z),.188,'dark',24)
    for i in range(9):
        yy=z-.2+i*.05
        b.box((u,.573,yy),(.75,.012,.009),'offwhite')
    for xx in [u-.36,u+.34]:
        b.box((xx,.16,z-.34),(.045,.49,.05),'rust')
    b.pipe([(u+.42,.12,z+.04),(u+.56,.10,z+.04),(u+.56,.10,z-.70),(u+.62,-.05,z-.70)],.029,'offwhite')
