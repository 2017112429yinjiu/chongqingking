"""Original enamel chilli bowl, oil, spoon, folded cloth and sealed side portion."""
from pathlib import Path
import bpy, math, random, json, hashlib
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'scene_r21/condiments'
GAME=ROOT/'project/chongqing_godot_v05/assets/counter_r21'
OUT.mkdir(exist_ok=True)
GAME.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.context.preferences.filepaths.save_version=0
rng=random.Random(456)

def mat(name, rgb, rough, metal=0):
    material=bpy.data.materials.new(name)
    material.use_nodes=True
    bs=material.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal
    return material

enamel=mat('Warm white enamel',(.64,.65,.51),.31)
rim=mat('Bottle-green enamel rim',(.018,.065,.051),.30)
steel=mat('Worn stainless spoon',(.50,.50,.46),.26,.83)
fabric=mat('Washed cotton',(.48,.43,.32),.95)
weft=mat('Red woven selvedge',(.26,.048,.035),.95)
oil=mat('Chilli oil and ground flake',(.39,.046,.012),.25)
plastic=mat('Frosted polypropylene lip',(.67,.63,.51),.35)
portion=mat('Oil visible through portion tub',(.35,.063,.021),.32)

def mesh(name,verts,faces,mats,indices=None,smooth=False):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    obj=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(obj)
    for m in mats:me.materials.append(m)
    for i,p in enumerate(me.polygons):
        p.use_smooth=smooth
        if indices:p.material_index=indices[i]
    return obj

def lathe(name,profile,mats):
    coords=[];faces=[];slots=[];n=72
    for r,z,slot in profile:
        coords.extend([(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n)])
    for j in range(len(profile)-1):
        for i in range(n):
            k=(i+1)%n
            faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
            slots.append(profile[j][2])
    return mesh(name,coords,faces,mats,slots,True)

cloth_z=.0028
bowl=lathe('Enamel oil bowl',[(.0001,cloth_z,0),(.036,cloth_z,1),(.037,.006,0),(.035,.01,0),
           (.049,.015,0),(.065,.029,0),(.076,.053,0),(.078,.061,1),(.080,.062,1),
           (.081,.064,1),(.080,.066,1),(.077,.066,1),(.075,.063,0),(.073,.054,0),
           (.061,.033,0),(.041,.020,0),(.0001,.019,0)],[enamel,rim])
# A curved meniscus uses radial UVs. Bake chilli flakes and seeds at millimetre scale.
n=512;yy,xx=np.mgrid[:n,:n];rr=np.random.default_rng(2712)
field=np.sin(xx*.021+np.sin(yy*.017)*2.4)+.6*np.cos(yy*.036+xx*.018)
base=np.zeros((n,n,4),dtype=np.float32);base[:,:,3]=1
for c,value in enumerate([.274,.038,.007]):base[:,:,c]=value*(1+.14*field)+rr.normal(0,.0015,(n,n))
for i in range(2750):
    x,y=rr.integers(8,n-8,2);a,b=rr.uniform(1.3,6),rr.uniform(.7,2.6);ang=rr.uniform(0,6.28)
    dy,dx=np.mgrid[-7:8,-7:8]
    shape=((dx*math.cos(ang)+dy*math.sin(ang))/a)**2+((dy*math.cos(ang)-dx*math.sin(ang))/b)**2
    alpha=np.clip((1.2-shape)*2.3,0,1)[:,:,None]*rr.uniform(.35,.85)
    shade=rr.choice([(.091,.011,.003),(.35,.046,.008),(.49,.118,.017),(.55,.257,.058)],p=[.47,.32,.16,.05])
    patch=base[y-7:y+8,x-7:x+8,:3];patch[:]=patch*(1-alpha)+np.array(shade)*alpha
image=bpy.data.images.new('Fried chilli in rapeseed oil',width=n,height=n,alpha=False)
image.pixels.foreach_set(np.clip(base,0,1).ravel());image.filepath_raw=str(OUT/'fried_chilli.png');image.file_format='PNG';image.save();image.pack()
node=oil.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
oil.node_tree.links.new(node.outputs['Color'],oil.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
surface=lathe('Chilli oil surface',[(.068,.0445,0),(.065,.0435,0),(.036,.0432,0),(.0001,.0432,0)],[oil])
uv=surface.data.uv_layers.new(name='Top')
for loop in surface.data.loops:
    x,y,z=surface.data.vertices[loop.vertex_index].co
    uv.data[loop.index].uv=(.5+x/.139,.5+y/.139)
# Pressed spoon with a dished, elliptical bowl and a slightly lifted handle.
vv=[(.012,.003,.041)];ff=[]
for j in range(1,7):
    r=j/6
    for i in range(36):
        a=math.tau*i/36;vv.append((.012+r*.019*math.cos(a),.003+r*.029*math.sin(a),.041+.008*r*r+.006*r*math.sin(a)))
        k=1+(j-1)*36+i;after=1+(j-1)*36+(i+1)%36
        ff.append((0,k,after) if j==1 else (k-36,k,after,after-36))
spoon=mesh('Dished ladle',vv,ff,[steel],smooth=True)
vv=[];ff=[]
for j in range(25):
    t=j/24;w=.0036+.0022*t+.0016*math.cos(t*6)
    x=.012+.030*t+.009*math.sin(t*math.pi);y=.027+.102*t;z=.054+.038*t+.010*math.sin(t*math.pi)
    vv.extend([(x-w,y,z),(x,y,z+.0014),(x+w,y,z)])
    if j:
        for k in [0,1]:
            i=j*3+k;ff.append((i-3,i-2,i+1,i))
handle=mesh('Pressed spoon handle',vv,ff,[steel],smooth=True)
for part in [spoon,handle]:
    m=part.modifiers.new('Steel thickness','SOLIDIFY');m.thickness=.0008
# Worn dishcloth under the bowl, with sewn stripes that continue over the turned edge.
vv=[];ff=[];idx=[];nx=43;ny=29
for j in range(ny):
    for i in range(nx):
        u=i/(nx-1);v=j/(ny-1);x=(u-.5)*.205;y=(v-.5)*.168
        edge=min(1,abs(x)/.079)**3
        z=.0016+.0008*edge*(1+math.sin(v*19+u*7))+.00045*math.sin(18*u-8*v)
        vv.append((x+.002*math.sin(v*5),y+.0015*math.sin(u*8),z))
        if i and j:
            k=j*nx+i;ff.append((k-nx-1,k-nx,k,k-1));idx.append(int(i in (3,5,6,37,38,40)))
towel=mesh('Folded striped cotton',vv,ff,[fabric,weft],idx,True)
m=towel.modifiers.new('Double cloth edge','SOLIDIFY');m.thickness=.0011
station=[bowl,surface,spoon,handle,towel]
cup=lathe('Sealed side portion',[(.0001,0,0),(.023,0,0),(.026,.002,0),(.030,.025,0),(.031,.028,1),
            (.033,.0285,1),(.033,.031,1),(.031,.032,1),(.028,.0324,1),(.027,.0315,1),(.024,.0312,0),(.0001,.0312,0)],[portion,plastic])
cup.location.x=.23  # Separate editable objects in the source file.
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'counter_condiments.blend'),compress=True)
for name,objects in [('chilli_station',station),('side_portion',[cup])]:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    if name=='side_portion':cup.location.x=0
    bpy.ops.export_scene.gltf(filepath=str(GAME/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
(GAME/'provenance.json').write_text(json.dumps({'geometry_and_texture':'Original project-authored Blender geometry and seeded oil texture.',
    'reference_only':'https://epaper.cqdsrb.com.cn/html/202601/06/content_513347.html','reference_use':'Reported condiment counter observed as contextual reference. No article text or imagery distributed.',
    'source_blend_sha256':sha(OUT/'counter_condiments.blend'),'oil_texture_sha256':sha(OUT/'fried_chilli.png'),
    'glb_sha256':{p.name:sha(p) for p in GAME.glob('*.glb')}},indent=2),encoding='utf8')
