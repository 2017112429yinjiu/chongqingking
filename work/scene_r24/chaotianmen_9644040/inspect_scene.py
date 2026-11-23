"""Inspect the original MAX hierarchy in Blender while keeping large mesh streams on disk."""
from collections import Counter
from functools import cached_property, lru_cache
import importlib.util
import json
import mmap
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

STUDY = Path(os.environ.get("CQ_MAX_STUDY", Path(__file__).resolve().parent)).resolve()
MAX = next((STUDY / "source").glob("*.max"))
module = STUDY.parents[1] / "tools/max_import_1_9_2/io_scene_max/io_scene_max/import_max.py"
spec = importlib.util.spec_from_file_location("nrgsille_max", module)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
handle = (STUDY / "metadata/Scene").open("rb")
buf = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ)


class Part:
    def __init__(self, kind, begin, end, container, idx=None):
        self.types = kind
        self.begin = begin
        self.end = end
        self.container = container
        self.idx = idx

    @property
    def children(self):
        return list(parts(self.begin, self.end)) if self.container else []

    def get_first(self, kind):
        if self.container:
            return next((c for c in parts(self.begin, self.end) if c.types == kind), None)
        return None

    @property
    def data(self):
        if self.container:
            return None
        raw = buf[self.begin:self.end]
        chunk = reader.ByteArrayChunk(None, self.types, 0, 0, len(raw), None)
        chunk.set_data(raw)
        return chunk.data


def parts(start, stop):
    while start < stop:
        kind, size = struct.unpack_from("<Hi", buf, start)
        header = 6
        if size:
            length = size & 0x7fffffff
        else:
            size, = struct.unpack_from("<q", buf, start + 6)
            header = 14
            length = size & 0x7fffffffffffffff
        if length < header or start + length > stop:
            raise ValueError((kind, start, length, stop))
        yield Part(kind, start + header, start + length, size < 0)
        start += length


ole = reader.ImportMaxFile(str(MAX))
reader.read_class_directory(ole, str(MAX))
reader.read_directory(ole, str(MAX))
root = next(parts(0, len(buf)))
records = root.children
for idx, obj in enumerate(records):
    obj.idx = idx
from types import SimpleNamespace
reader.SCENE_LIST = [SimpleNamespace(children=records)]
is_node = {i for i in set(n.types for n in records)
           if reader.get_guid(Part(i,0,0,False)) == 1 and reader.get_super_id(Part(i,0,0,False)) == 1}

@lru_cache(maxsize=None)
def node_matrix(index):
    n = records[index]
    parent = reader.get_node_parent(n)
    prs, mesh, mat, layer = reader.get_matrix_mesh_material(n)
    matrix = reader.create_matrix(prs) if prs else Matrix.Identity(4)
    if parent and parent.types in is_node and parent.idx != index:
        matrix = node_matrix(parent.idx) @ matrix
    return matrix


def object_pivot(node):
    pos, rot, scale = [node.get_first(t) for t in (0x96A,0x96B,0x96C)]
    q = rot.data if rot else (0.,0.,0.,1.)
    return Matrix.LocRotScale(Vector(pos.data[:3]) if pos else Vector((0,0,0)),
                              Quaternion((q[3],q[2],q[1],q[0])),
                              Vector(scale.data[:3]) if scale else Vector((1,1,1)))


def catalog():
    result = []
    for n in records:
        if n.types not in is_node:
            continue
        name = reader.get_node_name(n).rstrip("\0")
        try:
            prs, mesh, mat, layer = reader.get_matrix_mesh_material(n)
            tr = node_matrix(n.idx).translation
            result.append([n.idx,name,mesh.idx if mesh else None,
                           reader.get_cls_name(mesh).strip("'\0") if mesh else "",
                           [round(v,3) for v in tr],mat.idx if mat else None])
        except (IndexError, KeyError, ValueError, TypeError, AttributeError) as exc:
            result.append([n.idx,name,None,type(exc).__name__,[],None])
    (STUDY / "nodes.json").write_text(json.dumps(result,ensure_ascii=False),encoding="utf8")
    print("CATALOG",len(records),len(result),Counter(row[3] for row in result).most_common(20),flush=True)

if "--catalog" in sys.argv:
    catalog()
