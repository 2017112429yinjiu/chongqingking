"""Assemble unretouched Godot frames at their recorded simulation intervals."""
from pathlib import Path
import json
import sys
from PIL import Image

def assemble(folder, name):
    frames = sorted(folder.glob("reel_" + name + "_*.png"))
    if len(frames) < 2:
        raise ValueError(name)
    ticks = [int(p.stem.rsplit("_", 1)[1]) for p in frames]
    times = [round((n - ticks[0]) * 1000 / 60) for n in ticks]
    durations = [b - a for a, b in zip(times, times[1:])]
    durations.append(durations[-1])
    pictures = []
    for frame in frames:
        with Image.open(frame) as source:
            pictures.append(source.convert("RGB"))
    output = folder / (name + ".webp")
    pictures[0].save(output, save_all=True, append_images=pictures[1:], duration=durations,
                     loop=0, quality=89, method=3)
    with Image.open(output) as result:
        actual_duration = 0
        for i in range(result.n_frames):
            result.seek(i)
            result.load()
            actual_duration += result.info.get("duration", 0)
        if abs(actual_duration - sum(durations)) > 5:
            raise RuntimeError((output, actual_duration, sum(durations)))
        return {"file":output.name, "source_pngs":len(frames), "encoded_frames":result.n_frames,
                "first_physics_tick":ticks[0], "last_physics_tick":ticks[-1], "duration_ms":actual_duration}

if __name__ == "__main__":
    folder = Path(sys.argv[1]).resolve()
    checks = [assemble(folder, action) for action in sys.argv[2:]]
    (folder / "review_clips.json").write_text(json.dumps(checks, indent=2), encoding="utf8")
