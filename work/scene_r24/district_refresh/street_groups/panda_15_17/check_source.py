"""Check the edited front and public floor when reopening the Panda layer in Blender."""
import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
assets = here.parents[3]/"project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets/"panda-15-17.json").read_bytes())
objects = bpy.context.scene.objects
expected=plan["new_meshes"]+plan["replacement_meshes"]
assert all(name in objects for name in expected)
assert not set(plan["retired_objects"]).intersection(objects.keys())
for name in plan["new_meshes"]:
    obj=objects[name]
    assert obj.data.uv_layers.active and obj.data.uv_layers.active.data, name
    assert all(m.use_nodes for m in obj.data.materials), name
for spec in plan.get("upright_trees", []):
    node=objects[spec["name"]]
    assert (node.location-Vector(spec["enu"])).length < .001
    live_vertices={i for face in node.data.polygons for i in face.vertices}
    heights=[node.data.vertices[i].co.z for i in live_vertices]
    assert min(heights)>1.5 and max(heights)>4., (node.name,min(heights),max(heights))
if Path(bpy.data.filepath).name=="city_and_outer.local.blend":
    for spec in plan["trees"]:
        tree,original = objects[spec["name"]],objects[spec["donor"]]
        assert tree.data==original.data
        assert (tree.location-Vector(spec["enu"])).length < .001
    assert "COL_Houci_1306489251_Asphalt" in objects
paving=objects["COL_Panda228_PublicFlagstones"]
vertices=[paving.matrix_world @ v.co for v in paving.data.vertices]
geom=BVHTree.FromPolygons(vertices,[tuple(f.vertices) for f in paving.data.polygons])
sections=[]
for row in plan["minor_cross_sections"]:
    for en in row:
        hit, normal, _, _ = geom.ray_cast(Vector((*en,60)),Vector((0,0,-1)),70)
        assert hit is not None and normal.z >= .94, (en,hit,normal)
        sections.append([*en,hit.z,normal.z])
print("CQ_PANDA_SOURCE",json.dumps({"source":Path(bpy.data.filepath).name,
  "blender":bpy.app.version_string,"render_faces":{name:len(objects[name].data.polygons) for name in expected},
  "footway_sections":sections,"samples":len(sections)}))
