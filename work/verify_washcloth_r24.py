"""Measure the exported cloth silhouette at three observed wind phases, and compare game shots."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

WORK = Path(__file__).resolve().parent
ACTIVE = WORK / "project/chongqing_godot_v05"
REFERENCE = ACTIVE / "verification_r24/cloth09_reference"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    folder = parser.parse_args().folder
    report = json.loads((folder / "cotton.json").read_text(encoding="utf8"))
    assert report["passed"] and report["modern"] and len(report["meshes"]) == 15
    masks = []
    for value in (0, 16, 32):
        with Image.open(folder / f"silhouette_{value}.png") as image:
            assert image.mode == "RGBA"
            masks.append(np.asarray(image)[:, :, 3] >= 128)
    y, x = np.nonzero(masks[0])
    height = y.max() - y.min() + 1
    assert height > 300 and np.ptp(x) > 100
    counts = {}
    for name, start, end in [("peg_edge", 0., .055), ("lower_quarter", .72, .99)]:
        section = slice(y.min() + int(start * height), y.min() + int(end * height))
        counts[name] = [int(np.count_nonzero(mask[section] ^ masks[0][section])) for mask in masks[1:]]
    assert max(counts["peg_edge"]) <= 2 and min(counts["lower_quarter"]) > 250, counts
    assert json.loads((REFERENCE / "cotton.json").read_text(encoding="utf8"))["modern"] is False
    size = (660, 371)
    canvas = Image.new("RGB", (1344, 832), "#212421")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
    for column, (root, label) in enumerate([(REFERENCE, "原布面"), (folder, "毛圈布")]):
        for row, (file, view) in enumerate([("line.png", "步行距离"), ("fibres.png", "近看夹口与下摆")]):
            x0, y0 = 8 + column * 670, 8 + row * 411
            draw.text((x0, y0), label + " · " + view, font=font, fill="#edece2")
            with Image.open(root / file) as image:
                canvas.paste(image.convert("RGB").resize(size, Image.Resampling.LANCZOS), (x0, y0 + 33))
    canvas.save(folder / "球场毛巾同机位对照.jpg", quality=94)
    files = ["line.png", "fibres.png", "silhouette_0.png", "silhouette_16.png", "silhouette_32.png", "cotton.json"]
    evidence = {"alpha_threshold": 128, "phase_s": [0, 1.6, 3.2], "render_target_px": [640, 640],
                "tested_mesh": report["nearest"], "mesh_pin_and_hem_rows_inspected": len(report["meshes"]),
                "changed_silhouette_pixels_vs_phase_0": counts, "current_images": {f: digest(folder / f) for f in files},
                "previous_comparison_images": {f: digest(REFERENCE / f) for f in ["line.png", "fibres.png"]}}
    (folder / "cloth_mask_check.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf8")
    print("Cloth silhouette", counts, "UV orientation checked on", len(report["meshes"]), "meshes")


if __name__ == "__main__":
    main()
