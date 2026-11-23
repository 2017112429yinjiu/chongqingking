from pathlib import Path
import hashlib, json, shutil, zipfile

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = Path('C:/Users/尹久/Downloads')
ARCHIVES = ROOT / 'outputs' / 'R15原始资产'
WORKING = ROOT / 'work' / 'project'
ARCHIVES.mkdir(parents=True, exist_ok=True)
WORKING.mkdir(parents=True, exist_ok=True)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

files = ['chongqing_street_godot_v05.zip', 'chongqing_street_blender_v05.zip', 'chongqing_street_blender_rebuild_v05.zip', 'chongqing_v05_engine_photos.zip']
report = {'baseline': 'v05 / R15', 'date_local': '2026-11-20', 'archives': [], 'engine_tests_this_session': 'not_run'}
for name in files:
    src, dst = DOWNLOADS / name, ARCHIVES / name
    if not src.exists():
        report['archives'].append({'name': name, 'status': 'not_downloaded'})
        continue
    if not dst.exists():
        shutil.copy2(src, dst)
    source_hash = sha(src)
    assert source_hash == sha(dst), name
    with zipfile.ZipFile(dst) as z:
        bad = z.testzip()
        assert bad is None, (name, bad)
        inventory = [{'name': e.filename, 'bytes': e.file_size, 'crc32': f'{e.CRC:08x}'} for e in z.infolist()]
        for e in z.infolist():
            target = (WORKING / e.filename).resolve()
            assert target.is_relative_to(WORKING), e.filename
        # Baseline files only; never overwrite edited working files on rerun.
        for e in z.infolist():
            if not (WORKING / e.filename).exists():
                z.extract(e, WORKING)
    item = {'name': name, 'bytes': dst.stat().st_size, 'sha256': source_hash, 'crc_verified': True, 'entries': len(inventory), 'status': 'recovered'}
    report['archives'].append(item)
    (ARCHIVES / (name + '.inventory.json')).write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(item, ensure_ascii=False), flush=True)

metadata_path = WORKING / 'chongqing_godot_v05/docs/delivery_metadata.json'
if metadata_path.exists():
    m = json.loads(metadata_path.read_text(encoding='utf-8'))
    report['verified_files'] = []
    for key, relative in [('scene_glb', 'chongqing_godot_v05/assets/chongqing_district.glb'), ('main_blend', 'chongqing_blender_v05/chongqing_district.blend')]:
        p = WORKING / relative
        actual = sha(p)
        assert actual == m[key]['sha256'] and p.stat().st_size == m[key]['bytes'], relative
        report['verified_files'].append({'file': relative, 'sha256': actual, 'bytes': p.stat().st_size, 'matches_r15_delivery': True})
    (ARCHIVES / 'delivery_metadata.json').write_bytes(metadata_path.read_bytes())
    shutil.copy2(WORKING / 'chongqing_godot_v05/docs/review_zh.txt', ARCHIVES / 'chongqing_v05_review_zh.txt')
report['complete_four_archives'] = all(x['status'] == 'recovered' for x in report['archives'])
(ARCHIVES / 'RECOVERY_MANIFEST.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'complete': report['complete_four_archives'], 'working': str(WORKING)}, ensure_ascii=False), flush=True)
