"""Open-footprint study of the photographed riverside park service building."""
import json
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector

here=Path(__file__).resolve().parent
root=here.parents[2]
group=root/'district_refresh/street_groups'
sys.path[:0]=[str(group),str(group/'guoco')]
from factory import Mesh, material, terrain
from factory_glazing import glaze_material

spec=json.loads((here/'registration.json').read_bytes())
south_east,north_east,north_west,south_west=map(Vector,spec['footprint'])
width=(north_east-north_west).length
depth=((south_east-north_east).length+(south_west-north_west).length)*.5
surface=terrain()

def xy(u,v):
    edge0=north_west.lerp(north_east,u/width)
    edge1=south_west.lerp(south_east,u/width)
    return edge0.lerp(edge1,v/depth)

def height(u,v):
    p=xy(u,v)
    hit,*_=surface.ray_cast(Vector((p.x,p.y,60.)),Vector((0.,0.,-1.)))
    if hit is None:
        raise ValueError((u,v))
    return hit.z

def pt(u,v,z):
    p=xy(u,v)
    return p.x,p.y,z

def block(mesh,u1,u2,v1,v2,z1,z2,finish):
    ring=[(u1,v1),(u1,v2),(u2,v2),(u2,v1)]
    mesh.solid([pt(u,v,z1) for u,v in ring],[pt(u,v,z2) for u,v in ring],finish)

def front(mesh,u1,u2,v,z1,z2,finish):
    mesh.face([pt(u1,v,z1),pt(u2,v,z1),pt(u2,v,z2),pt(u1,v,z2)],finish)

ochre = glaze_material('Park building red ground course',(.45,.196,.120),.79)
tile=[glaze_material(f'Park original-style ceramic {i}', rgb,.74) for i,rgb in enumerate(
    [(.52,.244,.158),(.49,.217,.138),(.47,.205,.129),(.55,.270,.183)])]
cream=material('Warm pale upper render',(.78,.61,.37),'plastered_wall_04_diff_2k.jpg')
soffit=material('Pale concrete roof edge',(.81,.79,.72),'concrete_wall_006_diff_2k.jpg')
stone=material('Entry cut slate flags',(.48,.45,.40),'stone_floor_diff_2k.jpg')
frame=glaze_material('Shaded metal window frame',(.082,.084,.073),.64)
glass=glaze_material('Visible shaded window panes',(.114,.202,.190),.26,.19)
back=glaze_material('Recessed glass back wall',(.037,.046,.041),.68)
structure=Mesh('COL_Riverside_62_registered_body')
finish=Mesh('Riverside_62_red_tiles_open_reveal_and_vents')
roof=Mesh('Riverside_62_asymmetric_eaves')
basis=min(height(u,v) for u,v in [(0,0),(0,depth),(width,0),(width,depth)])-.24
entry_left,entry_right=2.82,5.08
datum=height((entry_left+entry_right)*.5,-.32)+.08
high=datum+2.70
ridge=3.88

def eave(u):
    return datum+(3.94+u*.35 if u<ridge else 5.298-(u-ridge)*.36)

block(structure,0,width,0,depth,basis,datum-.12,stone)
block(structure,0,.22,.22,depth,datum-.12,datum+3.98,ochre)
block(structure,width-.24,width,.22,depth,datum-.12,datum+3.19,ochre)
block(structure,.22,width-.24,depth-.25,depth,datum-.12,datum+3.29,ochre)
block(structure,entry_left,entry_right,1.58,1.85,datum,high,back)
block(structure,0,entry_left,0,.27,datum,high,ochre)
block(structure,entry_right,width,0,.27,datum,high,ochre)
block(structure,entry_left,entry_left+.14,0,1.65,datum,high,ochre)
block(structure,entry_right-.14,entry_right,0,1.65,datum,high,ochre)
block(structure,entry_left+.14,entry_right-.14,-.40,1.64,datum-.14,datum,stone)
block(structure,entry_left,entry_right,0,.31,high-.17,high+.13,ochre)
block(structure,entry_left+.06,entry_right-.06,0,.34,high+.73,high+.88,ochre)

# The ground face reads as panel cladding, including the framed actual windows.
for left,right in [(0,entry_left),(entry_right,width)]:
    n=1+int((right-left)/.58)
    for column in range(n):
        u1,u2=left+(right-left)*column/n,left+(right-left)*(column+1)/n
        for row in range(6):
            z1=datum+.04+row*.433
            front(finish,u1+.008,u2-.008,-.009,z1,z1+.416,tile[(column*7+row*3)%4])
for u1,u2,z1,z2 in [(.52,2.34,datum+.99,datum+1.95),(.77,2.43,datum+3.10,datum+3.95)]:
    block(finish,u1-.05,u2+.05,-.048,-.015,z1-.05,z2+.05,frame)
    for j in range(3):
        l=u1+(u2-u1)*j/3.
        rr=u1+(u2-u1)*(j+1)/3.
        front(finish,l+.027,rr-.027,-.051,z1+.03,z2-.034,glass)
for z in (datum+.42,datum+1.58):
    front(finish,width-1.24,width-.51,-.032,z,z+.38,frame)
    for j in range(4):
        front(finish,width-1.18,width-.57,-.035,z+.044+j*.077,z+.065+j*.077,soffit)
for j in range(7):
    x=entry_left+(entry_right-entry_left)*(j+.05)/7.
    block(structure,x,x+.083,0,.28,high+.07,high+.72,ochre)
block(structure,entry_left,entry_right,0,.27,high+.35,high+.40,ochre)

# Eave heights are visual estimates from the photograph.
for a,b in ((0,entry_left),(entry_right,ridge) if entry_right<ridge else (entry_right,7.),(7.,width)):
    if b<=a:
        continue
    finish.face([pt(a,0.,high),pt(b,0.,high),pt(b,0.,eave(b)),pt(a,0.,eave(a))],cream)
finish.face([pt(entry_left,.23,high+.87),pt(ridge,.23,high+.87),pt(ridge,.23,eave(ridge)),pt(entry_left,.23,eave(entry_left))],ochre)
finish.face([pt(ridge,.23,high+.87),pt(entry_right,.23,high+.87),pt(entry_right,.23,eave(entry_right)),pt(ridge,.23,eave(ridge))],ochre)
for u in (0.11,entry_left-.06,entry_right+.03,6.38,7.56,8.63,width-.14):
    block(finish,u,u+.105,-.039,.014,high-.01,min(eave(u),eave(u+.105)),ochre)
for a,b in ((-.56,ridge),(ridge,width+.62)):
    order=[(a,-.54),(a,depth+.35),(b,depth+.35),(b,-.54)]
    roof.solid([pt(u,v,eave(u)) for u,v in order],[pt(u,v,eave(u)+.16) for u,v in order],soffit)
for v in (-.45,-.71):
    step=height((entry_left+entry_right)*.5,v)
    h=max(step+.04,datum-(.15 if v<-.6 else .075))
    block(structure,entry_left-.14,entry_right+.14,v-.25,v+.09,min(step-.10,h-.12),h,stone)
keep=[m.save() for m in (structure,finish,roof)]
for obj in list(bpy.data.objects):
    if obj not in keep:
        bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
bpy.context.preferences.filepaths.save_version=0
staging=Path(os.environ['CQ_PAVILION62_STAGING'])
staging.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(staging/'pavilion62-body.blend'),compress=True)
study={'footprint':spec['footprint'],'door_threshold_east_north':list(xy((entry_left+entry_right)*.5,0)),
       'threshold_y':datum,'base_y':basis,'width_m':width,'depth_m':depth,'visual_ridge_y':eave(ridge)+.16}
(staging/'model-dimensions.json').write_text(json.dumps(study,indent=2)+'\n')
print('CQ_RIVERSIDE_62_SHELL',study)
