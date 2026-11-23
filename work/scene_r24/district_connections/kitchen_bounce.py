"""Bake room-scale daylight access and short-range contact into the fitted surfaces."""
def hero_face(name,coords):
    if name in ('D18_NoodleKitchen','COL_D18_NoodleEntry'):return True
    if name not in ('D18_BackRoomFurnishings','COL_D18_RoomShells'):return False
    centre=sum((Vector(c) for c in coords),Vector())/len(coords)
    return -26.7<centre.x<-21.96 and -67.95<centre.y<-61.96 and 11.28<centre.z<14.

def subdivide_kitchen():
    for name in list(batches):
        if name not in ('D18_NoodleKitchen','COL_D18_NoodleEntry','D18_BackRoomFurnishings','COL_D18_RoomShells'):continue
        vs,polys,keys=batches.pop(name)
        for inds,key in zip(polys,keys):
            coords=[Vector(vs[i]) for i in inds]
            if len(coords)!=4 or not hero_face(name,coords):
                face(name,coords,key);continue
            a,b,c,d=coords
            nx=max(1,math.ceil(max((b-a).length,(c-d).length)/.085))
            ny=max(1,math.ceil(max((d-a).length,(c-b).length)/.085))
            for j in range(ny):
                for i in range(nx):
                    def sample(t,u):return a.lerp(b,t).lerp(d.lerp(c,t),u)
                    face(name,[sample(i/nx,j/ny),sample((i+1)/nx,j/ny),sample((i+1)/nx,(j+1)/ny),sample(i/nx,(j+1)/ny)],key)

def bake_kitchen_occlusion():
    low=Vector((-27.25,-68.48,10.55));high=Vector((-21.3,-60.6,15.0))
    vertices=[];polygons=[]
    for obj in scene.objects:
        if obj.type!='MESH' or obj.hide_render or obj.name in layout['retired'] or obj.name.startswith('COLH_'):continue
        lo,hi=extent(obj)
        if any(hi[k]<low[k] or lo[k]>high[k] for k in range(3)):continue
        mv=obj.matrix_world;ws=[mv@v.co for v in obj.data.vertices];index={}
        for poly in obj.data.polygons:
            pts=[ws[i] for i in poly.vertices]
            if any(max(p[k] for p in pts)<low[k] or min(p[k] for p in pts)>high[k] for k in range(3)):continue
            buf=[]
            for i in poly.vertices:
                if i not in index:index[i]=len(vertices);vertices.append(ws[i])
                buf.append(index[i])
            polygons.append(buf)
    tree=BVHTree.FromPolygons(vertices,polygons)
    cache={};samples=22
    offsets=[]
    for i in range(samples):
        z=math.sqrt((i+.5)/samples);radius=math.sqrt(1-z*z);ang=i*2.3999632297
        offsets.append((radius*math.cos(ang),radius*math.sin(ang),z))
    portals=[Vector((x,-61.90,z)) for x in [-25.9,-24.1,-22.6] for z in [12.21,13.26]]
    def value(p,n):
        key=tuple(round(v*225) for v in p)+tuple(round(v*12) for v in n)
        if key in cache:return cache[key]
        e=n.cross(Vector((0,0,1)) if abs(n.z)<.92 else Vector((0,1,0))).normalized()
        b=n.cross(e);at=p+n*.0045
        proximity=0.
        for dx,dy,dz in offsets:
            direction=e*dx+b*dy+n*dz
            dist=tree.ray_cast(at,direction,.82)[3]
            proximity+=1. if dist is None else min(1.,(dist/.82)**.57)
        ao=proximity/samples
        window=0.
        for source in portals:
            vec=source-at;distance=vec.length;vec.normalize()
            if n.dot(vec)>.01 and tree.ray_cast(at,vec,max(.001,distance-.012))[0] is None:
                window+=max(.16,n.dot(vec))
        depth=max(0.,-61.975-p.y)
        light=.50+.36*window/len(portals)+.10*math.exp(-.53*depth)
        # Local lighting remains dynamic. Static response keeps surfaces out of direct daylight from glowing.
        out=min(1.,max(.083,(.25+.75*ao)*light))
        cache[key]=out
        return out
    for name in ('D18_NoodleKitchen','COL_D18_NoodleEntry','D18_BackRoomFurnishings','COL_D18_RoomShells'):
        obj=scene.objects[name];mesh=obj.data
        if name=='D18_NoodleKitchen':
            nearby=defaultdict(list)
            def poskey(v):return tuple(round(n*5000) for n in v)
            for pol in mesh.polygons:
                for i in pol.vertices:nearby[poskey(mesh.vertices[i].co)].append(pol.normal.copy())
            normals=[None]*len(mesh.loops)
            for pol in mesh.polygons:
                unit=pol.normal.copy();pol.use_smooth=True
                for i,li in zip(pol.vertices,pol.loop_indices):
                    neighbours=nearby[poskey(mesh.vertices[i].co)]
                    normals[li]=sum((n for n in neighbours if n.dot(unit)>.89),Vector()).normalized()
            mesh.normals_split_custom_set(normals)
        attr=mesh.color_attributes.new(name='CookhouseBounce',type='FLOAT_COLOR',domain='CORNER')
        mesh.color_attributes.active_color=attr
        for poly in mesh.polygons:
            coords=[mesh.vertices[i].co for i in poly.vertices]
            active=hero_face(name,coords);unit=poly.normal.normalized()
            for li,at in zip(poly.loop_indices,coords):
                v=value(at,unit) if active and unit.length>.9 else 1.
                attr.data[li].color=(v,v,v,1.)
    print('KITCHEN_BOUNCE',len(cache),'samples',samples,'range',min(cache.values()),max(cache.values()),flush=True)
