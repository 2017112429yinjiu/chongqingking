"""Pack the licensed terry scan as one linear, mipmapped texture for Godot."""
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

SCENE = Path(__file__).resolve().parent / "scene_r24"
ORIGINALS = SCENE / "cloth_review/originals"
DEST = SCENE / "assets"
PLAYTEST = SCENE / "playtest/assets/frontage_r24"


def main():
    record = json.loads((ORIGINALS / "sources.json").read_text(encoding="utf8"))
    maps = {}
    for key, info in record["maps"].items():
        path = ORIGINALS / info["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == info["sha256"]
        with Image.open(path) as im:
            maps[key] = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.
    # Use luminance and occlusion to retain the relative pile density independently of dye.
    luminance = maps["Diffuse"] @ np.array([.2126, .7152, .0722], dtype=np.float32)
    detail = luminance * (.65 + .35 * maps["AO"][:, :, 0])
    lo, hi = np.percentile(detail, [2, 98])
    pile = np.clip((detail - lo) / (hi - lo), 0., 1.)
    packed = np.dstack((maps["nor_gl"][:, :, :2], pile))
    output = DEST / "terry_pile.png"
    Image.fromarray(np.rint(packed * 255).astype(np.uint8)).save(output)
    record["derived"] = {"file": output.name, "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                         "rg": "Tangent-space OpenGL normal XY, linear data.",
                         "b": "Luminance times softened occlusion, normalized using the 2nd and 98th percentiles.",
                         "game_modifications": "Local faded dyes, woven bands, pinned edge and moving hem."}
    (DEST / "terry_sources.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf8")
    for file in [output, DEST / "terry_sources.json"]:
        shutil.copy2(file, PLAYTEST / file.name)


if __name__ == "__main__":
    main()
