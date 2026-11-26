"""Intersect the actual outer terrain with finished floors and tree meshes with occupied space."""
import json,math,os
from pathlib import Path
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[3]
assets=root/"work/project/chongqing_godot_v05/assets/district_500"
read=lambda name:json.loads((assets/name).read_bytes())
layout=read("layout.json")
deps=bpy.context.evaluated_depsgraph_get()
def tree(obj):return BVHTree.FromObject(obj,deps)
def global_vertices(obj):
    coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32)
    obj.data.vertices.foreach_get("co",coords)
    mat=np.asarray(obj.matrix_world)
    return coords.reshape(-1,3)@mat[:3,:3].T+mat[:3,3]
tiles=[]
plants=[]
for obj in bpy.context.scene.objects:
    if obj.type!="MESH":continue
    if obj.name.startswith("COL_Outer500_Surface_"):
        vertices=global_vertices(obj)
        assert np.allclose(np.asarray(obj.matrix_world),np.eye(4))
        tiles.append((vertices.min(axis=0)[:2],vertices.max(axis=0)[:2],tree(obj)))
    elif obj.name.startswith("Outer500_Plant_"):
        vertices=global_vertices(obj)
        plants.append((obj.name,vertices.min(axis=0),vertices.max(axis=0),vertices))

def sample(key,uv,level,finish=None,physical=.0):
    a,b,c,d=np.asarray(uv,dtype=float)
    low=np.min(uv,axis=0);high=np.max(uv,axis=0)
    candidates=[t for lo,hi,t in tiles if (lo<=high).all() and (hi>=low).all()]
    floor_tree=tree(finish) if finish else None
    nx,ny=[max(1,math.ceil(np.linalg.norm(pt-a)/.50)) for pt in (b,d)]
    peak=-999.;positive=sampled=missing=0;where=None
    inner_peak=-999.;inner_where=None;inner_count=0
    for i in range(nx):
        u=(i+.5)/nx
        for j in range(ny):
            v=(j+.5)/ny
            xy=((1-u)*a+u*b)*(1-v)+((1-u)*d+u*c)*v
            surf=level+physical
            if floor_tree:
                pt=floor_tree.ray_cast((*xy,level+.70),(0,0,-1),1.4)[0]
                if pt is None:missing+=1;continue
                surf=pt.z
            hits=[t.ray_cast((*xy,155),(0,0,-1),240)[0] for t in candidates]
            z=max((p.z for p in hits if p is not None),default=None)
            if z is None:missing+=1;continue
            sampled+=1
            gap=z-surf
            if gap>peak:peak=gap;where=[round(float(x),3) for x in (*xy,surf)]
            if gap>.015:positive+=1
            if min(u,1-u)*np.linalg.norm(b-a)>.70 and min(v,1-v)*np.linalg.norm(d-a)>.70:
                if gap>.015:inner_count+=1
                if gap>inner_peak:inner_peak=gap;inner_where=[round(float(x),3) for x in (*xy,surf)]
    trunks=[]
    # Count vertices, not opacity pixels. Runtime camera isolation confirms selected cases.
    for name,lo,hi,verts in plants:
        if (lo[:2]>high).any() or (hi[:2]<low).any() or lo[2]>level+2.4 or hi[2]<level+.25:continue
        mask=(verts[:,2]>level+.25)&(verts[:,2]<level+2.4)
        middle=(a+b+c+d)*.25
        for x,y in zip((a,b,c,d),(b,c,d,a)):
            edge=y-x;normal=np.array((-edge[1],edge[0]))/np.linalg.norm(edge)
            if (middle-x)@normal<0:normal=-normal
            mask&=((verts[:,:2]-x)@normal>.22)
        count=np.count_nonzero(mask)
        if count:trunks.append([name,int(count)])
    return {"key":key,"samples":sampled,"unpaired":missing,"above_15mm":positive,
            "highest_terrain_minus_floor_m":round(float(peak),3) if sampled else None,"peak_east_north_floor":where,
            "inner_peak_m":round(float(inner_peak),3),"inner_point":inner_where,"inner_above_15mm":inner_count,
            "plant_vertices_inside":trunks,"used_visual_floor":floor_tree is not None}

results=[]
for p in layout["plots"]:
    cx,cy=p["east_north"];cs,sn=math.cos(p["bearing"]),math.sin(p["bearing"])
    w=p["width"]*.5-.30;d=p["depth"]*.5-.30
    uv=[[cx+x*cs-y*sn,cy+x*sn+y*cs] for x,y in [(-w,-d),(w,-d),(w,d),(-w,d)]]
    obj=bpy.data.objects["Outer500_InteriorFloor_%02d"%p["plot_id"]]
    results.append(sample("plot_%02d"%p["plot_id"],uv,p["height"],obj))
for b in read("historic_courts.json")["buildings"]:
    results.append(sample(b["id"],b["ring"],b["floor"]))
for b in read("shancheng_lane.json")["buildings"]:
    results.append(sample(b["osm"],b["wall_base_corners"],b["floor_z"]))
out=Path(os.environ["CQ_QA_DIR"])
(out/"floors.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
