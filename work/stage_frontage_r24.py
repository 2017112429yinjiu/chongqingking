"""Install the new authored layer and camera coordinates in the R24 scratch checkout."""
from pathlib import Path
import shutil,json
S=Path(__file__).resolve().parent/'scene_r24';P=S/'playtest';A=P/'assets';dest=A/'frontage_r24';dest.mkdir(exist_ok=True)
for src in (S/'assets').glob('*'):
    if src.is_file():shutil.copy2(src,dest/src.name)
profile=json.loads((A/'render_profile_r23.json').read_text(encoding='utf8'));profile.update(market_r24=True,traffic_lanes_r24=True,washcloth_shader='res://shaders/washcloth_r24.gdshader',art_revision='R24_market_terrace_10_internal')
(A/'render_profile_r24.json').write_text(json.dumps(profile,indent=2,ensure_ascii=False),encoding='utf8')
view=A/'viewpoints.json';data=json.loads(view.read_text(encoding='utf-8-sig'))
titles=dict(stall='南区路菜摊',counter='菜筐与台秤',repair='坡边修配铺',stairs='上下街梯口',court='球场看中央梯道')
titles.update(viaduct='南区路下梯看高架',junction='中兴路与南区路',verge='桥下分流岛')
for key,(eye,aim) in json.loads((S/'assets/frontage.json').read_text())['views'].items():
    name='r24_'+key;data['views'][name]=dict(position=eye,target=aim,fov=65,title=titles[key])
    if name not in data['view_order']:data['view_order'].append(name)
view.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
(P/'verification_r24').mkdir(exist_ok=True);(P/'verification_r24/.gdignore').touch()

