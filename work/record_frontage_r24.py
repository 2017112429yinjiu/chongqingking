"""Cross-check installed R24 build 09, its reopened source, and its in-engine evidence."""
import hashlib
import json
from pathlib import Path

WORK = Path(__file__).resolve().parent
SCENE = WORK / "scene_r24"
PROJECT = WORK / "project/chongqing_godot_v05"
EVIDENCE = PROJECT / "verification_r24"
BASELINE = EVIDENCE / "traffic08_full"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def hashes(root, paths):
    return {path.relative_to(root).as_posix(): sha(path) for path in paths}


def main():
    run = EVIDENCE / "build09"
    revision = "R24_market_terrace_09_internal"
    installed = read(SCENE / "active_install.json")
    for name, record in installed.items():
        assert sha(PROJECT / name) == record["installed"] == sha(SCENE / "playtest" / name), name
    export = SCENE / "assets/frontage.glb"
    assert sha(export) == sha(PROJECT / "assets/frontage_r24/frontage.glb")
    reopened = read(SCENE / "source_reopened.json")
    assert reopened["sha256"] == sha(SCENE / reopened["file"])
    tests = {}
    names = ["walk", "corner_walk", "corner_walk_visual", "traffic", "traffic_cameras",
             "block_test", "smoke", "survey", "delivery_end_to_end", "native_1080"]
    current_hashes = {}
    for name in names:
        report_path = run / (name + ".json")
        report = read(report_path)
        assert report["art_profile"]["revision"] == revision, name
        for address, digest in report["runtime_sha256"].items():
            if address not in current_hashes:
                current_hashes[address] = sha(PROJECT / address.removeprefix("res://"))
            assert current_hashes[address] == digest, (name, address)
        tests[name] = report
    assert tests["walk"]["success"] and len(tests["walk"]["waypoints"]) == 15
    for name in ["corner_walk", "corner_walk_visual"]:
        assert tests[name]["passed"] and not tests[name]["blockers"]
        assert len(tests[name]["checkpoints"]) == 24
    for name in ["block_test", "smoke", "survey", "delivery_end_to_end"]:
        assert tests[name]["passed"], name
    assert tests["delivery_end_to_end"]["teleports_between_stages"] == 0
    road = tests["traffic"]
    assert road["passed"] and road["checked"] == 2128 and len(road["parked_wheels"]) == 12
    assert all(track["missing"] == track["covered_over_10cm"] == 0 for track in road["tracks"])
    catches = read(run / "captures/capture_manifest.json")
    assert not catches["failures"] and len(catches["captures"]) == 10
    for shot in catches["captures"]:
        assert shot["exact_requested_size"] and (PROJECT / shot["path"].removeprefix("res://")).is_file()
    defects = read(run / "defect_views/capture_manifest.json")
    assert not defects["failures"] and len(defects["captures"]) == 7
    for pose in tests["traffic_cameras"]["poses"]:
        assert (run / (pose["view"] + ".png")).is_file()
    native = tests["native_1080"]
    comparison_source = BASELINE
    old = read(comparison_source / "native_1080.json")
    assert native["framebuffer"] == old["framebuffer"] == [1920, 1080] and native["gpu"] == old["gpu"]
    perf = []
    for a, b in zip(old["views"], native["views"], strict=True):
        for key in ("view", "position", "fov", "samples"):
            assert a[key] == b[key], key
        assert b["samples"] == 240
        perf.append({"view": b["view"], "before_gpu_p50_ms": a["gpu_p50_ms"],
                     "after_gpu_p50_ms": b["gpu_p50_ms"], "after_gpu_p95_ms": b["gpu_p95_ms"]})
    art = read(SCENE / "assets/road_sources.json")
    for item in art["materials"]:
        assert sha(PROJECT / item["local_input"]) == item["sha256"], item["name"]
    assert sha(PROJECT / art["layout"]["derived"]) == art["layout"]["derived_sha256"]
    assert sha(PROJECT / art["layout"]["original_layout"]) == art["layout"]["layout_sha256"]
    report_files = [run / (name + ".json") for name in names] + [run / "captures/capture_manifest.json", run / "defect_views/capture_manifest.json"]
    image_files = sorted(p for p in run.rglob("*") if p.suffix.lower() in (".jpg", ".png"))
    record = {
        "scope": revision + ". Nanqu Road / Zhongxing Road and named defect sites.",
        "project": hashes(PROJECT, [PROJECT / "project.godot", PROJECT / "main.tscn",
                                     PROJECT / "scripts/main.gd", PROJECT / "assets/render_profile_r24.json"]),
        "source_sha256": hashes(WORK, [SCENE / reopened["file"], export, SCENE / "source_reopened.json",
                                     SCENE / "assets/road_sources.json", SCENE / "geometry.json",
                                     SCENE / "active_install.json", SCENE / "traffic_fit.json"]),
        "inputs_checked_in_daily_project": current_hashes, "installation_entries_checked": len(installed),
        "geometry": {"blender": reopened["version"], "stair_contacts": len(reopened["tread_hits"]),
                     "bridge_sections": len(reopened["bridge_cross_sections"]), "ramp_max_grade": reopened["east_ramp_max_grade"]},
        "ground_contact": {"full_route_wheel_samples": road["checked"],
                           "full_route_peak_m": max(t["max_gap_m"] for t in road["tracks"]),
                           "live_frames": road["live"]["physics_frames"],
                           "live_wheels": sum(c[1] for c in road["live"]["cars"]),
                           "live_peak_m": max(c[3] for c in road["live"]["cars"]),
                           "parked_wheel_peak_m": max(abs(w[1]) for w in road["parked_wheels"])},
        "walk_m": {name: tests[name]["metres"] for name in ["walk", "corner_walk", "corner_walk_visual"]},
        "checks_passed": {name: len(tests[name]["tests"]) for name in ["block_test", "smoke", "survey", "delivery_end_to_end"]},
        "reports_sha256": hashes(run, report_files), "images_sha256": hashes(run, image_files),
        "native_1080": {"gpu": native["gpu"], "warmup_per_view": 90, "frames_per_view": 240, "views": perf},
        "baseline_comparison": comparison_source.relative_to(PROJECT).as_posix(),
        "visual_limits": ["Sparse foot traffic on the long approach", "Plain vehicle glazing and wheel arches",
                          "Untested interiors and frontage outside these walks", "Street-level image quality remains under review"]
    }
    (run / "session_record.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("R24 build09", len(installed), "installed inputs,", len(report_files), "reports,", len(image_files), "images checked")


if __name__ == "__main__":
    main()
