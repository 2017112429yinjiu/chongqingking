# 午市拼送

老彭带完三单后，梯坎小面的柜台会同时提供散单和午市拼送。照常按 E 接一单，在柜台前按 G 可以先看三张报价。再按 G 返回，按 E 才接下整趟。[直接进入面馆练习](../../../午市拼送练习.cmd)

这一趟采用策划案 V1.1 的同店多送。接单前显示取餐店、收餐地址、平面距离和报酬。接单后，三张小票同时开始计时。路线、返店时机、上楼次序都由玩家决定。三户在固定地点收餐，方便反复比较路线。

| 收餐点 | 餐品 | 从接单到出餐 | 从接单到限时 | 准时收入 |
| --- | --- | --- | --- | --- |
| 球场下巷取餐架甲位 | 杂酱面 | 已备好 | 65 秒 | 9 元 |
| 一单元 201 | 清汤抄手 | 5 秒 | 115 秒 | 12 元 |
| 一单元 202 | 豌杂面 | 22 秒 | 150 秒 | 11 元 |

V 翻小票，E 取当前这袋。可以一次提两袋，第三袋留店。每张餐袋贴有单号、餐名和地址。翻票时餐袋留在原先那只手里。上车后两袋分别占车箱的前后两个位置，下车后可继续提餐。柜台给老彭留有取餐位。

在球场呼叫收餐人，到甲位放餐。住宅单要进一单元，按门牌报号，再把餐放到住户的搁板。走错户、放错格、手里没有对应餐袋或放到一半走开，都要重新核对。放稳并松手后才记账；每个超时单少 3 元。全部送完可回店再接午市或散单。

## 存档与复查

正式游戏保存时间、手里的餐、各户的应答和已结算收入。接单、取餐、报号、放稳会写入进度，运行期间每五秒也会记录。重开时从已确认的操作继续，关闭游戏的时间不计入限时。单独练习从已完成教学三单、累计 24 元开始，进度放在内存里。

Godot 4.6.3 的复查通过实际步行控制、车体物理、交互键和游戏存档完成。球场优先路线在返店后把两份住宅单一起上楼，本趟 32 元。另一条路线依次送 202、201，再返店送球场，本趟 29 元。双袋上坡实骑约 25 米、上升 3.4 米，然后停车下车，步行完成球场交付。初次试骑曾被老彭的回程车辆堵住，随后调整了练习起点的停车方向和位置。

- [球场优先路线与账单](../verification_r24/lunch_run/verified23/court_first/trip.json)
- [两户优先路线与账单](../verification_r24/lunch_run/verified23/homes_first/trip.json)
- [柜台纸质小票近景](../verification_r24/lunch_run/verified23/homes_first/paper_ticket.png)
- [左手在 202 放餐](../verification_r24/lunch_run/verified23/court_first/04_202_left_hand.png) · [右手在 201 放餐](../verification_r24/lunch_run/verified23/homes_first/04_201_right_hand.png)
- [带餐骑行与甲乙位检查](../verification_r24/lunch_run/verified23/loaded_ride/trip.json) · [被回程车辆挡住的旧车位](../verification_r24/lunch_run/ride_probe/trip.json)
- [送完两张后重开并续送](../verification_r24/lunch_run/verified23/reopen/trip.json) · [结清重开，返回柜台接 014 散单](../verification_r24/lunch_run/verified23/next_order/trip.json)
- [首日教学三单](../verification_r24/lunch_run/verified23/teacher/first_shift.json) · [教学后的第一张散单](../verification_r24/lunch_run/verified23/single/free_order.json)
- [柜台定点性能采样](../verification_r24/lunch_run/verified23/counter_timing/timing.json)

柜台定点在 RTX 4070 Laptop 上各采了 120 帧。窗口为 960 × 540，实测渲染画面为 480 × 270。柜台空闲和三份出齐时的 GPU 帧耗时第 95 百分位分别为 15.17 和 15.31 毫秒。这组数据只覆盖柜台视角和当前运行分辨率。

复查入口为 `work/scene_r24/lunch_run/verify.ps1 -Run <新目录名> -Timing`。几何沿用构建 22 的一单元、球场和柜台，继续使用原项目的模型和字体授权。计时、出餐节奏和扣款是本轮试玩值。
