# 原生返图与实走

同一场景入口和机位用收尾图层开关切换父版 64fe77f1 与候选。固定机位记录位置、指向和垂直视野，园内回望为实际角色到最后一个路点后转身。返图使用 Godot 4.6.3、Xvfb 和 Mesa llvmpipe Compatibility，900 × 506 PNG。 [渲染条件与退出日志](native-renderer.txt)

| 位置 | 改前 | 改后 |
|---|---|---|
| 弯道下层由西向东 | [原图](bend-west-before.png) | [原图](bend-west-after.png) |
| 弯道下层由东向西 | [原图](bend-east-reverse-before.png) | [原图](bend-east-reverse-after.png) |
| 公厕东端看向平行道路与园边 | [原图](road-and-park-west-before.png) | [原图](road-and-park-west-after.png) |
| 下游向西回望两段铺带 | [原图](road-and-park-east-before.png) | [原图](road-and-park-east-after.png) |

[63／65 真正步行到点后转身](bend-player-look-back-after.png) · [64／66 真正步行到点后转身](park-player-look-back-after.png)

| 路线 | 进入 | 回到同一街边 | 地面探针 | 最小机动车中心线距离 |
|---|---:|---:|---:|---:|
| 63／65 弯道下层车库外侧 | 27.360 米 · 8/8 | 27.343 米 · 8/8 | 27/27 | 6.87 米，1256859184 北侧 |
| 64／66 长滨路公园侧绕公厕 | 54.251 米 · 15/15 | 54.227 米 · 15/15 | 48/48 | 5.53 米，59146737 南侧 |

实际玩家两次在园边先原地转身，然后以同一角色连续回到起点。两方向间均为 0 次传送。旧 64／66 道路中心用碰撞柱线核对，玩家走的是同侧公园铺带。父版弯道路线走了 3.560 米，旧楼围护挡住第一个路点。父版园边路线走了 23.176 米并通过 7 个路点，随后被旧 64 号附属庭院碰撞挡住。首次南侧改图试走 则因贴近公厕外墙，起步横移 0.219 米，后续路线绕其东端。 [最终弯道实走](bend-walk.json) · [最终园边实走](park-walk.json) · [旧弯道阻挡](bend-native-before.json) · [旧园边阻挡](park-native-before.json) · [南侧初次入点失败](park-initial-entry-failure.json) · [其他尝试](trials.json)

Blender 4.3.2 重开独立源及整城组合，复读 75 处走路地面支承、新旧匝道和道路分层。Godot 4.6.3 复查导入，以及 62 公厕 6/6、修车 10/10 和默认首班 85/85。 [Blender 重开](blender-reopen.json) · [四个父版中心柱线](baseline-blender-centres.json) · [Godot 导入](godot-import.txt) · [62 公厕](regression-pavilion62.json) · [修车](regression-repair.json) · [首班](regression-first-shift.txt)
