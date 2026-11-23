"""Audit the exported skinned GLB, including animation, in metre-scale Y-up space."""
import json,struct,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
revision=sys.argv[1] if len(sys.argv)>1 else 'r17'
assert revision in ['r17','r18']
p=ROOT/f'project/chongqing_godot_v05/assets/characters/shopkeeper_{revision}.glb'
with p.open('rb') as f:
    f.read(12);n,_=struct.unpack('<II',f.read(8));g=json.loads(f.read(n));n,_=struct.unpack('<II',f.read(8));blob=f.read(n)
def acc(i):
    a=g['accessors'][i];v=g['bufferViews'][a['bufferView']]
    dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
    cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    offset=v.get('byteOffset',0)+a.get('byteOffset',0);item=np.dtype(dtype).itemsize
    return np.ndarray((a['count'],cols),dtype=dtype,buffer=blob,offset=offset,strides=(v.get('byteStride',cols*item),item)).copy()
def matrix(node):
    if 'matrix' in node:return np.array(node['matrix']).reshape(4,4).T
    x,y,z,w=node.get('rotation',[0,0,0,1]);m=np.eye(4)
    m[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
    m[:3,:3]*=np.array(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m
def evaluate(name,t):
    nodes=json.loads(json.dumps(g['nodes']))
    anim=next(a for a in g['animations'] if a['name']==name)
    for channel in anim['channels']:
        sampler=anim['samplers'][channel['sampler']];times=acc(sampler['input']).ravel();values=acc(sampler['output'])
        k=max(0,min(len(times)-2,int(np.searchsorted(times,t,side='right'))-1));factor=min(1,max(0,(t-times[k])/max(1e-8,times[k+1]-times[k])))
        a,b=values[k],values[k+1]
        if channel['target']['path']=='rotation' and np.dot(a,b)<0:b=-b
        value=a*(1-factor)+b*factor
        if channel['target']['path']=='rotation':value/=np.linalg.norm(value)
        nodes[channel['target']['node']][channel['target']['path']]=value.tolist()
    matrices={}
    def visit(i,parent):
        matrices[i]=parent@matrix(nodes[i])
        for child in nodes[i].get('children',[]):visit(child,matrices[i])
    for root in g['scenes'][g.get('scene',0)]['nodes']:visit(root,np.eye(4))
    result=[]
    for i,node in enumerate(nodes):
        if 'mesh' not in node or i not in matrices:continue
        points=[]
        for primitive in g['meshes'][node['mesh']]['primitives']:
            attrs=primitive['attributes'];positions=acc(attrs['POSITION']);hom=np.column_stack([positions,np.ones(len(positions))])
            if 'skin' in node:
                skin=g['skins'][node['skin']];inverse=acc(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
                joints=acc(attrs['JOINTS_0']);weights=acc(attrs['WEIGHTS_0']);weights=weights/weights.sum(axis=1,keepdims=True)
                palette=np.array([matrices[j]@inverse[k] for k,j in enumerate(skin['joints'])]);posed=np.zeros_like(hom)
                for k in range(4):posed+=np.einsum('nij,nj->ni',palette[joints[:,k]],hom)*weights[:,k,None]
            else:posed=hom@matrices[i].T
            points.extend(posed[:,:3])
        a=np.array(points);result.append({'node':node.get('name',''),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()})
    return {'clip':name,'time':t,'lowest_y':min(x['min'][1] for x in result),'highest_y':max(x['max'][1] for x in result),'meshes':result}
results=[evaluate(c,t) for c,ts in [('idle',[0,.5,1,1.5,2,2.5,3,4,5,6,7,8,9,9.5,10]),('serve',[0,.5,1,1.5,2,2.5,3])] for t in ts]
(ROOT/f'audit/character_{revision}_glb_geometry.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps([{k:v for k,v in r.items() if k!='meshes'} for r in results],indent=2))
