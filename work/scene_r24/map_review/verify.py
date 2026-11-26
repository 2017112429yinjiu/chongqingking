"""Run the two game entries, floor intersections, registered walks and diagnostic views."""
import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
R24 = HERE.parent
ROOT = R24.parents[1]
GAME = ROOT / "work/project/chongqing_godot_v05"

def street_positions(output, patrol):
    def read(path):
        return json.loads(path.read_bytes())
    points = [pt[:3] for leg in read(output/"outer_roads/routes.json")["routes"]
              if not leg["riding"] for pt in leg["samples"]]
    for path in sorted(patrol.glob("player_out_*/drives.json")):
        for leg in read(path):
            points.extend(pt[:3] for pt in leg["history"][::3])
    for leg in read(output/"approaches/approaches.json"):
        if leg["pass"] and leg["name"].endswith("_out"):
            points.append([float(v) for v in leg["detail"]["end"].strip("()").split(",")])
    file = output/"feet_full.json"
    file.write_text(json.dumps(points), encoding="utf-8")
    return file

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="Fresh run name below .cloud-dev")
    parser.add_argument("--godot", type=Path, default=ROOT/"work/tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe")
    parser.add_argument("--blender", type=Path, default=ROOT/"work/tools/blender-4.3.2-windows-x64/blender.exe")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+",args.run):
        parser.error("Use letters, numbers, underscores or hyphens for the run directory.")
    output = ROOT/".cloud-dev"/args.run
    patrol = GAME/"verification_r24/district_patrol"/args.run
    repair = ROOT/".cloud-dev/plot0"/args.run
    for folder in (output,patrol,repair):
        if folder.exists(): parser.error(f"Choose a fresh run name; found {folder}")
    output.mkdir(parents=True)
    environment=os.environ.copy()
    user_data=ROOT/".cloud-dev"/("m"+uuid.uuid4().hex[:8])
    user_data.mkdir()
    environment["APPDATA"]=str(user_data)
    def execute(cmd, sub, env=None):
        with (sub/"engine.log").open("w",encoding="utf-8") as stream:
            return subprocess.run(cmd,cwd=ROOT,env=env or environment,stdout=stream,stderr=subprocess.STDOUT).returncode
    def powershell(script,*flags):
        subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(script),"-Run",args.run,*flags],check=True,cwd=ROOT)
    powershell(R24/"district_patrol/verify.ps1","-AllRoads","-Timing")
    powershell(R24/"repair_court/verify.ps1","-Capture")
    subprocess.run([sys.executable,R24/"shancheng_courts/verify.py","--output",output/"school",
                    "--godot",args.godot,"--blender",args.blender,"--capture",
                    "--user-data",user_data.with_name(user_data.name+"s")],cwd=ROOT,check=True)
    sub=output/"inner_floors"
    sub.mkdir()
    code=execute([args.blender,"-b",R24/"district_500/city_and_outer.local.blend",
                  "--python-exit-code","8","-P",HERE/"ground.py"],sub,dict(environment,CQ_QA_DIR=str(sub)))
    if code or not (sub/"floors.json").is_file():raise RuntimeError(f"Blender survey failed: {sub}")
    flags=["--","--explore-500","--day-one-test","--qa-still-frames"]
    def game(label,script,result,graphics=False,extra=(),inputs=None,measure=False):
        sub=output/label
        sub.mkdir()
        env=dict(environment,CQ_QA_DIR=str(sub))
        env.update({k:str(v) for k,v in (inputs or {}).items()})
        display=["--resolution","960x540","--disable-vsync"] if graphics else ["--headless"]
        rc=execute([args.godot,*display,"--path",GAME,"--fixed-fps","60","--script",script,*flags,*extra],sub,env)
        path=sub/result
        if not path.is_file():raise RuntimeError(f"Missing {path}, see engine.log")
        data=json.loads(path.read_bytes())
        # Two diagnostic sweeps intentionally record blocked approaches. Preserve all observations.
        expected_failure = measure and isinstance(data,list) and any(not r["pass"] for r in data)
        if rc and not (rc==2 and expected_failure):raise RuntimeError(f"{script.name} exited {rc}: {sub}")
        if "SCRIPT ERROR" in (sub/"engine.log").read_text(encoding="utf-8",errors="replace"):
            raise RuntimeError(f"Script error in {sub}")
    game("play",HERE/"survey.gd","views.json",True)
    game("art_views",HERE/"survey.gd","views.json",True,["--art-entry"])
    game("terrain_views",HERE/"landscape.gd","views.json",True,inputs={"CQ_MAP_FLOORS":sub/"floors.json"})
    game("approaches",HERE/"approaches.gd","approaches.json",measure=True)
    game("width_recheck",HERE/"stair_recheck.gd","stairs.json",inputs={"CQ_MAP_DIRECT":output/"approaches/approaches.json"},measure=True)
    game("pixels",HERE/"pixels.gd","pixels.json",True,inputs={"CQ_MAP_VIEWS":output/"play/views.json"})
    game("outer_roads",R24/"district_500/routes.gd","routes.json")
    game("all_halls",R24/"outer_neighborhood/survey.gd","checks.json",extra=["--all-halls"])
    game("shared",R24/"outer_neighborhood/shared_paths.gd","shared_paths.json")
    game("homes",R24/"outer_neighborhood/survey.gd","checks.json")
    game("front_stairs",R24/"street_blocks/walk_stairs.gd","stairs.json")
    feet=street_positions(output,patrol)
    game("road_views_full",HERE/"street_outlines.gd","views.json",True,
         inputs={"CQ_MAP_FEET":feet,"CQ_MAP_OUTLINES":output/"terrain_views/views.json"})
    print(f"Native evidence in {output}; patrol in {patrol}; repair court in {repair}")

if __name__=="__main__":
    main()
