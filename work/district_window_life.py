"""Retrofit rain hoods and laundry rails to surveyed sockets on existing facades."""
import math,json,random
import bpy
from mathutils import Vector

def build(source, project, layer, architecture, ground, plain):
    mat=[plain('R21 Galvanised folded edge',(.26,.28,.25),.56),
         plain('R21 Rusted angle frame',(.091,.067,.045),.70),
         plain('R21 Faded green sheet',(.21,.28,.244),.67),
         plain('R21 Chalked ivory sheet',(.39,.36,.275),.69),
         plain('R21 Work indigo',(.077,.14,.19),.95),
         plain('R21 Worn ticking',(.52,.42,.30),.98),
         plain('R21 Woven stripe',(.19,.105,.082),.98),
         plain('R21 Muted celadon cotton',(.22,.34,.28),.95)]
    for j in [4,5,6,7]:mat[j].use_backface_culling=False
    target={'809889623':[0,1,2,5],'1413081560':[1,2,3,4],'A05':[0,1,2],
            'A06':[1,3],'A01':[0,1,2],'809889622':[0,2],'A03':[0,1,3],
            '809889627':[0,2,3],'809889629':[1,3],'1335306667':[1,2]}
    data=json.loads((project/'architecture_manifest.json').read_text(encoding='utf8'))
    dg=bpy.context.evaluated_depsgraph_get();rng=random.Random(8822);all_records=[]
    for b in data['buildings']:
        key=str(b['id'])
        if key not in target:continue
        verts=[];ff=[];slots=[]
        def face(points,slot):
            ix=len(verts);verts.extend(points);ff.append(tuple(range(ix,ix+len(points))));slots.append(slot)
        for side in b['facade_openings']:
            if side['edge'] not in target[key]:continue
            a=Vector((*side['a'],b['base_m']));t=Vector((side['b'][0]-a.x,side['b'][1]-a.y,0)).normalized()
            n=Vector((t.y,-t.x,0));up=Vector((0,0,1))
            def pt(u,d,z):return a+t*u+n*d+up*z
            def beam(start,end,r,slot=1,sides=8):
                p=pt(*start);q=pt(*end);v=(q-p).normalized()
                ax=v.cross(up if abs(v.z)<.8 else n).normalized();ay=v.cross(ax)
                ring=[r*(ax*math.cos(k*math.tau/sides)+ay*math.sin(k*math.tau/sides)) for k in range(sides)]
                for i,off in enumerate(ring):face([p+off,p+ring[(i+1)%sides],q+ring[(i+1)%sides],q+off],slot)
            def socket(u,z):
                hit,where,_,_,ob,_=bpy.context.scene.ray_cast(dg,pt(u,1.35,z),-n,distance=1.61)
                if not hit or ('B_'+key+'_') not in ob.name:return None
                return (where-pt(u,0,z)).dot(n)
            holes=[h for h in side['holes'] if h[2]>3.5 and 1.1<h[1]-h[0]<2.65 and 1.2<h[3]-h[2]<1.99]
            rng.shuffle(holes);made=0
            for u0,u1,bottom,top in holes:
                if made>=min(4,1+len(holes)//5):break
                u=(u0+u1)/2;w=(u1-u0)+.28
                # Rain hoods fasten above the opening. Rails fasten to the piers
                # outside its jambs. Both brackets need an actual masonry hit.
                drying=(len(all_records)+made)%3==1
                mount=bottom+.48 if drying else top+.14
                extent=.64 if drying else .83
                anchors=[socket(u+sgn*(w*.5),mount) for sgn in [-1,1]]
                lower=[socket(u+sgn*(w*.5),mount-.31) for sgn in [-1,1]]
                checks=anchors+lower
                if any(d is None or abs(d)>.205 for d in checks):continue
                if any((depth:=socket(u+s*w*.34,mount+.015)) is not None and depth>.28 for s in [-1,0,1]):continue
                center=pt(u,extent,bottom)
                if center.z-ground(center.x,center.y)<3.0:continue
                level=max(anchors)+.04
                for k,sign in enumerate([-1,1]):
                    x=u+sign*w*.5
                    beam((x,anchors[k]-.006,mount),(x,level+extent,mount-.12),.016,1)
                    beam((x,lower[k]-.006,mount-.31),(x,level+extent*.79,mount-.095),.012,1)
                    beam((x,anchors[k]+.01,mount+.065),(x,lower[k]+.01,mount-.37),.024,1,4)
                if drying:
                    tip=level+extent;rodz=mount-.115
                    beam((u-w*.56,tip,rodz),(u+w*.56,tip,rodz),.011,0,12)
                    palette=rng.choice([4,5,7]);sw=w*rng.uniform(.41,.68);length=rng.uniform(.53,.92)
                    cx=u+rng.uniform(-.12,.12)
                    def fabric(i,j):
                        s=i/28;v=j/20
                        d=tip+.019+.016*math.sin(s*math.tau*3.2+.43*v)*(.35+.9*v)+.028*v*v
                        z=rodz+.006-length*v-.036*math.sin(math.pi*s)*(1-.6*v)+v*v*.021*math.sin(s*8.)
                        return pt(cx+(s-.5)*sw+.014*v*math.sin(5*s),d,z)
                    for i in range(28):
                        for j in range(20):
                            col=6 if palette==5 and (i in (3,5,22) or j in (17,19)) else palette
                            face([fabric(i,j),fabric(i+1,j),fabric(i+1,j+1),fabric(i,j+1)],col)
                    for i in range(28):
                        p=fabric(i,0);q=fabric(i+1,0)
                        face([q,p,p-n*.053-up*.12,q-n*.053-up*.12],palette)
                else:
                    # Thin folded sheet with a turned front hem and corrugation.
                    slot=rng.choice([0,2,2,3]);count=max(18,round(w/.07)*4)
                    prev=None
                    for k in range(count+1):
                        x=u-w*.56+w*1.12*k/count;ripple=.010*math.cos(k*math.pi/2)
                        row=[pt(x,level-.04,mount+.075+ripple),pt(x,level+extent,mount-.109+ripple),pt(x,level+extent,mount-.141+ripple)]
                        if prev:
                            face([prev[0],row[0],row[1],prev[1]],slot)
                            face([prev[1],row[1],row[2],prev[2]],slot)
                        prev=row
                made+=1
                all_records.append({'building':key,'edge':side['edge'],'opening':list(map(lambda v:round(v,3),[u0,u1,bottom,top])),
                                 'kind':'drying rail and cloth' if drying else 'sheet rain hood','four_socket_depths_m':[round(d,4) for d in checks]})
        if ff:
            name='R21_Inhabited_facade_'+key;m=bpy.data.meshes.new(name);m.from_pydata(verts,[],ff);m.update()
            ob=bpy.data.objects.new(name,m);layer.objects.link(ob);architecture.append(ob)
            for material in mat:m.materials.append(material)
            for p,idx in zip(m.polygons,slots):p.material_index=idx
    return all_records
