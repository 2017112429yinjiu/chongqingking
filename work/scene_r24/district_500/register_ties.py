"""Turn native 25b probe readings into measured road-edge sections."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("sections",type=Path)
args=parser.parse_args()
sections=json.loads(args.sections.read_text())["sections"]
ties=[]
for name,rows in sections.items():
    center=next(r for r in rows if r[0]==0 and r[1]==-.04)
    if name.startswith("west"):
        side="west"
    elif name.startswith("east") or name=="southeast":
        side="east"
    else:
        side=name
    edge=[r for r in rows if r[1]==-.04 and r[4] is not None]
    cross=sorted([(-r[3] if side in ("east","west") else r[2],
                   round(r[4],4),r[5]) for r in edge])
    near=next(r for r in rows if r[0]==0 and r[1]==-1.)
    ties.append({"name":name,"side":side,"center":round(-center[3] if side in ("east","west") else center[2],4),
                 "height":round(center[4],4),"grade_out":round((center[4]-near[4])/.96,4),
                 "profile":cross})
Path(__file__).with_name("road_ties.json").write_text(json.dumps(ties,ensure_ascii=False,indent=2)+"\n")
