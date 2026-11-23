"""Retile a convex cut in the existing slope. The old pavement inside the cut is removed."""
import math,bmesh,bpy
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from site_data import scene,here,Surfaces,save,game
# Bottom perimeter follows the uphill pavement a handspan inside the existing kerb.
corners=[(35,-79.90),(43,-77.75),(47,-76.58),(52,-74.90),(60,-70.78),(68,-65.94),(68,-59.25),(35,-59.25)]
poly=[Vector(p) for p in corners]
edges=[(a,b,(b-a).normalized()) for a,b in zip(poly,poly[1:]+poly[:1])]
def signed(p,e):return e[2].cross(p-e[0])
def distance(p):return min(signed(p,e) for e in edges)
def smooth(t):
    t=min(1.,max(0.,t));return t*t*(3.-2.*t)
names=['COL_D18_NanquShoulder','D18_RoadEndBedding','COL_Road_176034707_0_pavement','COL_R24_JunctionStem_R24_junction_stem']+[o.name for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_Terrain_200m')]
support=Surfaces([scene.objects[n] for n in names if not ('Bedding' in n or 'JunctionStem' in n)])
for n in names:
    if n not in ('D18_RoadEndBedding','COL_R24_JunctionStem_R24_junction_stem'):support.tree(scene.objects[n])
def old(p):
    rows=support.down(p.x,p.y,18,13)
    if not rows:
        for x,y in [(0,.001),(.001,0),(-.001,0),(0,-.001)]:
            rows=support.down(p.x+x,p.y+y,18,13)
            if rows:break
    if not rows:raise ValueError(('no surface at edge',list(p)))
    return rows[0][0]
tyres=__import__('json').loads((game/'assets/frontage_r24/frontage.json').read_text('utf8'))['parked_contacts']['Parked_car_46_-78']
coords=np.array(tyres);grade=np.linalg.lstsq(np.column_stack((coords[:,0],-coords[:,2],np.ones(len(coords)))),coords[:,1],rcond=None)[0]
# Recover the broad hillside fall without copying the angles of its triangles. The car
# fixes a local bearing plane only in its parking bay, not the entire shoulder.
grid_x,grid_y=30.,-85.
cell=.4
h=np.zeros((78,111),float);mask=np.zeros_like(h)
for iy,ix in np.ndindex(h.shape):
    hit=support.down(grid_x+ix*cell,grid_y+iy*cell,18,13)
    if hit:h[iy,ix]=hit[0][0];mask[iy,ix]=1.
k=np.exp(-.5*(np.arange(-15,16)/4.8)**2);k/=k.sum()
def broad(a):
    for axis in (0,1):a=np.apply_along_axis(lambda row:np.convolve(np.pad(row,15,'edge'),k,'valid'),axis,a)
    return a
guide=broad(h)/np.maximum(broad(mask),.00001)
def datum(p):
    gx=(p.x-grid_x)/cell;gy=(p.y-grid_y)/cell;i=int(gx);j=int(gy);u=gx-i;v=gy-j
    ground=(1-v)*((1-u)*guide[j,i]+u*guide[j,i+1])+v*((1-u)*guide[j+1,i]+u*guide[j+1,i+1])
    # All four contacts fit inside this ellipse. Outside it the long grade follows the hillside.
    radius=math.hypot((p.x-52.)/2.65,(p.y+72.)/2.70)
    bearing=1.-smooth((radius-.82)/1.65)
    wheel_plane=grade[0]*p.x+grade[1]*p.y+grade[2]
    return float(ground+(wheel_plane-ground)*bearing)
def design(p):
    # Extend the measured tie height inwards along its edge normal, fading over walking distance.
    delta=0.;weights=0.;total=1.
    for a,b,u in edges:
        q=a+u*max(0.,min((b-a).length,(p-a).dot(u)))
        dist=(p-q).length
        w=1.-smooth(dist/2.35)
        if w==0.:continue
        if dist<.00012:return old(q)
        inverse=w*w/(dist*dist+.000001)
        delta+=(old(q)-datum(q))*inverse;weights+=inverse;total*=1.-w
    return datum(p)+(delta/weights*(1.-total) if weights else 0.)
def contains(f):
    xs=[v.co.x for v in f.verts];ys=[v.co.y for v in f.verts]
    return min(xs)<68.0001 and max(xs)>34.9999 and min(ys)<-59.249 and max(ys)>-79.901
changed={};edge_pts=[set([0.,(b-a).length]) for a,b,u in edges]
for name in names:
    ob=scene.objects[name];mesh=ob.data;bm=bmesh.new();bm.from_mesh(mesh);bm.transform(ob.matrix_world)
    pool={f for f in bm.faces if contains(f)}
    for a,b,u in edges:
        if not pool:break
        n=Vector((-u.y,u.x,0));c=Vector((a.x,a.y,0))
        both=[f for f in pool if min((v.co-c).dot(n) for v in f.verts)<-.000011 and max((v.co-c).dot(n) for v in f.verts)>.000011]
        if both:
            geo=set(both)
            for f in both:geo.update(f.edges);geo.update(f.verts)
            result=bmesh.ops.bisect_plane(bm,geom=list(geo),dist=.000002,plane_co=c,plane_no=n)
            pool.update(f for f in result['geom'] if isinstance(f,bmesh.types.BMFace))
        pool={f for f in pool if f.is_valid and (f.calc_center_median()-c).dot(n)>-.000009}
    if pool:
        for f in pool:
            for v in f.verts:
                p=v.co.xy
                for i,(a,b,u) in enumerate(edges):
                    if abs(signed(p,edges[i]))<.00004:edge_pts[i].add(max(0.,min((b-a).length,(p-a).dot(u))))
        changed[name]=len(pool)
        bmesh.ops.delete(bm,geom=list(pool),context='FACES')
        bm.transform(ob.matrix_world.inverted());bm.to_mesh(mesh);mesh.update()
    bm.free()
ring=[]
for (a,b,u),ds in zip(edges,edge_pts):
    length=(b-a).length
    ds.update(i*length/math.ceil(length/.40) for i in range(math.ceil(length/.40)))
    for t in sorted(ds):
        if t>length-.0002:continue
        p=a+u*t
        if ring and (p-ring[-1]).length<.00018:continue
        ring.append(p)
points=ring.copy()
for iy in range(-160,-117):
    for ix in range(70,137):
        p=Vector((ix*.5+.25*(iy%2),iy*.5))
        if distance(p)>.19:points.append(p)
vertices,_,faces,*_=delaunay_2d_cdt(points,[],[list(range(len(ring)))],1,.000035)
vs=[(p.x,p.y,design(p)) for p in vertices]
mesh=bpy.data.meshes.new('Fork graded public pavement');mesh.from_pydata(vs,[],faces);mesh.update()
obj=bpy.data.objects.new('COL_Terrace21_Fork',mesh);scene.collection.objects.link(obj)
mesh.materials.append(bpy.data.materials.new('Terrace21_floor'))
for f in mesh.polygons:f.use_smooth=True
uv=mesh.uv_layers.new(name='PavingMetres')
for l in mesh.loops:uv.data[l.index].uv=mesh.vertices[l.vertex_index].co.xy
area=sum(f.area*abs(f.normal.z) for f in mesh.polygons)
assert 380<area<540 and min(f.normal.z for f in mesh.polygons)>.5,(area,min(f.normal.z for f in mesh.polygons))
record={'cut':changed,'outline':corners,'xy_area_m2':area,'design_plane':grade.tolist(),'perimeter_samples':len(ring),'faces':len(faces)}
# The previous terrain uses two shader families with different tangent bases. Inside the
# fully resurfaced neighbourhood both sides of the cut carry the very same finish.
finish=mesh.materials[0];tied={}
for key in ['COL_Terrain_200m_pavement','COL_Terrain_200m_yard_concrete','COL_Road_176034707_0_pavement','COL_D18_NanquShoulder']:
    surface=scene.objects[key];data=surface.data;assigned=0;slot=len(data.materials)
    data.materials.append(finish)
    for f in data.polygons:
        if f.normal.z<.78:continue
        world=surface.matrix_world@f.center
        if not (30.<world.x<82. and -82.<world.y< -41.):continue
        if key=='COL_D18_NanquShoulder' and not data.materials[f.material_index].name.startswith('R18_paver'):continue
        f.material_index=slot;assigned+=1
    if assigned:changed.setdefault(key,0);tied[key]=assigned
    data.update()
record['joined_finish_faces']=tied
save('grade.json',record)
