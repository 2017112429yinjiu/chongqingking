# 原生与物理复核

四处测试在正常 first_shift.tscn 固定 60Hz。每次从室外地面开始，去回由同一玩家身体走，转身时无需重新置人。

| 地块 | 去 m | 回 m | 路点 | 终点距旧轮廓 m |
| --- | ---: | ---: | ---: | ---: |
| 02 | 12.115 | 12.379 | 5/5、5/5 | 1.36 |
| 24 | 17.122 | 17.119 | 5/5、5/5 | 7.51 |
| 25 | 4.961 | 4.950 | 7/7、7/7 | 6.71 |
| 26 | 17.680 | 17.720 | 5/5、5/5 | 9.18 |

长滨路登记道路 1256859184 路线的反向仅在无人 QA 中检查。

| 方向 | m | 路点 | 离地帧 | 支撑采样 |
| --- | ---: | ---: | ---: | ---: |
| closed_reverse | 53.871 | 9/9 | 0 | 92/92 |
| forward | 53.870 | 9/9 | 0 | 92/92 |

茶摊正常选择摊主目标和交接架，取、送、单次到账6元、步行原地返回均通过，11/11。首班85，市场5，修车10，山城巷取件送件也通过。原国浩两条合成走线本次 4/4，后半偏离登记街道约29m，分别保留原失败和本次原线结果，以新设计的公开街肩和大阶为依据。

固定图是 Godot 4.6.3 原生 PNG，OpenGL API 4.5 (Core Profile) Mesa 25.0.7-2+deb13u1 - Compatibility - Using Device: Mesa - llvmpipe (LLVM 19.1.7, 256 bits)，画面900×560，两组相机逐项一致。02来自带抬高铺带的最终导出，24–26的在场网格与上一原生同矩阵版逐面一致。保留并行绘制导致 SIGKILL 的旧运行。

[实时行走与断面](public-walk.json) · [车线](closed-qa-ride-lines.json) · [茶摊取送](tea-actual-handoff.json) · [原国浩历史走线本次实跑](old-guoco-route-current.json)

- 02 [来向改前](02-field-axis-before.png) · [改后](02-field-axis-after.png) · [回向改前](02-return-axis-before.png) · [改后](02-return-axis-after.png)
- 24 [来向改前](24-field-axis-before.png) · [改后](24-field-axis-after.png) · [回向改前](24-return-axis-before.png) · [改后](24-return-axis-after.png)
- 25 [来向改前](25-field-axis-before.png) · [改后](25-field-axis-after.png) · [回向改前](25-return-axis-before.png) · [改后](25-return-axis-after.png)
- 26 [来向改前](26-field-axis-before.png) · [改后](26-field-axis-after.png) · [回向改前](26-return-axis-before.png) · [改后](26-return-axis-after.png)
