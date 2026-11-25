"""Compare two native collision surveys on the same grid. All coordinates are metres."""
import argparse
import json
from collections import Counter
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def inside(x, y, vertices):
    hit = False
    for (a, b), (c, d) in zip(vertices, vertices[1:] + vertices[:1]):
        if (b > y) != (d > y) and x < a + (y - b) * (c - a) / (d - b):
            hit = not hit
    return hit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    source = "work/project/chongqing_godot_v05/source_data/river_r22/river_plan.json"
    rings = read(root / source)["rings"]
    old = {(x, z): hits for x, z, hits in read(args.before / "grid_500.json")["samples"]}
    new = {(x, z): hits for x, z, hits in read(args.after / "grid_500.json")["samples"]}
    if set(old) != set(new) or len(new) != 2601:
        raise ValueError("Both native surveys must contain the same 51 by 51 points")
    counts = {}
    core_changes = []
    misses = []
    for (x, z), hits in new.items():
        extent = max(abs(x), abs(z))
        if extent <= 100:
            zone = "core"
        else:
            # OSM river plan stores east and north. Godot +Z points south.
            water = sum(1 if r["role"] == "outer" else -1 for r in rings if inside(x, -z, r["points"])) > 0
            zone = "outer_mapped_water" if water else "outer_land"
        group = counts.setdefault(zone, Counter())
        group["sample_count"] += 1
        previous = old[x, z]
        group["before_hit_any"] += bool(previous)
        group["after_hit_any"] += bool(hits)
        # The old core owns its interior. The shared boundary belongs to both surfaces.
        if extent < 100 and previous != hits:
            core_changes.append([x, z, previous, hits])
        if zone == "outer_land" and not hits:
            misses.append([x, z])
    result = {
        "metric": "Any layer-1 body hit from +130 to -35 m, including roofs. Route trials measure traversability.",
        "river_source": source, "attribution": "© OpenStreetMap contributors, ODbL 1.0",
        "counts": counts, "outer_land_misses_xz": misses,
        "changed_interior_core_samples": core_changes,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
