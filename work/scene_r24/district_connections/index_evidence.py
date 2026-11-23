from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
here=Path(__file__).resolve().parent
work=here.parents[1];project=work/'project/chongqing_godot_v05';qa=project/'verification_r24/build18'
fontpath=work/'assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf'
def read(p):return json.loads(p.read_text('utf8'))
def hashed(p):
    with p.open('rb') as file:
        return hashlib.file_digest(file,'sha256').hexdigest()
def panel(path,pair,detail=False):
    dim=(1276,498) if detail else (1440,455)
    board=Image.new('RGB',dim,(35,37,34));d=ImageDraw.Draw(board)
    for i,(label,p) in enumerate(pair):
        a=Image.open(p).convert('RGB');x=i*(dim[0]//2);font=ImageFont.truetype(str(fontpath),22)
        d.text((x+12,8),label,font=font,fill=(241,235,217))
        size=(638,359) if detail else (720,405)
        board.paste(a.resize(size,Image.Resampling.LANCZOS),(x,40 if detail else 48))
        if detail:
            board.paste(a.crop((388,235,455,269)).resize((181,91),Image.Resampling.NEAREST),(x+448,406))
            d.text((x+12,426),'同一位置局部放大',font=font,fill=(219,214,196))
    board.save(path,quality=94)
def shot(n,k='current'):return here/k/('godot_r24_join18_'+n+'.png')
panel(here/'面馆同机位对照.jpg',[('玩家退回的铺面',here/'player/followup_3.png'),('当前默认工程 · 同一机位',shot('shop'))])
panel(here/'南区路斜向接缝对照.jpg',[('修前 · 斜看露天',shot('road','third')),('当前 · 接回旧铺面',shot('road'))],True)
font=ImageFont.truetype(str(fontpath),18)
gallery=Image.new('RGB',(960,1495),(32,35,34));draw=ImageDraw.Draw(gallery)
for i,(n,title) in enumerate([('long','中央梯段 / 长边'),('bend','中央梯段 / 转角'),('alley','东巷 / 旧箅子所在处'),('road','南区路 / 新旧路肩'),('court','篮球场 / 西侧座椅'),('room','西侧住宅 / 窗后'),('front','巷对面 / 面馆'),('shop','面馆 / 门外'),('threshold','面馆 / 门槛'),('prep','面馆 / 后场')]):
    x=i%2*480;y=i//2*299
    gallery.paste(Image.open(shot(n)).resize((480,270),Image.Resampling.LANCZOS),(x,y))
    draw.text((x+9,y+271),title,font=font,fill=(231,225,203))
gallery.save(here/'本轮十个原生机位.jpg',quality=91)
motion=read(here/'motion/rooms_walk.json')
assert motion['passed'] and len(motion['takes'])==2
for take,name in zip(motion['takes'],['从街边走进面馆','横过住宅窗前']):
    frames=[Image.open(here/'motion'/('frame_%03d.jpg'%row[0])).convert('RGB').resize((680,382),Image.Resampling.LANCZOS) for row in take['frames']]
    frames[0].save(here/(name+'.webp'),format='WEBP',save_all=True,append_images=frames[1:],duration=84,loop=0,quality=81,method=4)
profile=hashed(project/'assets/render_profile_r24.json')
now=read(here/'current/capture_manifest.json');prior=read(here/'prior_final/capture_manifest.json')
assert not now['failures'] and not prior['failures'] and now['art_profile_sha256']==profile
assert len(now['captures'])==len(prior['captures'])==10
results={}
for q in list(qa.glob('*.json'))+[qa/'walk/rooms_walk.json']:
    r=read(q);ok=r.get('passed',r.get('success'))
    assert ok is True and r['art_profile']['sha256']==profile,q
    results[q.relative_to(qa).as_posix()]=ok
assert len(results)==15
paths=[here/'city_and_connections.blend',here/'17b_default.json',here/'native_source_checks.json',here/'promenade_failure.json',here/'surface_hits_first.json',here/'rail_hits.json',project/'project.godot',project/'assets/render_profile_r24.json',project/'scripts/qa_context.gd',project/'scripts/main.gd',project/'scripts/district_connections_r24.gd',project/'scripts/junction_editor_preview.gd',project/'docs/DISTRICT_PRODUCTION_STANDARD.md',project/'docs/DISTRICT_CONNECTIONS_R24_REVIEW.md',project/'assets/connections_r24/connections.glb.import']
for folder,pattern in [(here,'*.py'),(here,'*.gd'),(here,'*.ps1'),(here/'player','*.png'),(here/'current','*'),(here/'prior_final','*'),(here/'motion','*'),(here/'prior_timing','*.json'),(here/'timing','*.json'),(qa,'**/*.json'),(project/'assets/connections_r24','**/*'),(project/'shaders','*r24.gdshader'),(work/'assets_incoming/r24_noodle','**/PROVENANCE.json')]:
    paths.extend(x for x in folder.glob(pattern) if x.is_file())
notes=read(here/'native_source_checks.json')
assert notes['passed']
light=[]
for folder in ['third','current']:
    a=np.asarray(Image.open(shot('road',folder)).convert('RGB')).astype(float)
    light.append({str((x,y)):a[y,x].astype(int).tolist() for x,y in [(424,253),(428,252),(420,256),(439,249),(424,251)]})
index={'revision':now['art_profile'],'source':'R24 build 17b full editable scene plus the authored changes in this folder','blender':'4.3.2','godot':now['engine'],'renderer':now['renderer'],'profile_sha256':profile,'default_checks':results,'game_opened_at':'r24_join18_shop','screenshot_pixels_third_final':light,'static_source':notes,'visual_scope':'Ten engine views and two native takes. Player art approval pending.','files':{p.relative_to(work.parent).as_posix():hashed(p) for p in sorted(set(paths))}}
(here/'evidence.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),'utf8')
print(len(index['files']),len(results),light)
