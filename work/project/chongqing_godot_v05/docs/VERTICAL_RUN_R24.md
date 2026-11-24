# 穿楼托送 · 一单元 202 到 301

构建 25 已开放本楼直达 301 的楼梯。下文记录构建 24 首次做成的跨楼走法，仍可实际游玩。[当前两条路线及实测](DISTRICT_PATROL_R24.md)

202 的蒋嬢嬢托你给 301 的罗师傅捎一袋豆花饭，送到收 16 元。两户写着同一个单元号，却通往不同标高的入口。[直接从下院试玩](../../../穿楼托送练习.cmd) · [约 31 秒的引擎实走录像](../verification_r24/vertical_run/playable24/穿楼托送实走.mp4)

## 怎么走

1. 从院坝进一单元，上二楼，在 202 门边看向搁板，按 E 取餐。
2. 沿住户走廊穿出后门，顺外梯下到背巷。沿蓝砖楼外墙转到背巷门，进楼。
3. 爬完头一跑，在装着电表箱的平台折返。再上一跑，到临街窗边右转，顺过道走向四层连廊。
4. 跨巷过桥。桥面与蓝砖楼的四层齐平，另一头接入小院高处。进楼下六级，到 301 报号。听到应答后靠近门边搁板，按 E 把餐放稳。

结业后在梯坎小面按 B 看托送单，E 接单，B 收起。G 仍可查看午市拼送。独立练习从已经接下这单的下院开始，使用内存进度。正式游戏沿用原存档。可从桥上退出再接着走。各个楼梯和连廊在普通探索及送单时都能双向通行。

## 空间与制作

两栋楼原来相距 12 米。本轮在原楼体开洞，接入背巷门、折返梯、临街窗和钢连廊，在原小院增设半层落差和 301 收餐搁板。站在桥上朝背巷看，可以认出取餐后下过的外梯。桥边使用铆接节点和涂装钢件，门槛按背巷原地面找坡。未改动街区边界。[可编辑整城](../../../scene_r24/vertical_run/city_and_crossing.blend) · [模型与材质来源](../../../scene_r24/vertical_run/assets.json)

| 位置 | 玩家实测脚下标高 |
| --- | ---: |
| 一单元下院门槛 | 16.46 米 |
| 一单元二楼取餐层 | 19.90 米 |
| 下外梯后的背巷 | 17.28 米 |
| 蓝砖楼背巷门 | 17.13 米 |
| 折返平台 | 20.53 米 |
| 蓝砖楼四层与过街连廊 | 23.93 米 |
| 小院 301 | 22.91 米 |

## 游戏内复核

Godot 4.6.3 用实际步行角色从下院一路取送，抵达搁板共约 92 米。结账后又反向走回蓝砖楼外，约 45 米。全程经过物理地面和门洞。独立进程从桥上存档恢复，再送到 301，结算一次。另从既有教学结业存档回面馆，实测两种报价切换、取消与正常接单。[完整路线和脚下高度](../verification_r24/vertical_run/playable24/route.json) · [桥上续送](../verification_r24/vertical_run/resume24/reopen.json) · [面馆接单](../verification_r24/vertical_run/counter24/reopen.json)

369 处采样覆盖了两跑楼梯、桥面与两端、新增六级台阶和背巷门槛。采样范围内最小净高 2.35 米，门槛前后相邻采样点的最大高差 1.26 厘米。初稿中残留的窗外阳台构件和第二稿的门槛缺口均保留了原图。最终图像为修整接头、重烘遮挡后的运行结果。[几何测量](../verification_r24/vertical_run/surfaces24/section.json) · [早期窗外残件](../verification_r24/vertical_run/walk01/05_upper_window.png) · [门槛修整前](../verification_r24/vertical_run/walk02/03b_blue_door.png) · [修整后](../verification_r24/vertical_run/playable24/03b_blue_door.png)

原有第一天三单、结业后常规散单和午市三单均另起进程回归。Blender 4.3.2 重新打开完整工程核对了该层 83 件网格。录像来自游戏视口 464 帧连续采样，按原游戏时间编码为每秒 15 帧。[教学回归](../verification_r24/vertical_run/training24/first_shift.json) · [散单回归](../verification_r24/vertical_run/single24/free_order.json) · [午市回归](../verification_r24/vertical_run/lunch24/trip.json) · [源文件重开](../../../scene_r24/vertical_run/reopened.json)

RTX 4070 Laptop 上，窗口为 1152 × 648，实际渲染视口为 692 × 389。每处取 150 帧，折返梯、桥上、301 门前的 GPU 第 95 百分位分别为 5.49、11.08、10.53 毫秒。结果只覆盖这些定点视角。实际玩家对背巷入口、上层转角和门牌的辨认仍待试玩。[原始计时](../verification_r24/vertical_run/views24/timing.json)

复查使用 `work/scene_r24/vertical_run/verify.ps1 -Run <新目录名> -Timing`。
