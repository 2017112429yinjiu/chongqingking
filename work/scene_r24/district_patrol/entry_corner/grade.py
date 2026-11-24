"""Join the courtyard to the two complete stair ends on their own nosing lines."""
sys.path.insert(0,str(here.parents[1]/'project/chongqing_blender_v05'))
from district_layout import ground_height


def cut_flight(obj, ring, bottom, top):
    """Split all adjoining faces together, then remove the interior of the junction."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    xy = np.asarray(ring)
    lower = (*xy.min(axis=0), bottom)
    upper = (*xy.max(axis=0), top)
    candidates = {f for f in bm.faces if all(
        max(v.co[k] for v in f.verts) >= lower[k] - .001 and
        min(v.co[k] for v in f.verts) <= upper[k] + .001 for k in range(3))}
    planes = [(Vector((*a, 0)), Vector((a.y-b.y, b.x-a.x, 0)).normalized())
              for a, b in zip(ring, ring[1:] + ring[:1])]
    planes += [(Vector((0, 0, bottom)), Vector((0, 0, 1))),
               (Vector((0, 0, top)), Vector((0, 0, -1)))]
    for origin, normal in planes:
        straddling = set()
        for f in candidates:
            distances = [(v.co-origin).dot(normal) for v in f.verts]
            if min(distances) < -.00001 and max(distances) > .00001:
                straddling.add(f)
        if straddling:
            geom = straddling | {e for f in straddling for e in f.edges} | {v for f in straddling for v in f.verts}
            result = bmesh.ops.bisect_plane(bm, geom=list(geom), plane_co=origin, plane_no=normal, dist=.000002)
            candidates = {f for f in candidates if f.is_valid}
            candidates.update(g for g in result['geom'] if isinstance(g, bmesh.types.BMFace) and g.is_valid)
    dead = []
    for f in candidates:
        center = f.calc_center_median()
        if all((center-p).dot(n) >= -.00001 for p, n in planes):
            dead.append(f)
    if dead:
        bmesh.ops.delete(bm, geom=dead, context='FACES')
        finish(obj, bm)
    else:
        bm.free()
    return len(dead)


def regrade_turn(name, lower, upper, rise, padding, bend=None):
    # Find a transverse edge on the original structural tread, in world metres.
    def portal(spec):
        obj_name, centre, travel = spec
        obj = scene.objects[obj_name]
        center = Vector(centre)
        forward = Vector(travel).normalized()
        options = []
        for f in obj.data.polygons:
            if f.normal.z < .86:continue
            vs = [(obj.matrix_world @ obj.data.vertices[j].co).xy for j in f.vertices]
            for a,b in zip(vs,vs[1:]+vs[:1]):
                edge=b-a
                if edge.length<1.1 or abs(edge.normalized().dot(forward))>.18:continue
                options.append((((a+b)*.5-center).length, a.copy(), b.copy()))
        distance,a,b=min(options,key=lambda item:item[0])
        if distance>.11:raise ValueError((name,obj_name,'missing doorway',distance))
        if (b-a).cross(forward)<0:a,b=b,a
        return a,b

    lower_direction,upper_direction = Vector(lower[2]).normalized(),Vector(upper[2]).normalized()
    lower = portal(lower)
    upper = portal(upper)
    across=(lower[1]-lower[0]).normalized()
    diagonal=(upper[1]-upper[0]).normalized()
    # The neighbouring stair sometimes has a separate 6 mm dressed surface.
    # Measure on the retained side before removing anything from either flight.
    def outside_level(portal,sign):
        a,b=portal
        outside=Vector((b.y-a.y,a.x-b.x)).normalized()*sign
        p=(a+b)*.5+outside*.035
        hits=ground_before.down(p.x,p.y,50,60)
        return hits[0][0]
    low_z=outside_level(lower,1)
    high_z=outside_level(upper,-1)
    lower = tuple(p - .075*lower_direction for p in lower)
    upper = tuple(p + .075*upper_direction for p in upper)
    outline = [lower[0]-across*padding, lower[1]+across*padding]
    if bend is not None:outline.append(Vector(bend))
    outline.extend([upper[1]+diagonal*padding,upper[0]-diagonal*padding])
    # For a sharp turn the inside shoulder is bounded by the intersection of
    # the two cut lines. Do not permit the widened mouths to cross one another.
    from mathutils.geometry import convex_hull_2d
    # Build the enclosing polygon, then clip it by the exact two nosing lines.
    hull=[outline[j] for j in convex_hull_2d(outline)]
    if sum(a.cross(b) for a,b in zip(hull,hull[1:]+hull[:1]))<0:hull.reverse()
    for a,b in [lower,upper[::-1]]:
        result=[]
        for u,v in zip(hull,hull[1:]+hull[:1]):
            du=(b-a).cross(u-a);dv=(b-a).cross(v-a)
            if abs(du)<.0001:du=0.
            if abs(dv)<.0001:dv=0.
            if du>=0:result.append(u)
            if du*dv < 0:result.append(u.lerp(v,du/(du-dv)))
        hull=result
    assert all((a-b).length>.01 for a,b in zip(hull,hull[1:]+hull[:1])), (name,hull)
    # Clip road ribbons only. The adjacent soil and the stair mouths must share
    # a continuous substrate; cutting the base on the same oblique line leaves
    # hairline openings under the individual pavers.
    x0=math.floor(min(p.x for p in hull))-2; x1=math.ceil(max(p.x for p in hull))+2
    y0=math.floor(min(p.y for p in hull))-2; y1=math.ceil(max(p.y for p in hull))+2
    # The old trench along the east stair continues past its uphill mouth.
    if name=='east':
        x1=max(x1,57)
        y1=max(y1,-36)
    removed={}
    rect=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    hardscape=[o for o in terrain_objects if o.name.endswith(('_pavement','_yard_concrete'))]
    terrain_source=Surfaces(terrain_objects)
    def native_level(x,y):
        hits=terrain_source.down(x,y,high_z+3,high_z-low_z+8)
        return hits[0][0] if hits else None
    # Original hardscape is on a metre lattice. Include every intersection of
    # an older cut triangle with the new perimeter so neighbouring edges agree.
    xcuts=set();ycuts=set()
    for ob in hardscape:
        for e in ob.data.edges:
            a,b=(ob.data.vertices[i].co for i in e.vertices)
            if max(a.x,b.x)<x0 or min(a.x,b.x)>x1 or max(a.y,b.y)<y0 or min(a.y,b.y)>y1:continue
            for axis,stations,cuts in [(0,(x0,x1),ycuts),(1,(y0,y1),xcuts)]:
                delta=b[axis]-a[axis]
                for st in stations:
                    if abs(delta)<.00001:
                        if abs(a[axis]-st)<.00002:cuts.update([a[1-axis],b[1-axis]])
                    else:
                        u=(st-a[axis])/delta
                        if 0<=u<=1:cuts.add(a[1-axis]+u*(b[1-axis]-a[1-axis]))
    # Quarter-metre paving samples. Fine perimeter splits remain coplanar with
    # their original neighbour; their shading uses the grade, not triangle size.
    def stations(lo,hi,cuts):
        pts=sorted({round(v,4) for v in cuts if lo<v<hi}|set(np.arange(lo,hi+.1,.25)))
        arr=[pts[0]]
        for v in pts[1:]:
            if v-arr[-1]>.005:arr.append(v)
        arr[-1]=hi
        return np.asarray(arr)
    xs=stations(x0,x1,xcuts); ys=stations(y0,y1,ycuts)
    xx,yy=np.meshgrid(xs,ys,indexing='ij')
    surface=np.empty_like(xx)
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            z=native_level(x,y)
            if z is None:
                z=ground_height(x,y)
            surface[i,j]=z
    original=surface.copy()
    # Diffuse the baked stair imprint before fitting the two retained ends.
    # Interpolate on an evenly spaced mesh to avoid bias from short cut edges.
    def smooth01(t):
        t=np.clip(t,0.,1.)
        return t*t*(3.-2.*t)
    main_x=np.arange(x0,x1+.1,.25);main_y=np.arange(y0,y1+.1,.25)
    selection=np.asarray([[surface[np.argmin(abs(xs-x)), np.argmin(abs(ys-y))] for y in main_y] for x in main_x])
    g=selection.copy()
    for _ in range(45):
        old=g.copy()
        g[1:-1,1:-1]=(.035*selection[1:-1,1:-1]+.965*(old[1:-1,:-2]+old[1:-1,2:]+old[:-2,1:-1]+old[2:,1:-1])*.25)
    surface=np.asarray([np.interp(ys,main_y,np.asarray([np.interp(x,main_x,g[:,j]) for j in range(len(main_y))])) for x in xs])
    margin=np.minimum.reduce([xx-x0,x1-xx,yy-y0,y1-yy])
    surface=original+(surface-original)*smooth01(margin/1.4)
    for gate,level,direction in [(lower,low_z,lower_direction),(upper,high_z-rise,upper_direction)]:
        a,b=gate
        side=(b-a).normalized()
        across=(xx-a.x)*side.x+(yy-a.y)*side.y
        along=(xx-a.x)*direction.x+(yy-a.y)*direction.y
        edge_distance=np.maximum(0,np.maximum(-across,across-(b-a).length))
        weight=(1.-smooth01((abs(along)-.22)/1.55))*(1.-smooth01((edge_distance-.15)/1.05))*smooth01(margin/1.)
        surface+=weight*(level-surface)
    # Where older treads remain, keep the substrate below their visible top.
    # This avoids a diamond of terrain popping up between two real steps.
    for obj in floors:
        lo,hi=extent(obj)
        if hi[0]<x0 or lo[0]>x1 or hi[1]<y0 or lo[1]>y1:continue
        if obj in hardscape:count=solid_clip(obj,[(rect,low_z-2.,high_z+1.2)])
        elif obj in terrain_objects:continue
        else:count=cut_flight(obj,hull,low_z-2.,high_z+1.2)
        if count:removed[obj.name]=count
    flights=Surfaces([o for o in floors if o.name.startswith(('COL_Walk_','COL_D18_StoneFlights')) and o.data.polygons])
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            if margin[i,j]<.005:continue
            point=Vector((x,y))
            if all((b-a).normalized().cross(point-a)>.001 for a,b in zip(hull,hull[1:]+hull[:1])):
                continue
            # Within a full grid-cell diagonal of a nosing the surveyed apron
            # controls both sides, including the two outside corners.
            gate_distance=float('inf')
            for a,b in [lower,upper]:
                span=b-a
                t=min(1.,max(0.,(point-a).dot(span)/span.length_squared))
                gate_distance=min(gate_distance,(point-(a+t*span)).length)
            bed_weight=smooth01((gate_distance-.37)/.43)*smooth01(margin[i,j]/.55)
            if bed_weight<=0:continue
            # A grid cell can straddle the side or the riser of a real step.
            # Fit its corners to the lower support as well as the step above.
            nearby=[h[0][0] for dx,dy in ((0.,0.),(-.26,0.),(.26,0.),(0.,-.26),(0.,.26),
                                            (-.20,-.20),(-.20,.20),(.20,-.20),(.20,.20))
                    if (h:=flights.down(x+dx,y+dy,high_z+2.,high_z-low_z+5))]
            if nearby:
                # At the last lower tread only a few millimetres of bedding are needed.
                axial=(point-(lower[0]+lower[1])*.5).dot(lower_direction)
                bury=.008+.095*smooth01((abs(axial)-.10)/.48)
                surface[i,j]+=bed_weight*min(0.,min(nearby)-bury-surface[i,j])
    pavement=scene.objects['COL_Terrain_200m_pavement']
    bm=bmesh.new();bm.from_mesh(pavement.data);bm.transform(pavement.matrix_world)
    uv=bm.loops.layers.uv.active
    top=[[bm.verts.new((x,y,surface[i,j])) for j,y in enumerate(ys)] for i,x in enumerate(xs)]
    def add_face(vs,smooth):
        f=bm.faces.new(vs)
        f.smooth=smooth
        if uv:
            for l in f.loops:l[uv].uv=l.vert.co.xy
        return f
    threshold_faces=[]
    mouth_start,mouth_end=lower
    mouth_span=mouth_end-mouth_start
    tangent=mouth_span.normalized()
    inward=Vector((-tangent.y,tangent.x))
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            f=add_face([top[i][j],top[i+1][j],top[i+1][j+1],top[i][j+1]],True)
            delta=f.calc_center_median().xy-mouth_start
            if -.65 < delta.dot(tangent) < mouth_span.length+.65 and abs(delta.dot(inward)) < .90:
                threshold_faces.append(f)
    # Put an actual row of vertices on the last stone edge. Across that row
    # the visible yard meets the tread; behind it the bedding dives underneath.
    # Coplanar polygons otherwise alternate at the renderer's depth precision.
    edges={e for f in threshold_faces for e in f.edges}
    verts={v for e in edges for v in e.verts}
    split=bmesh.ops.bisect_plane(bm,geom=[*threshold_faces,*edges,*verts],
            plane_co=Vector((*mouth_start,low_z)),plane_no=Vector((*inward,0)),dist=.000002)
    verts.update(v for v in split['geom'] if isinstance(v,bmesh.types.BMVert))
    for v in verts:
        delta=v.co.xy-mouth_start
        axial=delta.dot(inward)
        across=delta.dot(tangent)
        end_distance=max(0.,-across,across-mouth_span.length)
        weight=(1.-smooth01(end_distance/.28))*(1.-smooth01((abs(axial)-.36)/.35))
        if weight<=0:continue
        if axial<0:
            maximum=low_z-.006-.030*smooth01(-axial/.22)
        else:
            maximum=low_z-.006+.12*smooth01(axial/.30)
        v.co.z+=weight*min(0.,maximum-v.co.z)
    # The upper mouth has one real riser. Both ends have a solid backing below
    # the adjacent pavement, which also encloses the dressed stone edge strips.
    for gate,level in [(upper,high_z),(lower,low_z)]:
        a,b=gate
        p=bm.verts.new((*a,level));q=bm.verts.new((*b,level))
        ua=bm.verts.new((*a,level-.55));ub=bm.verts.new((*b,level-.55))
        add_face([p,ua,ub,q] if gate is upper else [q,ub,ua,p],False)
    finish(pavement,bm)
    # Smooth normals for the bedding itself and its join to old paved triangles.
    for obj in hardscape:
        norms=[n.vector.copy() for n in obj.data.corner_normals]
        for f in obj.data.polygons:
            if f.normal.z<.65 or not (x0-.4<f.center.x<x1+.4 and y0-.4<f.center.y<y1+.4):continue
            for li in f.loop_indices:
                idx=obj.data.loops[li].vertex_index;v=obj.data.vertices[idx].co
                if not (x0-.01<=v.x<=x1+.01 and y0-.01<=v.y<=y1+.01):continue
                i=int(np.argmin(abs(xs-v.x)));j=int(np.argmin(abs(ys-v.y)))
                # Finite differences over 50 cm ignore sub-centimetre perimeter remnants.
                l=int(np.argmin(abs(xs-(v.x-.25))));r=int(np.argmin(abs(xs-(v.x+.25))))
                b=int(np.argmin(abs(ys-(v.y-.25))));t=int(np.argmin(abs(ys-(v.y+.25))))
                slope_x=(surface[r,j]-surface[l,j])/max(.01,xs[r]-xs[l])
                slope_y=(surface[i,t]-surface[i,b])/max(.01,ys[t]-ys[b])
                norms[li]=Vector((-slope_x,-slope_y,1)).normalized()
        obj.data.normals_split_custom_set(norms);obj.data.update();changed(obj)
    measure['walk_junctions'][name]={'mouth_heights':[low_z,high_z],'upper_rise':rise,
        'portals':[list(map(list,lower)),list(map(list,upper))],'terrain_bounds':[x0,x1,y0,y1],
        'samples':int(surface.size),'cut':removed,'outline':[list(p) for p in hull]}

def author_junctions():
    walk='COL_Walk_'
    steps='_step_concrete'
    west=walk+'West_residential_link'+steps
    east=walk+'East_photo_alley'+steps
    central=walk+'Central_stair_lane'+steps
    narrow=walk+'Narrow_upper_passage'+steps
    data=[
        ('street_entry',(walk+'OSM_734116594_0'+steps,(16.026,-69.291),(-.018,1)),
         (central,(12,-63.4),(-2,1.3)),.144,2.6,(21,-63.5)),
        ('central',(central,(-37.4115,35.1765),(-1.294,1.412)),
         (narrow,(-38.44,41.),(.52,1)),.16,2.7,(-42.7,37.6)),
        ('upper',(narrow,(-29.275,56.125),(.575,.875)),
         (walk+'Upper_terrace_connection'+steps,(-27.4,61.6),(.8,.8)),.163,2.45,(-31.,60.)),
        ('west_lower',(west,(-75.58334,-34.91667),(1.58,.917)),
         (west,(-73.90909,-31.63636),(.09,2.36)),.14,2.75,(-67.,-35.0)),
        ('west_upper',(west,(-76.68421,58.78947),(-.316,2.21)),
         (west,(-76.83318,63.08529),(.167,2.085)),.14,1.45,None),
        ('east',(east,(48.666667,-51.11666),(-.667,2.117)),
         (east,(48.57143,-47.0),(.571,2)),.14,1.45,None)]
    measure['walk_junctions']={}
    measure['landings']=[]
    prior=[('West residential link',[-74.,-34.]),('West residential link',[-77.,61.]),('East photo alley',[48.,-49.])]
    for i,(key,lower,upper,rise,padding,bend) in enumerate(data):
        regrade_turn(key,lower,upper,rise,padding,bend)
        if i>=3:
            label,center=prior[i-3]
            levels=measure['walk_junctions'][key]['mouth_heights']
            measure['landings'].append({'street':label,'center_xy':center,'entry':[*lower[1],levels[0]],'exit':[*upper[1],levels[1]]})
