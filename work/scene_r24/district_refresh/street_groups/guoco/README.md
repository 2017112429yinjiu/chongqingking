# 国浩 18T 与火柴坊街面

本批在原场景 `first_shift.tscn` 接入双塔、公共裙房通道及火柴坊近窗更新。地图用同一组山城巷控制点和 500 米坐标。开放地图几何归属 © OpenStreetMap contributors，按 ODbL 1.0 使用。来源照片仅作观察。组合城通过相对路径链接各批 Blender 源。

| 旧编号 | 地图及同址材料 | 实际替换和依据边界 |
| --- | --- | --- |
| 74 | 旧占位在宗地 1374780311，到 T2 轮廓约 5.6 米 | 撤去独立试作楼，按 1374780313 开放轮廓制作 T2。重庆日报对云领 T2 记为 193 米、51 层，OSM 轮廓标签为 42 层。当前采用报道高度与分带，报道楼名和该轮廓的最终对应仍需现场复核。 |
| 75 | 旧中心落在有 42 层标签的 T1 轮廓 1374780314 | 依开放边界制作 T1，外窗折转、暖金属条和暗玻璃参考开发商实景。151 米为游戏制作值，待核实外墙实高。 |
| 76 | 旧占位在宗地 1374780311，至 T1 约 12.6 米 | 撤去旧独立住宅，试玩中用两翼裙房、上下街和中间公共通道表达地势。桥跨、通道净空、花岗石边沟的确切尺寸是游戏设计。原 74–76 的可选虚构住户空间随三栋占位撤回。 |
| 28、29 | 已合并的火柴坊位于 704006706。业主街面照片可辨木框、小窗格及开启方式 | 原砌体、券柱和歇山体量沿用。78 个窗位加独立分格、内凹玻璃及多档色值，做一扇半开启窗示范，具体开启位置是游戏制作选择。临街增石边沟和路缘。 |

国浩实拍和年代核查见 [开发商 2023 简报第 34 页](https://www.guocoland.com.sg/Documents/FS/2023/GLL_FY2023_Results_Presentation_31Aug2023.pdf)、[年度报告印刷页 30](https://www.guocoland.com.sg/Documents/AnnualRpt/AnnRep2026.pdf)、[重庆日报 2024 年报道](https://epaper.cqrb.cn/cqrb/2024-11/18/031/content_rb_339489.htm)、[建筑师多标高街口说明](https://www.lwkp.com/wp-content/uploads/2020/12/20201215-O-Newsletter_Issue-237_Link_Compressed.pdf)。火柴坊窗与砖柱见 [业主街面观察](https://18t-mansion.cn/humanities.php) 与 [同址报道](https://app.cqrb.cn/dichan/2021-10-15/996703_pc.html)。源与建筑本体授权以项目原登记为准。T3A 的地图轮廓在制作框东缘、仅局部入框，法国领事馆轮廓在框外，两处继续列于来源登记。

## 重建和回归

- `field-registration.json` 保存开放轮廓及坐标、来源指纹与旧地块交叠。云端原始 XML 为 1,058,302 字节，SHA-256 为 `37c269b570deb778828e26766a62cde853d02a5e4663954612383426115e51a8`。它与桌面首报的同框 XML 指纹不同，两份快照分别登记。可用项目当前 OSM XML 执行 `python register_sites.py <osm.osm> <field-registration.json>`，依赖 Shapely。保留同位置的原始开放地图控制点。
- 使用 Blender 4.3.2 打开 `work/scene_r24/district_500/outer_district.blend`，以 `-P work/scene_r24/district_refresh/street_groups/guoco/build.py -- <输出目录>` 生成可编辑 Blender、GLB 和运行清单。依赖同一检出里已经校验的火柴坊、马蹄街、中兴路及桥西增量。按旧地块登记的面指纹继承此前已改接坡和家具。
- Godot 4.6.3 下 `walk.gd` 用正常控制器验证三条路线双向和实物碰撞，`views.gd` 导出同机位。用 `--day-one-test --explore-500 --match-factory`。旧画面额外带 `--qa-without-guoco`。首次下街路线西端落入另行登记的 24 号楼。第二轮去程碰到旧 25 号楼角。保留两轮失败，最后一轮沿两栋旧楼外的公共地面验收。

本批 Godot 4.6.3 实测，上下街、塔间公共路线按去程和回程共走通 6/6，340.33 米。火柴坊 18 项检查和 6 个走行方向通过，修车 10/10，山城巷外卖 6/6。区内原版检验脚本通过 7 组地表断面（2,275 点）、10 段步行、10 段骑行和首班 85/85。裙房下沿测试净空 4.34 米。数字、原始行走迹线和两轮旧路线失败见 `evidence/`。

原生返图使用 Godot Compatibility、Mesa llvmpipe、800 × 450。火柴坊回望、近窗、双塔分别保存同机位改前和改后，裙房下单列街眼图。测试保留了老建筑前景、开口通道和土地接边。云端未采集 Windows Forward+ 帧时间。通过原 `work/scene_r24/district_500/play.sh --software -- --explore-500 --match-factory` 从火柴坊步行街进入。

后续的中兴路收藏品市场（旧 8、9、11 的邻地）及杏林学校、蔡家石堡（旧 43、44 的邻地）已在坐标表登记，须分别核实地表、车库入口、旧路接头及在用玩法。
