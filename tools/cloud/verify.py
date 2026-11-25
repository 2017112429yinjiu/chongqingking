"""Fully hydrate the checkout, verify bytes, import the game and reopen the editable city."""
import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("CQ_PROJECT_ROOT", Path(__file__).resolve().parents[2])).resolve()
GAME = ROOT / "work/project/chongqing_godot_v05"
SOURCE = ROOT / "work/scene_r24/district_patrol/city_and_patrol.blend"
BASELINE = "ce1841b079b78c1f876bfa0da3b8b6a404ac9532"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, encoding="utf-8").strip()


def verify_lfs():
    git("lfs", "pull", "--include=", "--exclude=", "origin")
    git("lfs", "fsck", "--objects", "--pointers", "HEAD")
    files = json.loads(git("lfs", "ls-files", "--json", "HEAD"))["files"]
    if not files:
        raise RuntimeError("Expected versioned LFS assets")
    for entry in files:
        path = ROOT / entry["name"]
        if path.stat().st_size != entry["size"]:
            raise ValueError(f"LFS size mismatch: {path}")
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(2**20), b""):
                sha.update(chunk)
        if sha.hexdigest() != entry["oid"]:
            raise ValueError(f"LFS SHA-256 mismatch: {path}")
    unique = {e["oid"]: e["size"] for e in files}
    return {"files": len(files), "unique_objects": len(unique), "unique_bytes": sum(unique.values()),
            "working_tree_bytes": sum(e["size"] for e in files)}


def execute(command, log, *, check_godot=False):
    with log.open("wb") as output:
        result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
    data = log.read_text(encoding="utf-8", errors="replace")
    # Godot may exit zero after reporting a resource, script, or shader error.
    errors = re.findall(r"(?m)^\s*(?:(?:SCRIPT|SHADER) )?ERROR:.*$", data) if check_godot else []
    if result.returncode or errors:
        raise RuntimeError(f"{log.name}: exit {result.returncode}\n" + "\n".join(errors[:12]) + "\n" + data[-1200:])
    return data


def ready_state(log):
    ready = re.search(r"^CQ_READY (.+)$", log, re.MULTILINE)
    if not ready or "PENG_TEACH AT_BIKE" not in log:
        raise ValueError("The default scene did not reach the district and first-shift ready markers")
    state = json.loads(ready[1])
    if not state["collisions"]["bodies"] or state["collisions"]["failed"]:
        raise ValueError("District collision setup failed")
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default="godot")
    parser.add_argument("--blender", default="blender")
    args = parser.parse_args()
    git("merge-base", "--is-ancestor", BASELINE, "HEAD")
    head = git("rev-parse", "HEAD")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run = ROOT / ".cloud-dev/runs" / f"{stamp}-{head[:8]}"
    run.mkdir(parents=True)
    print("Verification output:", run, flush=True)
    version = subprocess.check_output([args.godot, "--version"], encoding="utf-8").strip()
    if not version.startswith("4.6.3.stable."):
        raise ValueError(f"Expected Godot 4.6.3 stable, got {version}")
    report = {"revision": head, "baseline": BASELINE, "godot": version, "lfs": verify_lfs()}
    print("Verified materialized LFS files:", report["lfs"], flush=True)
    (run / "lfs.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    execute([args.blender, "-b", "--factory-startup", "--disable-autoexec", str(SOURCE),
             "--python-exit-code", "1", "--python", str(Path(__file__).with_name("blender_scene.py")),
             "--", str(run)], run / "blender.log")
    report["blender"] = json.loads((run / "blender.json").read_text(encoding="utf-8"))
    print("Reopened editable scene:", report["blender"]["objects"], "objects", flush=True)
    engine = [args.godot, "--headless", "--path", str(GAME)]
    report["fresh_import"] = not (GAME / ".godot/imported").exists()
    execute([*engine, "--editor", "--import", "--log-file", str(run / "import-engine.log")],
            run / "import.log", check_godot=True)
    metadata = (GAME / "assets/district_patrol/district.glb.import").read_text(encoding="utf-8")
    imported = re.search(r'^path="res://([^"]+)"', metadata, re.MULTILINE)
    if not imported or not (GAME / imported[1]).is_file():
        raise RuntimeError("Imported district PackedScene is missing")
    config = (GAME / "project.godot").read_text(encoding="utf-8")
    if 'run/main_scene="res://first_shift.tscn"' not in config:
        raise ValueError("Unexpected default entry")
    startup = execute([*engine, "--log-file", str(run / "startup-engine.log"), "--fixed-fps", "60",
                       "--quit-after", "120", "--", "--day-one-test"], run / "startup.log", check_godot=True)
    report["ready"] = ready_state(startup)
    report["entry"] = "res://first_shift.tscn"
    report["imported_district_bytes"] = (GAME / imported[1]).stat().st_size
    report["startup_iterations_requested"] = 120
    (run / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Verified:", run / "verification.json", flush=True)


if __name__ == "__main__":
    main()
