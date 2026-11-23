"""Encode the continuous 15 fps native take, keeping player camera and HUD."""
import bpy,json
from pathlib import Path
import sys
study=Path(__file__).resolve().parent
folder=study.parents[1]/'project/chongqing_godot_v05/verification_r24/vertical_run'/sys.argv[-1]
files=sorted((folder/'take').glob('walk_*.jpg'))
assert len(files)==json.loads((folder/'route.json').read_text('utf8'))['native_frames_15fps'] and len(files)>150
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
editor=scene.sequence_editor_create()
strip=editor.sequences.new_image('Godot player viewport',str(files[0]),1,1)
for f in files[1:]:strip.elements.append(f.name)
strip.frame_final_duration=len(files)
scene.render.resolution_x=1152;scene.render.resolution_y=648;scene.render.resolution_percentage=100
scene.render.fps=15
scene.frame_start=1;scene.frame_end=len(files)
scene.view_settings.view_transform='Standard'
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='HIGH'
scene.render.filepath=str(folder/'穿楼托送实走.mp4')
bpy.ops.render.render(animation=True)
