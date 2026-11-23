"""Build a distance-only city extension on the R22 visible relief, excluding existing shells."""
import math,random,json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

def build(scene,s,spatial,bounds,surface,box,mat,bpy):
    terrain=[o for o in scene.objects if o.name in ('R22_Bank_Outer','R22_Bank_Relief')]
    land=spatial(terrain)
    def ground(x,y):
        hits=[]
        for ((xl,xh),(yl,yh),_),tree,_ in land:
            if xl<=x<=xh and yl<=y<=yh:
                p,_,_,_=tree.ray_cast((x,y,400),(0,0,-1),650)
                if p is not None:hits.append(p.z)
        return max(hits) if hits else None
    footprints=json.loads((s/'playtest/source_data/east_r24/footprints.json').read_text())
    exclusions=[bounds(o) for o in scene.objects if o.type=='MESH' and (o.name.startswith('Context_authored_') or (o.name.startswith('Context_') and o.name[8:9].isdigit()))]
    mats=[]
    for i in range(3):
        m=mat('east_wall_%d'%i,(.43,.42,.40));pic=m.node_tree.nodes.new('ShaderNodeTexImage')
        pic.image=bpy.data.images.load(str(s/('east_windows_%s.png'%i)));pic.image.pack()
        m.node_tree.links.new(pic.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);mats.append(m)
    roof=mat('east_roof',(.245,.243,.222));band=mat('east_concrete_band',(.37,.367,.34))
    glass=mat('east_loggia_glass',(.135,.180,.187),.42,.16)
    shadow=mat('east_balcony_shadow',(.155,.155,.143))
    results=[];synthetic=0
    for rec in footprints:
        pts=rec['points'];xs,ys=zip(*pts);x=sum(xs)/len(xs);y=sum(ys)/len(ys)
        if any(min(xs)<b[0][1]+2 and max(xs)>b[0][0]-2 and min(ys)<b[1][1]+2 and max(ys)>b[1][0]-2 for b in exclusions):continue
        heights=[ground(*p) for p in pts]
        if None in heights:continue
        rng=random.Random(int(rec['osm_id']));area=rec['area']
        try:levels=max(1,int(float(rec['levels'])))
        except (TypeError,ValueError):levels=max(3,min(14,round(math.sqrt(area)/3.7)+rng.randint(-2,2)))
        try:h=float(str(rec['height']).removesuffix(' m'))
        except ValueError:h=levels*(3.05 if levels>7 else 3.23)
        if not rec['levels'] and not rec['height']:synthetic+=1
        h=max(3.4,min(h,170));top=max(heights)+h;base=min(heights)-.36
        if sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(pts,pts[1:]+pts[:1]))<0:pts=pts[::-1]
        group='R24_East_Block_%d'%int(x//240);wall=rng.choice(mats);radix=rng.uniform(.0,.9)
        for side,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):
            width=math.dist(a,b)
            if width<.02:continue
            dx,dy=(b[0]-a[0])/width,(b[1]-a[1])/width
            bays=max(1,round(width/(3.2 if levels>9 else 3.57)))
            u0=radix;u1=u0+bays/8
            surface(group,wall,[(*a,base),(*b,base),(*b,top),(*a,top)],[(0,1,2,3)],uv=[(u0,(base-top)/3.1/8),(u1,(base-top)/3.1/8),(u1,0),(u0,0)])
            oa=(a[0]+dy*.17,a[1]-dx*.17);ob=(b[0]+dy*.17,b[1]-dx*.17)
            for z in [top]+([top-h*.37] if levels>13 else []):
                surface(group,band,[(*oa,z-.25),(*ob,z-.25),(*ob,z+.095),(*oa,z+.095),(*a,z+.095),(*b,z+.095)],[(0,1,2,3),(3,2,5,4)])
            # Model deep balcony stacks on the four closest tagged towers. At this
            # distance a single window texture flattens both side walls and the crown.
            if levels>=20 and x<480 and width>=11:
                def point(u,out,z):
                    return (a[0]+dx*u+dy*out,a[1]+dy*u-dx*out,z)
                def plate(u1,u2,out,lo,hi,material):
                    surface(group,material,[point(u1,.02,lo),point(u2,.02,lo),point(u2,out,lo),point(u1,out,lo),point(u1,.02,hi),point(u2,.02,hi),point(u2,out,hi),point(u1,out,hi)],[(0,1,2,3),(7,6,5,4),(3,2,6,7),(0,3,7,4),(2,1,5,6)])
                for j in range(max(1,int(width//10.))):
                    center=(j+.5)*width/max(1,int(width//10.))
                    span=min(6.4,width*.48);u1=center-span*.5;u2=center+span*.5
                    floor_h=h/levels;depth=1.36 if side%3 else 1.72
                    for k in range(2,levels):
                        base_z=top-h+floor_h*k
                        plate(u1,u2,depth,base_z-.15,base_z+.10,band)
                        if (k+j+side)%5:
                            surface(group,glass,[point(u1+.1,depth-.17,base_z+.12),point(u2-.1,depth-.17,base_z+.12),point(u2-.1,depth-.17,base_z+floor_h-.23),point(u1+.1,depth-.17,base_z+floor_h-.23)],[(0,1,2,3)])
                        plate(u1+.06,u2-.06,depth-.08,base_z+.11,base_z+.78,shadow)
                    for stem in [u1+.12,center,u2-.12]:
                        plate(stem-.10,stem+.10,depth-.02,top-h+2*floor_h,top+.38,band)
                    plate(u1-.17,u2+.17,depth+.18,top-.12,top+.46,band)
        ring=[Vector((*a,top+.07)) for a in pts]
        surface(group,roof,ring,tessellate_polygon([ring]))
        # Place rooftop services inside a large roof triangle so concave slabs retain their outline.
        tris=tessellate_polygon([ring])
        if tris and area>175 and levels>=3:
            tri=max(tris,key=lambda t:(ring[t[1]]-ring[t[0]]).cross(ring[t[2]]-ring[t[0]]).length)
            co=sum((ring[i] for i in tri),Vector())/3
            dist=min((ring[tri[(k+1)%3]]-ring[tri[k]]).cross(co-ring[tri[k]]).length/max(.01,(ring[tri[(k+1)%3]]-ring[tri[k]]).length) for k in range(3))
            side=min(11.5 if levels>=20 else 5.5,dist*1.2)
            if side>1.3:
                bh=4.9 if levels>=20 else (2.6 if levels>6 else 1.35)
                if levels>=20:
                    box(group,shadow,(co.x,co.y,top+bh+.77),(side*.62,side*.51,1.5))
                box(group,band,(co.x,co.y,top+bh/2),(side,side*.81,bh))
                box(group,roof,(co.x,co.y,top+bh+.05),(side+.22,side*.81+.22,.11))
        results.append(rec['osm_id'])
    return dict(installed=results,estimated_storeys=synthetic,footprints_considered=len(footprints))

