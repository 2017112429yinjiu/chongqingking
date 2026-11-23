from pathlib import Path
import struct,json
path=Path(__file__).resolve().parent/'characters/rider_r18_trial/godot/assets/rider.glb'
b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n])
for a in j.get('animations',[]):
    print(a['name'],[(j['accessors'][s['input']].get('min'),j['accessors'][s['input']].get('max')) for s in a['samplers'][:2]])
