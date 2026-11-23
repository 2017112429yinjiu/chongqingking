"""Spatially split the unchanged high-detail meter triangles for per-cabinet visibility."""
from pathlib import Path
import struct,json,hashlib
import numpy as np
W=Path(__file__).resolve().parent
P=W/'project/chongqing_godot_v05/assets'
out=P/'lane_r20'
sites=json.loads((W/'audit/r20_meter_sites.json').read_text())
centers=np.asarray([s['center'] for s in sites],dtype='<f4')
selected=['R17_Meter_Details_'+suffix for suffix in ('dark','aluminium','offwhite','meter_oxide')]
tree={'asset':{'version':'2.0','generator':'Chongqing district / spatial meter detail'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'buffers':[],'bufferViews':[],'accessors':[]}
binary=bytearray(); groups=[[] for _ in sites];expected=0;actual=0;max_radius=0.;max_error=0.
def add_array(a,kind,component,mode):
    while len(binary)%4:binary.append(0)
    a=np.ascontiguousarray(a)
    entry={'buffer':0,'byteOffset':len(binary),'byteLength':a.nbytes,'target':mode}
    tree['bufferViews'].append(entry);binary.extend(a.tobytes())
    accessor={'bufferView':len(tree['bufferViews'])-1,'componentType':component,'count':len(a),'type':kind}
    if mode==34962 and kind=='VEC3':
        accessor.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
    tree['accessors'].append(accessor);return len(tree['accessors'])-1
def primitive(pos,norm,indices,mat):
    code=5123 if len(pos)<65536 else 5125
    return {'material':mat,'attributes':{'POSITION':add_array(pos.astype('<f4'),'VEC3',5126,34962),'NORMAL':add_array(norm.astype('<f4'),'VEC3',5126,34962)},'indices':add_array(indices.reshape(-1).astype('<u2' if code==5123 else '<u4'),'SCALAR',code,34963)}
with open(P/'chongqing_district.glb','rb') as f:
    f.seek(12);size,_=struct.unpack('<II',f.read(8));src=json.loads(f.read(size));f.read(8);offset=f.tell()
    def source_array(id):
        acc=src['accessors'][id];view=src['bufferViews'][acc['bufferView']]
        assert 'byteStride' not in view and 'sparse' not in acc
        dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[acc['componentType']]
        count={'VEC3':3,'SCALAR':1}[acc['type']]
        f.seek(offset+view.get('byteOffset',0)+acc.get('byteOffset',0))
        return np.frombuffer(f.read(acc['count']*count*np.dtype(dtype).itemsize),dtype=dtype).reshape(-1,count)
    for slot,name in enumerate(selected):
        node=next(n for n in src['nodes'] if n['name']==name)
        assert set(node)<={'extras','mesh','name'}
        prim,=src['meshes'][node['mesh']]['primitives']
        material=src['materials'][prim['material']]
        assert 'Texture' not in json.dumps(material)
        tree['materials'].append(material)
        pos=source_array(prim['attributes']['POSITION']);nor=source_array(prim['attributes']['NORMAL'])
        triangles=source_array(prim['indices']).reshape(-1,3);expected+=len(triangles)
        midpoint=pos[triangles].mean(axis=1)
        bins=[]
        for start in range(0,len(midpoint),4096):
            delta=midpoint[start:start+4096,None,:]-centers[None,:,:]
            bins.append(np.argmin(np.einsum('ijk,ijk->ij',delta,delta),axis=1))
        owners=np.concatenate(bins)
        for i,c in enumerate(centers):
            subset=triangles[owners==i]
            if not len(subset):continue
            used,mapping=np.unique(subset,return_inverse=True)
            rebased=pos[used]-c
            max_error=max(max_error,float(np.abs(rebased+c-pos[used]).max()))
            max_radius=max(max_radius,float(np.linalg.norm(rebased,axis=1).max()))
            # These four materials use flat PBR parameters. UV and tangent seams
            # are redundant; weld only bit-identical relative positions and normals.
            pn=np.ascontiguousarray(np.concatenate([rebased,nor[used]],axis=1))
            packed,weld=np.unique(pn.view(np.dtype((np.void,24))).ravel(),return_inverse=True)
            vertices=packed.view('<f4').reshape(-1,6)
            groups[i].append(primitive(vertices[:,:3],vertices[:,3:],weld[mapping.ravel()],slot))
            actual+=len(subset)
def add_mesh(name,primitives,translation):
    tree['meshes'].append({'name':name,'primitives':primitives})
    tree['scenes'][0]['nodes'].append(len(tree['nodes']))
    tree['nodes'].append({'mesh':len(tree['meshes'])-1,'name':name,'translation':translation.tolist()})
def simplified(i):
    # Original cabinet enamel, LCD and rain hood remain in the base city.
    # At distance retain the face border, viewing recess, latch and vent lines.
    t=np.array(sites[i]['right']);n=np.array(sites[i]['front']);up=np.array([0.,1.,0.])
    pieces=[]
    for slot,faces in [(0,[(0,.030,0,.49,.67),(-.04,.059,.12,.278,.174)]+[(-.04,.047,-.16-j*.026,.23,.006) for j in range(5)]),(1,[(-.04,.053,.12,.31,.205),(.18,.067,-.035,.03,.10)])]:
        points=[];indices=[]
        for x,d,z,w,h in faces:
            k=len(points)
            points.extend(t*(x+sx*w/2)+n*d+up*(z+sz*h/2) for sx,sz in [(-1,-1),(1,-1),(1,1),(-1,1)])
            winding=[0,1,2,0,2,3] if np.dot(np.cross(t,up),n)>0 else [0,2,1,0,3,2]
            indices.extend(k+j for j in winding)
        pieces.append(primitive(np.array(points),np.tile(n,(len(points),1)),np.array(indices),slot))
    return pieces
assert actual==expected and max_error<.00001 and max_radius<.51,(actual,expected,max_error,max_radius)
for i,c in enumerate(centers):
    assert len(groups[i])==4,(i,len(groups[i]))
    add_mesh(f'MeterClose_{i:03}',groups[i],c)
    add_mesh(f'MeterFar_{i:03}',simplified(i),c)
while len(binary)%4:binary.append(0)
tree['buffers']=[{'byteLength':len(binary)}]
document=json.dumps(tree,separators=(',',':')).encode()
document+=b' '*((-len(document))%4)
path=out/'meter_lods.glb'
with path.open('wb') as fp:
    fp.write(struct.pack('<4sII',b'glTF',2,28+len(document)+len(binary)))
    fp.write(struct.pack('<I4s',len(document),b'JSON')+document)
    fp.write(struct.pack('<I4s',len(binary),b'BIN\0')+binary)
report={'source_nodes':selected,'sites':len(sites),'original_triangles':expected,'close_triangles':actual,'max_rebase_error_m':max_error,'max_cabinet_radius_m':max_radius,'far_triangles_per_site':18,'asset_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(out/'meter_lods.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report,path.stat().st_size)
