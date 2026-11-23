from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_neighborhood import *
allwalls=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('COL_B_','Roof_','R22_Roof','RoofDeck'))])
layout=json.loads((root/'geometry_report.json').read_text());res=[]
for wire in layout['wires']:
 gp=lambda p:Vector((p[0],-p[2],p[1]))
 a,b=map(gp,wire['ends'][0]);stations=[]
 for i in range(1,20):
  t=i/20;pt=a.lerp(b,t);pt.z-=4*t*(1-t)*.58
  hits=allwalls.down(pt.x,pt.y,pt.z+50,50.2)
  stations.append([t,[[round(k[0]-pt.z,2),k[1]] for k in hits if k[0]>pt.z+.1]])
 res.append([wire['name'],stations])
(root/'span_exposure.json').write_text(json.dumps(res,indent=2))
print('N13_OVERHEAD',[(name,sum(bool(v[1]) for v in stations)) for name,stations in res])
