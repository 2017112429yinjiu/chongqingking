"""Measure the two exported rail corners in the locked 34 street eye."""
from hashlib import file_digest
from math import cos, radians, sin, tan
from pathlib import Path
import json
import struct
import sys

import numpy as np

HERE = Path(__file__).resolve().parent


def corners(path, name):
    raw=path.read_bytes()
    length,magic=struct.unpack_from('<I4s',raw,12)
    assert magic==b'JSON'
    asset=json.loads(raw[20:20+length])
    buffer=memoryview(raw)[28+length:]
    node=next(n for n in asset['nodes'] if n.get('name')==name)
    assert not any(k in node for k in ('rotation','translation','matrix','scale')),node
    rows=[]
    for part in asset['meshes'][node['mesh']]['primitives']:
        a=asset['accessors'][part['attributes']['POSITION']]
        view=asset['bufferViews'][a['bufferView']]
        assert a['type']=='VEC3' and a['componentType']==5126
        offset=view.get('byteOffset',0)+a.get('byteOffset',0)
        p=np.ndarray((a['count'],3),dtype='<f4',buffer=buffer,offset=offset,strides=(view.get('byteStride',12),4))
        rows.append(np.stack([p[:,0],-p[:,2],p[:,1]],axis=1))
    return np.concatenate(rows)


def sha(path):
    with path.open('rb') as stream:
        return file_digest(stream,'sha256').hexdigest()


def main(parent,child,report):
    site=json.loads((HERE/'corner-register.json').read_text())['34']
    control=site['stations'][0]
    theta=radians(control['heading'])
    horizontal=np.array([sin(theta),cos(theta)])
    right=np.array([cos(theta),-sin(theta)])
    e=np.array(site['eye'])
    target=np.array(site['measured_top']['enu'])
    width,height=control['pixels']
    focal=height*.5/tan(radians(control['fovy'])*.5)
    def project(p):
        delta=p-e
        a,b=float(delta[:2]@horizontal),float(delta[:2]@right)
        return dict(enu=p.tolist(),ahead_m=a,right_m=b,up_m=float(delta[2]),
                    pixel=[width*.5+b*focal/a,height*.5-float(delta[2])*focal/a])
    old=corners(parent,'Review34_FineBlackRails')
    within=old[((old[:,:2]-e[:2])@horizontal>0)&((old[:,:2]-e[:2])@horizontal<8)]
    before=within[np.argmax(within[:,2])]
    newer=corners(child,'Review34_CloseRegisteredBlackRailCorner')
    after=newer[np.argmin(np.linalg.norm(newer-target,axis=1))]
    assert np.linalg.norm(after-target)<.07
    result=dict(eye_enu=e.tolist(),observed_corner_pixel=control['rail_corner_pixel'],
                fitted_control=project(target),parent_geometry=project(before),current_geometry=project(after),
                parent_export_sha256=sha(parent),current_export_sha256=sha(child))
    report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,separators=(',',':')))


if __name__=='__main__':
    main(*map(Path,sys.argv[1:]))
