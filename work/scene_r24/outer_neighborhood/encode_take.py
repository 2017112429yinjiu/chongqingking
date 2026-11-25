"""Re-encode the unbroken native player take at its recorded physics cadence."""
import json,os
from pathlib import Path
import bpy

folder=Path(os.environ["CQ_QA_DIR"])
report=json.loads((folder/"market_entry.json").read_text(encoding="utf-8-sig"))
frames=sorted(folder.glob("walk_*.jpg"))
assert len(frames)==report["images"] and all(row["pass"] for row in report["checks"])
scene=bpy.context.scene
seq=scene.sequence_editor_create()
track=seq.sequences.new_image("Godot player camera",str(frames[0]),1,1)
for frame in frames[1:]:
    track.elements.append(frame.name)
scene.frame_start=1
scene.frame_end=len(frames)
scene.render.resolution_x=track.elements[0].orig_width
scene.render.resolution_y=track.elements[0].orig_height
scene.render.resolution_percentage=100
scene.render.fps=report["physics_hz"]
scene.render.fps_base=report["ticks_per_image"]
scene.view_settings.view_transform="Standard"
scene.render.image_settings.file_format="FFMPEG"
scene.render.ffmpeg.format="MPEG4"
scene.render.ffmpeg.codec="H264"
scene.render.ffmpeg.constant_rate_factor="HIGH"
scene.render.filepath=os.environ.get("CQ_TAKE_OUTPUT",str(folder.parent/"market_to_201.mp4"))
bpy.ops.render.render(animation=True)
