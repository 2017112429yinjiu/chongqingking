"""Bind the junction's reused source maps, map-derived layout and original art to exact local files."""
from pathlib import Path
import hashlib,json,shutil
w=Path(__file__).resolve().parent;s=w/'scene_r24';p=s/'playtest'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
materials=[]
for name,author,asset in [
    ('brown_mud_leaves_01','Rob Tuytel','chongqing_district_brown_mud_leaves_01_diff_2k.jpg'),
    ('leaf_scattered_gravel','Dimitrios Savva','chongqing_district_leaf_scattered_gravel_diff_2k.jpg'),
    ('mossy_stone_wall','Amal Kumar','district_r21/terraces_mossy_stone_wall_diff_2k.jpg'),
    ('concrete_floor_worn_001','Dimitrios Savva, Rico Cilliers','street_r19/street_life_concrete_floor_worn_001_diff_2k.jpg'),
    ('asphalt_02','Rob Tuytel','chongqing_district_asphalt_02_diff_1k.jpg')]:
    materials.append(dict(name=name,author=author,url='https://polyhaven.com/a/'+name,license='CC0-1.0',local_input='assets/'+asset,sha256=sha(p/'assets'/asset),usage='Existing unchanged scan, mapped in metres on authored surfaces.'))
font=w/'assets_incoming/r20_noto'
layout=p/'source_data/geo_layout.json';d=json.loads(layout.read_text(encoding='utf8'))
record={'materials':materials,'lettering':{'name':'Noto Sans CJK SC','author':'Noto CJK project contributors','commit':(font/'source_commit.txt').read_text().strip(),'source':'https://github.com/notofonts/noto-cjk','license':'SIL OFL 1.1','notice':'assets/fonts/LICENSE_Noto_CJK.txt','original_font_sha256':{q.name:sha(q) for q in font.glob('*.otf')},'usage':'Raster lettering on two original street-name blades.'},'layout':{'author':'OpenStreetMap contributors','license':'ODbL-1.0','url':d.get('source_url'),'attribution_url':'https://www.openstreetmap.org/copyright','original_layout':'source_data/geo_layout.json','layout_sha256':sha(layout),'derived':'assets/frontage_r24/traffic_lanes.json','derived_sha256':sha(s/'assets/traffic_lanes.json'),'modifications':'Bound existing OSM ways to their own road meshes, joined endpoints and authored local game elevations and roadway finishes.'},'original_art':{'road_name_faces':sha(s/'road_names.png'),'soft_contact_projection':sha(s/'assets/tyre_contact.png'),'models':'Original game geometry for the median, local retaining face, planted strip, grass, drains, street sign and pier treatment.'}}
out=s/'assets/road_sources.json';out.write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf8')
shutil.copy2(out,p/'assets/frontage_r24'/out.name)

