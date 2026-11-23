"""Remove startup frames and transcode a continuous Godot Movie Maker shot."""
from pathlib import Path
import bpy,json,hashlib,sys
W=Path(__file__).resolve().parent
tag=sys.argv[sys.argv.index('--')+1]
assert tag.isidentifier()
revision='r22' if '--r22' in sys.argv else 'r21'
d=W/'project/chongqing_godot_v05'/('verification_'+revision)/tag
stage=W/('scene_'+revision)
data=json.loads((d/'district_take.json').read_text(encoding='utf8'))
avi=stage/f'district_{tag}.avi';mp4=stage/f'district_{tag}.mp4'
s=bpy.context.scene;s.sequence_editor_create()
movie=s.sequence_editor.sequences.new_movie('Forward+ recording',str(avi),channel=1,frame_start=1)
n=data['frames'];s.frame_end=movie.frame_final_duration;s.frame_start=s.frame_end-n+1
assert s.frame_start>0
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.fps=30
s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264'
s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.audio_codec='NONE'
s.view_settings.view_transform='Standard';s.view_settings.look='None'
s.render.filepath=str(mp4);bpy.ops.render.render(animation=True)
review=stage/(tag+'_walk_frames');review.mkdir(exist_ok=True)
for f in [1,61,121,181,241]:
    s.frame_set(s.frame_start+f-1)
    s.render.image_settings.file_format='JPEG';s.render.filepath=str(review/f'{f:03}.jpg')
    bpy.ops.render.render(write_still=True)
encoded=s.sequence_editor.sequences.new_movie('Check encoded stream',str(mp4),channel=2,frame_start=1)
assert encoded.frame_duration==n,(encoded.frame_duration,n)
element=encoded.elements[0]
assert (element.orig_width,element.orig_height)==(1280,720)
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
(d/'movie_review.json').write_text(json.dumps({'frames':n,'native_fps':30,'decoded_size':[element.orig_width,element.orig_height],
    'source_frame_range':[s.frame_start,s.frame_end],'source_avi_sha256':sha(avi),'mp4_sha256':sha(mp4),'method':'Continuous in-engine tracking camera. Trimmed startup and encoded H.264 in Blender. Original colour, silent.'},indent=2),encoding='utf8')
