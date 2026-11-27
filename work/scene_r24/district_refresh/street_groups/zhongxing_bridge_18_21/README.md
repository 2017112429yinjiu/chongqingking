# 中兴路立交 18、21 号分层

| 地块 | 地图和同址实景 | 运行内容 |
| --- | --- | --- |
| 18 | OSM 上层 `59146775` 距旧中心 0.179 米、穿旧足迹 16.285 米。2023-05-15 同址两侧能分辨上层花带、护栏、下位行车和分隔设施。 | 撤下与原立交相交的旧住宅及附属。保留原 R24 桥面、车行宽、箱梁和墩，沿已登记上缘制作低花槽。桥面用正常电瓶车实走，逆向仅作封闭验收。 |
| 21 | 上层 `59146775` 距旧中心 3.612 米、穿旧足迹 18.584 米。2019-06-29、07-01 三个低位角度交叉确认梁腹、桥下绿带、路侧栅栏及其外侧步行带。2023-05-15 同址补证桥上花带、下层坡路和车道分隔。 | 撤下穿桥的另一栋住宅，保留 R24 结构。沿图中可见的步行面做贴地灰铺、濒桥绿栏和低植，步行绕开在用车道、不穿桥墩或栅栏。 |

2019 年照片是低位设施的历史证据。2023 年分隔栏挡住部分桥底，绿栅用作已见边界的游戏表达，最新同址延伸范围待核。脚路 `1328811306` 是相距 22.187 米的另一处 −1 层过街通道。18 下层花带背后是否可供公众横穿仍待核。摄影坐标使用近似平面绑定，照片高度没有用于建模。路幅、地面级差和结构高程使用游戏的父版碰撞及开放线位。 [上层道路](https://www.openstreetmap.org/way/59146775) · [下层中兴路](https://www.openstreetmap.org/way/1189963552) · [−1 层过街线](https://www.openstreetmap.org/way/1328811306) · [逐帧出处和观察](registered-views.json)

贴纹来自项目已有许可的石铺和混凝土素材。护栏、花槽、紫红花叶与阔叶为独立几何。21 首次跟随原坡的外缘有一处表面法线 Y 约 0.677。最终浅石铺帽沿实测地形找坡，行走带内横坡约 3.4%，两端贴回原地面，石侧立面封到旧地面。位置、高程、宽度按模型实测，待实景补测的绿化品种和铺砖尺寸不作实体主张。

从仓库根目录用 Blender 4.3.2 重建。先生成父版组合，再制作和复开独立图层。GLB 与 JSON 输出目录放在本批游戏资源处，Blender 源保存在此目录。

```sh
site=work/scene_r24/district_refresh/street_groups/zhongxing_bridge_18_21
assets=work/project/chongqing_godot_v05/assets/district_500
CQ_ZHONGXING_PARENT=1 blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.before_zhongxing_18_21.local.blend --python-exit-code 1 --python "$site/build.py" -- "$assets"
blender -b "$site/zhongxing-bridge-18-21.blend" --python-exit-code 1 --python "$site/check_source.py"
blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --zhongxing-bridge-21
```

Godot 4.6.3 通过正常 `first_shift.tscn`。21 巡检 `walk_21.gd` 使用 `--explore-500 --zhongxing-bridge-21`；18 巡检 `ride_18.gd` 使用原教学电瓶车的真实控制与物理。两者用全新 `CQ_QA_DIR`，引擎 `--headless --fixed-fps 60`，游戏参数 `--day-one-test --qa-still-frames`。原版对照加 `--qa-without-zhongxing-18-21`。固定原生返图用 `fixed_views.gd` 和 `--a2-views` 指向 [相机定义](views.json)。 [验收与原始统计](evidence/README.md)
