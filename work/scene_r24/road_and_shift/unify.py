"""Remove the elevated courtyard walking ribbon wherever the original terrain supports it.
All path colour changes are painted on the surviving street surface in world coordinates.
True stairs, raised courts, building floors and road bridges keep their structural geometry.
"""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
work=here.parents[1]
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import Surfaces,scene
out=work/'project/chongqing_godot_v05/assets/courtyard_grade'
out.mkdir(exist_ok=True)
terrain=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_Terrain_200m')])
strip=scene.objects['COL_Walk_Courtyard_approach_pavement']
trim=scene.objects['Walk_details_Courtyard_approach_stone']
foundation=scene.objects['COL_R23_PathFoundations']
changed=[];retired=[];tops=[];before=[]
# At the market flank the old square yard datum formed a narrow depression in the
# public passage. Grade its existing vertices between the plinth and planter.
def ease(t):
 t=min(1.,max(0.,t));return t*t*(3.-2.*t)
graded={}
# Build terrain samplers before mutating shared datum vertices.
for ob in scene.objects:
 if ob.type=='MESH' and not ob.hide_render and ob.name.startswith('COL_Terrain_200m'):terrain.tree(ob)
for ob in scene.objects:
 if ob.type!='MESH' or not ob.name.startswith('COL_Terrain_200m_'):continue
 count=0
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co;x,y,z=p;along=-y
  weight=ease((x+28.0)/1.20)*ease((-23.85-x)/.8)*ease((along-28)/1.7)*ease((39.4-along)/2.15)
  court=ease((x+50)/2.1)*ease((-20.4-x)/1.8)*ease((along-17.55)/.78)*ease((22.95-along)/.76)
  if court>0:
   # A flush crossfall through the former deck; match the two untouched banks.
   high=terrain.down(x,-17.54,19,4);low=terrain.down(x,-22.96,19,4)
   if high and low:
    t=(along-17.54)/5.42
    target=high[0][0]*(1-t)+low[0][0]*t
    if abs(target-z)<.37:p.z+=(target-z)*court;v.co=ob.matrix_world.inverted()@p;count+=1
  if weight<=0:continue
  grade=14.15+.137*(38-along)+.024*(x+25)
  if grade-z<.015 or grade-z>1.9:continue
  p.z+=(grade-z)*weight
  v.co=ob.matrix_world.inverted()@p;count+=1
 if count:graded[ob.name]=count;ob.data.update();changed.append(ob.name)
terrain=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_Terrain_200m')])
def support(p):
 h=terrain.down(p.x,p.y,p.z+.58,1.3)
 return h[0][0] if h else None
def flush_ribbon():
 bm=bmesh.new();bm.from_mesh(strip.data);discard=[]
 for f in bm.faces:
  p=f.calc_center_median()
  pts=[v.co.copy() for v in f.verts]
  probes=[p]+[v.lerp(p,.03) for v in pts]
  hs=[support(v) for v in probes]
  if None in hs:continue
  if max(abs(a.z-b) for a,b in zip(probes,hs))>.68:continue
  tops.append(pts);discard.append(f);before.append(round(p.z-hs[0],4))
 bmesh.ops.delete(bm,geom=discard,context='FACES')
 commit(strip,bm)
def commit(o,bm):
 bm.to_mesh(o.data);bm.free();o.data.update()
 if len(o.data.polygons):changed.append(o.name)
 else:retired.append(o.name);o.hide_render=True;o.hide_set(True)
flush_ribbon()
verts=[];faces=[]
for ring in tops:
 idx=len(verts);verts.extend([(p.x,p.y,0) for p in ring]);faces.append(tuple(range(idx,len(verts))))
flat=BVHTree.FromPolygons(verts,faces)
def surface(p,margin):
 h,n,idx,d=flat.find_nearest((p.x,p.y,0),margin)
 if h is None:return None
 ring=tops[idx];a,b,c=ring[:3];normal=(b-a).cross(c-a)
 return a.z-(normal.x*(p.x-a.x)+normal.y*(p.y-a.y))/normal.z if abs(normal.z)>.000001 else None
counts={}
for ob,margin in [(trim,.17),(foundation,.055)]:
 bm=bmesh.new();bm.from_mesh(ob.data);discard=[]
 for f in bm.faces:
  p=f.calc_center_median();old=surface(p,margin)
  if (ob==trim and not len(strip.data.polygons)) or (old is not None and old-.85<p.z<old+.075):discard.append(f)
 counts[ob.name]=len(discard)
 bmesh.ops.delete(bm,geom=discard,context='FACES')
 commit(ob,bm)
# Keep drain frames, inset masonry seams and their paint on the same surviving face.
for ob in scene.objects:
 if ob.type!='MESH' or not ob.name.startswith(('Street_small_furniture_','Urban_paving_joints','District_surface_repairs')):continue
 bm=bmesh.new();bm.from_mesh(ob.data);remaining=set(bm.verts);moved=0
 while remaining:
  group=[remaining.pop()]
  for v in group:
   for e in v.link_edges:
    nxt=e.other_vert(v)
    if nxt in remaining:remaining.remove(nxt);group.append(nxt)
  if len(group)>80:continue
  p=sum((v.co for v in group),Vector())/len(group);old=surface(p,.05)
  if old is None or abs(p.z-old)>.075:continue
  h=support(p)
  if h is None:continue
  for v in group:v.co.z+=h-old
  moved+=1
 if moved:commit(ob,bm);counts[ob.name]=moved
 else:bm.free()
# Street furniture occupies its own pocket along the north market frontage.
# Keep the table top and settings rigid and fit each metal foot to the new slope.
def next_height(x,y,z):
 hits=terrain.down(x,y,z+2,4)
 if not hits:raise ValueError((x,y,z))
 return hits[0][0]
furniture={}
for ob in scene.objects:
 cafe=ob.name.startswith('CQF_CafeSet_') and ob.name.endswith('.001')
 waste=ob.name.startswith('Resident_waste_18_')
 if ob.type!='MESH' or not(cafe or waste):continue
 dx,dy=(-6.1,2.05) if cafe else (-3.4,1.2)
 ob.data=ob.data.copy()
 pts=[ob.matrix_world@v.co for v in ob.data.vertices]
 if cafe:
  cx,cy,old=-25.60,-39.27,14.144
 else:
  # Bin accessories share the datum of their parent bin. Bags and crate sit individually.
  if '_bin_' in ob.name:cx,cy,old=-26.2,-38.71,14.007
  else:cx=sum(q.x for q in pts)/len(pts);cy=sum(q.y for q in pts)/len(pts);old=min(q.z for q in pts)
 dz=next_height(cx+dx,cy+dy,old)-old
 foot=min(q.z for q in pts)
 frame=cafe and ('black_metal' in ob.name or 'steel' in ob.name)
 for v,p in zip(ob.data.vertices,pts):
  p.x+=dx;p.y+=dy
  if frame and p.z<foot+.065:
   p.z=next_height(p.x,p.y,old)+(p.z-foot)-.003
  else:p.z+=dz
  v.co=ob.matrix_world.inverted()@p
 ob.data.update();changed.append(ob.name);furniture[ob.name]=[dx,dy,dz]
# Old narrow joint meshes drew across the new continuous courses and caught highlights.
ob=scene.objects['District_surface_repairs_and_utilities_soil_dark']
bm=bmesh.new();bm.from_mesh(ob.data)
obsolete=[f for f in bm.faces if -49<f.calc_center_median().x<-21.5 and -21.6<f.calc_center_median().y<-17.9 and abs(f.calc_center_median().z-(16.45+.023*(f.calc_center_median().x+35)+.137*(f.calc_center_median().y+19.6)))<.42]
bmesh.ops.delete(bm,geom=obsolete,context='FACES')
bm.to_mesh(ob.data);bm.free();ob.data.update()
plan={'furniture':furniture,'retired_false_joints':len(obsolete),'graded_vertices':graded,'changed':[n.replace('.','_') for n in changed],'retired':retired,'removed_faces':len(tops),'relocated_or_removed':counts,'previous_offset_m':before}
(out/'layout.json').write_text(json.dumps(plan,indent=2),'utf8')
(here/'paint_polygons.json').write_text(json.dumps([[[p.x,-p.y] for p in ring] for ring in tops]),'utf8')
bpy.ops.object.select_all(action='DESELECT')
for key in changed:scene.objects[key].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'grade.glb'),use_selection=True,export_format='GLB',export_animations=False,export_image_format='NONE')
scene['street_revision']='R24 courtyard single-surface teaching ride'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_grade.blend'),compress=True,relative_remap=True)
print('COURT_GRADE',len(tops),counts,changed,retired,flush=True)
