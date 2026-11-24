"""Connect the north courtyard grade to the outer edge of its existing sidewalk."""
def grade_north_frontage():
    road=scene.objects['COL_Road_734116597_0_pavement']
    outer=[]
    for face in road.data.polygons:
        if face.normal.z<.9:continue
        for index in face.vertices:
            p=road.matrix_world@road.data.vertices[index].co
            if -39<p.x<-10 and abs(p.y-(84.-.589*(p.x+25.54)))<.045:
                outer.append(tuple(p))
    edge=sorted(set(outer))
    assert len(edge)>=16
    ex,ey,ez=np.asarray(edge).T
    x0,x1,y0,y1=-36,-12,74,94
    xs=np.arange(x0,x1+.1,.25)
    ys=np.arange(y0,y1+.1,.25)
    terrain_meshes=[ob for ob in terrain_objects if ob.name.endswith(('_pavement','_yard_concrete'))]
    survey=Surfaces(terrain_meshes)
    ring=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    z=np.empty((len(xs),len(ys)))
    original=np.empty_like(z)
    def ease(t):
        t=min(1.,max(0.,t))
        return t*t*(3.-2.*t)
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            hits=survey.down(x,y,39.,14.)
            if not hits:
                hits=[h for dx,dy in [(-.015,0),(.015,0),(0,-.015),(0,.015)]
                      for h in survey.down(x+dx,y+dy,39.,14.)[:1]]
            if not hits:
                # Beneath the road the original terrain was already trimmed.
                original[i,j]=ground_height(x,y)
            else:
                original[i,j]=sum(h[0] for h in hits)/len(hits)
            d=(y-np.interp(x,ex,ey))*.862
            road_z=np.interp(x,ex,ez)
            # Meet the existing walk at its edge. The shoulders rise over
            # several metres and the bedding then continues below the walk.
            target=road_z-.008+.23*min(0.,d)-.13*ease(d/.45)
            weight=ease(min(x-x0,x1-x)/5.5)*ease(min(y-y0,y1-y)/3.)*(1.-ease((-d-1.)/4.8))*(1.-ease((d-.55)/1.2))
            z[i,j]=original[i,j]+weight*(target-original[i,j])
    cut={o.name:solid_clip(o,[(ring,24.,39.)]) for o in terrain_meshes}
    ob=scene.objects['COL_Terrain_200m_pavement']
    bm=bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    uv=bm.loops.layers.uv.active
    verts=[[bm.verts.new((x,y,z[i,j])) for j,y in enumerate(ys)] for i,x in enumerate(xs)]
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            f=bm.faces.new((verts[i][j],verts[i+1][j],verts[i+1][j+1],verts[i][j+1]))
            f.smooth=True
            if uv:
                for loop in f.loops:loop[uv].uv=loop.vert.co.xy
    finish(ob,bm)
    # Match the original paving's custom normals at the perimeter, and set
    # the interior normals from the metre-scale grade rather than old batches.
    dx,dy=np.gradient(z,.25,.25)
    for ob in terrain_meshes:
        normals=[n.vector.copy() for n in ob.data.corner_normals]
        for poly in ob.data.polygons:
            if poly.normal.z<.65 or not (x0-.7<poly.center.x<x1+.7 and y0-.7<poly.center.y<y1+.7):continue
            for li in poly.loop_indices:
                p=ob.data.vertices[ob.data.loops[li].vertex_index].co
                if not (x0-.001<=p.x<=x1+.001 and y0-.001<=p.y<=y1+.001):continue
                i,j=int(round((p.x-x0)*4)),int(round((p.y-y0)*4))
                normals[li]=Vector((-dx[i,j],-dy[i,j],1.)).normalized()
        ob.data.normals_split_custom_set(normals)
        ob.data.update()
        changed(ob)
    measure['north_frontage']={'bounds':[x0,x1,y0,y1],'sidewalk_edge':edge,'samples':int(z.size),
        'max_fill_m':float((z-original).max()),'cut':cut}

grade_north_frontage()
