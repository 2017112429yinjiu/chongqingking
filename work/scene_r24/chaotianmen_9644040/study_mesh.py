"""Measure native triangle mesh nodes and their source transforms without evaluating Max modifiers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_scene import *
import numpy as np

rows = json.loads((STUDY/"nodes.json").read_text(encoding="utf8"))

@lru_cache(maxsize=None)
def base(idx):
    mesh = records[idx]
    if reader.get_guid(mesh) in {0x2032,0x2033}:
        refs = reader.get_references(mesh)
        if refs and refs[-1] and refs[-1].idx != idx:
            return base(refs[-1].idx)
    return mesh

def packed(chunk, code, columns):
    count = struct.unpack_from("<I",buf,chunk.begin)[0]
    assert chunk.end-chunk.begin >= 4 + count*columns*4
    return np.frombuffer(buf,dtype=code,count=count*columns,offset=chunk.begin+4).reshape(-1,columns)

@lru_cache(maxsize=None)
def geom(idx):
    block = records[idx].get_first(0x08fe)
    if not block:
        return None
    v, f = block.get_first(0x0914), block.get_first(0x0912)
    if not (v and f):
        return None
    xyz=packed(v,"<f4",3)
    faces = packed(f,"<u4",5)
    return xyz,faces,block

def xform(row):
    return np.array(node_matrix(row[0]) @ object_pivot(records[row[0]]),dtype="float64")

def measure():
    counts=Counter()
    out=[]
    for row in rows:
        if row[3] not in {"Editable Mesh","Editable Poly","2032","2033"}:continue
        mesh=base(row[2]); counts[reader.get_cls_name(mesh)]+=1
        data=geom(mesh.idx)
        if not data:continue
        v,f,_=data
        if not len(v) or not len(f):continue
        m=xform(row)
        xyz=v@m[:3,:3].T + m[:3,3]
        out.append([row[0],mesh.idx,len(v),len(f),row[-1],xyz.min(axis=0).round(3).tolist(),xyz.max(axis=0).round(3).tolist()])
    (STUDY/"bounds.json").write_text(json.dumps(out,separators=(",",":")),encoding="utf8")
    print("MESH_TOTALS",len(out),sum(r[3] for r in out),counts,flush=True)

if "--measure" in sys.argv:measure()

