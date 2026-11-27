# 50 号遗址外缘实地对照与游戏实走

| 固定机位 | 父版 | 最终版 |
| --- | --- | --- |
| 外缘靠近 | [原图](50-garden-approach-before.png) | [新图](50-garden-approach-after.png) |
| 公开观察端 | [原图](50-public-edge-before.png) | [新图](50-public-edge-after.png) |
| 石墙反向 | [原图](50-stone-side-reverse-before.png) | [新图](50-stone-side-reverse-after.png) |

两套图保持同机位、视场和日照，像素均为 900×506，使用 Godot 4.6.3、Xvfb 和 Mesa llvmpipe OpenGL Compatibility。第一次场景已能往返，图上有条石落在原车道路缘一侧。终版将两块近路的条石移入园内，留原图和最终画面。 [第一次路缘条石](50-first-trial-seat-at-road-edge.png) · [记录](summary.json)

正常玩法从公开接头出发，用同一个角色走至遗址外观察点，原地转身回到接头。父版同一路线结果也留存。检查每条腿的支撑、端点到原足迹边缘及中心的距离、返回误差、同一版本的纹理资源。独立 Blender 源及组合重开实测 54 个铺面接触点，Blender 4.3.2。 [父版路线](parent-walk.json) · [新版玩家路线](player-walk.json) · [无窗口复测](headless-walk.json) · [Blender复开](blender-reopen.json)

原生玩家画面记录起步、面向原来向的回望以及走返同一接头。验收只覆盖本片段公开面。外栈道、园北住区与遗迹内部继续各自核对。 [起步](50-player-start.png) · [实走回望](50-player-turn.png) · [返回接头](50-player-return.png)

回归确认开档、市场摊主、修车与山城巷取送入口，另检查在用收藏品市场。 [首班](regression-first.json) · [照相巷](regression-market.json) · [修车](regression-repair.json) · [山城巷](regression-handoff.json) · [收藏品市场](regression-collectibles.json)
