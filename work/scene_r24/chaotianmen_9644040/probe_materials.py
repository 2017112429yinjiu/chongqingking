import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from study_mesh import *
from collections import Counter
print("streams",ole.listdir() if hasattr(ole,"listdir") else [d.name for d in ole.direntries if d])
print("MAT",Counter(reader.get_cls_name(records[r[-1]]) for r in rows if r[-1] and r[3]!="VRayProxy"))
try:
    reader.META_DATA=reader.read_chunks(ole,'FileAssetMetaData2',superId=0xA)
    print("META", str(reader.META_DATA[0].data)[:290])
except Exception as e: print("META",repr(e))
for mid,count in Counter(r[-1] for r in rows if r[-1] and r[3]!="VRayProxy").most_common(25):
    m=records[mid]; refs=reader.get_references(m); alt=reader.get_reference(m)
    print("M",mid,count,reader.get_cls_name(m),[(k,reader.get_cls_name(v) if v else None) for k,v in list(alt.items())[:9]],[(v.idx,reader.get_cls_name(v)) if v else None for v in refs[:6]])
    if reader.get_guid(m)==reader.VRAY_MTL:
        try: print("DIFF",reader.get_bitmap(alt.get(7)),reader.get_color(alt.get(1),1))
        except Exception as e: print("err",repr(e))
for r in rows:
    if "Camera" in r[3]: print("CAM",r[:5])

