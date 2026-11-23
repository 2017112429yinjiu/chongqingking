import bpy,json
from pathlib import Path
W=Path(__file__).resolve().parent
ob=bpy.data.objects['District_surface_repairs_and_utilities_offwhite']
vs=[ob.matrix_world@v.co for v in ob.data.vertices]
records=[]
for k in range(0,len(vs),8):
    pts=vs[k:k+8]
    if abs((pts[1]-pts[0]).length-.46)>.002 or abs((pts[4]-pts[0]).length-.64)>.002:continue
    def engine(p):return [p.x,p.z,-p.y]
    records.append({'center':engine(sum(pts[1:],pts[0].copy())/8),'right':engine((pts[1]-pts[0]).normalized()),'front':engine((pts[3]-pts[0]).normalized())})
(W/'audit/r20_meter_sites.json').write_text(json.dumps(records),encoding='utf-8')
print('METER_SITES',len(records))
