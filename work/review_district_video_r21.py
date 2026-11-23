"""Decode the saved MP4, measure adjacent frames and retain a contact sheet."""
from pathlib import Path
import hashlib
import json
import tempfile
import sys

import bpy
import numpy as np


work = Path(__file__).resolve().parent
revision = 'r22' if '--r22' in sys.argv else 'r21'
tag=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--take=')),'current')
assert tag.isidentifier()
folder = work/'project/chongqing_godot_v05'/('verification_'+revision)/tag
source = work/('scene_'+revision)/('district_'+tag+'.mp4')
report = json.loads((folder/'movie_review.json').read_text(encoding='utf8'))
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest() == report['mp4_sha256']
scene = bpy.context.scene
scene.sequence_editor_create()
clip = scene.sequence_editor.sequences.new_movie('Decode saved H264',str(source),channel=1,frame_start=1)
assert clip.frame_duration == report['frames']
scene.frame_start, scene.frame_end = 1, clip.frame_duration
scene.render.resolution_x,scene.render.resolution_y = 1280,720
scene.render.resolution_percentage = 25
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
previous = None
deltas = []
selected = {}
with tempfile.TemporaryDirectory() as temp:
    scene.render.filepath = str(Path(temp)/'frame_')
    bpy.ops.render.render(animation=True)
    for frame in range(1,clip.frame_duration+1):
        path = Path(temp)/f'frame_{frame:04d}.png'
        im = bpy.data.images.load(str(path))
        assert list(im.size)==[320,180], path
        px = np.empty(320*180*4,dtype=np.float32)
        im.pixels.foreach_get(px)
        rgb = px.reshape(180,320,4)[:,:,:3]
        assert np.isfinite(rgb).all() and rgb.std()>.01, path
        if previous is not None:deltas.append(float(np.abs(rgb-previous).mean()))
        if (frame-1)%30==0:selected[frame]=rgb.copy()
        previous=rgb.copy()
        bpy.data.images.remove(im)
canvas=np.ones((180*3,320*3,4),dtype=np.float32)
for i,(frame,rgb) in enumerate(selected.items()):
    row=2-i//3;col=i%3
    canvas[row*180:(row+1)*180,col*320:(col+1)*320,:3]=rgb
image=bpy.data.images.new('Encoded video contact sheet',width=960,height=540)
image.pixels.foreach_set(canvas.ravel())
image.filepath_raw=str(folder/'movie_decoded_contact.png')
image.file_format='PNG'
image.save()
(folder/'movie_decode.json').write_text(json.dumps({'mp4_sha256':report['mp4_sha256'],
    'decoded_frames':clip.frame_duration,'measured_thumbnail_size':[320,180],
    'contact_sheet_frames':list(selected),'mean_absolute_linear_rgb_step':deltas,
    'largest_adjacent_step_after_frame':int(np.argmax(deltas))+1},indent=2),encoding='utf8')
