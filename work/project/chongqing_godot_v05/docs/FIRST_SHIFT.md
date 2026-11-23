# 第一天跟老彭跑三单

构建 24 在结业后的面馆增加 B 键邻里托送。玩家从一单元 202 取餐，通过背巷的蓝砖楼和高连廊送到 301。G 键仍接原有午市三单。[穿楼路线、练习入口与原生录像](VERTICAL_RUN_R24.md)

构建 23 在结业后的面馆加入午市拼送。G 看三张报价，E 接受，V 翻小票。老彭继续跑自己的单，玩家安排两袋的去向和第三袋的返店时间。[午市玩法与实跑记录](LUNCH_RUN_R24.md)

构建 22 的第一单送进一单元，门牌 201。在车箱边取餐，随老彭进楼上两段台阶，在户门前看他示范。背巷可从另一侧的外梯、连廊进入同一层。结业后的第一张散单为学员 008 号，送一单元 201，下张送 202。供练习用的 [单元门停车点入口](../../../跟老彭进单元送餐.cmd) 使用内存进度。[楼内与散单复核](UNIT_DELIVERY_R24.md)

构建 21 从同一入口做三单带教。南区路接坡、东巷平台和北侧高路的路面复查使用同一辆玩家电瓶车。可在机位菜单回看两处新绿化。[道路与居民院记录](TERRACE_GARDENS_R24_REVIEW.md)

构建 20 沿用三单带教；新增院路转角、坡脚、支路汇入口及旧住区环境。全区骑行矩阵、路线可达范围和真实车轮探点见 [街区复查](DISTRICT_AGE_R24_REVIEW.md)。

本地工程使用 Godot 4.6.3，默认从 `first_shift.tscn` 入职。每单由老彭先接、取、装、送，学员骑自己的车跟做。老彭的配送单和收入独立。学员每份实送餐记 8 元。

| 次序 | 两人的小票 | 去哪里 | 学员要完成的操作 |
| --- | --- | --- | --- |
| 第一单 | 老彭 001，学员 002 | 山城里小院一单元 201 | 骑过面馆坡道和球场横巷，在下院停车。提餐后跟老彭上二楼，在 201 户门敲门报号，再把餐挂在第二个钩上 |
| 第二单 | 老彭 003，学员 004 | 骑手站取餐架 | 看老彭另装辣子。等自己的餐打包后按 E 装入密封小盒，再按 E 提袋。送到骑手站的乙位 |
| 第三单 | 老彭 005，学员 006 | 篮球场下巷取餐架 | 上坡送餐，到架后按左侧呼叫键报号，听到回应再把餐放在乙位。放错位置会收到提示 |

靠近黄帽子的老彭按 E 报到。W 加速，S 减速和倒车，A、D 转向，空格刹车。停稳后按 P 停车，再按 E 下车。在自己的车旁按 E 装卸餐袋，装好后再按 E 骑车。师傅会等掉队或中途下车的学员。三单结算后开放自由接单，老彭会回店取下一份独立的餐，骑到站点交给取餐架。

正常进度保存在 `user://first_shift_v1.cfg`。旧版只做完首单的存档接续第二单，保留原有订单数和收入。动作途中退出，读档从最近的教学节点恢复。重练入口使用独立练习进度。[启动游戏](../../../打开重庆街区.cmd) · [从报到重练](../../../重练第一天.cmd) · [观看自动跟做](../../../老彭跑教学自检.cmd)

## 三单教学和路面复查

正常入口实跑两辆车。球场边使用同一份地面渲染和生成碰撞，脚下的磨损直接画在保留的地面上。专项测试单独跑中央石梯、旧卡点、垂直穿过横巷及从低速倒车上坎。第一天的检查脚本改用 `../../scene_r24/road_and_shift/verify_shift.gd`，从游戏目录运行。传入 `--day-one-test` 和独立的 `--qa-dir` 可保留每次的读档、截图、路线上报与关节采样。

实测证据来自同一项目的独立运行。[三单及老彭独立配送](../verification_r24/road_shift/playcheck/first_shift.json) · [中途下车与人工路障复跑](../verification_r24/road_shift/pausecheck/first_shift.json) · [球场横断面](../verification_r24/road_shift/court_pocket/cross_sections.json) · [双车驶过整段中央石梯](../verification_r24/road_shift/whole_flight/first_shift.json) · [顺坡穿过球场边线](../verification_r24/road_shift/downhill_check/first_shift.json) · [不同高度的轮胎测试](../verification_r24/road_shift/lips04/results.json) · [旧档与新档恢复](../verification_r24/road_shift/final_resume/resume.json)

现场性能另测了 1280 × 720 窗口中的街口、住宅入口和骑手坐姿。此时原有编辑器和玩家的游戏窗口也在运行，保留桌面帧间隔与视口 GPU 时间作后续同条件对照。[性能原始记录](../verification_r24/road_shift/street_timing/performance.json)

## 历史动作复看


针对玩家提交的提袋、敲门、装箱和挂钩四张图，近景保留手指、手腕和接触面，全身机位保留头、肩、肘和车箱。纸袋离台、越过箱沿、落入箱内、松手和抽手都在引擎中连续执行。门板位置取自 A04 木门可见三角面。门框上的门铃继续用于街区其他互动。

[装箱侧面连续画面](../verification_r24/mentor_demo/verified_motion/load_box.webp) · [挂餐和撤手](../verification_r24/mentor_demo/verified_motion/hang.webp) · [门板敲击](../verification_r24/mentor_demo/verified_motion/knock.webp) · [柜台提袋](../verification_r24/mentor_demo/verified_motion/pickup.webp)

## 复验

- 正常教学使用项目默认入口和真实按键，检查两辆车、两段步行、两次店主出餐、装卸、门口先后顺序和单次记账。每张复核图对应引擎物理帧，动图记录原帧顺序及间隔。[整趟记录](../verification_r24/mentor_demo/verified_motion/first_shift.json)
- 关节数据来自最终变形骨架。检查工作手腕相对前臂的角度、两肘是否同时高于肩、提袋手腕距头部骨点的距离，以及纸袋横截面与四面箱壁的交叠。骨点距离与皮肤、袖子实际轮廓分别检查。[逐次关节采样](../verification_r24/mentor_demo/verified_motion/joints.json)
- 途中停车下车、跟丢、敲门示范时转头看开，分别检查师傅能否停下并接续。实体路障案检查实际卡点和移除后的奏效。五个进度点用同一工程重新加载。[中断后继续](../verification_r24/mentor_demo/case_fit11/first_shift.json) · [路障记录](../verification_r24/mentor_demo/verified_obstacle/route_issues.json) · [读档](../verification_r24/mentor_demo/case_fit11/resume.json)
- 复查旧版单笔教学时运行下面的历史命令，每次选用一个新目录。加 `--test-roadblock`、`--test-dismount` 或 `--test-look-away` 可测试打断。使用图形窗口时，`--qa-still-frames --contact-motion` 额外记录动作连续分解图。图形检查的固定时间步长不用于推算实机帧率。

```text
godot --headless --path . --fixed-fps 60 --script ../../scene_r24/day_one/verify.gd -- --day-one-test --qa-dir=res://verification_r24/mentor_demo/my_run
```

这组历史记录的美术底图为 R24 构建 18。原始投诉截图、旧教学代码、退回的动作试验、可编辑保温箱和木门表面探测分别保存在 `work/scene_r24/day_one/demonstration` 和游戏的 `verification_r24/mentor_demo`。老路线的石梯受阻证据仍在 `verification_r24/first_shift/former_approach`。肩肘轮廓、衣料折痕和负重感继续以玩家实际观看为准。
