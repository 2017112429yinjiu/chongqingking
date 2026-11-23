"""Read just the editor's affected original mesh buffers without loading the city's textures."""
from pathlib import Path
import json,struct
here=Path(__file__).resolve().parent
project=here.parents[1]/'project/chongqing_godot_v05'
names=set(json.loads((project/'assets/lane_connection_r24/layout.json').read_text('utf8'))['source_nodes'])
with (project/'assets/chongqing_district.glb').open('rb') as source:
    length=struct.unpack_from('<I',source.read(20),12)[0];data=json.loads(source.read(length));source.read(8);start=source.tell()
    nodes=[n for n in data['nodes'] if n.get('name') in names and 'mesh' in n]
    out={'asset':{'version':'2.0'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':[],'meshes':[],'materials':[{'name':'EditorOriginal'}],'accessors':[],'bufferViews':[]}
    binary=bytearray();views={};accessors={}
    def access(index):
        if index in accessors:return accessors[index]
        meta=dict(data['accessors'][index]);k=meta['bufferView']
        if k not in views:
            view=dict(data['bufferViews'][k])
            source.seek(start+view.get('byteOffset',0));raw=source.read(view['byteLength'])
            binary.extend(b'\0'*(-len(binary)%4));view['byteOffset']=len(binary);binary.extend(raw)
            views[k]=len(out['bufferViews']);out['bufferViews'].append(view)
        meta['bufferView']=views[k];accessors[index]=len(out['accessors']);out['accessors'].append(meta);return accessors[index]
    for node in nodes:
        assert not any(k in node for k in ('matrix','translation','scale','rotation'))
        ps=[]
        for pr in data['meshes'][node['mesh']]['primitives']:
            ps.append({'attributes':{k:access(v) for k,v in pr['attributes'].items()},'indices':access(pr['indices']),'material':0})
        out['nodes'].append({'name':node['name'],'mesh':len(out['meshes'])})
        out['meshes'].append({'name':node['name'],'primitives':ps})
out['buffers']=[{'byteLength':len(binary)}];binary.extend(b'\0'*(-len(binary)%4))
encoded=json.dumps(out,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4)
with (here/'editor_base.glb').open('wb') as fp:
    fp.write(struct.pack('<4sIIII',b'glTF',2,len(encoded)+len(binary)+28,len(encoded),0x4E4F534A));fp.write(encoded)
    fp.write(struct.pack('<II',len(binary),0x004E4942));fp.write(binary)
print('EDITOR17_BASE',len(nodes),len(binary))
