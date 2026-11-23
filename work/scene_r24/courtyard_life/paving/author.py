"""Cut mutually exclusive paving materials on the original sloped triangle planes."""
from pathlib import Path
from collections import defaultdict
import sys,json,bpy,bmesh
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent))
from paving_cells import faces
from paving_runs import trace
assets=here.parents[2]/'project/chongqing_godot_v05/assets/courtyard_r24'
cells=defaultdict(list)
for key,ob,face,category,points in faces():
    cells[key].append((category,face.index,points))
runs=trace({key:[row[0] for row in group] for key,group in cells.items()})
assert any(run['c']==-16 and run['start']==12 for run in runs)
objects={name:bpy.context.scene.objects['COL_Terrain_200m_'+name] for name in ('pavement','yard_concrete')}
bms={}; original_faces={};verts={};drop=defaultdict(list);probes=[]
def vertex_key(p):return tuple(round(v,6) for v in p)
for name,ob in objects.items():
    bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table();bms[name]=bm
    verts[name]={vertex_key(v.co):v for v in bm.verts}
    original_faces[name]=list(bm.faces)
def cut(poly,signed,side):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da,db=signed(a)*side,signed(b)*side
        if da>=-1.e-7:result.append(a.copy())
        if da*db < -1.e-12:result.append(a.lerp(b,da/(da-db)))
    return result
def xy(p):return p.x,-p.y
def key_at(c,t,axis):return (c,t) if axis==0 else (t,c)
def source_uv(row):
    name,idx,pts=row;mesh=objects[name].data
    uv=mesh.uv_layers.active
    values=[uv.data[i].uv.copy() for i in mesh.polygons[idx].loop_indices]
    a,b,c=pts
    def project(point):
        x,y=point.x-a.x,point.y-a.y
        v,w=b-a,c-a;den=v.x*w.y-v.y*w.x
        wb=(x*w.y-y*w.x)/den;wc=(v.x*y-v.y*x)/den
        return values[0]+wb*(values[1]-values[0])+wc*(values[2]-values[0])
    return project
for run in runs:
    for t in range(run['start'],run['end']):
        for name,idx,_ in cells[key_at(run['c'],t,run['axis'])]:
            drop[name].append(original_faces[name][idx])
for name,bm in bms.items():
    bmesh.ops.delete(bm,geom=drop[name],context='FACES_ONLY')
area_old=area_new=0.
for run in runs:
    axis=run['axis'];c=run['c'];start=run['start'];end=run['end']
    def border(t):return run['a']+(run['b']-run['a'])*(t-start)/(end-start)
    def signed(point):
        q=xy(point)
        return q[axis]-border(q[1-axis])
    for t in range(start,end):
        key=key_at(c,t,axis);pair=cells[key]
        assert len(pair)==2
        maps={row[0]:source_uv(row) for row in pair}
        for name,idx,pts in pair:
            old_area=(pts[1]-pts[0]).cross(pts[2]-pts[0]).length*.5
            area_old+=old_area;new_area=0.
            for dest,side in [(run['low'],-1),(run['high'],1)]:
                clipped=cut(pts,signed,side)
                if len(clipped)<3:continue
                bm=bms[dest];uv=bm.loops.layers.uv.active
                for i in range(1,len(clipped)-1):
                    tri=[clipped[0],clipped[i],clipped[i+1]];local=[objects[dest].matrix_world.inverted()@p for p in tri]
                    area=(tri[1]-tri[0]).cross(tri[2]-tri[0]).length*.5
                    if area<1.e-8:continue
                    new_area+=area;vs=[]
                    for v in local:
                        vk=vertex_key(v)
                        if vk not in verts[dest]:verts[dest][vk]=bm.verts.new(v)
                        vs.append(verts[dest][vk])
                    face=bm.faces.new(vs)
                    for loop,point in zip(face.loops,tri):loop[uv].uv=maps[dest](point)
            assert abs(old_area-new_area)<.00001
            area_new+=new_area
        for offset in (.19,.47,.78):
            for side,dest in [(-1,run['low']),(1,run['high'])]:
                x,z=key_at(border(t+offset)+.042*side,t+offset,axis)
                for _,_,pts in pair:
                    a,b,p=pts;v=b-a;w=p-a;dx=x-a.x;dy=-z-a.y;det=v.x*w.y-v.y*w.x
                    s=(dx*w.y-dy*w.x)/det;u=(v.x*dy-v.y*dx)/det
                    if min(s,u,1.-s-u)>=-.00001:
                        probes.append({'x':x,'z':z,'h':a.z+s*v.z+u*w.z,'material':dest});break
                else:raise ValueError((x,z))
for label,ob in objects.items():
    bm=bms[label]
    bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES')
    bm.to_mesh(ob.data);ob.data.update();bm.free()
bpy.ops.object.select_all(action='DESELECT')
copies=[]
for name,ob in objects.items():
    m=ob.data.copy();m.materials.clear();copy=bpy.data.objects.new('CourtPaving_'+name,m)
    bpy.context.scene.collection.objects.link(copy);copy.matrix_world=ob.matrix_world.copy();copy.select_set(True);copies.append(copy)
bpy.ops.export_scene.gltf(filepath=str(assets/'paving.glb'),export_format='GLB',use_selection=True,export_animations=False,export_yup=True)
for ob in copies:bpy.data.objects.remove(ob,do_unlink=True)
scene=bpy.context.scene;scene['street_revision']='R24 14c courtyard paving';bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_courtyard.blend'),compress=True,relative_remap=True)
record={'runs':runs,'removed_faces':{k:len(v) for k,v in drop.items()},'surface_area_before':area_old,'surface_area_after':area_new,'probes':probes}
(here/'boundary.json').write_text(json.dumps(record,indent=2),'utf8')
print('COURT14_PAVING',len(runs),len(probes),area_old,area_new,flush=True)
