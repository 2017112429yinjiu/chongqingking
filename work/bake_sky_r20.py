"""Bake two local diffuse sky-visibility fields from actual opaque static geometry."""
import bpy, math, struct, zlib, json, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

W = Path(__file__).resolve().parent
out = W/'project/chongqing_godot_v05/assets/lane_r20'
out.mkdir(parents=True, exist_ok=True)
verts, polys = [], []
for ob in bpy.context.scene.objects:
    if ob.type != 'MESH' or ob.hide_render or ob.name.startswith('COLH_'):
        continue
    if not (ob.name.startswith(('COL_', 'R19_Canvas_awning', 'B_A01_noodle', 'IR_B_A01'))):
        continue
    bounds = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    if (min(p.x for p in bounds) > 5 or max(p.x for p in bounds) < -68
        or min(p.y for p in bounds) > 84 or max(p.y for p in bounds) < -95):
        continue
    if any('glass' in m.name.lower() for m in ob.data.materials if m):
        continue
    off = len(verts)
    verts.extend(ob.matrix_world @ v.co for v in ob.data.vertices)
    polys.extend(tuple(off+i for i in f.vertices) for f in ob.data.polygons)
tree = BVHTree.FromPolygons(verts,polys)
dirs = []
for i in range(64):
    r = math.sqrt((i+.5)/64)
    phi = i*math.pi*(3-math.sqrt(5))
    dirs.append(Vector((r*math.cos(phi),r*math.sin(phi),math.sqrt(1-r*r))))

def chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))

regions = {}
for name, origin, dims in [('shop',(-35,-74,10),(35,42,15)),('alley',(-42,37,24),(35,50,16))]:
    nx,ny,nz = dims
    pixels = bytearray()
    bins = []
    for k in range(nz):
        for j in range(ny):
            pixels.append(0)
            for i in range(nx):
                p=Vector((origin[0]+i*.5,origin[1]+j*.5,origin[2]+k*.75))
                hits = [tree.ray_cast(p,d,22)[3] for d in dirs]
                # Distant obstructions fade smoothly into the sky dome.
                value = sum(1 if t is None else (t/22)**2 for t in hits)/len(hits)
                bins.append(value)
                pixels.append(round(value*255))
    path=out/(name+'_sky.png')
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',nx,ny*nz,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(pixels,9))+chunk(b'IEND',b''))
    regions[name]=dict(origin=origin,dimensions=dims,spacing=[.5,.5,.75],directions=len(dirs),probes=len(bins),min=min(bins),max=max(bins),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
(out/'sky_fields.json').write_text(json.dumps(regions,indent=2),encoding='utf-8')
print('R20_SKY',len(polys),regions)
