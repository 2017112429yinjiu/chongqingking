"""Find top-facing triangles in the exported local sample under candidate eye positions."""
import struct, sys, json
import numpy as np
from pathlib import Path
root=Path(__file__).resolve().parent
name=sys.argv[1]
file=root/(name+".glb")
with file.open("rb") as f:
    f.seek(12)
    size,_=struct.unpack("<I4s",f.read(8))
    doc=json.loads(f.read(size))
    f.read(8)
    start=f.tell()
points=[tuple(map(float,s.split(","))) for s in sys.argv[2:]]
hits={p:[] for p in points}
for mesh in doc["meshes"]:
    for prim in mesh["primitives"]:
        a=doc["accessors"][prim["attributes"]["POSITION"]]
        view=doc["bufferViews"][a["bufferView"]]
        arr=np.memmap(file,dtype="<f4",mode="r",offset=start+view["byteOffset"],shape=(a["count"]//3,3,8))
        for x,z in points:
            if not (a["min"][0]<=x<=a["max"][0] and a["min"][2]<=z<=a["max"][2]):continue
            xyz=arr[:,:,:3]
            k=(xyz[:,:,0].min(1)<=x)&(xyz[:,:,0].max(1)>=x)&(xyz[:,:,2].min(1)<=z)&(xyz[:,:,2].max(1)>=z)
            pts=xyz[k]
            if not len(pts):continue
            v=pts[:,1]-pts[:,0];w=pts[:,2]-pts[:,0]
            det=v[:,0]*w[:,2]-v[:,2]*w[:,0]
            good=abs(det)>.00001
            v=v[good];w=w[good];o=pts[good,0];det=det[good]
            u=((x-o[:,0])*w[:,2]-(z-o[:,2])*w[:,0])/det
            t=(v[:,0]*(z-o[:,2])-v[:,2]*(x-o[:,0]))/det
            inside=(u>=-.000001)&(t>=-.000001)&(u+t<=1.000001)
            for y in (o[:,1]+u*v[:,1]+t*w[:,1])[inside]:
                hits[x,z].append((round(float(y),3),doc["materials"][prim["material"]]["name"]))
for p,h in hits.items():print(p,sorted(set(h),reverse=True)[:10])

