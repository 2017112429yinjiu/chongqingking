"""Build comparisons and real-time replays using only saved Godot framebuffers."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
study=Path(__file__).resolve().parent
font=ImageFont.truetype(str(study.parents[1]/'assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf'),21)
def compare(before,after,name,captions):
    inputs=[Image.open(p).convert('RGB') for p in [before,after]]
    sheet=Image.new('RGB',(1440,442),(31,33,33));draw=ImageDraw.Draw(sheet)
    for i,im in enumerate(inputs):
        assert im.size==(1280,720)
        sheet.paste(im.resize((720,405),Image.Resampling.LANCZOS),(i*720,37))
        draw.text((i*720+12,3),captions[i],font=font,fill=(237,237,230))
    sheet.save(study/name,quality=93)
def compare_site(view,old,name,captions):
    f='godot_'+view+'.png'
    compare(study/old/f,study/'current'/f,name,captions)
compare_site('r24_west_life','before_final','西巷同机位对照.jpg',['构建 13 · 西巷梯坎','当前试玩 · 窗下择豆与街坊来往'])
compare_site('r24_chess_table','stance_current','院坝铺装对照.jpg',['修改前 · 棋桌旁的铺装边缘','修改后 · 铺装沿坡相接'])
compare_site('r24_west_bowl','paving/current','西巷案板对照.jpg',['初版 · 膝盖穿过案板和盆','复查后 · 调整桌下净空与双手动作'])
for name,label in [('court_take','院坝走棋.webp'),('west_take','走进西巷.webp')]:
    take=study/name;meta=json.loads((take/'take.json').read_text('utf8'));frames=sorted(take.glob('frame_*.jpg'))
    assert len(frames)==len(meta['frames']) and meta['reached']
    seq=[]
    for f in frames:
        with Image.open(f) as im: seq.append(im.convert('RGB').resize((720,405),Image.Resampling.LANCZOS))
    seq[0].save(study/label,save_all=True,append_images=seq[1:],duration=100,loop=0,quality=80,method=3)
    with Image.open(study/label) as saved:assert saved.n_frames==len(seq)
