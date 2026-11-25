# 重庆外卖王 · 500 米城区试作

默认项目是 `work/project/chongqing_godot_v05/project.godot`。Godot 4.6.3 运行项目进入 `first_shift.tscn`，按原来的方式向老彭报到，完成教学后可沿出区道路自由活动。独立检出从 R24 build 25b 游戏提交 `ce1841b079b78c1f876bfa0da3b8b6a404ac9532` 开始，云端工具安装脚本来自 `0253cada1833dc66fa6a93f12e6af373451e99a4`。

## 试玩入口

在云端桌面终端执行：

```bash
cd /workspace/chongqing-500
export GODOT_BIN=/workspace/work/runtime/.cloud-dev/tools/bin/godot
bash work/scene_r24/district_500/play.sh --software -- --explore-500
```

人物出生在东侧接头，面前是自己的电瓶车。靠近并看向车按 **E**，**W** 前进，**A／D** 转向，**空格**刹车。停稳按 **P**，再按 **E** 下车。顺中兴路向外探索，反向回到旧城区。试玩参数跳过教学，适合核对交界和外圈，常规存档由默认启动读取。首次启动可能要等软件驱动编译街区着色器。去掉 `-- --explore-500` 可跑默认首日。Windows 桌面可直接用同一版本 Godot 从工程运行，或启动控制台程序时给引擎参数末尾加 `-- --explore-500`。首次检出请先执行 Godot 的 `--headless --editor --import`。

## 文件和重建

- `outer_district.blend` 是可独立打开的 Blender 4.3.2 新区，打包了源纹理。它含道路支撑、建筑和梯坎、路灯与树、南侧桥下接坡及范围外视觉过渡。
- `city_and_outer.local.blend` 是云端可重开的整城组合，由 `compose.py` 产出。它重定位原三个人物库及现有外链图片，并相对链接 `outer_district.blend`。它在本地保留，工作站可用同一脚本生成。
- Godot 增量在 `work/project/chongqing_godot_v05/assets/district_500/`，包含 `outer_district.glb`、表面分区纹理、路牌子集字体和布局。场景启用后由标准碰撞构建器用导出网格建立支撑。
- `terrain_baseline.json` 来自原 Blender 200 米地形五个网格，内接基准覆盖四个边界。 `road_ties.json` 来自原生 Godot 25b 横断面，用旧路边标高和坡度收头。桥下使用低位射线，避免把桥面量作地面。
- `evidence/` 保存本轮实跑文件。 `probe.gd` 重新量横断面并拍固定视角。 `routes.gd` 使用玩家控制器跑代表路径；每段只有起始就位，往返两腿分别就位。路线固定输入由脚本给出。软件图像的条件见随附报告。

在仓库根目录，先恢复项目运行资产和指定整城源依赖，再执行：

```bash
blender -b work/scene_r24/district_patrol/city_and_patrol.blend \
  -P work/scene_r24/district_500/measure_baseline.py
blender -b -P work/scene_r24/district_500/build.py
python work/scene_r24/district_500/build_font.py
blender -b work/scene_r24/district_patrol/city_and_patrol.blend \
  -P work/scene_r24/district_500/compose.py
```

需要更新道路接头时，先用 `probe.gd -- --baseline --day-one-test` 测原场景，将输出的 `sections.json` 传给 `register_ties.py`，再导出。Blender 使用自带 NumPy，字体脚本使用 Python FontTools 和原仓库 `work/assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf`。

## 坐标和来源

地理原点沿用 `source_data/geo_layout.json` 的 WGS84 经度 106.56445、纬度 29.55325，使用米制东／北坐标。新增支撑外包围至东、北各 ±250 米，原样板与核心路径保持原坐标。Blender 为 Z 向上，Godot 为 Y 向上且北向负 Z。岸线落在测量范围内的水域部分保留为水面。

- 南区路两幅车道、中兴路、东侧横街、马蹄街和解放西路走向来自已有 OSM 派生数据。原始要素 ID 为 49182408、1189963598、176034707、734116597、1513362409、830761786。岸线读取 `source_data/river_r22/river_plan.json` 中长江关系 9087399。
- 部分外围住宅按原 OSM 轮廓重建，精确 ID 见 `layout.json`。近地基础按新地表落地，缺少高度或实景立面的部分按游戏设计补齐。新增坡度、沿江步带、北脊转折、桥下接坡、支路和市场等门面用途为游戏化设计。路名标示的是场景方向，维修铺、市场和茶摊的布置为原创。
- 地理数据 © OpenStreetMap contributors，ODbL 1.0。派生要素的可复查出处保留在项目数据、上述布局和重建脚本。纹理为既有资产复用，来源见游戏内 `assets/material_provenance.json`、`assets/CREDITS.txt`。路牌为重新命名的 Noto Sans CJK SC 子集，许可见 `assets/fonts/R20_OFL.txt`，原版本见 `assets/fonts/first_shift_sources.json`。[OSM 数据许可](https://www.openstreetmap.org/copyright)
- MAX 派生远景记录及其仅供内部参考的用途仍见 `docs/CITY_FRAME_R24_REVIEW.md` 和 `work/scene_r24/city_frame_11864101/sources.json`。试作首日入口禁用该本地远景。新增导出只引用 OSM 派生坐标、项目已登记纹理和本轮原创建模。
