"""Compare the same scripted 262-frame shot, including static bench-edge regions, from native Godot AVI files."""
from pathlib import Path
from io import BytesIO
import json
import mmap
import struct
import numpy as np
from PIL import Image

W=Path(__file__).resolve().parent
V=W/'project/chongqing_godot_v05/verification_r20'
def load_json(path):return json.loads(path.read_text())

def video_chunks(stream,start,end):
    while start+8<=end:
        tag,size=struct.unpack_from('<4sI',stream,start);data=start+8
        if tag in [b'RIFF',b'LIST'] and size>=4:
            yield from video_chunks(stream,data+4,data+size)
        elif tag in [b'00dc',b'00db'] and size:
            yield data,size
        start=data+size+(size%2)

before=load_json(V/'trial11/resident_motion/encoding.json')
after=load_json(V/'current/resident_motion/encoding.json')
assert before['scene']==after['scene'] and before['fps']==after['fps']==30
assert before['profile_sha256']!=after['profile_sha256'] and before['take_frames']==after['take_frames']==262
paths=[W/'audit/court_motion11/court_resident.avi',W/'audit/court_resident.avi']
files=[path.open('rb') for path in paths]
maps=[mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) for f in files]
frames=[list(video_chunks(stream,0,len(stream))) for stream in maps]
for i,meta in enumerate([before,after]):
    first,last=meta['source_frame_range']
    assert len(frames[i])>=last,(i,len(frames[i]),last)
    frames[i]=frames[i][first-1:last]
field=(175,395,439,680)
errors=[];temporal=[[],[]];previous=[None,None]
for i in range(262):
    down=[]
    for k in range(2):
        loc,length=frames[k][i]
        with Image.open(BytesIO(maps[k][loc:loc+length])) as im:
            assert im.size==(1280,720)
            im=im.convert('L')
            patch=np.asarray(im.crop(field),dtype=np.int16)
            down.append(np.asarray(im.resize((320,180),Image.Resampling.BOX),dtype=np.int16))
        if previous[k] is not None:temporal[k].append(float(np.abs(patch-previous[k]).mean()))
        previous[k]=patch
    errors.append(float(np.abs(down[0]-down[1]).mean()))
for stream in maps:stream.close()
for file in files:file.close()
result={'frames_compared':262,'fps':30,'native_dimensions':[1280,720],'reference_revision':'R20_lane_11_internal','working_revision':'R20_lane_12_internal',
    'source_avi_sha256':[before['raw_avi_sha256'],after['raw_avi_sha256']],'method':'Matched uncut motion at the same fixed camera and greeting frame. MJPEG decoded; intensity error is on a 320x180 box-filtered full frame. Temporal luma variation uses a static crop at original scale.',
    'bench_edge_crop_xyxy':field,'full_frame_mean_abs_0_255':float(np.mean(errors)),'largest_single_frame_mean_abs_0_255':max(errors),
    'bench_mean_abs_between_consecutive_frames_0_255':{'full_size':float(np.mean(temporal[0])),'half_size':float(np.mean(temporal[1]))}}
(V/'current/resident_motion/lighting_motion_review.json').write_text(json.dumps(result,indent=2))
print(result['full_frame_mean_abs_0_255'],result['bench_mean_abs_between_consecutive_frames_0_255'])
