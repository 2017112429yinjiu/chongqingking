"""Follow each band of the western reservation in the reopened source."""
import sys,json
from pathlib import Path
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import scene,Surfaces
plan=json.loads((here.parents[1]/'project/chongqing_godot_v05/assets/district_age/layout.json').read_text('utf8'))['road']['western_median']
obs=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_R24_Median_R24_median_')]
bank=Surfaces(obs);out=[]
for ob in obs:
    for f in ob.data.polygons:
        if f.normal.z<.2:continue
        p=ob.matrix_world@f.center
        if not plan['from_x']+.05<p.x<plan['to_x']-.05:continue
        hits=bank.down(p.x,p.y,18.,17.)
        if hits:out.append([p.x,-p.y,hits[0][0]])
# At every longitudinal station straddle the median-to-asphalt boundary, including the
# triangle tips that did not reach the centre of any existing median face.
rows={}
for ob in obs:
    for f in ob.data.polygons:
        if abs(f.normal.z)<.04:continue
        for i in f.vertices:
            p=ob.matrix_world@ob.data.vertices[i].co
            if plan['from_x']-.0002<=p.x<=plan['to_x']+.0002:rows.setdefault(round(p.x,4),[]).append(p.y)
paved=Surfaces([o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Road_') and o.name.endswith('_asphalt') and not o.hide_render])
xx=sorted(rows);uncovered=[]
for a,b in zip(xx,xx[1:]):
    x=(a+b)*.5
    low=(min(rows[a])+min(rows[b]))*.5;high=(max(rows[a])+max(rows[b]))*.5
    for offset in [-1.16,-.9,-.66,-.42,-.21,-.11,-.04,.015,.055,.10,.18,.28,.42,.62,.82,1.]:
        y=low+offset if offset<0 else low+(high-low)*offset
        hits=bank.down(x,y,25.,24.)+paved.down(x,y,25.,24.)
        if hits:out.append([x,-y,max(h[0] for h in hits)])
        else:uncovered.append([x,-y])
(here/'median_sections.json').write_text(json.dumps(out),'utf8')
(here/'median_open_pixels.json').write_text(json.dumps(uncovered),'utf8')
print('MEDIAN_CENTRES',len(out),'uncovered source positions',len(uncovered),flush=True)
