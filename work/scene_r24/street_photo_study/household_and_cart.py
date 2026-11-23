"""A single west-lane doorstep garden and a two-wheel produce handcart beside the market."""
from mathutils import Matrix
extras=[]
placements=[]
solids=[]
def plant_copy(x,y,base,scale,spin):
    originals=[scene.objects['B_809889623_market_Interior_asset_0_%02d'%i] for i in range(3)]
    coords=[ob.matrix_world@Vector(c) for ob in originals for c in ob.bound_box]
    low=min(v.z for v in coords);mid=Vector(((min(p.x for p in coords)+max(p.x for p in coords))*.5,(min(p.y for p in coords)+max(p.y for p in coords))*.5,low))
    transform=Matrix.Translation((x,y,base))@Matrix.Rotation(spin,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-mid)
    number=len(placements);placements.append(dict(at=[x,base,-y],yaw=spin,scale=scale))
    for i,src in enumerate(originals):
        cp=src.copy();cp.data=src.data;cp.parent=None;cp.matrix_world=transform@src.matrix_world;cp.name=f'Workday12_ResidentPot_{number}_{i}';extras.append(cp)
group='Workday12_DoorstepGarden'
# Narrow recycled slats parallel to the east-side wall. Separate feet meet the sloped approach.
x,y=-66.82,-16.35
h=anchor('doorstep bench',x,y);top=h+.40
for dx in [-.16,.16]:
    for dy in [-.57,.57]:
        fz=anchor('garden bench foot',x+dx,y+dy,h)
        rod((x+dx,y+dy,fz+.002),(x+dx,y+dy,top),.027,'timber',5)
for i in range(3):box(x+(i-1)*.127,y,top,(.119,1.29,.042),'timber')
solids.append(dict(at=[x,top-.10,-y],size=[.42,.22,1.31]))
plant_copy(x+.01,y-.34,top+.023,1.54,.46)
plant_copy(x-.02,y+.33,top+.023,1.03,2.6)
# An old red-clay pot with narrow spring-onion leaves beside the bench.
px,py=x-.02,y+.95;ph=anchor('chive pot',px,py,h)
rod((px,py,ph+.003),(px,py,ph+.29),.133,'terracotta',28,.192)
ring(px,py,ph+.284,.192,.192,.015,'terracotta');rod((px,py,ph+.29),(px,py,ph+.296),.169,'old_cane',26)
for i in range(60):
    a=rng.random()*math.tau;r=.128*math.sqrt(rng.random());xx=px+r*math.cos(a);yy=py+r*math.sin(a)
    height=rng.uniform(.18,.45);bend=rng.uniform(.026,.14);ang=a+rng.uniform(-.75,.75)
    mid=(xx+.27*bend*math.cos(ang),yy+.27*bend*math.sin(ang),ph+.296+height*.69)
    rod((xx,yy,ph+.293),mid,.0039,'green' if i%3 else 'pale_leaf',5,.0046)
    rod(mid,(xx+bend*math.cos(ang),yy+bend*math.sin(ang),ph+.296+height),.0046,'green',5,.00065)
# Two long handles and wheels balance the cart on the front parking legs.
group='Workday12_ProduceHandcart'
cx,cy=-31.46,-74.90
h=anchor('cart axle station',cx,cy,9.2)
rad=.239;ax=cx+.18;az=max(anchor('cart tyre',ax,cy+d,h) for d in [-.377,.377])+rad
def cart_wheel(x,y,z):
    va=[];fa=[];N=40;M=8
    for i in range(N):
        a=i*math.tau/N
        for j in range(M):
            t=j*math.tau/M;va.append((x+(rad-.025+.025*math.cos(t))*math.cos(a),y+.026*math.sin(t),z+(rad-.025+.025*math.cos(t))*math.sin(a)))
    for i in range(N):
        for j in range(M):fa.append((i*M+j,i*M+(j+1)%M,((i+1)%N)*M+(j+1)%M,((i+1)%N)*M+j))
    part(va,fa,'rubber')
    for i in range(12):
        a=i*math.tau/12;rod((x,y,z),(x+(rad-.037)*math.cos(a),y,z+(rad-.037)*math.sin(a)),.006,'dark_steel',6)
    # Steel rim rolled round the inside edge of the solid rubber tyre.
    for i in range(32):
        a=i*math.tau/32;b=(i+1)*math.tau/32
        rod((x+(rad-.044)*math.cos(a),y,z+(rad-.044)*math.sin(a)),(x+(rad-.044)*math.cos(b),y,z+(rad-.044)*math.sin(b)),.009,'dark_steel',5)
# Both wheels follow the small crossfall; the axle actually connects their hubs.
ends=[]
for offset in [-.377,.377]:
    ground=support(ax,cy+offset,h)[0];height=ground+rad-.001
    cart_wheel(ax,cy+offset,height);ends.append((ax,cy+offset,height))
    rod((ax,cy+offset*.84,height),(ax-.03,cy+offset*.71,az+.11),.023,'paint',7)
rod(*ends,.027,'dark_steel',8)
for oy in [-.27,.27]:
    fz=anchor('cart parking leg',cx-.61,cy+oy,h)
    rod((cx-.61,cy+oy,fz+.001),(cx-.57,cy+oy,az+.118),.018,'paint',7)
    rod((cx-.63,cy+oy,az+.11),(cx+.76,cy+oy,az+.11),.027,'paint',7)
    rod((cx-.57,cy+oy,az+.106),(cx-1.19,cy+oy,az+.41),.021,'paint',7)
    rod((cx-1.19,cy+oy,az+.41),(cx-1.34,cy+oy,az+.43),.025,'rubber',7)
for i in range(6):box(cx+.03,cy+(i-2.5)*.10,az+.146,(1.34,.094,.046),'timber')
# Two slatted return crates, one turned crosswise with an open interior.
def slat_crate(tx,ty,tz,w,d,height):
    for i in [-1,1]:
        for j in [-1,1]:box(tx+i*(w*.5-.02),ty+j*(d*.5-.02),tz+height/2,(.031,.031,height),'split_bamboo')
    for j in range(3):
        high=tz+.038+j*(height-.071)/2
        for k in [-1,1]:
            box(tx,ty+k*(d*.5-.013),high,(w,.020,.047),'light_cane' if j==2 else 'split_bamboo')
            box(tx+k*(w*.5-.012),ty,high,(.021,d,.047),'old_cane' if j==0 else 'split_bamboo')
    for i in range(4):box(tx+(i-1.5)*w*.238,ty,tz+.016,(w*.222,d-.014,.026),'old_cane')
slat_crate(cx+.35,cy,az+.171,.55,.45,.27)
slat_crate(cx-.25,cy+.035,az+.171,.46,.48,.22)
solids.append(dict(at=[cx+.02,az+.14,-cy],size=[1.43,.38,.76]))
(root/'workday_layout.json').write_text(json.dumps({'plants':placements,'solids':solids},indent=2),'utf-8')
(project/'assets/street_use_r24/layout.json').write_text(json.dumps({'plants':placements,'solids':solids},indent=2),'utf-8')

