"""Replace the old ribbons, their foundations and the yard beneath them together."""
import numpy as np

floors=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and
        o.name.startswith(('COL_Terrain_200m','COL_East17_CourtyardPaving','COL_East17_LandingReturns',
            'COL_East17_ShoulderReturns','COL_Walk_','Walk_details_','COL_R23_PathFoundations',
            'COL_N13_StairFoundations','COL_R21_Footing_','R21_Dressed_','R20_Hand_laid_treads_','COL_D18_StoneFlights','COL_D18_LaneShoulders'))]
ground_before=Surfaces(floors)
bank_returns=scene.objects.get('COL_N13_BankCutFaces')
if bank_returns and not bank_returns.hide_render:
    floors.append(bank_returns)
measure['continuous_paving']=[]
measure['street_landings']=[]
exec(compile((here/'entry_corner/grade.py').read_text('utf-8-sig'),str(here/'entry_corner/grade.py'),'exec'))
author_junctions()
exec(compile((here/'entry_corner/north.py').read_text('utf-8'),str(here/'entry_corner/north.py'),'exec'))
sites=[('EastLane',(38.5,51.,1.50,7.25),29.),('StationRear',(23.25,31.75,11.50,24.25),29.)]
for key,(x0,x1,y0,y1),ceiling in sites:
    nx=round((x1-x0)*4)+1
    ny=round((y1-y0)*4)+1
    xs=np.linspace(x0,x1,nx)
    ys=np.linspace(y0,y1,ny)
    old=np.empty((nx,ny))
    grade=np.empty_like(old)
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            # The neighbouring real stair occupies this notch of the rear court.
            sx=min(x,28.50) if key=='StationRear' and y<16. else x
            hits=ground_before.down(sx,y,ceiling,10.)
            if not hits:
                # A cut edge can miss an individual vertical ray. Only bridge
                # a sub-step gap with support on at least two sides.
                hits=[row for dx,dy in ((.14,0),(-.14,0),(0,.14),(0,-.14))
                      for row in ground_before.down(sx+dx,y+dy,ceiling,10.)[:1]]
                if len(hits)<2:raise ValueError(('Missing existing pavement',key,x,y))
                hits.sort(key=lambda row:row[0])
            old[i,j]=hits[0][0]
            under=[h for h,name,_ in hits if name.startswith('COL_Terrain_200m')]
            grade[i,j]=under[0] if under else old[i,j]
    # Diffuse the residual high spots from old curbs inside the graded area.
    # At the perimeter the surface inherits the actual adjacent elevation.
    for iteration in range(26):
        g=grade.copy()
        grade[1:-1,1:-1]=(4*g[1:-1,1:-1]+g[1:-1,:-2]+g[1:-1,2:]+g[:-2,1:-1]+g[2:,1:-1])/8
    d=np.minimum(np.minimum(xs-x0,x1-xs)[:,None],np.minimum(ys-y0,y1-ys)[None,:])
    if key=='StationRear':
        d=np.minimum(d,np.hypot(np.maximum(0,28.50-xs)[:,None],np.maximum(0,ys-16.)[None,:]))
    t=np.clip(d/1.55,0,1)
    top=old+(grade-old)*t*t*(3-2*t)
    tiles=[(x0,28.50,y0,16.),(x0,x1,16.,y1)] if key=='StationRear' else [(x0,x1,y0,y1)]
    domain=[([(a,c),(b,c),(b,d),(a,d)],float(top.min()-2.5),float(old.max()+.16)) for a,b,c,d in tiles]
    clipped={}
    for ob in floors:
        lo,hi=extent(ob)
        if hi[0]<x0 or lo[0]>x1 or hi[1]<y0 or lo[1]>y1:continue
        count=solid_clip(ob,domain)
        if count:clipped[ob.name]=count
    name='COL_Patrol25_'+key
    vertices=[(x,y,float(top[i,j])) for i,x in enumerate(xs) for j,y in enumerate(ys)]
    quads=[]
    for i in range(nx-1):
        for j in range(ny-1):
            if key=='StationRear' and xs[i]>=28.50 and ys[j]<16.:continue
            a=i*ny+j
            quads.append((a,a+ny,a+ny+1,a+1))
    # Close the sawn ends of old kerbs where the adjoining street has a vertical
    # face. Duplicate perimeter vertices here keep the top normals independent.
    boundary={}
    for quad in quads:
        for a,b in zip(quad,quad[1:]+quad[:1]):
            if (b,a) in boundary:del boundary[(b,a)]
            else:boundary[(a,b)]=True
    top_count=len(quads)
    for a,b in boundary:
        xa,ya,za=vertices[a]
        xb,yb,zb=vertices[b]
        idx=len(vertices)
        vertices.extend([(xa,ya,za),(xb,yb,zb),(xb,yb,zb-.65),(xa,ya,za-.65)])
        quads.append((idx+3,idx+2,idx+1,idx))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],quads)
    mesh.materials.append(mat['tread'])
    mesh.update()
    uv=mesh.uv_layers.new(name='SurfaceMetres')
    for f in mesh.polygons:
        f.use_smooth=f.index<top_count
        for loop in f.loop_indices:
            p=mesh.vertices[mesh.loops[loop].vertex_index].co
            uv.data[loop].uv=p.xy
    ob=bpy.data.objects.new(name,mesh)
    collection.objects.link(ob)
    layout['new'].append(name)
    measure['continuous_paving'].append({'site':key,'bounds':[x0,x1,y0,y1],'samples':int(top.size),
        'removed_faces':clipped,'max_height_removed_m':float(np.max(old-top))})
