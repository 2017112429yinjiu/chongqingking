# 59–61 号滨江园边铺地与树带

重庆日报龙帆 2023 年 10 月原片可区分 59 号周围的浅砂、浅蓝折线铺装、窄草带、灰石树池广场和纵向园路。规资局的反向实景可见桥侧树冠和铺装的相对关系。沿用上一批的道路、墩脚和铺地转角登记，照片用于观察点位和表面。颜色、粒径、石板缝宽、植物种类和具体株距采用试作尺度，61 号树冠下的低设施仍待核。 [59 号图源与配准](../park_plot59/field-controls.json) · [61 号图源与机位](../park_plot61/field-controls.json) · [规资局反向图](https://www.cqnews.net/web/content_1572174477726445568.html) · [重庆日报龙帆原片](https://epaper.cqrb.cn/cqrb/2023-10/26/004/cqrb20231026004.pdf)

`park-edge-finish.blend` 独立可编辑，六张自制底图均打包。它以六个局部网格替换既有园边表面，另加街口约 4.807 平方米灰石板补片和一条树带草坡。图案按米级世界坐标展开。组合城和游戏各自读同一组树木变换，放大五株现有树冠，在园边补三株实例，使用已有许可树木网格和材质。 [场景清单](../../../../project/chongqing_godot_v05/assets/district_500/park-edge-finish.json) · [植被许可](../../../district_500/README.md)

从仓库根目录用 Blender 4.3.2 执行，先取 `district_500` 原地形和 57、59、61、58–61 桥下批的 Blender 源，以及原工具引用的地形资料。以 Godot 4.6.3 导入增量 GLB。

```sh
blender -b work/scene_r24/district_500/outer_district.blend --python-exit-code 1 --python work/scene_r24/district_refresh/riverside/park_edge_finish/build.py
blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
godot --headless --path work/project/chongqing_godot_v05 --import
work/scene_r24/district_500/play.sh --software -- --explore-500 --park-59
work/scene_r24/district_500/play.sh --software -- --explore-500 --park-61
```

`surface_probe.py` 用于重开的组合城。Godot 脚本 `views.gd` 从标准场景走 59 号路线并记录固定机位，`--qa-without-park-edge-finish` 可恢复父版同机位。61 号使用上一批 `walk.gd` 来回实走。 [原图、路程与复核](evidence)
