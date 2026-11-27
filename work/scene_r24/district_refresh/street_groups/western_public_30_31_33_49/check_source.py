"""Check reopened stone courses and route support in the final west-side increment."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
assets = here.parents[4] / "work/project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "western-public-30-31-33-49.json").read_text())
objects = bpy.context.scene.objects
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in plan["new_meshes"]+plan["replacement_meshes"]:
    geo = objects[name].data
    assert geo.polygons and geo.uv_layers, name
for name in plan["retired_objects"]:
    assert name not in objects, name
support = {}
for code, points in plan["walks"].items():
    tree = BVHTree.FromObject(objects[f"COL_Western{code}_OutdoorStoneFlags"], depsgraph)
    hits = []
    for east, north, y in points:
        pos, normal, _, _ = tree.ray_cast(Vector((east,north,y+.20)),Vector((0,0,-1)),.40)
        assert pos is not None and abs(pos.z-y)<.035 and normal.z>.80, (code,east,north,y,pos,normal)
        hits.append(list(pos))
    support[code] = hits
spec = json.loads((here/"field.json").read_text())["registered_2015_wall_pipe"]
pipe = objects["Western33_LocatedPipeAndClamps"]
pipe_tree = BVHTree.FromObject(pipe,depsgraph)
pipe_hit,_,_,_ = pipe_tree.ray_cast(Vector((*spec["en"],45.)),Vector((0,0,-1)),25.)
assert pipe_hit is not None, spec["en"]
print("CQ_WESTERN_PUBLIC_SOURCE "+json.dumps({
    "supports":support,"file":bpy.data.filepath,"engine":bpy.app.version_string,"pipe_top":list(pipe_hit),
}))
