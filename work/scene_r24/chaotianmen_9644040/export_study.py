"""Write a bounded Godot review sample from genuine MAX base triangles and diffuse inputs."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from study_mesh import *
from collections import defaultdict
from contextlib import redirect_stdout
import os

bounds=json.loads((STUDY/"bounds.json").read_text())
nodes={r[0]:r for r in rows}
stage=STUDY/"review_textures"
images=json.loads((stage/"index.json").read_text())
with open(os.devnull,"w") as silent, redirect_stdout(silent):
    reader.META_DATA=reader.read_chunks(ole,"FileAssetMetaData2",superId=0xA)
mode=sys.argv[sys.argv.index("--")+1]
center=np.array([740000.,10000.,18000.])
region=(430000.,1000000.,-230000.,230000.)
if mode=="street":
    x,y,rad=map(float,sys.argv[-3:])
    region=(x-rad,x+rad,y-rad,y+rad)
layers=defaultdict(list)
why=Counter()
selected=[]
@lru_cache(maxsize=None)
def surface(mid):
    color=(.42,.43,.43)
    texture=None
    if mid is not None:
        m=records[mid]
        kind=reader.get_cls_name(m).strip("'")
        try:
            if kind=="VRayMtl":
                refs=reader.get_reference(m)
                color=reader.get_color(refs[1],1) or color
                texture=reader.get_bitmap(refs.get(7))
            elif kind=="Standard":
                refs=reader.get_references(m)
                shader=reader.get_references(refs[2])[0]
                color=reader.get_color(shader,1) or color
                texture=reader.get_bitmap(reader.get_reference(refs[1]).get(3))
        except (IndexError,ValueError,KeyError,AttributeError,TypeError):
            why["material_read_fallback"]+=1
    return tuple(float(np.clip(c,.018,1.)) for c in color), images.get(str(texture).casefold())

def uv_arrays(block):
    channel=0
    coords=None
    for c in block.children:
        if c.types==0x0959:
            channel=struct.unpack_from("<I",buf,c.begin)[0]
        if c.types in (0x0916,0x2394) and channel==1:coords=packed(c,"<f4",3)
        if c.types in (0x0918,0x2396) and channel==1 and coords is not None:return coords,packed(c,"<u4",3)
    return None,None

for nid,meshidx,nv,nf,mid,lo,hi in bounds:
    x0,x1,y0,y1=region
    if hi[0]<x0 or lo[0]>x1 or hi[1]<y0 or lo[1]>y1 or lo[2]>90000 or hi[2]>145000:continue
    span=np.subtract(hi,lo)
    if mode=="district" and nf>3200 and not (max(span[:2])>42000 and nf<=470000):continue
    row=nodes[nid]
    vert,face,block=geom(meshidx)
    m=xform(row)
    v=(vert@m[:3,:3].T + m[:3,3] - center)*.01
    v=v[:,[0,2,1]]
    v[:,2]*=-1
    tri=face[:,:3].copy()
    if tri.max()>=len(v):
        why["invalid_geometry"]+=1
        continue
    if np.linalg.det(m[:3,:3])<0:tri=tri[:,[2,1,0]]
    pos=v[tri].astype("<f4")
    # Keep incident triangles at the crop boundary. Cameras are framed independently.
    use=np.ones(len(tri),dtype=bool)
    if lo[0]<x0 or hi[0]>x1 or lo[1]<y0 or hi[1]>y1:
        use=(pos[:,:,0].max(1)>=(x0-center[0])*.01)&(pos[:,:,0].min(1)<=(x1-center[0])*.01)&(pos[:,:,2].max(1)>=-(y1-center[1])*.01)&(pos[:,:,2].min(1)<=-(y0-center[1])*.01)
    pos=pos[use]
    if not len(pos):continue
    cross=np.cross(pos[:,1]-pos[:,0],pos[:,2]-pos[:,0])
    lengths=np.linalg.norm(cross,axis=1)
    valid=lengths>.0000001
    if not np.any(valid):continue
    normals=cross[valid]/lengths[valid,None]
    tex_vertices, tex_faces = uv_arrays(block)
    color,texture=surface(mid)
    textured=bool(texture and tex_vertices is not None and tex_faces.shape[0]==nf and tex_faces.max()<len(tex_vertices))
    data=np.zeros((len(normals),3,8),dtype="<f4")
    data[:,:,:3]=pos[valid]
    data[:,:,3:6]=normals[:,None,:]
    if textured:
        uvf=tex_faces[use][valid]
        if np.linalg.det(m[:3,:3])<0:uvf=uvf[:,[2,1,0]]
        data[:,:,6:]=tex_vertices[uvf][:,:,:2]
        data[:,:,7]=1-data[:,:,7]
    key=(mid,texture if textured else None)
    layers[key].append(data.reshape(-1,8))
    selected.append([nid,int(valid.sum()),key[1]])
    why["textured_faces" if textured else "flat_faces"]+=int(valid.sum())

out=STUDY/(mode+".glb")
tmp=STUDY/(mode+".bin.tmp")
doc={"asset":{"version":"2.0","generator":"MAX local assessment"},"scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0}],"meshes":[{"primitives":[]}],"materials":[],"textures":[],"images":[],"buffers":[{}],"bufferViews":[],"accessors":[]}
image_ids={}
with tmp.open("wb") as stream:
    def store(data,**details):
        offset=stream.tell()
        stream.write(data)
        size=stream.tell()-offset
        stream.write(bytes((-size)%4))
        doc["bufferViews"].append(dict(buffer=0,byteOffset=offset,byteLength=size,**details))
        return len(doc["bufferViews"])-1
    for (mid,texture),chunks in layers.items():
        a=np.concatenate(chunks)
        view=store(a,byteStride=32,target=34962)
        attrs={}
        for attr,skip,kind in [("POSITION",0,"VEC3"),("NORMAL",12,"VEC3"),("TEXCOORD_0",24,"VEC2")]:
            if attr=="TEXCOORD_0" and not texture:continue
            ac=dict(bufferView=view,componentType=5126,count=len(a),byteOffset=skip,type=kind)
            if attr=="POSITION":
                ac.update(min=a[:,:3].min(0).tolist(),max=a[:,:3].max(0).tolist())
            attrs[attr]=len(doc["accessors"])
            doc["accessors"].append(ac)
        color,_=surface(mid)
        pbr={"baseColorFactor":list((1.,1.,1.) if texture else color)+[1.],"roughnessFactor":1.,"metallicFactor":0.}
        if texture:
            if texture not in image_ids:
                v=store((stage/texture).read_bytes())
                image_ids[texture]=len(doc["images"])
                doc["images"].append(dict(bufferView=v,mimeType="image/jpeg",name=texture))
                doc["textures"].append(dict(source=image_ids[texture]))
            pbr["baseColorTexture"]={"index":image_ids[texture]}
        mi=len(doc["materials"])
        doc["materials"].append(dict(name="source_"+str(mid),doubleSided=True,pbrMetallicRoughness=pbr))
        doc["meshes"][0]["primitives"].append({"attributes":attrs,"material":mi,"mode":4})
        chunks.clear()
primitives=doc["meshes"][0]["primitives"]
doc["meshes"]=[{"primitives":primitives[i:i+64]} for i in range(0,len(primitives),64)]
doc["nodes"]=[{"mesh":i} for i in range(len(doc["meshes"]))]
doc["scenes"][0]["nodes"]=list(range(len(doc["nodes"])))
size=tmp.stat().st_size
doc["buffers"][0]["byteLength"]=size
j=json.dumps(doc,separators=(",",":")).encode()
j+=b" "*((-len(j))%4)
import shutil
with out.open("wb") as wr,tmp.open("rb") as src:
    wr.write(struct.pack("<4sII",b"glTF",2,28+len(j)+size))
    wr.write(struct.pack("<I4s",len(j),b"JSON")+j)
    wr.write(struct.pack("<I4s",size,b"BIN\0"))
    shutil.copyfileobj(src,wr,4*1024*1024)
tmp.unlink()
stats=dict(mode=mode,region=region,origin=center.tolist(),assumed_meters_per_unit=.01,nodes=len(selected),materials=len(layers),images=len(image_ids),triangles=sum(v[1] for v in selected),counts=why,bytes=out.stat().st_size)
(STUDY/(mode+"_sample.json")).write_text(json.dumps(dict(stats=stats,nodes=selected),indent=None),encoding="utf8")
print("EXPORTED",stats,flush=True)

