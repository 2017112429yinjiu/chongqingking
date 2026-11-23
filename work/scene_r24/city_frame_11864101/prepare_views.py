from pathlib import Path
import json
root=Path(__file__).resolve().parent
project=root.parents[1]/"project/chongqing_godot_v05"
baseline=root/"build10_profile.json"
profile=json.loads((baseline if baseline.exists() else project/"assets/render_profile_r24.json").read_bytes())
views={
"r24_canopy_joint":{"title":"院落雨棚 · 连接","position":[-4.85,17.66,31.2],"target":[-1.38,18.50,28.72],"fov":60},
"r24_canopy_under":{"title":"院落雨棚 · 檐底","position":[-1.43,17.86,28.1],"target":[-.45,18.71,29.6],"fov":75},
"r24_hoop":{"title":"社区球场 · 篮板","position":[-33,22.20,6.4],"target":[-34,23.72,11.18],"fov":51},
"r24_frame":{"title":"渝中城市框架 · 楼群","position":[-60,122,110],"target":[850,109,-650],"fov":56},
"r24_frame_walk":{"title":"临街向渝中眺望","position":[-23.92,9.435,81.05],"target":[39,17,4],"fov":67},
"r24_step_edge":{"title":"中央梯坎 · 侧沿","position":[-26.4,14.1,49],"target":[-19,14.8,41],"fov":65}}
(root/"review_views.json").write_text(json.dumps(views,ensure_ascii=False,indent=2),encoding="utf8")
profile["diagnostic_views"].update(views)
(root/"baseline_profile.json").write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding="utf8")

