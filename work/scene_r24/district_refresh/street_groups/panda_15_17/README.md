# 熊猫古玩城中兴路临街 15、17 号

在原 500 米游戏内重做中兴路 228 号的两个相邻公开街面。以 OSM 步行线 `734116598` 和中兴路 `176034707` 的走向校准旧足迹、两处独立街景机位与近年正射。较低店面与橙框门廊之间有同一排梁柱和同向步行带。公开地图与相片均保留来源，照片像素留在云端作观察。

| 旧地块 | 位置与可确认形态 | 公开路线 |
| --- | --- | --- |
| 15 | E176.158 / N40.523。旧中心离步行线 7.489 米，街景可见凹入橙框入口，正射可辨宽前场和相连裙房。 | 从北侧外街走进门廊外槛，到可见铺地一端原地转身返街。窗后和门内按退进的封闭背景建模。 |
| 17 | E158.075 / N21.021。步行线穿旧足迹 11.337 米，独立前景为公交候车棚、树池、盲道、低栏及低店窗。 | 从南侧同一街边步行带经过站棚，到低栏边回望后原地返街。下层铺户入口、内部及公交班次待核。 |

街景在 2023-05-15 拍摄。 归档正射的原始采集日期已按旧地块中心分别读回，为 2024-03-25 和 2025-05-20。元数据平面绝对精度为 8.47 米。道路分叉和连续裙房一起用于比对，把照片中的铺装细部单独登记。向左和向右的原始视线均能在相邻门廊、同排树池、纵向店面和道路识别上互证。2025 年蔡家石堡报道所述下口接熊猫公馆和优雅广场，国浩在街对面。门廊与公共人行铺装按照照片可见范围制作。真实柜台排布、铺装分格、树种株距和裙房背面尚待现场核实。 [逐地块地图、视线与航片](field-registration.json) · [2025 年公共电梯实景](https://www.cqnews.net/1/detail/1341846153863208960/app/content_1341846153863208960.html)

使用深浅两档灰石旗、竖纹石柱、分层压顶与暗色退进窗。树冠和已有许可模型共用网格。首层局部收檐、橙框进深及石栏按游戏尺寸调到可通行。原 15、17 旧楼、虚构住户空间、楼梯和附属碰撞按面指纹退役。

从仓库根目录使用 Blender 4.3.2 重建，Godot 4.6.3 导入并在同一正常主场景进入相应地块。

```sh
site=work/scene_r24/district_refresh/street_groups/panda_15_17
game=work/project/chongqing_godot_v05
CQ_PANDA_PARENT=1 blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.before_panda.local.blend --python-exit-code 1 --python "$site/build.py" -- "$site"
mv "$site/panda-15-17.glb" "$site/panda-15-17.json" "$game/assets/district_500/"
blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b "$site/panda-15-17.blend" --python-exit-code 1 --python "$site/check_source.py"
godot --headless --path "$game" --import
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --panda-15
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --panda-17
```

从 Godot 正常场景用 `walk.gd` 走双向并原地转身。用全新 `CQ_QA_DIR`、`--fixed-fps 60`、游戏参数 `--day-one-test --qa-still-frames --explore-500 --panda-15` 或 `--panda-17`，父版用 `--qa-without-panda-frontage`。 [返图与实走](evidence)

第二轮按 15、17 的同址店面与候车带补折纹石柱、窗台招牌和暗门廊，保留公共入口。换立树、封树池边沿、分格触砖。站牌和浅陈列用独立制作内容。钢石和树材使用项目已有许可素材。正常玩家回望沿用 Explorer；独立静帧排除第一人称身体网格。固定镜头诊断用 `camera_audit.gd`，成对父版用 `fixed_cameras.gd`、`--qa-without-panda-frontage` 及 `--a2-views` 参数指向 `views.json`。17 的 `--panda-visual-details` 追加近看。 [同机位、取图诊断和正常玩法](evidence/visual-review/README.md)
