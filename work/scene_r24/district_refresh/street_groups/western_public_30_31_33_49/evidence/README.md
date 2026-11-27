# 室外实走与固定相机

实跑正常场景，转身由同一个玩家身体完成。使用 Godot 4.6.3，固定相机两组同矩阵，原生 PNG 900×560，OpenGL Compatibility 和 Mesa llvmpipe。

| 地块 | 去 m | 回 m | 路点 | 折返点距旧边 m |
| --- | ---: | ---: | ---: | ---: |
| 30 | 9.370 | 9.427 | 6/6、6/6 | 19.94 |
| 30-garden | 11.827 | 11.755 | 6/6、6/6 | 1.11 |
| 31 | 10.095 | 10.065 | 6/6、6/6 | 19.41 |
| 31-garden | 7.144 | 7.107 | 6/6、6/6 | 16.77 |
| 33 | 8.070 | 8.042 | 6/6、6/6 | 3.26 |
| 49 | 9.655 | 9.581 | 6/6、6/6 | 9.38 |
| 01 | 9.892 | 9.935 | 3/3、3/3 | — |
| 52 | 14.155 | 14.169 | 6/6、6/6 | — |

33 在距离2015年登记立管 1.045m 的室外铺带折返。市场01实际从街肩到原公共主厅，再回到街肩。52记录81个碰撞断面和外侧现有斜地通行，实际道路和用户可访问层分开登记。

- 33_to_30_public_junction 为 4.740 米。
- 30_junction_back_to_33 为 4.727 米。
- 33_to_31_public_junction 为 5.251 米。
- 31_junction_back_to_33 为 4.906 米。

[正常场景身体轨迹](walks-and-connectors.json) · [既有市场](market-01-hall-loop.json) · [52 断面与原地折返](outside-52-sections-and-loop.json) · [配准](2015-pipe-fit.json)

- 30-field-axis.png [前](30-field-axis-before.png) · [后](30-field-axis-after.png)
- 30-return-axis.png [前](30-return-axis-before.png) · [后](30-return-axis-after.png)
- 31-field-axis.png [前](31-field-axis-before.png) · [后](31-field-axis-after.png)
- 31-return-axis.png [前](31-return-axis-before.png) · [后](31-return-axis-after.png)
- 49-field-axis.png [前](49-field-axis-before.png) · [后](49-field-axis-after.png)
- 49-return-axis.png [前](49-return-axis-before.png) · [后](49-return-axis-after.png)
- 30-garden-field-axis.png [前](30-garden-field-axis-before.png) · [后](30-garden-field-axis-after.png)
- 30-garden-return-axis.png [前](30-garden-return-axis-before.png) · [后](30-garden-return-axis-after.png)
- 31-garden-field-axis.png [前](31-garden-field-axis-before.png) · [后](31-garden-field-axis-after.png)
- 31-garden-return-axis.png [前](31-garden-return-axis-before.png) · [后](31-garden-return-axis-after.png)
- 33-pipe-from-public-lane.png [前](33-pipe-from-public-lane-before.png) · [后](33-pipe-from-public-lane-after.png)
- 33-pipe-at-wall.png [前](33-pipe-at-wall-before.png) · [后](33-pipe-at-wall-after.png)
- 33-pipe-turn-back.png [前](33-pipe-turn-back-before.png) · [后](33-pipe-turn-back-after.png)
