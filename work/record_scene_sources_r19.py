from pathlib import Path
import json,hashlib,shutil
W=Path(__file__).resolve().parent;P=W/'project/chongqing_godot_v05';S=W/'project/chongqing_blender_v05'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda:f.read(4*1024*1024),b''):h.update(data)
    return h.hexdigest()
credits=read(S/'scanned_assets/source_credits.json')
keys={'chinese_tea_table','plastic_monobloc_chair_01','potted_plant_02','metal_trash_can','metal_trash_can_rust','metal_trash_can_clean','trashbag','plastic_crate_01'}
assets=[v for v in credits['assets'] if v['id'] in keys]
sky=W/'assets_incoming/r19_sky/kloofendal_overcast_puresky_2k.hdr'
sky_record={'id':'kloofendal_overcast_puresky','author':'Greg Zaal','license':'CC0-1.0','commercial_use':'permitted','attribution_required':False,'source_url':'https://polyhaven.com/a/kloofendal_overcast_puresky','license_url':'https://polyhaven.com/license','download_url':read(W/'assets_incoming/r19_sky/files_metadata.json')['hdri']['2k']['hdr']['url'],'provider_md5':'26462123fc5ce757a331553d05e4db37','md5_verified':hashlib.md5(sky.read_bytes()).hexdigest()=='26462123fc5ce757a331553d05e4db37','sha256':digest(sky),'bytes':sky.stat().st_size,'modifications':'Source HDR pixels unchanged. Runtime sky energy and orientation adjusted; broad bright-cloud position measured, not a sharp solar disk.'}
(W/'assets_incoming/r19_sky/PROVENANCE.json').write_text(json.dumps(sky_record,ensure_ascii=False,indent=2),encoding='utf-8')
existing_materials=read(S/'materials/material_provenance.json')['assets']
record={'revision':'R19_scene_05','checked_on':'2026-11-20','authored':'Original mesh sign, canopy tailoring, fittings, duct, drainage grates, dish profiles, stair caps/curbs, distant terrain, placements and runtime weathering. No AI raster assets created.','reused_scans':assets,'reused_material_sources':{k:v for k,v in existing_materials.items() if k in ['concrete','step_concrete','stone','timber','curtain_beige']},'reuse_note':'Existing project Poly Haven CC0 library, not a claim of newly downloaded models. Low support vertices refitted to R17 paving; source scans retained. Attribution is optional for these CC0 assets, but authors and URLs retained. Other earlier licenses remain in force.','new_sky':sky_record,'reference_photos':[{'url':'https://www.johnrash.com/imported-20110606170757/2013/7/22/report-from-the-river-chongqing.html','author':'John Rash','publication_date':'2013-07-22','observed':'Stair/terrace relationship; grilles; wires; household objects; irregular repairs. Black-and-white photo, not a color or illumination calibration.','use':'Viewed in browser for visual study only; not downloaded into the game or used as a texture. No commercial reuse license assumed.'}],'unrecovered':'Original final R15 reference photo ZIP still missing; new references are not recovered project files.','source_files':{},'exported_files':{}}
for path in [S/'scanned_assets/prepared_assets.blend',W/'r17_scene/chongqing_district.blend',W/'scene_r19/street_life.blend',W/'build_street_r19.py',S/'scanned_assets/source_credits.json',S/'materials/material_provenance.json']:
    record['source_files'][str(path.relative_to(W)).replace('\\','/')]=digest(path)
for path in (P/'assets/street_r19').iterdir():
    if path.suffix.lower() in ['.glb','.jpg','.png']:
        record['exported_files'][path.name]=digest(path)
(P/'assets/street_r19/PROVENANCE.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('R19 provenance:',len(assets),'reused scan credits;',len(record['exported_files']),'exported files hashed; new HDR MD5',sky_record['md5_verified'])
