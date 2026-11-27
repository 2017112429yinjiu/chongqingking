# 南区路 04、06、51 实测与原生图

04 原轮迹的顺向停点为 E−145.111／N−79.608，沿江侧偏离登记线 1.085 米，距游戏路缘 1.505 米。现场连续帧的同侧车道有车通行。反向接触的实际网格为 COL_Outer500_Retaining_and_boundaries，靠来源指纹归到 53 号旧石梯挡边。只裁车行范围内突出部分，沿用原检测输入和路点。 [碰撞、轨迹和照片登记](04-original-wheel-EN-audit.json) · [整改前失败](old-inner-wheel-line-failure.json)

原轮迹顺向 45.63 米、封闭逆向 45.64 米，各 8/8。江侧车轮线 45.68／45.69 米、各 8/8。西接坡到 51 号 51.95／51.86 米，各 9/9。车轮空中帧 0。玩家从公开步道至禁行牌前去回 89.90／89.91 米，各 15/15。梁箱六点净空为 2.470 米左右，另测得墩帽下约 1.773 米。53 号石梯 129 点，最大接缝差为 4.857 毫米。 [骑行](wheel-routes.json) · [步行](player-walk.json) · [断面](sections.json) · [53 石梯](landing-53-profile.json)

| 原生机位 | 父版 | 本版 |
| --- | --- | --- |
| 06-approach | [前](06-approach-before.png) | [后](06-approach-after.png) |
| 51-see-river | [前](51-see-river-before.png) | [后](51-see-river-after.png) |
| 51-reverse | [前](51-reverse-before.png) | [后](51-reverse-after.png) |
| 06-51-overview | [前](06-51-overview-before.png) | [后](06-51-overview-after.png) |
| 51-bridge-side | [前](51-bridge-side-before.png) | [后](51-bridge-side-after.png) |
| 04-pedestrian-limit | [前](04-pedestrian-limit-before.png) | [后](04-pedestrian-limit-after.png) |
| 04-under-rail | [前](04-under-rail-before.png) | [后](04-under-rail-after.png) |

原生 900 × 506，Godot 4.6.3 Compatibility／llvmpipe。现有轨道承台整体高度与真实近照还有差异，留作桥轨后续整体标高复核。 [起点](player-start.png) · [原地回望](player-turn.png) · [返回街边](player-return.png)

首班教学 85/85、照相巷市场到 201 为 5/5、原南区路修车路线 10/10。Blender 4.3.2 独立和组合各测 48 个落脚及花箱支撑。 [汇总](summary.json) · [旧地表卡点](old-ground-seam-failure.json) · [旧53基础失败](old-53-apron-failure.json)
