# 马蹄街、凉亭子与管家巷

依照已登记的公共街线，撤下横压马蹄街的 23、36、37、39 号试作单体和压住凉亭子的 7 号试作单体。马蹄街分别穿过四处旧轮廓 10.458、8.060、9.235、16.195 米，凉亭子穿过 7 号 2.665 米。共用网格按已验证的原面指纹改动，户内玩法和实际街线分开登记。沿马蹄街和凉亭子制作用于游戏的 3.12、2.51 米石料铺带，在原公共接点连铺，局部加石路缘和排水边。管家巷沿现有坡地通过。 [道路登记](../run/plot-registration.json) · [OSM 许可](https://www.openstreetmap.org/copyright)

凉亭子 43 号旧后梯的 204 个归属面横在路中。旧梯改成坡侧两跑共 20 级，转角有石落脚台，沿既有地形落地，保留原楼后门标高。正门路线亦复测。另在管家巷与凉亭子高侧两处挡土面开出 2.60、2.80 米净宽，沿两边保留山脊挡墙与原地表。

社区调查与同址营造记录可辨窄巷、石阶和邻接路径。图 3 的候选配准留一误差 4.39 至 29.81 米，图 4 的照片只用于阅读公开空间形态。蔡家石堡 5、7 号间升降梯经现场报道确认上接马蹄街、下接优雅广场和熊猫公馆，高差 15 米，具体井道落位须另取双锚。亦庐、长乐永康、厚庐和金马寺小学的门牌、连接与实景证据见 `field-controls.md`。本批恢复公共路线与 43 号两向接入，围绕旧地块的历史街墙和院落继续按独立定位复核。[社区调研](https://www.shplanning.com.cn/archive/download/id/1312.html) · [马蹄街营造](https://chongjian-lab.cqu.edu.cn/info/1012/2113.htm) · [现场控制点](field-controls.md)

## 制作与复验

从仓库根目录用 Blender 4.3.2 重算旧面归属、生成独立源和增量 GLB。云端 Linux 以 `OPENBLAS_NUM_THREADS=1` 固定归属计算。输出源链接进 `district_500/compose.py` 所建的组合城。图形和物理都通过常规 `first_shift.tscn` 进入本区。

```sh
outer=work/scene_r24/district_500
matix=work/scene_r24/district_refresh/street_groups/matix
assets=work/project/chongqing_godot_v05/assets/district_500
out=$(mktemp -d)
OPENBLAS_NUM_THREADS=1 CQ_OUTER_PLOT_IDS=7,23,28,29,36,37,39,43 \
  CQ_OUTER_PLOT_OWNERSHIP="$out/owners.json" blender -b --python-exit-code 8 -P "$outer/build.py"
blender -b "$outer/outer_district.blend" --python-exit-code 8 -P "$matix/build.py" -- "$out" "$out/owners.json"
cp "$out/matix_streets.blend" "$matix/"
cp "$out/matix_streets.glb" "$out/matix_streets.json" "$assets/"
godot --headless --editor --import --path work/project/chongqing_godot_v05
GODOT_BIN=/path/to/godot bash "$outer/play.sh" --software -- --explore-500 --matix-streets
```

为每次测量创建独立的 `CQ_QA_DIR`。Godot 4.6.3 使用 `--fixed-fps 60 --headless`，用户参数 `--day-one-test --qa-still-frames --explore-500 --matix-streets`。街线脚本为上级 `measure.gd`，另加 `--walk-registered-streets --walk-joined-streets`。`approach.gd` 单独实跑 43 号正门、后梯。`views.gd` 用原生图形渲染记录同机位，对照运行可加 `--qa-without-matix-streets`，并使相机和后端一致。

## 实测与原生返图

马蹄街、凉亭子、管家巷 6 个方向均通过。三巷连续去／回 413.75、414.31 米，各走到 152 个目标点，接头无重置。43 号原正门两向 4.58、4.57 米，改建后梯 17.73、17.67 米。原坡面保留 182 个五点断面记录。火柴坊 18 项、取送后上金马寺图书馆 6 项、修车 10 项及首班 85 项通过。[实测汇总](checks.json)

通堂与玩法房巡检 187/187。外墙开口脚本仍记录 0 号修车院旧窗清单为 0、物理窗洞为 14，开关本批几何时逐项结果相同。原指向 0 号的门厅、送修及交互另行实跑通过。

Blender 4.3.2 复开独立源的 9 个网格。整城重开 11 个源库。Godot 4.6.3 重导入通过。原生 PNG 使用 OpenGL 4.5 Compatibility 与 Mesa llvmpipe。两张凉亭子同机位看到旧梯从横穿街线变为在坡侧转向，回望验证铺装与新挡墙接边。周边部分街墙、背景楼体和绿地仍为待复核的试作。[改前](views/before.png) · [改后](views/after.png) · [回望](views/return.png)
