# Verified source and original UVs are kept separately from the district donor.
from mathutils import Matrix
from shutil import copyfile
ginger_src=work/'assets_incoming/r24_noodle/ginger'
record=json.loads((ginger_src/'PROVENANCE.json').read_text('utf8'))
import hashlib
for item in record['files']:
    if hashlib.sha256((ginger_src/item['file']).read_bytes()).hexdigest()!=item['sha256']:raise ValueError(item['file'])
bpy.ops.import_scene.gltf(filepath=str(ginger_src/'food_ginger_01.gltf'))
ginger=next(o for o in bpy.context.selected_objects if o.type=='MESH')
geo=ginger.data;geo.transform(ginger.matrix_world);ginger.parent=None;ginger.matrix_world=Matrix.Identity(4)
# Align the scanned root's longest axis along the board. The supplier's vertical display pose was unsuitable.
import numpy as np
points=np.array([list(v.co) for v in geo.vertices])
axes=np.linalg.eigh(np.cov(points.T))[1][:,::-1].T.copy()
if np.linalg.det(axes)<0:axes[1]*=-1
geo.transform(Matrix.Rotation(.62,4,'Z')@Matrix(axes).to_4x4())
coords=[v.co.copy() for v in geo.vertices];lo=Vector([min(p[k] for p in coords) for k in range(3)]);hi=Vector([max(p[k] for p in coords) for k in range(3)])
scale=.169/max(hi.x-lo.x,hi.y-lo.y)
centre=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for v in geo.vertices:v.co=(v.co-centre)*scale+Vector((-23.324,-63.345,12.109715))
geo.update();ginger.name='D18_PhotoGinger';geo.name='D18_PhotoGinger'
for coll in list(ginger.users_collection):coll.objects.unlink(ginger)
collection.objects.link(ginger);layout['new'].append(ginger.name)
target=out/'ginger';target.mkdir(exist_ok=True)
for q in (ginger_src/'textures').glob('*.jpg'):copyfile(q,target/q.name)
layout['ginger']={'source':record['source'],'author':record['artist'],'license':record['license'],'support_blender_z':12.109715,'width_m':.169,'node':ginger.name}
