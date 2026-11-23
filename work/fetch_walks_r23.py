"""Retrieve the two walk cycles for the district's existing licensed adult meshes."""
from pathlib import Path
import hashlib, json, shutil, urllib.request

work=Path(__file__).resolve().parent
catalog=work/'assets_incoming/rocketbox_research'
dest=work/'assets_incoming/r23_walks'
dest.mkdir(exist_ok=True)
commit=(catalog/'COMMIT.txt').read_text(encoding='utf-8-sig').strip()
tree=json.loads((catalog/'tree.json').read_text(encoding='utf-8-sig'))['tree']
rows=[]
for name in ['f_walk_neutral_01.max.fbx','m_walk_stroll_01.max.fbx']:
    path='Assets/Animations/all_animations_max_motextr_xy/'+name
    item=next(r for r in tree if r['path']==path)
    url='https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/'+commit+'/'+path
    output=dest/name
    data=output.read_bytes() if output.exists() else urllib.request.urlopen(url,timeout=45).read()
    assert len(data)==item['size'] and hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==item['sha']
    output.write_bytes(data)
    rows.append({'file':name,'source':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
shutil.copy2(catalog/'LICENSE.md',dest/'LICENSE.txt')
(dest/'sources.json').write_text(json.dumps({'commit':commit,'license':'MIT','credit':'Copyright (c) 2020 Microsoft','files':rows},indent=2),encoding='utf8')
