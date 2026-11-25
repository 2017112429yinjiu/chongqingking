"""Render the real market frame from the reopened Blender asset as a cutaway."""
import json
import os
from math import cos, sin
from pathlib import Path

import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[3]
asset=root/"work/scene_r24/district_500/outer_district.blend"
assert Path(bpy.data.filepath).resolve()==asset and bpy.app.version==(4,3,2)
layout=json.loads((root/"work/project/chongqing_godot_v05/assets/district_500/layout.json").read_text(encoding="utf-8"))
p=next(p for p in layout["plots"] if p["name"]=="照相巷便民市场")
source=bpy.data.objects["COL_Outer500_Frame_%02d"%p["plot_id"]]
original=source.data
c,s=cos(p["bearing"]),sin(p["bearing"])
def local(vertex):
    x,y,z=source.matrix_world @ vertex.co
    x-=p["east_north"][0]; y-=p["east_north"][1]
    return Vector((c*x+s*y,-s*x+c*y,z-p["height"]))

def cut_slab(poly):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if a.y>=2.8: result.append(a)
        if (a.y>=2.8)!=(b.y>=2.8): result.append(a.lerp(b,(2.8-a.y)/(b.y-a.y)))
    return result

vertices=[]; faces=[]; colors=[]
parts={"column":0,"beam":0,"slab":0,"omitted_wall":0}
assert len(original.polygons)%6==0
for index in range(0,len(original.polygons),6):
    polys=[[local(original.vertices[v]) for v in original.polygons[i].vertices] for i in range(index,index+6)]
    z=[v.z for poly in polys for v in poly]; height=max(z)-min(z)
    kind="column" if height>p["floors"]*2.95 else "omitted_wall" if height>1 else "slab" if abs(height-.15)<.003 else "beam"
    parts[kind]+=1
    if kind=="omitted_wall": continue
    for poly in polys:
        pts=cut_slab(poly) if kind=="slab" else poly
        if len(pts)<3: continue
        faces.append(tuple(range(len(vertices),len(vertices)+len(pts))))
        vertices.extend(pts); colors.append(("column","beam","slab").index(kind))
assert all(parts.values())
scene=bpy.data.scenes.new("Market frame inspection")
bpy.context.window.scene=scene
mesh=bpy.data.meshes.new("Cutaway from saved frame faces")
mesh.from_pydata(vertices,[],faces)
item=bpy.data.objects.new("Market structural section",mesh)
scene.collection.objects.link(item)
for name,color in (("Column",(.42,.43,.41)),("Beam",(.68,.44,.24)),("Slab",(.36,.49,.52))):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1)
    mesh.materials.append(mat)
for poly,slot in zip(mesh.polygons,colors): poly.material_index=slot
camera=bpy.data.cameras.new("Axonometric")
view=bpy.data.objects.new("Inspection camera",camera);scene.collection.objects.link(view)
view.location=(23,-35,22); target=Vector((0,0,4.2))
view.rotation_euler=(target-view.location).to_track_quat("-Z","Y").to_euler()
camera.type="ORTHO";camera.ortho_scale=33.0;scene.camera=view
scene.render.engine="BLENDER_WORKBENCH"
shade=scene.display.shading;shade.light="STUDIO";shade.color_type="MATERIAL"
shade.show_shadows=True;shade.show_cavity=True;shade.cavity_type="WORLD";shade.show_specular_highlight=False
shade.background_type="WORLD";scene.world=bpy.data.worlds.new("Paper");scene.world.color=(.71,.72,.70)
scene.render.resolution_x=1200;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
folder=Path(os.environ["CQ_QA_DIR"])
scene.render.filepath=str(folder/"market_frame.png")
bpy.ops.render.render(write_still=True)
(folder/"cutaway.json").write_text(json.dumps({"source":asset.relative_to(root).as_posix(),"object":source.name,
    "parts":parts,"display":"Original saved mesh faces. Upper perimeter infill hidden; rear slab portion shown from local v=2.8 m."},indent=2),encoding="utf-8")
