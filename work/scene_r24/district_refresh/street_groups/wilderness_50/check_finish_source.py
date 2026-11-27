"""Reopen the independent stone finish or the assembled exterior in Blender."""
import json
from pathlib import Path

import bpy

here=Path(__file__).resolve().parent
asset=here.parents[4] / "work/project/chongqing_godot_v05/assets/district_500/wilderness-50-finish.json"
plan=json.loads(asset.read_text())
scene=bpy.context.scene
counts={}
for name in plan["replacement_meshes"]+plan["new_meshes"]:
    mesh=scene.objects[name].data
    assert mesh.uv_layers and len(mesh.polygons)>0, name
    assert all(not slot.is_missing for slot in mesh.materials), name
    counts[name]={"vertices":len(mesh.vertices),"faces":len(mesh.polygons),"materials":len(mesh.materials)}
    for slot in mesh.materials:
        if slot.name in plan["surface_textures"]:
            nodes=[node for node in slot.node_tree.nodes if node.type=="TEX_IMAGE"]
            assert len(nodes)==1 and nodes[0].image.packed_file,slot.name
print("CQ_RENAI50_FINISH_SOURCE "+json.dumps({"version":bpy.app.version_string,"file":bpy.data.filepath,"meshes":counts}))
