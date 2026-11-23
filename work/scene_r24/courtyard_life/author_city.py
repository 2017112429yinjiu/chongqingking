"""Author courtyard and doorstep furnishings on the build 13 surface, in Godot metre coordinates."""
from pathlib import Path
import sys,json,math,random,bpy
from collections import defaultdict
from mathutils import Vector,Matrix
home=Path(__file__).resolve().parent;work=home.parents[1];assets=work/'project/chongqing_godot_v05/assets/courtyard_r24'
sys.path.insert(0,str(home.parent/'stair_neighborhood'))
from site_neighborhood import floors,Surfaces,extent
rng=random.Random(21114)
def V(p):return Vector(p)
def bl(p):return Vector((p[0],-p[2],p[1]))
def god(p):return [p.x,p.z,-p.y]
def ground(x,z):
 h=floors(x,-z)
 if not h:raise ValueError((x,z))
 return h[0][0]
def local(root,yaw,p):
 x,y,z=p;c=math.cos(yaw);s=math.sin(yaw)
 return root+V((c*x+s*z,y,-s*x+c*z))
coll=bpy.data.collections.new('R24_14_CourtyardLife');bpy.context.scene.collection.children.link(coll)
data=defaultdict(lambda:[[],[],[],[]]);materials={};solids=[];feet=[];actors=[];origins={}
def mat(n,color,rough=.75,metal=0,texture=None):
 m=bpy.data.materials.new('Court14_'+n);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texture),check_existing=True);tex.image.pack();m.node_tree.links.new(tex.outputs[0],p.inputs['Base Color'])
 materials[n]=m
src=home.parent/'street_photo_study/workday_surfaces'
mat('wood',(.2,.12,.053),texture=src/'timber.jpg');mat('cane',(.36,.24,.12),texture=src/'old_cane.jpg');mat('edge',(.23,.127,.052));mat('board',(.65,.45,.32),texture=home/'board.jpg');mat('tokens',(.65,.45,.32),texture=home/'chessmen.png')
for n,c,ro,me in [('iron',(.10,.103,.09),.68,.45),('enamel',(.45,.58,.55),.29,.28),('rim',(.08,.17,.17),.43,.4),('ceramic',(.79,.72,.56),.34,.1),('tea',(.11,.061,.026),.22,0),('chili',(.36,.026,.009),.66,0),('bean',(.11,.23,.057),.74,0),('shoot',(.27,.34,.115),.79,0),('ivy',(.059,.16,.046),.71,0),('tip',(.15,.26,.067),.66,0),('twine',(.26,.20,.10),.92,0),('paper',(.34,.33,.266),.94,0)]:mat(n,c,ro,me)
def face(obj,pts,m,uv=None):
 vs,fs,ms,us=data[obj];ix=len(vs);vs.extend([tuple(bl(p)) for p in pts]);fs.append(tuple(range(ix,ix+len(pts))));ms.append(m);us.append(uv)
def box(obj,c,size,material,yaw=0):
 a,b,d=[v*.5 for v in size];points=[local(V(c),yaw,(x,y,z)) for y in (-b,b) for x,z in [(-a,-d),(a,-d),(a,d),(-a,d)]]
 for idx in [(0,1,2,3),(7,6,5,4),(4,5,1,0),(5,6,2,1),(6,7,3,2),(7,4,0,3)]:face(obj,[points[i] for i in idx],material)
def rod(obj,a,b,r,m,n=8,r2=None):
 a,b=V(a),V(b);v=(b-a).normalized();u=v.orthogonal().normalized();w=v.cross(u);r2=r if r2 is None else r2
 rings=[[p+radius*(u*math.cos(i*math.tau/n)+w*math.sin(i*math.tau/n)) for i in range(n)] for p,radius in [(a,r),(b,r2)]]
 for i in range(n):j=(i+1)%n;face(obj,[rings[0][i],rings[0][j],rings[1][j],rings[1][i]],m)
 face(obj,rings[1],m);face(obj,rings[0][::-1],m)
def ring(obj,c,r,m,minor=.003,n=36):
 for i in range(n):
  a,b=[math.tau*j/n for j in [i,i+1]]
  rod(obj,V(c)+V((r*math.cos(a),0,r*math.sin(a))),V(c)+V((r*math.cos(b),0,r*math.sin(b))),minor,m,5)
def solid(center,sz,yaw):solids.append(dict(at=list(center),size=list(sz),yaw=yaw))
def furnishing(obj,center,yaw,w,d,h,chair):
 # Four legs are independently cut at the existing sloped paving.
 a=[local(center,yaw,(x*w*.40,0,z*d*.38)) for x,z in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 for v in a:
  g=ground(v.x,v.z);box(obj,(v.x,(g+h)*.5,v.z),(.038,h-g+.005,.038),'wood',yaw);feet.append([v.x,g,v.z])
 for i in range(4):
  u,v=a[i],a[(i+1)%4];rod(obj,(u.x,h-.082,u.z),(v.x,h-.082,v.z),.016,'edge',5)
 for i in range(3):
  pos=local(V((center.x,h-.015,center.z)),yaw,(0,0,d*(i-1)/3));box(obj,pos,(w,.03,d/3-.003),'wood',yaw)
 solid((center.x,h-.085,center.z),(w,.17,d),yaw)
def dish(obj,c,r,depth,m):
 # Open, rolled enamel interior. The rim and basin share the same circumference.
 levels=[(r*.56,0),(r*.75,.22*depth),(r*.94,.75*depth),(r,depth)]
 n=40;parts=[]
 for radius,dy in levels:
  parts.append([V(c)+V((radius*math.cos(i*math.tau/n),dy,radius*math.sin(i*math.tau/n))) for i in range(n)])
 for a,b in zip(parts,parts[1:]):
  for i in range(n):
   j=(i+1)%n;face(obj,[a[i],a[j],b[j],b[i]],m);face(obj,[b[i],b[j],a[j],a[i]],m)
 face(obj,parts[0][::-1],m);ring(obj,V(c)+V((0,depth,0)),r,'rim')
original=json.loads((home/'rest_contacts.json').read_text())
def pose_root(role,x,z,yaw):
 contacts=original[role]
 pts={k:local(V((x,0,z)),yaw,v) for k,v in contacts.items()}
 return max(ground(pts[k].x,pts[k].z)-pts[k].y for k in ['left','right'])
yaw=math.radians(76)
leaves=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.name.startswith(('Planted_tree_','N13_Greenery_')):continue
 low,high=extent(ob)
 if low[0]<-11 and high[0]>-18 and low[1]<-12 and high[1]>-18:leaves.append(ob)
foliage=Surfaces(leaves)
def leaf_clearance(center):
 smallest=5.
 for sign in [-1,1]:
  origin=local(center,yaw,(0,0,sign*.572));ground_y=ground(origin.x,origin.z)
  for dy in [.80,1.02,1.22,1.38]:
   pos=bl((origin.x,ground_y+dy,origin.z))
   for ob in leaves:
    hit=foliage.tree(ob).find_nearest(pos,smallest)
    if hit and hit[0] is not None:smallest=min(smallest,hit[3])
 return smallest
sites=sorted([(dx,dz) for dx in [0,-.25,-.5,-.75,-1.,-1.25] for dz in [0,-.24,-.48,-.72,.24]],key=lambda q:q[0]**2+q[1]**2)
original_center=V((-14.24,0,15.16));previous_clearance=leaf_clearance(original_center)
for dx,dz in sites:
 center=original_center+V((dx,0,dz));canopy_gap=leaf_clearance(center)
 if canopy_gap>=.48:break
else:raise RuntimeError('No clear place under the tree')
roots={}
for role,s in [('red',-1),('black',1)]:
 at=local(center,yaw,(0,0,s*.5715));angle=yaw+(math.pi if s==1 else 0);roots[role]=[at,angle,pose_root(role,at.x,at.z,angle)]
calibration_path=home/'fit_targets.json'

new_fit={}
common=max(roots['red'][2],roots['black'][2]);center.y=common;tabletop=common+.713
def actor(role,at,angle,common):
 fit=json.loads((home/(role+'_contacts.json')).read_text())['contacts'];at.y=common
 new_fit[role]={'root_y':at.y,'shifts':{}}
 for key,xx in [('left',.105),('right',-.117)]:
  sole=V(original[role][key]);delta=V((xx-sole.x,0,-.065))
  future=local(at,angle,sole+delta)
  delta.y=ground(future.x,future.z)-future.y
  new_fit[role]['shifts'][key]=list(delta)
 seat=local(at,angle,fit['seat']);mid=local(at,angle,(0,0,fit['seat'][2]))
 furnishing('Court14_Stools',mid,angle,.465,.32,seat.y+.002,True)
 targets={}
 for key in ['left','right']:
  pt=local(at,angle,fit[key]);targets[key]=ground(pt.x,pt.z)-pt.y
 actors.append(dict(role=role,at=list(at),yaw=angle,seat=list(seat),sole_adjust=targets))
for role,(root,angle,_) in roots.items():actor(role,root,angle,common)
furnishing('Court14_Table',center,yaw,.88,.59,tabletop,False)
# Actual printed board and 32 turned pieces.
board_y=tabletop+.012
def board_pt(x,y,z):return local(center,yaw,(x,y-common,z))
box('Court14_Table',board_pt(0,tabletop+.0055,0),(.46,.011,.50),'edge',yaw)
face('Court14_Table',[board_pt(x,board_y,z) for x,z in [(-.23,-.25),(-.23,.25),(.23,.25),(.23,-.25)]],'board',[(0,1),(0,0),(1,0),(1,1)])
pieces=[];labels='帥仕相俥傌炮兵將士象車馬砲卒'
for team in [0,1]:
 ranks=[('俥傌相仕帥仕相傌俥' if team==0 else '車馬象士將士象馬車',0),(' 炮     炮 ' if team==0 else ' 砲     砲 ',2),('兵 兵 兵 兵 兵' if team==0 else '卒 卒 卒 卒 卒',3)]
 for row,rk in ranks:
  for i,ch in enumerate(row):
   if ch==' ':continue
   rank=rk if team==0 else 9-rk
   name=('Court14_RedHorse' if team==0 else 'Court14_BlackHorse') if rk==0 and i==(1 if team==0 else 7) else 'Court14_Chessmen'
   p=board_pt((i-4)*.048,board_y,(rank-4.5)*.049);h=.013
   if name!='Court14_Chessmen':origins[name]=bl(p)
   rod(name,p,p+V((0,h-.002,0)),.0184,'edge',24,.0188)
   tile=labels.index(ch);vs=[];tex=[]
   for j in range(32):
    angle=-j*math.tau/32;x,z=math.cos(angle),math.sin(angle);vs.append(local(p,yaw,(.0188*x,h,.0188*z)))
    if team==1:x,z=-x,-z
    tex.append(((tile%7+.5+.485*x)/7,1-(tile//7+.5+.485*z)/2))
   face(name,vs,'tokens',tex);pieces.append([team,ch,i,rank])
for x,z in [(.312,-.14),(-.33,.156)]:
 cup=board_pt(x,tabletop,z);dish('Court14_Teacups',cup,.038,.072,'ceramic');rod('Court14_Teacups',cup+V((0,.055,0)),cup+V((0,.057,0)),.034,'tea',24)
moves={}
for role,token in [('red','Court14_RedHorse'),('black','Court14_BlackHorse')]:
 moves[token]=list(local(Vector(),roots[role][1],(.048,0,.098)))
# A resident trims vegetables beside the existing window rack, clear of the staircase.
wy=math.radians(-79);wr=V((-67.12,0,18.49));wr.y=pose_root('greens',wr.x,wr.z,wy);actor('greens',wr,wy,wr.y)
def wp(x,y,z):return local(wr,wy,(x,y,z))
cs=wp(-.035,0,.401);top=wr.y+.525
furnishing('Court14_VegetableStand',cs,wy,.66,.38,top,False)
for x,z,depth,r in [(-.161,.378,.054,.112),(.075,.319,.086,.104)]:
 base=wp(x,.526,z);dish('Court14_EnamelBowls',base,r,depth,'enamel')
 for i in range(24):
  px=base.x+rng.uniform(-r*.48,r*.48);pz=base.z+rng.uniform(-r*.38,r*.38);yy=base.y+depth*.50+i*.00078
  length=rng.uniform(.035,.078);a=rng.uniform(-.68,.68);delta=V((math.cos(a)*length,0,math.sin(a)*length));mid=V((px,yy,pz))
  rod('Court14_SnappedBeans',mid-delta,mid+V((0,.006,0)),.0036,'bean',6);rod('Court14_SnappedBeans',mid+V((0,.006,0)),mid+delta,.0034,'shoot',6,.0016)
pod=wp(-.16,.598-.004,.37);other=wp(.065,.622-.004,.313)
origins['Court14_SortingPod']=bl(pod);moves['Court14_SortingPod']=list(other-pod)
for edge in (-1,1):
 rod('Court14_SortingPod',pod,pod+V((.037*edge,-.003,.012*edge)),.0038,'bean',7,.0014)
visit=[]
for x,z in [(-70.65,31.1),(-70.57,28.6),(-70.1,25.8),(-69.55,23.4),(-69.04,21.35),(-68.6,20.15),(-68.34,19.42)]:
 visit.append([x,ground(x,z),z])
calibration_path.write_text(json.dumps(new_fit,indent=2))
# Narrow climbing bean trellis tied to a planted pot on the existing household rack.
base=V((-66.81,16.62478,16.69))
for dx in [-.102,.102]:rod('Court14_Trellis',base+V((dx,.11,0)),base+V((dx,.85,-.10)),.008,'cane')
for h in [.30,.49,.69,.83]:
 rod('Court14_Trellis',base+V((-.12,h,-h*.105)),base+V((.12,h,-h*.105)),.0055,'cane')
 for dx in [-.102,.102]:rod('Court14_Trellis',base+V((dx-.010,h-.007,-h*.104-.005)),base+V((dx+.010,h+.010,-h*.104-.005)),.003,'twine')
for branch in range(3):
 last=base+V(((branch-1)*.066,.135,.008))
 for j in range(1,15):
  h=.135+j*.050;pos=base+V(((branch-1)*.066+.028*math.sin(j*.72+branch),h,-h*.109+.02*math.cos(j)))
  rod('Court14_Climber',last,pos,.0023,'ivy',5)
  side=(-1 if (j+branch)%2 else 1);length=.045+rng.random()*.035;end=pos+V((side*length,.018,-.025))
  mid=pos.lerp(end,.51);width=V((-.007,.016,.017))
  for a,b in [(mid-width,end),(end,mid+width)]:
   pts=[pos,a,b];face('Court14_Climber',pts,'tip' if j>11 else 'ivy');face('Court14_Climber',pts[::-1],'ivy')
  last=pos
exec(compile((home/'window_and_basket.py').read_text('utf-8'),str(home/'window_and_basket.py'),'exec'))
# Replaced table and both old seats stay identifiable in the saved historical source.
for ob in bpy.context.scene.objects:
 if ob.name.startswith('N13_ChessFurniture'):ob.hide_render=True;ob.hide_viewport=True
new=[]
for name,(vs,fs,ms,uvs) in data.items():
 origin=origins.get(name,Vector());geometry=[tuple(Vector(p)-origin) for p in vs]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(geometry,[],fs);mesh.update();ob=bpy.data.objects.new(name,mesh);coll.objects.link(ob);ob.location=origin;new.append(ob)
 used=list(dict.fromkeys(ms))
 for m in used:mesh.materials.append(materials[m])
 layer=mesh.uv_layers.new(name='UVMap')
 for i,poly in enumerate(mesh.polygons):
  poly.material_index=used.index(ms[i])
  for idx,loop in enumerate(poly.loop_indices):
   co=Vector(vs[mesh.loops[loop].vertex_index]);norm=poly.normal
   layer.data[loop].uv=uvs[i][idx] if uvs[i] else ((co.x*.8,co.y*.75) if abs(norm.z)>.6 else (co.y*.8 if abs(norm.x)>.6 else co.x*.8,co.z*.7))
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for ob in new:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(assets/'courtyard.glb'),export_format='GLB',use_selection=True,export_animations=False)
# Keep the animated resident sources linked in the whole editable district.
for spec in actors:
 with bpy.data.libraries.load(str(home/(spec['role']+'.blend')),link=True) as (source,dest):
  dest.objects=['WalkRig','StreetNeighbor']
 cast=bpy.data.collections.new('Court14_Ensemble_'+spec['role'])
 for item in dest.objects:
  if item:cast.objects.link(item)
 inst=bpy.data.objects.new('Court14_Resident_'+spec['role'],None);coll.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=cast;inst.location=bl(spec['at']);inst.rotation_euler.z=spec['yaw']
scene=bpy.context.scene;scene['street_revision']='R24 build 14 courtyard and west doorstep';scene.render.fps=12;scene.frame_set(0);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(home/'city_and_courtyard.blend'),compress=True,relative_remap=True)
layout={'canopy_clearance':[previous_clearance,canopy_gap],'center_shift':[center.x-original_center.x,center.z-original_center.z],'mounts':mounts,'moves':moves,'visit':visit,'actors':actors,'solids':solids,'feet':feet,'pieces':pieces,'board_center':list(center),'board_yaw':yaw,'board_surface':board_y,'motions':{k:god(v) for k,v in origins.items()}}
(assets/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
print('COURT14_CITY',actors,len(pieces),len(feet),flush=True)

