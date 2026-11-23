from pathlib import Path
import json,hashlib,shutil,urllib.request
W=Path(__file__).resolve().parent;catalog=W/'assets_incoming/rocketbox_research';folder=W/'assets_incoming/r24_stall';folder.mkdir(exist_ok=True)
commit=(catalog/'COMMIT.txt').read_text(encoding='utf-8-sig').strip()
tree={p['path']:p for p in json.loads((catalog/'tree.json').read_text(encoding='utf8'))['tree']}
rows=[]
for name in ['f_idle_look_around_01','f_gestic_talk_neutral_02']:
    rel='Assets/Animations/all_animations_max_motextr_static/'+name+'.max.fbx';entry=tree[rel]
    url='https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/'+commit+'/'+rel
    dest=folder/rel.split('/')[-1];raw=dest.read_bytes() if dest.exists() else urllib.request.urlopen(url,timeout=35).read()
    assert len(raw)==entry['size'] and hashlib.sha1(bytes('blob %d'%len(raw),'ascii')+bytes(1)+raw).hexdigest()==entry['sha']
    dest.write_bytes(raw);rows.append(dict(file=dest.name,source=url,sha256=hashlib.sha256(raw).hexdigest(),git_blob=entry['sha']))
out=W/'scene_r24/assets'
shutil.copy2(catalog/'LICENSE.md',out/'Rocketbox_LICENSE.txt')
(out/'provenance.json').write_text(json.dumps(dict(commit=commit,authors='Microsoft Rocketbox contributors',license='MIT',notice='Copyright (c) 2020 Microsoft. Retain copyright and permission notice.',license_url='https://github.com/microsoft/Microsoft-Rocketbox/blob/'+commit+'/LICENSE.md',files=rows,modifications='Retargeted two standing clips to the existing Female_Adult_14 rig. Original storefront meshes, painted sign atlas and canopy. Existing source credits cover Noto CJK and concrete and timber scans.'),indent=2),encoding='utf8')

