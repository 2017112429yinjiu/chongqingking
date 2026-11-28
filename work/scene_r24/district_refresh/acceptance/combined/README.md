# 20 处联合实测与 R24 build 25b

正常首班场景加载五个增量图层。Godot 4.6.3 下 18 条公共路线分别原地折返，36 个方向都通过。34 新街肩接入原巷去 11.95 米、回 11.99 米。52 的高低两层、53 石梯、54–56 共巷、00 修车和 01 实际取送各留专项记录。 [联合走测](acceptance-walks.json) · [分组验收与试玩入口](../README.md) · [南片专测](../south/refinement)

凉亭子全长去 172.43 米、回 172.42 米，各 61 个目标点。马蹄街、凉亭子、管家巷各自去回均完成，三巷连续去 413.75 米、回 414.31 米，各 152 个目标点。34 初版墙脚曾卡住马蹄街长线，保留实际失败。复测把墙脚移到高侧，栏顶仍保留在登记位置。 [三巷原始记录](../north/refinement/43-long-street_group_profiles.json) · [34 原失败](../west/refinement/34-original-wall-blockage.json) · [34 栏顶投影](../west/registered-rail-projection.json)

43 南街中心像素仍命中原门台支承，距 4.166 米，固定眼里的横匾局部被挡。走进檐下可见绿色横匾、窗栏和错层立面。22 个原踏面与平台上表面逐顶点相同。56 旧私门保留被挡的失败，共巷去回继续通过。 [43 眼位及台阶](../north/refinement) · [56 已知缺口](../south/FRONTAGES.md)

Blender 4.3.2 重开后，组合城 4,790 个物体，五个图层声明的 142 个物体均已找到。独立源与 GLB、JSON 在各区域目录随分支交付。 [组合重开记录](combined-source.json)

## 正式巡检

Linux 运行 Windows district_patrol/verify.ps1 -AllRoads -Timing 对应的原生 GDScript、数据和版本。物理样本以固定帧率运行。原生画面使用 Xvfb/Mesa llvmpipe Compatibility，沿用云端软件档的太阳阴影设置。标准计时使用 1152×648、三个观察位和原计时脚本。软件补测保留各帧的墙钟间隔，供同类环境比较。

运行时可指定 Godot 4.6.3 与 Blender 4.3.2 的完整路径，使用新 QA 目录。

    bash work/scene_r24/district_refresh/acceptance/combined/verify-linux.sh /tmp/cq-r24-fresh

外围 GLB 的 84 块有效地表网格在东西、南北方向的顶点范围均为 −250 至 +250 米。正常场景在四个距中心 249 米的测点均测得外围地面。七处中心接缝各采 325 点，合计 2,275 点均测到支承。 [外围顶点足迹](500-export-footprint.json) · [真实碰撞横断面](500-core-edge-sections.json)

另按早期 500 米固定路线测了五条路径的走、骑及往返，共 20 段。西、东、东高、北的 16 段通过。南线步行与骑行去程各达 5/6、返程各达 0/6，约在 E66/N−136 和 E98–99/N−126 止步。使用同一 Godot、输入、原采点和固定帧率，关闭本轮验收增量重现制作父版的四个停点；四处停点坐标最大差约 2.5 毫米。一次骑行去程最后接触从原地表切换到既有滨江裙房，仍停在同一处。 [早期外围模式 20 段原记录](500-legacy-modes.json) · [旧南线与本轮对照](southern-legacy-parent-comparison.json) · [父版原始轨迹](southern-legacy-parent-raw.json) · [本轮原始轨迹](southern-legacy-current-raw.json)

同一候选另测了南区路西端接回原车道、176968735 接 176034697、1189963552 接 176034697。三个已登记接头的两向实际骑行均通过。这组使用各自实际地表，是独立于上表早期南线的路径。 [现有南向接头实骑](southern-mapped-join-rides.json)

## 本次实际结果

正式巡检素材提交为 `5787c14158f33f2d1a53e5831ac010d4dfd3e21f`。最新试玩素材提交为 `034207b30a1f759dd9cb14287fc0e56dcca1a6a4`。后续素材更新仅涉及 00 的工作台、工具网格和色图。两个南片碰撞网格、其余网格及碰撞替换清单逐项相同，最终素材另跑原修车流程和新增斜近景去回。四区返图均为 Godot 原生帧。 [00 的最终实测与画面](../south/repair-evidence/README.md)

| 项目 | 实跑结果 |
|---|---|
| 正常首班 | 85/85，四个存读点正常 |
| 正常玩法 | 市场到 201、午单、单次下单、摊主交接、工作台打气和进院回街均通过 |
| 26 条原城芯地面道路 | 去 26/26，回 26/26，每向分 9、9、8 三批 |
| 原巡逻演示 | 14 条道路，28/28 个方向 |
| 路口原生巡检 | 67/67 |
| 跨街送达及重开 | 42/42，送达后存档重开退出 0 |
| 原北缘核对 | 旧标高或旧支承规则 260 个失败。停用本轮图层，原失败值一致。北缘窄缝、原步行往返及两张原生图正常 |
| 原计时脚本 | 软件运行超时，退出 124。补测 switchback 8 帧，墙钟中位 14962.8 毫秒，crossing 8 帧，墙钟中位 19974.2 毫秒，301 8 帧，墙钟中位 18394.2 毫秒 |

云桌面无可用的 ALSA 音频设备，窗口实际使用 Dummy 音频后端。

[完整实测摘要](actual-summary.json) · [原生数字、命令和日志](original-numerical-output.tar.gz) · [原始文件 SHA](raw-file-manifest.json) · [北缘父版对照](north-parent-comparison.json) · [实际打开的试玩画面](playable-window.png) · [窗口状态](playable-window.json)
