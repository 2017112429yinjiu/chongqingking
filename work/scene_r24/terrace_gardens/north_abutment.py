"""Close the exposed downhill edge of the north street and bed the actual landing crossing."""
import bpy,bmesh,math,bisect
from mathutils import Vector
from site_data import scene,Surfaces,save
from grade import changed,smooth
deck=scene.objects['COL_Road_734116597_0_pavement']
street=scene.objects['COL_Road_734116597_0_asphalt']
terrain=[scene.objects[n] for n in ('COL_Terrain_200m_pavement','COL_Terrain_200m_yard_concrete')]
source=Surfaces(terrain);tops=Surfaces([street,deck])
for t in terrain:source.tree(t)
# Each four-corner pavement station shares its outer pair with the next station.
edges=[]
for f in deck.data.polygons:
    if f.normal.z<.9:continue
    pts=[deck.matrix_world@deck.data.vertices[i].co for i in f.vertices]
    if len(pts)!=4:continue
    b,c=pts[:2]
    if -30<b.x<-7 and abs(b.y-(86.431-(b.x+29.669)*.58885))<.28 and 0<c.x-b.x<1.85:edges.append((b,c))
edges.sort(key=lambda e:e[0].x)
assert len(edges)>=22 and all((b[1]-c[0]).length<.002 for b,c in zip(edges,edges[1:]))
a0=edges[0][0];axis=(edges[5][1].xy-a0.xy).normalized();up=Vector((-axis.y,axis.x))
def uv(v):return ((v.xy-a0.xy).dot(axis),(v.xy-a0.xy).dot(up))
def floor(p,default):
    hits=source.down(p.x,p.y,36,8)
    return hits[0][0] if hits else default
def height(p):
    x=p.x
    i=max(0,min(len(edges)-1,bisect.bisect_right([b.x for b,c in edges],x)-1))
    b,c=edges[i];t=(x-b.x)/(c.x-b.x)
    return b.z+(c.z-b.z)*t
def new_z(p):
    station,d=uv(p)
    if not 4.<station<17. or not -8.6<d<5.0:return p.z
    w=smooth((station-4.)/2.)*(1.-smooth((station-14.)/3.))
    toe=a0.xy+axis*station;lip=height(toe)
    # Slab rises to the narrow pavement. The outside land stays below its outer edge.
    if d<=.06:
        # Carry the rise over the full approach rather than balancing it on the last few slabs.
        bottom=floor(toe-up*8.6,lip-1.4)
        t=min(1.,max(0.,(d+8.6)/8.6))
        target=bottom+(lip-.023-bottom)*t
        return p.z+(target-p.z)*w*smooth((d+8.6)/1.8)
    hits=tops.down(p.x,p.y,35,7)
    if not hits:return p.z
    limit=hits[0][0]-.055
    gutter=1.-smooth((d-4.1)/.9)
    return p.z-w*gutter*max(0.,p.z-limit)
counts={}
for ob in terrain:
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
    pool=[f for f in bm.faces if min(v.co.x for v in f.verts)<-11 and max(v.co.x for v in f.verts)>-31 and min(v.co.y for v in f.verts)<95 and max(v.co.y for v in f.verts)>68]
    for direction,values in [(axis,[3.7+i*.41 for i in range(35)]),(up,[-8.7+i*.36 for i in range(40)]+[0.,.06,1.15,1.24])]:
        n=Vector((direction.x,direction.y,0.))
        for val in values:
            c=Vector((a0.x+val*direction.x,a0.y+val*direction.y,0.))
            crossing=[f for f in pool if f.is_valid and min((v.co-c).dot(n) for v in f.verts)<-.00001 and max((v.co-c).dot(n) for v in f.verts)>.00001]
            if not crossing:continue
            geo=set(crossing)
            for f in crossing:geo.update(f.verts);geo.update(f.edges)
            result=bmesh.ops.bisect_plane(bm,geom=list(geo),dist=.000001,plane_co=c,plane_no=n)
            pool=list({f for f in pool if f.is_valid}|{f for f in result['geom'] if isinstance(f,bmesh.types.BMFace)})
    count=0
    for v in {v for f in pool if f.is_valid for v in f.verts}:
        h=new_z(v.co)
        if abs(h-v.co.z)>.00001:v.co.z=h;count+=1
    if count:bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update();changed.setdefault(ob.name,0);counts[ob.name]=count
    bm.free()
ground=Surfaces(terrain);vs=[];faces=[];uvs=[];chain=0.;measures=[]
for b,c in edges:
    edge=c-b;length=edge.xy.length
    for k in range(4):
        p=b.lerp(c,k/4.);q=b.lerp(c,(k+1)/4.)
        lo=[]
        for r in [p,q]:
            s=ground.down(r.x-up.x*.015,r.y-up.y*.015,35,7)
            if not s:raise ValueError(('north retaining toe',r))
            lo.append(min(r.z-.026,s[0][0]-.048))
        index=len(vs)
        vs.extend([(p.x,p.y,lo[0]),(q.x,q.y,lo[1]),tuple(q),tuple(p)])
        faces.append(tuple(range(index,index+4)))
        uvs.extend([(chain,lo[0]),(chain+length*.25,lo[1]),(chain+length*.25,q.z),(chain,p.z)])
        measures.append([p.x,p.y,p.z,p.z-lo[0]-.048]);chain+=length*.25
mesh=bpy.data.meshes.new('North road retaining masonry');mesh.from_pydata(vs,[],faces);mesh.update()
mesh.materials.append(bpy.data.materials.new('Terrace21_retaining'))
layer=mesh.uv_layers.new(name='WallMetres')
for i,v in enumerate(uvs):layer.data[i].uv=v
name='COL_Terrace21_NorthRetaining';ob=bpy.data.objects.new(name,mesh);scene.collection.objects.link(ob)
save('north_repair.json',{'length':chain,'terrain':counts,'sections':measures,'crossing_station_m':[6.,14.]})
