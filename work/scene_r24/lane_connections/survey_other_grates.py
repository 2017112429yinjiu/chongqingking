"""Catalogue the remaining legacy seven-bar assemblies from the opened editable scene."""
from pathlib import Path
import bpy, bmesh, json, sys
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parents[1]/'project/chongqing_blender_v05'))
from district_layout import SUPPLEMENTAL, line_distance

def bounds(name):
    obj=bpy.context.scene.objects['Street_small_furniture_'+name]
    mesh=bmesh.new()
    mesh.from_mesh(obj.data)
    mesh.transform(obj.matrix_world)
    remaining=set(mesh.verts)
    result=[]
    while remaining:
        vertices=[remaining.pop()]
        for v in vertices:
            for e in v.link_edges:
                other=e.other_vert(v)
                if other in remaining:
                    remaining.remove(other)
                    vertices.append(other)
        xyz=[[v.co[axis] for v in vertices] for axis in range(3)]
        result.append(tuple((min(values),max(values)) for values in xyz))
    mesh.free()
    return result

bars=bounds('aluminium')
sites=[]
for (x0,x1),(y0,y1),(bottom,lid) in bounds('dark'):
    x=(x0+x1)/2
    y=(y0+y1)/2
    local=[]
    for i in range(7):
        bx=x-.17+.055*i
        candidates=[b for b in bars if abs(sum(b[0])/2-bx)<.0005 and abs(sum(b[1])/2-y)<.0005 and abs(b[2][1]-lid-.0115)<.002]
        if candidates:local.append(candidates[0])
    if len(local)!=7:
        raise ValueError(('expected seven bars',x,y,len(local)))
    path=min(SUPPLEMENTAL,key=lambda r:line_distance((x,y),r[1]))[0]
    sites.append({'position':[x,lid,-y],'bar_top':max(b[2][1] for b in local),'nearest_original_lane':path})
sites.sort(key=lambda row:tuple(row['position']))
output=Path(sys.argv[sys.argv.index('--')+1]).resolve() if '--' in sys.argv else here
(output/'legacy_grate_sites.json').write_text(json.dumps(sites,indent=2),'utf8')
print('EAST17_LEGACY_GRATES',len(sites))
