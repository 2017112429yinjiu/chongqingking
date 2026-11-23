"""Retrieve a single district resident and two seated actions at the project's pinned Rocketbox revision."""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import shutil
import urllib.parse
import urllib.request

W = Path(__file__).resolve().parent
catalog = W/'assets_incoming/rocketbox_research'
out = W/'assets_incoming/court_resident'
out.mkdir(exist_ok=True)
commit = (catalog/'COMMIT.txt').read_text(encoding='utf-8-sig').strip()
items = json.loads((catalog/'tree.json').read_text(encoding='utf-8-sig'))['tree']
base = 'Assets/Avatars/Adults/Female_Adult_14/'
motions = {'f_sit_chair_idle_neutral_01.max.fbx', 'f_sit_chair_idle_look_around.max.fbx'}
selected = [item for item in items if item['type']=='blob' and (
    (item['path'].startswith(base) and (item['path'].endswith('_facial.fbx') or '/Textures/' in item['path'])) or
    (item['path'].startswith('Assets/Animations/') and Path(item['path']).name in motions))]
assert len(selected)>=7 and all(not item['path'].endswith('.exe') for item in selected)

def fetch(item):
    name = Path(item['path']).name
    url = 'https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/'+commit+'/'+urllib.parse.quote(item['path'])
    target = out/name
    for attempt in range(3):
        try:
            data = target.read_bytes() if target.exists() else urllib.request.urlopen(url, timeout=45).read()
            assert len(data)==item['size'] and hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==item['sha'], name
            target.write_bytes(data)
            return {'name':name,'source':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        except OSError:
            if attempt==2: raise
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    files = list(pool.map(fetch,selected))
shutil.copy2(catalog/'LICENSE.md',out/'LICENSE.md')
record={'model':'Female_Adult_14','provider':'Microsoft Rocketbox','commit':commit,'license':'MIT','notice':'Copyright (c) 2020 Microsoft. Include full MIT copyright and permission notice.','license_url':'https://github.com/microsoft/Microsoft-Rocketbox/blob/'+commit+'/LICENSE.md','files':files,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(out/'provenance.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(len(files),'source files verified',flush=True)
