"""Identify and join square-ended residential flights at actual changes in direction."""
from mathutils import Vector
sys.path.insert(0,str(here.parents[1]/'project/chongqing_blender_v05'))
from district_layout import SUPPLEMENTAL
from site_neighborhood import tread_rows
measure['landings']=[]
for label,path,width in SUPPLEMENTAL:
    if label not in ['West residential link','East photo alley']:continue
    key=label.replace(' ','_')
    source=scene.objects['COL_Walk_'+key+'_step_concrete']
    trim=scene.objects['Walk_details_'+key+'_stone']
    rows=tread_rows(source.name)
    for before,corner,after in zip(path,path[1:],path[2:]):
        point=Vector(corner)
        d1=(point-Vector(before)).normalized();d2=(Vector(after)-point).normalized()
        if abs(d1.angle_signed(d2))<.19:continue
        n1=Vector((-d1.y,d1.x));n2=Vector((-d2.y,d2.x))
        mit=(n1+n2).normalized()
        if mit.dot(n1)<.55:continue
        def side(d,previous):
            candidates=[]
            for c,ring in rows:
                v=c.xy-point
                if abs(v.cross(d))>.03:continue
                t=v.dot(d)*(-1 if previous else 1)
                if not .8<t<4.7:continue
                border=max((abs((p.xy-point).dot(d)) for p in ring))
                if border<1.50:continue
                candidates.append((abs(border-2.20),border,c.z))
            if not candidates:return None
            _,dist,y=min(candidates)
            return point+d*dist*(-1 if previous else 1),y,dist
        start=side(d1,True);end=side(d2,False)
        if not start or not end:continue
        a,za,da=start;c,zc,dc=end
        if abs(za-zc)/(da+dc)>.29:continue
        mid=point;zm=(za*dc+zc*da)/(da+dc)
        rings=[[a-n1*width/2,a+n1*width/2,mid+mit*(width/2/mit.dot(n1)),mid-mit*(width/2/mit.dot(n1))],
               [mid-mit*(width/2/mit.dot(n1)),mid+mit*(width/2/mit.dot(n1)),c+n2*width/2,c-n2*width/2]]
        ds=[(r,min(za,zc)-.68,max(za,zc)+.48) for r in rings]
        solid_clip(source,ds);solid_clip(trim,ds)
        oldbed=scene.objects.get('COL_R23_PathFoundations')
        if oldbed:solid_clip(oldbed,ds)
        if label=='West residential link':
            # The older dressed stone has independent render geometry over the collision stair.
            solid_clip(scene.objects['R21_Dressed_West_steps'],ds)
        for ring,h1,h2 in zip(rings,[za,zm],[zm,zc]):
            v=[Vector((p.x,p.y,h)) for p,h in zip(ring,[h1,h1,h2,h2])]
            for ids in [(0,2,1),(0,3,2)]:face('COL_Patrol25_TurnLandings',[v[i] for i in ids],'terrazzo')
            for i,j in [(1,2),(3,0),(0,1),(2,3)]:
                p,q=v[i],v[j]
                g1=height(p.x,p.y,p.z);g2=height(q.x,q.y,q.z)
                face('COL_Patrol25_TurnLandings',[p,q,Vector((q.x,q.y,min(q.z-.18,g2-.045 if g2 is not None else q.z-.50))),Vector((p.x,p.y,min(p.z-.18,g1-.045 if g1 is not None else p.z-.50)))],'edge')
        measure['landings'].append({'street':label,'center_xy':list(mid),'entry':[a.x,a.y,za],'exit':[c.x,c.y,zc]})
