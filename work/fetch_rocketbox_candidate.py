"""Fetch one MIT-licensed avatar for isolated visual evaluation, not production."""
from pathlib import Path
import json,urllib.request,urllib.parse,hashlib,concurrent.futures,datetime
root=Path(__file__).resolve().parent/'assets_incoming/rocketbox_research'
tree=json.loads((root/'tree.json').read_text(encoding='utf-8-sig'))
commit=(root/'COMMIT.txt').read_text(encoding='utf-8-sig').strip()
name='Male_Adult_10';prefix=f'Assets/Avatars/Adults/{name}/'
files=[x for x in tree['tree'] if x['type']=='blob' and x['path'].startswith(prefix) and (x['path'].endswith('_facial.fbx') or '/Textures/' in x['path'] or x['path'].endswith('.png'))]
assert files and sum(x['size'] for x in files)<140_000_000
assert 'Copyright (c) 2020 Microsoft' in (root/'LICENSE.md').read_text() and 'MIT License' in (root/'LICENSE.md').read_text()
def fetch(entry):
    relative=entry['path'][len(prefix):];dest=root/name/relative;dest.parent.mkdir(parents=True,exist_ok=True)
    url=f'https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/{commit}/'+urllib.parse.quote(entry['path'])
    payload=urllib.request.urlopen(url,timeout=60).read()
    assert len(payload)==entry['size'],relative
    blob=hashlib.sha1(f'blob {len(payload)}\0'.encode()+payload).hexdigest()
    assert blob==entry['sha'],(relative,'Git blob hash mismatch')
    dest.write_bytes(payload)
    return {'file':str(dest.relative_to(root)),'source':url,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'git_blob_sha1':blob}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,files))
report={'status':'Downloaded for isolated evaluation only; not integrated into the game','source':'https://github.com/microsoft/Microsoft-Rocketbox','commit':commit,'license':'MIT','copyright':'Copyright (c) 2020 Microsoft','obligation':'Include full MIT copyright and permission notice with copies or substantial portions','authors':'Microsoft Rocketbox contributors; original avatars by Rocketbox team','modified':False,'animations_downloaded':False,'retrieved':datetime.datetime.now().astimezone().isoformat(),'files':results}
(root/'PROVENANCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'avatar':name,'files':len(results),'bytes':sum(x['bytes'] for x in results),'status':report['status']}))
