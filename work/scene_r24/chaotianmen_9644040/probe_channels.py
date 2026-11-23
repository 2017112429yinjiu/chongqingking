import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from study_mesh import *
for r in json.loads((STUDY/"bounds.json").read_text())[:12]:
 v,f,block=geom(r[1])
 print("UV",r[:5],[(hex(c.types),c.end-c.begin,struct.unpack_from("<I",buf,c.begin)[0] if c.end-c.begin>=4 and not c.container else 0) for c in block.children if c.types in (0x0924,0x0959,0x0916,0x0918,0x2394,0x2396)],flush=True)
reader.read_config(ole,str(MAX))
for c in reader.CONFIG:print("CFG",hex(c.types),str(c.data)[:60],[(hex(x.types),str(x.data)[:32]) for x in c.children[:4]])

