# 山城巷西北段与临街铺地

后续批次已撤下送单两端的四块旧楼，接通仁爱堂和金马寺小学。下文记录西北段的上一轮制作。[收件院口新批次及 71 块待核清单](../shancheng_courts/README.md)

从[山城巷取一单](../../沿山城巷送一单.cmd)进入 Godot 4.6.3 的正常城区。走近取件台按 E，带着纸袋沿山城巷走，或从山城第三步道绕行，在仁爱堂外的公共交接架按 E 签收，收入 6 元。默认首日教学完成后也可前往。两个交接点是游戏设计。

## 现实依据

四栋新增的一层房屋采用同一坐标系下的独立建筑轮廓。西北弯道上的位置、朝向、各角点和层数来自地图。可查 [704006729](https://www.openstreetmap.org/way/704006729)、[704006732](https://www.openstreetmap.org/way/704006732)、[704006733](https://www.openstreetmap.org/way/704006733) 和 [704006741](https://www.openstreetmap.org/way/704006741)。[坐标、GERS 标识和楼层记录](mapped_group.json)

公共步道沿山城巷和第三步道的三条真实线形建模。用原图的 67 个共用节点配准到项目坐标，最大残差小于 5 毫米。这表示两份数据的配准误差。实际街道、地形及房屋的位置精度受源地图限制。[山城巷](https://www.openstreetmap.org/way/734116601) · [第三步道](https://www.openstreetmap.org/way/734116600) · [连接段](https://www.openstreetmap.org/way/734116599)

灰瓦、灰白墙面、木窗、挑檐、石门槛和室内木柱梁参考渝中区老街资料及项目实拍。门位、分间、檐高、地坪和铺装边界按游戏尺度制作，缺少逐栋实测。仁爱堂照片所见的建筑群与单个地图轮廓范围不同，本轮仅在外围步道设置交接点。[渝中区山城巷介绍](https://www.cqyz.gov.cn/zjyz/lyyz/ctjq/202210/t20221005_11164462.html) · [山城巷保护规划](https://www.cqyz.gov.cn/bm_229/lswhjqgwh/zwxx_97154/dt/202112/t20211206_10082904.html) · [仁爱堂资料图](https://www.cqyz.gov.cn/zjyz/lyyz/lswh/tk/202504/t20250421_14541659.html) · [项目材料与照片来源](sources.json)

原试作的 32 号楼和基础占用实有步道，已撤下。[全区轮廓叠合图](evidence/footprint_map.png)对照了全部 75 个旧地块与本次有来源的建筑多边形。其余 75 个旧试作地块有些承担教学或住户玩法，实际建筑对应关系仍待核对。旧地块尺寸已在生成器中冻结。以后拓展实际建筑须有可辨认的坐标、建筑群及来源，记录哪些细节有照片、哪些需要推断，逐段替换旧模型。

## 铺地与高差

按登记道路、建筑临街面、住户院坝和实际步道补石板、条石边沟与入口铺地。道路蒙版优先保留车行面。另取同区域 56 条 OSM 建筑轮廓，用于估算门前硬地范围。滨江公园的登记边界从这部分推断中排除。河岸及远离建筑的坡面仍可见土壤和草。铺装类型和宽度为复原设计。[地面依据及公园边界](frontage_controls.json) · [滨江公园](https://www.openstreetmap.org/way/1499726225)

24 段保留住宅入口的楼梯改为沿墙上行，碰撞和可见踏面使用同一网格。取件和送达两条走法在同一点会合。住宅间的共用巷在 11 号楼阶侧增加了转弯，55 与 57 号之间沿挡墙保留原可通行路线。

## 重建

从仓库根目录运行。使用 Blender 4.3.2，先还原本项目的 Git LFS 资产。

```bash
blender -b --python-exit-code 8 -P work/scene_r24/district_500/build.py
blender -b work/scene_r24/district_500/outer_district.blend --python-exit-code 8 -P work/scene_r24/street_blocks/mapped_lane.py
blender -b work/scene_r24/district_500/outer_district.blend --python-exit-code 8 -P work/scene_r24/street_blocks/ground_context.py
python work/scene_r24/district_500/build_font.py
blender -b work/scene_r24/district_patrol/city_and_patrol.blend --python-exit-code 8 -P work/scene_r24/district_500/compose.py
godot --headless --editor --import --path work/project/chongqing_godot_v05
```

打开 [可编辑巷道与四栋房屋](shancheng_lane.blend)。完整整城由上面的组合步骤生成。用 `CQ_QA_DIR` 指向新的绝对目录，从工程运行本目录的 `views.gd`、`walk_mapped.gd`、`doorways.gd`、`walk_stairs.gd`、`checkpoint.gd`。其中 `views.gd` 需图形窗口。用 `handoff.gd -- --explore-500 --shancheng --day-one-test --qa-still-frames` 验证取送，固定物理频率为 60 Hz。

地图版本 Overture 2026-11-18.0，范围见 `mapped_group.json`。以 Overture CLI 下载 buildings/building 类型、GeoJSON 格式和所列 bbox，原批次含 166 要素。仅使用带 OpenStreetMap 来源的要素。建模读取仓库中的派生数据，无需在线查询。用 `source_ground.py <原批次.geojson>` 可由该次下载重新生成铺地依据。坐标数据 © OpenStreetMap contributors，经 Overture Maps Foundation 提供，ODbL 1.0。[Overture 下载说明](https://docs.overturemaps.org/getting-data/cloud-sources/) · [OSM 许可](https://www.openstreetmap.org/copyright)

[固定机位对照](evidence/street_comparison.jpg) · [测试与迭代记录](evidence/README.md)
