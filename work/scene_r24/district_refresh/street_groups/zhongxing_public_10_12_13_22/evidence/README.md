# 中兴路与广场公开边实测

Godot 4.6.3 首班正常场景，每处独立街边起步，到端点转身原路返回。去回之间没有复位。旧楼边和旧门槛按原试作几何量。12 单另量到已登记的实景柱间开口，还差 0.86 米，测试止于公开面。

| 地块 | 去 / 回 m | 路点去 / 回 | 离旧楼边 / 旧游戏门槛 m | 同机位主视 | 同机位回望 | 实际玩家回望 |
| --- | ---: | --- | ---: | --- | --- | --- |
| 10 | 10.05 / 10.11 | 5/5、5/5 | 1.45 / 3.30 | [父](10-field-axis-before.png) · [今](10-field-axis-after.png) | [父](10-return-axis-before.png) · [今](10-return-axis-after.png) | [图](10-player-turn.png) |
| 12 | 6.08 / 6.15 | 5/5、5/5 | 9.66 / 9.71 | [父](12-field-axis-before.png) · [今](12-field-axis-after.png) | [父](12-return-axis-before.png) · [今](12-return-axis-after.png) | [图](12-player-turn.png) |
| 13 | 14.32 / 14.40 | 5/5、5/5 | 0.21 / 4.07 | [父](13-field-axis-before.png) · [今](13-field-axis-after.png) | [父](13-return-axis-before.png) · [今](13-return-axis-after.png) | [图](13-player-turn.png) |
| 22 | 10.92 / 10.95 | 5/5、5/5 | 0.49 / 8.20 | [父](22-field-axis-before.png) · [今](22-field-axis-after.png) | [父](22-return-axis-before.png) · [今](22-return-axis-after.png) | [图](22-player-turn.png) |

同机位软件原生帧 900×506，Compatibility／Mesa llvmpipe，统一日照，太阳阴影关闭。路点每块6，Godot 支撑总24/24，Blender 4.3.2 独立与组合各24/24。13初件与旧楼包络冲突；撤已登记试作面后，首张图又遇新墙太近，末件向初测远侧调整1.62米，重新实跑所有四地块并重拍13。 [初件走测失败](first-route-failures.json) · [13真实撞击](13-shell-failure.json) · [13初版视觉失败](13-camera-too-close-first.png)

[无头轨迹](current-walk.json) · [原生轨迹](native-walk.json) · [点位与旧门槛距离](old-threshold-distances.json) · [Blender重开](blender-support.json)

末件另实跑首班85/85、市场到201为5/5、修车10/10。 [首班](first-shift.json) · [市场](market-to-201.json) · [修车](repair-court.json)
