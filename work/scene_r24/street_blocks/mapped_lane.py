"""Editable surface detail for the Shancheng Lane fork, built against the native outer terrain."""
from pathlib import Path
from math import sin,cos,atan2,pi,hypot
import json,hashlib,xml.etree.ElementTree as ET
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
root=here.parents[2]
out=root/"work/project/chongqing_godot_v05/assets/district_500"
raw=root/"work/assets_incoming/r22_city/osm_southwest.osm"
source=ET.parse(raw)
nodes={n.get("id"):[float(n.get("lon")),float(n.get("lat"))] for n in source.findall("node")}
ways={int(w.get("id")):[n.get("ref") for n in w.findall("nd")] for w in source.findall("way")}
geo=json.loads((out.parents[1]/"source_data/geo_layout.json").read_bytes())
trace=next(w["points"] for w in geo["paths"] if w["id"]==734116601)
# Register the two branches on exactly the same local metre controls as the existing game.
wgs=np.array([nodes[n] for n in ways[734116601]])
origin=wgs.mean(axis=0)
def design(x):return np.column_stack((np.array(x)-origin,np.ones(len(x))))
transform=np.linalg.lstsq(design(wgs),np.array(trace),rcond=None)[0]
err=np.linalg.norm(design(wgs)@transform-np.array(trace),axis=1).max()
assert err<.005
registered=dict(zip(ways[734116601],trace))
def route(w,ids):
    return [registered.get(n,(design([nodes[n]])@transform)[0].tolist()) for n in ids]
trace=np.array(trace)
branch=route(734116600,ways[734116600][31:])
link=route(734116599,ways[734116599])
assert ways[734116600][-1]==ways[734116601][42] and ways[734116599][-1]==ways[734116601][37]
walks=[trace[:47],np.array(branch),np.array(link)]
from runpy import run_path
plan=run_path(str(here/"street_plan.py"))
road_data=json.loads((out/"layout.json").read_bytes())
reserved=plan["Streets"](plan["roads"](road_data))
verts=[];faces=[]
for ob in bpy.context.scene.objects:
    if ob.name.startswith("COL_Outer500_Surface_"):
        k=len(verts);verts.extend(ob.matrix_world@v.co for v in ob.data.vertices)
        faces.extend(tuple(k+i for i in f.vertices) for f in ob.data.polygons)
ground=BVHTree.FromPolygons(verts,faces)
def z(q):
    hit=ground.ray_cast((float(q[0]),float(q[1]),100),(0,0,-1))[0]
    if hit is None:raise ValueError(q)
    return hit.z
def xyz(q,offset=0):
    return [float(q[0]),float(q[1]),z(q)+offset]
bpy.ops.wm.read_factory_settings(use_empty=True)
def material(name,color,source=None,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value=(*color,1);b.inputs["Metallic"].default_value=metal
    b.inputs["Roughness"].default_value=.86 if metal==0 else .54
    m.diffuse_color=(*color,1)
    if source:
        tex=m.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image=bpy.data.images.load(str(out.parent/("chongqing_district_"+source)),check_existing=True)
        tex.image.pack()
        mix=m.node_tree.nodes.new("ShaderNodeMixRGB");mix.blend_type="MULTIPLY";mix.inputs[0].default_value=1.0
        mix.inputs[2].default_value=(*color,1);m.node_tree.links.new(tex.outputs[0],mix.inputs[1])
        m.node_tree.links.new(mix.outputs[0],b.inputs["Base Color"])
        normal_path=out.parent/("chongqing_district_"+source.replace("_diff","_nor_gl"))
        normal=m.node_tree.nodes.new("ShaderNodeTexImage")
        normal.image=bpy.data.images.load(str(normal_path),check_existing=True)
        normal.image.colorspace_settings.name="Non-Color"
        normal.image.pack()
        relief=m.node_tree.nodes.new("ShaderNodeNormalMap")
        relief.inputs["Strength"].default_value=.65
        m.node_tree.links.new(normal.outputs["Color"],relief.inputs["Color"])
        m.node_tree.links.new(relief.outputs["Normal"],b.inputs["Normal"])
    return m
mats=[material("Shancheng dressed sandstone "+str(i),col,"concrete_floor_worn_001_diff_2k.jpg") for i,col in enumerate([(.47,.48,.46),(.39,.42,.40),(.53,.52,.46),(.43,.45,.44)])]
mats+= [material("Shancheng kerbstone",(.35,.35,.32),"stone_wall_05_diff_2k.jpg"),
        material("Shancheng blackened steel",(.08,.105,.093),metal=.48),material("Used counter oak",(.58,.44,.30),"wood_table_worn_diff_2k.jpg"),
        material("Shelf side enamel",(.15,.25,.22),metal=.3)]
class Batch:
    def __init__(self):self.v=[];self.f=[];self.slots=[]
    def face(self,pts,mat):
        k=len(self.v);self.v.extend(pts);self.f.append(tuple(range(k,k+len(pts))));self.slots.append(mat)
    def make(self,name):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(self.v,[],self.f);mesh.update()
        for m in mats:mesh.materials.append(m)
        uv=mesh.uv_layers.new()
        for f,slot in zip(mesh.polygons,self.slots):
            f.material_index=slot
            for i in f.loop_indices:
                p=mesh.vertices[mesh.loops[i].vertex_index].co
                if abs(f.normal.z)>.68:uv.data[i].uv=(p.x*.51,p.y*.51)
                else:uv.data[i].uv=((-p.x*f.normal.y+p.y*f.normal.x)*.51,p.z*.51)
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
stones=Batch();details=Batch();furniture=Batch()
slabs=0
# Interpolate each transverse row through a shared bisector so the paving turns with the alley.
for route_index,points in enumerate(walks):
    tang=np.diff(points,axis=0);length=np.linalg.norm(tang,axis=1);unit=tang/length[:,None]
    normals=np.column_stack((-unit[:,1],unit[:,0]))
    normal=[normals[0]]
    for a,b in zip(normals,normals[1:]):
        bis=a+b;normal.append(bis/max(.80,float(bis@a)))
    normal.append(normals[-1])
    dist=np.r_[0,np.cumsum(length)]
    def sample(s,across):
        i=min(len(length)-1,max(0,np.searchsorted(dist,s,side="right")-1));t=(s-dist[i])/length[i]
        return points[i]+t*tang[i]+across*((1-t)*normal[i]+t*normal[i+1])
    width=1.50 if route_index==0 else 1.04
    # Secondary trails meet the primary apron at its edge, avoiding coplanar stones at fork vertices.
    trim0=1.50 if route_index==2 else 0
    trim1=1.65 if route_index>0 else 0
    end=dist[-1]-trim1
    for course in range(4 if route_index==0 else 3):
        rows=4 if route_index==0 else 3
        a=-width+2*width*course/rows+.008;b=-width+2*width*(course+1)/rows-.008
        start=trim0
        while start<end-.06:
            step=.68+((slabs*7+course*19)%21)*.019
            if start==trim0 and course%2:step*=.54
            finish=min(end,start+step)
            # Keep subfaces short enough to follow the collision terrain along each joint.
            for m0,m1 in zip(np.linspace(start+.008,finish-.008,4)[:-1],np.linspace(start+.008,finish-.008,4)[1:]):
                for x,y in ((a,(a+b)*.5),((a+b)*.5,b)):
                    s=[sample(m0,x),sample(m1,x),sample(m1,y),sample(m0,y)]
                    if reserved.margin(s).min()<.10:continue
                    stones.face([xyz(q,.021) for q in s],(slabs+course*2)%4)
            slabs+=1;start=finish
    for s in np.arange(trim0+.35,end-.45,.82):
        # Slotted run-off grates alternate with a shallow dressed channel at the verge.
        a=sample(s,-width-.17);b=sample(s+.77,-width-.17);c=sample(s+.77,-width-.015);d=sample(s,-width-.015)
        if reserved.margin([a,b,c,d]).min()<.10:continue
        details.face([xyz(q,.025) for q in (a,b,c,d)],4)
        if int(s/.82)%9==0:
            for t in np.arange(.07,.70,.10):
                qs=[sample(s+t,-width-.148),sample(s+t+.038,-width-.148),sample(s+t+.038,-width-.033),sample(s+t,-width-.033)]
                details.face([xyz(q,.034) for q in qs],5)
def stand(idx,lateral):
    a=trace[idx];v=trace[idx-1]-a;v/=np.linalg.norm(v);normal=np.array([-v[1],v[0]])
    base=a+normal*lateral
    top=z(base)+.86
    def rect(batch,u0,v0,h0,u1,v1,h1,mat):
        ps=[[* (base+u*v+w*normal),h] for h in (h0,h1) for u,w in ((u0,v0),(u1,v0),(u1,v1),(u0,v1))]
        for f in ((3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
            batch.face([ps[i] for i in f],mat)
    for u in (-.57,.57):
        for w in (-.23,.23):rect(furniture,u-.035,w-.035,z(base+u*v+w*normal)-.04,u+.035,w+.035,top,5)
    for i in range(4):rect(furniture,-.68,-.33+i*.17,top,.68,-.33+i*.17+.16,top+.044,6)
    rect(furniture,-.59,-.26,top-.48,.59,.26,top-.43,7)
    return {"target":[float(base[0]),top+.11,-float(base[1])],"approach":xyz(a,.045),"upper":top}
stops=[stand(42,1.85),stand(34,-1.85)]
for batch,name in ((stones,"Shancheng_registered_flagstones"),(details,"Shancheng_edge_channels"),(furniture,"COL_Shancheng_exchange_shelves")):batch.make(name)
def lift(path):return [xyz(q,.045) for q in path]
group=json.loads((here/"mapped_group.json").read_bytes())
built=run_path(str(here/"group_models.py"))["build"](group,trace,z,material,mats,Batch,road_data["building_grades"])
record={"buildings":built,"sources":[734116601,734116600,734116599,585541371],"control_error_m":float(err),"primary":lift(trace[34:43][::-1]),"branch":lift(branch[::-1]+link[1:]+trace[34:37][::-1].tolist()),"public_stops":stops,"flags":slabs,
        "source_sha256":hashlib.sha256(raw.read_bytes()).hexdigest(),"attribution":"© OpenStreetMap contributors, ODbL 1.0"}
(out/"shancheng_lane.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/"shancheng_lane.blend"),compress=True)
bpy.ops.export_scene.gltf(filepath=str(out/"shancheng_lane.glb"),export_format="GLB",export_yup=True)
