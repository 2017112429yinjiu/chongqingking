"""Join the two cropped parts of existing OSM way 59146775 and seat its structure."""
import math,json,bisect
from mathutils import Vector

def build(scene,s,spatial,surface,box,rod,mat,garden):
    from mathutils.bvhtree import BVHTree
    panels=garden['bearing_faces']
    bed=BVHTree.FromPolygons([p for face in panels for p in face],[tuple(i*4+j for j in range(4)) for i in range(len(panels))])
    old=[scene.objects['COL_Road_59146775_%d_asphalt'%i] for i in [0,1]]
    sections=[]
    for o in old:
        v=[o.matrix_world@q.co for q in o.data.vertices]
        sections.append([(a,b) for a,b in zip(v[::2],v[1::2])])
    def mid(pair):return (pair[0]+pair[1])*.5
    left,right=sections
    x1=mid(left[-1]).x;x2=mid(right[0]).x
    route=json.loads((s/'playtest/source_data/geo_layout.json').read_text(encoding='utf8'))
    source=next(q['points'] for q in route['roads'] if q['id']==59146775 or str(q['id'])=='59146775')
    terrain=[o for o in scene.objects if o.type=='MESH' and (o.name.startswith('COL_Terrain_200m') or o.name in ('R22_Bank_Outer','R22_Bank_Relief'))]
    land=spatial(terrain)
    def soil(x,y):
        planted=bed.ray_cast((x,y,60),(0,0,-1),110)[0]
        if planted is not None:return planted.z
        for prefix in [('COL_Terrain',),('R22_Bank_Outer',),('R22_Bank_Relief',)]:
            vals=[]
            for ((xl,xh),(yl,yh),_),tree,name in land:
                if not name.startswith(prefix) or not(xl-.001<=x<=xh+.001 and yl-.001<=y<=yh+.001):continue
                p,_,_,_=tree.ray_cast((x,y,230),(0,0,-1),400)
                if p is not None:vals.append(p.z)
            if vals:return max(vals)
        raise ValueError(('no support for bridge',x,y))
    def route_y(x):
        i=min(len(source)-2,max(0,bisect.bisect_right([p[0] for p in source],x)-1));a,b=source[i:i+2]
        return a[1]+(b[1]-a[1])*((x-a[0])/(b[0]-a[0]))
    def insert(a,b,first=None,last=None):
        count=math.ceil((b-a)/1.25);sample=[]
        for i in range(count+1):
            x=a+(b-a)*i/count;y=route_y(x);g=soil(x,y)
            if first is not None and last is not None:
                t=i/count;z=mid(first).z*(1-t)+mid(last).z*t
            else:
                end=mid(last if last is not None else first)
                near=abs(end.x-x);t=max(0.,min(1.,1.-near/abs(b-a)));t=t*t*(3.-2.*t)
                z=g+.13+(end.z-soil(end.x,end.y)-.13)*t
            tangent=Vector((1.,(route_y(x+.05)-route_y(x-.05))/.10,0.)).normalized()
            n=Vector((-tangent.y,tangent.x,0.))
            center=Vector((x,y,z));sample.append((center-2.60*n,center+2.60*n))
        if first is not None:sample[0]=first
        if last is not None:sample[-1]=last
        return sample
    west=insert(source[0][0],mid(left[0]).x,last=left[0])
    middle=insert(x1,x2,left[-1],right[0])
    east=insert(mid(right[-1]).x,source[-1][0],first=right[-1])
    line=west[:-1]+left+middle[1:-1]+right+east[1:]
    retired=['Bridge_structure_59146775_concrete','Bridge_structure_59146775_concrete.001']
    for name in retired:
        scene.objects[name].hide_render=True;scene.objects[name].hide_set(True)
    concrete=mat('link_concrete',(.31,.306,.275));asphalt=mat('link_asphalt',(.13,.133,.123))
    iron=mat('link_painted_rail',(.165,.113,.077),.77,.21);rubber=mat('bearing_pad',(.058,.057,.051))
    stripe=mat('edge_line',(.58,.57,.51))
    def quad(group,m,a,b,c,d):surface(group,m,[a,b,c,d],[(0,1,2,3)])
    def frame(pair):
        a,b=pair;center=mid(pair);n=(b-a).normalized()
        return center,n
    def at(pair,offset,dz):
        p,n=frame(pair);return p+offset*n+Vector((0,0,dz))
    for a,b in zip(line,line[1:]):
        # A closed box with splayed webs gives the elevated road a visible underside.
        profile=[(-2.80,-.035),(-2.80,-.28),(-1.83,-.40),(-1.49,-.91),(1.49,-.91),(1.83,-.40),(2.80,-.28),(2.80,-.035)]
        for k in range(len(profile)-1):
            p,q=profile[k:k+2]
            quad('R24_FlyoverBox',concrete,at(a,*q),at(b,*q),at(b,*p),at(a,*p))
        for sign in (-1,1):
            face=[at(a,sign*2.80,-.035),at(b,sign*2.80,-.035),at(b,sign*2.57,-.015),at(a,sign*2.57,-.015)]
            surface('R24_FlyoverBox',concrete,face,[(0,1,2,3) if sign<0 else (3,2,1,0)])
    for series in [west,middle,east]:
        for a,b in zip(series,series[1:]):
            quad('COL_R24_LinkDeck',asphalt,a[0],b[0],b[1],a[1])
            for sign in [-1,1]:
                face=[at(a,sign*2.23,.009),at(b,sign*2.23,.009),at(b,sign*2.31,.009),at(a,sign*2.31,.009)]
                surface('R24_LinkPaint',stripe,face,[(0,1,2,3) if sign>0 else (3,2,1,0)])
        for sign in [-1,1]:
            # Match both heights and the confirmed rail-end socket of the old sections.
            seq=series[::2]
            if seq[-1] is not series[-1]:seq=seq+[series[-1]]
            for a,b in zip(seq,seq[1:]):
                for h in [.45,1.05]:rod('R24_LinkRail',iron,at(a,sign*2.55,h),at(b,sign*2.55,h),.028,sides=7)
            for a in seq[1:-1]:
                rod('R24_LinkRail',iron,at(a,sign*2.55,-.025),at(a,sign*2.55,1.05),.034,sides=8)
    lanes=json.loads((s/'playtest/assets/block_r23/routes.json').read_text())
    protected=[(Vector((x,-z)),k) for k in ['east','west','promenade'] for x,_,z in lanes[k]]
    supports=[];last=-1000.
    for a in line[::2]:
        c,n=frame(a);ground=soil(c.x,c.y)
        if c.x-last<17.4 or c.z-.94-ground<1.18:continue
        if any((Vector((c.x,c.y))-p).length<(3.65 if k!='promenade' else 1.5) for p,k in protected):continue
        top=c.z-.94;last=c.x
        foot=c.copy()
        if garden['begin']<c.x<garden['end']:
            shifted=c+n*1.24
            if bed.ray_cast((shifted.x,shifted.y,60),(0,0,-1),110)[0] is not None:foot=shifted
        ground=soil(foot.x,foot.y)
        rod('COL_R24_LinkPiers',concrete,(foot.x,foot.y,ground-.55),(foot.x,foot.y,top-.40),.58,.48,sides=18)
        rod('R24_LinkCaps',concrete,c+n*1.60+Vector((0,0,-1.29)),c-n*1.29+Vector((0,0,-1.29)),.35,sides=10)
        for side in [-1,1]:
            pos=c+side*.89*n
            box('R24_LinkCaps',rubber,(pos.x,pos.y,top-.046),(.52,.47,.16))
        supports.append([round(foot.x,3),round(foot.y,3),round(ground,3),round(top,3)])
    return dict(retired=retired,old_gap_m=x2-x1,measured_ends=[[list(v) for v in a] for a in [left[-1],right[0]]],piers=supports,edge_sections=len(line),source_way=59146775)

