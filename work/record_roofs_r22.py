"""Compare the ungraded native frames only after matching the two camera manifests."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
from PIL import Image, ImageDraw, ImageFont

work = Path(__file__).resolve().parent
project = work / 'project/chongqing_godot_v05'
checks = project / 'verification_r22'
tag=sys.argv[1] if len(sys.argv)>1 else 'import01'
assert tag.isidentifier()
active=checks/tag
old,new=checks/'reference/captures',active/'captures'
out = work.parent / 'outputs/R22城区内部对照'
out.mkdir(exist_ok=True)

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

previous, latest = [read(x/'capture_manifest.json') for x in (old,new)]
assert not previous['failures'] and not latest['failures']
assert previous['capture_order'] == latest['capture_order'] and len(latest['capture_order'])==13
assert latest['art_profile_sha256'] == sha(project/'assets/render_profile_r22.json')
for folder, ident, asset in [('river_r22','river_r22','river_context'),('roofs_r22','roofs_r22','roofs_and_breakfast')]:
    assert latest['scene_identity'][ident]['layer_sha256'] == sha(project/'assets'/folder/(asset+'.glb'))
rows = {}
for a,b in zip(previous['captures'],latest['captures']):
    keys = ['view','position','target','fov','width','height','capture_state']
    assert all(a[k] == b[k] for k in keys) and b['width']==1600 and b['height']==900
    assert a['save_error']==b['save_error']==0
    file='godot_'+b['view']+'.png'
    rows[b['view']]={'camera':{k:b[k] for k in keys},'before':sha(old/file),'current':sha(new/file)}
font=ImageFont.truetype(str(work/'assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf'),26)
for group,views in [('屋面与街边',[('r22_roof_garden','住宅天台'),('roofscape','屋顶全景'),('r22_breakfast','面馆早餐桌')]),
                    ('街口与江岸',[('r22_river_street','路口行人眼高'),('r22_river_overview','高处看江岸'),('r22_river_detail','跨江远景检查')])]:
    board=Image.new('RGB',(1610,500*len(views)),'#171919')
    draw=ImageDraw.Draw(board)
    for i,(key,label) in enumerate(views):
        for j,(folder,version) in enumerate([(old,'R21'),(new,'R22')]):
            x=810*j;y=500*i
            draw.text((x+8,y+2),label+'　'+version,font=font,fill='#f0ebe1')
            with Image.open(folder/('godot_'+key+'.png')) as im:
                board.paste(im.resize((800,450),Image.Resampling.LANCZOS),(x,y+44))
    board.save(out/(group+'同机位.jpg'),quality=93,subsampling=0)
summary={'comparison':'R21 / R22, same native cameras and capture state','views':rows,
         'current_profile_sha256':latest['art_profile_sha256'],'reference_profile_sha256':previous['art_profile_sha256']}
defects=read(active/'defect_views/capture_manifest.json')
assert not defects['failures'] and len(defects['capture_order'])==8
assert defects['art_profile_sha256']==latest['art_profile_sha256']
originals=list((work.parent/'outputs/R15原始资产/用户缺陷截图').glob('*.png'))
assert len(originals)==6
summary['defect_evidence']={'original_screenshots':{p.name:sha(p) for p in originals},
    'current_diagnostic_cameras':{n:sha(active/'defect_views'/('godot_'+n+'.png')) for n in defects['capture_order']},
    'scope':'Related locations only. The original user camera transforms are unknown.'}
take=read(active/'district_take.json')
movie=read(active/'movie_decode.json')
assert take['profile_sha256']==latest['art_profile_sha256'] and movie['decoded_frames']==take['frames']==241
video=work/'scene_r22'/('district_'+tag+'.mp4')
output_video=out/'早餐桌到街口连续实机.mp4'
assert sha(video)==movie['mp4_sha256']
shutil.copy2(video,output_video)
assert sha(output_video)==movie['mp4_sha256']
summary['movie']=movie['mp4_sha256']
(active/'camera_comparison.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
