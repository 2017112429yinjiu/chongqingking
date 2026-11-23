"""Join cut paving boundaries to their stair support, then author grounded lane furnishings and facade-mounted utility spans."""
import sys,random,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_neighborhood import *
from mathutils.geometry import intersect_point_line
from collections import Counter
root_out=project/'assets/neighborhood_r24';root_out.mkdir(exist_ok=True)
collection=bpy.data.collections.new('R24_13_Neighborhood');scene.collection.children.link(collection)
shape={};mats={};published=[];rng=random.Random(13737)
def mat(k,color,rough=.84,metal=.0):
    m=bpy.data.materials.new('Neighborhood_'+k);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    m.diffuse_color=(*color,1);mats[k]=m
for key,col,r,m in [('cement',(.15,.137,.107),.88,0),('wire',(.026,.026,.023),.72,.16),('iron',(.116,.088,.065),.69,.60),('ceramic',(.49,.47,.375),.36,.1),('earthenware',(.255,.128,.075),.88,0),('soil',(.083,.056,.031),.95,0),('galvanized',(.23,.248,.215),.64,.38)]:mat(key,col,r,m)
def add(name,verts,faces,material):
    v,f,ms=shape.setdefault(name,([],[],[]));off=len(v);v.extend([tuple(p) for p in verts]);f.extend([tuple(off+k for k in face) for face in faces]);ms.extend([material]*len(faces))
def rod(name,a,b,r,material,k=10,top=None):
    a,b=Vector(a),Vector(b);d=b-a
    if d.length<.00001:return
    d.normalize();u=d.orthogonal().normalized();v=d.cross(u)
    vs=[p+rad*(math.cos(i*math.tau/k)*u+math.sin(i*math.tau/k)*v) for p,rad in [(a,r),(b,r if top is None else top)] for i in range(k)]
    add(name,vs,[tuple(reversed(range(k))),tuple(range(k,2*k))]+[(i,(i+1)%k,k+(i+1)%k,k+i) for i in range(k)],material)
def retire(ob):ob.hide_render=True;ob.hide_set(True)
retired=[]
for o in list(scene.objects):
    if o.type=='MESH' and (o.name.startswith(('COL_Handrails_','COL_R20_Returned_handrail_')) or o.name in ['Court_entry_rails_frame','Utility_cables_dark']):
        retired.append(o.name);retire(o)
exec(compile((root/'corner_repair.py').read_text('utf-8'),str(root/'corner_repair.py'),'exec'))
# Map actual side edges of each tread, including both flights. Keep the court-entry steps open at the tee.
stairs={};sides=defaultdict(list);edge_list=[]
for key,ob in [('central','COL_Walk_Central_stair_lane_step_concrete'),('west','COL_Walk_West_residential_link_step_concrete')]:
    rows=tread_rows(ob)
    stairs[key]=[[c.x,c.z,-c.y] for c,_ in rows]
    for j,(c,ring) in enumerate(rows):
        edges=list(zip(ring,ring[1:]+ring[:1]))
        for a,b in sorted(edges,key=lambda pts:(pts[0]-pts[1]).length)[:2]:
            entry=(key,a,b,c);edge_list.append(entry)
            for ix in range(math.floor((min(a.x,b.x)-.3)/2),math.floor((max(a.x,b.x)+.3)/2)+1):
                for iy in range(math.floor((min(a.y,b.y)-.3)/2),math.floor((max(a.y,b.y)+.3)/2)+1):sides[ix,iy].append(entry)
def match(x,y):
    best=None
    for key,a,b,c in sides.get((math.floor(x/2),math.floor(y/2)),[]):
        dx=b.x-a.x;dy=b.y-a.y;t=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/(dx*dx+dy*dy)))
        px=a.x+t*dx;py=a.y+t*dy;dist=math.hypot(x-px,y-py)
        if best is None or dist<best[0]:best=(dist,c.z,px,py,key)
    return best
walls=defaultdict(int);probes=[];checked=set()
for obj in list(scene.objects):
    if not visible_ground(obj) or not obj.name.startswith(('COL_Terrain','COL_R23_PathFoundations','COL_Walk_Courtyard','Walk_details_Courtyard')):continue
    vs=[obj.matrix_world@v.co for v in obj.data.vertices];edges=defaultdict(list)
    for f in obj.data.polygons:
        if abs(f.normal.z)<.09:continue
        # Only boundaries near the stair line need a new side. Count adjacent faces in geometric rather than UV space.
        idx=list(f.vertices)
        for i,j in zip(idx,idx[1:]+idx[:1]):
            a,b=vs[i],vs[j];mid=(a+b)*.5
            if (math.floor(mid.x/2),math.floor(mid.y/2)) not in sides:continue
            k=tuple(sorted(tuple(round(w,4) for w in v) for v in [a,b]));edges[k].append((a,b))
    for ends,segments in edges.items():
        if len(segments)!=1 or ends in checked:continue
        a,b=segments[0];mid=(a+b)*.5;m=match(mid.x,mid.y)
        if not m or m[0]>.09 or max(abs(a.z-m[1]),abs(b.z-m[1]))<.045 or (a-b).length>5:continue
        left,right=match(a.x,a.y),match(b.x,b.y)
        if not left or not right or max(left[0],right[0])>.17:continue
        if mid.z<m[1]-.01:continue
        # Undercut retained terrain had an open underside at its trimmed perimeter.
        # Fix the cut from its actual top down past the structural tread, on that same edge.
        bottom=min(m[1],left[1],right[1],a.z,b.z)-.22
        add('COL_N13_BankCutFaces',[a,b,(b.x,b.y,bottom),(a.x,a.y,bottom)],[(0,1,2,3)],'cement')
        checked.add(ends);walls[obj.name]+=1
        if mid.z>m[1]+.10:probes.append({'p':[mid.x,(mid.z+m[1])*.5,-mid.y],'toward':[m[2],m[1],-m[3]],'rise':mid.z-m[1],'edge':[[a.x,a.z,-a.y],[b.x,b.z,-b.y]]})
# A continuous cheek closes tread sides where native paving falls below their thin boxes.
cheeks=0
for key,a,b,c in edge_list:
    mid=(a+b)*.5;out=Vector((mid.x-c.x,mid.y-c.y,0)).normalized()
    near=mid+out*.10
    support=[v for v in floors(near.x,near.y,c.z+.16) if not v[1].startswith(('R21_Dressed','COL_Walk_Central_stair','COL_Walk_West_residential'))]
    if not support or support[0][0]>c.z-.15:continue
    lo=max(c.z-2.3,support[0][0]-.035);aa=a-out*.018;bb=b-out*.018
    add('COL_N13_StairFoundations',[(*aa.xy,c.z-.045),(*bb.xy,c.z-.045),(*bb.xy,lo),(*aa.xy,lo)],[(0,1,2,3)],'cement');cheeks+=1
exec(compile((root/'connections.py').read_text('utf-8'),str(root/'connections.py'),'exec'))
exec(compile((root/'street_edges.py').read_text('utf-8'),str(root/'street_edges.py'),'exec'))
exec(compile((root/'lamps_and_seats.py').read_text('utf-8'),str(root/'lamps_and_seats.py'),'exec'))
for label,(verts,faces,materials) in shape.items():
    mesh=bpy.data.meshes.new(label);mesh.from_pydata(verts,[],faces);mesh.update();keys=list(dict.fromkeys(materials))
    for k in keys:mesh.materials.append(mats[k])
    for poly,key in zip(mesh.polygons,materials):poly.material_index=keys.index(key)
    uv=mesh.uv_layers.new(name='World metres')
    for face in mesh.polygons:
        for i in face.loop_indices:
            v=mesh.vertices[mesh.loops[i].vertex_index].co;n=face.normal
            uv.data[i].uv=(v.x if abs(n.y)>abs(n.x) else v.y,v.z) if abs(n.z)<.65 else (v.x,v.y)
    ob=bpy.data.objects.new(label,mesh);collection.objects.link(ob);published.append(ob)
# Replace only the two trimmed terrain resources in the game. Other authored layers retain their data.
donor_nodes={};runtime_donors=[]
for i,source in enumerate(orig_names):
    orig=scene.objects[source];mesh=orig.data.copy();mesh.materials.clear();dup=bpy.data.objects.new('N13_CornerSource%d'%i,mesh);collection.objects.link(dup);dup.matrix_world=orig.matrix_world.copy();runtime_donors.append(dup);donor_nodes[dup.name]=source
bpy.ops.object.select_all(action='DESELECT')
for ob in published+runtime_donors:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(root_out/'street.glb'),export_format='GLB',use_selection=True,export_animations=False,export_yup=True)
for ob in runtime_donors:bpy.data.objects.remove(ob,do_unlink=True)
info={'donors':donor_nodes,'corner_replaced':len(old_faces),'furniture':furniture,'retire':retired,'wall_sections':dict(walls),'stair_cheeks':cheeks,'wall_probes':probes,'wires':spans,'adjustments':adjustments,'ground_audit':groundaudit,'plants':plant_instances,'beds':beds,'walks':walks}
(root_out/'layout.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),'utf-8')
(root/'geometry_report.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),'utf-8')
scene['street_revision']='R24 build 13 bank and occupied streets'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'city_and_neighborhood.blend'),compress=True,relative_remap=True)
print('N13_ART',len(retired),dict(walls),cheeks,len(probes),len(spans),len(adjustments),len(plant_instances),len(beds),flush=True)

