"""Reopen the actual saved files and independently ray-test decks and the river."""
from pathlib import Path
import bpy,json,hashlib,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parent;S=W/'scene_r22';P=W/'project/chongqing_godot_v05'
tag=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--run=')),'import01')
assert tag.isidentifier()
V=P/'verification_r22'/tag
V.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
roof=read(P/'assets/roofs_r22/layout.json');river=read(P/'assets/river_r22/layout.json')
for name,record in [('roofs_and_breakfast',roof),('river_context',river)]:
    assert sha(S/(name+'.blend'))==record['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(S/(name+'.blend')))
    assert len(bpy.context.scene.objects)>20
bpy.ops.wm.open_mainfile(filepath=str(S/'chongqing_district.blend'))
scene=bpy.context.scene
assert sha(S/'chongqing_district.blend')==river['city_sha256']
def tree(name):
    obj=bpy.data.objects[name];m=obj.data
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in m.vertices],[p.vertices[:] for p in m.polygons])
def zhit(bvh,x,y,above,travel):
    hit=bvh.ray_cast(Vector((x,y,above)),Vector((0,0,-1)),travel)[0]
    return hit.z if hit else None
decks={};samples=[]
for spec in roof['decks']:
    bvh=tree(spec['donor']);decks[spec['building']]=bvh
    cap=bpy.data.objects[spec['name']]
    for f in cap.data.polygons:
        p=cap.matrix_world@f.center;z=zhit(bvh,p.x,p.y,p.z+.03,.10)
        assert z is not None and abs(p.z-z-.014)<.002,(cap.name,p,z)
        samples.append(p.z-z)
stations=[]
for site in roof['stations']:
    x,y,z=site['anchor'];a=site['yaw'];w,h=site['clear_rect_m'];offset=[]
    for i in [-.5,0,.5]:
        for j in [-.5,0,.5]:
            xx=x+i*w*math.cos(a)-j*h*math.sin(a);yy=y+i*w*math.sin(a)+j*h*math.cos(a)
            raw=zhit(decks[site['building']],xx,yy,z+.12,.25);assert raw is not None
            offset.append(z-raw)
    assert max(abs(v-.014) for v in offset)<.002,site
    stations.append({'type':site['kind'],'support_samples':len(offset)})
wall=tree('COL_B_A01_noodle_plaster_ochre');sockets=[]
for q in roof['wall_sockets']:
    p=Vector(q);hit=wall.ray_cast(p+Vector((0,.15,0)),Vector((0,-1,0)),.3)[0]
    assert hit and (p-hit).length<.006;sockets.append((p-hit).length)
table=tree('R19_Breakfast_table_00');crocks=[]
for x,y,z in roof['dining_table']:
    hit=zhit(table,x,y,z+.10,.15)
    assert hit is not None and abs(z-hit)<.012,(x,y,z,hit)
    crocks.append(z-hit)
water=tree('R22_Water_sheet_river')
sand=tree('R22_Sandbar')
rings=read(P/'source_data/river_r22/river_plan.json')['rings']
shore=next(r['points'] for r in rings if r['role']=='inner')
crossings=[]
for a,b in zip(shore,shore[1:]+shore[:1]):
    ax,ay=a;bx,by=b;x,y=(ax+bx)*.5,(ay+by)*.5
    length=math.hypot(bx-ax,by-ay)
    if length<18:continue
    nx,ny=(by-ay)/length,(ax-bx)/length
    levels=[zhit(sand,x+s*nx,y+s*ny,0,35) for s in range(-12,13)]
    if not all(z is not None for z in levels):continue
    candidates=[i-11.5 for i in range(24) if (levels[i]+16)*(levels[i+1]+16)<=0]
    if candidates:crossings.append(min(candidates,key=abs))
assert len(crossings)>=20 and max(abs(v) for v in crossings)<6,crossings
banks=[tree(info['replacement']) for info in river['terrain'].values()]
upward_topography={}
for info in river['terrain'].values():
    obj=bpy.data.objects[info['replacement']]
    up=sum(face.normal.z>0 for face in obj.data.polygons)
    sides=sum(face.normal.z==0 and face.area>0 for face in obj.data.polygons)
    assert up>0 and up+sides==len(obj.data.polygons),(obj.name,up,sides,len(obj.data.polygons))
    upward_topography[obj.name]={'top':up,'vertical_seam':sides}
water_hits=[]
for axis in river['axes']:
    a=Vector(axis['north']);b=Vector(axis['south'])
    for i in range(3,19):
        t=i/20;p=a.lerp(b,t)
        x=p.x+18;y=-p.z;w=zhit(water,x,y,100,200)
        if w is None:continue
        bed=[v for bank in banks if (v:=zhit(bank,x,y,240,360)) is not None]
        assert bed and abs(w-river['river_level_m'])<.02,(x,y,w)
        water_hits.append({'surface_z':w,'terrain_z':max(bed),'deck_z':p.y+2.1*math.sin(math.pi*t)})
assert len(water_hits)>12
assert sum(h['terrain_z']<h['surface_z']-.15 for h in water_hits)>=.80*len(water_hits),water_hits
report={'scope':'Editable full city and both editable kits independently reopened; background game heights are art-directed.',
 'city_sha256':sha(S/'chongqing_district.blend'),'roof_layer_sha256':sha(S/'roofs_and_breakfast.blend'),'river_layer_sha256':sha(S/'river_context.blend'),
 'runtime_glbs':{},'objects':len(scene.objects),'packed_images':sum(bool(im.packed_file) for im in bpy.data.images),
 'deck_triangle_centres':len(samples),'deck_lift_range_m':[min(samples),max(samples)],'roof_stations':stations,'wall_socket_errors_m':sockets,'table_contact_errors_m':crocks,
 'river_cross_sections':water_hits,'mapped_sandbar_edge_offsets_m':crossings,'upward_terrain_faces':upward_topography,'bank_meshes':river['terrain'],'street_sightline':river['street_sightlines'][0]}
for folder,name,expected in [('roofs_r22','roofs_and_breakfast',roof['glb_sha256']),('river_r22','river_context',river['model_sha256'])]:
    value=sha(P/'assets'/folder/(name+'.glb'));assert value==expected;report['runtime_glbs'][name]=value
miss=[im.name for im in bpy.data.images if im.users and im.filepath and not im.packed_file];assert not miss,miss
(V/'blender_audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('AUDITED',len(samples),len(stations),len(water_hits),report['objects'])
