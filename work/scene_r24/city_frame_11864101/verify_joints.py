import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parent
scene=bpy.context.scene
deps=bpy.context.evaluated_depsgraph_get()
def worldverts(o):
    return [o.matrix_world@v.co for v in o.data.vertices]
def intervals(name,x,y):
    o=scene.objects[name]; im=o.matrix_world.inverted()
    tree=BVHTree.FromObject(o,deps);point=Vector((x,y,38));z=[]
    for k in range(9):
        h,n,i,d=tree.ray_cast(im@point,im.to_3x3()@Vector((0,0,-1)))
        if h is None:break
        pt=o.matrix_world@h;z.append(pt.z);point=pt-Vector((0,0,.00015))
    return [min(z),max(z)] if len(z)>1 else []
checks=[]
for i in range(3):
    verts=worldverts(scene.objects[f'Canopy{i}_Roof'])
    cx=(min(v.x for v in verts)+max(v.x for v in verts))/2
    cy=(min(v.y for v in verts)+max(v.y for v in verts))/2
    for a in [-1,1]:
        for b in [-1,1]:
            x=cx+a*1.7+.001;y=cy+b*1.5+.001
            ints=[intervals(f'Canopy{i}_{n}',x,y) for n in ['Posts','SideRail','Purlins','Roof']]
            assert all(ints),ints
            gaps=[round(t[0]-s[1],4) for s,t in zip(ints,ints[1:])]
            checks.append(dict(site=i,xy=[x,y],gaps_m=gaps))
assert all(max(r['gaps_m'])<.002 for r in checks),checks
target=scene.objects['Court_Rim_Target']
j=dict(post_to_beam_to_roof=checks,board_target_quads=len(target.data.polygons),city_meshes=len(bpy.data.collections['R24_11_Local_city_frame'].objects))
(root/'reopen_final.json').write_text(json.dumps(j,indent=2),encoding="utf8")
print('JOINTS',len(checks),max(max(r['gaps_m']) for r in checks),flush=True)

