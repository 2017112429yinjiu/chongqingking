"""Clip the saved terrain triangles to the registered floor; inspect the whole footprint."""
import json
import os
from pathlib import Path
import bpy
from mathutils import Vector
import numpy as np

study=Path(__file__).resolve().parents[1]
asset=study.parents[2]/"work/project/chongqing_godot_v05/assets/district_500/historic_courts.json"
school=next(b for b in json.loads(asset.read_bytes())["buildings"] if b["id"]=="jinma_classrooms")
ring=np.array(school["ring"])
lower,upper=ring.min(axis=0),ring.max(axis=0)
centre=ring.mean(axis=0)
halfplanes=[]
for a,b in zip(ring,np.roll(ring,-1,axis=0)):
    normal=np.array([b[1]-a[1],a[0]-b[0]])
    normal/=np.linalg.norm(normal)
    if (centre-a)@normal<0: normal=-normal
    halfplanes.append((a,normal))

def clip(poly,a,n):
    points=[]
    prev=poly[-1]
    side=(prev[:2]-a)@n
    for p in poly:
        dist=(p[:2]-a)@n
        if (dist>=0)!=(side>=0):
            points.append(prev+(p-prev)*(side/(side-dist)))
        if dist>=0: points.append(p)
        prev,side=p,dist
    return points

highest=-float("inf")
area=0.
tiles={}
for obj in bpy.context.scene.objects:
    if not obj.name.startswith("COL_Outer500_Surface_"): continue
    bounds=np.asarray([list(obj.matrix_world @ Vector(c)) for c in obj.bound_box])
    if (bounds[:,:2].max(axis=0)<lower).any() or (bounds[:,:2].min(axis=0)>upper).any(): continue
    mesh=obj.data
    coords=np.asarray([list(obj.matrix_world@v.co) for v in mesh.vertices])
    mesh.calc_loop_triangles()
    indices=np.empty(3*len(mesh.loop_triangles),dtype=np.int32)
    mesh.loop_triangles.foreach_get("vertices",indices)
    tri=coords[indices.reshape((-1,3))]
    overlap=((tri[:,:,:2].max(axis=1)>=lower)&(tri[:,:,:2].min(axis=1)<=upper)).all(axis=1)
    count=0
    for polygon in tri[overlap]:
        for a,n in halfplanes:
            polygon=clip(polygon,a,n)
            if len(polygon)<3: break
        if len(polygon)<3: continue
        pts=np.array(polygon)
        area+=abs(pts[:,0]@np.roll(pts[:,1],1)-pts[:,1]@np.roll(pts[:,0],1))*.5
        highest=max(highest,max(pts[:,2]))
        count+=1
    if count: tiles[obj.name]=count
expected=abs(ring[:,0]@np.roll(ring[:,1],1)-ring[:,1]@np.roll(ring[:,0],1))*.5
clearance=school["floor"]-highest
report=dict(source=Path(bpy.data.filepath).name,tiles=tiles,floor_area_m2=expected,covered_area_m2=area,
            minimum_slab_top_to_earth_m=clearance)
(Path(os.environ["CQ_QA_DIR"])/"subgrade.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
assert abs(area-expected)<.01 and clearance>.145,report
