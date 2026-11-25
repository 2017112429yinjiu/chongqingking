# 500 米城区试作 · 云端复核

此报告保留初次云端提交 `e99e544f` 的模型哈希、软件渲染和实跑结果。后续修订、同机位比较及硬件结果见[街面复核](../expansion_review/README.md)。

## 候选和工作区

检出位于 `/workspace/chongqing-500`，分支为 `prototype/district-500`，父基线为 R24 build 25b 的 `ce1841b079b78c1f876bfa0da3b8b6a404ac9532`。新增地形、接坡及建筑导出提交为 `6960350e193aea3da28ca0b73de0cde893ef5e84`。其后的改动校正了门面牌字的遮挡和探索界面的范围文字，并纳入复核记录。

实际试玩入口、重建命令和资产来源见 [README](README.md)。Godot 运行增量 `outer_district.glb` 的 SHA-256 为 `442810882d006fa417820d5d6ae245f5b00012407806b6460c8f73275d2b8470`，文件大小 65,131,720 字节。独立 Blender 源 `outer_district.blend` 大小 34,782,084 字节，SHA-256 为 `ac3a0365a33b2f5b3a05382a0fe4e48b7864921150a4edd12f3b226fa8ef45b7`。整城可编辑组合保留在云端的 `city_and_outer.local.blend`，可由同版 Blender 从两层重新生成。

原 200 米城区接回南区路、中兴路、东侧高位横街、马蹄街和南侧桥下通道。扩区内有 81 处新层建筑体量，其中三处按已登记的 OSM 轮廓重建。维修铺、市场、江岸茶摊及临街梯台由游戏设计。桥下接坡从原下层路面分出，保留上层栏杆。范围外设视觉缓坡，河岸依据原 OSM 关系裁出水面。

## 实测

| 项目 | 结果 | 证据 |
| --- | --- | --- |
| Godot 4.6.3 | 新增 GLB 和项目通过导入，默认游戏进入第一天报到，东侧快速试玩启动。默认场景生成 378 个静态碰撞体，构建失败列表为空。 | [导入](evidence/godot-import.log) · [默认启动](evidence/physics/default.log) · [探索启动](evidence/physics/explore.log) |
| Blender 4.3.2 | 关闭后重开独立新区和整城组合。独立新区含 84 个地表对象、185,166 个地表三角面，材质图片均已打包。整城组合重开为 3,638 个对象，其中新区链接 92 个，四个库均解析，缺失链接列表为空。 | [实测范围](evidence/blender/blender_footprint.json) · [组合重开](evidence/blender/reopen.log) |
| 足迹及剖面 | 实际地表网格东、北均跨 `−250…+250 m`。四向外围点命中新区地表，东 16.859、西 5.587、北 49.060、南 −12.797 米。7 处横断面共 2,275 个射线命中。代表中心线内外各取 0.04 米，实测标高差 0.0–8.4 毫米，含该 0.08 米内的纵坡。 | [基线剖面](evidence/baseline/sections.json) · [候选剖面](evidence/physics/sections.json) |
| 玩家步行和骑行 | 西、东、东北、北、南五条代表路线，两个方向，各用玩家步行与车控制器跑一段，共 20/20 通过。步行 1,452.72 m，骑行 1,450.71 m。十段车行全部实际完成上车、刹停、停车和下车。每段只在起点放置，路线内最大单物理帧位移 0.093 m。南侧走桥下，桥面隔离栏保留。 | [轨迹及接触](evidence/physics/routes.json) |
| 第一日 | 用既有首日回归跑完 85 项，覆盖三单、老彭等候、跟做及老彭独立补送。首日和路线均用正常项目入口。 | [结果](evidence/first_shift/first_shift.json) · [日志](evidence/first_shift/engine.log) |
| 原生画面 | Godot 4.6.3 Compatibility，Mesa llvmpipe，1180×663，取景时关阴影。留原区同机位、总览、市场、五处接缝正反低机位。东侧高位横街另留 28 张连续骑行帧，每 9 个 60 Hz 物理帧取样一次。 | [原区基线](evidence/baseline/core.png) · [同机位候选](evidence/still/core.png) · [总览](evidence/still/overview.png) · [市场台地](evidence/still/east_market_landing.png) · [桥下反向](evidence/still/south_back.png) · [第一张骑行帧](evidence/motion/ride_000.png) |

## 失败和保留问题

- 首轮走查发现旧版玩家与车的回收范围，视觉走查发现市场门前高差、总览外缘断边及南侧试线跨过上层栏杆。已改用新区回收范围，市场加门前平台与梯坎，外缘接出过渡缓坡，南侧下移到桥下。初次试跑轨迹和画面保存在 `evidence/failed/`。东侧连续骑行采集时探索 HUD 仍显示旧尺寸，该文字已改为 500 × 500。
- 目前新铺装与老路相接时可见色差，市场等门面的生活细节与乔木材质仍需后续细化。外圈目的地以街面通行为主，新增门面室内及外圈配送任务未纳入本试作。高处总览仍能见到旧地形轮廓和远景过渡。
- 软件图像用于场地及接缝检查。Compatibility 对继承的次表面着色有警告，退出时原版和候选都有两条 GL 贴图清理诊断。首日、地面和路线记录来自无图形输出的独立运行。暂缺 Windows 原生全巡检和硬件 Forward+ 帧时，留给桌面用既有基线机位与剖面对照。
- 首次导入时 Godot 从旧 GLB 提取纹理，写回了八个已有贴图文件。已逐一恢复基线 SHA-256，并核对全部已恢复 LFS 实体。少量原生画面采集在这次恢复前，街区网格与剖面哈希一致。
- LFS 批量请求曾返回 `Resource not accessible by integration`。恢复使用媒体端点，逐文件校验大小和 SHA-256。仅取游戏目录（排除历史验证图）、指定源、一个对照图和路牌源字体。试作分支推送被 GitHub 以 HTTP 403 拒绝，远端 `main` 仍为 `0253cada1833dc66fa6a93f12e6af373451e99a4`。工作站交接压缩包包含增量 bundle 和本次变更新增的 LFS 文件，并提供还原脚本。


## 磁盘与桌面交接

工作区初始 `df -h` 为 32 GiB 卷、888 KiB 已用、约 30 GiB 可用。候选导入、Blender 组合与采集后为约 8 GiB 已用、约 23 GiB 可用。Git LFS 本地缓存约 3.1 GiB，Godot 导入缓存约 1.6 GiB。云端工具按工作流固定的 SHA-256 安装，版本为 Godot 4.6.3、Blender 4.3.2 和 Git LFS 3.8.1。历史验收材料保留文本与指针，工作区以本地 Godot 忽略标记阻止导入未恢复的早期历史截图。

ZIP、独立 bundle 和校验和位于云端 `/workspace/shared/downloads/chongqing-500-handoff/`。ZIP 内的接收说明面向具有原基线的独立桌面检出。增量文件实体包含 Blender 源、GLB、地表分区、字体及图片证据。从包内执行 `restore-lfs.py` 会逐项验证，再写入接收检出的 LFS 缓存。云端 403 的原始记录在 [push.log](evidence/push.log)。
