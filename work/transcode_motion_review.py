"""Review transcode: engine AVI to lossy H.264, no grading, cuts or image edits."""
from pathlib import Path
import bpy,json,sys,hashlib
root=Path(__file__).resolve().parent
tag=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'r18_motion'
assert tag.replace('_','').isalnum()
source_metadata=root/f'project/chongqing_godot_v05/verification_r18/motion_takes/{tag}.json'
evidence=json.loads(source_metadata.read_text(encoding='utf-8'))
scene=bpy.context.scene
scene.sequence_editor_create()
movie=scene.sequence_editor.sequences.new_movie('Raw Godot capture',str(root/f'audit/{tag}.avi'),channel=1,frame_start=1)
scene.frame_start=1;scene.frame_end=movie.frame_final_duration
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.fps=30
scene.render.use_sequencer=True;scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='HIGH';scene.render.ffmpeg.ffmpeg_preset='GOOD'
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.render.filepath=str(root/f'audit/{tag}.mp4')
print('REVIEW_TRANSCODE_FRAMES',scene.frame_end,flush=True)
bpy.ops.render.render(animation=True)
# Unaltered decoded source frames for inspecting contact and expression at intervals.
scene.render.image_settings.file_format='PNG'
frames=[30,60,75,90,130,150,180,210,240,250,270,290,315,345,375,408] if 'rider' in tag else [30,90,150,210,270,315,345,375,390,408,423,440,462,485,510]
for frame in [f for f in frames if f<=scene.frame_end]:
    scene.frame_set(frame);scene.render.filepath=str(root/f'audit/{tag}_frames/frame_{frame:03}.png');bpy.ops.render.render(write_still=True)
evidence.update({'source':'Godot Movie Maker native render','resolution':[1280,720],'fps':30,'frames':scene.frame_end,'postprocessing':'No grading or cuts; lossy H264 video-only conversion; Standard display transform. Original engine WAV retained separately if generated.','source_avi':tag+'.avi','source_avi_sha256':hashlib.file_digest((root/f'audit/{tag}.avi').open('rb'),'sha256').hexdigest(),'mp4':tag+'.mp4'})
(root/f'audit/{tag}_metadata.json').write_text(json.dumps(evidence,indent=2))
