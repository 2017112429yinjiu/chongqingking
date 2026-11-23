"""A recessed walking route at the stepped courtyard and a single carriageway around the blue flats."""
import math,json,bmesh,bpy
from mathutils import Vector
from roads import scene,asset,changed,road_record
from survey import Surfaces
east=[[49.,-19.],[49.70,-16.53],[50.45,-13.80],[50.20,-11.80],[48.60,-9.53],[46.30,-7.60],[43.17,-5.25],[40.20,-2.88],[38.40,-.8],[35.,5.]]
(asset/'east_passage.json').write_text(json.dumps(east),'utf8')
a=Vector((78.482,22.4685));u=(Vector((113.0618,-18.9207))-a).normalized();n=Vector((-u.y,u.x))
def xy(s,d):return a+u*s+n*d
def sd(p):
    d=Vector(p[:2])-a;return d.dot(u),d.dot(n)
s0,s1=.9871,25.665;L=s1-s0
def centre(s):return 5.1*math.sin(math.pi*max(0.,min(1.,(s-s0)/L)))**2
def high(s):return 4.98+5.15*max(0.,min(1.,(s-s0)/7.3,(s1-s)/7.3))
left=-5.05
corners=[(s0,left),(s1,left),(s1,high(s1)),(s1-7.3,high(s1-7.3)),(s0+7.3,high(s0+7.3)),(s0,high(s0))]
terrain_obs=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_Terrain_200m')]
road_obs=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Road_734116595_0')]
terrain=Surfaces(terrain_obs);original=Surfaces(road_obs)
for o in road_obs:original.tree(o)
for o in terrain_obs:terrain.tree(o)
def level(surface,p):
    h=surface.down(*p,31,17);return h[0][0] if h else None
def ground(s,d):
    h=level(terrain,xy(s,d));assert h is not None,(s,d,xy(s,d))
    return h
def profile(s,d):
    h=level(original,xy(s,d));return ground(s,d) if h is None else h
shore=[xy(s,d) for s,d in corners]
def clip(ob):
    if not ob.data.vertices:return 0
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
    def in_area(f):
        if max(v.co.z for v in f.verts)<19 or min(v.co.z for v in f.verts)>28:return False
        vs=[v.co for v in f.verts]
        return not(max(v.x for v in vs)<72 or min(v.x for v in vs)>100 or max(v.y for v in vs)<-2 or min(v.y for v in vs)>32)
    pool=[f for f in bm.faces if in_area(f)]
    for l,r in zip(shore,shore[1:]+shore[:1]):
        norm=Vector((l.y-r.y,r.x-l.x,0)).normalized();p=Vector((*l,0));new=[]
        for f in pool:
            if not f.is_valid:continue
            ds=[(v.co-p).dot(norm) for v in f.verts]
            if max(ds)<.000003:continue
            if min(ds)>=-.000003:new.append(f);continue
            result=bmesh.ops.bisect_plane(bm,geom=[f,*f.verts,*f.edges],plane_co=p,plane_no=norm,dist=.000001)
            split={q for q in result['geom'] if isinstance(q,bmesh.types.BMFace) and q.is_valid}
            if f.is_valid:split.add(f)
            new.extend(q for q in split if (q.calc_center_median()-p).dot(norm)>-.000002)
        pool=new
    if pool:
        bmesh.ops.delete(bm,geom=pool,context='FACES');bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update();changed.add(ob.name)
    bm.free();return len(pool)
cuts={}
obsolete=[scene.objects['COL_R23_PathFoundations']]
for ob in terrain_obs+road_obs+obsolete:
    count=clip(ob)
    if count:cuts[ob.name]=count
assert 'COL_Road_734116595_0_asphalt' in cuts
stations=set([s0,s0+7.3,s1-7.3,s1]+[s0+L*k/93 for k in range(94)])
end_offsets=set()
for ob in terrain_obs+road_obs:
    if ob.name not in cuts:continue
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co
        if not 74<p.x<101 or not -2<p.y<32:continue
        s,d=sd(p)
        if s0<s<s1 and min(abs(d-left),abs(d-high(s)))<.003:stations.add(s)
        if abs(s-s0)<.003 or abs(s-s1)<.003:
            if left<d<4.98:end_offsets.add(d)
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3.-2.*t)
def unique(items,gap):
    out=[]
    for v in sorted(items):
        if not out or v-out[-1]>gap:out.append(v)
    return out
stations=unique(stations,.044);stations[0]=s0;stations[-1]=s1
# Offset columns travel with the carriageway, while the apron edges follow the old terrain triangles.
relative=unique([-3.78,-3.74,-3.42,-2.76,-2.65,-2.61,-2.6,-2.56,-2.53,-2.49,-1.3,0,1.3,2.49,2.53,2.56,2.60,2.61,2.65,2.76,3.42,3.74,3.78]+[v for v in end_offsets if -3.77<v<3.77],.016)
columns=[('l',i/10) for i in range(10)]+[('s',v) for v in relative]+[('r',.5),('r',1)]
verts=[];faces=[];materials=[];centres=[];fit=[]
for j,s in enumerate(stations):
    c=centre(s);p=xy(s,c);hi=high(s)
    # Longitudinal grade is fixed by the intact road at both surveyed ends.
    f=(s-s0)/L;datum=profile(s0-.005,0)*(1-f)+profile(s1+.005,0)*f
    centres.append(list(p))
    for kind,k in columns:
        if kind=='s':d=c+k
        elif kind=='l':d=left+((c+relative[0])-left)*k
        else:d=c+relative[-1]+(hi-c-relative[-1])*k
        g=ground(s,d);p=xy(s,d);ad=abs(d-c)
        base=datum-.012*min(ad,2.6)+.022*max(0.,min(ad-2.6,1.16))
        if d<c+relative[0]:w=smooth((d-left)/(c+relative[0]-left))
        elif d>c+relative[-1]:w=smooth((hi-d)/(hi-c-relative[-1]))
        else:w=1.
        val=g+(base-g)*w
        for end,direction in [(s0,-1),(s1,1)]:
            dist=abs(s-end)
            if dist<2.8:
                edge=profile(end+direction*.006,d-c);val+=((edge-val)*(1-smooth(dist/2.8))*w)
        # The older downhill flat has an entrance immediately inside the bend. Preserve its real sill.
        gate=Vector((84.1024,8.6873));wall_t=Vector((6.4158,7.6594)).normalized()
        wall_n=Vector((wall_t.y,-wall_t.x));delta=p-gate;front=delta.dot(wall_n)
        fit_weight=(1-smooth((abs(delta.dot(wall_t))-1.62)/1.20))*(1-smooth((front-1.05)/2.10))*smooth((front+.70)/.65)
        if fit_weight>0:val+=(23.690+max(0.,front)*.010-val)*fit_weight
        verts.append((*p,val))
    if j:
        for i in range(len(columns)-1):
            off=(relative[0] if columns[i][0]=='l' else relative[-1] if columns[i][0]=='r' else columns[i][1])
            off2=(relative[0] if columns[i+1][0]=='l' else relative[-1] if columns[i+1][0]=='r' else columns[i+1][1])
            m=0 if abs((off+off2)*.5)<2.6 else 1
            a0=(j-1)*len(columns)+i;b0=j*len(columns)+i
            for tri in [(a0,b0,b0+1),(a0,b0+1,a0+1)]:faces.append(tri);materials.append(m)
name='COL_Yard20_CornerSurface';mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
for suffix in ('asphalt','pavement'):mesh.materials.append(scene.objects['COL_Road_734116595_0_'+suffix].data.materials[0])
uv=mesh.uv_layers.new(name='SurfaceMetres')
for poly,index in zip(mesh.polygons,materials):
    poly.material_index=index;poly.use_smooth=True
    for li in poly.loop_indices:uv.data[li].uv=mesh.vertices[mesh.loops[li].vertex_index].co.xy
ob=bpy.data.objects.new(name,mesh);scene.collection.objects.link(ob)
(asset/'blue_block_bend.json').write_text(json.dumps(centres),'utf8')
road_record['blue_corner']={'cut':cuts,'shared_faces':len(faces),'bypassed_length_m':L,'width_m':5.2,'highest_offset_m':5.10}
