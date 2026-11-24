from pathlib import Path
import bpy,sys,math
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import scene,extent,Surfaces
def native(v):return Vector((v[0],-v[2],v[1]))
def read(eye,target,pixels,fov=66):
    eye=native(eye);direction=(native(target)-eye).normalized();right=direction.cross(Vector((0,0,1))).normalized();up=right.cross(direction)
    objs=[]
    for o in scene.objects:
        if o.type!='MESH' or o.hide_render or o.name.startswith('COLH_'):continue
        lo,hi=extent(o)
        if all(lo[i]-10<eye[i]<hi[i]+10 for i in range(3)):objs.append(o)
    s=Surfaces(objs)
    for x,y in pixels:
        ray=(direction+(right*((x+.5-500)/282)+up*((282-y-.5)/282))*math.tan(math.radians(fov)/2)).normalized();hits=[]
        for ob in objs:
            p,n,k,d=s.tree(ob).ray_cast(eye,ray,14)
            if p is not None:hits.append([round(d,4),ob.name,[round(v,3) for v in p],k])
        print('PIX',x,y,sorted(hits)[:3])
if '--landing' in sys.argv:
    x,y,h=16.41106796,-66.57210541,10.7670326
    ang=math.pi*.75
    read((x+4.3*math.cos(ang),h+2.75,-y+4.3*math.sin(ang)),(x,h+.34,-y),[(399,411),(400,412),(411,421),(407,418),(502,515),(494,503),(575,297),(409,214),(272,254)],64)
elif '--intersections' in sys.argv:
    import json
    for rec in json.loads((here/'legacy_turns.json').read_text('utf8')):
        x,y,h=rec['centre']
        ang=math.pi*.25
        read((x+4.3*math.cos(ang),h+2.75,-y+4.3*math.sin(ang)),(x,h+.34,-y),[(330,290),(515,355),(480,300),(590,330),(532,330),(410,320),(550,280),(452,403)],64)
elif '--last-seams' in sys.argv:
    read((-77.31339,15.76321,35.91897),(-74.,14.42433,34.),[(413,368),(411,350),(397,360),(421,381),(469,375),(411,405),(360,447),(605,360),(600,306)],75)
    read((26.1,25.48,-21.5),(23.9,23.25,-12.6),[(332,334),(328,335),(335,335),(345,329),(413,264),(352,321),(122,328)])
elif '--lanes' in sys.argv:
    read((26.1,25.48,-21.5),(23.9,23.25,-12.6),[(105,429),(114,423),(106,436),(60,466),(480,380),(780,421),(494,295),(382,300),(453,303)])
    read((49.1,23.63,-1.88),(46.54,22.43,-2.23),[(540,187),(538,190),(541,192),(524,162),(530,162),(551,245),(450,349),(574,331),(590,332)])
else:
    read((-18.79,21.31,2.55),(-22.15,20.28,1.71),[(617,530),(618,530),(615,530),(618,526),(526,302),(503,291),(530,333),(468,314),(480,360),(178,360),(850,338),(555,317),(439,470)])
