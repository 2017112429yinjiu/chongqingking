from pathlib import Path
import json,struct
p=Path(__file__).resolve().parent/'project/chongqing_godot_v05/assets/characters/shopkeeper_r18.glb'
with p.open('rb') as f:
    f.read(12);n,_=struct.unpack('<II',f.read(8));g=json.loads(f.read(n))
for m in g['materials']:print(m['name'],json.dumps(m))
print('BROWS',[n['name'] for n in g['nodes'] if 'brow' in n.get('name','')])
print('CLIPS',[(a['name'],max(g['accessors'][s['input']]['max'][0] for s in a['samplers'])) for a in g['animations']])
for a in g['animations']:
    if a['name']!='idle':continue
    for ch in a['channels']:
        node=g['nodes'][ch['target']['node']]
        if node.get('name') in ['foot_l','foot_r']:
            ac=g['accessors'][a['samplers'][ch['sampler']]['output']]
            print('FOOT_CHANNEL',node['name'],ch['target']['path'],ac.get('min'),ac.get('max'),ac['count'])
