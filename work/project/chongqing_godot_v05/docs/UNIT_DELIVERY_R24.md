# 山城里小院一单元 · 楼内送餐

从第一天默认入口报到、取餐、骑到小院。老彭从自己的车箱提走 001 号餐；玩家取出 002 号，跟他穿过敞开的单元铁门。两段楼梯中间有休息平台，二楼第一户为 201。老彭先敲门报号、挂餐、退到一旁，玩家在同一户门操作。两人沿楼梯下楼回到自己的车旁，接着去学第二、三单。[从停车处单独练习](../../../跟老彭进单元送餐.cmd)

### 熟悉楼以后

201 所在的楼层还通往 202 和北侧背巷。站在背巷能从外梯上人行连廊，再从北门进二楼；从院坝走的是 20 级室内楼梯，中途有平台。楼层之间相差 3.45 米。背巷外梯有 15 级，连廊沿既有住宅外墙布置。两条路在同一栋楼里相通，步行时没有切场景或位置跳转。

第一天结束后，玩家的散单交替派往 201、202。小票写明地址。到正确户门按 E 报号，看到住户回复，走近同一户的搁板，面向搁板按 E 放下。放稳后结算 8 元。学员首张散单为 008，老彭继续以自己的奇数小票独立送单。室内依靠单元牌、楼层和户号识路；散单界面计算平面距离。报号后播放门铃声，住户的回复以字幕显示。

### 现场复核

- Blender 从构建 21 完整整城开工，改用一号楼原有门洞和木门，连同原门框、锁、猫眼移到 201。按通行范围打通原先的内衬与楼板，重新做真实的墙顶、踢脚、台阶、搁板、门牌和管线。[可编辑整城](../../../scene_r24/indoor_delivery/city_and_unit.blend) · [重开校验](../../../scene_r24/indoor_delivery/reopened.json)
- 第一版向东落地的外梯被树冠遮住，出口还剩一截旧阳台。原生视角发现两处问题，点开可对照。改为向西落地，拆掉旧阳台的木栏、托撑和冲突附件，保留原树及树池。室内曾逐级拼墙漆和顶板，复看后改为连续斜面。在两条路线的截线上，300 个竖向探点测量地板以上 0.025 至 2.36 米，最低门楣的实测净高约 2.12 米。此项用于检查指定的行走带。[旧外梯](../verification_r24/indoor_delivery/registered_views/unit22_gallery.png) · [初次门楣探测](../../../scene_r24/indoor_delivery/headroom_lintel_trial.json) · [最后净空采样](../../../scene_r24/indoor_delivery/headroom.json)
- 实际角色从下院走到 201 和 202，再经连廊下到背巷，从背巷上行进楼，并从低处单元门返回。逐段记录行走距离、站立高度、阻挡和每帧最大位移；独立检查错门、重复按键、放稳前收入与餐袋落点。[步行与交付记录](../verification_r24/indoor_delivery/district22/both_entrances/route.json)
- 常规教学从报到连续跑完三单和师傅收工后的首个独立订单。散单另从三单结业存档读起，回店接 008，再提袋实走约 78 米送进 201。另有途中停车、跟丢、人工路障、恢复存档、正常骑行与交互回归。[正常教学](../verification_r24/indoor_delivery/district22/teaching/first_shift.json) · [008 号散单](../verification_r24/indoor_delivery/district22/free_order/free_order.json) · [中断和复行](../verification_r24/indoor_delivery/district22/wait_rejoin/first_shift.json) · [恢复进度](../verification_r24/indoor_delivery/district22/restore/resume.json)
- Godot 4.6.3 Forward+ 默认工程与 Blender 4.3.2 重开检查分别记录。[复测脚本](../../../scene_r24/indoor_delivery/verify.ps1) · [固定原生机位](../verification_r24/indoor_delivery/district22/views) · [搁板放餐画面](../verification_r24/indoor_delivery/district22/free_order/fourth_order_delivered.png) · [材质来源与哈希](../../../scene_r24/indoor_delivery/assets.json)

在 RTX 4070 Laptop GPU、960 × 540、Forward+ 下，下院入口、二楼过道和背巷连廊各采样 240 帧，视口 GPU 帧耗时第 95 百分位分别为 4.31、5.60、6.33 毫秒。[计时原始数据](../verification_r24/indoor_delivery/gallery_timing/performance.json) · [下院至背巷实机图](../../../scene_r24/indoor_delivery/一单元两条进楼路线.jpg)

本轮可投递的室内地址为一单元二楼两户。首日其余两单继续服务骑手站和球场取餐架。玩家仍负责在正常游戏中评价认路难度、建筑陈设和动作表现。
