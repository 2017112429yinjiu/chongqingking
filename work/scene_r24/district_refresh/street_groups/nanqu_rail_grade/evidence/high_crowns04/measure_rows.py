"""Read foliage silhouettes from the registered, unmodified image rows."""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROWS = (16, 30, 55, 75, 100, 130, 155, 180, 195)
SET = (("2922191", 370), ("2924863", 270), ("2926254", 190))


def read(path, limit):
    image = np.asarray(Image.open(path).convert("RGB"))[:, :limit].astype("int16")
    red, green, blue = image.transpose((2, 0, 1))
    foliage = (green > red + 3) & (green > blue + 6) & (green < 159)
    result = {}
    for y in ROWS:
        stable_hits = np.where(foliage[y - 1:y + 2].sum(axis=0) >= 2)[0]
        result[str(y)] = int(stable_hits[-1]) if stable_hits.size else None
    return result


def collect(field, parent, candidate):
    result = []
    for short, limit in SET:
        result.append({
            "pano": short+"AU",
            "maximum_x_exclusive": limit,
            "field_x": read(next(field.glob("*" + short + "AU.jpg")), limit),
            "stage_x": read(parent / f"pano-{short}AU-regraded-eye.png", limit),
            "candidate_x": read(candidate / f"pano-{short}AU-regraded-eye.png", limit),
        })
    return result


if __name__ == "__main__":
    field, parent, candidate, output = map(Path, sys.argv[1:])
    measured = collect(field, parent, candidate)
    output.write_text(json.dumps(measured, indent=2) + "\n")
    for m in measured:
        print(m)
