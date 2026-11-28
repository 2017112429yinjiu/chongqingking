# 10 号中兴路砖廊实测与返图

测试从正式 `first_shift.tscn` 进入。父版相同街边起点走 5.446 米、1/8 路点，在 E239.464／N154.746／Y48.699 碰到旧壳。终版从街缘到檐下 25.867 米，原地掉头返回 25.907 米，各 8/8，全程零卡停、零重置，路点踏面 9/9。三条登记视线原先都受挡，最终全部通到柱间同一观察点。280 个同位上下剖面中，父版 39 点命中旧 10 号框架，终版为零，280 个原地形命中保持一致。父版与候选都用 4.6.3 固定 60 帧作运动验证。[父版堵点、各帧位置与碰撞](before/blocked-walk.json) · [终版去回与视线](after/round-trip.json) · [父版断面](before/surface-profiles.json) · [终版断面](after/surface-profiles.json) · [断面对照](surface-comparison.json)

独立制作源由 Blender 4.3.2 复开，公共步线九处均有踏面，五处檐下净空 4.231–5.130 米，九件退役实体未再出现。铺地局部匹配工程现有地表。现场绝对标高、门后范围与具体店号仍待核。[独立源复开](after/blender-reopened.json) · [组合城复开](after/combined-reopened.json) · [复开日志](after/blender-reopened.log) · [Godot 导入](after/godot-import.log) · [同址实景登记](../registration.json)

## 原生同机位

Godot 4.6.3、Mesa llvmpipe Compatibility，700 × 440，前后各组使用相同视图矩阵、投影和日照。初件在固定视图中几乎读不出砖色和开口，保留作为失败记录。终版补可辨门框、暗门洞和分段灰铺，并处理路缘接头。[机位与图片 SHA‑256](view-comparison.json) · [初件](failed/first-dark-frontage.png)

| 固定机位 | 父版 | 终版 |
|---|---|---|
| 南侧 42° | [PNG](before/south-42.png) | [PNG](after/south-42.png) |
| 北侧 90° | [PNG](before/north-90.png) | [PNG](after/north-90.png) |
| 2021 正面 89° | [PNG](before/history-89.png) | [PNG](after/history-89.png) |
| 街缘入廊 | [PNG](before/walk-approach.png) | [PNG](after/walk-approach.png) |
| 檐下向街 | [PNG](before/under-arcade-return.png) | [PNG](after/under-arcade-return.png) |

实际玩家相机另存街缘、掉头和回街三张 900 × 560 原图，完整原生运动也通过两向各 8/8。[街缘](player/street-at-the-new-curb.png) · [檐下回望](player/under-the-eaves-look-back.png) · [回到街面](player/returned-to-the-street.png) · [同场原生运动](player/round-trip.json)

相邻边界复测。11 号凤凰台坡口去回 9.544／9.531 米，各 4/4。中兴收藏市场主厅去回 23.208／23.205 米，各 7/7。26 号既有公共边去回 17.680／17.720 米，各 5/5。[凤凰台](after/regression-11.json) · [市场](after/regression-market.json) · [26 号](after/regression-26.json)
