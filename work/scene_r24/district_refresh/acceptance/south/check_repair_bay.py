"""Measure the published/current GLBs without altering either Blender source."""
from hashlib import sha256, file_digest
import json
import math
import mmap
from pathlib import Path
import struct
import sys

import numpy as np


class Export:
    def __init__(self, path):
        self.stream = path.open('rb')
        self.data = mmap.mmap(self.stream.fileno(), 0, access=mmap.ACCESS_READ)
        length, = struct.unpack_from('<I', self.data, 12)
        self.doc = json.loads(self.data[20:20+length])
        self.binary = length+28
        self.nodes = {node['name']: node for node in self.doc['nodes'] if 'mesh' in node}

    def primitives(self, name):
        return self.doc['meshes'][self.nodes[name]['mesh']]['primitives']

    def accessor(self, index):
        a = self.doc['accessors'][index]
        view = self.doc['bufferViews'][a['bufferView']]
        typ = {5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
        n = {'SCALAR':1, 'VEC2':2, 'VEC3':3, 'VEC4':4}[a['type']]
        size = np.dtype(typ).itemsize
        offset = self.binary+view.get('byteOffset',0)+a.get('byteOffset',0)
        return np.ndarray((a['count'],n),typ,self.data,offset,(view.get('byteStride',n*size),size))

    def vertices(self, name, material=None):
        assert not {'translation','rotation','scale','matrix'} & self.nodes[name].keys(), name
        return np.concatenate([self.accessor(p['attributes']['POSITION']) for p in self.primitives(name)
                               if material is None or self.material(p).startswith(material)])

    def material(self, p):
        return self.doc['materials'][p['material']]['name'] if 'material' in p else ''

    def geometry(self, name):
        meshes = []
        for p in self.primitives(name):
            keys = sorted(p['attributes'])
            attrs = {key:sha256(self.accessor(p['attributes'][key]).tobytes()).hexdigest() for key in keys}
            attrs['indices'] = sha256(self.accessor(p['indices']).tobytes()).hexdigest()
            meshes.append({'material': self.material(p), **attrs})
        return meshes


def local(points, plot):
    c,s = math.cos(plot['bearing']),math.sin(plot['bearing'])
    en = points[:,[0,2]]*[1,-1]-plot['east_north']
    return np.column_stack([en@[[c,-s],[s,c]],points[:,1]-plot['height']])


def bounds(points):
    return np.stack((points.min(axis=0),points.max(axis=0)))


def separation(one, other):
    distance = np.maximum(one[0,:2]-other[1,:2],other[0,:2]-one[1,:2])
    return float(np.linalg.norm(distance.clip(min=0))) if any(distance>0) else float(distance.max())


def record(path):
    with path.open('rb') as f:
        return {'path':str(path),'sha256':file_digest(f,'sha256').hexdigest(),'bytes':path.stat().st_size}


def main():
    layout, outer_path, parent_path, latest_path, report = map(Path, sys.argv[1:])
    plot = next(p for p in json.loads(layout.read_text())['plots'] if p['plot_id']==0)
    outer,parent,latest = (Export(path) for path in (outer_path,parent_path,latest_path))
    structure = local(outer.vertices('COL_Outer500_Frame_00'),plot)
    trim = local(outer.vertices('Outer500_Joinery_00','Limewash and worn oil dado'),plot)
    columns, cores = [], []
    for u in plot['frame']['u']:
        for v in plot['frame']['v']:
            zone = trim[(abs(trim[:,0]-u)<.22)&(abs(trim[:,1]-v)<.22)&(trim[:,2]<1.35)]
            core = structure[(abs(structure[:,0]-u)<.22)&(abs(structure[:,1]-v)<.22)
                             &(abs(structure[:,2]+.18)<.0001)]
            assert len(core)>=4, (u,v,len(core))
            if abs(u+2.04)<.001 and abs(v+1.75)<.001:
                assert len(zone)>=8
            columns.append(bounds(np.concatenate((zone,core))))
            cores.append(bounds(core)[:,:2].tolist())
    unchanged = sorted(name for name in parent.nodes if not name.startswith('Review00_'))
    assert unchanged == sorted(name for name in latest.nodes if not name.startswith('Review00_'))
    for mesh in unchanged:
        assert parent.geometry(mesh)==latest.geometry(mesh), mesh
    previous = local(parent.vertices('Review00_RepairBenchAndHandTools'),plot)
    old_top = bounds(previous[(previous[:,2]>.85-.001)&(previous[:,2]<.916)])
    current = local(latest.vertices('Review00_BayWorkbench'),plot)
    tabletop = bounds(current[current[:,2]>.8495])
    feet = current[current[:,2]<.10]
    legs = [bounds(feet[(feet[:,0]<-3.1 if left else feet[:,0]>-3.1)
                       &(feet[:,1]<-.52 if low else feet[:,1]>-.52)])
            for left in (True,False) for low in (True,False)]
    clearance = lambda box: min(separation(box,column) for column in columns)
    furniture = {name:bounds(local(latest.vertices(name),plot)) for name in latest.nodes
                 if name.startswith('Review00_') and name!='Review00_BayWorkbench'}
    assert clearance(old_top)<0 and clearance(tabletop)>.5 and min(map(clearance,legs))>.5
    assert all(clearance(box)>.35 for box in furniture.values())
    plan_name='acceptance-south.json'
    parent_plan, latest_plan = [json.loads((p.parent/plan_name).read_text()) for p in (parent_path,latest_path)]
    for key in ('retired_objects','replacement_meshes','borrowed_materials'):
        assert parent_plan[key]==latest_plan[key],key
    assert all(not name.startswith('COL_') for name in latest.nodes.keys()-parent.nodes.keys())
    floor = local(outer.vertices('Outer500_InteriorFloor_00'),plot)
    floor = bounds(floor[(floor[:,0]>-4.)&(floor[:,0]<-2.)&(floor[:,1]>-1)&(floor[:,1]<0)])
    # Existing timber counter lip in the adjoining bay, including its actual
    # collision owner. Sample vertices rather than inferring the gap from a photo.
    envelope = local(outer.vertices('COL_Outer500_Building_envelopes'),plot)
    expected = np.array([[u,v,z] for u in (-4.905,-2.475) for v in (-1.914,-1.394) for z in (.78,.86)])
    candidate = envelope[(envelope[:,0]>-5.02)&(envelope[:,0]<-2.4)
                          &(envelope[:,1]>-2.0)&(envelope[:,1]<-1.3)&(envelope[:,2]>.7)&(envelope[:,2]<.9)]
    lip = np.array([candidate[np.linalg.norm(candidate-point,axis=1).argmin()] for point in expected])
    assert max(np.linalg.norm(lip-expected,axis=1))<.0001
    counter_gap = separation(tabletop,bounds(lip))
    assert counter_gap>.50
    out = dict(inputs=[record(f) for f in (outer_path,parent_path,latest_path)],
               axes='Plot 00 u, v, up above the original building base, metres',
               column_cladding_bounds=[b.tolist() for b in columns], structural_column_plan_bounds=cores,
               previous_top_bounds=old_top.tolist(), previous_min_signed_column_gap_m=clearance(old_top),
               tabletop_bounds=tabletop.tolist(), tabletop_min_column_gap_m=clearance(tabletop),
               four_legs_bounds=[a.tolist() for a in legs], four_leg_min_gaps_m=list(map(clearance,legs)),
               accessories_min_gaps_m={name:clearance(box) for name,box in furniture.items()},
               visible_floor_in_bay_m=floor[:,2].tolist(),
               original_counter_lip_bounds=bounds(lip).tolist(), table_to_original_counter_gap_m=counter_gap,
               center_aisle_band_width_m=2*min(abs(b[0,0]) if b[0,0]>0 else abs(b[1,0]) for b in columns),
               unchanged_non_workshop_surfaces=unchanged,
               collision_meshes_verified_byte_identical=[name for name in unchanged if name.startswith('COL_')])
    report.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('previous_min_signed_column_gap_m','tabletop_min_column_gap_m',
                     'four_leg_min_gaps_m','accessories_min_gaps_m','center_aisle_band_width_m',
                     'collision_meshes_verified_byte_identical','visible_floor_in_bay_m','table_to_original_counter_gap_m')}))


if __name__=='__main__':
    main()
