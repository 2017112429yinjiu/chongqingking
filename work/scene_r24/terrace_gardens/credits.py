from pathlib import Path
import json,hashlib
here=Path(__file__).resolve().parent;work=here.parents[1];base=work/'project/chongqing_blender_v05';game=work/'project/chongqing_godot_v05'
credit=json.loads((base/'scanned_assets/source_credits.json').read_text('utf-8-sig'))
assets=[a for a in credit['assets'] if a['id'] in ('tree_small_02','shrub_01','potted_plant_02')]
for key,author in [('concrete_floor_worn_001','Dimitrios Savva, Rico Cilliers'),('brick_wall_08','Amal Kumar'),('stone_wall_05','Charlotte Baglioni'),('leaf_scattered_gravel','Dimitrios Savva')]:
    assets.append({'id':key,'authors':author,'license':'CC0 1.0','source_url':'https://polyhaven.com/a/'+key})
files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for a in assets for f in (game/'assets').glob('chongqing_district_'+a['id']+'*') if not f.name.endswith('.import')}
(here/'assets.json').write_text(json.dumps({'source_credits':assets,'source_terms':credit['license_url'],'inherited_files_sha256':files,'new_downloads':[],'uses':'Existing material maps, original mesh UVs and donor meshes are reused locally. Three small trees, shrub variations and potted scan foliage without pots are instanced by the district. Grade geometry, normals, root openings and masonry authored for this revision. Prior OSM and city-context notices remain with the game.','reference_directory':'../street_photo_study/reference/credits.json'},indent=2,ensure_ascii=False),'utf8')
