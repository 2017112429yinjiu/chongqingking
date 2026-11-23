from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import scene
report={}
for label,cx,cy,names in [('north',66.85,74.5,('COL_Road_734116597','COL_Road_734116595')),('south',-49,-94.1,('COL_Road_1189963598','COL_Road_1324001442')),('stone',16.19,-76.1,('COL_D18_NanquShoulder','COL_Walk_OSM_734116594'))]:
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
(here/'junction_faces.json').write_text(json.dumps(report),'utf8')
