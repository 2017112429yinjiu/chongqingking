from pathlib import Path
import bpy,json,math
from mathutils import Vector
root=Path(__file__).resolve().parent
p=root/'project/chongqing_godot_v05/assets'
views=json.loads((p/'viewpoints.json').read_text(encoding='utf8'))['views']
views.update(json.loads((p/'render_profile_r20.json').read_text(encoding='utf8'))['diagnostic_views'])
def bl(v):return Vector((v[0],-v[2],v[1]))
dg=bpy.context.evaluated_depsgraph_get()
result={}
for name in ['r20_tree_court','central_steps','street_entry','noodle_corner','roofscape','residential_entry','west_lane','narrow_passage']:
    cam=views[name];eye=bl(cam['position']);aim=(bl(cam['target'])-eye).normalized()
    right=aim.cross(Vector((0,0,1))).normalized();up=right.cross(aim)
    extent=math.tan(math.radians(cam['fov'])/2)
    cells=[]
    for v in [.12,.24,.34,.45,.55,.70,.86]:
        for u in [.08,.22,.36,.50,.64,.78,.92]:
            ray=(aim+right*((2*u-1)*extent*16/9)+up*((1-2*v)*extent)).normalized()
            hit,pt,normal,index,ob,_=bpy.context.scene.ray_cast(dg,eye,ray,distance=1400)
            row={'uv':[u,v]}
            if hit:
                mat=ob.material_slots[ob.data.polygons[index].material_index].name if index<len(ob.data.polygons) and ob.material_slots else ''
                row.update(point=[round(x,2) for x in pt],object=ob.name,material=mat)
            cells.append(row)
    result[name]={'camera':cam,'rays':cells}
def bounds(o):
    vv=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[round(f(v[i] for v in vv),2) for i in range(3)] for f in [min,max]]
result['meshes']={o.name:{'bounds':bounds(o),'materials':[s.name for s in o.material_slots]} for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith(('Terrain','Outer_ground','Context_','Authored_distant','Planting_soil')))}
(root/'scene_r21/district_rays.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf8')
