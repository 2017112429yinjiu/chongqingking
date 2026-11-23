from pathlib import Path
import bpy, json, math
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
p=here.parents[2]/'project/chongqing_godot_v05'
sites=json.loads((p/'assets/lane_inlets_r24/inlets.json').read_text('utf8'))
scene=bpy.context.scene
def tree(name):
    obj=scene.objects[name]
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[face.vertices[:] for face in obj.data.polygons])
grate=tree('COL_East17_IronGrate')
floor=tree('COL_Terrain_200m_pavement')
base=tree('East17_GullyBed')
old=[tree('Street_small_furniture_'+s) for s in ['aluminium','dark']]
observed=[]
for s in sites:
    x,z,neg_y=s['centre'];sx,sy=s['slope']
    damage=[]
    for i in range(15):
        u=-.18+i*.0257
        level=z+sx*u
        start=(x+u,-neg_y,level+.15)
        bar=grate.ray_cast(start,(0,0,-1),.30)[0]
        bed=base.ray_cast(start,(0,0,-1),.30)[0]
        cover=floor.ray_cast(start,(0,0,-1),.30)[0]
        assert bed is not None and abs(level-bed.z-.055)<.003 and cover is None
        assert (bar is None)==(i%2==1)
        if bar is not None:damage.append(abs(bar.z-level))
    ox,oy=s['original_xy']
    assert all(obj.ray_cast((ox,oy,z+.6),(0,0,-1),1.)[0] is None for obj in old)
    observed.append({'centre':s['centre'],'bar_error_m':max(damage),'bars':8,'slots':7,'vacated_original':True})
assert len([lib for lib in bpy.data.libraries if Path(bpy.path.abspath(lib.filepath)).is_file()])>=3
(here/'reopen.json').write_text(json.dumps({'opened':bpy.data.filepath,'engine':bpy.app.version_string,'sites':observed},indent=2,ensure_ascii=False),'utf8')
print('INLETS_REOPEN',observed)
