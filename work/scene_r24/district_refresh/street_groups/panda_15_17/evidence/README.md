# 熊猫古玩城临街 15、17 号复核

Godot 4.6.3 从正常 `first_shift.tscn` 运行。三组固定机位的眼位、朝向、FOV、分辨率逐个比对。改前与改后原帧均为 Mesa llvmpipe、Xvfb、Compatibility 模式，窗口请求 900 × 560，PNG 实存 900 × 506，沿用原软件模式日照条件。

| 固定机位 | 父版 | 新版 |
| --- | --- | --- |
| 15 橙框入口轴线 | [改前](15-portal-before.png) | [改后](15-portal-after.png) |
| 17 公交候车面与旧楼墙脚 | [改前](17-bus-stop-before.png) | [改后](17-bus-stop-after.png) |
| 17 固定回望街边 | [改前](17-street-return-before.png) | [改后](17-street-return-after.png) |

实际转身时另留 [15 玩家眼高回望](15-player-look-back.png) 和 [17 玩家眼高回望](17-player-look-back.png)。近景检查灰铺地、竖石和窗框的纹理尺度，橙框收檐及暗玻璃的真实退进，树池、候车架和旧住宅墙脚撤去后的可走范围。

| 地块 | 正常入口往返的有效范围 | 父版同路停步 |
| --- | --- | --- |
| 15 | 街道到橙框可见外槛 10.44 米，原地转身返街 10.40 米，各 5/5。 | 8.38 米，2/5，旧围护墙。 |
| 17 | 候车区旁公开步行带到低栏前 14.49 米，原地转身返街 14.46 米，各 5/5。 | 5.68 米，1/5，旧围护墙。 |

原始轨迹精确距离、高程和通行检查见 [双地块统计](summary.json)、[15 新版](15-walk.json)、[17 新版](17-walk.json)、[15 父版停步](15-parent-stopped.json)、[17 父版停步](17-parent-stopped.json)。所有验收行进使用原玩家控制器。共用街面 8 组断面，48/48 点通过，门廊实测净高 4.184 米。门廊背后的暗面为封闭的可视边界。Blender 4.3.2 分别重开独立源和组合城。 [独立源和链接组合复开](blender-reopen.json)

[相邻厚慈街 77，14/14](regression-houci-77.json) · [修车，10/10](regression-repair.json) · [山城巷取送，12/12](regression-shancheng.json) · [当前首班，85/85](regression-first-shift.json)

首轮并行软件返图两进程都退出 137，串行重拍保留完整原帧。云端完整日志、街景对照及逐地块下一轮注册位于 `/workspace/work/runtime/district-refresh/remaining-33-KxMhkZe8`。 [A 组其余机位](../A-pending.md) · [上下文恢复](../../../evidence/REFRESH_RESUME.md)

补充视觉复核保留以上原图和行走结果。原 `15-portal-after.png` 的固定相机含第一人称身体图层。新增诊断、无遮挡改前改后、正常玩家回望在 [视觉复拍](visual-review/README.md)。
