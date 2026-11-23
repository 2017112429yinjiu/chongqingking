from pathlib import Path
import sys,json,bpy
from mathutils import Vector
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
manifest=json.loads((work/'project/chongqing_blender_v05/architecture_manifest.json').read_text('utf8'))['buildings']
seen=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and len(o.data.polygons)]
def sites():
    src={}
    for o in seen:
        if o.name.startswith(('COL_','COLH_')) and not o.name.startswith(('COL_B_','COL_Upper_B','COL_Outer_B')):src[o.name]=extent(o)
    dump('structures.json',src)
    walls=Surfaces([o for o in seen if o.name.startswith('COL_B_')])
    around=Surfaces([o for o in seen if not o.name.startswith(('COLH_','Outer_','R21_Dressed'))])
    places=[]
    for b in manifest:
        if b['id'] not in [809889622,809889624,1335306667,'A03','A04',1413081560,809889630]:continue
        face=b['facade_openings'][b['front_edge']];a,bb=map(Vector,(face['a'],face['b']));edge=(bb-a).normalized()
        normal=Vector((edge.y,-edge.x))
        entry=b['entrances'][0]
        if (Vector(entry['approach'][:2])-Vector(entry['position'][:2])).dot(normal)<0:normal=-normal
        spans=[]
        for i in range(int((bb-a).length*10)-4):
            d=.25+i*.1;p=a+d*edge
            floor=road.down(*(p+.28*normal),b['base_m']+1.65,6)
            if not floor:continue
            h=floor[0][0];names=[];depths=[]
            for high in [.58,.90,1.20,1.52,1.8]:
                orig=Vector((*(p+normal*.35),h+high));dir=Vector((-normal.x,-normal.y,0))
                contact=[]
                for _,_,o in walls.cells[(math.floor(p.x/8),math.floor(p.y/8))]:
                    hit,n,_,dst=walls.tree(o).ray_cast(orig,dir,.60)
                    if hit is not None:contact.append((dst,o.name))
                if contact:
                    depth,who=min(contact);names.append(who);depths.append(round(.35-depth,4))
            if len(names)==5 and max(depths)-min(depths)<.04 and all(str(b['id']) in n for n in names):
                spans.append([round(d,2),round(h,3),depths[0],names[2]])
        places.append({'id':b['id'],'name':b['name'],'a':list(a),'t':list(edge),'n':list(normal),'spans':spans})
    dump('placement.json',places)
    for x,y in [(-48,-27),(-50,-26),(-53,-31.8),(-58,-31.8),(-61,-31.8),(-63,-32),(-75,25),(-75,23),(-77,23),(-78,23),(-66,24),(-67,24),(-49,-11),(-51,-13),(-67,-21),(-68,-22)]:
        h=road.down(x,y)
        hit=around.down(x,y,min(55,h[0][0]+3.2) if h else 55,6)
        print('SITE',x,y,[(round(z,2),n) for z,n,_ in hit[:5]],flush=True)
sites()
