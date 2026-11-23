"""Preserve the verified R22 increment and its dependency on the existing R21 checkpoint."""
from pathlib import Path
import hashlib
import json
import shutil

work=Path(__file__).resolve().parent
root=work.parent
project=work/'project/chongqing_godot_v05'
scene=work/'scene_r22'
evidence=project/'verification_r22'
current=evidence/'current'
target=work/'checkpoints/R22_district_06'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

profile=sha(project/'assets/render_profile_r22.json')
assert read(current/'camera_comparison.json')['current_profile_sha256']==profile
assert sha(scene/'chongqing_district.blend')==read(current/'blender_audit.json')['city_sha256']
assert sha(scene/'district_current.mp4')==read(current/'movie_decode.json')['mp4_sha256']
reports={}
for name in ['art_test','survey','delivery_end_to_end','gameplay_test','district_test','lane_test','street_test','rider/report']:
    report=read(current/(name+'.json'))
    assert report['passed'] and report['art_profile']['sha256']==profile,name
    reports[name]=len(report['tests'])

perf_old=read(evidence/'perf_reference/performance.json')
perf_new=read(current/'performance.json')
assert perf_new['art_profile']['sha256']==profile
assert perf_old['art_profile']['sha256']==read(current/'camera_comparison.json')['reference_profile_sha256']
assert perf_old['gpu']==perf_new['gpu'] and perf_old['window_pixels']==perf_new['window_pixels']
assert perf_old['viewport_texture_pixels']==perf_new['viewport_texture_pixels']
assert len(perf_new['views'])==len(perf_old['views'])==9
for a,b in zip(perf_old['views'],perf_new['views']):
    assert a['view']==b['view'] and a['samples']==b['samples']==240
    assert min(a['viewport_gpu_positive_count'],b['viewport_gpu_positive_count'])==240
native_a,native_b=[read(folder/'native_1080.json') for folder in [evidence/'perf_reference',current]]
assert native_a['framebuffer']==native_b['framebuffer']==[1920,1080]
assert native_a['scale']==native_b['scale']==1 and native_b['art_profile']['sha256']==profile
assert native_a['gpu']==native_b['gpu'] and len(native_b['views'])==len(native_a['views'])==5
for a,b in zip(native_a['views'],native_b['views']):
    assert all(a[key]==b[key] for key in ['view','position','fov','samples']) and b['samples']==240
    assert min(a['gpu_p50_ms'],b['gpu_p50_ms'])>0

selection=[root/'START.md',root/'AGENTS.md',root/'HANDOFF_LOG.md',project/'CHANGELOG.md',project/'project.godot',
    project/'scripts/main.gd',project/'scripts/qa_context.gd',project/'scripts/qa_performance.gd',
    project/'scripts/river_r22.gd',project/'scripts/roofs_r22.gd',project/'assets/render_profile_r22.json',
    work/'encode_district_r21.py',work/'review_district_video_r21.py',
    work/'checkpoints/R21_district_07/manifest.json',evidence/'base_profile.json',evidence/'light_A.json']
for pattern in ['*r22.py','*r22.gd','*r22.ps1']:
    selection.extend(work.glob(pattern))
for pattern in ['*.blend','*.json','*.npy','surfaces/*','district_current.mp4','*06.log','river_sandbar06.jpg','light_comparison.jpg','legacy_locations.jpg']:
    selection.extend(scene.glob(pattern))
selection.extend((project/'shaders').glob('*r22.gdshader'))
for folder in [project/'assets/roofs_r22',project/'assets/river_r22',project/'source_data/river_r22',
               work/'assets_incoming/r22_city',project/'docs',current,evidence/'reference/captures',evidence/'perf_reference',evidence/'light_A/captures',
               evidence/'native_repeat_current',evidence/'native_repeat_base',evidence/'native_checked_current',evidence/'native_aa_trial',
               root/'outputs/R22城区内部对照']:
    selection.extend(folder.rglob('*'))
if target.exists() and (target/'manifest.json').exists():
    raise RuntimeError('Completed checkpoint already exists. Choose a new revision for further work.')
target.mkdir(parents=True,exist_ok=True)
files={}
for src in sorted(set(p for p in selection if p.is_file())):
    relative=src.relative_to(root);dest=target/relative
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dest)
    checksum=sha(src)
    assert sha(dest)==checksum,dest
    files[relative.as_posix()]=checksum
manifest={'scope':'Incremental internal authoring checkpoint. Prior city sources are retained in R21_district_07. No packaged game.',
          'profile_sha256':profile,'checked_reports':reports,'files':files}
(target/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('Checkpoint',target.name,len(files))
