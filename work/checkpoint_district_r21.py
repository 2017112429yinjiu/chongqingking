"""Preserve the active authored increment and its verified runtime inputs."""
from pathlib import Path
import hashlib
import json
import shutil

work = Path(__file__).resolve().parent
root = work.parent
game = work/'project/chongqing_godot_v05'
qa = game/'verification_r21'
review = json.loads((qa/'current/review_summary.json').read_text(encoding='utf8'))
revision = review['profile']
assert revision == json.loads((game/'assets/render_profile_r21.json').read_text(encoding='utf8'))['art_revision']
dest = work/'checkpoints'/revision.removesuffix('_internal')
items = set()


def add(path):
    if path.is_dir():
        items.update(p for p in path.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    elif path.is_file():
        items.add(path)
    else:
        raise FileNotFoundError(path)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


for name in ['START.md','AGENTS.md','HANDOFF_LOG.md']:
    add(root/name)
for pattern in ['*r21.py','*r21.ps1','*r21.gd','district_*.py','build_counter_condiments.py',
                'counter_*.py','counter_*.gd','capture_counter_take.gd','capture_district_walk.gd',
                'bake_district_trees.py','shopkeeper_hair_finish.py','export_shopkeeper_mesh.py',
                'shopkeeper_performance.py','subset_lane_type_r20.py']:
    for path in work.glob(pattern):add(path)
for name in ['chongqing_district.blend','district_environment.blend','district_current.mp4',
             'exterior_sun_bake.json','canopy','condiments','washed_sandstone.jpg','district_rays.json']:
    add(work/'scene_r21'/name)
add(work/'characters/shopkeeper_r21')
add(work/'assets_incoming/district_r21')
for name in ['project.godot','main.tscn','CHANGELOG.md','docs','scripts','shaders','assets/counter_r21',
             'assets/district_r21','assets/render_profile_r21.json','assets/fonts/cq_district_ui.otf',
             'assets/fonts/cq_district_ui.otf.import']:
    add(game/name)
for pattern in ['characters/shopkeeper_r21*','sky/kloofendal_28d_misty_puresky_2k.hdr*']:
    for path in (game/'assets').glob(pattern):add(path)
for name in ['current','perf_reference','final_contact','shadow_study','district_base/captures/capture_manifest.json']:
    add(qa/name)
hashes = {}
for file in sorted(items):
    target = dest/file.relative_to(root)
    target.parent.mkdir(parents=True,exist_ok=True)
    value = sha(file)
    if target.exists():
        assert value == sha(target), f'Existing checkpoint differs: {target}'
    else:
        shutil.copy2(file,target)
        assert sha(target)==value, target
    hashes[file.relative_to(root).as_posix()] = value
(dest/'manifest.json').write_text(json.dumps({'revision':revision,
    'scope':'Internal R21 working increment. Reuses the R20 base. Godot import caches and engine binaries excluded.',
    'files_sha256':hashes},indent=2,ensure_ascii=False),encoding='utf8')
print(revision,len(hashes),'verified working files')
