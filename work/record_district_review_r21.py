"""Verify the R21 work evidence and copy selected engine frames for review."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

from PIL import Image, ImageDraw, ImageFont


work = Path(__file__).resolve().parent
project = work / 'project/chongqing_godot_v05'
checks = project / 'verification_r21'
current = checks / 'current'
source = work / 'scene_r21'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def same_copy(original, target):
    shutil.copy2(original, target)
    assert sha(original) == sha(target), target
    return sha(target)


def record(out):
    out.mkdir(parents=True, exist_ok=True)
    base = checks / 'district_base/captures'
    new = current / 'captures'
    prior, latest = [read(path / 'capture_manifest.json') for path in [base, new]]
    profile_hash = sha(project / 'assets/render_profile_r21.json')
    assert not latest['failures'] and not prior['failures']
    assert latest['art_profile_sha256'] == profile_hash
    assert latest['scene_identity']['district_r21']['layer_sha256'] == sha(project / 'assets/district_r21/terraces.glb')
    assert latest['capture_order'] == prior['capture_order']
    shots = {}
    for a, b in zip(prior['captures'], latest['captures']):
        keys = ['view', 'position', 'target', 'fov', 'width', 'height', 'capture_state']
        assert all(a[k] == b[k] for k in keys), (a['view'], b['view'])
        assert b['width'] == 1600 and b['height'] == 900 and b['save_error'] == 0
        file = 'godot_' + a['view'] + '.png'
        shots[a['view']] = dict(before=sha(base/file), current=sha(new/file), camera={k:b[k] for k in keys})
    defect_dir = current/'defect_views'
    defect_review = read(defect_dir/'capture_manifest.json')
    assert defect_review['art_profile_sha256']==profile_hash and not defect_review['failures']
    expected = ['r16_scooter','r17_A04_entry','r16_roof','r16_meter','r17_worker_entry','r17_worker_door','r16_clothesline','r17_west_route']
    assert defect_review['capture_order']==expected
    originals = list((work.parent/'outputs').glob('R15*/**/image(*).png'))
    assert len(originals)==6
    defect_evidence = {'original_screenshots':{p.name:sha(p) for p in sorted(originals)},
                       'current_diagnostic_cameras':{n:sha(defect_dir/('godot_'+n+'.png')) for n in expected},
                       'scope':'Existing diagnostic locations. Original user camera transforms are unknown.'}
    public = {}
    rows = [('street_entry','街口'), ('central_steps','中央梯坎'), ('r20_tree_court','上巷树池'), ('roofscape','住宅屋顶')]
    font_path = work / 'assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf'
    font = ImageFont.truetype(str(font_path), 28)
    width, height = 800, 450
    comparison = Image.new('RGB', (width*2+12,(height+50)*len(rows)), '#141716')
    draw = ImageDraw.Draw(comparison)
    for i, (view, title) in enumerate(rows):
        file = 'godot_' + view + '.png'
        for j, (folder, label) in enumerate([(base,'原工作版'),(new,'当前工作版')]):
            x, y = j*(width+12), i*(height+50)
            draw.text((x+10,y+3), title+'　·　'+label, font=font, fill='#efebe1')
            with Image.open(folder/file) as image:
                comparison.paste(image.resize((width,height), Image.Resampling.LANCZOS), (x,y+46))
        dest = out / (title+'实机.png')
        public[dest.name] = same_copy(new/file, dest)
    pair = out / '城区同机位对照.jpg'
    comparison.save(pair,quality=92,subsampling=0)
    public[pair.name] = sha(pair)
    movie = read(current/'movie_review.json')
    take = read(current/'district_take.json')
    assert take['profile_sha256'] == profile_hash and take['frames'] == movie['frames'] == 241
    assert movie['mp4_sha256'] == sha(source/'district_current.mp4')
    decoded = read(current/'movie_decode.json')
    assert decoded['mp4_sha256']==movie['mp4_sha256'] and decoded['decoded_frames']==movie['frames']
    dest = out/'中央梯坎连续实机.mp4'
    public[dest.name] = same_copy(source/'district_current.mp4',dest)
    tested = {}
    for name in ['district_test','gameplay_test','lane_test','delivery_end_to_end','survey','shopkeeper_performance','street_test','rider/report']:
        path = current / (name+'.json')
        test = read(path)
        assert test['passed'] and test['art_profile']['sha256'] == profile_hash, path
        tested[name] = {'tests':len(test['tests']), 'sha256':sha(path)}
    contact_study = None
    if latest['art_profile']['art_revision'] == 'R21_district_07_internal':
        previous_shots = checks/'district06/captures'
        old_roof = next(v for v in read(previous_shots/'capture_manifest.json')['captures'] if v['view']=='roofscape')
        new_roof = next(v for v in latest['captures'] if v['view']=='roofscape')
        assert [old_roof[k] for k in ['position','target','fov']]==[new_roof[k] for k in ['position','target','fov']]
        region = (1184,0,1598,240)
        detail = Image.new('RGB',(836,281),'#141716')
        labels = ImageDraw.Draw(detail)
        for index,(path,label) in enumerate([(previous_shots,'第六次'),(new,'当前工作版')]):
            x=index*422
            labels.text((x+5,0),label,font=font,fill='#efebe1')
            with Image.open(path/'godot_roofscape.png') as source_image:
                detail.paste(source_image.crop(region),(x,39))
        detail.save(current/'roof_tree_contact_comparison.png')
        contact_study = {'source_pixel_rect':list(region),'comparison_sha256':sha(current/'roof_tree_contact_comparison.png')}
    previous, performance = [read(x/'performance.json') for x in [checks/'perf_reference', current]]
    assert performance['art_profile']['sha256']==profile_hash
    assert previous['gpu']==performance['gpu'] and previous['window_size']==performance['window_size']
    assert all(a['view']==b['view'] and a['samples']==b['samples']==240 for a,b in zip(previous['views'],performance['views']))
    blends = read(current/'blender_reopen.json')
    assert blends['city_sha256']==sha(source/'chongqing_district.blend')
    assert blends['runtime_glb_sha256']==latest['scene_identity']['district_r21']['layer_sha256']
    runtime_files = ['project.godot','scripts/main.gd','scripts/district_r21.gd',
                     'shaders/canopy_r21.gdshader','shaders/exterior_r21.gdshader',
                     'shaders/paving_r21.gdshader','shaders/worn_rail_r21.gdshader',
                     'assets/district_r21/layout.json','assets/district_r21/wall_fields.json',
                     'assets/district_r21/wall_runoff.png','assets/district_r21/exterior_land.png',
                     'assets/district_r21/canopy_atlas.png','assets/district_r21/provenance.json',
                     'assets/district_r21/exterior_sun_mask.png','shaders/facade_runoff_r21.gdshaderinc']
    summary = {'profile':latest['art_profile']['art_revision'], 'profile_sha256':profile_hash,
               'runtime_files':{s:sha(project/s) for s in runtime_files},
               'comparison_baseline':prior['art_profile']['art_revision'],'same_cameras':shots,'original_defects':defect_evidence,
               'checks':tested,'routes':read(current/'survey.json')['configured_route_count'],
               'delivery_teleports':read(current/'delivery_end_to_end.json')['teleports_between_stages'],
               'device':performance['gpu'],'window_size':performance['window_size'],
               'p95_ms_by_view':{a['view']:{'previous':a['p95_ms'],'current':b['p95_ms']} for a,b in zip(previous['views'],performance['views'])},
               'geometry_reopen':blends,'tree_contact_study':contact_study,'movie':movie,
               'decoded_movie_frames':decoded['decoded_frames'],'media_files_sha256':public}
    (current/'review_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    print('Verified',len(shots),'matching cameras,',len(public),'review files.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output',type=Path)
    record(parser.parse_args().output)
