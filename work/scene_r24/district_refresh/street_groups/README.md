# 500 米城区刷新 · 火柴坊

国浩用地南缘按 OSM `704006706` 的开放轮廓建一座火柴原料厂旧址，替换试作住宅 28、29。两栋旧轮廓分别与同一旧址相交 12.804、37.943 平方米，原先下街和西侧过往都撞旧围护。旧楼编号保留在地块档案中，常规连通和开口巡检跳过已被替换的两栋。山城巷取件台、修车铺和首班由原入口验证。

开放轮廓约 43.27 × 18.70 米，共 809.08 平方米，其中 582.44 平方米落在 500 米可玩方框内。越过东界的连续建筑轮廓落在现有视线范围，游戏地界仍为东向 250 米。独立 Blender 源可重开，合成脚本链接原城、原扩建和本批替换。沿墙真实底形支承的高度范围是 5.07 至 12.97 米，2.36 米铺装投影面积 66.08 平方米，整段贴合现有地面。

业主现场照片可辨灰砖柱、分格窗、浅拱券及青瓦歇山轮廓。坡下图的三道开窗带与 OSM `building:levels=1` 一并记录。墙基贴当前游戏坡形，高侧遮住部分底层。各层标高、入内门状态、铺装宽和看不见的室内采用游戏设定。可绕建筑走上下两侧。参考照片用于阅读体块与材料，贴图复用项目的灰砖、青瓦、石板和灰砂浆。业主 2023 简报第 34 页右图标记为实拍，可观察后续塔楼的蓝灰玻璃和暖金属边框。[开放轮廓](https://www.openstreetmap.org/way/704006706) · [业主火柴坊实景](https://18t-mansion.cn/humanities.php) · [业主 2023 简报](https://www.guocoland.com.sg/Documents/FS/2023/GLL_FY2023_Results_Presentation_31Aug2023.pdf)

## 逐地块叠合与碰撞

- 马蹄街 `59146654` 穿过 23、37、39 号旧轮廓 10.458、9.235、16.195 米，五线横断面实际碰到试作楼框架和围护。三处保留作马蹄街改造前证据。凉亭子研究图 3 提供区位、比例与北向，图 4 提供五处节点、五条巷道和可达关系。原图可观察砖石、台阶与临街界面，照片编号还需与路口独立对位。[凉亭子社区田野研究](https://www.shplanning.com.cn/archive/download/id/1312.html) · [重庆大学马蹄街营造](https://chongjian-lab.cqu.edu.cn/info/1012/2113.htm)
- 11 号分别压下回水沟 9.474 米、凤凰台路 10.587 米，77 号压厚慈街 9.500 米。2、55、62、66 号与长江滨江路主线分别叠合 14.227、10.440、10.898、17.501 米。抽样处记录地面和试作楼层。历史或当代真实道路的桥、隧、裙房层高仍需同址资料对照。
- 75 号中心在国浩 T1 `1374780314`，74、76 号位于国浩用地 `1374780311`，分别距 T2 外轮廓 5.604 米、T1 外轮廓 12.638 米。70 号中心落入 40 层 `1128648941`，单独登记。此批完成火柴坊外部，下批塔楼裙房需要确定各标高的公共入口。[T1](https://www.openstreetmap.org/way/1374780314) · [T2](https://www.openstreetmap.org/way/1374780313)
- 本次 OSM 全框下载 1,058,302 字节，SHA-256 为 `37c269b570deb778828e26766a62cde853d02a5e4663954612383426115e51a8`，用户保存副本的字节长度相同，指纹不同。换算重新使用游戏 `734116601` 原配准，登记各 way 版本与节点、叠合长度及采样坐标。归属 © OpenStreetMap contributors，ODbL 1.0。[逐地块登记](run/plot-registration.json) · [原碰撞剖面](run/street_group_profiles.json) · [OSM 许可](https://www.openstreetmap.org/copyright)

## 重建与试玩

从仓库根目录使用 Blender 4.3.2 重建。先重算 28、29 号的旧网格面归属，然后生成独立源文件、增量 GLB 和同批运行清单。退役脚本逐面核对 float32 顶点指纹，保留其他地块和第一批石梯挡墙改动。

```bash
study=work/scene_r24/district_refresh/street_groups
outer=work/scene_r24/district_500
game=work/project/chongqing_godot_v05
out=$(mktemp -d)
CQ_OUTER_PLOT_IDS=28,29 CQ_OUTER_PLOT_OWNERSHIP="$out/owners.json" \
  blender -b --python-exit-code 8 -P "$outer/build.py"
blender -b "$outer/outer_district.blend" --python-exit-code 8 -P "$study/factory.py" -- "$out" "$out/owners.json"
cp "$out/match_factory.blend" "$study/"
cp "$out/match_factory.glb" "$out/match_factory.json" "$game/assets/district_500/"
blender -b work/scene_r24/district_patrol/city_and_patrol.blend --python-exit-code 8 -P "$outer/compose.py"
godot --headless --editor --import --path "$game"
GODOT_BIN=/path/to/godot bash "$outer/play.sh" --software -- --explore-500 --match-factory
```

Godot 4.6.3 用不同的新 `CQ_QA_DIR` 和 `--headless --fixed-fps 60 --day-one-test --explore-500 --match-factory` 运行 `walk_factory.gd`。脚本的用户参数加 `--qa-without-match-factory` 测旧碰撞，加 `--capture-factory` 启动有图形的原生定机位。拍摄结果同时记录相机和当前渲染器。

## 实测结果

- Blender 4.3.2 重开 9 个对象的独立源，核到火柴坊碰撞体 4,966 面。原城组合随 10 个源库重开。Godot 4.6.3 重导入的最终 GLB 指纹为 `ab742e6b12ad0b52c4cffef0f8342e1a957b59de5cfe3abde4dd691f853d76c6`。
- 三条步行线旧版通过 2/6 个方向，旧楼围护挡住低街和西侧接驳。新版通过 6/6，低街 27.72 / 27.78 米，高侧 22.75 / 22.72 米，西侧串接 23.18 / 23.16 米，累计 147.30 米。新建筑碰撞体和旧组件实际退役另有 12 项检查，全部通过。[旧版失败与剖面](run/walks-before.json) · [最终实走](run/walks-after.json)
- 同一导出下，山城巷送单 12/12 项通过，修车铺 10/10 项通过。[送单记录](run/handoff.json) · [修车记录](run/repair.json)
- 云桌面正常入口打开《重庆外卖王 · 梯坎里 R24 构建 25b (DEBUG)》，显示火柴坊下街和 500 米步行探索 HUD。[备用启动记录](run/play.log)
- 原 200 米使用仓库 `-AllRoads` 的地面采样和六个骑行批次，Godot 4.6.3 固定 60 Hz 运行，26 条地面路去程、回程各 26/26，四个历史地下路线按原规则排除。探测 16,004 个断面站点、10,000 个地表网格点。原 `timing.gd` 在 Xvfb 用 Vulkan Forward+ 软件设备 llvmpipe 启动，400 秒超时，未生成计时 JSON。[骑行和计时记录](run/core-road-regression.json)
- 中兴路两处上坡接触分别落在现有山脊挡土网格面 7850、7848，距离误差 0.10 / 0.13 毫米。后续修正以这两处接触、原地面及同址市场裙房关系定位。[中兴路接触几何](run/northeast-wall.json)

### 原生返图

相同下街机位，改前。

![火柴坊下街改前](views/lower_wall_before.png)

相同下街机位，改后。

![火柴坊下街改后](views/lower_wall_after.png)

沿新铺装走到东侧回望。

![火柴坊下街回望](views/return_after.png)

三张图为 Godot 原生 PNG，云端渲染使用 OpenGL 4.5 Compatibility 和 Mesa llvmpipe。[最终机位和后端](run/cameras-after.json) · [改前机位](run/cameras-before.json)
