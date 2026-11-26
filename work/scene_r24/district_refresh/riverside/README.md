# 500 米城区刷新 · 第二批 · 长滨路滨江步道

游戏从第一批 `23f206c8` 继续。在正常 `first_shift.tscn` 接入长滨路滨江步道，沿游戏内实测落地三角面裁切铺装，原地形继续承载玩家。铺装贴面抬高 15 mm，西侧接驳的接头抬高 28 mm 以免面片互相闪烁。低岸用暖红石砖，园路用偏冷石砖，两侧用窄水泥边带。纹理复用项目原已入库的 `stone_floor_diff_2k.jpg` 和 `concrete_floor_worn_001_diff_2k.jpg`，原参考影像只用于判读。视线、店铺、院落、任务目标和基础地形继续采用第一批的场景。

## 图源与地块

按原航片配准读取低岸带、上层灰色园路、西侧接头和能看清的东园路。四段宽分别为 3.30、3.10、1.85、3.00 米，切得 705.32、441.15、37.90、192.84 平方米，各段名义面积极小误差内都有底部支承。路缘设计宽采用游戏尺度。西接头在下层 `(-205,-210)`、上层 `(-200,-191)` 接两条路，接头中间的曲线和各段高度服从现有游戏地表。东侧林冠下的走向缺逐点地面照，已做可达性试走。东园路的铺装止于航片可读处。长滨路当代路线记录载有桥下儿童乐园、运动场地和经储奇门的滨水线。当前资料没有给出游戏局部坐标原点对应的实地高程，照片年代也有差异。[第一批图源与航片指纹](../README.md) · [滨江公园界](https://www.openstreetmap.org/way/1499726225) · [渝中区住建委](https://www.cqyz.gov.cn/zwgk_229/jytabl/rddbjy/202310/t20231009_12409956.html) · [2026 年长滨路实走线路](https://cq.people.com.cn/n2/2026/1113/c365402-41749706.html)

井字坐标使用同一游戏 EN 原点。23 个地块的实测竖向柱线与逐地块航片判读一起保存。4 号中心同时命中地形 7.933 m、高架面 8.699 m 和试作楼围护顶 9.920 m，属于值得单独复验的重合，既有核心轨道修复仍占用这个地块的游戏位置。58 号在航片上被桥覆盖，游戏中心柱线仅命中楼和地形。21、55、63、65 号的车道影像需同址核对层级。57、59、61 号在公园界内，当前室内和与街道相连的游戏走线保留。59 号实地体块用途和高度仍缺证。74、76 号保留为后续楼体实景核对对象。[地块层级实测](../evidence/riverside-site-layers.tsv) · [原逐地块航片判读](../evidence/aerial-readings.tsv)

用 Overture `2026-11-18.0` 的原 bbox 获取 166 项建筑，56 项 OSM 派生轮廓全部逐项复现了原项目登记。新 CLI 文件字节指纹为 `4270a1a4a7ca7adc745a543135be5c2fbaaa487bb02c35321f63eca2bde75a9d`，原批字节指纹另见 `mapped_group.json`。110 项来自 Qian Shi、Jiajun Zhu、Zhengyu Liu、Haonan Guo、Mengxi Liu、Zihong Liu、Xiaoping Liu，CC BY 4.0；56 项归属 © OpenStreetMap contributors，ODbL 1.0，由 Overture 分发。用原山城巷 OSM 控制点将两组 WGS84 轮廓变换为游戏 EN，叠合 70 个待核地块，26 个有面积重叠。74 和 76 号最大交并比分别为 0.33743、0.30128，对应重叠 66.270、46.867 平方米。这两个命中的来源未登记楼层；外墙、入口、地面和用途仍需查照片。地形和建筑未从机器轮廓推断高度。[每地块叠合结果](../evidence/overture-overlaps.json) · [Overture](https://docs.overturemaps.org/getting-data/cloud-sources/) · [Shi 等人](https://doi.org/10.5281/zenodo.8174931) · [OSM 许可](https://www.openstreetmap.org/copyright)

## 重建

使用 Blender 4.3.2 从底稿生成可编辑局部源和对应嵌入材质的 GLB。之后重作原整城本地组合，并用 Godot 4.6.3 导入。

```bash
blender -b work/scene_r24/district_500/outer_district.blend --python-exit-code 8 -P work/scene_r24/district_500/riverside.py
blender -b work/scene_r24/district_patrol/city_and_patrol.blend --python-exit-code 8 -P work/scene_r24/district_500/compose.py
godot --headless --editor --import --path work/project/chongqing_godot_v05
GODOT_BIN=/path/to/godot bash work/scene_r24/district_500/play.sh --software -- --explore-500 --riverside
```

`survey.gd` 读铺装登记并以 60 Hz 固定频率走双向。将 `CQ_QA_DIR` 指向新的目录，Godot 使用 `--headless --fixed-fps 60 --path work/project/chongqing_godot_v05 --script work/scene_r24/district_refresh/riverside/survey.gd -- --day-one-test --explore-500 --riverside`。以相同参数运行 `access.gd` 验证原 200 米动线、37、42、76 号和中兴路加密线。机位图使用同一场景开关新增铺装，图形模式加 `--capture-riverside --qa-no-sun-shadows`。

重算轮廓证据需要 Overture CLI 2.1.1，NumPy、Shapely 2 与同一发行版切片。原有 `source_ground.py <旧批次.geojson>` 继续校验原字节并输出原 OSM 铺装控制。

```bash
overturemaps download -r 2026-11-18.0 -t building -f geojson --bbox 106.5618,29.55095,106.56715,29.55553 -o overture.geojson
python work/scene_r24/district_refresh/riverside/footprints.py overture.geojson overture-overlaps.json
```

## 本次云端实跑

- Blender 4.3.2 重开了独立步道源与原城组合。Godot 4.6.3 重导入后，默认启动和探索启动成功。500 米回归得到 7 处横断面、20/20 段运动和首班 85/85 项通过。
- 四条新铺装线走通 8/8 个方向，累计 879.44 米。主巡检通过 13/14 项，加密巡检通过 11/12 项。旧 200 米动线、37、42、76 号的入户楼梯，以及东园路接茶铺街均双向走通。新成功走线进入 12 个此前未覆盖的 100 米网格，两批合计进入 25/25 个网格。网格统计以采样点计。[滨江巡检](../evidence/riverside-walks.json) · [接驳加密巡检](../evidence/riverside-access.json) · [覆盖统计](../evidence/riverside-coverage.json)
- 中兴路 `176034707` 上坡返向两次在游戏坐标 `z` 约 −176 到 −178 米遇阻。两种采样间距的原始数据均保留。滨江入口到茶铺街的往返实走为 32.61 和 32.62 米。
- 原生五组同机位前后图使用 Mesa 25.0.7 llvmpipe 的 Godot Compatibility 渲染。第一版铺装过于均匀，检查街眼和低机位后换成带缝砖纹并重抓。第一次半途退出的图形采集与 Mesa 退出时的纹理报告随原始日志保留。待工作站复核 Forward+。
- 山城巷送单 12/12 项通过，两条来回路线分别实走 83.51 / 83.52 米、93.87 / 93.80 米。修车 10/10 项通过，模拟玩家步入、为踏板车充气到 2.4、穿院回街，实走 55.83 米。[首班和城区回归](run/regression.json) · [送单记录](run/handoff.json) · [修车记录](run/repair.json)
- 云桌面使用正常试玩入口进入滨江步道。窗口显示《重庆外卖王 · 梯坎里 R24 构建 25b (DEBUG)》及 500 × 500 米步行探索界面。[启动日志](run/play.log)

### 下层步道原生返图

西段同机位，改前。

![低岸西段改前](views/lower_west_before.jpg)

西段同机位，改后。

![低岸西段改后](views/lower_west_after.jpg)

走到东侧后回望西段。

![低岸步道回望](views/lower_return_after.jpg)

[机位和渲染器记录](views/cameras.json) · [图形运行日志](views/engine.log)
