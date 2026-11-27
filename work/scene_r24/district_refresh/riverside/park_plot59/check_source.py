"""Reopen the independent Plot 59 source or the linked city and probe the park surfaces."""
from pathlib import Path
import json

import bpy
from mathutils import Vector

here = Path(__file__).resolve().parent
assets = here.parents[3] / "project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "park-plot59.json").read_bytes())
scene = bpy.context.scene
objects = scene.objects
paving = objects["COL_Park59_PublicPaving"]
assert all(name in objects for name in plan["new_meshes"] + plan["replacement_meshes"])
assert all(name not in objects for name in plan["retired_objects"])
assert len(paving.data.materials) == 6 and paving.data.uv_layers.active
textures = {node.image.name for finish in paving.data.materials
            for node in finish.node_tree.nodes if node.type=="TEX_IMAGE" and node.image.packed_file}
assert len(textures) >= 4
tests = []
graph = bpy.context.evaluated_depsgraph_get()
for point, name in (([-71.75,-191.86],"old house centre"),([-70.4,-194.4],"shallow sand"),
                    ([-68.67,-184.52],"tree plaza"),([-82.14,-189.93],"pale blue paving")):
    e,n = point
    hit,pos,normal,index,found,_ = scene.ray_cast(graph,Vector((e+.022,n-.031,6.)),Vector((0,0,-1)),distance=12)
    assert hit and found.name==paving.name and normal.z>.90, (
        name,list(pos),found and found.name
    )
    finish = found.data.materials[found.data.polygons[index].material_index]
    tests.append({"spot":name,"contact_enu":list(pos),"material":finish.name})
if bpy.data.filepath.endswith("city_and_outer.local.blend"):
    assert objects.get("COL_Outer500_Frame_61") or objects.get("Park61_WestParkEdgePath")
    assert objects.get("COL_Nanjimen_NorthRailSteelBox")
    assert objects.get("COL_Riverside_62_registered_body")
    assert paving.library and paving.library.filepath.endswith("/park-plot59.blend")
print("CQ_PARK59_SOURCE",json.dumps({"blender":bpy.app.version_string,
      "surfaces":tests,"paving_faces":len(paving.data.polygons),"packed_textures":sorted(textures)}))
