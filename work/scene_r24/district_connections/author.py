"""District pedestrian-height corrections, built from the complete 17b scene."""
from pathlib import Path
from collections import defaultdict
import bpy,bmesh,json,math,sys
from mathutils import Vector
here=Path(__file__).resolve().parent
work=here.parents[1]; project=work/'project/chongqing_godot_v05'; out=project/'assets/connections_r24'
out.mkdir(exist_ok=True)
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
sys.path.insert(0,str(work/'project/chongqing_blender_v05'))
from site_neighborhood import scene,extent,Surfaces,visible_ground,tread_rows
from mathutils.bvhtree import BVHTree
layout={'changed':[],'new':[],'stairs':[],'banks':[],'rooms':[],'drains':[],'benches':[]}
collection=bpy.data.collections.new('R24_18_StreetConnections');scene.collection.children.link(collection)
def mark(o):
    if o.name not in layout['changed']:layout['changed'].append(o.name)
def material(name,color,rough=.82,metal=0):
    m=bpy.data.materials.new('R18_'+name);m.diffuse_color=(*color,1.);m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=m.diffuse_color;b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    return m
mat={k:material(k,c) for k,c in {'stone':(.28,.26,.225),'paver':(.255,.248,.222),'mortar':(.21,.198,.17),'wall':(.43,.39,.315),'lime':(.66,.61,.50),'deepgreen':(.14,.19,.15),'redwood':(.19,.078,.038),'timber':(.36,.255,.15),'cement':(.29,.27,.225),'porcelain':(.68,.66,.55),'bluegrey':(.19,.24,.235),'iron':(.07,.073,.063),'ochre':(.56,.36,.17),'glass':(.26,.34,.32)}.items()}
batches={}
metric_uv={}
def face(name,ps,key):
    v,fs,ms=batches.setdefault(name,([],[],[]));idx=len(v);v.extend([tuple(p) for p in ps]);fs.append(tuple(range(idx,idx+len(ps))));ms.append(key)
def surface_face(name,ps,key,uv):
    ps=[Vector(q) for q in ps]
    if (ps[1]-ps[0]).cross(ps[2]-ps[0]).z<0:ps.reverse();uv=list(reversed(uv))
    face(name,ps,key);metric_uv[(name,len(batches[name][1])-1)]=uv
def topquad(name,ps,key):
    ps=[Vector(q) for q in ps]
    if (ps[1]-ps[0]).cross(ps[2]-ps[0]).z<0:ps.reverse()
    face(name,ps,key)
def box(name,c,size,key):
    x,y,z=c;a,b,h=(q*.5 for q in size);p=[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    for g in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[p[i] for i in g],key)
def publish():
    for name,(vs,fs,ms) in batches.items():
        me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
        keys=list(dict.fromkeys(ms))
        for key in keys:me.materials.append(mat[key])
        uv=me.uv_layers.new(name="SurfaceMetres")
        uv2=me.uv_layers.new(name="MasonrySetout") if name in ("COL_D18_StoneFlights","COL_D18_LaneShoulders","COL_D18_NanquShoulder") else None
        for poly,key in zip(me.polygons,ms):
            poly.material_index=keys.index(key);n=poly.normal
            for corner,li in enumerate(poly.loop_indices):
                if uv2:
                    values=metric_uv.get((name,poly.index));uv2.data[li].uv=values[corner] if values else (0,0)
                p=me.vertices[me.loops[li].vertex_index].co
                if name=='D18_SoupNotice':uv.data[li].uv=metric_uv[(name,poly.index)][corner];continue
                uv.data[li].uv=(p.x,p.y) if abs(n.z)>.55 else ((p.y,p.z) if abs(n.x)>abs(n.y) else (p.x,p.z))
        obj=bpy.data.objects.new(name,me);collection.objects.link(obj);layout['new'].append(name)
def finish(o,bm):
    bm.transform(o.matrix_world.inverted());bm.to_mesh(o.data);bm.free();o.data.update();mark(o)
def bounds(o):return extent(o)
def solid_clip(obj,domains):
    # Convex vertical prisms clip only intersecting triangles. Track every split face for subsequent neighbouring prisms.
    bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world)
    mins=[min(min(p[j] for p in ring) for ring,lo,hi in domains)-.015 for j in (0,1)]
    maxs=[max(max(p[j] for p in ring) for ring,lo,hi in domains)+.015 for j in (0,1)]
    def bbox(f):
        coords=[v.co for v in f.verts]
        return tuple(min(p[k] for p in coords) for k in range(3))+tuple(max(p[k] for p in coords) for k in range(3))
    def meets(a,b):
        return all(a[k]<=b[k+3]+1e-5 and a[k+3]>=b[k]-1e-5 for k in range(3))
    span=(*mins,min(q[1] for q in domains),*maxs,max(q[2] for q in domains))
    active={}
    for f in bm.faces:
        b=bbox(f)
        if meets(b,span):active[f]=b
    removed=0
    for ring,lo,hi in domains:
        ring=[Vector(p[:2]) for p in ring]
        if sum(a.x*b.y-b.x*a.y for a,b in zip(ring,ring[1:]+ring[:1]))<0:ring.reverse()
        b=(min(p.x for p in ring),min(p.y for p in ring),lo,max(p.x for p in ring),max(p.y for p in ring),hi)
        pool=[f for f,bb in active.items() if f.is_valid and meets(b,bb)]
        planes=[(Vector((a.x,a.y,0)),Vector((a.y-b.y,b.x-a.x,0)).normalized()) for a,b in zip(ring,ring[1:]+ring[:1])]
        planes.extend([(Vector((0,0,lo)),Vector((0,0,1))),(Vector((0,0,hi)),Vector((0,0,-1)))])
        for at,n in planes:
            new=[]
            for f in pool:
                if not f.is_valid:continue
                ds=[(v.co-at).dot(n) for v in f.verts]
                if max(ds)<-.000008:continue
                if min(ds)>=-.000008:new.append(f);continue
                if max(ds)<.000008:continue
                change=bmesh.ops.bisect_plane(bm,geom=[f,*f.edges,*f.verts],plane_co=at,plane_no=n,dist=.000001)
                parts={g for g in change['geom'] if isinstance(g,bmesh.types.BMFace) and g.is_valid}
                if f.is_valid:parts.add(f)
                for g in parts:
                    active[g]=bbox(g)
                    if (g.calc_center_median()-at).dot(n)>=-.000003:new.append(g)
            pool=list(set(new))
            if not pool:break
        if pool:
            removed+=len(pool)
            for f in pool:active.pop(f,None)
            bmesh.ops.delete(bm,geom=pool,context='FACES')
    if removed:finish(obj,bm)
    else:bm.free()
    return removed
def rect(x0,x1,y0,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
def gd(p):return [p[0],p[2],-p[1]]
survey=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_Terrain_200m_')])
def yard(x,y,z):
    hits=[h for h,n,_ in survey.down(x,y,z+.95,4) if abs(h-z)<2.]
    return max(hits) if hits else None
for key,col,r,m in [('steel',(.55,.55,.50),.34,.80),('duct',(.29,.31,.29),.53,.65),('stove',(.118,.145,.138),.50,.48),('knob',(.037,.036,.027),.49,.08),('rice',(.78,.76,.655),.27,.03),('ivory',(.66,.64,.52),.31,.03),('celadon',(.57,.63,.54),.34,.03),('grout',(.255,.26,.224),.86,0),('chili',(.41,.078,.032),.27,.04),('amber',(.26,.128,.043),.26,.07),('jar',(.22,.34,.23),.29,.05),('bamboo',(.42,.26,.116),.65,0),('wine',(.25,.063,.036),.54,.04),('indigo',(.078,.155,.214),.32,.04),('broth',(.33,.225,.092),.26,0),('opal',(.97,.84,.60),.38,0)]:
    mat[key]=material(key,col,r,m)
for key,col in {'oldstep':(.38,.36,.29),'oldtile':(.61,.61,.51),'skirt':(.20,.27,.215),'dado':(.56,.575,.49),'kitchenfloor':(.35,.305,.255),'formica':(.43,.52,.455),'stoolgreen':(.165,.30,.245),'brownware':(.245,.128,.056),'leaf':(.13,.31,.085),'scallion':(.25,.42,.145),'chilioil':(.53,.10,.035),'brine':(.43,.38,.12),'noodle':(.70,.59,.31),'noodleplaster':(.46,.445,.355),'agedtile':(.50,.508,.439),'workrag':(.44,.47,.42),'oiljug':(.38,.247,.068),'flask':(.38,.095,.058),'paintcream':(.56,.50,.39)}.items():
    mat[key]=material(key,col,.55,0)
for part in ('stairs','street','kitchen','interiors'):
    exec(compile((here/(part+'.py')).read_text('utf8'),str(here/(part+'.py')),'exec'))
exec(compile((here/'kitchen_bounce.py').read_text('utf8'),str(here/'kitchen_bounce.py'),'exec'))
subdivide_kitchen()
publish()
bake_kitchen_occlusion()
exec(compile((here/'ginger.py').read_text('utf8'),str(here/'ginger.py'),'exec'))
exec(compile((here/'source_finishes.py').read_text('utf8'),str(here/'source_finishes.py'),'exec'))
# Refit resident track elevations against the same top faces used by walking and rendering.
ground_trees=Surfaces([scene.objects[n] for n in ('COL_D18_NanquShoulder','COL_D18_StoneFlights','COL_D18_LaneShoulders')])
lanes=json.loads((project/'assets/neighborhood_r24/walk_lanes.json').read_text('utf8'))
layout['walk_adjustments']=[]
for route,lane in lanes.items():
    for direction in ('forward','backward'):
        for i,(x,y,z) in enumerate(lane[direction]):
            hits=ground_trees.down(x,-z,y+.85,1.68)
            if hits:
                top=hits[0][0]+.008
                if abs(top-y)>.004:layout['walk_adjustments'].append([route,direction,i,round(top,5)])
for source_name in list(layout['changed']):
    if not scene.objects[source_name].data.polygons:
        layout['changed'].remove(source_name);layout['retired'].append(source_name)
(out/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf8')
bpy.ops.object.select_all(action='DESELECT')
for name in layout['changed']+layout['new']:scene.objects[name].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'connections.glb'),use_selection=True,export_format='GLB',export_animations=False,export_image_format='NONE',export_vertex_color='ACTIVE')
scene['street_revision']='R24 build 18, stair turns, Nanqu shoulder, ball court and interiors'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_connections.blend'),compress=True,relative_remap=True)
print('CONNECTIONS18',len(layout['changed']),len(layout['new']),len(layout['stairs']),len(layout['drains']),flush=True)
