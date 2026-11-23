"""Checkpoint the R22 import-only revision against the immutable R22 build 06 city."""
from pathlib import Path
import hashlib
import json
import shutil

work=Path(__file__).resolve().parent;root=work.parent
project=work/'project/chongqing_godot_v05'
evidence=project/'verification_r22/import01'
trial=work/'gpu_trial_r22/verification'
checkpoint=work/'checkpoints/R22_district_07'
prior=work/'checkpoints/R22_district_06/manifest.json'

def read(path):return json.loads(path.read_text(encoding='utf8'))
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

profile=project/'assets/render_profile_r22.json';profile_hash=sha(profile)
assert read(profile)['art_revision']=='R22_district_07_internal'
recipes=project/'assets/roofs_r22/surface_imports.json'
record=read(recipes);files=[profile,recipes,prior]
for row in record['maps']:
    meta=project/row['path'];original=Path(str(meta)[:-7])
    assert sha(meta)==row['validated_import_sha256'] and sha(original)==row['image_sha256']
    files.extend([meta,original])
checks={}
for name in ['art_test','survey','delivery_end_to_end','gameplay_test','district_test','lane_test','street_test','rider/report']:
    row=read(evidence/(name+'.json'))
    assert row['passed'] and row['art_profile']['sha256']==profile_hash
    checks[name]=len(row['tests'])
assert read(evidence/'art_test.json')['tests']['active_source_and_bptc_recipe_hashes']
assert read(evidence/'delivery_end_to_end.json')['teleports_between_stages']==0
comparison=read(evidence/'camera_comparison.json')
assert comparison['current_profile_sha256']==profile_hash and len(comparison['views'])==13
audit=read(evidence/'blender_audit.json')
prior_files=read(prior)['files']
for rel in ['work/scene_r22/chongqing_district.blend','work/scene_r22/river_context.blend','work/scene_r22/roofs_and_breakfast.blend']:
    assert sha(root/rel)==prior_files[rel]
assert audit['city_sha256']==prior_files['work/scene_r22/chongqing_district.blend']
perf=read(evidence/'native_1080.json')
assert perf['art_profile']['sha256']==profile_hash and perf['framebuffer']==[1920,1080]
for row in perf['views']:
    assert sha(evidence/('1080_'+row['view']+'.png'))==row['readback_sha256']
    assert row['samples']==240 and row['gpu_p50_ms']>0
desktop=read(evidence/'performance.json')
assert len(desktop['views'])==9 and all(r['viewport_gpu_positive_count']==240 for r in desktop['views'])
probe=read(evidence/'texture_probe.json')
assert all(r['already_loaded'] and r['format']==22 for r in probe['maps'])
movie=work/'scene_r22/district_import01.mp4'
assert sha(movie)==comparison['movie'] and read(evidence/'movie_decode.json')['decoded_frames']==241
files+=[root/'START.md',root/'HANDOFF_LOG.md',root/'AGENTS.md',project/'CHANGELOG.md',
        project/'scripts/main.gd',project/'scripts/qa_context.gd',project/'scripts/qa_performance.gd',movie,
        work/'encode_district_r21.py',work/'review_district_video_r21.py']
for pattern in ['*r22*.py','*r22*.gd','*r22*.ps1']:
    files.extend(work.glob(pattern))
for folder in [evidence,trial,project/'docs',root/'outputs/R22城区内部对照']:
    files.extend(folder.rglob('*'))
checkpoint.mkdir(parents=True,exist_ok=True)
if (checkpoint/'manifest.json').exists():raise RuntimeError('The verified checkpoint already exists.')
digests={}
for src in sorted(set(p for p in files if p.is_file())):
    rel=src.relative_to(root);dest=checkpoint/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dest);checksum=sha(src);assert sha(dest)==checksum
    digests[rel.as_posix()]=checksum
manifest={'scope':'Internal import-only increment, inherits editable city/GLBs from R22_district_06.',
          'prior_manifest_sha256':sha(prior),'art_profile_sha256':profile_hash,'checks':checks,'files':digests}
(checkpoint/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('Verified checkpoint',checkpoint.name,len(digests))
