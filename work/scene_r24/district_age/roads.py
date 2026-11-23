"""Retire two fully terrain-backed overlays, bed small street fixtures and reshape the actual fork."""
from pathlib import Path
import sys,json,bmesh,bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here))
from survey import scene,Surfaces,work
asset=work/'project/chongqing_godot_v05/assets/district_age'
terrain=Surfaces([o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Terrain_200m') and not o.hide_render])
mesh_keys=('OSM_1328811309_0','Old_school_approach','OSM_734116598_0')
changed=set();retired=set();rings=[];props={};support_gaps=[]
for key in mesh_keys:
    strip=scene.objects['COL_Walk_'+key+'_pavement']
    partial=key=='OSM_734116598_0'
    discard=[]
    for f in strip.data.polygons:
        pts=[strip.matrix_world@strip.data.vertices[i].co for i in f.vertices];c=strip.matrix_world@f.center
        if partial and min(v.x for v in pts)<46.998:continue
        discard.append(f.index)
        # Edges and interiors must have support. Recessed buildings and bridge gaps fail this rule.
        probes=[c]+[v.lerp(c,.018) for v in pts]+[(v+pts[(j+1)%len(pts)])*.49+c*.02 for j,v in enumerate(pts)]
        for p in probes:
            if abs(p.x)>99.997 or abs(p.y)>99.997:continue
            h=terrain.down(p.x,p.y,p.z+.6,1.28);assert h and abs(p.z-h[0][0])<.48,(key,list(p),h)
            support_gaps.append(p.z-h[0][0])
        rings.append(pts)
    if partial:
        for name in [strip.name,'Walk_details_'+key+'_stone']:
            ob=scene.objects[name];bm=bmesh.new();bm.from_mesh(ob.data)
            fs=[f for f in bm.faces if (f.index in discard if ob==strip else f.calc_center_median().x>=46.995)]
            bmesh.ops.delete(bm,geom=fs,context='FACES');bm.to_mesh(ob.data);bm.free();ob.data.update();changed.add(name)
        continue
    for name in [strip.name,'Walk_details_'+key+'_stone']:
        ob=scene.objects[name];ob.hide_render=True;ob.hide_set(True);retired.add(name)
from supported_runs import trim_supported
runs=trim_supported(scene,terrain,changed,rings,support_gaps)
terrain=Surfaces([o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_Terrain_200m') and not o.hide_render])
vs=[];faces=[]
for r in rings:
    n=len(vs);vs.extend([(p.x,p.y,0) for p in r]);faces.append(tuple(range(n,len(vs))))
flat=BVHTree.FromPolygons(vs,faces)
def old_surface(p,margin):
    h,_,i,_=flat.find_nearest((p.x,p.y,0),margin)
    if h is None:return None
    a,b,c=rings[i][:3];n=(b-a).cross(c-a)
    return a.z-(n.x*(p.x-a.x)+n.y*(p.y-a.y))/n.z
foundation=scene.objects['COL_R23_PathFoundations']
bm=bmesh.new();bm.from_mesh(foundation.data);remove=[]
for f in bm.faces:
    p=f.calc_center_median();z=old_surface(p,.045)
    if z is not None and z-.8<p.z<z+.05:remove.append(f)
bmesh.ops.delete(bm,geom=remove,context='FACES')
bm.to_mesh(foundation.data);bm.free();foundation.data.update();changed.add(foundation.name)
for ob in scene.objects:
    if ob.type!='MESH' or not ob.name.startswith(('Street_small_furniture_','Urban_paving_joints','District_surface_repairs')):continue
    bm=bmesh.new();bm.from_mesh(ob.data);remaining=set(bm.verts);n=0
    while remaining:
        group=[remaining.pop()]
        for v in group:
            for e in v.link_edges:
                v2=e.other_vert(v)
                if v2 in remaining:remaining.remove(v2);group.append(v2)
        if len(group)>95:continue
        p=sum((v.co for v in group),Vector())/len(group);old=old_surface(p,.085)
        if old is None or abs(p.z-old)>.105:continue
        hits=terrain.down(p.x,p.y,old+.5,1.2)
        if not hits:continue
        for v in group:
            # Individual ends follow the new grade; preserve relief over the local slab.
            deck=old_surface(v.co,.14);hit=terrain.down(v.co.x,v.co.y,old+.55,1.3)
            v.co.z+=(hit[0][0]-deck if hit and deck is not None else hits[0][0]-old)
        n+=1
    if n:
        bm.to_mesh(ob.data);ob.data.update();changed.add(ob.name);props[ob.name]=n
    bm.free()
# The eastern merge of the main-road shoulder copied a stair-shaped datum from its older neighbour.
# Relax complete cross-sections in the same mesh, leaving its actual welded outline at both ends.
ob=scene.objects['COL_D18_NanquShoulder']
rows={}
for v in ob.data.vertices:
    p=v.co
    if 39.0 < p.x <46.999:
        xs=round(p.x,3);ys=round(p.y,4);row=rows.setdefault(xs,{})
        row[ys]=max(row.get(ys,-100),p.z)
changes={}
for x,row in rows.items():
    ys=sorted(row)
    if len(ys)!=12:continue
    l,r=ys[1],ys[-1];blend=min(1.,(x-39)/3,(47-x)/.66)
    for y in ys[2:-1]:
        t=(y-l)/(r-l); smooth=t*t*(3-2*t);target=row[l]+(row[r]-row[l])*(.6*t+.4*smooth)
        changes[x,y]=(target-row[y])*blend
for v in ob.data.vertices:
    p=v.co;p.z+=changes.get((round(p.x,3),round(p.y,4)),0)
assert changes
ob.data.update();changed.add(ob.name)
road_record={'additional_runs':runs,'old_support_offset_range_m':[min(support_gaps),max(support_gaps)],'removed_top_faces':len(rings),'removed_base_faces':len(remove),'refit_fixtures':props,'shoulder_stations':len({k[0] for k in changes}),'max_shoulder_adjustment_m':max(abs(z) for z in changes.values())}
(here/'wear.json').write_text(json.dumps([[[p.x,-p.y] for p in r] for r in rings]),'utf8')
