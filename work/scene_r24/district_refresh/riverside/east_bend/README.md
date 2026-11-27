# 雷家坡东弯与 67–69 号地块

- **67** 的旧独栋穿过 `1375242615` 和 `1375242617` 上层车道。弯道内侧的上下层梁、圆柱和导流区以完工斜照、正射和历史对向街景为依据。
- **68** 的旧中心在下层路肩与树池一侧。2020 年同址两向可见相邻楼座连续浅色竖分格和深色横向百叶，2024、2025 年正射在旧中心保留浅铺地、树及窄边。游戏恢复公共步行带和树池，沿内侧放置两向可辨的楼座背景。折角及层距采用试作尺度，地下连通、背面和权属留待核查。 [向 39°](https://mapsv0.bdimg.com/?qt=pr3d&panoid=09029200122004271206551753O&heading=39&pitch=0&fovy=80&width=900&height=560) · [向 306°](https://mapsv0.bdimg.com/?qt=pr3d&panoid=09029200122004271206537123O&heading=306&pitch=0&fovy=80&width=900&height=560)
- **69** 的旧独栋跨 `1256839997` 和 `1375242615` 弧面车道。外弯延续到 `1256840008`，内弯沿登记的 `1375242616`、`1375242618` 方向落坡。滨江壹号 70 号留在独立登记。

63–66 原机位所见的两处断头分别沿 `1324001438 → 1256840006` 与 `1256840000 → 1256840005` 补到洞口。低层 `1324001436` 和 `1375242613`、上层 `1256839997`、`1375242615` 和 `1375242617` 与路面的 `59146737`、`1256859184` 分层。车库五片封板撤下，转角可见层间深度和竖分格。长滨路灰路贯通原草坡断点，加白色分道线、两处红色磨耗层区间的方向箭头和分流标线。高程以现有游戏地表和登记节点拟合，真实洞内纵断面、实测标高和标线坐标仍待核。 [原图、四类登记及位置边界](field-controls.json)

地图来源为 © OpenStreetMap contributors，ODbL 1.0，沿用 `734116601` 控制点。龙帆原片、两期正射、渝中规资实景和百度图仅用于核对。增量不含这些照片。铺地和混凝土沿用既有项目制作材质，与源材质链接表一起记录。树池实例共用许可树木 `Outer500_Plant_018`。 [许可及控制](../../../district_500/README.md) · [龙帆原片](https://epaper.cqrb.cn/cqrb/2023-10/26/004/cqrb20231026004.pdf) · [2024 正射](https://www.arcgis.com/home/item.html?id=24efa4fabd92463d805bfd82ef8f8b32) · [2025 正射](https://www.arcgis.com/home/item.html?id=b4c5c1b59c4141c5b503335b5baa2df4) · [渝中区规资局照片](https://www.cqnews.net/web/content_1572174477726445568.html)

## 重开、导出和试玩

从仓库根目录，使用 Blender 4.3.2 和 Godot 4.6.3。组合城保留父版链接，`raijiapo-east-bend.blend` 可单独重开并编辑，需还原之前批次的 Blender 材质库。GLB 的增量对象在原 `first_shift.tscn` 载入，十个替换网格复用原有导入材质。

```sh
CQ_EAST_PARENT=1 blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.before_east.local.blend --python-exit-code 1 --python work/scene_r24/district_refresh/riverside/east_bend/build.py
blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.local.blend --python-exit-code 1 --python work/scene_r24/district_refresh/riverside/east_bend/check_source.py
godot --headless --path work/project/chongqing_godot_v05 --import
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --raijiapo-east
```

`walk.gd` 使用正常 `first_shift.tscn`，用全新 `CQ_QA_DIR` 和 `--fixed-fps 60`，游戏参数为 `--day-one-test --qa-still-frames --explore-500 --raijiapo-east`。原机位用 Compatibility、900×560 窗体和 `--qa-no-sun-shadows` 复拍。 [画面、检测及实走](evidence)
