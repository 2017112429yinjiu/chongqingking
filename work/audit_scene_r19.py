import bpy, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
report={'objects':[], 'materials':[]}
for o in bpy.context.scene.objects:
    if o.type!='MESH': continue
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    lo=[min(p[k] for p in pts) for k in range(3)]
    hi=[max(p[k] for p in pts) for k in range(3)]
    if hi[0]<-40 or lo[0]>-17 or hi[1]<-66 or lo[1]>-53 or hi[2]<9 or lo[2]>23: continue
    report['objects'].append({'name':o.name,'bounds':[lo,hi],'location':list(o.location),'materials':[m.name for m in o.data.materials if m], 'vertices':len(o.data.vertices)})
for m in bpy.data.materials:
    report['materials'].append({'name':m.name,'meters':m.get('uv_meters'),'color':list(m.diffuse_color),'images':[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.node_tree else []})
(ROOT/'audit/r19_source_inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('R19_AUDIT',len(report['objects']),len(report['materials']))
