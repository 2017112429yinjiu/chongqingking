import bpy,json
from pathlib import Path
import sys
here=Path(__file__).resolve().parent
p=here.parents[1]/'project/chongqing_godot_v05/verification_r24/vertical_run'/sys.argv[-1]
source=next(p.glob('*.mp4'))
scene=bpy.context.scene
strip=scene.sequence_editor_create().sequences.new_movie('Reopen native take',str(source),1,1)
expected=json.loads((p/'route.json').read_text('utf8'))['native_frames_15fps']
assert len(strip.elements)>0 and strip.frame_duration==expected
scene.frame_set(expected//2)
report={'file':source.name,'frames':strip.frame_duration,'fps':strip.fps,'width':strip.elements[0].orig_width,'height':strip.elements[0].orig_height}
(p/'movie_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print('NATIVE_TAKE',report)
