"""Index the surveyed plot IDs, 100 m cells and registered riverside park."""
from collections import defaultdict
import hashlib
import json
from math import asinh, cos, degrees, floor, radians, sin, sqrt, tan
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
GAME = ROOT / "work/project/chongqing_godot_v05"
SITE = ROOT / "work/scene_r24/street_blocks"
EXTENT = (11862384.4391, 3445935.1103, 11863016.1823, 3446570.0754)
EXPECTED_IMAGE = "54ba3944fea775e513e9c23e304db170c7ab7a48eb9880fdc619dc6a6f790273"


def load(path):
    return json.loads(path.read_bytes())


def inside(point, ring):
    x, y = point
    return sum((a[1] > y) != (b[1] > y)
               and x < a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])
               for a, b in zip(ring, ring[1:] + ring[:1])) % 2 == 1


def cell(x, y):
    return "%d,%d" % (floor((x + 250) / 100), floor((y + 250) / 100))


def intersects_district(points):
    return all(min(p[i] for p in points) <= 250 and max(p[i] for p in points) >= -250 for i in (0, 1))


def outline(plot):
    x, y = plot["east_north"]
    c, s = cos(plot["bearing"]), sin(plot["bearing"])
    w, d = plot["width"] / 2, plot["depth"] / 2
    return [[x + c*u - s*v, y + s*u + c*v] for u, v in [(-w, -d), (w, -d), (w, d), (-w, d)]]


def nearest_way(point, ways):
    def segment_distance_sq(start, end):
        dx, dy = end[0] - start[0], end[1] - start[1]
        span_sq = dx * dx + dy * dy
        x, y = point[0] - start[0], point[1] - start[1]
        t = min(1., max(0., (x * dx + y * dy) / span_sq)) if span_sq else 0.
        return (x - dx * t) ** 2 + (y - dy * t) ** 2

    distance, way = min(
        ((min(segment_distance_sq(a, b) for a, b in zip(w["points"], w["points"][1:])), w)
         for w in ways if len(w["points"]) > 1),
        key=lambda candidate: candidate[0],
    )
    tags = way["tags"]
    return {"osm": way["id"], "name": tags.get("name"), "type": way["type"],
            "centre_distance_m": round(sqrt(distance), 2), "layer": tags.get("layer"),
            "bridge": tags.get("bridge"), "tunnel": tags.get("tunnel"),
            "source": way["source_url"]}


def atlas(image, output, geo, park, plots):
    """Keep the imagery and annotated atlas outside the versioned assets."""
    from PIL import Image, ImageDraw, ImageFont

    with image.open("rb") as stream:
        assert hashlib.file_digest(stream, "sha256").hexdigest() == EXPECTED_IMAGE
    canvas = Image.open(image).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
    radius, eccentricity_sq = 6378137., .00669437999014
    latitude = radians(geo["center_lat"])
    prime = radius / sqrt(1 - eccentricity_sq * sin(latitude)**2)
    meridional = prime * (1 - eccentricity_sq) / (1 - eccentricity_sq * sin(latitude)**2)

    def pixel(point):
        x, y = point
        lon = geo["center_lon"] + degrees(x / (prime * cos(latitude)))
        lat = geo["center_lat"] + degrees(y / meridional)
        e = radius * radians(lon)
        n = radius * asinh(tan(radians(lat)))
        return ((e - EXTENT[0]) / (EXTENT[2] - EXTENT[0]) * canvas.width,
                (EXTENT[3] - n) / (EXTENT[3] - EXTENT[1]) * canvas.height)

    draw.line([pixel(q) for q in park + park[:1]], fill="#64ffc9", width=3)
    for row in plots:
        ring = row["footprint"]
        color = "#ffb25d" if row["inside_park_boundary"] else "#fbfff1"
        draw.line([pixel(q) for q in ring + ring[:1]], fill=color, width=2)
        draw.text(pixel(row["centre"]), str(row["id"]), fill=color, font=font,
                  anchor="mm", stroke_width=2, stroke_fill="#18231e")
    canvas.save(output)


def main():
    geo = load(GAME / "source_data/geo_layout.json")
    registry = load(SITE / "frontage_controls.json")
    park = registry["park"]
    frontages = [f for f in registry["frontages"] if any(intersects_district(r) for r in f["rings"])]
    frontage_records = {}
    for f in frontages:
        osm = f["osm"]
        osm_id = osm.split("@")[0]
        kind = {"w": "way", "r": "relation"}[osm_id[0]]
        frontage_records[osm] = {"gers": f["gers"], "mapped_storeys": f["source_storeys"],
                                  "source": f"https://www.openstreetmap.org/{kind}/{osm_id[1:]}"}
    court = load(SITE.parent / "shancheng_courts/registered.json")
    photos = {ref["id"]: ref["url"] for ref in court["references"]}
    named = {b["id"]: {"ring": b["points"], "reference": photos[b["photo"]]}
             for b in court["buildings"]}
    plots = []
    sectors = defaultdict(list)
    mapped_buildings = geo["buildings"] + geo["context_buildings"]
    for p in sorted(load(GAME / "assets/district_500/layout.json")["plots"], key=lambda p: p["plot_id"]):
        xy = p["east_north"]
        sector = cell(*xy)
        row = {"id": p["plot_id"], "centre": xy, "sector": sector,
               "footprint": outline(p), "inside_park_boundary": inside(xy, park["boundary"]),
               "registered_site": p.get("registered_site"), "building_type_confirmed": False,
               "mapped_buildings_at_centre": sorted({b["id"] for b in mapped_buildings
                                                     if inside(xy, b["points"])}),
               "overture_frontages_at_centre": sorted(f["osm"] for f in frontages
                                                       if any(inside(xy, r) for r in f["rings"])),
               "nearest_mapped_road": nearest_way(xy, geo["roads"]),
               "nearest_mapped_path": nearest_way(xy, geo["paths"])}
        plots.append(row)
        sectors[sector].append(row["id"])
    footprints = defaultdict(list)
    for category in ("buildings", "context_buildings"):
        for building in geo[category]:
            points = building["points"]
            if intersects_district(points):
                footprints[str(building["id"])].append(category)
    result = {"plots": plots, "registered_osm_ids": dict(footprints),
              "overture_frontages": frontage_records, "frontage_attribution": registry["license"],
              "named_courts": named,
              "park": {"osm": park["osm"], "name": park["name"]},
              "sectors": {f"{i},{j}": sectors[f"{i},{j}"] for i in range(5) for j in range(5)}}
    Path(sys.argv[1]).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    if len(sys.argv) == 4:
        atlas(Path(sys.argv[2]), Path(sys.argv[3]), geo, park["boundary"], plots)


if __name__ == "__main__":
    main()
