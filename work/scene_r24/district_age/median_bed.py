"""Trim terrain triangles that protruded through the already built concrete central reservation."""
import bmesh,bisect
from mathutils import Vector
from roads import scene,changed,road_record
from street_mouths import cut
from survey import Surfaces
sections={}
for ob in scene.objects:
    if not ob.name.startswith('COL_R24_Median_R24_median_'):continue
    for f in ob.data.polygons:
        if abs(f.normal.z)<.04:continue
        for vi in f.vertices:
            p=ob.matrix_world@ob.data.vertices[vi].co
            if -101<p.x<-35:
                sections.setdefault(round(p.x,4),[]).append((p.y,p.z))
xs=sorted(sections);assert len(xs)>110
edges={x:(min(q[0] for q in vs),max(q[0] for q in vs),min(q[1] for q in vs),max(q[1] for q in vs)) for x,vs in sections.items()}
# The original terrain also rises through the adjacent carriageway just outside the median.
# Cut only where the actual road mesh carries the full added strip at this station.
paved=Surfaces([ob for ob in scene.objects if ob.type=='MESH' and ob.name.startswith('COL_Road_') and ob.name.endswith('_asphalt') and not ob.hide_render])
apron_count=0
for x in xs:
    a,b,l,h=edges[x]
    if all(paved.down(x,a-d,h+2.5,8.) for d in (.025,.16,.48,.80,1.20)):
        edges[x]=(a-1.20,b,l,h);apron_count+=1
affected={}
for ob in scene.objects:
    if ob.type!='MESH' or not ob.name.startswith(('COL_Terrain_200m','COL_R23_PathFoundations')):continue
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
    grid={k:[] for k in range(len(xs)-1)}
    for f in list(bm.faces):
        lo=min(v.co.x for v in f.verts);hi=max(v.co.x for v in f.verts)
        if hi<xs[0] or lo>xs[-1] or min(v.co.y for v in f.verts)>-71 or max(v.co.y for v in f.verts)<-99:continue
        start=max(0,min(len(xs)-2,bisect.bisect_right(xs,lo)-1));last=max(0,min(len(xs)-2,bisect.bisect_left(xs,hi)))
        ylo=min(v.co.y for v in f.verts);yhi=max(v.co.y for v in f.verts)
        if all(ylo>max(edges[xs[i]][1],edges[xs[i+1]][1])+.03 or yhi<min(edges[xs[i]][0],edges[xs[i+1]][0])-.03 for i in range(start,last+1)):continue
        pieces=[f]
        for x in xs[max(0,start):min(len(xs),last+2)]:
            pieces=cut(bm,pieces,Vector((x,0,0)),Vector((1,0,0)))
        for part in pieces:
            x=part.calc_center_median().x
            if xs[0]<x<xs[-1]:grid[bisect.bisect_right(xs,x)-1].append(part)
    gone=[]
    for ix,faces in grid.items():
        if not faces:continue
        x,u=xs[ix],xs[ix+1];a,b=edges[x],edges[u]
        def at(v,k):return a[k]+(b[k]-a[k])*(v-x)/(u-x)
        for j in [0,1]:
            faces=cut(bm,faces,Vector((x,a[j],0)),Vector((-(b[j]-a[j])/(u-x),1,0)).normalized())
        for f in faces:
            p=f.calc_center_median()
            if at(p.x,0)-.00001<p.y<at(p.x,1)+.00001 and at(p.x,2)-1.45<p.z<at(p.x,3)+1.10:gone.append(f)
    gone=list({f for f in gone if f.is_valid})
    if gone:
        bmesh.ops.delete(bm,geom=gone,context='FACES');bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update();changed.add(ob.name);affected[ob.name]=len(gone)
    bm.free()
# The concrete is 6 cm proud of the adjoining asphalt. Close the hairline left
# by two independent collision meshes with a 17 mm splay on the existing curb face.
# Non-coplanar joint: the toe runs below the asphalt, the kerb top stays above it.
splays={}
for ob in scene.objects:
    if ob.type!='MESH' or not ob.name.startswith('COL_R24_Median_R24_median_'):continue
    count=0
    for vert in ob.data.vertices:
        p=ob.matrix_world@vert.co;x=round(p.x,4)
        if x not in sections:continue
        by0=min(y for y,z in sections[x]);by1=max(y for y,z in sections[x])
        side=-1. if abs(p.y-by0)<.00009 else 1. if abs(p.y-by1)<.00009 else 0.
        if not side:continue
        yc=by1 if side>0 else by0
        cap=max(z for y,z in sections[x] if abs(y-yc)<.00012)
        extension=.005+min(.012,max(0.,(cap-p.z)*.09))
        p.y+=side*extension;vert.co=ob.matrix_world.inverted()@p;count+=1
    if count:ob.data.update();changed.add(ob.name);splays[ob.name]=count
road_record['median_kerb_splay']=splays
road_record['western_median']= {'from_x':xs[0],'to_x':xs[-1],'sections':len(xs),'road_edge_stations':apron_count,'retired_inside_faces':affected}
