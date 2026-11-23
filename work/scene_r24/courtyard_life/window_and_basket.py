# A short woven blind on the west-facing kitchen, with its brackets fixed in the lintel.
from site_neighborhood import Surfaces
shells=[ob for ob in bpy.context.scene.objects if ob.name.startswith('COL_B_A04_courtyard_home_') and ob.type=='MESH']
receiver=Surfaces(shells);mounts=[]
def fixed_hook(z,h):
    origin=bl((-67.3,h,z));axis=Vector((1,0,0));found=[]
    for ob in shells:
        pos,norm,idx,dist=receiver.tree(ob).ray_cast(origin,axis,1.58)
        if pos is not None and abs(norm.x)>.7:found.append((dist,pos,ob.name))
    if not found:raise ValueError(('missing lintel',z,h))
    _,coord,source=min(found,key=lambda item:item[0]);at=V(god(coord));mounts.append({'at':list(at),'mesh':source})
    box('Court14_BlindFixings',at+V((-.007,0,0)),(.027,.075,.045),'iron')
    tip=at+V((-.235,.003,0));rod('Court14_BlindFixings',at,tip,.010,'iron')
    rod('Court14_BlindFixings',at+V((-.018,-.031,0)),tip,.005,'iron')
    return tip
z0=21.25;left=fixed_hook(z0-.60,19.39);right=fixed_hook(z0+.60,19.39)
rod('Court14_BambooShade',left,right,.048,'cane',18)
for j in range(30):
 h=left.y-.042-j*.0155;xx=left.x-.017-j*.0008;offset=.007*math.sin(j*.31)
 box('Court14_BambooShade',(xx,h,z0+offset),(.009,.012,1.22-.006*math.sin(j*.79)),'cane')
for side in [-.49,0,.49]:
 p=V((left.x-.030,left.y-.020,z0+side));rod('Court14_BambooShade',p,p+V((-.018,-.492,0)),.002,'twine',6)
# Dried peppers are threaded onto the cord; each fruit joins a calyx.
pin=fixed_hook(20.32,18.95);cord=pin+V((0,-.052,0))
rod('Court14_PepperBraid',pin,cord+V((0,-.43,0)),.0032,'twine')
for j in range(25):
 a=j*2.401;along=j*.014;start=cord+V((.004*math.cos(a),-along,.004*math.sin(a)));shift=V((math.cos(a)*.042,0,math.sin(a)*.042))
 neck=start+shift*.5+V((0,-.007,0));middle=start+shift+V((0,-.037,0));end=middle+shift*.40+V((.004,-.060,0))
 rod('Court14_PepperBraid',start,neck,.0033,'edge');rod('Court14_PepperBraid',neck,middle,.0066,'chili',7,.0103);rod('Court14_PepperBraid',middle,end,.0103,'chili',7,.0012)
# A woven carrying basket stands independently on three points on the sloping pavement.
basket=V((-66.84,0,19.30));supports=[]
for i in range(3):
 a=math.tau*i/3;px=basket.x+.105*math.cos(a);pz=basket.z+.105*math.sin(a);supports.append(V((px,ground(px,pz),pz)))
bottom=max(q.y for q in supports)+.012;basket.y=bottom
for v in supports:
 rod('Court14_BackBasket',v-Vector((0,.002,0)),Vector((v.x,bottom+.015,v.z)),.016,'edge');feet.append(list(v))
def weave_point(a,h,ripple=0):
 radius=.119+.100*math.sin((h/.44)*math.pi*.57)+ripple
 return basket+V((radius*math.cos(a),h,.82*radius*math.sin(a)))
for i in range(20):
 a=math.tau*i/20
 for j in range(5):
  h=.44*j/5;h2=.44*(j+1)/5
  rod('Court14_BackBasket',weave_point(a,h),weave_point(a,h2),.0065,'cane',6)
for j in range(20):
 h=.014+j*.022
 for i in range(40):
  a=i*math.tau/40;b=(i+1)*math.tau/40
  rod('Court14_BackBasket',weave_point(a,h,.004*math.sin(i*math.pi/2+j*math.pi)),weave_point(b,h,.004*math.sin((i+1)*math.pi/2+j*math.pi)),.0054,'cane',5)
for off in (-.066,.066):
 last=basket+V((.174,.38,off))
 for j in range(1,17):
  q=j/16;end=basket+V((.17+.087*math.sin(q*math.pi),.38-.288*q,off))
  rod('Court14_BackBasket',last,end,.009,'twine',7);last=end
for idx in range(7):
 a=idx*2.399;stem=basket+V((.065*math.cos(a),.37,.071*math.sin(a)))
 end=stem+V((.092*math.cos(a),.09+rng.random()*.06,.077*math.sin(a)))
 rod('Court14_BasketGreens',stem,end,.004,'shoot')
 for j in range(4):
  leaf_mid=stem.lerp(end,.30+j*.16);tip=leaf_mid+V((math.cos(a+j)*.054,.040,math.sin(a+j)*.052))
  chord=leaf_mid.lerp(tip,.48);wide=V((-.025*math.sin(a+j),.009,.023*math.cos(a+j)))
  for fin in [[leaf_mid,chord+wide,tip],[leaf_mid,tip,chord-wide]]:
   face('Court14_BasketGreens',fin,'tip' if j>1 else 'ivy');face('Court14_BasketGreens',fin[::-1],'ivy')
solid((basket.x,bottom+.19,basket.z),(.33,.38,.27),0)

