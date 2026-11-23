"""Plan-view clearance audit. These results are not 3D traversal certification."""
from pathlib import Path
import json,sys,math
root=Path(__file__).resolve().parent/'project/chongqing_blender_v05'
sys.path.insert(0,str(root))
import district_layout as dl
arch=json.loads((root/'architecture_manifest.json').read_text(encoding='utf-8'))

def violates(p,clearance,rec):
    poly=rec['points']
    if p[0]<min(v[0] for v in poly)-clearance or p[0]>max(v[0] for v in poly)+clearance or p[1]<min(v[1] for v in poly)-clearance or p[1]>max(v[1] for v in poly)+clearance:return False
    return dl.point_in_poly(p,poly) or min(dl.distance_segment(p,a,b)[0] for a,b in zip(poly,poly[1:]+poly[:1]))<clearance

def audit(name,points,width):
    contacts={}
    for a,b in zip(points,points[1:]):
        count=max(1,math.ceil(math.dist(a,b)/.2))
        for i in range(count+1):
            p=tuple(a[k]+(b[k]-a[k])*i/count for k in [0,1])
            for r in arch['buildings']:
                if violates(p,width/2+.10,r):contacts.setdefault(str(r['id']),[]).append(p)
    return {'name':name,'width_m':width,'points':points,'contacts':{key:{'sample_count':len(pts),'first':pts[0],'last':pts[-1]} for key,pts in contacts.items()}}

records=[audit(n,pts,w) for n,pts,w in dl.SUPPLEMENTAL if n!='Main hillside lane']
records.extend([audit('Central_stair_lane',dl.SPINE[:6],3.8),audit('Narrow_upper_passage',dl.SPINE[5:9],1.65),audit('Upper_terrace_connection',dl.SPINE[8:],2.5)])
proposal=[(-93.,-45.),(-74.,-34.),(-73.,-8.),(-76.,17.),(-69.,23.5),(-68.7,28.9),(-69.,34.2),(-74.,40.),(-77.,61.),(-76.,77.5)]
records.append(audit('PROPOSED west detour',proposal,2.7))
records.append(audit('PROPOSED east detour',[(52.,-61.7),(48.,-49.),(52.,-35.),(49.,-19.),(51.,-11.),(42.,4.8),(35.,5.),(28.,14.)],2.5))
records.append(audit('PROPOSED lower spine',[(16.,-66.),(6.,-59.5),(-20.,-52.),(-20.,-30.),(-18.,-8.),(-18.,14.)],3.8))
records.append(audit('PROPOSED narrow corridor',[(-40.,38.),(-37.4,43.),(-33.3,50.),(-28.7,57.),(-29.,60.)],1.35))
records.append(audit('PROPOSED upper connector',[(-29.,60.),(-25.,64.),(-17.,77.),(-27.,90.)],2.5))
out=Path(__file__).resolve().parent/'audit/circulation_plan.json'
out.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False),flush=True)
