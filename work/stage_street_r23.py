"""Copy authored R23 resources into the isolated playtest and register its actual camera poses."""
from pathlib import Path
import hashlib,json,shutil
W=Path(__file__).resolve().parent;S=W/'scene_r23'; project=S/'playtest';dest=project/'assets/block_r23'
dest.mkdir(exist_ok=True)
for f in (S/'assets').iterdir():
    if f.is_file():shutil.copy2(f,dest/f.name)
sources=W/'assets_incoming/r23_walks/sources.json'
shutil.copy2(sources,dest/'motion_sources.json')
v=project/'assets/viewpoints.json';cfg=json.loads(v.read_text(encoding='utf-8-sig'))
titles=dict(main_road='南区路沿街',laundry='球场边晾衣',shop_window='临街窗内',court_bench='球场长椅',
            shutter='梯坎便利',garden='树池与花坛',street_support='坡道接缝',brick='砖墙与墙脚')
for key,(pos,target) in json.loads((dest/'block.json').read_text())['views'].items():
    name='r23_'+key
    cfg['views'][name]=dict(position=pos,target=target,fov=67,title=titles[key])
    if name not in cfg['view_order']:cfg['view_order'].append(name)
v.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')

