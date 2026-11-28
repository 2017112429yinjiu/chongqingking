# 中兴路与照相巷 01、12、22

父版 `cb36b07c1128acdd871923610bf6704c6ac5d57a`。五组固定机位使用同一视图矩阵、投影矩阵与 700×440 窗口。后两组为不同视角的同一个花池。原图来自 Godot 4.6.3 Compatibility / Mesa llvmpipe。[逐图矩阵与 SHA-256](evidence/fixed-views.json)

| 地块 | 制作与实景范围 | 正常场景实走 |
|---|---|---|
| 01 照相巷便民市场 | 原市场柜台分出釉面售卖台和冷灰干货台，补木面、金属拉手与台上反光罩。陈设属既有玩法；来源可支持巷旁通行面，未证实同址柜台。 | 街肩到摊主 11.85 米（4/4），按 E 取货，厅内 2.86 米（2/2），交接一次入账，再按 E 未重复记账，沿原通道返街 14.90 米（6/6）。 |
| 12 沿街瓦檐 | 沿已定位的双层红柱瓦檐，重做两层独立瓦条、椽头和石脚；门后用途待证。三眼交会 E219.414/N104.337，最大侧向残差 0.782 米。 | 原公开廊沿去 6.08、回 6.15 米，各向 5/5；未穿门。 |
| 22 圆端花池 | 保留已验公共灰铺支承，沿既有曲线切合分段压顶，补草叶与低植株。2019 四眼可辨外侧分缝铺装、圆端与树撑。 | 公共铺地去 18.20、回 18.10 米，各向 12/12，去回连续接地采样 26/26 和 25/25，留 48 个压顶与外沿断面。 |

[逐地块出处与控制 ID](../../evidence/plots.tsv) · [正常取送脚本原输出](evidence/market-handoff.json) · [12/22 路线原输出](evidence/acceptance-walks.json) · [22 接地报告](evidence/planter-walk.json) · [48 处压顶断面](evidence/cap-sections.json)

| 机位 | 父版 | 本版 |
|---|---|---|
| 01 主厅回望 | [图](evidence/before/01-hall-look-back.png) | [图](evidence/after/01-hall-look-back.png) |
| 01 取件柜台 | [图](evidence/before/01-pickup-counter.png) | [图](evidence/after/01-pickup-counter.png) |
| 12 街边双瓦檐 | [图](evidence/before/12-field-axis.png) | [图](evidence/after/12-field-axis.png) |
| 22 花池回望 | [图](evidence/before/22-return-axis.png) | [图](evidence/after/22-return-axis.png) |
| 22 西侧近面 | [图](evidence/before/22-west-near.png) | [图](evidence/after/22-west-near.png) |

Blender 4.3.2 重开五件新网格及外链材质；Godot 4.6.3 重新导入并在正常首班内运行三项测试。初稿导入曾因区域变量的类型推断失败，改为显式字符串后通过。[源码复开输出](evidence/blender-reopen.log) · [初次导入失败原输出](evidence/failed-first-import.log)

从 [试玩脚本](../../../district_500/play.sh) 进入时，01 使用 `--explore-500 --outer-market`，12 或 22 使用 `--explore-500 --refresh-plot=12` 或 `--refresh-plot=22`，各参数放在脚本的 `--` 后。
