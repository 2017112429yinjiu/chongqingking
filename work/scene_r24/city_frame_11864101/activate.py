import json
from pathlib import Path
p=Path(__file__).resolve().parent
base=p.parents[1]/"project/chongqing_godot_v05/assets/render_profile_r24.json"
original=base.read_bytes()
historical=p/"build10_profile.json"
if not historical.exists():
    assert b'R24_market_terrace_10_internal' in original
    historical.write_bytes(original)
source=json.loads(historical.read_bytes())
views=json.loads((p/'review_views.json').read_bytes())
views.update({
"r24_court_entry":{"position":[-17.5,21.68,2.7],"target":[-21.55,20.23,.34],"fov":65,"title":"球场东口 · 梯坎接头"},
"r24_west_seam":{"position":[-73.7,16.88,25.35],"target":[-71.95,15.7,19.0],"fov":58,"title":"西巷梯坎与院路"},
"r24_center_seam":{"position":[-20.1,18.83,24.0],"target":[-18.0,17.1,18.0],"fov":62,"title":"中央梯坎与院路"},
"r24_lower_seam":{"position":[6.0,13.13,61.6],"target":[.9,11.6,57.2],"fov":63,"title":"中央梯坎下段铺面"}
})
source["diagnostic_views"].update(views)
(p/"baseline_profile.json").write_text(json.dumps(source,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
source.update(art_revision="R24_city_frame_11_internal",street_finish_r24=True)
base.write_text(json.dumps(source,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
(p/"review_views.json").write_text(json.dumps(views,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

