"""Walking-player view of the existing licensed commuter. Remove head/neck geometry only."""
from pathlib import Path
import bpy,bmesh
W=Path(__file__).resolve().parent;S=W/'scene_r23'
ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');rig=ob.parent
groups={g.index for g in ob.vertex_groups if any(word in g.name.lower() for word in ['head','neck','jaw','brow','eye','lip','tongue','cheek','nose','mouth','teeth',' ear','face'])}
ids={v.index for v in ob.data.vertices if sum(g.weight for g in v.groups if g.group in groups)>.24}
bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in ids],context='VERTS');bm.to_mesh(ob.data);bm.free()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(S/'walking_body.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(S/'assets/body_view.glb'),export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_frame_range=False,export_force_sampling=True,export_morph=False)

