"""Bind the reopened source, engine results and untouched fixed views to the working revision."""
from pathlib import Path
from functools import lru_cache
import datetime
import hashlib
import json
import numpy as np
from PIL import Image

W = Path(__file__).resolve().parent
P = W / 'project/chongqing_godot_v05'
V = P / 'verification_r20'
C = V / 'current'
L = P / 'assets/lane_r20'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

@lru_cache(maxsize=None)
def sha(path):
    with path.open('rb') as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(4 << 20), b''):
            digest.update(chunk)
        return digest.hexdigest()

def check_paths(mapping):
    for path, digest in mapping.items():
        assert sha(P / path.removeprefix('res://')) == digest, path

def main():
    composition_path = P / 'assets/scene_composition_r20.json'
    composition = read(composition_path)
    check_paths(composition['runtime_layers'])
    assert composition['source_sha256'] == sha(W/'scene_r20/chongqing_district.blend')
    assert composition['layer_blend_sha256'] == sha(W/'scene_r20/upper_lane.blend')
    assert not composition['unpacked']
    files = ['meter_lods.glb','meter_lods.json','rinse_fixture.json','tree_seats.json','alley_sky.png','shop_sky.png']
    composition['render_derivatives'] = {'assets/render_profile_r20.json':sha(P/'assets/render_profile_r20.json')}
    composition['render_derivatives'].update({'assets/lane_r20/'+f:sha(L/f) for f in files})
    if read(P/'assets/render_profile_r20.json').get('court_resident'):
        model_dir=P/'assets/characters/court_resident'
        composition['animated_resident']={'editable_source_sha256':sha(W/'characters/court_resident/court_resident.blend'),
            'model_sha256':sha(model_dir/'court_resident.glb'),'fit_sha256':sha(model_dir/'bench_fit.json')}
    write(composition_path, composition)
    materials = read(P/'assets/material_provenance.json')['assets']
    shrub = next(item for item in read(P/'docs/MODEL_CREDITS.json')['assets'] if item['id']=='shrub_01')
    sources = {key: materials[key] for key in ['timber','step_concrete','soil_dark','stone']}
    assert all(row['license'].startswith('CC0') for row in [*sources.values(),shrub])
    write(L/'PROVENANCE.json',{
        'original':'District-authored lane geometry, fixture, water audio, typography layouts, bench and court assembly, garden blades and shading fields.',
        'reused_materials':sources,'reused_shrub':shrub,'poly_haven_license':'https://polyhaven.com/license',
        'credit':'CC0 permits commercial reuse without mandatory attribution. Creator and source names are retained here.',
        'font':read(P/'assets/fonts/R20_font_sources.json'),'font_license_in_game':'assets/fonts/R20_OFL.txt',
        'private_visual_reference':{'source':'https://www.nrdc.cn/Public/uploads/2016-12-02/58416d12760d3.pdf#page=21','figures':[19,20],'use':'Private visual reference for step-side handrails and resting places. No photographs redistributed.'},
        'meter_derivative':'Spatial partition and distance models derived from the original project meter meshes. Original editable source retained.',
        'authored_prints':{f.name:sha(f) for f in sorted((W/'scene_r20/print_sources').glob('*.png'))}
    })
    perf = read(C/'performance.json')
    profile = read(P/'assets/render_profile_r20.json')
    tests = {}
    for file in sorted(C.glob('*.json')):
        data = read(file)
        assert data.get('passed', file.name == 'performance.json'), file
        assert data['art_profile']['revision'] == profile['art_revision']
        assert data['art_profile']['sha256'] == sha(P/'assets/render_profile_r20.json')
        assert data['upper_lane']['model_sha256'] == sha(L/'upper_lane.glb')
        assert data['meter_lod']['sha256'] == sha(L/'meter_lods.glb')
        check_paths(data['upper_lane']['sky_sha256'])
        check_paths(data['runtime_sha256'])
        if 'tests' in data:
            tests[file.stem] = len(data['tests'])
    shots = read(C/'captures/capture_manifest.json')
    check_paths(shots['script_sha256'])
    assert shots['scene_identity']['meter_lod']==perf['meter_lod']
    assert shots['scene_identity']['upper_lane']==perf['upper_lane']
    assert shots['art_profile_sha256']==perf['art_profile']['sha256'] and not shots['failures']
    views = {item['view']:item for item in shots['captures']}
    assert views['r20_tap']['rinse_visibly_running']
    resident = profile.get('court_resident',False)
    assert len(views)==(12 if resident else 10)
    if resident:
        assert shots['scene_identity']['court_resident']==perf['court_resident']
        model = P/'assets/characters/court_resident'
        assert perf['court_resident']['model']==sha(model/'court_resident.glb')
        assert perf['court_resident']['fit']==sha(model/'bench_fit.json')
        assert perf['court_resident']['controller']==sha(P/'scripts/court_resident.gd')
        for file in C.glob('*.json'):
            assert read(file)['court_resident']==perf['court_resident']
    trial = V/('resident_meter_comparison' if resident else 'meter_trial07')
    comparison_profile = read(trial/'comparison_profile.json')
    assert {k for k in set(profile)|set(comparison_profile) if profile.get(k)!=comparison_profile.get(k)}=={'meter_lod'}
    old_shots = read(trial/'comparison_captures/capture_manifest.json')
    assert not old_shots['failures'] and 'meter_lod' not in old_shots['scene_identity']
    assert old_shots['art_profile_sha256']==sha(trial/'comparison_profile.json')
    assert old_shots['scene_identity']['upper_lane']==perf['upper_lane']
    if resident:assert old_shots['scene_identity']['court_resident']==perf['court_resident']
    diffs = {}
    for old in old_shots['captures']:
        view = old['view']
        current = views[view]
        for key in ['position','target','fov','width','height']:
            assert old[key]==current[key],(view,key)
        a,b = [np.asarray(Image.open(P/item['path'].removeprefix('res://')).convert('RGB'),dtype=np.int16) for item in [old,current]]
        delta = np.abs(a-b)
        diffs[view] = {'mean_absolute_rgb_0_255':float(delta.mean()),'pct_pixels_max_channel_delta_above_8':float((delta.max(axis=2)>8).mean()*100)}
    sizes = {}
    for view,row in views.items():
        file = P/row['path'].removeprefix('res://')
        with Image.open(file) as im:
            assert im.size==(1600,900)
        sizes[view] = sha(file)
    baseline = read(V/'trial06/performance.json')
    survey = read(C/'survey.json')
    delivery = read(C/'delivery_end_to_end.json')
    assert delivery['teleports_between_stages']==0 and len(survey['tested_route_names'])==24
    rows = []
    for old,new in zip(baseline['views'],perf['views']):
        assert old['view']==new['view'] and old['samples']==new['samples']==240
        rows.append({'view':new['view'],'pre_partition_p95_ms':old['p95_ms'],'current_p95_ms':new['p95_ms'],'primitives_before':old['primitives'],'primitives_current':new['primitives']})
    record = {'revision':profile['art_revision'],'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'tests':tests,'survey_routes':len(survey['tested_route_names']),'teleports_between_delivery_stages':0,
        'render_composition_sha256':sha(composition_path),'provenance_sha256':sha(L/'PROVENANCE.json'),
        'composition':composition,'runtime':perf['runtime_sha256'],'evidence_sha256':{f.name:sha(f) for f in sorted(C.glob('*.json'))},
        'capture_manifest_sha256':sha(C/'captures/capture_manifest.json'),'fixed_view_image_sha256':sizes,
        'meter_only_image_differences':diffs,'performance':{'gpu':perf['gpu'],'viewport':perf['window_size'],'warmup_frames':90,'samples_per_view':240,'fixed_views':rows,'scope':'Stationary cameras; comparison baseline predates court surface changes. No moving crowd/traffic benchmark.'},
        'limits':['No cinematic acceptance. Repetition and empty slopes remain.','Full pedestrian/traffic simulation and final R15 photo archive remain outstanding.']}
    if resident:
        contacts=read(C/'resident_motion/contact_sweep.json')
        assert contacts['model_sha256']==perf['court_resident']['model'] and len(contacts['samples'])==130
        court_perf=read(V/'resident_court_gpu/performance.json')
        assert court_perf['court_resident']==perf['court_resident'] and court_perf['art_profile']==perf['art_profile']
        assert len(court_perf['views'])==3 and all(v['samples']==240 for v in court_perf['views'])
        motion=read(C/'resident_motion/encoding.json')
        assert motion['scene']==perf['court_resident'] and motion['profile_sha256']==perf['art_profile']['sha256']
        assert motion['mp4_sha256']==sha(W/'audit/court_resident.mp4') and motion['take_frames']==262
        imports={}
        for settings in sorted(model.glob('*.png.import')):
            config=settings.read_text()
            assert 'compress/mode=2' in config and '.bptc.ctex' in config,settings
            imports[settings.name]=sha(settings)
        assert len(imports)==5
        ab=V/'resident_ab'
        disabled=read(ab/'disabled.json')
        assert {k for k in set(profile)|set(disabled) if profile.get(k)!=disabled.get(k)}=={'court_resident'}
        controls={}
        for key in ['off_a','on','off_b']:
            sample=read(ab/key/'performance.json')
            assert sample['art_profile']['sha256']==(perf['art_profile']['sha256'] if key=='on' else sha(ab/'disabled.json'))
            assert sample.get('court_resident')==(perf['court_resident'] if key=='on' else None)
            assert len(sample['views'])==3 and all(row['samples']==240 for row in sample['views'])
            controls[key]={row['view']:row['p95_ms'] for row in sample['views']}
        record['resident']={'runtime':perf['court_resident'],'editable_source_sha256':sha(W/'characters/court_resident/court_resident.blend'),
          'source_notice_sha256':sha(model/'LICENSE.txt'),'provenance':read(model/'PROVENANCE.json'),
          'placement':read(model/'bench_fit.json'),'contact_ranges_m':contacts['ranges_m'],'samples_per_action':65,
          'court_performance':court_perf['views'],'resident_on_off_p95_ms':controls,'video':motion,'desktop_texture_imports':imports,
          'resident_qa_script':sha(P/'scripts/qa_court_resident.gd'),
          'scope':'One seated neighbor with two skeletal actions, paired eyelid and smile controls, contextual directions and distance-based animation sampling.'}
    write(V/'review_summary.json',record)
    print('Verified',record['revision'], tests, rows[-1], diffs['r16_meter'])

if __name__=='__main__':
    main()
