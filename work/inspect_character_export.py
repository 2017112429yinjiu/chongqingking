import json,struct,numpy as np
from pathlib import Path
f=(Path(__file__).resolve().parent/'project/chongqing_godot_v05/assets/characters/shopkeeper_r18.glb').open('rb');f.read(12);n,_=struct.unpack('<II',f.read(8));j=json.loads(f.read(n));n,_=struct.unpack('<II',f.read(8));blob=f.read(n)
for mesh in j['meshes']:
    if 'SoftApron' not in mesh['name']:continue
    for attr,idx in mesh['primitives'][0]['attributes'].items():
        if 'COLOR' not in attr:continue
        a=j['accessors'][idx];v=j['bufferViews'][a['bufferView']];c=4 if a['type']=='VEC4' else 3;dt={5126:'<f4',5121:'u1',5123:'<u2'}[a['componentType']]
        arr=np.ndarray((a['count'],c),dtype=dt,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dt).itemsize*c),np.dtype(dt).itemsize))
        print(attr,arr.min(0),arr.max(0),a['componentType'])
    print('material',j['materials'][mesh['primitives'][0]['material']])
