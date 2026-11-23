"""Individually art-directed architecture for the 200 m Chongqing district.

Only source plan coordinates are geographic. Floor heights, facades, roof forms,
shop names, room fragments and infill are original scene design, not a survey.
The real photographs are visual references, never extracted texture material.

Public entry: build(ctx) -> {buildings, lights, views, excluded, checks}
ctx: Batch, col, MATS, lettering, ground_height, ROOT. Blender Z is up; metres.
All facade coordinates are collected into one set of mesh batches per building
rather than creating an object for every window or iron bar.
"""
from pathlib import Path
import math
import json
import random
import hashlib
import os
import interior_scenes as interiors
import interior_domains as room_domains

# Public project v05 retains the source footprint, storeys and traversable
# openings while replacing placeholder domestic contents with real components.
REVISION = int(os.environ.get('CQ_REVISION', '13'))

# Distinct compositions, not one repeated house mesh. These are art-direction
# choices, not assertions about the measured appearance of the source buildings.
PROFILES = {
    809889603: dict(name='North skyline fragment', style='contemporary', wall='plaster_grey', floors=7, fh=3.10, roof='flat', bay=3.25),
    809889604: dict(name='North cream residence', style='cream_residence', wall='tile_cream', floors=6, fh=3.12, roof='flat', bay=3.45, sign='北坡居民楼'),
    809889622: dict(name='West workers courtyard', style='workers', wall='plaster_ochre', floors=5, fh=3.02, roof='flat', bay=3.05, sign='山城里'),
    809889623: dict(name='South market tenement', style='market', wall='tile', floors=4, fh=3.15, roof='terrace', bay=3.20, sign='老街杂货'),
    809889624: dict(name='Eastern stepped courtyard', style='courtyard', wall='brick_dark', floors=3, fh=3.75, roof='flat', bay=3.10, sign='坡上书屋'),
    809889625: dict(name='Outside eastern tower', style='contemporary', wall='tile_cream', floors=37, fh=3.1, roof='flat', bay=3.10),
    809889626: dict(name='Grey brick tea house', style='heritage', wall='brick_dark', floors=3, fh=3.55, roof='gable', bay=3.45, sign='巷口茶馆'),
    809889627: dict(name='East blue tile apartments', style='blue_apartments', wall='tile_blue', floors=7, fh=3.05, roof='terrace', bay=3.10, sign='青石里 6 栋'),
    809889628: dict(name='Hilltop former clinic', style='clinic', wall='plaster', floors=2, fh=3.85, roof='flat', bay=3.70, sign='山城卫生站'),
    809889629: dict(name='Upper artisan terrace', style='artisan', wall='brick', floors=2, fh=3.70, roof='sawtooth', bay=3.80, sign='坡上手作'),
    809889630: dict(name='Northern concrete apartment wings', style='contemporary', wall='plaster_grey', floors=8, fh=3.12, roof='flat', bay=3.15, sign='北街社区'),
    1335306665: dict(name='Ochre civic courtyard', style='civic', wall='plaster_ochre', floors=4, fh=3.62, roof='flat', bay=3.60, sign='山城里文化室'),
    1335306666: dict(name='Grey masonry guest house', style='heritage', wall='brick_dark', floors=3, fh=3.30, roof='gable', bay=3.05, sign='梧桐小院'),
    1335306667: dict(name='Brick corner residence', style='brick_home', wall='brick', floors=2, fh=3.45, roof='gable', bay=3.15, sign='石阶人家'),
    1413081560: dict(name='Northwestern tile walkups', style='old_tile', wall='tile', floors=5, fh=3.02, roof='terrace', bay=2.95, sign='山城巷 12 号'),
    1413081561: dict(name='Western restored masonry block', style='restored', wall='plaster_grey', floors=4, fh=3.45, roof='flat', bay=3.45, sign='西坡人家'),
}

INFILL = [
    dict(id='A01', bounds=(-33,-73,-20,-62), name='Noodle corner', style='noodle', wall='plaster_ochre', floors=2, fh=3.50, roof='gable', bay=3.00, sign='梯坎小面', secondary='老汤抄手'),
    dict(id='A02', bounds=(-70,-54,-55,-42), name='Cycle repair shophouse', style='repair', wall='brick', floors=2, fh=3.40, roof='shed', bay=3.20, sign='老杨修车', secondary='配钥匙  补胎'),
    dict(id='A03', bounds=(-94,-31,-78,-9), name='Blue corner walkup', style='blue_apartments', wall='tile_blue', floors=4, fh=3.12, roof='terrace', bay=3.25, sign='南坡居民楼'),
    dict(id='A04', bounds=(-66,-30,-53,-9), name='Grey courtyard residence', style='courtyard_home', wall='plaster_grey', floors=3, fh=3.45, roof='gable', bay=3.25, sign='山城里小院'),
    dict(id='A05', bounds=(-46,-49,-28,-28), name='Mixed shop apartment', style='market', wall='tile_cream', floors=3, fh=3.45, roof='terrace', bay=3.40, sign='香满坡家常菜', secondary='梯坎便利'),
    dict(id='A06', bounds=(-11,-49,4,-32), name='Brick print workshop', style='workshop', wall='brick', floors=2, fh=4.00, roof='sawtooth', bay=3.45, sign='山城印务', secondary='印刷  装订'),
    dict(id='A07', bounds=(4,8,23,17), name='Community service house', style='service', wall='plaster', floors=2, fh=3.65, roof='flat', bay=3.50, sign='社区服务站', secondary='快递驿站'),
]
SPINE = [(16,-66),(-20,-52),(-20,-30),(-18,-8),(-18,14),(-40,38),(-37,43),(-33.1,50),(-28.7,57),(-25,64),(-17,77),(-27,90)]


def _add(a,b): return tuple(x+y for x,y in zip(a,b))
def _sub(a,b): return tuple(x-y for x,y in zip(a,b))
def _mul(a,s): return tuple(x*s for x in a)
def _dot(a,b): return sum(x*y for x,y in zip(a,b))
def _cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _norm(a):
    n=math.sqrt(_dot(a,a)); return _mul(a,1/n) if n>1e-9 else (0,0,1)
def _area(p): return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2

def _centroid(p):
    a=_area(p)
    if abs(a)<1e-6:return (sum(x for x,y in p)/len(p),sum(y for x,y in p)/len(p))
    sx=sy=0
    for v,w in zip(p,p[1:]+p[:1]):
        c=v[0]*w[1]-w[0]*v[1];sx+=(v[0]+w[0])*c;sy+=(v[1]+w[1])*c
    return sx/(6*a),sy/(6*a)

def _inside(p,poly):
    flag=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if ((a[1]>p[1])!=(b[1]>p[1])) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]: flag=not flag
    return flag

def _segdist(p,a,b):
    vx,vy=b[0]-a[0],b[1]-a[1];vv=vx*vx+vy*vy
    t=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/vv)) if vv else 0
    return math.hypot(p[0]-a[0]-t*vx,p[1]-a[1]-t*vy)

def _clean(poly):
    p=[]
    for v in poly:
        q=(round(float(v[0]),6),round(float(v[1]),6))
        if not p or math.dist(q,p[-1])>.025:p.append(q)
    if len(p)>1 and math.dist(p[0],p[-1])<.025:p.pop()
    if len(p)>=3 and _area(p)<0:p.reverse()
    return p

def _clip(poly):
    p=list(poly)
    for axis,bound,positive in [(0,-100,True),(0,100,False),(1,-100,True),(1,100,False)]:
        out=[]
        if not p:return []
        for a,b in zip(p,p[1:]+p[:1]):
            ia=a[axis]>=bound if positive else a[axis]<=bound
            ib=b[axis]>=bound if positive else b[axis]<=bound
            if ia:out.append(a)
            if ia!=ib:
                t=(bound-a[axis])/(b[axis]-a[axis]);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
        p=out
    return _clean(p)

def _triangles(poly):
    """Ear-clipped concave cap, falling back to Blender's robust tessellator."""
    try:
        from mathutils import Vector
        from mathutils.geometry import tessellate_polygon
        vv=[Vector((x,y,0)) for x,y in poly]
        ix={tuple(v):i for i,v in enumerate(vv)}
        tris=[tuple(v if isinstance(v,int) else ix[tuple(v)] for v in t) for t in tessellate_polygon([vv])]
        # Clipping concave northern footprints may introduce collinear boundary
        # vertices. Do not export the zero-area triangles a tessellator can emit.
        good=[]
        for t in tris:
            a,b,c=[poly[i] for i in t]
            signed=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            if abs(signed)>1e-8:good.append(t if signed>0 else tuple(reversed(t)))
        return good
    except ImportError:
        ids=list(range(len(poly)));out=[];guard=0
        def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        while len(ids)>3 and guard<len(poly)**2:
            guard+=1;found=False
            for j,b in enumerate(ids):
                a,c=ids[j-1],ids[(j+1)%len(ids)]
                if cross(poly[a],poly[b],poly[c])<=1e-8:continue
                def in_tri(q):return all(v>=-1e-8 for v in [cross(poly[a],poly[b],q),cross(poly[b],poly[c],q),cross(poly[c],poly[a],q)])
                if any(in_tri(poly[k]) for k in ids if k not in [a,b,c]):continue
                out.append((a,b,c));ids.pop(j);found=True;break
            if not found:break
        if len(ids)==3:out.append(tuple(ids))
        return out


class Frame:
    """Local facade drawing into one global building batch."""
    def __init__(self,batch,origin=(0,0,0),u=(1,0),v=(0,1)):
        self.b=batch;self.o=origin;self.u=u;self.v=v;self.mirror=u[0]*v[1]-u[1]*v[0]<0
    def transform(self,p):
        return (self.o[0]+self.u[0]*p[0]+self.v[0]*p[1],self.o[1]+self.u[1]*p[0]+self.v[1]*p[1],self.o[2]+p[2])
    def mesh(self,vs,fs,mat,smooth=False):
        self.b.mesh([self.transform(p) for p in vs],[tuple(reversed(f)) if self.mirror else f for f in fs],mat,smooth)
    def box(self,p,size,mat):
        x,y,z=p;a,b,c=[s/2 for s in size]
        if min(a,b,c)<=0:return
        self.mesh([(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
    def quad(self,a,b,c,d,mat):self.mesh([a,b,c,d],[(0,1,2,3)],mat)
    def decal(self,vertices,mat,uvs):
        """One authored decal with local image UVs, still in the material batch."""
        face_index=len(self.b.data[mat][1])
        self.mesh(vertices,[tuple(range(len(vertices)))],mat)
        if not hasattr(self.b,'_facade_uvs'):self.b._facade_uvs={}
        if self.mirror ^ bool(getattr(self.b,'mirrored',False)):uvs=list(reversed(uvs))
        self.b._facade_uvs.setdefault(mat,[]).append((face_index,uvs))
    def cylinder(self,a,b,r,mat,segments=8,r2=None):
        n=_norm(_sub(b,a));aux=(0,0,1) if abs(n[2])<.9 else (1,0,0);u=_norm(_cross(n,aux));v=_cross(n,u)
        vs=[]
        for p,rr in [(a,r),(b,r if r2 is None else r2)]:
            for i in range(segments):
                theta=2*math.pi*i/segments;vs.append(_add(p,_mul(_add(_mul(u,math.cos(theta)),_mul(v,math.sin(theta))),rr)))
        fs=[tuple(reversed(range(segments))),tuple(range(segments,2*segments))]+[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
        self.mesh(vs,fs,mat,True)
    def pipe(self,points,r,mat,segments=8):
        for a,b in zip(points,points[1:]):self.cylinder(a,b,r,mat,segments)


def _thin_panel(f,vertices,top,bottom,thickness):
    """Roof/sunshade skin with separate underside and closed edge thickness."""
    lower=[(x,y,z-thickness) for x,y,z in vertices]
    n=len(vertices)
    f.mesh(vertices,[tuple(range(n))],top)
    f.mesh(lower,[tuple(reversed(range(n)))],bottom)
    for i in range(n):
        j=(i+1)%n
        f.quad(vertices[i],lower[i],lower[j],vertices[j],bottom)


def _dedupe_same_faces(batch):
    # Exact, same-winding duplicates can arise where architectural trim meets.
    # Retain opposite-facing surfaces and never merge nearby facade layers.
    removed=0
    for mat,(vs,faces,smooth) in batch.data.items():
        seen=set();keep=[];flags=[];remap={}
        for old_index,(face,flag) in enumerate(zip(faces,smooth)):
            coords=tuple(tuple(round(v,5) for v in vs[i]) for i in face)
            key=min(coords[k:]+coords[:k] for k in range(len(coords)))
            if key in seen:
                removed+=1;continue
            remap[old_index]=len(keep)
            seen.add(key);keep.append(face);flags.append(flag)
        batch.data[mat]=[vs,keep,flags]
        overrides=getattr(batch,'_facade_uvs',{})
        if mat in overrides:
            overrides[mat]=[(remap[index],uvs) for index,uvs in overrides[mat] if index in remap]
    return removed


def _apply_facade_uvs(batch,objects):
    # Called before the export triangulation. Only authored weathering polygons
    # override their UVs; every brick/plaster surface keeps metre-scale mapping.
    overrides=getattr(batch,'_facade_uvs',{})
    for ob in objects or []:
        key=ob.name[len(batch.name)+1:]
        if key not in overrides:continue
        layer=ob.data.uv_layers.active
        for index,uvs in overrides[key]:
            poly=ob.data.polygons[index]
            if len(poly.loop_indices)!=len(uvs):continue
            for li,uv in zip(poly.loop_indices,uvs):layer.data[li].uv=uv


def _damp_decal(f,x,z,w,h,seed,mat='grime_streak'):
    rng=random.Random(seed+933);u0=rng.uniform(0,.20);u1=rng.uniform(.78,1.)
    v0=rng.uniform(0,.16);v1=rng.uniform(.84,1.)
    if REVISION>=7:
        # The authored image has a transparent border. Cropping that border
        # produced a visible rectangular stamp in the second engine review.
        u0,u1,v0,v1=0.,1.,0.,1.
    if seed%2:u0,u1=u1,u0
    f.decal([(x-w/2,.010,z-h/2),(x-w/2,.010,z+h/2),(x+w/2,.010,z+h/2),(x+w/2,.010,z-h/2)],mat,[(u0,v0),(u0,v1),(u1,v1),(u1,v0)])


def _surface_patch(f,x,z,w,h,seed,material='concrete'):
    """Irregular repaired/eroded patch, rather than a wall-sized noise mask."""
    rng=random.Random(seed+1401);n=10;verts=[]
    if REVISION>=7:
        # Broken tile edges are angular, very local and follow the masonry;
        # the former large circular chips read as pasted brown stones.
        perimeter=[(-.50,-.36),(-.40,-.50),(-.08,-.47),(.03,-.36),(.33,-.50),(.50,-.27),(.42,.08),(.50,.42),(.16,.50),(-.12,.37),(-.50,.43),(-.44,.07)]
        verts=[(x+xx*w,.006,z+zz*h) for xx,zz in perimeter]
        f.mesh(verts,[tuple(reversed(range(len(verts))))],material)
        return
    for i in range(n):
        a=i*math.tau/n;r=rng.uniform(.78,1.)
        verts.append((x+math.cos(a)*w/2*r,.006,z+math.sin(a)*h/2*r))
    f.mesh(verts,[tuple(reversed(range(n)))],material)


def _facade_wear(ctx,f,width,height,holes,seed,style):
    rng=random.Random(seed+1529)
    count=min(2,max(1,int(width/8))) if REVISION>=7 else max(2,int(width/3.5))
    for k in range(count):
        x=rng.uniform(.32,max(.33,width-.32))
        if REVISION>=7:x=(.26 if k%2==0 else width-.26)+rng.uniform(-.065,.065)
        pos=f.transform((x,.015,0));ground=ctx.ground_height(pos[0],pos[1])-f.o[2]
        zz=max(.24,ground+.30)+rng.uniform(0,.32)
        ww=rng.uniform(.18,.62);hh=rng.uniform(.19,.58)
        if REVISION>=7:
            zz=max(.11,ground+.14)+rng.uniform(0,.13)
            ww=rng.uniform(.10,.22);hh=rng.uniform(.06,.14)
        if zz+hh/2>height-.3:continue
        if any(not(x+ww/2<a-.12 or x-ww/2>b+.12 or zz+hh/2<lo-.12 or zz-hh/2>hi+.12) for a,b,lo,hi in holes):continue
        if style not in ('contemporary','clinic','service'):
            _surface_patch(f,x,zz,ww,hh,seed+k,'plaster' if REVISION>=7 else ('concrete' if k%3 else 'plaster_grey'))
        if 'moss_grime' in ctx.MATS:
            _damp_decal(f,x,max(.15,ground+.16) if REVISION>=7 else max(.22,ground+.24),min(.55,ww*2.4) if REVISION>=7 else min(1.25,ww*2.4),.24 if REVISION>=7 else .42,seed+k*17,'moss_grime')
    # Discrete maintenance plaster around utility entries has a different
    # scale and placement on every house, and is kept away from open doors.
    if width>8 and style not in ('contemporary','civic','clinic'):
        x=.24 if seed%2 else width-.24
        _surface_patch(f,x,2.28,.11 if REVISION>=7 else .29,.18 if REVISION>=7 else .58,seed+86,'plaster')


def _label(ctx,frame,text,loc,size=.35,mat='sign_cream',bold=True):
    p=frame.transform(loc)
    ob=ctx.lettering(text,p,tangent=frame.u,outward=frame.v,size=size,mat=mat,bold=bold)
    # Blender font conversion can leave coplanar collinear fill triangles.
    # Removing those preserves the glyph while avoiding glTF normal warnings.
    if getattr(ob,'type',None)=='MESH':
        import bmesh
        for _ in range(3):
            ob.data.update()
            bad=[p.index for p in ob.data.polygons if p.area<1e-10]
            if not bad:break
            bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table()
            bmesh.ops.delete(bm,geom=[bm.faces[i] for i in bad],context='FACES_ONLY')
            bm.to_mesh(ob.data);bm.free();ob.data.update()
    return ob


def _wall(f,width,height,holes,material,foundation=0.0):
    """Facade sheet split around actual apertures, with 24cm reveals."""
    cuts=sorted(set([foundation,0,height]+[round(z,5) for h in holes for z in h[2:]]))
    for za,zb in zip(cuts,cuts[1:]):
        if zb-za<1e-5:continue
        mid=(za+zb)/2
        occupied=sorted([(max(0,a),min(width,b)) for a,b,lo,hi in holes if lo-1e-5<mid<hi+1e-5])
        pos=0
        for a,b in occupied+[(width,width)]:
            if a>pos+1e-5:
                f.quad((pos,0,za),(pos,0,zb),(a,0,zb),(a,0,za),material)
                f.quad((pos,-.24,za),(a,-.24,za),(a,-.24,zb),(pos,-.24,zb),material)
            pos=max(pos,b)
    # Aperture reveals, no intersecting opaque wall behind the panes.
    for a,b,lo,hi in holes:
        f.quad((a,0,lo),(a,-.24,lo),(a,-.24,hi),(a,0,hi),'concrete')
        f.quad((b,0,lo),(b,0,hi),(b,-.24,hi),(b,-.24,lo),'concrete')
        f.quad((a,0,hi),(a,-.24,hi),(b,-.24,hi),(b,0,hi),'concrete')
        if lo>.02:f.quad((a,0,lo),(b,0,lo),(b,-.24,lo),(a,-.24,lo),'concrete')


def _aircon(f,u,z,seed):
    """Separate condenser casing, recessed fan and grille, not a white block."""
    rng=random.Random(seed+713)
    wide=.76+(seed%4)*.055;high=.51+(seed%3)*.025
    body='offwhite' if seed%3 else 'painted_metal'
    f.box((u,.31,z),(wide,.45,high),body)
    f.box((u,.537,z),(wide-.08,.016,high-.07),'aluminium')
    fx=u-wide*.13;fz=z+.015;rad=high*.34
    f.cylinder((fx,.548,fz),(fx,.559,fz),rad,'dark',20)
    # Blades and a centre hub remain visible behind the actual protective wires.
    for k in range(5):
        a=k*math.tau/5
        vs=[(fx+math.cos(a)*.025,.562,fz+math.sin(a)*.025),
            (fx+math.cos(a+.12)*rad*.90,.562,fz+math.sin(a+.12)*rad*.90),
            (fx+math.cos(a+.55)*rad*.82,.562,fz+math.sin(a+.55)*rad*.82)]
        f.mesh(vs,[(0,2,1)],'painted_metal')
    f.cylinder((fx,.565,fz),(fx,.577,fz),.035,'aluminium',10)
    for rr in [rad*.40,rad*.73,rad*.99]:
        ring=[(fx+math.cos(k*math.tau/20)*rr,.59,fz+math.sin(k*math.tau/20)*rr) for k in range(21)]
        f.pipe(ring,.0045,'offwhite',5)
    for k in range(8):
        a=k*math.pi/8
        f.cylinder((fx-math.cos(a)*rad,.592,fz-math.sin(a)*rad),(fx+math.cos(a)*rad,.592,fz+math.sin(a)*rad),.0035,'aluminium',5)
    for k in range(7):f.box((u+wide*.31,.558,z-high*.32+k*high*.10),(wide*.16,.022,.010),'dark')
    # Two distinct wall brackets, rusty horizontal feet, mounting washers.
    for x in [u-wide*.33,u+wide*.33]:
        f.box((x,.19,z-high/2-.045),(.040,.57,.042),'rust')
        f.box((x,.04,z-high/2+.11),(.040,.045,.36),'frame')
        f.pipe([(x,.04,z-high/2-.18),(x,.43,z-high/2-.045)],.014,'frame',6)
    for x in [u-wide*.42,u+wide*.42]:
        for zz in [z-high*.36,z+high*.36]:f.cylinder((x,.552,zz),(x,.565,zz),.010,'frame',6)
    f.box((u+wide*.28,.57,z-high*.33),(.13,.012,.055),'paper')
    run=.40+(seed%4)*.11
    f.pipe([(u+wide/2,.19,z+.06),(u+wide/2+.13,.17,z+.02),(u+wide/2+.17,.11,z-run),(u+wide/2+.28,.035,z-run-.10)],.021,'offwhite',8)
    # Fine uninsulated drain follows a different path from the insulated line.
    f.pipe([(u+wide*.35,.08,z-high/2),(u+wide*.43,.07,z-high/2-.24),(u+wide*.43,.05,z-high/2-.46)],.008,'painted_metal',6)


def _curtain(f,x,y,z,w,h,seed,material='curtain',detail=None):
    """Thin closed fabric mesh: rounded pleats and an uneven relaxed hem."""
    rng=random.Random(seed+859);cols=max(10,int(w/.028))
    # First two street-facing storeys keep the complete cloth profile. Above
    # that, removing redundant vertical segments leaves every horizontal pleat
    # intact and preserves the room's geometry, thickness and parallax.
    rows=2 if REVISION>=6 and z>7.0 else 4
    phase=rng.uniform(0,math.tau);pleats=max(3,int(w/.09))
    if REVISION>=8:
        # Reinvest redundant high-storey cloth subdivisions into readable
        # near-street furniture; every curtain still has a real folded surface.
        tier=(2 if z<7 else 0) if detail is None else detail
        cols=max(10 if tier>1 else 8,int(w/(.035 if tier>1 else .05)))
        rows=3 if tier>1 else (2 if tier else 1)
        pleats=max(2,int(w/.10))
    vs=[]
    for back in [False,True]:
        for row in range(rows+1):
            t=row/rows
            for col in range(cols+1):
                s=col/cols
                xx=x-w/2+w*s+(1-t)*math.sin(s*math.pi)*.018
                yy=y+math.sin(s*math.tau*pleats+phase)*.030-(.012 if back else 0)
                zz=z-h/2+h*t+(1-t)*(.022*math.sin(s*9+phase)+.012*math.sin(s*23))
                vs.append((xx,yy,zz))
    n=(cols+1)*(rows+1);faces=[]
    for row in range(rows):
        for col in range(cols):
            a=row*(cols+1)+col;b=a+cols+1
            faces.append((a,b,b+1,a+1));faces.append((a+n,a+1+n,b+1+n,b+n))
    for col in range(cols):
        a=col;b=rows*(cols+1)+col
        faces.extend([(a,a+1,a+1+n,a+n),(b,b+n,b+1+n,b+1)])
    for row in range(rows):
        a=row*(cols+1);b=a+cols+1;c=a+cols;d=b+cols
        faces.extend([(a,a+n,b+n,b),(c,d,d+n,c+n)])
    f.mesh(vs,faces,material,True)


def _curtain_material(seed):
    if REVISION<6:return 'curtain'
    r=random.Random(seed+52707).random()
    if r<.34:return 'curtain_linen'
    if r<.65:return 'curtain_beige'
    if r<.90:return 'curtain_sage'
    return 'curtain'


def _grid_quad(f,a,b,c,d,material,spacing):
    """The actual room plane, subdivided for contact and sky-visibility samples."""
    nx=max(1,int(math.ceil(math.dist(a,b)/spacing)))
    ny=max(1,int(math.ceil(math.dist(a,d)/spacing)))
    vs=[];fs=[]
    for iy in range(ny+1):
        v=iy/ny
        for ix in range(nx+1):
            u=ix/nx
            vs.append(tuple(a[k]*(1-u)*(1-v)+b[k]*u*(1-v)+c[k]*u*v+d[k]*(1-u)*v for k in range(3)))
    for iy in range(ny):
        for ix in range(nx):
            j=iy*(nx+1)+ix;fs.append((j,j+1,j+nx+2,j+nx+1))
    f.mesh(vs,fs,material)


def _grid_box(f,p,size,material,spacing):
    """One actual closed construction solid with sampled surfaces."""
    x,y,z=p;a,b,c=[s/2 for s in size]
    vs=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
        (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
    for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        _grid_quad(f,*(vs[i] for i in face),material,spacing)


def _room_envelope(frame,u,w,pitch,facade_width,points,edge,seed,detail,floor_z,doors):
    """Fit a real near-street room without touching another facade's recess.

    Expanded rectangles stay inside the source footprint, have a partition
    gap to the next bay, and stay beyond the 2.45 m entry pockets on every
    other facade. The distance comparison also prevents opposite expanded
    rooms from overlapping in narrow wings. Corner windows remain bounded.
    """
    base_depth=(1.48 if detail>1 else (1.38 if detail else 1.24))+random.Random(seed+505).random()*.30
    base_width=w+.16
    bounds={'width':base_width,'depth':base_depth,'expanded':False,'constraint':'distant_or_small_window'}
    if detail<2 or w<1.08:return bounds
    other_edges=[(a,b) for j,(a,b) in enumerate(zip(points,points[1:]+points[:1])) if j!=edge]
    def proper_cross(a,b,c,d):
        orient=lambda p,q,r:(q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
        return orient(a,b,c)*orient(a,b,d)<-1e-8 and orient(c,d,a)*orient(c,d,b)<-1e-8
    def fits(width,depth,separation=False):
        corners=[frame.transform((x,y,0))[:2] for x,y in [(u-width/2,-.26),(u+width/2,-.26),(u+width/2,-depth),(u-width/2,-depth)]]
        if not all(_inside(q,points) for q in corners):return False
        if any(proper_cross(a,b,c,d) for a,b in zip(corners,corners[1:]+corners[:1]) for c,d in zip(points,points[1:]+points[:1])):return False
        if separation:
            for sx in [-.5,-.25,0,.25,.5]:
                for dep in [.26,(depth+.26)/2,depth]:
                    q=frame.transform((u+sx*width,-dep,0))[:2]
                    if not _inside(q,points):return False
                    if min((_segdist(q,a,b) for a,b in other_edges),default=100)<max(2.60,dep+.12):return False
        return True
    # Keep existing corner fragments within their own source footprint. Their
    # depth is never increased into the neighbouring perpendicular facade.
    corner_cap=max(1.42,min(u,facade_width-u)-.08)
    bounds['depth']=min(base_depth,corner_cap)
    while bounds['depth']>1.05 and not fits(base_width,bounds['depth']):bounds['depth']-=.10
    bounds['depth']=round(bounds['depth'],5)
    candidate_width=min(3.10,pitch-.22)
    for du,dw,dh,kind in doors:
        if floor_z<dh:
            clearance=(du-dw/2-u if u<du else u-du-dw/2)-.17
            candidate_width=min(candidate_width,max(0,clearance*2))
    if candidate_width<2.70:
        bounds['constraint']='bay_or_entry_clearance';return bounds
    if min(u-candidate_width/2,facade_width-u-candidate_width/2)<2.60:
        bounds['constraint']='corner_clearance';return bounds
    candidate_depth=2.40+.40*random.Random(seed+9413).random()
    depths=sorted(set([round(candidate_depth,5),2.60,2.50,2.40]),reverse=True)
    depths=[d for d in depths if d<=candidate_depth+.00001]
    widths=[candidate_width]
    if candidate_width>2.85:widths.extend([2.85,2.70])
    elif candidate_width>2.70:widths.append(2.70)
    for rw in widths:
        for rd in depths:
            if fits(rw,rd,True):
                return {'width':round(rw,5),'depth':round(rd,5),'expanded':True,'constraint':'source_footprint_and_adjacent_recess_clearance'}
    bounds['constraint']='footprint_or_opposite_wing_clearance'
    return bounds


def _window_room(f,u,z,w,h,seed,balcony=False,detail=1,floor_z=None,hero_assets=False,room_spec=None):
    """Real, non-enterable room fragment behind each transparent pane.

    Five interior faces stop opposite building walls showing through.  Their
    depth, surfaces and silhouettes provide parallax instead of a dark card.
    """
    rng=random.Random(seed+505)
    depth=(1.48 if detail>1 else (1.38 if detail else 1.24))+rng.random()*.30
    room_width=w+.16
    if room_spec is not None:depth=room_spec['depth'];room_width=room_spec['width']
    curtain_mat=_curtain_material(seed)
    left=u-room_width/2;right=u+room_width/2
    bottom=floor_z if floor_z is not None else z-h/2-(.04 if balcony else 1.08)
    top=max(z+h/2+.19,bottom+2.62)
    side='room_wall'
    # Reverse-wound caps face into the room, so no transparency cheat is needed.
    grid=.45 if detail>1 else (.80 if detail else 1.10)
    shared=room_spec.get('_shared') if room_spec else None
    walls=room_domains.ClipFrame(f,shared['wall']) if shared else f
    ceiling=room_domains.ClipFrame(f,shared['ceiling']) if shared else f
    floor_frame=room_domains.ClipFrame(f,shared['floor']) if shared else f
    _grid_quad(walls,(left,-depth,top),(right,-depth,top),(right,-depth,bottom),(left,-depth,bottom),side,grid)
    _grid_quad(walls,(left,-.23,top),(left,-depth,top),(left,-depth,bottom),(left,-.23,bottom),side,grid)
    _grid_quad(walls,(right,-depth,bottom),(right,-depth,top),(right,-.23,top),(right,-.23,bottom),side,grid)
    _grid_quad(ceiling,(right,-.23,top),(right,-depth,top),(left,-depth,top),(left,-.23,top),'room_wall',grid)
    _grid_quad(floor_frame,(left,-depth,bottom),(right,-depth,bottom),(right,-.23,bottom),(left,-.23,bottom),'room_floor',.20 if detail>1 else grid)
    if not shared or shared['is_owner']:
        room=interiors.dress_window_room(f,u,bottom,w,h,depth,seed,detail,balcony,hero_assets,room_width,not shared)
    else:
        room={'kind':shared['kind'],'lamp':None,'detail':detail,'floor_m':bottom,'assets':[],
              'shared_view':True,'furnishing_owner':shared['owner']}
    room['room_width_m']=room_width;room['room_depth_m']=depth
    # A small plaster ceiling rose has a three-dimensional diffuser, never an
    # emissive rectangular card floating in the room.
    if seed%13==0 and detail and (not shared or shared['is_owner']):
        interiors.lathe(f,(u,-depth*.65,top-.075),[(0,0),(.09,0),(.13,.028),(.13,.045),(0,.045)],'offwhite',12)
    # Some rooms have pulled-down venetian blinds, others soft uneven curtains.
    if seed%13==3:
        bh=h*(.25+(seed%3)*.045);by=-.42
        for k in range(max(3,int(bh/.07))):
            zz=z+h/2-.06-k*.07
            # Closed, correctly wound slats: R8 exposed only the pull cords
            # because the old one-sided blades faced away from the street.
            vertices=[(u-w/2+.065,by-.012,zz-.026),(u-w/2+.065,by+.025,zz+.026),(u+w/2-.065,by+.025,zz+.026),(u+w/2-.065,by-.012,zz-.026)]
            _thin_panel(f,vertices,curtain_mat,curtain_mat,.004)
        for xx in [u-w*.31,u+w*.31]:f.cylinder((xx,by+.03,z+h/2-bh),(xx,by+.03,z+h/2-.03),.004,'offwhite',5)
    else:
        coverage=(.13,.16,.19,.22)[seed%4]
        for side_sign in [-1,1]:
            cw=w*(coverage if side_sign<0 else coverage*.69)
            cx=u+side_sign*(w/2-cw/2-.035)
            _curtain(f,cx,-.44-(seed%3)*.025,z-.03,cw,h+.03,seed+side_sign,curtain_mat,detail)
        f.cylinder((u-w/2-.05,-.43,z+h/2+.07),(u+w/2+.05,-.43,z+h/2+.07),.014,'frame',6)
    return room


def _window(f,u,z,w,h,style,seed,balcony=False,detail=1,floor_z=None,hero_assets=False,room_spec=None,room_frame=None):
    rng=random.Random(seed)
    timber=style in ('heritage','brick_home','courtyard_home','artisan')
    frame='timber' if timber else ('offwhite' if style in ('clinic','civic','service','restored') else 'aluminium')
    glass='glass_warm' if seed%17==0 else ('glass_blue' if seed%5==0 else 'glass')
    room=_window_room(room_frame or f,u,z,w,h,seed,balcony,detail,floor_z,hero_assets,room_spec)
    def trim(frame,position,size,material):
        if detail>1:interiors.bevel(frame,position,size,material,.004)
        else:frame.box(position,size,material)
    def pane(frame,x,y,zz,ww,hh,material):
        frame.quad((x-ww/2,y,zz-hh/2),(x-ww/2,y,zz+hh/2),(x+ww/2,y,zz+hh/2),(x+ww/2,y,zz-hh/2),material)
    open_sash=seed%7 in (1,4) and not balcony and style not in ('clinic','service','contemporary')
    if open_sash:
        # The room is visible behind an independently hinged leaf. A single
        # thin glazing surface prevents doubled alpha at front/back box faces.
        pane(f,u-w*.25,-.08,z,w*.5-.05,h-.06,glass)
        angle=math.radians(19+(seed%5)*7);cs=math.cos(angle);sn=math.sin(angle)
        tu=(-f.u[0]*cs+f.v[0]*sn,-f.u[1]*cs+f.v[1]*sn)
        tv=(f.u[0]*sn+f.v[0]*cs,f.u[1]*sn+f.v[1]*cs)
        leaf=Frame(f.b,f.transform((u+w*.5-.04,-.055,z)),tu,tv)
        sw=w*.5-.07;sh=h-.11
        pane(leaf,sw/2,-.017,0,sw-.06,sh-.06,glass)
        for xx in [.025,sw-.025]:trim(leaf,(xx,.022,0),(.040,.075,sh),frame)
        for zz in [-sh/2+.025,sh/2-.025]:trim(leaf,(sw/2,.022,zz),(sw,.075,.040),frame)
        leaf.box((sw/2,.026,.20),(sw,.055,.035),frame)
        leaf.box((sw-.11,.074,-.08),(.025,.05,.16),'frame')
    else:
        # Sliding sashes sit on two tracks, so even closed windows have a
        # readable 3D overlap instead of an uninterrupted tinted rectangle.
        pane(f,u-w*.25,-.075,z,w*.5-.055,h-.065,glass)
        pane(f,u+w*.25,-.097,z,w*.5-.055,h-.065,glass)
    for x in [u-w*.5+.027,u+w*.5-.027,u]:trim(f,(x,-.035,z),(.048,.10,h),frame)
    for zz in [z-h*.5+.027,z+h*.5-.027]:trim(f,(u,-.035,zz),(w,.10,.054),frame)
    if detail>1:
        # Sliding channel, mitred sill highlight and operable pull hardware.
        for yy in [-.082,-.115]:f.box((u,yy,z-h/2+.035),(w-.11,.014,.015),'frame')
        if not open_sash:
            for xx in [u-.075,u+.075]:
                interiors.tube(f,[(xx,-.005,z-.12),(xx,.015,z-.10),(xx,.015,z+.025),(xx,-.005,z+.045)],.009,'frame',5)
        else:
            for zz in [z-h*.31,z+h*.31]:f.cylinder((u+w*.5-.039,.005,zz-.04),(u+w*.5-.039,.005,zz+.04),.014,'aluminium',8)
    # Thin dark gasket reads around the glass but never covers the clear pane.
    for x in [u-w*.5+.057,u+w*.5-.057]:f.box((x,-.067,z),(.012,.012,h-.10),'frame')
    if timber:
        for x in [u-w*.25,u+w*.25]:f.box((x,-.052,z),(.038,.08,h),frame)
        f.box((u,-.052,z+.15),(w,.08,.045),frame)
    else:f.box((u,-.025,z+h*(.17 if seed%3 else .30)),(w,.075,.030),frame)
    f.box((u,.055,z-h/2-.065),(w+.19,.36,.13),'concrete')
    f.box((u,.018,z+h/2+.07),(w+.17,.17,.12),'concrete')
    if REVISION>=6 and seed%3!=1 and (not balcony or REVISION<7):
        # Rain runoff is concentrated below the sill ends, not distributed as
        # a uniform cloud texture across every ceramic tile.
        for side in [-1,1]:
            _damp_decal(f,u+side*w*.36,z-h/2-.34,.19+(seed%3)*.045,.45+(seed%2)*.16,seed+side)
    cage=style in ('workers','old_tile','blue_apartments','market','noodle','repair') and seed%3!=0 and not balcony and not open_sash
    if cage:
        dep=.38+(.08 if seed%2 else 0)
        for zz in [z-h*.5-.09,z+h*.5+.08]:
            f.cylinder((u-w*.5-.08,.06,zz),(u+w*.5+.08,.06,zz),.021,'frame')
            f.cylinder((u-w*.5-.08,dep,zz),(u+w*.5+.08,dep,zz),.021,'frame')
        for x in [u-w*.5-.08,u+w*.5+.08]:
            f.cylinder((x,.06,z-h*.5-.09),(x,dep,z-h*.5-.09),.021,'frame')
            f.cylinder((x,.06,z+h*.5+.08),(x,dep,z+h*.5+.08),.021,'frame')
        bars=max(8,int((w+.16)/.135))
        for k in range(bars):
            x=u-w*.5-.08+(w+.16)*k/(bars-1);f.cylinder((x,dep,z-h*.5-.09),(x,dep,z+h*.5+.08),.0095,'frame',6)
        for side in [-1,1]:
            xx=u+side*(w/2+.08)
            for yy in [.15,dep-.1]:f.cylinder((xx,yy,z-h/2-.09),(xx,yy,z+h/2+.08),.010,'frame',6)
        if seed%2:f.cylinder((u-w/2-.08,dep,z-.12),(u+w/2+.08,dep,z-.12),.012,'frame',6)
        plane=[(u-w/2-.13,-.03,z+h/2+.17),(u+w/2+.13,-.03,z+h/2+.17),(u+w/2+.13,dep+.12,z+h/2+.075),(u-w/2-.13,dep+.12,z+h/2+.075)]
        _thin_panel(f,plane,'painted_metal','rust',.018)
        # Rain-cover ribs and attachment tabs give it thickness and scale.
        for k in range(max(4,int(w/.18))):
            xx=u-w/2+k*.18
            f.cylinder((xx,-.03,z+h/2+.19),(xx,dep+.12,z+h/2+.095),.009,'aluminium',5)
        for xx in [u-w/2-.08,u+w/2+.08]:
            f.box((xx,.023,z+.23),(.055,.055,.16),'rust')
    if timber and seed%3==1:
        # Narrow louvers/shutters in alternating closed and open positions.
        for side in [-1,1]:
            x=u+side*(w*.5+.19);f.box((x,.03,z),(.29,.10,h),'timber')
            for k in range(7):f.box((x,.09,z-h*.36+k*h*.12),(.25,.035,.027),'wood')
    if style in ('clinic','civic','restored'):
        # Stone surrounds produce a different depth language from tiled walkups.
        for x in [u-w*.5-.09,u+w*.5+.09]:f.box((x,.035,z),(.14,.16,h+.28),'plaster')
        f.box((u,.07,z+h*.5+.17),(w+.4,.26,.17),'plaster')
    if balcony:
        if REVISION>=7:
            lo=z-h/2
            if timber:f.box((u,-.025,lo+.20),(w-.12,.08,.30),'timber')
            for xx in [u-.065,u+.065]:
                f.box((xx,.032,lo+.97),(.020,.058,.16),'frame')
        _balcony(f,u,z-h*.5-.16,w+.58,timber,seed)
    return room


def _balcony(f,u,z,w,timber,seed):
    dep=.95 if timber else .72
    f.box((u,dep*.48,z),(w,dep+.1,.16),'timber' if timber else 'concrete')
    rail='timber' if timber else 'painted_metal'
    rail_top=1.04 if REVISION>=7 else .94
    bar_center=(.17+rail_top)/2 if REVISION>=7 else .56
    bar_height=rail_top-.17 if REVISION>=7 else .78
    f.box((u,dep,z+rail_top),(w,.09,.08),rail)
    f.box((u,dep,z+.17),(w,.07,.07),rail)
    for k in range(max(5,int(w/.19))):
        x=u-w/2+.06+(w-.12)*k/max(1,int(w/.19)-1)
        f.box((x,dep,z+bar_center),(.045,.06,bar_height),rail)
    for x in [u-w/2,u+w/2]:
        f.box((x,dep/2,z+rail_top),(.08,dep,.08),rail)
        f.box((x,dep/2,z+.17),(.07,dep,.07),rail)
        for k in range(4):f.box((x,.13+k*dep/4,z+(bar_center if REVISION>=7 else .55)),(.05,.05,bar_height),rail)
    if seed%3==0:
        interiors.plant(f,(u-w*.23,dep-.17,z+.10),.35,1 if z<7 else 0,seed)
    if timber:
        for x in [u-w*.4,u+w*.4]:f.pipe([(x,.03,z-.65),(x,dep*.8,z-.1)],.065,'timber',8)
    if REVISION>=6:
        if seed%4==0:
            # Domestic drying, with real folded thickness and sagging hems.
            f.cylinder((u-w*.42,dep+.10,z+1.30),(u+w*.42,dep+.10,z+1.30),.008,'frame',6)
            _curtain(f,u-w*.13,dep+.12,z+.94,w*.33,.71,seed+71,_curtain_material(seed+77))
            for xx in [u-w*.27,u+w*.01]:f.box((xx,dep+.13,z+1.29),(.027,.04,.055),'wood')
        elif seed%4==1 and not timber:
            # Residents have partly enclosed selected railings with sheet
            # metal; this changes facade massing rather than only bar colour.
            f.box((u,dep+.035,z+.47),(w-.12,.028,.61),'painted_metal')
            for k in range(max(6,int(w/.11))):
                xx=u-w/2+.08+k*.11
                f.cylinder((xx,dep+.057,z+.18),(xx,dep+.057,z+.77),.007,'aluminium',5)
        if seed%5==0:
            interiors.plant(f,(u+w*.28,dep*.45,z+.09),.42,1 if z<7 else 0,seed+34)


def _awning(f,u,z,w,style,seed):
    dep=1.22 if style not in ('heritage','repair') else 1.45
    if REVISION>=6 and style in ('noodle','market','service'):
        # Street canopies have repaired solid fabric or ribbed metal skins,
        # replacing the identical clean candy-striped storefront treatment.
        material='curtain_beige' if seed%3==0 else 'painted_metal'
        strips=max(7,int(w/.24));depth_segments=5
        for k in range(strips):
            a=u-w/2+w*k/strips;b=u-w/2+w*(k+1)/strips
            for j in range(depth_segments):
                t0=j/depth_segments;t1=(j+1)/depth_segments
                y0=-.04+(dep+.04)*t0;y1=-.04+(dep+.04)*t1
                sag=lambda t:.065*math.sin(math.pi*t)
                za=z+.22-.37*t0-sag(t0);zb=z+.22-.37*t1-sag(t1)
                _thin_panel(f,[(a,y0,za),(b,y0,za),(b,y1,zb),(a,y1,zb)],material,material,.014)
            if material=='painted_metal':
                points=[(a+.045,-.04+(dep+.04)*j/5,z+.245-.37*j/5-.065*math.sin(math.pi*j/5)) for j in range(6)]
                f.pipe(points,.010,'aluminium',5)
        f.box((u,dep,z-.205),(w+.02,.032,.11),material)
        f.cylinder((u-w/2-.03,dep,z-.16),(u+w/2+.03,dep,z-.16),.024,'frame',8)
        for xx in [u-w/2+.08,u+w/2-.08]:
            f.pipe([(xx,.035,z-.36),(xx,dep,z-.16),(xx,-.035,z+.22)],.019,'frame',6)
        return
    if style in ('heritage','repair','workshop'):
        plane=[(u-w/2,-.04,z+.25),(u+w/2,-.04,z+.25),(u+w/2,dep,z-.12),(u-w/2,dep,z-.12)]
        _thin_panel(f,plane,'roof_tiles' if style=='heritage' else 'painted_metal','timber' if style=='heritage' else 'painted_metal',.025)
        for i in range(max(3,int(w/.3))):
            x=u-w/2+i*.3;f.cylinder((x,-.04,z+.27),(x,dep,z-.10),.027,'frame',6)
    else:
        n=max(6,int(w/.32))
        for k in range(n):
            a=u-w/2+w*k/n;b=u-w/2+w*(k+1)/n
            material='offwhite' if k%2 else ('faded_green' if seed%2 else 'faded_red')
            plane=[(a,-.04,z+.22),(b,-.04,z+.22),(b,dep,z-.15),(a,dep,z-.15)]
            _thin_panel(f,plane,material,material,.012)
            f.box(((a+b)/2,dep,z-.22),(b-a,.025,.16),material)
    for x in [u-w/2+.10,u+w/2-.10]:f.cylinder((x,.02,z-.30),(x,dep,z-.12),.023,'frame',6)


def _wall_fixture_placement(ctx,frame,facade_width,holes,x,z,half_width=.23,below=.31,above=.31,outer_depth=.18,preserve_actual_clear=False):
    """Place existing wall hardware on actual solid masonry, above the street.

    The dimensions, materials and wall offset are unchanged. Prefer the old
    location, then solid wall below the sill, then a nearby clear wall pier.
    The full rain-hood envelope is used for shop meter boxes.
    """
    margin=.06;edge_margin=.08;ground_margin=.25
    def overlap_area(cx,cz,extra=0.):
        left,right=cx-half_width,cx+half_width;bottom,top=cz-below,cz+above
        return sum(max(0.,min(right,h[1]+extra)-max(left,h[0]-extra))*
                   max(0.,min(top,h[3]+extra)-max(bottom,h[2]-extra)) for h in holes)
    def clearance(cx,cz):
        ground=[]
        for dx in [-half_width,0,half_width]:
            for dy in [0.,outer_depth/2,outer_depth]:
                p=frame.transform((cx+dx,dy,0));ground.append(ctx.ground_height(p[0],p[1]))
        return frame.o[2]+cz-below-max(ground)
    def legal(cx,cz,extra=margin):
        return (cx-half_width>=edge_margin-1.e-8 and cx+half_width<=facade_width-edge_margin+1.e-8
                and overlap_area(cx,cz,extra)<1.e-10 and clearance(cx,cz)>=ground_margin-1.e-8)
    def free_slots(cz):
        occupied=sorted((max(edge_margin,h[0]-margin),min(facade_width-edge_margin,h[1]+margin)) for h in holes
                        if cz+above>h[2]-margin and cz-below<h[3]+margin)
        intervals=[];start=edge_margin
        for left,right in occupied+[(facade_width-edge_margin,facade_width-edge_margin)]:
            if left-start>=half_width*2-1.e-8:intervals.append((start+half_width,left-half_width))
            start=max(start,right)
        return intervals
    original_overlap=overlap_area(x,z);candidates=[]
    if legal(x,z,0. if preserve_actual_clear else margin):candidates.append((0,0.,x,z,'retained_original'))
    # The real concrete sill projects 13 cm below the aperture. Mount below
    # that solid, not merely below the opening's lower edge.
    sill_heights=sorted({round(h[2]-.13-margin-above,8) for h in holes if .5<h[2]<2.6})
    for height in sill_heights:
        if legal(x,height):candidates.append((1,abs(height-z),x,height,'solid_wall_below_sill'))
    for lo,hi in free_slots(z):
        cx=max(lo,min(hi,x))
        if legal(cx,z):candidates.append((2,abs(cx-x),cx,z,'solid_wall_pier'))
    for height in sill_heights:
        for lo,hi in free_slots(height):
            cx=max(lo,min(hi,x))
            if legal(cx,height):candidates.append((3,math.hypot(cx-x,height-z),cx,height,'lower_solid_wall_pier'))
    result={'placed':bool(candidates),'original_local':[x,z],'half_width_m':half_width,'bottom_offset_m':below,
            'top_offset_m':above,'outer_depth_m':outer_depth,'opening_margin_m':margin,'minimum_ground_clearance_m':ground_margin,
            'original_opening_overlap_area_m2':original_overlap}
    if not candidates:
        result.update({'reason':'no_solid_wall_with_ground_clearance','selected_local':None});return result
    _,_,cx,cz,reason=min(candidates)
    result.update({'selected_local':[cx,cz],'reason':reason,'moved':abs(cx-x)+abs(cz-z)>1.e-7,
                   'actual_opening_overlap_area_m2':overlap_area(cx,cz),'actual_ground_clearance_m':clearance(cx,cz),
                   'world_mount_center':list(frame.transform((cx,0,cz)))})
    return result


def _doorway(ctx,shell,deco,u,width,height,kind,seed,label,style,hero_assets=False,interior_frame=None,shop_shell=None,shared_masks=None,wall_fixtures=None):
    # The first 2.4m is genuine explorable room geometry.
    if (kind=='shop' or shared_masks) and shop_shell is not None:
        # The same collision-bearing recess, moved to an identifiable actual
        # interior batch. No duplicate top plane or darkening proxy is added.
        floor_frame=room_domains.ClipFrame(shop_shell,shared_masks['floor']) if shared_masks else shop_shell
        wall_frame=room_domains.ClipFrame(shop_shell,shared_masks['wall']) if shared_masks else shop_shell
        ceiling_frame=room_domains.ClipFrame(shop_shell,shared_masks['ceiling']) if shared_masks else shop_shell
        _grid_box(floor_frame,(u,-1.20,.045),(width,2.45,.09),'pavement',.20)
        for x in [u-width/2-.06,u+width/2+.06]:_grid_box(wall_frame,(x,-1.20,height/2),(.12,2.45,height),'plaster',.45)
        _grid_box(wall_frame,(u,-2.38,height/2),(width,.12,height),'plaster_grey',.45)
        _grid_box(ceiling_frame,(u,-1.20,height+.03),(width,2.45,.12),'concrete',.45)
    else:
        shell.box((u,-1.20,.045),(width,2.45,.09),'pavement')
        for x in [u-width/2-.06,u+width/2+.06]:shell.box((x,-1.20,height/2),(.12,2.45,height),'plaster')
        shell.box((u,-2.38,height/2),(width,.12,height),'plaster_grey')
        shell.box((u,-1.20,height+.03),(width,2.45,.12),'concrete')
    for x in [u-width/2+.035,u+width/2-.035]:deco.box((x,.025,height/2),(.07,.12,height),'frame')
    deco.box((u,.025,height-.02),(width,.12,.08),'frame')
    exterior_deco=deco
    is_shop=kind=='shop'
    asset_markers=[]
    timber_entry=style in ('courtyard_home','brick_home','heritage')
    if is_shop:
        if interior_frame is not None:deco=interior_frame
        eatery=style=='noodle' or '家常菜' in label
        # A true shop recess, with different fitted contents by use. All are
        # inside the building; the street and clear door width stay unobstructed.
        deco.box((u,-2.285,.48),(width-.06,.055,.94),'timber' if style!='service' else 'painted_metal')
        if eatery:
            deco.box((u,-2.275,1.67),(width-.08,.055,1.40),'tile_cream')
            for side in [-1,1]:deco.box((u+side*(width/2-.035),-1.20,.48),(.06,2.40,.94),'timber')
            cw=max(1.0,width*.33);cu=u-width*.29
            interiors.bevel(deco,(cu,-.72,.53),(cw,.76,.94),'timber',.014)
            interiors.bevel(deco,(cu,-.72,1.03),(cw+.10,.84,.065),'aluminium',.014)
            # Dark fluted timber and stainless service counter, stock pot,
            # ceramic bowls, condiment shelf, and a real extractor hood.
            for k in range(max(4,int(cw/.14))):
                deco.box((cu-cw/2+.07+k*.14,-.325,.47),(.035,.035,.84),'wood')
            potx=cu-cw*.21
            interiors.lathe(deco,(potx,-.72,1.065),[(0,0),(.16,0),(.195,.025),(.20,.09),(.20,.30),(.213,.315),(.208,.33),(.18,.335),(0,.335)],'aluminium',20)
            interiors.lathe(deco,(potx,-.72,1.397),[(0,0),(.213,0),(.195,.025),(.14,.045),(0,.050)],'aluminium',20)
            interiors.tube(deco,[(potx-.052,-.72,1.444),(potx-.045,-.72,1.474),(potx+.045,-.72,1.474),(potx+.052,-.72,1.444)],.014,'dark',6)
            for side in [-1,1]:interiors.tube(deco,[(potx+side*.19,-.76,1.30),(potx+side*.27,-.76,1.31),(potx+side*.27,-.68,1.31),(potx+side*.19,-.68,1.30)],.015,'dark',6)
            for k in range(3):
                bx=cu+.11+k*.17
                interiors.vessel(deco,(bx,-.72,1.065),.102,.082,'ceramic_glaze',2,'bowl')
            hx=u-width*.29;hw=width*.35
            deco.mesh([(hx-hw/2,-2.28,2.12),(hx+hw/2,-2.28,2.12),(hx+hw/2,-1.81,2.12),(hx-hw/2,-1.81,2.12),
                       (hx-hw*.34,-2.25,2.35),(hx+hw*.34,-2.25,2.35),(hx+hw*.34,-1.97,2.35),(hx-hw*.34,-1.97,2.35)],
                      [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'aluminium')
            interiors.bevel(deco,(hx,-2.10,2.50),(.28,.30,.32),'aluminium',.014)
            for k in range(9):deco.box((hx-hw*.38+k*hw*.095,-1.804,2.16),(.016,.009,.065),'frame')
            for zz in [1.25,1.69]:
                interiors.bevel(deco,(u-width*.28,-2.10,zz),(width*.34,.29,.065),'timber',.008)
                for k in range(4):
                    xx=u-width*.41+k*width*.085
                    if zz<1.5:interiors.vessel(deco,(xx,-2.08,zz+.04),.057,.15,'ceramic_glaze',2,'cup')
            # The narrow fixed pane and opened door leaf articulate the shop
            # frontage without placing opaque glass across the kitchen view.
            gx=u-width/2+.24
            deco.quad((gx-.21,-.05,1.08),(gx-.21,-.05,2.16),(gx+.21,-.05,2.16),(gx+.21,-.05,1.08),'glass_blue')
            for xx in [gx-.23,gx+.23]:deco.box((xx,.0,1.62),(.045,.09,1.18),'timber')
            for zz in [1.05,2.19]:deco.box((gx,0,zz),(.50,.09,.045),'timber')
            doorx=u+width/2-.09
            for yy in [-1.09,-.11]:interiors.bevel(deco,(doorx,yy,1.13),(.09,.06,2.20),'timber',.005)
            for zz in [.06,1.01,2.20]:interiors.bevel(deco,(doorx,-.60,zz),(.09,1.02,.07),'timber',.005)
            interiors.bevel(deco,(doorx,-.60,.53),(.06,.88,.87),'timber',.008)
            deco.quad((doorx-.051,-1.03,1.05),(doorx-.051,-1.03,2.16),(doorx-.051,-.17,2.16),(doorx-.051,-.17,1.05),'glass')
            deco.box((u+width/2-.20,-.26,1.04),(.08,.035,.21),'aluminium')
        elif style=='repair':
            deco.box((u-width*.12,-1.70,.87),(width*.70,.78,.12),'timber')
            for xx in [u-width*.42,u+width*.18]:deco.box((xx,-1.70,.43),(.08,.66,.86),'frame')
            deco.box((u-width*.22,-2.27,1.70),(width*.42,.045,.87),'painted_metal')
            for k in range(6):
                xx=u-width*.40+k*width*.065
                deco.cylinder((xx,-2.22,1.48),(xx,-2.22,1.85+(k%2)*.12),.018,'aluminium',6)
                deco.box((xx,-2.21,1.46),(.07,.035,.085),'dark')
            wheelx=u+width*.28
            wheel=[(wheelx+math.cos(k*math.tau/16)*.37,-2.16,1.47+math.sin(k*math.tau/16)*.37) for k in range(17)]
            deco.pipe(wheel,.052,'dark',8)
            for k in range(8):deco.cylinder((wheelx,-2.15,1.47),wheel[k*2],.009,'aluminium',6)
        elif style=='workshop':
            interiors.printer(deco,(u-width*.24,-1.45,.09),width*.31)
            for xx in [u+width*.10,u+width*.44]:interiors.bevel(deco,(xx,-1.99,.85),(.035,.32,1.53),'timber',.005)
            for k in range(3):
                zz=.27+k*.48
                interiors.bevel(deco,(u+width*.27,-1.99,zz),(width*.36,.53,.035),'timber',.005)
                for j in range(5):
                    deco.box((u+width*.27+(j%2)*.012,-1.98,zz+.035+j*.024),(width*.30,.45,.020),'paper')
        elif style=='service':
            interiors.sideboard(deco,(u-width*.27,-1.20,.09),width*.32,.90,2)
            for xx in [u-.02,u+1.48]:interiors.bevel(deco,(xx,-2.12,.96),(.04,.22,1.79),'painted_metal',.005)
            for row in range(3):
                interiors.bevel(deco,(u+.73,-2.01,.15+row*.51),(1.57,.58,.035),'timber',.005)
                for col in range(3):
                    xx=u+width*.04+col*.48;hh=.28+((row+col)%3)*.055;zz=.17+row*.51+hh/2
                    interiors.parcel(deco,(xx,-1.96,zz),(.35+.025*(col%2),.45,hh),seed+row*3+col)
        else:
            interiors.sideboard(deco,(u-width*.28,-1.30,.09),width*.30,.94,2)
            for zz in [1.15,1.67,2.14]:
                interiors.bevel(deco,(u,-2.08,zz),(width*.79,.34,.06),'timber',.008)
                for k in range(5):
                    xx=u-width*.31+k*width*.155
                    if k%2:interiors.vessel(deco,(xx,-2.06,zz+.04),.075,.18+(k%3)*.05,'ceramic_glaze',2,'pot')
                    else:interiors.bottle(deco,(xx,-2.06,zz+.04),.27+(k%2)*.08,.065,'faded_green',2)
        caption_x=u+width*.17 if eatery else u
        caption_z=1.82 if eatery else 2.34
        caption_w=max(.7,width*(.43 if eatery else .64))
        deco.box((caption_x,-2.22,caption_z),(caption_w,.045,.52),'faded_red' if eatery else 'timber')
        caption='欢 迎 光 临'
        if '小面' in label or '抄手' in label:caption='小 面  ·  抄 手'
        elif '修车' in label:caption='修 车  ·  配 钥 匙'
        elif '印务' in label:caption='印 刷  ·  装 订'
        elif '茶' in label:caption='盖 碗 茶  ·  咖 啡'
        elif '服务' in label:caption='便 民 服 务'
        elif '手作' in label:caption='手 作 体 验'
        elif '家常菜' in label:caption='家 常 小 炒'
        elif '小院' in label:caption='小 院 会 客'
        _label(ctx,deco,caption,(caption_x,-2.188,caption_z+.01),.18,'sign_cream',False)
        for x in [u-width*.25,u+width*.25]:
            deco.cylinder((x,-1.05,height-.02),(x,-1.05,height-.35),.012,'dark',6)
            deco.cylinder((x,-1.05,height-.38),(x,-1.05,height-.29),.18,'painted_metal',12,r2=.07)
            deco.cylinder((x,-1.05,height-.39),(x,-1.05,height-.38),.14,'light_warm',12)
        asset_markers=interiors.shop_details(deco,u,width,height,style,label,seed,hero_assets)
    else:
        if not timber_entry:deco.box((u+width*.44,-.59,1.17),(.075,1.06,2.25),'painted_metal')
        if timber_entry:
            dx=u+width*.44
            for yy in [-1.09,-.09]:interiors.bevel(deco,(dx,yy,1.17),(.075,.06,2.25),'timber',.005)
            for zz in [.075,1.04,2.265]:interiors.bevel(deco,(dx,-.59,zz),(.075,1.06,.06),'timber',.005)
            interiors.bevel(deco,(dx,-.59,.55),(.052,.92,.89),'timber',.007)
            deco.quad((dx-.042,-1.05,1.075),(dx-.042,-1.05,2.23),(dx-.042,-.13,2.23),(dx-.042,-.13,1.075),'glass_warm')
            interiors.tube(deco,[(dx-.045,-.20,1.01),(dx-.085,-.20,1.04),(dx-.085,-.20,1.17),(dx-.045,-.20,1.20)],.012,'rust',6,reference=(0,1,0))
            for xx in [u-width/2-.09,u+width/2+.09]:
                deco.box((xx,.07,height/2),(.19,.24,height+.13),'timber')
                deco.box((xx,.09,.20),(.24,.28,.40),'stone')
            deco.box((u,-2.275,.48),(width-.06,.055,.94),'brick_dark')
            deco.box((u,-1.00,height-.13),(.31,.25,.09),'light_warm')
        for k in range(5):shell.box((u,-1.45-k*.19,.05+.065*(k+1)),(width*.67,.20,.13*(k+1)),'pavement')
        meter=(wall_fixtures or {}).get('meter',{'placed':True,'selected_local':[u-width*.65,1.5]})
        if meter['placed']:
            mx,mz=meter['selected_local']
            deco.box((mx,.08,mz),(.46,.16,.62),'painted_metal')
            for k in range(3):deco.box((mx,.165,mz-.16+k*.17),(.40,.016,.012),'dark')
        plaque=(wall_fixtures or {}).get('plaque',{'placed':True,'selected_local':[u+width*.7,2.05]})
        if plaque['placed']:
            px,pz=plaque['selected_local']
            deco.box((px,.045,pz),(.48,.08,.34),'electric_blue')
            _label(ctx,deco,str(seed%23+1)+' 号',(px,.095,pz),.19)
    exterior_deco.box((u,.12,height+.19),(width+.45,.45,.20),'timber' if timber_entry else 'concrete')
    return asset_markers


def _poly_cap(b,points,z,mat,thickness=.15,side_faces=True):
    tris=_triangles(points)
    b.mesh([(x,y,z) for x,y in points],tris,mat)
    if thickness:
        b.mesh([(x,y,z-thickness) for x,y in points],[tuple(reversed(t)) for t in tris],mat)
        if side_faces:
            for a,c in zip(points,points[1:]+points[:1]):
                b.quad((a[0],a[1],z),(a[0],a[1],z-thickness),(c[0],c[1],z-thickness),(c[0],c[1],z),mat)


def _roof(ctx,b,points,base,height,p,seed):
    z=base+height;style=p['roof'];rng=random.Random(seed+83)
    # The facade already closes the slab perimeter. A second coplanar strip
    # caused small depth-fighting bands at the roof and foundation in Godot.
    _poly_cap(b,points,z,'concrete',.20,side_faces=False)
    # Faceted dark clay tiled gable with visible ridge and timber under-eaves.
    # Only compact buildings use this form; large concave footprints stay flat.
    if style in ('gable','shed'):
        edges=list(zip(points,points[1:]+points[:1]));a,c=max(edges,key=lambda e:math.dist(*e))
        w=math.dist(a,c);u=((c[0]-a[0])/w,(c[1]-a[1])/w);v=(-u[1],u[0])
        coords=[((x-a[0])*u[0]+(y-a[1])*u[1],(x-a[0])*v[0]+(y-a[1])*v[1]) for x,y in points]
        xmin,xmax=min(x for x,y in coords),max(x for x,y in coords);ymin,ymax=min(y for x,y in coords),max(y for x,y in coords)
        f=Frame(b,(a[0],a[1],z),u,v);ridge=(ymin+ymax)/2;rise=min(2.3,max(1.15,(ymax-ymin)*.20))
        lo=xmin-.48;hi=xmax+.48;front=ymin-.52;back=ymax+.52
        def roof_plane(vertices):
            _thin_panel(f,vertices,'roof_tiles','timber',.06)
        if style=='gable':
            roof_plane([(lo,front,.20),(hi,front,.20),(hi,ridge,rise),(lo,ridge,rise)])
            roof_plane([(lo,ridge,rise),(hi,ridge,rise),(hi,back,.20),(lo,back,.20)])
            f.mesh([(xmin,ymin,.1),(xmin,ymax,.1),(xmin,ridge,rise-.08)],[(0,2,1)],p['wall'])
            f.mesh([(xmax,ymin,.1),(xmax,ridge,rise-.08),(xmax,ymax,.1)],[(0,2,1)],p['wall'])
            f.cylinder((lo-.05,ridge,rise+.045),(hi+.05,ridge,rise+.045),.11,'roof_tiles',10)
            # Longitudinal ridges and eave ends give real silhouette, not a flat roof card.
            n=max(4,int((hi-lo)/.36))
            for k in range(n+1):
                x=lo+(hi-lo)*k/n
                f.cylinder((x,front,.23),(x,ridge,rise+.02),.025,'roof_tiles',6)
                f.cylinder((x,ridge,rise+.02),(x,back,.23),.025,'roof_tiles',6)
            for yy in [front,back]:
                f.box(((lo+hi)/2,yy,.13),(hi-lo,.16,.16),'timber')
                f.cylinder((lo,yy,.12),(hi,yy,.12),.075,'painted_metal',10)
        else:
            roof_plane([(lo,front,.2),(hi,front,.2),(hi,back,rise),(lo,back,rise)])
            f.mesh([(xmin,ymin,.1),(xmin,ymax,.1),(xmin,ymax,rise)],[(0,2,1)],p['wall'])
            f.mesh([(xmax,ymin,.1),(xmax,ymax,rise),(xmax,ymax,.1)],[(0,2,1)],p['wall'])
        return
    # Varied parapet/cornice rather than the identical roof-on-a-box silhouette.
    for i,(a,c) in enumerate(zip(points,points[1:]+points[:1])):
        d=math.dist(a,c)
        if d<.1:continue
        u=((c[0]-a[0])/d,(c[1]-a[1])/d);v=(u[1],-u[0]);f=Frame(b,(a[0],a[1],z),u,v)
        ph=.50 if p['style'] in ('artisan','workshop') else (.72 if seed%3==0 else .48)
        f.box((d/2,-.09,ph/2),(d,.18,ph),p['wall'])
        f.box((d/2,-.09,ph+.055),(d+.04,.28,.11),'concrete')
        if p['style'] in ('civic','clinic','restored'):f.box((d/2,.14,-.13),(d+.08,.48,.24),'plaster')
    cx,cy=_centroid(points)
    if not _inside((cx,cy),points):cx,cy=points[0][0]*.3+points[1][0]*.7,points[0][1]*.3+points[1][1]*.7
    # Choose rooftop object positions that stay safely within the footprint.
    xmin=min(q[0] for q in points);xmax=max(q[0] for q in points);ymin=min(q[1] for q in points);ymax=max(q[1] for q in points)
    candidates=[]
    for _ in range(140):
        q=(rng.uniform(xmin,xmax),rng.uniform(ymin,ymax))
        if _inside(q,points) and min(_segdist(q,a,c) for a,c in zip(points,points[1:]+points[:1]))>1.75:candidates.append(q)
    if candidates:
        x,y=candidates[0];f=Frame(b)
        if p['style'] in ('contemporary','blue_apartments','cream_residence','old_tile','workers','market'):
            f.box((x,y,z+1.05),(2.9,3.1,2.1),'plaster_grey')
            f.box((x,y,z+2.15),(3.2,3.4,.20),'concrete')
            f.box((x,y-1.56,z+.91),(1.1,.05,1.8),'painted_metal')
        elif p['style'] in ('clinic','service','civic'):
            f.box((x,y,z+.55),(2.4,1.7,1.1),'offwhite')
            for k in range(8):f.box((x,y-.86,z+.18+k*.1),(2.15,.025,.024),'aluminium')
        if len(candidates)>8:
            x,y=candidates[8]
            if p['style'] in ('blue_apartments','old_tile','workers','market','cream_residence'):
                f.box((x,y,z+.18),(1.6,1.6,.36),'concrete')
                f.cylinder((x,y,z+.36),(x,y,z+1.72),.61,'aluminium',20)
                for zz in [.44,1.02,1.65]:f.cylinder((x,y,z+zz),(x,y,z+zz+.035),.64,'aluminium',20)
                f.cylinder((x,y,z+1.72),(x,y,z+1.82),.56,'offwhite',20,r2=.22)
                f.pipe([(x+.61,y,z+.55),(x+.88,y,z+.55),(x+.88,y,z+.15)],.06,'offwhite')
            elif p['style'] in ('artisan','workshop'):
                f.box((x,y,z+.15),(3.,2.,.3),'concrete')
                f.quad((x-1.4,y-.9,z+.3),(x+1.4,y-.9,z+.3),(x+1.4,y+.9,z+1.0),(x-1.4,y+.9,z+1.0),'glass_blue')
                for xx in [x-1.4,x,x+1.4]:f.cylinder((xx,y-.9,z+.32),(xx,y+.9,z+1.02),.035,'aluminium',6)
    if style=='sawtooth':
        # Short roof lanterns, each placed within the polygon, differ from housing.
        for j,(x,y) in enumerate(candidates[1:20:5]):
            if j>=3:break
            f=Frame(b);f.box((x,y,z+.31),(2.7,1.7,.62),'brick')
            f.quad((x-1.38,y-.9,z+.62),(x+1.38,y-.9,z+.62),(x+1.38,y+.9,z+1.18),(x-1.38,y+.9,z+1.18),'roof_tiles')
            f.box((x,y+.84,z+.85),(2.65,.05,.55),'glass_blue')
    if REVISION>=6 and candidates:
        # Household rooftop equipment has a different silhouette from the
        # existing stair headhouse and cylindrical water tank. Keep footprints
        # separated, and never cross a concave roof edge.
        occupied=candidates[:1]+(candidates[8:9] if len(candidates)>8 else [])
        spare=next((q for q in candidates if all(math.dist(q,o)>4.1 for o in occupied)),None)
        if spare and p['style'] in ('blue_apartments','old_tile','workers','market','cream_residence'):
            x,y=spare;f=Frame(b)
            if seed%3!=1:
                # Evacuated-tube solar water heater, compact and naturally
                # asymmetric with respect to the building's roof ridgeline.
                f.cylinder((x-1.05,y+.54,z+1.24),(x+1.05,y+.54,z+1.24),.245,'aluminium',20)
                for xx in [x-.77,x+.77]:
                    f.pipe([(xx,y-.84,z+.11),(xx,y+.60,z+1.02),(xx,y+.64,z+.12)],.024,'frame',8)
                    f.box((xx,y-.80,z+.065),(.22,.27,.10),'concrete')
                    f.box((xx,y+.60,z+.065),(.22,.27,.10),'concrete')
                for k in range(14):
                    xx=x-.88+k*1.76/13
                    f.cylinder((xx,y-.80,z+.22),(xx,y+.42,z+1.08),.032,'dark',8)
                    f.cylinder((xx,y-.80,z+.22),(xx,y-.74,z+.26),.040,'aluminium',8)
                f.cylinder((x-1.06,y-.83,z+.18),(x+1.06,y-.83,z+.18),.035,'painted_metal',8)
                f.pipe([(x+.98,y+.54,z+1.24),(x+1.23,y+.54,z+1.24),(x+1.23,y+.54,z+.14),(x+1.0,y+1.30,z+.14)],.029,'offwhite',8)
            else:
                # Old television antenna and service conduit on another house,
                # avoiding a cloned roof-asset layout across the district.
                f.box((x,y,z+.09),(.65,.65,.18),'concrete')
                f.cylinder((x,y,z+.18),(x,y,z+2.45),.023,'frame',8)
                f.cylinder((x-1.1,y,z+2.20),(x+1.1,y,z+2.20),.019,'aluminium',8)
                for k in range(7):
                    xx=x-.88+k*.29;reach=.48-abs(k-3)*.065
                    f.cylinder((xx,y-reach,z+2.20),(xx,y+reach,z+2.20),.010,'aluminium',6)
                f.pipe([(x+.04,y,z+2.14),(x+.04,y,z+.22),(x+1.2,y+.8,z+.19)],.009,'dark',6)


def _intersects(p,q):
    if any(_inside(x,q) for x in p) or any(_inside(x,p) for x in q):return True
    def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    for a,b in zip(p,p[1:]+p[:1]):
        for c,d in zip(q,q[1:]+q[:1]):
            if orient(a,b,c)*orient(a,b,d)<-1e-7 and orient(c,d,a)*orient(c,d,b)<-1e-7:return True
    return False


def _front_edge(points,base,ground,paths):
    candidates=[]
    for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
        w=math.dist(a,b)
        if w<5.0:continue
        if (abs(a[0])>99.99 and abs(b[0])>99.99) or (abs(a[1])>99.99 and abs(b[1])>99.99):continue
        u=((b[0]-a[0])/w,(b[1]-a[1])/w);v=(u[1],-u[0]);m=((a[0]+b[0])/2+v[0]*1.5,(a[1]+b[1])/2+v[1]*1.5)
        near=min((_segdist(m,c,d) for c,d in paths),default=8)
        grade=abs(base-ground(*m))
        score=near+grade*6.0-min(w,20)*.10
        candidates.append((score,i))
    return min(candidates)[1] if candidates else 0


def _floor_cutout(frame,building_id,room_id,kind,storey,left,right,back,front,floor,cut_bounds=None,visible_bounds=None):
    """Actual room floor bounds for terrain carving, in Blender world metres."""
    def polygon(bounds):
        l,r,b,f=bounds
        return [list(frame.transform((x,y,0))[:2]) for x,y in [(l,b),(r,b),(r,f),(l,f)]]
    # Hide the terrain join within the 24 cm outer wall and the side/rear
    # partition. The authored floor surface and building datum do not move.
    if cut_bounds is None:cut_bounds=(left-.015,right+.015,back-.015,-.13)
    cut_polygon=polygon(cut_bounds)
    if kind in ('shop','entry'):
        # The existing collision-bearing floor box projects 2.5 cm beyond
        # the facade. Keep that visible threshold clear too; outside y=0,
        # the cut is strictly limited to the actual floor's covered width.
        l,r,b,front_cut=cut_bounds
        outline=[(l,b),(r,b),(r,0),(right,0),(right,front_cut),
                 (left,front_cut),(left,0),(l,0)]
        cut_polygon=[list(frame.transform((x,y,0))[:2]) for x,y in outline]
    return {'building_id':str(building_id),'room_id':room_id,'kind':kind,'storey':storey,
            'polygon_xy':polygon((left,right,back,front)),'cut_polygon_xy':cut_polygon,
            'visible_polygon_xy':polygon(visible_bounds or (left,right,back,front)),
            'floor_covered_threshold_projection_m':.025 if kind in ('shop','entry') else 0.,
            'floor_top_z':frame.o[2]+floor,'coordinate_system':'Blender Z-up, metres'}


def _shared_domain_masks(frame,room_id,members,plans):
    """Actual union surfaces in the current facade frame, with stable ownership."""
    rank=members.index(room_id);current=plans[room_id];result={'wall':[],'floor':[],'ceiling':[]}
    for index,other in enumerate(members):
        if other==room_id:continue
        peer=plans[other];poly=[]
        for p in peer['polygon_xy']:
            x=p[0]-frame.o[0];y=p[1]-frame.o[1]
            poly.append((x*frame.u[0]+y*frame.u[1],x*frame.v[0]+y*frame.v[1]))
        mask={'polygon':poly,'bottom':peer['floor_top_z']-frame.o[2],
              'top':peer['ceiling_z']-frame.o[2],'keep_boundary':rank<index}
        result['wall'].append(mask)
        if index<rank:
            result['floor'].append({'polygon':poly,'keep_boundary':False})
        higher=peer['ceiling_z']>current['ceiling_z']+1.e-7
        same=abs(peer['ceiling_z']-current['ceiling_z'])<=1.e-7
        if higher or (same and index<rank):
            result['ceiling'].append({'polygon':poly,'keep_boundary':False})
    return result


def _planned_window_kind(window):
    x,z,w,h,seed,balcony,floor,detail,spec,sill=window
    kind=(seed//3+seed%5)%6
    if w<1.08:return 'utility'
    if detail==2 and kind==2 and spec['depth']<2.30:return 'utility_wash' if seed%2==0 else 'compact_prep'
    return ['study','reading_nook','dining','bedroom','kitchen_sideboard','bookshelf'][kind]


def _make_building(ctx,record,profile,architecture,details,paths,asset_budget=None,layout_only=False):
    p=dict(profile);points=_clean(record['points']);seed=int(hashlib.sha256(str(record['id']).encode()).hexdigest()[:7],16)
    rng=random.Random(seed);cx,cy=_centroid(points)
    base=float(ctx.ground_height(cx,cy))+.18
    floors=p['floors'];fh=p['fh'];height=floors*fh
    name='B_'+str(record['id'])+'_'+p['style']
    sb=db=rb=shop_rb=None;room_batches=[];diagnostic_room=False
    domain_plans={};domain_groups=[];domain_by_member={};shared_records=[]
    if not layout_only:
        planned,_,_=_make_building(ctx,record,profile,None,None,paths,None,True)
        domain_plans={r['room_id']:r for r in planned['interior_room_plans']}
        domain_groups=room_domains.shared_room_groups(list(domain_plans.values()))
        for members in domain_groups:
            ordered=sorted(members,key=lambda key:(domain_plans[key]['kind']=='window_room',key))
            for key in members:domain_by_member[key]=ordered
    if not layout_only:
        sb=ctx.Batch('COL_'+name,architecture);db=ctx.Batch(name+'_details',details)
        rb=ctx.Batch('IR_'+name+'_Interiors',details)
        rb._cq_metadata={'cq_room_id':str(record['id'])+'_aggregate'}
        shop_rb=ctx.Batch('COL_IR_'+name+'_Shop_envelope',architecture)
        shop_rb._cq_metadata={'cq_room_id':str(record['id'])+'_shop'}
        shop_rb._cq_shop_shell=True
        room_batches=[rb,shop_rb]
    shell=Frame(sb);deco=Frame(db)
    front=_front_edge(points,base,ctx.ground_height,paths)
    # Anchor the occupied ground floor to its selected street entrance, rather
    # than burying the door on the uphill side of a centroid-height slab.
    fa,fb=points[front],points[(front+1)%len(points)]
    fw=math.dist(fa,fb);fu=((fb[0]-fa[0])/fw,(fb[1]-fa[1])/fw);fv=(fu[1],-fu[0])
    front_shop=p['style'] in ('market','noodle','repair','workshop','heritage','artisan','service')
    fx=fw*(.33 if front_shop and fw>12 else .5)
    approach_xy=(fa[0]+fu[0]*fx+fv[0]*1.8,fa[1]+fu[1]*fx+fv[1]*1.8)
    base=float(ctx.ground_height(*approach_xy))+.20
    wall=p['wall'];entrances=[];lights=[];views=[];window_count=0;balcony_count=0;edge_types=[]
    interior_lights=[];interior_assets=[];interior_review_views=[];facade_openings=[];hero_rooms=0;room_envelopes=[];floor_cutouts=[];fixture_layouts=[];room_plans=[];wall_fixture_placements=[]
    interior_tiers={'near_street':0,'middle':0,'distant':0};interior_types={};pending_windows=[]
    def collect_assets(frame,entries,source,metadata=None):
        for entry in entries:
            marker=dict(entry);local_yaw=entry.get('yaw',0.)
            forward=(-frame.u[0]*math.sin(local_yaw)+frame.v[0]*math.cos(local_yaw),
                     -frame.u[1]*math.sin(local_yaw)+frame.v[1]*math.cos(local_yaw))
            marker['position']=[round(c,6) for c in frame.transform(entry['position'])]
            marker['yaw']=math.atan2(forward[0],-forward[1])
            marker['world_forward']=[round(c,6) for c in forward]
            marker['source_forward_axis']='-Y';marker['coordinate_system']='Blender Z-up, metres'
            marker['building_id']=str(record['id']);marker['context']=source
            marker['name']=name+'_Interior_asset_'+str(len(interior_assets))
            if metadata:marker.update(metadata)
            interior_assets.append(marker)
            if asset_budget is not None:asset_budget[0]-=1
    if not layout_only:
        _poly_cap(sb,points,base,'pavement',.14,side_faces=False)
        # Stepped/raked foundation follows the hillside at each perimeter vertex.
        for a,b in zip(points,points[1:]+points[:1]):
            za=min(base-.12,ctx.ground_height(*a)-.14);zb=min(base-.12,ctx.ground_height(*b)-.14)
            sb.quad((a[0],a[1],za),(b[0],b[1],zb),(b[0],b[1],base),(a[0],a[1],base),'stone')
    for edge,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
        width=math.dist(a,b)
        if width<.04:continue
        u=((b[0]-a[0])/width,(b[1]-a[1])/width);v=(u[1],-u[0])
        fs=Frame(sb,(*a,base),u,v);fd=Frame(db,(*a,base),u,v);fi=Frame(rb,(*a,base),u,v);fshop=Frame(shop_rb,(*a,base),u,v)
        is_cut=(abs(a[0])>99.99 and abs(b[0])>99.99) or (abs(a[1])>99.99 and abs(b[1])>99.99)
        if is_cut:
            if not layout_only:fs.box((width/2,-.12,height/2),(width,.24,height),wall)
            edge_types.append('site_boundary');continue
        # A few secondary wings intentionally use a different construction era.
        edge_wall=wall
        if p['style']=='market' and edge%3==2:edge_wall='plaster_grey'
        if p['style']=='courtyard' and edge%3==1:edge_wall='plaster'
        edge_types.append(edge_wall)
        holes=[];windows=[];doors=[]
        bays=max(1,int((width-.7)/p['bay']));pitch=width/bays
        is_front=edge==front
        shop=is_front and p['style'] in ('market','noodle','repair','workshop','heritage','artisan','service')
        # Several buildings have a second side entrance, not four identical fronts.
        entrance=is_front or (width>21 and edge%3==seed%3 and p['style'] in ('workers','blue_apartments','civic','old_tile'))
        door_u=width*(.33 if shop and width>12 else .5)
        # Tiled walk-ups have wider communal entrances; narrow timber houses
        # retain a domestic opening. This changes their ground-floor identity.
        communal=p['style'] in ('workers','old_tile','blue_apartments','cream_residence')
        door_w=min(width-1.0,4.5 if shop else (2.70 if communal else 2.15))
        door_h=2.75 if shop else 2.8
        if entrance and not is_front:
            ep=fd.transform((door_u,1.8,0))
            secondary_rise=base-ctx.ground_height(ep[0],ep[1])-.08
            if not .08<=secondary_rise<=1.4:entrance=False
        if entrance and width>4.2:
            holes.append((door_u-door_w/2,door_u+door_w/2,0,door_h));doors.append((door_u,door_w,door_h,'shop' if shop else 'entry'))
            floor_cutouts.append(_floor_cutout(fd,record['id'],str(record['id'])+'_edge'+str(edge)+'_door',
                'shop' if shop else 'entry',0,door_u-door_w/2,door_u+door_w/2,-2.425,.025,.09,
                (door_u-door_w/2-.015,door_u+door_w/2+.015,-2.430,.025),
                (door_u-door_w/2,door_u+door_w/2,-2.32,.025)))
            room_plans.append({**floor_cutouts[-1],'ceiling_z':base+door_h-.03,'detail':0})
        # Secondary shop is visibly shuttered, giving functional variety.
        shutter=None
        if shop and width>12.7:
            shutter=(width*.77,min(3.1,width*.23),2.55)
            holes.append((shutter[0]-shutter[1]/2,shutter[0]+shutter[1]/2,.03,shutter[2]))
        for fl in range(floors):
            for bay in range(bays):
                x=pitch*(bay+.5)
                local_seed=seed+edge*139+fl*23+bay
                w=min(1.75,pitch-.62)
                if p['style'] in ('civic','clinic','service','restored'):w=min(2.05,pitch-.62)
                if p['style'] in ('artisan','workshop'):w=min(2.40,pitch-.62)
                if p['style'] in ('old_tile','workers'):w=min(1.46,pitch-.72)
                # Altered household glazing and a narrower service/bathroom
                # stack break the mechanically identical window grid while
                # preserving a plausible shared structural bay rhythm.
                service_bay=bays>=4 and bay==((seed+edge)%bays) and p['style'] not in ('civic','clinic','service','artisan','workshop')
                w*=.91+((seed+bay*13+fl//2)%5)*.035
                if w<.50:continue
                h=1.62 if fh<3.3 else (2.05 if p['style'] in ('heritage','civic') else 1.77)
                z=fl*fh+1.20+h/2
                if service_bay and fl>0:
                    w=min(.82,w*.58);h=.86 if p['style']!='contemporary' else 1.15
                    z=fl*fh+1.56+h/2
                if z+h/2>height-.24:continue
                if fl==0 and any(not(x+w/2<l-.2 or x-w/2>r+.2) for l,r,lo,hi in holes):continue
                if fl==0:
                    world=fd.transform((x,0,0));local_ground=ctx.ground_height(world[0],world[1])-base
                    if local_ground>1.0:continue
                # Blank stairwell/bathroom bays are intentional, never one uniform grid.
                if p['style']=='contemporary' and bay%5==2:
                    w*=.55;h=fh-1.0;z=fl*fh+fh/2+.15
                balcony=(fl>0 and not service_bay and width>7 and bay%3==(seed+edge)%3 and p['style'] in ('heritage','brick_home','courtyard_home','blue_apartments','cream_residence'))
                if REVISION>=7 and balcony:
                    # An accessible balcony is tied to the actual storey, not
                    # suspended one metre above it under an ordinary window.
                    h=min(2.36,fh-.55);z=fl*fh+.14+h/2
                # Detail follows the local hillside street level, rather than
                # an absolute building floor number. Uphill ground-level rooms
                # can therefore receive the same care as a main front window.
                world=fd.transform((x,1.25,0))
                sill_above_street=base+z-h/2-ctx.ground_height(world[0],world[1])
                room_detail=2 if -.10<=sill_above_street<=3.35 else (1 if -.60<=sill_above_street<=7.2 else 0)
                floor_z=fl*fh+.12
                room_spec=_room_envelope(fd,x,w,pitch,width,points,edge,local_seed,room_detail,floor_z,doors)
                if room_detail==2:room_envelopes.append({'edge':edge,'u_m':x,'floor_m':floor_z,'sill_above_street_m':sill_above_street,**room_spec})
                floor_cutouts.append(_floor_cutout(fd,record['id'],str(record['id'])+'_edge'+str(edge)+'_window'+str(local_seed),
                    'window_room',fl,x-room_spec['width']/2,x+room_spec['width']/2,-room_spec['depth'],-.23,floor_z))
                room_plans.append({**floor_cutouts[-1],'ceiling_z':base+max(z+h/2+.19,floor_z+2.62),'detail':room_detail})
                holes.append((x-w/2,x+w/2,z-h/2,z+h/2));windows.append((x,z,w,h,local_seed,balcony,floor_z,room_detail,room_spec,sill_above_street));window_count+=1;balcony_count+=int(balcony)
        facade_openings.append({'edge':edge,'a':list(a),'b':list(b),'holes':[list(hole) for hole in holes]})
        if layout_only:continue
        _wall(fs,width,height,holes,edge_wall)
        # Floor construction differs by era: flush ceramic bands / heavy masonry lintels / timber.
        for floor in range(1,floors):
            zz=floor*fh
            band=.16 if p['style'] in ('civic','clinic','restored','courtyard') else .10
            if REVISION>=6 and edge_wall in ('tile','tile_blue','tile_cream'):
                # The ceramic finish normally wraps the slab edge. The old
                # dark projecting strip on every storey made all housing read
                # as the same striped prefab, despite different footprints.
                fd.box((width/2,.006,zz),(width,.022,.038),edge_wall)
            else:
                fd.box((width/2,.025,zz),(width,.10,band),'plaster' if p['style'] in ('heritage','civic','clinic') else 'concrete')
            if p['style']=='contemporary':fd.box((width/2,.11,zz+.15),(width,.24,.12),'offwhite')
        for window in windows:
            pending_windows.append({'frame':fd,'interior_frame':fi,'origin':(*a,base),'tangent':u,'outward':v,
                'front':is_front,'pitch':pitch,'width':width,'edge':edge,'window':window})
        if REVISION>=6:
            _facade_wear(ctx,fd,width,height,holes,seed+edge*701,p['style'])
        # Sparse damp bands under eaves, never the same weather mask on every floor.
        if 'grime_streak' in ctx.MATS and width>2.5 and edge%3!=1:
            gh=min(2.6,height*.25);gw=min(width-.5,3.4+seed%5)
            x=.22+((seed+edge)%3)*max(0,(width-gw-.6)/3)
            fd.quad((x,.013,height-gh),(x,.013,height-.09),(x+gw,.013,height-.09),(x+gw,.013,height-gh),'grime_streak')
        if 'moss_grime' in ctx.MATS and width>4.8 and edge%3==0:
            x=.3;gw=min(2.7,width*.26)
            fd.quad((x,.015,.02),(x,.015,.72),(x+gw,.015,.72),(x+gw,.015,.02),'moss_grime')
        if width>3.5:
            # Gutters and downpipe elbows route around cornices.
            x=.34 if (seed+edge)%2 else width-.37
            pipe_world=fd.transform((x,.18,0))
            pipe_floor=ctx.ground_height(pipe_world[0],pipe_world[1])-base+.11
            pipe_mat='offwhite' if p['style'] not in ('heritage','brick_home') else 'painted_metal'
            fd.pipe([(x+.16,-.12,height+.32),(x+.16,.10,height-.35),(x,.10,height-.35),
                     (x,.10,pipe_floor+.28),(x,.34,pipe_floor+.08),(x+.20,.44,pipe_floor+.08)],.052,pipe_mat,8)
            for zz in range(math.ceil(pipe_floor+.65),int(height),3):
                fd.cylinder((x,.015,zz),(x,.19,zz),.070,'frame',8)
            if edge%2==0:
                fd.pipe([(0,.06,min(3.16,height-.5)),(width*.32,.12,min(3.10,height-.5)),(width*.65,.09,min(3.17,height-.5)),(width,.07,min(3.13,height-.5))],.015,'dark',6)
        if p['style'] in ('civic','clinic','restored') and width>5:
            for x in [.17,width-.17]:fd.box((x,.07,height/2),(.34,.20,height),'plaster')
        for du,dw,dh,kind in doors:
            door_id=str(record['id'])+'_edge'+str(edge)+'_door'
            shared_masks=_shared_domain_masks(fd,door_id,domain_by_member[door_id],domain_plans) if door_id in domain_by_member else None
            wall_fixtures=None
            if kind!='shop':
                wall_fixtures={'meter':_wall_fixture_placement(ctx,fd,width,holes,du-dw*.65,1.5),
                               'plaque':_wall_fixture_placement(ctx,fd,width,holes,du+dw*.7,2.05,.24,.17,.17,.11,True)}
                for family,placement in wall_fixtures.items():
                    wall_fixture_placements.append({'door_id':door_id,'edge':edge,'family':'entry_'+family,**placement})
            shop_assets=_doorway(ctx,fs,fd,du,dw,dh,kind,seed,p.get('sign',''),p['style'],asset_budget is not None and asset_budget[0]>0,fi,fshop,shared_masks,wall_fixtures)
            collect_assets(fd,shop_assets,'shop '+p['style'])
            if kind=='shop' and p['style'] in ('noodle','repair','workshop','heritage','service','artisan'):
                cp=fd.transform((du,2.7,0));cp=(cp[0],cp[1],ctx.ground_height(cp[0],cp[1])+1.73)
                target=fd.transform((du,-1.35,1.38))
                interior_review_views.append({'name':'shop_'+str(record['id']),'title':p['name']+' / fitted shop interior',
                    'position':[round(cp[0],4),round(cp[2],4),round(-cp[1],4)],'target':[round(target[0],4),round(target[2],4),round(-target[1],4)],
                    'fov':66,'coordinate_system':'Godot Y-up, metres','source':'Shop acceptance camera; framed open doorway and fitted contents'})
            threshold=fd.transform((du,.1,.02));approach=fd.transform((du,1.8,0));ground=ctx.ground_height(approach[0],approach[1])+.08
            rise=base-ground
            # Small threshold flight; large topographic access is root's path network.
            n=max(0,min(10,int(math.ceil(rise/.18))))
            if n and rise>.1:
                for k in range(n):
                    top=rise*(n-k)/n
                    fs.box((du,.18+.29*k,ground-base+top/2),(dw+.3,.30,top),'pavement')
            entrances.append({'position':[round(x,4) for x in threshold],'approach':[round(approach[0],4),round(approach[1],4),round(ground,4)],'type':kind,'width_m':dw,'threshold_rise_m':round(rise,3),'steps':n})
            if is_front:
                sign=p.get('sign','山城里')
                bw=min(width-.6,max(4.6,dw+1.8));sx=du
                # Keep lettering wholly above the projecting lintel. The old
                # floor-relative placement bisected text on low shop floors.
                sign_z=max(fh-.34,dh+.63)
                sign_mat='timber' if p['style'] in ('heritage','brick_home','courtyard_home') else ('faded_red' if shop else 'electric_blue')
                fd.box((sx,.17,sign_z),(bw,.25,.58),sign_mat)
                _label(ctx,fd,sign,(sx,.312,sign_z+.01),min(.50,bw/max(4,len(sign))*.71),'sign_cream')
                if sign_mat=='timber':
                    for zz in [sign_z-.29,sign_z+.29]:fd.box((sx,.30,zz),(bw+.08,.045,.05),'wood')
                if shop:
                    _awning(fd,du,2.62,dw+.75,p['style'],seed)
                    # Keep these small groups on the door pier, not in the
                    # protected lane. Contents are specific to the shop type.
                    menu_x=du+dw/2+.43
                    if menu_x+.34<width-.12 and (not shutter or menu_x+.34<shutter[0]-shutter[1]/2-.08):
                        fd.box((menu_x,.085,1.59),(.60,.13,.93),'timber')
                        fd.box((menu_x,.158,1.59),(.51,.025,.83),'dark')
                        menus={'noodle':'小面  8元\n豌杂  12元\n抄手  10元',
                               'repair':'补胎\n换电池\n配钥匙',
                               'workshop':'印刷\n复印\n装订',
                               'heritage':'盖碗茶\n现磨咖啡',
                               'artisan':'手作体验\n旧物修复',
                               'service':'快递取件\n便民服务',
                               'market':'米面粮油\n烟酒饮料'}
                        menu=menus.get(p['style'],'欢迎光临')
                        if '家常菜' in sign:menu='回锅肉\n家常小炒\n蛋炒饭'
                        _label(ctx,fd,menu,(menu_x,.177,1.60),.115,'sign_cream',False)
                        fd.box((menu_x,.19,2.11),(.65,.39,.055),'painted_metal')
                    meter_x=du-dw/2-.43
                    if meter_x-.26>.08 and seed%2==0:
                        placement=_wall_fixture_placement(ctx,fd,width,holes,meter_x,1.58,.275,.315,.3925,.34)
                        wall_fixture_placements.append({'door_id':door_id,'edge':edge,'family':'shop_meter_and_hood',**placement})
                        if placement['placed']:
                            meter_x,meter_z=placement['selected_local']
                            fd.box((meter_x,.12,meter_z),(.45,.24,.63),'painted_metal')
                            fd.box((meter_x,.251,meter_z+.08),(.36,.025,.30),'offwhite')
                            for mx in [meter_x-.10,meter_x+.10]:
                                fd.cylinder((mx,.269,meter_z+.11),(mx,.284,meter_z+.11),.061,'glass',10)
                            fd.box((meter_x,.14,meter_z+.36),(.55,.38,.065),'rust')
                            pipe_bottom=min(.31,meter_z-.42)
                            fd.pipe([(meter_x,.09,meter_z-.34),(meter_x,.09,pipe_bottom),(meter_x+.19,.06,pipe_bottom)],.025,'painted_metal',6)
                lamp=fd.transform((du,-.9,dh-.42))
                lights.append({'name':name+'_warm_door','position':list(lamp),'color':[1.0,.68,.34],'energy':1.35 if shop else .45,'range':4.5 if shop else 2.5})
                cam=fd.transform((du,9.5,1.7));target=fd.transform((du,-.2,min(height*.46,5.6)))
                views.append({'name':name,'position':list(cam),'target':list(target),'fov':60,'source':'authored candidate; root checks occlusion'})
        if shutter:
            su,sw,sh=shutter
            fd.box((su,-.06,sh/2),(sw,.10,sh),'painted_metal')
            for k in range(int(sh/.105)):fd.box((su,.002,.05+k*.105),(sw-.04,.027,.018),'aluminium')
            shutter_sign_z=max(fh-.34,door_h+.63)
            fd.box((su,.10,shutter_sign_z),(sw+.18,.18,.58),'faded_green')
            _label(ctx,fd,p.get('secondary','便 民 小 店'),(su,.205,shutter_sign_z+.01),.30)
            for xx in [su-sw/2-.045,su+sw/2+.045]:fd.box((xx,.035,sh/2),(.08,.12,sh+.06),'frame')
            fd.box((su,.065,.30),(.26,.065,.07),'dark')
            fd.box((su,.025,.08),(sw+.03,.07,.09),'rust')
        if p['style']=='workshop' and is_front:
            fd.box((width-.65,.12,1.25),(.52,.18,.72),'painted_metal')
            fd.pipe([(width-.65,.12,1.65),(width-.65,.12,3.3),(width-.15,.12,3.3)],.035,'rust',8)
    if layout_only:
        return {'id':record['id'],'points':points,'base_m':base,'interior_floor_cutouts':floor_cutouts,'interior_room_plans':room_plans},[],[]
    # Select real furniture across the whole building, before drawing any
    # room. A public side lane can provide a much clearer low-sill view than
    # the downhill corner of the main shop facade.
    eligible=[]
    for job_index,job in enumerate(pending_windows):
        row=job['window'];pt=job['frame'].transform((row[0],1.65,0))
        job['street_distance']=min((_segdist(pt[:2],a,b) for a,b in paths),default=100.)
        if row[7]==2 and row[2]>=1.30 and -.10<=row[9]<=1.75 and (row[4]//3+row[4]%5)%6!=3:
            if job['front'] or job['street_distance']<=3.5:eligible.append(job_index)
    def job_order(index):
        job=pending_windows[index];row=job['window']
        return (not row[8]['expanded'],abs(row[9]-1.10),not job['front'],job['street_distance'])
    hero_limit=2 if isinstance(record['id'],str) else 1
    selected_jobs=set(sorted(eligible,key=job_order)[:hero_limit])
    jobs_by_id={str(record['id'])+'_edge'+str(job['edge'])+'_window'+str(job['window'][4]):index for index,job in enumerate(pending_windows)}
    for members in domain_groups:
        def owner_order(key):
            if domain_plans[key]['kind']!='window_room':return (0,0,0,0,key)
            index=jobs_by_id[key];row=pending_windows[index]['window'];kind=_planned_window_kind(row)
            return (1,index not in selected_jobs,kind not in ('compact_prep','utility_wash'),-row[7],key)
        ordered=sorted(members,key=owner_order);owner=ordered[0]
        kind=_planned_window_kind(pending_windows[jobs_by_id[owner]]['window']) if owner in jobs_by_id else 'shared_entry_foyer'
        shared_records.append({'owner':owner,'members':ordered,'kind':kind,'window_views':sum(key in jobs_by_id for key in ordered),
                               'scope':'Connected corner room containing at least one near-street window; original floor levels and apertures retained'})
        for key in ordered:
            if key not in jobs_by_id:continue
            job=pending_windows[jobs_by_id[key]];shared=_shared_domain_masks(job['frame'],key,ordered,domain_plans)
            shared.update({'owner':owner,'is_owner':key==owner,'members':ordered,'kind':kind})
            job['window'][8]['_shared']=shared
    for job_index in sorted(range(len(pending_windows)),key=lambda index:(index not in selected_jobs,*job_order(index))):
        job=pending_windows[job_index]
        fd=job['frame'];fi=job['interior_frame'];u=job['tangent'];v=job['outward']
        is_front=job['front'];pitch=job['pitch'];width=job['width'];edge=job['edge'];street_distance=job['street_distance']
        x,z,w,h,s,balc,floor_z,room_detail,room_spec,sill_above_street=job['window']
        use_asset=job_index in selected_jobs and asset_budget is not None and asset_budget[0]>0
        asset_slots=min(2,asset_budget[0]) if use_asset else 0
        room_id=str(record['id'])+'_edge'+str(edge)+'_window'+str(s)
        room_metadata={'cq_room_id':room_id,'cq_room_aperture_center':list(fd.transform((x,-.115,z))),
            'cq_room_inward':[-v[0],-v[1],0.],'cq_room_depth':room_spec['depth'],'cq_room_width':room_spec['width'],
            'cq_room_floor_z':base+floor_z,'cq_room_role':'furniture'}
        if room_spec.get('_shared'):room_metadata['cq_room_shared_owner']=room_spec['_shared']['owner']
        target_frame=fi
        if use_asset and not diagnostic_room and str(record['id']) in {'809889624','1335306667','A04','A05'}:
            hero_batch=ctx.Batch('IR_'+name+'_HeroRoom',details)
            hero_batch._cq_metadata=room_metadata.copy();room_batches.append(hero_batch)
            target_frame=Frame(hero_batch,job['origin'],u,v);diagnostic_room=True
        room=_window(fd,x,z,w,h,p['style'],s,balc,room_detail,floor_z,asset_slots,room_spec,target_frame)
        if room.get('fixture_dimensions_m'):
            fixture_layouts.append({'room_id':room_id,'kind':room['kind'],'floor_top_z':base+floor_z,
                'room_width_m':room_spec['width'],'room_depth_m':room_spec['depth'],**room['fixture_dimensions_m']})
        tier=('distant','middle','near_street')[room_detail];interior_tiers[tier]+=1
        interior_types[room['kind']]=interior_types.get(room['kind'],0)+1
        if room.get('assets'):
            collect_assets(fd,room['assets'],'near-street '+room['kind'],room_metadata)
        # Acceptance views belong to the selected real window, independently
        # of whether its appropriate furnishings use a scanned asset. This
        # preserves the R9 IDs/coordinates when a tiny dining bay becomes a
        # working utility room instead of hiding it from the review set.
        if job_index in selected_jobs:
            hero_rooms+=1
            cp=fd.transform((x+.08,1.65,0));cp=(cp[0],cp[1],ctx.ground_height(cp[0],cp[1])+1.74)
            target=fd.transform((x,-.83,floor_z+1.82))
            interior_review_views.append({'name':'window_'+str(record['id'])+'_'+str(hero_rooms),'title':p['name']+' / '+room['kind'],
                'position':[round(cp[0],4),round(cp[2],4),round(-cp[1],4)],'target':[round(target[0],4),round(target[2],4),round(-target[1],4)],
                'fov':64,'coordinate_system':'Godot Y-up, metres','source':'Near-street window acceptance camera; actual room geometry and clear glass'})
        if room.get('lamp') is not None and (is_front or street_distance<=3.5) and not interior_lights and room_detail==2:
            lamp=fd.transform(room['lamp'])
            interior_lights.append({'name':name+'_room_lamp','position':[round(lamp[0],4),round(lamp[2],4),round(-lamp[1],4)],
                'color':[1.0,.89,.73],'energy':.24,'range':2.7,'attenuation':1.35,'shadows':False,
                'coordinate_system':'Godot Y-up, metres','building_id':str(record['id']),'room_kind':room['kind']})
        # Off-centre utilities; no AC units intersect neighboring windows.
        if s%5==0 and pitch>w+1.15 and p['style'] not in ('clinic','civic','service'):
            acx=x+w/2+.47
            if acx+.43<width-.12:_aircon(fd,acx,z-.55,s)
    _roof(ctx,db,points,base,height,p,seed)
    _dedupe_same_faces(sb);_dedupe_same_faces(db)
    shell_objects=sb.finish(.0);detail_objects=db.finish(.0)
    room_objects=[]
    for batch in room_batches:
        _dedupe_same_faces(batch)
        objects=batch.finish(.0) or []
        for ob in objects:
            key=ob.name[len(batch.name)+1:]
            shop_shell=bool(getattr(batch,'_cq_shop_shell',False))
            envelope=shop_shell or key in ('room_wall','room_floor')
            for prop,value in batch._cq_metadata.items():ob[prop]=value
            ob['cq_interior']=True;ob['cq_room_envelope']=envelope
            ob['cq_interior_occluder']=not envelope and not key.startswith('glass')
            ob['cq_room_role']='floor' if key=='room_floor' or (shop_shell and key=='pavement') else ('ceiling' if shop_shell and key=='concrete' else ('walls_and_ceiling' if key=='room_wall' or shop_shell else 'furniture'))
        room_objects.extend(objects)
    _apply_facade_uvs(sb,shell_objects);_apply_facade_uvs(db,detail_objects)
    for ob in (shell_objects or [])+(detail_objects or [])+room_objects:
        ob['building_id']=str(record['id']);ob['architecture_profile']=p['style'];ob['source_geometry']=record['source']
    signature=hashlib.sha256(json.dumps({'points':points,'style':p['style'],'floors':floors,'fh':fh,'roof':p['roof'],'seed':seed},sort_keys=True).encode()).hexdigest()[:16]
    return dict(id=record['id'],name=p['name'],source=record['source'],source_url=record.get('source_url'),points=points,center=[cx,cy],base_m=base,height_m=height,floors=floors,architecture_profile=p['style'],wall_material=wall,roof_form=p['roof'],front_edge=front,facade_materials=edge_types,facade_openings=facade_openings,windows=window_count,balconies=balcony_count,unique_signature=signature,entrances=entrances,interior_detail_counts=interior_tiers,interior_scene_counts=interior_types,interior_room_envelopes=room_envelopes,interior_floor_cutouts=floor_cutouts,interior_fixture_layouts=fixture_layouts,interior_shared_rooms=shared_records,interior_room_plans=room_plans,door_wall_fixtures=wall_fixture_placements,interior_lights=interior_lights,interior_asset_markers=interior_assets,interior_review_views=interior_review_views,estimated=['height','floor count unless explicitly tagged','facades','roof','door position','foundation elevation'],objects=len(shell_objects or [])+len(detail_objects or [])+len(room_objects)),lights,views


def build(ctx,layout_only=False):
    root=Path(ctx.ROOT)
    src=root/'source_data/geo_layout.json'
    if not src.exists():src=root.parent/'chongqing_refined/source_data/geo_layout.json'
    data=json.loads(src.read_text())
    # Required styles gracefully fall back if a surface asset is unavailable.
    fallbacks={'tile_blue':'tile','tile_cream':'tile','plaster_ochre':'plaster','plaster_grey':'plaster','brick_dark':'brick','stone':'concrete','roof_tiles':'brick','timber':'wood','ceramic':'offwhite','ceramic_glaze':'offwhite','room_wall':'plaster','room_floor':'timber'}
    architecture=details=None
    if not layout_only:
        for key,old in fallbacks.items():
            if key not in ctx.MATS:ctx.MATS[key]=ctx.MATS[old]
        architecture=ctx.col('03_District_individual_building_shells')
        details=ctx.col('04_District_facades_roofs_and_lived_detail')
    paths=[]
    for r in data['roads']+data['paths']:
        if r.get('tags',{}).get('tunnel')=='yes':continue
        paths.extend(zip(r['points'],r['points'][1:]))
    paths.extend(zip(SPINE,SPINE[1:]))
    records=[];excluded=[];sources=[]
    for source in data['buildings']:
        points=_clip(source['points'])
        if len(points)<3 or abs(_area(points))<25:
            excluded.append({'id':source['id'],'reason':'Only a tiny source-footprint fragment intersects the district boundary'});continue
        # A clipped 37-storey tower sliver is not a credible stand-alone building.
        if source['id']==809889625:
            excluded.append({'id':source['id'],'reason':'37-storey source tower lies almost entirely outside area; do not render a thin cut tower as an in-area house'});continue
        sources.append({'id':source['id'],'points':points,'source':'OpenStreetMap footprint; architecture independently authored','source_url':source['source_url']})
    infill_checks=[]
    for p in INFILL:
        x0,y0,x1,y1=p['bounds'];points=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        collides=[r['id'] for r in sources if _intersects(points,r['points'])]
        # Check full edges along the protected spine, not only its vertices.
        spine_distance=min(_segdist((x,y),a,b) for x,y in points for a,b in zip(SPINE,SPINE[1:]))
        crosses=any(_inside(a,points) or _inside(b,points) for a,b in zip(SPINE,SPINE[1:]))
        ok=not collides and spine_distance>=3.9 and not crosses
        infill_checks.append({'id':p['id'],'source_overlap':collides,'spine_corner_clearance_m':round(spine_distance,3),'accepted':ok})
        if ok:sources.append({'id':p['id'],'points':points,'source':'Original curated infill; no claim of surveyed building position'})
        else:excluded.append({'id':p['id'],'reason':'Rejected infill collision/route clearance','checks':infill_checks[-1]})
    lights=[];views=[];interior_lights=[];interior_assets=[];interior_review_views=[];asset_budget=[36]
    byid={p['id']:p for p in INFILL}
    for record in sources:
        profile=PROFILES[record['id']] if isinstance(record['id'],int) else byid[record['id']]
        rec,li,vi=_make_building(ctx,record,profile,architecture,details,paths,asset_budget,layout_only)
        records.append(rec);lights+=li;views+=vi
        if layout_only:continue
        interior_lights.extend(rec['interior_lights']);interior_assets.extend(rec['interior_asset_markers'])
        interior_review_views.extend(rec['interior_review_views'])
        print('CQ03_ARCH',record['id'],rec['architecture_profile'],rec['windows'],rec['objects'],flush=True)
    floor_cutouts=[r for building in records for r in building['interior_floor_cutouts']]
    if layout_only:return {'buildings':records,'interior_floor_cutouts':floor_cutouts}
    result={'buildings':records,'lights':lights,'views':views,'excluded':excluded,'checks':{'unique_geometry_signatures':len({r['unique_signature'] for r in records}),'building_count':len(records),'architecture_profile_count':len({r['architecture_profile'] for r in records}),'all_source_footprints_distinct':len({r['unique_signature'] for r in records})==len(records),'infill':infill_checks},'provenance':'OSM XY retained; all roof/facade/height/infill compositions authored from varied Chongqing construction motifs. Photos used for observation only; no photograph pixels or Google assets are included.'}
    result['interior_floor_cutouts']=floor_cutouts
    result['interior_lights']=interior_lights
    result['interior_asset_markers']=interior_assets
    result['interior_review_views']=interior_review_views
    result['interior_provenance']=interiors.PROVENANCE
    result['checks']['interior_asset_budget']=36
    result['checks']['interior_asset_markers']=len(interior_assets)
    result['checks']['interior_rooms']=sum(r['windows'] for r in records)
    result['checks']['expanded_near_street_rooms']=sum(sum(room['expanded'] for room in r['interior_room_envelopes']) for r in records)
    (root/'architecture_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def plan_interior_floor_cutouts(root,ground_height):
    """Read current source layout before terrain meshing, without any Blender.

    The original ground function remains the architectural datum. This pass
    uses the very same bay, doorway and room-fit rules as the full build, but
    produces no geometry, material, collection, output file or altered datum.
    All storeys are included because an uphill street can reach a higher one.
    Consumers lower terrain only where it would pass through a real floor.
    """
    from types import SimpleNamespace
    ctx=SimpleNamespace(ROOT=Path(root),ground_height=ground_height)
    return build(ctx,layout_only=True)['interior_floor_cutouts']
