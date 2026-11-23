"""Author the R22 roof and breakfast terrace layer on the preserved full R21 city."""
from pathlib import Path
import bpy
import hashlib
import json
import math
import random
import sys
from mathutils import Matrix,Vector

W=Path(__file__).resolve().parent;S=W/'scene_r22';P=W/'project/chongqing_godot_v05/assets/roofs_r22'
sys.path[:0]=[str(W),str(W/'project/chongqing_blender_v05')]
import district_geometry as geo
import district_layout as layout
from roof_fixtures_r22 import garden,drying,service,pergola

def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert 'R21_District_environment' in bpy.data.collections
city=bpy.context.scene
kit=bpy.data.collections.new('R22_Roofs_and_breakfast');city.collection.children.link(kit)
dg=bpy.context.evaluated_depsgraph_get()
sur=read(S/'survey.json');projection=read(S/'projection.json')
records={'decks':[],'stations':[],'wall_sockets':[],'dining_table':[]}
colors={'soil':(.057,.043,.032,.97,0),'brick':(.255,.137,.087,.93,0),'dullbrick':(.19,.113,.081,.9,0),
        'stone':(.221,.222,.204,.90,0),'greens':(.070,.135,.048,.86,0),'leaf':(.117,.226,.070,.83,0),
        'sage_leaf':(.157,.226,.103,.76,0),'bamboo':(.285,.212,.108,.80,0),'iron':(.084,.086,.075,.66,.49),
        'zinc':(.316,.324,.306,.52,.64),'tin':(.232,.292,.273,.62,.41),'cord':(.095,.081,.057,.92,0),
        'timber':(.20,.12,.068,.80,0),'terra':(.30,.136,.089,.84,0),'indigo':(.082,.130,.168,.94,0),
        'faded':(.36,.228,.176,.95,0),'linen':(.52,.486,.394,.93,0),'flask':(.168,.258,.200,.39,.19),
        'enamel':(.647,.634,.511,.36,.10),'black':(.058,.066,.056,.61,.31),'tea':(.093,.049,.019,.27,0)}
materials={k:geo.solid('R22_'+k,c[:3],c[3],c[4]) for k,c in colors.items()}
for k in ['greens','leaf','sage_leaf','linen','indigo','faded']:materials[k].use_backface_culling=False
geo.setup(materials)

def texture(name,file,rough):
    m=geo.solid(name,(.35,.34,.32),rough,0);m.use_backface_culling=False
    nt=m.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(file),check_existing=True)
    nt.links.new(tx.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
    return m

def sheet(name,points,faces,uvcoords,mat):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(points,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);kit.objects.link(obj);mesh.materials.append(mat)
    uvs=mesh.uv_layers.new(name='Authored UV')
    for loop in mesh.loops:uvs.data[loop.index].uv=uvcoords[loop.vertex_index]
    return obj

def ray(point,direction,distance):
    ok,p,n,_,o,_=city.ray_cast(dg,Vector(point),Vector(direction),distance=distance)
    return (p,o.name) if ok else (None,None)

def plan_station(key,role,count):
    rec=sur['roofs'][key];spec=projection[key];rng=random.Random('R22-'+key)
    points=rec['bounds'];top=rec['top'];u=Vector(spec['u']);v=Vector(spec['v']);base=spec['min'];extent=spec['span']
    desired={'garden':(8.7,5.8),'drying':(6.4,3.1),'service':(4.6,3.6)}[role]
    def candidate():
        a=base[0]+rng.uniform(0,extent[0]);b=base[1]+rng.uniform(0,extent[1])
        return u*a+v*b
    centres=[]
    for _ in range(2600):
        if len(centres)==count:break
        c=candidate()
        if any((c-q).length<max(desired)+2.3 for q in centres):continue
        w,h=desired
        corners=[c+u*(a*w/2)+v*(b*h/2) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        if not all(layout.point_in_poly(tuple(pt),points) for pt in corners):continue
        samples=[];clear=True
        for j in range(math.ceil(w/.6)+1):
            for k in range(math.ceil(h/.6)+1):
                pt=c+u*(w*(j/math.ceil(w/.6)-.5))+v*(h*(k/math.ceil(h/.6)-.5))
                hit,name=ray((*pt,top+5.8),(0,0,-1),5.9)
                if hit is None or name not in rec['decks'] or abs(hit.z-top)>.025:
                    clear=False;break
                samples.append(round(hit.z-top,5))
            if not clear:break
        if clear:
            centres.append(c);records['stations'].append({'building':key,'kind':role,'anchor':[c.x,c.y,top+.014],
                 'yaw':math.atan2(u.y,u.x),'clear_rect_m':[w,h],'roof_samples':len(samples),'offset_range_m':[min(samples),max(samples)]})
    if len(centres)!=count:raise RuntimeError(('insufficient clear space',key,role,len(centres)))

for key,role,count in [('1335306665','garden',2),('1413081560','drying',2),('809889622','drying',1),
                       ('A05','garden',1),('A07','service',1),('809889627','garden',1),
                       ('809889630','service',1),('809889623','drying',1),('1413081561','service',2)]:
    plan_station(key,role,count)

for x in [-32.15,-30.54,-28.78]:
    for z in [13.89,14.04]:
        p,name=ray((x,-60.30,z),(0,-1,0),2.1)
        assert name=='COL_B_A01_noodle_plaster_ochre' and abs(p.y+62)<.014,(p,name)
        records['wall_sockets'].append(list(p))
for x,y in [(-30.78,-60.95),(-30.78,-60.63),(-30.05,-60.56)]:
    p,name=ray((x,y,12.6),(0,0,-1),1.4)
    assert p and 'Breakfast_table' in name,(p,name)
    records['dining_table'].append(list(p))

for key,rec in sur['roofs'].items():
    proj=projection[key]; donor=next(name for name in rec['decks'] if name.endswith('details_concrete'))
    old=bpy.data.objects[donor]
    vv=[];faces=[];uv=[];area=0;top=rec['top']
    for poly in old.data.polygons:
        if poly.normal.z<.999 or abs((old.matrix_world@poly.center).z-top)>.03 or poly.area<=.1:continue
        ix=len(vv)
        for vi in poly.vertices:
            p=old.matrix_world@old.data.vertices[vi].co
            vv.append((p.x,p.y,p.z+.014));xy=Vector((p.x,p.y))
            uv.append(tuple((xy.dot(Vector(proj[k]))-proj['min'][d])/proj['span'][d] for d,k in enumerate(['u','v'])))
        faces.append(tuple(range(ix,ix+len(poly.vertices))));area+=poly.area
    name='R22_Deck_'+key
    sheet(name,vv,faces,uv,texture('R22 Roof '+key,S/'surfaces'/(key+'.jpg'),.87))
    records['decks'].append({'name':name,'building':key,'donor':donor,'area_m2':area,'tri_faces':len(faces),'top':top,'kind':proj['kind']})

design=read(S/'roof_stations_design.json')
for i,site in enumerate(records['stations']):
    assert site['building']==design[i]['building'] and (Vector(site['anchor'])-Vector(design[i]['anchor'])).length<.002
    site['kind']=design[i]['kind']
    b=geo.Batch('R22_'+site['kind']+'_'+str(i).zfill(2),kit)
    {'garden':garden,'drying':drying,'service':service,'pergola':pergola}[site['kind']](b,random.Random(418+i))
    matrix=Matrix.Translation(Vector(site['anchor']))@Matrix.Rotation(site['yaw'],4,'Z')
    for obj in b.finish():obj.matrix_world=matrix

# The breakfast bay is under a separate shutter. Hang the canvas below the
# existing green fascia and leave the counter approach and the roadway clear.
x0,x1=-32.39,-28.45;nx,ny=88,22
material=texture('R22 Woven awning',S/'surfaces/awning.jpg',.91)
vv=[];fs=[];uv=[]
for j in range(ny+1):
    t=j/ny
    for i in range(nx+1):
        s=i/nx
        z=14.01-.52*t-.145*math.sin(math.pi*t)+.018*math.sin(math.tau*7*s+.4*t)*t
        vv.append((x0+(x1-x0)*s,-61.94+2.23*t,z));uv.append((s,1.-t*.83))
        if i<nx and j<ny:
            a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
last=len(vv)
for j in range(5):
    for i in range(nx+1):
        s=i/nx;t=j/4;top=vv[ny*(nx+1)+i]
        vv.append((top[0],top[1]+t*.021+.019*t*math.sin(43*s),top[2]-t*(.18+.065*(.5-.5*math.cos(math.tau*7*s)))))
        uv.append((s,.17*(1-t)))
        if i<nx and j<4:
            a=last+j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
sheet('R22_Breakfast_canvas',vv,fs,uv,material)
b=geo.Batch('R22_Canopy_hardware',kit)
b.cylinder((x0-.055,-61.934,14.012),(x1+.055,-61.934,14.012),.057,'zinc',20)
b.cylinder((x0-.026,-59.725,13.466),(x1+.026,-59.725,13.466),.025,'iron',16)
for x in [-32.15,-30.54,-28.78]:
    b.box((x,-61.986,13.964),(.12,.048,.26),'iron')
    for z in [13.89,14.04]:
        b.cylinder((x,-61.969,z),(x,-61.945,z),.018,'zinc',8)
    b.pipe([(x,-61.92,13.91),(x+.27,-60.82,13.62),(x,-59.725,13.453)],.025,'iron',12)
    b.cylinder((x+.27,-60.82,13.59),(x+.27,-60.82,13.66),.044,'zinc',14)
b.pipe([(x0-.025,-61.87,13.99),(x0-.025,-61.82,13.74),(x0-.025,-61.72,13.69)],.015,'iron',10)
b.finish()

def body_of_revolution(batch,x,y,z,profile,mat,segments=36):
    vs=[(x+r*math.cos(i*math.tau/segments),y+r*math.sin(i*math.tau/segments),z+h) for h,r in profile for i in range(segments)]
    faces=[(k*segments+i,k*segments+(i+1)%segments,(k+1)*segments+(i+1)%segments,(k+1)*segments+i)
           for k in range(len(profile)-1) for i in range(segments)]
    batch.mesh(vs,faces,mat,True)

b=geo.Batch('R22_Breakfast_tea',kit)
x,y,z=records['dining_table'][0]
body_of_revolution(b,x,y,z,[(0,.076),(.018,.087),(.042,.094),(.265,.095),(.300,.087),(.334,.057),(.348,.055)],'flask')
for bottom,top,r in [(.019,.031,.090),(.29,.300,.090),(.341,.365,.060)]:
    b.cylinder((x,y,z+bottom),(x,y,z+top),r,'zinc',36)
body_of_revolution(b,x,y,z,[(.365,.059),(.391,.060),(.404,.048),(.406,0)],'black')
b.pipe([(x+.085,y,z+.273),(x+.151,y,z+.255),(x+.16,y,z+.165),(x+.147,y,z+.103),(x+.082,y,z+.11)],.013,'black',14)
for x,y,z in records['dining_table'][1:]:
    body_of_revolution(b,x,y,z,[(0,.035),(.008,.041),(.099,.048),(.103,.049),(.105,.045),(.013,.036)],'enamel',32)
    b.cylinder((x,y,z+.080),(x,y,z+.084),.044,'tea',32)
    b.pipe([(x+.044,y,z+.086),(x+.068,y,z+.091),(x+.075,y,z+.066),(x+.065,y,z+.039),(x+.043,y,z+.034)],.006,'enamel',12)
b.finish()

bpy.context.preferences.filepaths.save_version=0
bpy.context.view_layer.update()
bpy.ops.file.pack_all()
ks=bpy.data.scenes.new('R22 Roofs and breakfast');ks.collection.children.link(kit)
bpy.data.libraries.write(str(S/'roofs_and_breakfast.blend'),{ks},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
bpy.data.scenes.remove(ks)
bpy.ops.object.select_all(action='DESELECT')
for obj in kit.objects:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'roofs_and_breakfast.glb'),export_format='GLB',use_selection=True,export_apply=True)
city['revision']=22
city['composition']='Full R21 city with R22 editable deck surfaces, garden and drying areas, breakfast canopy and utensils. Daylight and exterior foliage shading use the Godot art profile.'
bpy.ops.wm.save_as_mainfile(filepath=str(S/'city_roofs.blend'),compress=True)
records.update(glb_sha256=sha(P/'roofs_and_breakfast.glb'),source_sha256=sha(S/'roofs_and_breakfast.blend'),city_sha256=sha(S/'city_roofs.blend'),
               prior_city_sha256=sha(W/'scene_r21/chongqing_district.blend'),mesh_objects=len(kit.objects))
(P/'layout.json').write_text(json.dumps(records,indent=2),encoding='utf8')
print('R22_BUILT',len(records['decks']),len(records['stations']),records['mesh_objects'])
