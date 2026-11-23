# Each old span had free endpoints based only on the height of the hillside.
# Find opposed, outward-facing solid facade bays with an uninterrupted path between them.
walls_for_cast=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_B_') and any(t in o.name.lower() for t in ['_brick','_tile','_plaster','_concrete','_stone'])]
facades=Surfaces(walls_for_cast)
def ray_facade(start,vec,dist):
    found=None
    candidates=set()
    for i in range(math.ceil(dist/2)+1):
        q=start+vec*min(i*2,dist);candidates.update(t[2] for t in facades.cells.get((math.floor(q.x/8),math.floor(q.y/8)),[]))
    for o in candidates:
        hit,n,idx,d=facades.tree(o).ray_cast(start,vec,dist)
        if hit is not None and (found is None or d<found[0]):found=(d,hit,n.normalized(),o)
    return found
def gvec(v):return [v.x,v.z,-v.y]
spans=[]
seeds=[(-72,-19),(-26,-57),(-65,-35),(-14,-24),(-54,37),(-8,58),(-33,-41),(-53,-73)]
for sx,sy in seeds:
    choices=[]
    for j,(dx,dy) in enumerate([(0,0),(0,2.3),(2.1,0),(-2.4,-1.5)]):
        xx,yy=sx+dx,sy+dy;g=floors(xx,yy)
        if not g:continue
        start=Vector((xx,yy,g[0][0]+5.6))
        for a in range(0,180,15):
            d=Vector((math.cos(math.radians(a)),math.sin(math.radians(a)),0))
            A=ray_facade(start,-d,18);B=ray_facade(start,d,18)
            if not A or not B or A[3]==B[3] or min(A[0],B[0])<1.8 or not 6<A[0]+B[0]<27:continue
            if A[2].dot(d)<.72 or B[2].dot(-d)<.72 or max(abs(A[2].z),abs(B[2].z))>.18:continue
            # The mounts must sit on intact masonry at each insulator height.
            off=[Vector((0,0,k)) for k in [0,.18]]
            if any(not (z:=ray_facade(h[1]+h[2]*.25+v,-h[2],.42)) or z[3]!=h[3] or abs(z[0]-.25)>.025 for h in (A,B) for v in off):continue
            clearance=99
            prev=None
            for k in range(23):
                t=k/22;p=(A[1]+A[2]*.26).lerp(B[1]+B[2]*.26,t);p.z-=4*t*(1-t)*.58
                fl=floors(p.x,p.y,p.z+.1)
                if fl:clearance=min(clearance,p.z-fl[0][0])
                if prev is not None:
                    seg=p-prev
                    if ray_facade(prev,seg.normalized(),seg.length):clearance=-1;break
                prev=p
            if clearance>=3.8:choices.append((abs(A[0]+B[0]-14)+j+A[0]*.008,A,B,clearance))
    if not choices:continue
    _,A,B,clearance=min(choices,key=lambda q:q[0]);label='N13_ServiceSpan_%02d'%len(spans)
    starts=[];ends=[];sources=[]
    for hit,dst in [(A,starts),(B,ends)]:
        _,foot,normal,obj=hit; sources.append({'mesh':obj.name,'foot':gvec(foot),'normal':gvec(normal)})
        for k in [0,.18]:
            base=foot+Vector((0,0,k));tip=base+normal*.255
            rod(label,base-normal*.018,base+normal*.033,.063,'iron',12);rod(label,base+normal*.022,tip,.016,'iron')
            for off,r in [(.152,.04),(.181,.052),(.205,.044)]:rod(label,base+normal*off,base+normal*(off+.021),r,'ceramic',14)
            dst.append(tip)
    for a,b in zip(starts,ends):
        pts=[]
        for j in range(29):
            t=j/28;v=a.lerp(b,t);v.z-=4*t*(1-t)*.58;pts.append(v)
        for u,v in zip(pts,pts[1:]):rod(label,u,v,.011,'wire',6)
    spans.append({'name':label,'mounts':sources,'ends':[[gvec(u),gvec(v)] for u,v in zip(starts,ends)],'clearance':clearance})

