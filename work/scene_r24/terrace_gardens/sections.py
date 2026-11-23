"""Comparable half-metre grade breaks and forty-millimetre cross-seam contact pairs."""
from pathlib import Path
import sys,json,math,bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_data import scene,Surfaces,here,save
from mathutils import Vector
report=json.loads((here/'grade.json').read_text())
poly=[Vector(p) for p in report['outline']]
edges=[(a,b,(b-a).normalized()) for a,b in zip(poly,poly[1:]+poly[:1])]
ob=scene.objects.get('COL_Terrace21_Fork')
field=Surfaces([o for o in scene.objects if o.name in report['cut'] and not 'Stem' in o.name]+([ob] if ob else []))
fp=json.loads((here/'beds.json').read_text());locations={};rows=[];pairs=[]
def height(p):
    hit=field.down(p.x,p.y,18,12)
    return hit[0][0] if hit else None
def point(p):
    key=tuple(round(v,4) for v in p)
    if key not in locations:locations[key]=height(p)
    return str(key)
def inside(p):
    return min(u.cross(p-a) for a,b,u in edges)>1.5 and all((p-Vector(b['center'])).length>max(b['size'])*.54+.30 for b in fp)
for i in range(71,136):
    for j in range(-159,-118):
        p=Vector((i*.5,j*.5))
        for v in [Vector((.5,0)),Vector((0,.5))]:
            if all(inside(q) for q in (p-v,p,p+v)):rows.append([point(q) for q in (p-v,p,p+v)])
for a,b,u in edges:
    n=Vector((-u.y,u.x))
    for i in range(1,math.ceil((b-a).length/.22)):
        p=a.lerp(b,i/math.ceil((b-a).length/.22))
        if any((p-Vector(bed['center'])).length<max(bed['size'])*.54 for bed in fp):continue
        pairs.append([point(p-n*.02),point(p+n*.02)])
phase='after' if ob else 'before'
coords={str(k):v for k,v in locations.items()}
save('sections_'+phase+'.json',{'heights':coords,'triplets':rows,'pairs':pairs})
if ob:
    header=[str(k) for k in locations];save('probe_keys.json',header)
    save('probes.json',[[x,h if h is not None else 12,-y] for (x,y),h in locations.items()])
    print('REOPEN',bpy.app.version_string,scene['street_revision'],sum(o.name.startswith('Garden21_') for o in scene.objects),len(scene.objects))
print('PROBES',phase,len(coords),len(rows),len(pairs),sum(v is None for v in coords.values()))
