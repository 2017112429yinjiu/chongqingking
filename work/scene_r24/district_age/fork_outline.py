from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import scene
report={}
for label,cx,cy,names in [('cutbank',52,-74,('COL_Road_176034707','COL_R24_JunctionStem'))]:
    blocks={}
    for ob in scene.objects:
        if not ob.name.startswith(names):continue
        faces=[]
        for f in ob.data.polygons:
            if f.normal.z<.05:continue
            vs=[ob.matrix_world@ob.data.vertices[i].co for i in f.vertices]
            if min(p.x for p in vs)>cx+7 or max(p.x for p in vs)<cx-7 or min(p.y for p in vs)>cy+7 or max(p.y for p in vs)<cy-7:continue
            faces.append([[round(a,4) for a in v] for v in vs])
        blocks[ob.name]=faces
    report[label]=blocks
(here/'fork_outline.json').write_text(json.dumps(report),'utf8')
