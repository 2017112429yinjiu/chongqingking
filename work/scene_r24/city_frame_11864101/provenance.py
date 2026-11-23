import json,re,hashlib,collections
from pathlib import Path
p=Path(__file__).resolve().parent
def digest(path):
    with path.open("rb") as f:return hashlib.file_digest(f,'sha256').hexdigest()
assets={}
for d,archive in [(p,'11864101_058ccbc9956406e8ca5e7fe507ef9785.rar'),(p.parent/'chaotianmen_9644040','9644040_cb90eebcb147404ccf43c795e9863eaa.rar')]:
    orig=Path.home()/'Downloads'/archive;source=list((d/'source').iterdir());model=next(f for f in source if f.suffix=='.max')
    raw=(d/'metadata/FileAssetMetaData2').read_bytes()
    refs=set()
    for offset in (0,1):
        refs.update(s.lower() for s in re.findall(r"3d66model-\d+-files-\d+\.[a-z0-9]+",raw[offset:].decode('utf-16le',errors='ignore'),re.I))
    names={f.name.lower() for f in source}
    summary=(d/'metadata/[5]DocumentSummaryInformation').read_bytes()
    stats=[x.decode('ascii') for x in re.findall(rb'[\x20-\x7e]{5,}',summary) if x.startswith((b'Vertices:',b'Faces:',b'Objects:',b'3ds Max Version:',b'Build:'))]
    assets[archive]={"source":"user supplied Downloads archive, 3d66 ID in file names","author":"unconfirmed","commercial_game_grant":"unconfirmed","attribution_terms":"unconfirmed","review":"local model geometry only, no source image textures copied to playable project","archive_bytes":orig.stat().st_size,"archive_sha256":digest(orig),"max_sha256":digest(model),"max_bytes":model.stat().st_size,"source_files":len(source),"saved_scene_summary":stats,"numbered_external_names":len(refs),"missing_numbered_names":sorted(refs-names)}
assets['geo_controls']={"source":["https://api.openstreetmap.org/api/0.6/way/589752618/full.json","https://api.openstreetmap.org/api/0.6/way/230583762/full.json"],"authors":"© OpenStreetMap contributors","license":"ODbL-1.0","changes":"Local EN projection and landmark controls; preserve original OSM API responses with study."}
assets['tool']="Blender 4.3.2 / Blender Extensions Autodesk MAX importer 1.9.2 / Godot 4.6.3"
(p/"sources.json").write_text(json.dumps(assets,ensure_ascii=False,indent=2),encoding="utf8")
print(str([(k,v.get('archive_sha256')) for k,v in assets.items() if isinstance(v,dict)])[:310])

