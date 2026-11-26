"""Run an independent survey in a fresh directory on a desktop or cloud checkout."""
import argparse
import json
import os
from pathlib import Path
import subprocess

here=Path(__file__).resolve().parent
root=here.parents[2]
game=root/"work/project/chongqing_godot_v05"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--user-data",type=Path,help="Fresh user-data root, useful for short Windows shader-cache paths.")
    parser.add_argument("--godot",default="godot")
    parser.add_argument("--blender",default="blender")
    parser.add_argument("--capture",action="store_true",help="Capture the continuous player camera and fixed views with a graphics display.")
    args=parser.parse_args()
    output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy()
    user=args.user_data.resolve() if args.user_data else output/"user"
    user.mkdir(parents=True,exist_ok=False)
    env.update(APPDATA=str(user),XDG_DATA_HOME=str(user))
    def run(name,argv,extra=None):
        folder=output/name
        folder.mkdir()
        with (folder/"console.log").open("wb") as log:
            subprocess.run(argv,cwd=root,env=dict(env,CQ_QA_DIR=str(folder),**(extra or {})),
                           stdout=log,stderr=subprocess.STDOUT,check=True)
        if argv[0]==args.godot:
            errors=[line for line in (folder/"console.log").read_text(encoding="utf-8",errors="replace").splitlines()
                    if line.startswith(("ERROR:","SCRIPT ERROR:","SHADER ERROR:"))]
            if errors:
                raise RuntimeError(f"{folder}: {errors[0]}")
        return folder
    for executable,expected in ((args.blender,"Blender 4.3.2"),(args.godot,"4.6.3")):
        version=subprocess.check_output([executable,"--version"],text=True,encoding="utf-8",errors="replace")
        if not version.startswith(expected):
            raise RuntimeError(f"Expected {expected}, found {version.splitlines()[0]}")
    run("source",[args.blender,"-b",str(here/"delivery_courts.blend"),"--python-exit-code","8","-P",str(here/"audit.py")])
    run("subgrade",[args.blender,"-b",str(here.parent/"district_500/outer_district.blend"),"--python-exit-code","8","-P",str(here/"library_books/subgrade.py")])
    run("import",[args.godot,"--headless","--editor","--import","--path",str(game)])
    common=["--fixed-fps","60","--path",str(game)]
    flags=["--","--explore-500","--shancheng","--day-one-test","--qa-still-frames"]
    results={}
    for script,filename in ((here/"walk.gd","walk.json"),(here.parent/"street_blocks/handoff.gd","handoff.json"),
                             (here.parent/"street_blocks/walk_mapped.gd","walk.json"),(here/"delivery_take.gd","delivery_take.json"),
                             (here/"story_room/story_walk.gd","story_walk.json")):
        graphics=args.capture and script.stem in ("delivery_take","story_walk")
        mode=["--resolution","1152x648","--disable-vsync"] if graphics else ["--headless"]
        folder=run(script.stem,[args.godot,*mode,*common,"--script",str(script),*flags])
        data=json.loads((folder/filename).read_bytes())
        checks=data["checks"] if isinstance(data,dict) else data
        if not checks or not all(check["pass"] for check in checks):
            raise RuntimeError(f"Incomplete survey: {folder}")
        if graphics and (data["images"] < 2 or len(list(folder.glob("walk_*.jpg")))!=data["images"]):
            raise RuntimeError(f"Missing frames in {folder}")
        if graphics and script.stem=="story_walk":
            for view in ("look_back","exhibit_corner","window_collection","glass_case","fare_box","reverse_cabinets"):
                if not (folder/f"{view}.png").is_file():
                    raise RuntimeError(f"Missing story room view {view}")
        results[script.stem]=len(checks)
    mode=["--resolution","1152x648","--disable-vsync"] if args.capture else ["--headless"]
    books=run("library_books",[args.godot,*mode,*common,"--script",str(here/"library_books/views.gd"),*flags])
    inspected=json.loads((books/"materials.json").read_bytes())["checks"]
    if not inspected or not all(row["pass"] for row in inspected):
        raise RuntimeError(f"Missing printed bindings in {books}")
    ground=json.loads((books/"ground.json").read_bytes())
    if ground["missing"] or ground["unexpected"]:
        raise RuntimeError(f"Unowned or obstructed floor in {books}")
    rear=json.loads((books/"rear_steps.json").read_bytes())
    if not rear["pass"]:
        raise RuntimeError(f"Obstructed rear treads in {books}")
    results["library_books"]=len(ground["checks"])+1
    if args.capture:
        for view in ("player_shelf","spines","opposing_case","far_case","table","page_edges","entry","east","west","rear","rear_threshold","reading_aisle"):
            if not (books/f"{view}.png").is_file():
                raise RuntimeError(f"Missing book view {view}")
        views=run("views",[args.godot,"--resolution","1152x648",*common,"--script",str(here/"views.gd"),*flags])
        for name in ("from_pickup","lane_front","school_entry","school_door_detail","school_seating","long_hall","reading_room","upper_court"):
            if not (views/f"{name}.png").is_file():
                raise RuntimeError(f"Missing {name} in {views}")
    print(json.dumps(results))

if __name__=="__main__":
    main()
