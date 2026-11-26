# 500 米城区刷新 · 首批

起点为 `b065d7a5`。本批处理已有原机位和碰撞记录支持的问题，并登记滨江地块的用地证据。先读 [全图巡检](../map_review/README.md) 和 [原 71 地块台账](../map_review/PLOTS.md)。

## 实改与保留

- 山城巷西北四栋、仁爱堂两翼及 54、56 号的地形按场景登记墙基精确分片。墙内地表高点降至登记地坪以下至少 60 mm，墙外点仍在原三角面上。保留原有地面材质、铺地、门槛、楼体与基础。
- 37 号石梯的挡墙在下端横穿踏步净宽。只截断该墙上和现有踏步相交的 2.50 m，保留两翼、梯级及楼体。
- 42 号的现有植株移到楼西侧空地，由该点原地形确定根部标高。近景扫描、远景树冠和树干碰撞使用同一新位置，保留植株原材质和比例。
- 13、14、31、63、67、71、74 号仍是植被待核点，保存顶点侵入量与室内视角。1、2 号保留经平台转折的既有入口。地块用途、室内布置或建筑轮廓需要同址证据，未在本批重定。

替换网格在 Godot 创建碰撞前加载。Blender 组合场景链接同一套修正，原 `outer_district.blend` 和 `outer_district.glb` 作为底稿。

## 航片与江岸照片

`plot_sources.py` 按原地图的坐标原点为 71 个地块和 33 个 OSM ID 建立索引，归入 25 个百米分区。地图和影像仅支撑位置、用地或外部形态判读。在航片上，4、58 号部分投影到桥面，21、55、63、65 号与车行空间相叠。叠合说明下一轮应先查高差和道路权属。高架下方还需要地面照片。

57、59、61 号地块中心位于登记公园界内。57 号靠蓝面场地和桥边园路，59 号靠小体块和斜入的园路，61 号在树冠及阴影内。2023 年南纪门桥照片可见沿岸行道树、蓝面球场和低层设施，2018 年石板坡照片可见车道、绿带和当时的拱顶设施。尚未逐一确认三处地面标高、建筑用途或室内。原照片和航片未作游戏贴图。[滨江公园 OSM](https://www.openstreetmap.org/way/1499726225) · [Esri World Imagery](https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer) · [南纪门桥，2023](https://commons.wikimedia.org/wiki/File:2023-06-22_Nanjimen_Yangtze_River_bridge.jpg) · [石板坡桥，2018](https://commons.wikimedia.org/wiki/File:Shibanpo_Bridge_20180501_081333.jpg)

航片为 1600 × 1600，使用 EPSG:3857，查询边界 `11862384.4391,3445935.1103,11863016.1823,3446570.0754`，SHA-256 `54ba3944fea775e513e9c23e304db170c7ab7a48eb9880fdc619dc6a6f790273`。索引采用局部切平面近似，桥缘和屋角需用登记坐标再核。仍待补齐的范围包括原区和其余试作地块的同址照片、9 处重复院房、68 间普通房，以及店铺、书架、学校展陈逐项复验。

## 重建与复测

从仓库根目录运行。修正源继承原地形与扫图植株的贴图和材质，未引入外部贴图。

```bash
CQ_SAVE_PATCH=1 blender -b work/scene_r24/district_500/outer_district.blend --python-exit-code 8 -P work/scene_r24/district_500/interior_terrain.py
blender -b work/scene_r24/district_patrol/city_and_patrol.blend --python-exit-code 8 -P work/scene_r24/district_500/compose.py
godot --headless --editor --import --path work/project/chongqing_godot_v05
```

使用 Blender 4.3.2 与 Godot 4.6.3。每项以新的绝对路径设定 `CQ_QA_DIR`。室内探测脚本的 `CQ_REGISTERED_PROBES` 指向原 [巡检结果](../map_review/evidence/summary.json)。楼梯复测使用原 `approaches.json`，来自原巡检包的 `approaches/` 目录。固定机位复刻读取同包 `play/views.json`。图形记录使用 Mesa llvmpipe，关太阳阴影。与原 Windows 机位相同的对照仅用于几何与可见范围，渲染器与曝光条件可能不同。

## 云端第一批复测

组合源复开成功，含 8 个修正对象。78 处室内共 48,868 对有效样本，高于完成面 15 mm 的采样从 466 个降到 0 个。Godot 在原六个内点命中外区真实地形碰撞，净低 78–102 mm。四栋西北房门洞 8/8 向通过。

37 号两侧及中线从街上进门与反向出门均通过，合计 6/6，单程 6.91–7.01 m。原入口复查共 38 向通过 36 向。1、2 号右侧直接斜切仍撞柱，两栋经平台转折的进出均通过。保留失败轨迹。山城巷取送与修理院的交互分别通过 12/12 和 10/10。

全区 71 个穿堂、68 间普通房共 136 次进出和首班初始化均通过。71 个正门双向直走由 132/142 增至 133/142，仅 37 号进门的结果变化。跨区步行、骑行各 10 段全部通过，实走 1,452.73 m、实骑 1,450.63 m，轨迹采样进入 25 个分区中的 13 个。其余分区不能由该路线集的通过推定。

Godot 实际保存 18 张云端原生图。56 号露出原地砖，42 号窗内无原枝叶，37 号梯脚与反望可见净宽和两翼挡墙。固定机位保存了其余七处植被候选的画面，待补窗内反向及不透明像素的逐点查验。640 × 360 请求下，游戏生成 1180 × 663 的图。Compatibility 渲染日志保留了 Forward+ 次表面散射提示、V-Sync 提示和程序退出时的两条纹理资源告警。正常试玩加载至山城巷取件台。

首轮缓存导入缺 53 号的两张提取纹理，复跑前重新导入该 GLB。下列数据来自完整资产的复跑。[地面前](evidence/floors-before.json) · [地面后](evidence/floors-after.json) · [运行时碰撞](evidence/floor-contacts.json) · [石梯与失败](evidence/stairs.json) · [门洞](evidence/mapped-doors.json) · [正门直走](evidence/approaches.json) · [穿堂与普通房](evidence/all-halls.json) · [跨区步行骑行](evidence/outer-roads.json) · [送单](evidence/handoff.json) · [修车](evidence/repair-walk.json) · [镜头坐标](evidence/views.json) · [地块索引](evidence/plot-sources.json)
