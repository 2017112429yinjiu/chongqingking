# 马蹄街公共接头实测 34、35

Godot 4.6.3 `first_shift.tscn`，玩家抵户外转点原地折返，未重新安置。旧楼边和游戏门距是试作历史几何参照，两处实走都是公共街边，尚未走到或确认实景私人门位。

| 地块 | 去 / 回 m | 去回路点 | 离旧楼边 / 旧游戏门槛 m | 主视 | 回望 | 玩家转身 |
| --- | ---: | --- | ---: | --- | --- | --- |
| 34 | 12.03 / 12.11 | 5/5、5/5 | 22.77 / 27.27 | [父](34-field-axis-before.png) · [今](34-field-axis-after.png) | [父](34-return-axis-before.png) · [今](34-return-axis-after.png) | [原生](34-player-turn.png) |
| 35 | 10.65 / 10.63 | 5/5、5/5 | 16.59 / 26.29 | [父](35-field-axis-before.png) · [今](35-field-axis-after.png) | [父](35-return-axis-before.png) · [今](35-return-axis-after.png) | [原生](35-player-turn.png) |

Godot 公共步带支撑共12/12，Blender 4.3.2 独立与组合各12/12。固定图为 900×506 原生输出，使用 Compatibility／llvmpipe，并保持同矩阵、同日照且关闭太阳阴影。沿途仍可见保留的原试作背楼和外侧旧地表。 [逐点走测](current-walk.json) · [原生走测](native-walk.json) · [父版支撑](parent-sections.json) · [Blender](blender-support.json) · [旧门位](old-threshold-distances.json)

回归首班85/85、便民市场至201为5/5、修车院10/10。 [首班](first-shift.json) · [市场](market-to-201.json) · [修车](repair-court.json)
