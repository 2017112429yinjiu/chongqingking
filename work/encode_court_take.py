"""Encode a continuous engine take; remove the startup and camera settling frames."""
from pathlib import Path
import bpy, json, hashlib
W=Path(__file__).resolve().parent
evidence=W/'project/chongqing_godot_v05/verification_r20/current/resident_motion'
data=json.loads((evidence/'take.json').read_text())
raw=W/'audit/court_resident.avi'
scene=bpy.context.scene
scene.sequence_editor_create()
movie=scene.sequence_editor.sequences.new_movie('Godot scene',str(raw),channel=1,frame_start=1)
frames=data['take_frames']
assert movie.frame_final_duration>=frames
scene.frame_end=movie.frame_final_duration
scene.frame_start=scene.frame_end-frames+1
scene.render.resolution_x=1280;scene.render.resolution_y=720
scene.render.resolution_percentage=100;scene.render.fps=30
scene.render.image_settings.file_format='FFMPEG';scene.render.ffmpeg.format='MPEG4'
scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='HIGH'
scene.render.ffmpeg.audio_codec='NONE'
scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
scene.render.filepath=str(W/'audit/court_resident.mp4')
bpy.ops.render.render(animation=True)
data['raw_avi_sha256']=hashlib.file_digest(raw.open('rb'),'sha256').hexdigest()
data['mp4_sha256']=hashlib.file_digest((W/'audit/court_resident.mp4').open('rb'),'sha256').hexdigest()
data['source_frame_range']=[scene.frame_start,scene.frame_end]
data['encoding']='One continuous shot. Startup trimmed, H.264 video only, no grading or animation edits.'
(evidence/'encoding.json').write_text(json.dumps(data,indent=2))
for index in [1,45,76,118,170,250]:
    scene.frame_set(scene.frame_start+index-1)
    scene.render.image_settings.file_format='JPEG'
    scene.render.filepath=str(W/'audit'/f'court_resident_review_{index:03}.jpg')
    bpy.ops.render.render(write_still=True)
