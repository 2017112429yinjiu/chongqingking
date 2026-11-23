"""Bind the daily build 10 results to the reviewed shader, scan and unchanged Blender sources."""
import hashlib
import json
from pathlib import Path

WORK = Path(__file__).resolve().parent
SCENE = WORK / "scene_r24"
PROJECT = WORK / "project/chongqing_godot_v05"
RUN = PROJECT / "verification_r24/build10"
PREVIOUS = RUN.parent / "build09/session_record.json"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    installed = read(SCENE / "active_install.json")
    for name, row in installed.items():
        assert sha(PROJECT / name) == row["installed"] == sha(SCENE / "playtest" / name), name
    past = read(PREVIOUS)
    for rel, value in past["source_sha256"].items():
        if rel.endswith((".blend", ".glb", "source_reopened.json", "geometry.json")):
            assert sha(WORK / rel) == value, rel
    files = ["walk", "corner_walk", "traffic", "block_test", "delivery_end_to_end", "smoke", "survey", "cotton"]
    current_hashes = {}
    summaries = {}
    profile = sha(PROJECT / "assets/render_profile_r24.json")
    for name in files:
        d = read(RUN / (name + ".json"))
        assert d["art_profile"]["sha256"] == profile and d["art_profile"]["revision"] == "R24_market_terrace_10_internal"
        assert d.get("success", d.get("passed")), name
        for address, value in d["runtime_sha256"].items():
            if address not in current_hashes:
                current_hashes[address] = sha(PROJECT / address.removeprefix("res://"))
            assert current_hashes[address] == value, (name, address)
        if "metres" in d:
            summaries[name] = {"metres": d["metres"], "checkpoints": len(d.get("waypoints", d.get("checkpoints", [])))}
        elif "tests" in d:
            summaries[name] = {"passed": len(d["tests"])}
        elif name == "traffic":
            summaries[name] = {"route_wheels": d["checked"], "parked_wheels": len(d["parked_wheels"]),
                               "live_frames": d["live"]["physics_frames"],
                               "live_peak_m": max(car[3] for car in d["live"]["cars"])}
    mask = read(RUN / "cloth_mask_check.json")
    assert max(mask["changed_silhouette_pixels_vs_phase_0"]["peg_edge"]) == 0
    assert mask["mesh_pin_and_hem_rows_inspected"] == 15
    for filename, digest in mask["current_images"].items():
        assert sha(RUN / filename) == digest, filename
    provenance = read(PROJECT / "assets/frontage_r24/terry_sources.json")
    for row in provenance["maps"].values():
        assert sha(SCENE / "cloth_review/originals" / row["file"]) == row["sha256"]
    assert sha(PROJECT / "assets/frontage_r24/terry_pile.png") == provenance["derived"]["sha256"]
    gpu = read(RUN / "cloth_gpu.json")
    assert gpu["framebuffer"] == [1920, 1080] and gpu["meshes"] == 5 and gpu["warmup"] == 90
    for d in gpu["passes"]:
        assert d["samples"] == 240 and d["p50_ms"] > 0 and d["p95_ms"] >= d["p50_ms"]
        assert sha(RUN / ("cloth1080_" + d["mode"] + ".png")) == d["image_sha256"]
    evidence = {"revision": "R24_market_terrace_10_internal", "engine": "Godot 4.6.3 Forward+",
                "profile_sha256": profile, "project_sha256": sha(PROJECT / "project.godot"),
                "runtime_dependencies": current_hashes, "checked_installed_inputs": len(installed),
                "previous_geometry_evidence": {"file": PREVIOUS.relative_to(PROJECT).as_posix(), "sha256": sha(PREVIOUS)},
                "reopened_blender_sha256": read(SCENE / "source_reopened.json")["sha256"], "checks": summaries,
                "cloth_motion": mask, "texture": provenance, "isolated_gpu": gpu,
                "performance_scope": "One isolated five-mesh viewport. An editor play session was open. No build 10 whole-district FPS inferred.",
                "remaining": ["Long empty approaches, window occupancy, untreated building entrances and lower shop floors",
                              "Player acceptance in motion; district visual standards remain provisional."],
                "report_sha256": {f.name: sha(f) for f in sorted(RUN.glob("*.json")) if f.name != "session_record.json"},
                "capture_sha256": {f.name: sha(f) for f in sorted(RUN.iterdir()) if f.suffix in [".jpg", ".png"]}}
    (RUN / "session_record.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("R24 build10 verified", len(installed), "installed inputs and", len(files), "engine reports")


if __name__ == "__main__":
    main()
