"""Assemble the baked distant foliage atlas and measure the new lighting HDRI."""
from pathlib import Path
from PIL import Image
import shutil,json,hashlib
import numpy as np
W=Path(__file__).resolve().parent
P=W/'project/chongqing_godot_v05/assets'
A=P/'district_r21';A.mkdir(exist_ok=True)
S=W/'scene_r21/canopy'
atlas=Image.new('RGBA',(448*4,448*2))
for row in range(2):
    for col in range(4):
        img=Image.open(S/f'{row}_{col}.png').convert('RGBA')
        atlas.paste(img,(col*448,row*448))
atlas.save(A/'canopy_atlas.png')
sky='kloofendal_28d_misty_puresky'
root=W/'assets_incoming/district_r21'
stone=root/'sandstone_cracks/sandstone_cracks_diff_2k.jpg'
if stone.exists():
    raw=np.asarray(Image.open(stone).convert('RGB'),dtype=np.float32)/255
    lum=raw@np.array([.24,.59,.17])
    tint=np.clip(lum[:,:,None]*[.79,.80,.767]+.045*(raw-lum[:,:,None]),0,1)
    Image.fromarray((tint*255).astype('uint8')).save(W/'scene_r21/washed_sandstone.jpg',quality=95)
hdr=next((root/sky).glob('*.hdr'));shutil.copy2(hdr,P/'sky'/hdr.name)
profile=json.loads((P/'render_profile_r20.json').read_text(encoding='utf8'))
profile['art_revision']='R21_district_07_internal'
profile['district_r21']=True
profile['lighting'].update(hdri_path='res://assets/sky/'+hdr.name,hdri_energy=.88,ambient_energy=.61,
    background_energy=.83,sun_energy=.88,sun_color=[1,.94,.85],sun_rotation_deg=[-28.56445,62,0],
    hdri_rotation_deg=[0,51.18945,0],sun_angular_distance=2.05,fog_density=.00072,fog_color=[.62,.69,.73],
    fog_light_energy=.59,fog_aerial_perspective=.16,fog_sky_affect=.075)
(P/'render_profile_r21.json').write_text(json.dumps(profile,indent=2,ensure_ascii=False),encoding='utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
old=W/'project/chongqing_blender_v05/scanned_assets'
(A/'provenance.json').write_text(json.dumps({'imports':[json.loads((root/name/'PROVENANCE.json').read_text(encoding='utf8')) for name in ['mossy_stone_wall','sandstone_cracks',sky] if (root/name/'PROVENANCE.json').exists()],
 'existing_scans':[a for a in json.loads((old/'source_credits.json').read_text(encoding='utf8'))['assets'] if a['id'] in ['tree_small_02','island_tree_01','shrub_01']],
 'vegetation_source_library_sha256':sha(old/'prepared_assets.blend'),'canopy_atlas_sha256':sha(A/'canopy_atlas.png'),
 'modifications':'Two CC0 scan meshes rendered from four directions in Blender; alpha images assembled in one atlas for non-playable exterior trees. The same eight scan alpha images project fixed-sun ground shading in bake_exterior_sun_r21.py. The mossy masonry scan uses metre-based UVs. Sandstone Cracks diffuse desaturated and darkened, original OpenGL normal and roughness retained. The HDRI is copied byte-for-byte; brightest sample elevation 28.564 degrees, unrotated yaw 10.811 degrees. Panorama and sun rotate together.',
 'local_study':'Research only: pre-existing project photograph on the third Shancheng trail and city housing department Shancheng Lane record, https://zfcxjw.cq.gov.cn/zjzj/tszj/scbd/202211/t20221128_11339455.html. No reference-photo pixels in the game.'},indent=2,ensure_ascii=False),encoding='utf8')
