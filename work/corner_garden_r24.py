"""Build the planting and maintenance strip between the mapped carriageway and side street."""
import math,random,bmesh
from mathutils import Vector

def build(scene,s,change,spatial,surface,box,rod,mat,bpy):
    from grade_junction_r24 import sections,Edge
    road=Edge([b for a,b in sections(scene,(1189963547,49182408))])
    foot=scene.objects['COL_Road_176034707_0_pavement']
    loops=[[foot.matrix_world@foot.data.vertices[i].co for i in f.vertices] for f in foot.data.polygons if f.normal.z>.5]
    def northern(x):
        points=[]
        for loop in loops:
            for p,q in zip(loop,loop[1:]+loop[:1]):
                if (p.x<=x<q.x or q.x<=x<p.x):points.append(p.lerp(q,(x-p.x)/(q.x-p.x)))
        return min(points,key=lambda p:p.y) if points else None
    rows=[]
    for i in range(94):
        x=55+i*.25;a=road.sample(x);b=northern(x)
        if b is not None and b.y-a.y>.55:
            rows.append((Vector((x,a.y+.025,a.z)),Vector((x,b.y-.025,b.z))))
    assert len(rows)>40
    low=Edge([a for a,b in rows]);high=Edge([b for a,b in rows])
    start,end=rows[0][0].x,rows[-1][0].x
    old=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Terrain_200m')]
    from terrain_strip_r24 import cut_strip
    ground=spatial(old);removed=cut_strip(old,low,high,change)
    soil=mat('verge_soil',(.133,.107,.068));aggregate=mat('verge_stone',(.245,.249,.225))
    leaves=[mat('verge_leaf_%d'%i,color) for i,color in enumerate([(.055,.109,.039),(.079,.158,.052),(.115,.168,.066)])]
    metal=mat('verge_grate',(.094,.10,.086),.63,.37)
    def point(x,t):
        a=low.sample(x);b=high.sample(x);v=a.lerp(b,t);width=b.y-a.y
        # A narrow gravel maintenance path remains beside the bridge pier.
        v.z+=.048-.07*math.sin(t*math.pi)*min(1.,width*.55)
        return v
    def plant_band(x):
        width=high.sample(x).y-low.sample(x).y
        return min(.82,max(.16,(width-.90)/width))
    def breaks(x):
        t=plant_band(x);return [0.,.08,t,t+(1-t)*.43,1.]
    def quad(group,m,vs):
        surface(group,m,vs,[(0,1,2,3)])
    bearing_faces=[]
    for (a,_),(b,_) in zip(rows,rows[1:]):
        for k in range(4):
            l,r=breaks(a.x)[k:k+2];l2,r2=breaks(b.x)[k:k+2]
            pts=[point(a.x,l),point(b.x,l2),point(b.x,r2),point(a.x,r)]
            quad('COL_R24_Verge',soil if k==1 else aggregate,pts)
            bearing_faces.append([list(p) for p in pts])
    for t in [0.,1.]:
        for i in range(0,len(rows)-1,4):
            x=rows[i][0].x;x2=rows[min(i+4,len(rows)-1)][0].x-.005
            a=point(x,t);b=point(x2,t);inward=.125 if t==0. else -.125
            cap=[a,b,b+Vector((0,inward,0)),a+Vector((0,inward,0))]
            for v in cap:v.z+=.064
            quad('COL_R24_VergeKerb',aggregate,cap if t==0. else cap[::-1])
            for j,k in [(0,1),(1,2),(2,3),(3,0)]:
                v,w=cap[j],cap[k];quad('COL_R24_VergeKerb',aggregate,[v-Vector((0,0,.18)),w-Vector((0,0,.18)),w,v] if t==0 else [w-Vector((0,0,.18)),v-Vector((0,0,.18)),v,w])
    # Tie the end faces to the old terrain where the managed verge meets its neighbour.
    for x in [start,end]:
        for i in range(12):
            a=point(x,i/12);b=point(x,(i+1)/12);base=[]
            for p in (a,b):
                z=[v.z for ((xl,xh),(yl,yh),_),tree,_ in ground if xl<=x<=xh and yl<=p.y<=yh if (v:=tree.ray_cast((x,p.y,40),(0,0,-1),75)[0]) is not None]
                base.append(Vector((p.x,p.y,min(p.z-.08,max(z,default=p.z)-.05))))
            quad('COL_R24_VergeKerb',aggregate,[base[0],base[1],b,a] if x==end else [base[1],base[0],a,b])
    rng=random.Random(2481);tufts=0
    for i in range(380):
        x=rng.uniform(start+.17,end-.17);band=plant_band(x)
        if band<.29:continue
        t=rng.uniform(.1,band-.03);p=point(x,t)
        density=.70+.32*math.sin(x*.88)+.23*math.cos(p.y*2.4)
        if rng.random()>density or math.hypot(x-70.165,p.y+83.209)<1.45:continue
        tufts+=1
        moss=rng.choice(leaves);radius=rng.uniform(.12,.28)
        for j in range(rng.randint(9,17)):
            ang=rng.uniform(0,math.tau);u=Vector((math.cos(ang),math.sin(ang),0));v=Vector((-u.y,u.x,0));height=rng.uniform(.12,.33);span=radius*rng.uniform(.56,1.36);blade=rng.uniform(.008,.019)
            pos=p+u*rng.uniform(.015,.059);ps=[]
            for f,half_w,lift in [(0,.003,-.014),(.35,blade,height*.74),(.72,blade*.67,height),(1.,.001,height*.72)]:
                center=pos+u*span*f+Vector((0,0,lift));ps.extend([center-v*half_w,center+Vector((0,0,half_w*.45)),center+v*half_w])
            faces=[(3*k+j,3*k+j+3,3*k+j+4,3*k+j+1) for k in range(3) for j in range(2)]
            surface('R24_ShadeGrass',moss,ps,faces+[(d,c,b,a) for a,b,c,d in faces],True)
    for x in [start+1.9,min(end-1.7,start+11.4)]:
        a=low.sample(x);width=high.sample(x).y-a.y
        if width<.9:continue
        p=point(x,.27/width);p.z+=.007
        box('R24_VergeDrain',metal,tuple(p),(.55,.26,.018))
        for j in range(9):box('R24_VergeDrain',aggregate,(p.x-.24+j*.06,p.y,p.z+.014),(.016,.235,.017))
    # Two legible street names on a single anchored mast at the pedestrian corner.
    x,y=30.0,-78.04
    trees=spatial([scene.objects['COL_Walk_OSM_734116598_0_pavement']])
    z=trees[0][1].ray_cast((x,y,25),(0,0,-1),35)[0].z
    pole=mat('sign_galvanised',(.294,.305,.292),.57,.57);back=mat('sign_back',(.12,.163,.161),.66,.31)
    rod('COL_R24_StreetMast',pole,(x,y,z-.025),(x,y,z+3.01),.034,.025,sides=12)
    box('R24_StreetMast',pole,(x,y,z+.023),(.154,.148,.049))
    sign=mat('street_lettering',(.6,.65,.61),.61,.04);tex=sign.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(s/'road_names.png'));tex.image.pack();sign.node_tree.links.new(tex.outputs['Color'],sign.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    for i,(angle,lvl) in enumerate([(-.13,2.71),(.59,2.33)]):
        along=Vector((math.cos(angle),math.sin(angle),0));normal=Vector((along.y,-along.x,0))
        mid=Vector((x,y,z+lvl))+along*(.54 if i==0 else -.53);u=along*.64;up=Vector((0,0,.155))
        for side in [-1,1]:
            c=mid+normal*(side*.019);direction=u*side
            vs=[c-direction-up,c+direction-up,c+direction+up,c-direction+up]
            y0=.5 if i==0 else 0.
            surface('R24_RoadNames',sign,vs,[(0,1,2,3)],uv=[(0,y0),(1,y0),(1,y0+.5),(0,y0+.5)])
        for dz in [-.155,.155]:
            rod('R24_StreetMast',back,mid-u+Vector((0,0,dz)),mid+u+Vector((0,0,dz)),.012,sides=7)
        for dz in [-.115,.115]:
            rod('R24_StreetMast',pole,(x,y,z+lvl+dz-.015),(x,y,z+lvl+dz+.015),.041,sides=12)
    return dict(begin=start,end=end,soil_faces_removed=removed,plant_tufts=tufts,sign_anchor=[x,y,z],bearing_faces=bearing_faces)

