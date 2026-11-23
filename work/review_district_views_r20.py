"""Verify same-camera roof and residential entrance images against the preceding lighting."""
from pathlib import Path
import json
import hashlib
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent
V=W/'project/chongqing_godot_v05/verification_r20'
d=V/'ambient_trial'
read=lambda f:json.loads(f.read_text())
sets=[]
for kind,version in [('overlook_full','R20_lane_11_internal'),('overlook_half','R20_lane_12_internal')]:
    folder=d/kind/'captures';manifest=read(folder/'capture_manifest.json')
    assert manifest['art_profile']['art_revision']==version and not manifest['failures']
    sets.append((folder,{r['view']:r for r in manifest['captures']}))
sheet=Image.new('RGB',(820,470));results={}
for i,name in enumerate(['roofscape','residential_entry']):
    frames=[];rows=[];hashes=[]
    for j,(folder,info) in enumerate(sets):
        row=info[name];path=folder/('godot_'+name+'.png')
        im=Image.open(path).convert('RGB')
        assert im.size==(1600,900)
        frames.append(np.asarray(im,dtype=np.int16));rows.append(row)
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
        im.thumbnail((410,230));sheet.paste(im,(410*j,235*i))
    assert all(rows[0][k]==rows[1][k] for k in ['position','target','fov','directional_shadow'])
    delta=np.abs(frames[0]-frames[1])
    results[name]={'source_image_sha256':hashes,'position':rows[1]['position'],'mean_abs_rgb_0_255':float(delta.mean()),
        'pct_pixels_with_max_channel_over_8':float(100*(delta.max(2)>8).mean())}
sheet.save(W/'audit/r20_12_roof_entrance.jpg',quality=89)
(d/'district_comparison.json').write_text(json.dumps(results,indent=2))
print('Checked',list(results))
