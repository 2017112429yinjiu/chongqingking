"""Close the gap between the two surveyed primary-road edges, carrying side streets across it."""
import math
from mathutils import Vector

def build(s,edges,original,surface,mat,box,rod):
    south,north=edges['east'][1],edges['west'][0]
    start=max(south.x[0],north.x[0]);end=min(south.x[-1],north.x[-1])
    step=.42;n=math.ceil((end-start)/step)
    xx=[start+(end-start)*i/n for i in range(n+1)]
    crossing=[item for item in original if item[2].endswith('_asphalt') and item[2].split('_')[2] in ('176034707','1375242616','1375242618','1256840008')]
    def connector(x,y):
        for ((l,r),(b,t),_),tree,_ in crossing:
            if l-.12<=x<=r+.12 and b-.12<=y<=t+.12 and tree.ray_cast((x,y,35),(0,0,-1),65)[0] is not None:return True
        return False
    open_at=[]
    for i,x in enumerate(xx):
        a,b=south.sample(x),north.sample(x)
        if any(connector(x,a.y+(b.y-a.y)*t) for t in [0,.25,.5,.75,1.]):open_at.append(i)
    concrete=mat('median_concrete',(.285,.288,.264))
    chip=mat('median_cinder',(.18,.17,.14));asphalt=mat('median_asphalt',(.126,.127,.12));reflector=mat('median_marker',(.68,.47,.16),.56)
    rows=[]
    for i,x in enumerate(xx):
        a,b=south.sample(x),north.sample(x);width=b.y-a.y
        closest=min((abs(j-i) for j in open_at),default=100)*step
        u=min(1.,max(0.,(closest-1.9)/2.8));u=u*u*(3.-2.*u)
        # Across an intersection the full width becomes a paved crown. Where the
        # two lanes step apart the median has a raised north shelf and a faced slope.
        points=[]
        for t,profile in [(0,0),(.075,0),(.34,.05),(.63,.96),(.91,1),(1,1)]:
            p=a.lerp(b,t);blend=t*(1-u)+profile*u
            p.z=a.z+(b.z-a.z)*blend+.006+u*(.082 if 0<t<1 else .054)
            points.append(p)
        rows.append((points,u,width))
    count=0;markers=0
    for i in range(len(rows)-1):
        ps,u,w=rows[i];qs,v,w2=rows[i+1]
        if min(w,w2)<.07:continue
        count+=1
        for j in range(5):
            m=asphalt if max(u,v)<.09 else (chip if j in [1,3] and min(w,w2)>1.1 else concrete)
            surface('COL_R24_Median',m,[ps[j],qs[j],qs[j+1],ps[j+1]],[(0,1,2,3)])
        for k in [0,5]:
            a,b=ps[k],qs[k]
            face=[a-Vector((0,0,.15)),b-Vector((0,0,.15)),b,a]
            surface('COL_R24_Median',concrete,face,[(0,1,2,3) if k==0 else (3,2,1,0)])
        if i%27==13 and u>.97 and w>.6:
            p=ps[4].lerp(ps[5],.37);p.z+=.015
            box('R24_MedianStud',concrete,p,(.15,.095,.03))
            box('R24_MedianStud',reflector,p+Vector((-.076,0,.007)),(.006,.075,.014))
            markers+=1
    return dict(fitted_length_m=count*(end-start)/n,sampled_crossing_rows=len(open_at),reflectors=markers)

