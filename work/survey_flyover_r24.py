from pathlib import Path
from mathutils import Vector
import bpy,json
out={}
for o in bpy.context.scene.objects:
    if o.type=='MESH' and ('59146775' in o.name or 'Nanqu' in o.name):
        pts=[o.matrix_world@v.co for v in o.data.vertices]
        out[o.name]={'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'count':len(pts),'start':[list(p) for p in pts[:4]],'end':[list(p) for p in pts[-4:]]}
(Path(__file__).resolve().parent/'scene_r24/flyover_survey.json').write_text(json.dumps(out,indent=1))

