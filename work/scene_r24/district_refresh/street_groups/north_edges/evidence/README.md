# 北侧公共街面实走与画面

Godot 4.6.3 正常 `first_shift.tscn`，真实玩家在每处从公开街边起步；到折返点不复位，原路回到同一街边。下表为无头固定物理步 60 的实测，另以 Compatibility / Mesa llvmpipe 从原生窗口完整复走。楼边距是到旧外壳平面的最短距离，门槛距是到旧游戏门位的水平距离。真实住户门槛位置未证。

| 地块 | 去 / 回 m | 路点去 / 回 | 离旧楼边 / 旧游戏门槛 m | 同矩阵主视 | 同矩阵回望 | 玩家回望 |
| --- | ---: | --- | ---: | --- | --- | --- |
| 38 | 17.57 / 17.55 | 6/6、6/6 | 1.10 / 12.42 | [父](38-field-axis-before.png) · [今](38-field-axis-after.png) | [父](38-return-axis-before.png) · [今](38-return-axis-after.png) | [原生](38-player-turn.png) |
| 40 | 18.32 / 18.37 | 5/5、5/5 | 1.54 / 3.86 | [父](40-field-axis-before.png) · [今](40-field-axis-after.png) | [父](40-return-axis-before.png) · [今](40-return-axis-after.png) | [原生](40-player-turn.png) |
| 41 | 19.66 / 19.70 | 6/6、6/6 | 15.47 / 19.48 | [父](41-field-axis-before.png) · [今](41-field-axis-after.png) | [父](41-return-axis-before.png) · [今](41-return-axis-after.png) | [原生](41-player-turn.png) |

[碰撞和实际轨迹](current-walk.json) · [窗口复走](native-walk.json) · [旧门槛坐标](old-threshold-distances.json) · [父版旧路线](parent-walk.json) · [初件失败](first-grade-failure.json)

初件38顺向 1/6，坡面上叠支撑卡住。初件40顺向 4/5，撞旧外壳。后续40原生帧还看见穿过新墙的旧地基，用 Blender 射线找到六面凸墩，按原所有者指纹裁去。上部原楼、上方地面和其余原轮廓保留。远处背景楼及真实围墙高度需另核。 [修裁前命中](f40-before-trim-rays.txt) · [具体面记录](../field.json)

固定帧均 900×506，使用同一个相机位置、旋转、视场与相同游戏日照，软件预览关闭太阳阴影。父版关闭北侧增量；40回望用最终矩阵在父版重拍。其余未制作地块仍按原背景。 [相机](../views.json)

Blender 4.3.2 独立重开和链接组合各 20 个路线支撑点，均打到对应步带。较广入口的原有首班测试通过 85/85，市场到201 5/5，修车院10/10。作为诊断另跑旧的 `day_one/verify.gd`，父版和初候选均在交单一次与下一单提示两个断言失败。当前仓库用 `indoor_delivery/verify_shift.gd` 验收首班。 [Blender](blender-support.json) · [首班](first-shift.json) · [市场](market-to-201.json) · [修车](repair-court.json) · [旧入口父版](old-alternative-harness-parent.json) · [旧入口候选](old-alternative-harness-candidate.json)
