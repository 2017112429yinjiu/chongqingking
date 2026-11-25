# 照相巷市场、山坡住宅和共用院坝

在 Windows 双击[逛照相巷院坝](../../逛照相巷院坝.cmd)，或在[原 ChatGPT 云工作区](https://chatgpt.com/local/6b06ade0-5d00-83e8-8943-7283f30c5008)从市场出发。穿过柱间菜档和后院，沿石梯上木廊就到 201。[同机位前后对照](evidence/architecture_before_after.jpg) · [从市场进 201 的原生实录](evidence/landing_take/market_to_201.mp4)

## 临街窗洞、挑廊与室内质感

按玩家指出的新旧区差距，以老城的[门面](evidence/landing_views/old_service.png)、[出挑空间](evidence/landing_views/old_overhang.png)、[原 202 室内](../../project/chongqing_godot_v05/verification_r24/district_patrol/final25b/bridge/02_pickup_202.png)和项目存档的[重庆老街实拍](../street_photo_study/重庆老街八张实拍.jpg)对照。建筑制作提交 `32acad57`，补齐 53 号楼末级石梯后的可玩版本为 `1436ceaf`。[老城区与新区并排实录](evidence/old_and_outer.jpg)保留各自地点和机位。修改前后对照板上排是前一版，下排是本版，三列分别为市场、5 号住宅和 201 卧室。画面来自 Godot 4.6.3 Forward+ 的固定玩家视高。

| 轮次 | 在同一机位看到的问题和改动 |
| --- | --- |
| 一 | 原窗扇都贴着墙皮，挑檐和床脚下少有阴影。上层在柱间开洞，增加窗台、窗框和可见窗扇厚度。市场装布棚，修理铺用金属雨罩，茶摊用卷竹帘。内墙加入旧灰泥和腰墙，地面使用有磨损与拼缝的砖。复拍仍看到市场脚下单调的大平台。[原先的市场](evidence/architecture_reference/market_facade.png) · [初改市场](evidence/architecture_trial/market_facade.png) |
| 二 | 将台基做成分层砌石，开出三处有 32 厘米进深的百叶检修口。在挑廊补封窗、旧区同源的空调外机和墙托。按屋内家具、台面和柱脚的实形，把接触处阴影烘到地面。[住宅临街面](evidence/architecture_fitted/home_05_facade.png) · [201 卧室](evidence/architecture_fitted/market_bed.png) |
| 三 | 原有三处远景大楼的实测占地和屋顶附件保留，立面退进形成窗带与廊口。市场梯坎的踏面、踢面和侧墙分别铺石。菜摊里的瓜、茄子和橘子重新做表皮起伏、果蒂和堆叠。此时住宅首层仍像几块深色贴片。[第三轮临街面](evidence/architecture_final/home_05_facade.png) · [菜档](evidence/architecture_final/market_hall.png) |
| 四 | 打通 237 处首层临街窗，墙面、内侧抹灰、窗台、过梁在同一洞口收边。从街上可以看见窗帘、卷起的百叶和屋内墙面。楼上部分晒台封窗，玻璃后挂晾晒布。按原机位重拍市场、修理铺、茶摊和三栋普通住宅。[住宅外](evidence/landing_views/home_05_facade.png) · [住宅内](evidence/landing_views/home_05_inside.png) · [修理铺](evidence/landing_views/repair_facade.png) · [茶摊](evidence/landing_views/tea_facade.png) |

### 建筑和可走范围

- 76 栋、305 层延续上一版的 1,624 根柱和逐层梁板。Godot 复测 50,563 项梁柱、楼板和净空取样。2,272 处上层开口和 237 处首层窗均命中上下边。共有 369 处挑出阳台，其中 220 处封窗。Blender 复开组合模型后，检查了 104 台外机的 208 个墙托和 208 处脚垫。87 个导出地板图元同时保有纹理和接触阴影顶点色。[窗洞](evidence/landing_openings/openings.json) · [梁柱](evidence/landing_frame/frame_contacts.json) · [外机与地板](evidence/landing_composition/architecture_source.json) · [楼脚与斜坡](evidence/landing_composition/plinths.json)
- 原生玩家从市场连续步行 48.16 米进 201，经过全部七个目标点。逐栋穿堂及侧房进入、退出共 223 项，院坝路线 37 项。外圈五条主路均完成步行及骑行双向验证。整城 Blender 4.3.2 重开包含五个链接库、13 张外部图、302 株树和三处登记屋顶。[市场实走](evidence/landing_take/market_entry.json) · [住宅](evidence/landing_all/checks.json) · [院坝](evidence/street_courts/checks.json) · [外圈道路](evidence/landing_roads/routes.json) · [整城复开](evidence/landing_composition/combined_source.json)
- 邻楼全程复走时，4 号返回 53 号的低侧末级石梯卡住，单测却能通过。在末三级踏步侧面加进贴地石砌接坡，3 条断面各取 43 个位置，接缝前后 10 厘米最大高差 4.86 毫米。同次序复走全部 94 段通过。[原卡停](evidence/street_sequence/contact_sequence.json) · [单独走](evidence/street_lane_obstruction/contact.json) · [修后全程](evidence/landing_return/shared_paths.json) · [实机断面](evidence/landing_profile/landing_profile.json) · [面向上坡](evidence/landing_profile/uphill.png)
- 屋内与临街改造完成后，三个固定机位各连续采 90 帧。窗口 1152 × 648、渲染视口 692 × 389，RTX 4070 Laptop 采样期间处于 P8、210 MHz。街面、菜档和上院的 GPU 帧时中位数依次为 97.49、92.04、100.48 毫秒，上一版同机位为 92.79、86.50、98.32 毫秒。这组测量发生在 53 号接坡加入前。[本轮帧时](evidence/street_timing/timing.json) · [显卡状态](evidence/street_timing/gpu.csv) · [上一版帧时](evidence/frame_finish_timing/timing.json)

最终接坡版单独重测，照相巷街面、菜档、上院的 GPU 帧时中位数依次为 105.91、100.20、105.85 毫秒。显卡采样状态为 P8，核心频率为 210 MHz。三个机位均各测 90 帧。[最终新区帧时](evidence/landing_timing/timing.json) · [同次显卡采样](evidence/landing_timing/gpu.csv)

原 200 米城区用最终组合执行 `outer_architecture_03 -AllRoads -Timing`。师傅带骑 14 条路线、28 段，共 3453.97 米。玩家骑完 26 条地面道路的去程和回程，六处院坝与石梯接头完成 18 次步行往返。首班教学 85 项、午间订单 35 项通过。旧城折返坡、过街处、301 三处机位各采 150 帧，中位数分别为 213.68、337.56、439.44 毫秒。先前的 01 仅跑到带骑，02 巡检期间加入了 53 号接坡。上列数据出自重新开始的 03。[旧城区巡检](../../project/chongqing_godot_v05/verification_r24/district_patrol/outer_architecture_03/survey_summary.json) · [旧城区帧时](../../project/chongqing_godot_v05/verification_r24/district_patrol/outer_architecture_03/timing/timing.json)

原 ChatGPT 云工作区在同一试作的独立检出核对了四个 Blender／GLB 文件的大小和 SHA-256，实际重新导入，并从市场入口走入 201。云端也走通 94 个邻楼方向，记录到玩家与 53 号新接坡的 137 次接触，129 个断面点的最大接缝高差为 4.86 毫米。试玩从照相巷市场开始，使用 Mesa llvmpipe 软件渲染，本轮结束时工作盘剩余 19G。[云端核验摘要和原始结果目录](evidence/architecture_cloud.json)

临街窗后已有空间，远看的楼体比例和成排窗格仍相似。有些坡脚只见成片草地，缺少旧街沿墙长期使用留下的小构筑物。普通住宅楼上的房间只做了外部可见部分。视觉审看仍以玩家在街上行走的感受为准。素材的作者、许可、项目来源与文件指纹见[来源记录](sources.json)。

## 上一版室内梁柱与住用空间

上次制作提交为 `13d236ee696993cd6d2ff0952d64520798450465`。旧市场宽 22 米、进深 13 米，店面内两条横梁缺少中间支点，普通楼从首层上方到屋顶原是一整块建筑体量。76 栋现已用逐层边墙、楼板、纵横梁和连续立柱重建，首层改造沿用原有出入口。照相巷市场有三层、24 根柱，每层 38 段梁。剖视直接取自重开的 Blender 模型，为看清接头而隐去上层围墙、仅显示后侧楼板，灰色为柱、棕色为梁、蓝灰色为板。[市场原生视角](evidence/frame_finish_views/market_hall.png) · [剖视数据](evidence/frame_cutaway/cutaway.json)

| 修订 | 原位观察及修改 |
| --- | --- |
| 第一轮 | 全部新楼补入梁柱和各层楼板。11 个院坝的上下廊柱对轴，在石柱脚、木柱、通梁上承托楼廊，两户屋内都能看见木搁栅。厨房和洗衣间补进水槽、吊架、灶罩或洗衣机。柱网完成后，市场中段仍空，201 的床和帘布过于雷同。[市场](evidence/frame_views/market_hall.png) · [厨房](evidence/frame_views/ordinary_03.png) · [201](evidence/frame_views/market_bed.png) |
| 第二轮 | 将湿货台放入柱间，后场加备货台。睡铺改为四脚床、垂落的被沿和床头柜，床边增设挂物处。市场的部分菜叶轮廓过尖，卧室衣物像一张折纸，洗衣间窗下还露出一条斜杆。[市场](evidence/frame_final_views/market_hall.png) · [201](evidence/frame_final_views/market_bed.png) · [洗衣间](evidence/frame_final_views/ordinary_04.png) |
| 第三轮 | 菜档接入原院坝的竹背篓，重做叶片弯曲和菜堆轮廓。22 户楼上住家摆入木椅和背篓，窗帘使用原有棉布的织纹，枕面和挂巾改为有厚度、有褶皱的几何。洗衣间的斜线定位到旧坡道栏杆，将栏杆收在墙内，同时撤掉两个落入新楼的路灯灯位。[最终卧室](evidence/frame_finish_views/market_bed.png) · [最终洗衣间](evidence/frame_finish_views/ordinary_04.png) · [栏杆原命中](evidence/laundry_intrusion/pixel_hits.json) · [灯具原命中](evidence/laundry_fixture/pixel_hits.json) · [修后五个画面位置](evidence/frame_finish_laundry/laundry_pixels.json) |

### 实测范围

- Godot 4.6.3 从正常首班场景加载 76 栋的碰撞网格，在合计 305 个楼层核对 1,624 根连续立柱。50,563 项取样覆盖柱脚、楼地面、梁两端和跨中、板上下表面、跨内净空以及院坝木廊。实测最大轴线间距 4.816 米，命中表面与模型标高最大差约 0.37 毫米。首轮有 388 条射线从外侧先撞到了墙面，改从外柱的室内侧复测。这里核实的是游戏几何与碰撞位置。[初次射线记录](evidence/frame_contacts/frame_contacts.json) · [最终量测](evidence/frame_finish_contacts/frame_contacts.json)
- Blender 4.3.2 重新生成并打开整城组合，复查四个链接库、13 张外部图、原三处屋顶附件和 302 株树。另测 47 处新增竹篓和木椅的模型底部，均落在柜面或地板。原栏杆在房外的 5,212 个面中心与修后网格的最大距离约 0.26 毫米。[组合源重开](evidence/frame_finish_source/combined_source.json) · [摆设和房外栏杆量测](evidence/frame_finish_source/furnishing_contacts.json)
- 逐栋穿堂和侧房检查 223/223、院坝路线 37/37、邻楼和串门路线 94/94 通过。玩家从市场自然出生，连续走完通往 201 的 7 个目标，48.16 米，全程没有卡停。短片取 82 张原生玩家画面，按每 9 个物理步一帧播放。五条外圈主路步行、骑行双向 20/20，共 2,903.44 米。[逐户](evidence/frame_finish_all/checks.json) · [院坝](evidence/frame_finish_walk/checks.json) · [邻楼](evidence/frame_finish_shared/shared_paths.json) · [玩家短片记录](evidence/frame_finish_entry/market_entry.json) · [外圈骑步与断面](evidence/frame_finish_roads/routes.json)

原 25b 巡检用 `outer_frame_03 -AllRoads -Timing` 重跑。师傅带骑 28 段共 3,454.08 米，玩家骑完 26 条地面线路的去程和回程，六个院坝与楼梯接头完成 18 次步行往返。旧区三处机位各采 150 帧，GPU 帧时中位数为 197.07、304.75、425.75 毫秒。[旧区巡检](../../project/chongqing_godot_v05/verification_r24/district_patrol/outer_frame_03/survey_summary.json) · [旧区帧时](../../project/chongqing_godot_v05/verification_r24/district_patrol/outer_frame_03/timing/timing.json)

新区另开 Godot 单独采样，街面、菜档、上院三个固定机位各 90 帧。RTX 4070 Laptop 在全部 29 次显卡采样中均为 P8、210 MHz，窗口 1152 × 648，实际视口 692 × 389。GPU 帧时中位数依次为 92.79、86.50、98.32 毫秒，95 分位为 97.98、94.77、104.55 毫秒。同机位上一版中位数为 84.95、77.52、86.87 毫秒。这次三个机位均有退步，当前实测条件下没有达到稳定 30 帧。[新区帧时](evidence/frame_finish_timing/timing.json) · [同次显卡采样](evidence/frame_finish_timing/gpu.csv)

在原 OpenAI 云工作区，Godot 4.6.3 重新导入同一提交，Blender 4.3.2 复开新版打包源并测得 500 × 500 米地表。梁柱等 50,563 项几何取样、逐户 223 项及市场入口到 201 的 5 项检查均通过。新试玩窗口在照相巷市场实际打开，软件渲染使用 Mesa llvmpipe，声音回退到 Dummy；当时云盘剩余 19G。[云端实测与资产指纹](evidence/frame_cloud.json)

首层住户和共廊户型仍有重复，市场的部分货物、洗衣机及橱柜近景仍显简化，普通住宅上层的自由入户仍未制作。三处登记外景建筑维持原范围。来源、作者、许可和所用文件的 SHA-256 见[素材记录](sources.json)。

## 实景对照与六轮修改

参照项目收存的山城巷、山城步道及十八梯照片。厚慈街照片用于比较临街货摊与住户的距离，低层民居用于比较外梯、檐下空间和楼上入口，窄巷照片用于比较两侧墙体对通道的围合。街区的商业、住户和室内陈设为游戏设计。八张照片的年代、作者、许可和来源见[实拍图板](../street_photo_study/重庆老街八张实拍.jpg)与[逐张来源](../street_photo_study/reference/实拍来源.md)。[原生迭代对照](evidence/street_iterations.jpg)

| 轮次 | 实机看到的问题 | 实际修改和复核 |
| --- | --- | --- |
| 1 | 上版门面背后是整块几何；打开后又在修理铺内看到了另一栋楼的窗户。 | 将 78 个生成地块的首层改为有厚度的墙、门洞、侧窗和前后门；三处重点门面穿楼往返通过。保留了[初次可走的模型](evidence/round1_candidate.glb)、[穿墙像素命中](evidence/round1_views/repair_wall_hits.json)和[原位画面](evidence/round1_views/repair_hall.png)。 |
| 2 | 空间已经能穿过，但缺少用途，旧远景楼和窗组挡住了车铺。 | 按原供体成组撤去相撞的楼壳、窗组和所属屋顶附件。分别制作车轮工位、菜台和茶座，重做分片顶棚、檩条及排水边，再次连续走过三个门面。[修理间](evidence/round2_views/repair_hall.png) · [走测](evidence/round2_walk/checks.json) |
| 3 | 门后仍是裸坡；普通楼之间缺少可辨认的步行路线。 | 新作双层住宅、共用院坝、整跑外梯和有盖外廊，将邻楼、坡脚与街肩用随地形的石板路衔接。全数尝试首层时发现两户中段被旧高架穿过。[院坝初次复拍](evidence/round3_views/market_yard.png) · [两次受阻及其余逐栋结果](evidence/round3_all/checks.json) · [桥体命中](evidence/round3_walk/obstructions.json) |
| 4 | 桥下两处首层不可用；院子外廊上有大片白墙，部分檐口缺少可见承托。 | 保留高架，在两处取消相撞的新住宅。对修理铺后院向东偏置，补上前窗、窗台、屋檐支承、洗衣槽、花盆、茶桌、木椅与周转筐。市场摊主和修车人复用项目已有角色及动作。[修理铺后院](evidence/round4_views/repair_yard.png) · [逐栋首层](evidence/round4_all/checks.json) |
| 5 | 柜台过于分散，茶摊、菜市和车铺都像大开间。上层后窗太宽，进门看不清卧室用途。 | 用不同进深的柜台、半高墙和后场划分顾客过道、称重、茶水和修车区；悬灯、秤盘、配件板及货牌对齐实际工作面。住宅缩小后窗，补进床头柜、枕被及衣柜。[市场柜台](evidence/final_views/market_counter.png) · [车铺柜台](evidence/final_views/repair_counter.png) · [卧室原位](evidence/final_views/market_bed.png) |
| 6 | 三个重点门面能辨认用途，其余住宅的首层仍以过道为主。 | 在 73 栋普通住宅内，从公共穿堂开侧门进入分隔的生活空间，布置 22 间卧房、13 间厨房、18 间洗衣间、20 间起居室。房门、隔墙和主要家具随建筑一起参与碰撞。[普通住宅内侧](evidence/r6_views/ordinary_03.png) · [所有房间逐趟记录](evidence/r6_all/checks.json) |

## 上一版六轮试作的实走

精修游戏及 Blender 提交为 `8878d17326b9a9a7ad227514944da868cf0fce6b`。原 200 米核心沿用 25b，外圈尺寸为 500 × 500 米。76 栋新首层包括 73 栋普通住宅和三个公共门面。另有三栋按登记轮廓、屋顶标高保留的外部建筑体量。新院坝有 11 处、每处两户相连，已有 76 条通街铺装和 36 条邻楼共用铺装。普通住宅的其余楼层仍作外景，现有巡检只覆盖所列楼层、住宅和道路。专属外送订单尚未设计。

| Windows 原生检查 | 结果 |
| --- | --- |
| Godot 4.6.3，76 处前门至后门 | 76/76 单程贯通。每栋又从四个高度查找埋进过道的碰撞面，结果为空。[逐栋实走](evidence/r6_all/checks.json) · [扫线](evidence/r6_obstructions/obstructions.json) |
| 73 个住宅侧间 | 73 次进门、73 次回到街侧，累计 1,475.44 米。每次去程和回程中途均无重新定位。[地面行走](evidence/r6_all/checks.json) |
| 共用院坝和街巷 | 11 条进院、上梯、经外廊进住户的路线全部双向走通，往返累计 841.10 米。分四个方向各选一条邻楼通路，去返 8 段通过。[院坝和连接路径](evidence/r6_walk/checks.json) |
| 逐条邻楼通路和二楼串门 | 36 条坡巷逐条去返，72 段共 1,517.22 米。第 38 至 40 号地块间有一株原有行道树，首次直线回程碰到树干。沿现有 1.88 米宽铺装向宽侧让出 0.60 米后双向走通。11 处二楼 201 与隔壁住户经共廊互访，22 段共 301.84 米。[初次直走](evidence/r6_shared/shared_paths.json) · [全部 94 段复走](evidence/r6_shared_paving/shared_paths.json) · [复走脚本](shared_paths.gd) |
| 试玩入口 | 使用正常游戏入口和市场试玩参数，从出生点连续走过 7 个目标至 201，路长 48.14 米；两名店员的脚部原点与地面差均小于 7 毫米。短片保留 83 张实际玩家视角，每隔 9 个 60 Hz 物理步采一帧，约 12.45 秒。[入口数据](evidence/r6_entry/market_entry.json) · [原始帧](evidence/r6_entry) |
| 新旧区和外圈主路 | 原七处断面 2,275/2,275 个采样命中；五条出城线双向步行、双向骑行 20/20，2,903.43 米。三个旧门面前的原双侧台阶也复走过。[断面](evidence/r6_seams/sections.json) · [骑行及步行](evidence/r6_roads/routes.json) · [门前台阶](evidence/r6_aprons/destinations.json) |
| Blender 4.3.2 | 从原 25b 和新区源重建完整组合并实际重开。四个链接库、13 张外部图片和三个登记屋顶附件均核对，场景内有 302 株外圈树。院坝范围内为留出建筑和人行空间腾出四处树位。[重开记录](evidence/r6_source/combined_source.json) |

## 上一版六轮试作的旧区回归、帧时与云端复测

从正常首班场景执行 25b 的 `verify.ps1 -Run outer_homes_r6 -AllRoads -Timing`。师傅 14 条路线往返 28 段，共 3,454.05 米；玩家 26 条地面路线双向骑行全部通过。六处旧接头完成 18 次步行往返，300 个门槛断面样点的最大高差误差为 6.21 毫米以内。首班教学 85/85，午间送单 35/35。[整区巡检](../../project/chongqing_godot_v05/verification_r24/district_patrol/outer_homes_r6/survey_summary.json) · [旧接头原机位复拍](../../project/chongqing_godot_v05/verification_r24/district_patrol/outer_homes_r6/street_comparison.jpg)

另在本机独立测新区的街面、菜摊柜台与上院三个机位，各采 90 帧。RTX 4070 Laptop、Forward+，窗口 1152 × 648，实际视口 692 × 389，采样期间记录到 P8、210 MHz。三个机位的 GPU 帧时中位数依次为 84.95、77.52、86.87 毫秒，95 分位为 95.19、84.06、92.62 毫秒。这次条件下达不到稳定 30 帧。旧区三个不同机位各采 150 帧，中位数为 188.04、304.87 和 261.90 毫秒。[新区原始帧时](evidence/r6_timing/timing.json) · [同时段显卡频率](evidence/r6_timing/gpu_during.csv) · [旧区原始帧时](../../project/chongqing_godot_v05/verification_r24/district_patrol/outer_homes_r6/timing/timing.json)

同一制作提交已在原 OpenAI 云工作区重新导入 Godot 4.6.3，并用 Blender 4.3.2 重开打包源及组合城。云端 37 项院坝巡检和 223 项逐户巡检全部通过，市场自然出生到 201 连续走过 7 个目标、48.14 米。云桌面实开 800 × 450 的市场试玩，使用 Mesa llvmpipe 软件渲染、关闭太阳阴影，声音回退到 Dummy。实测时持久盘剩余 20G，这次原始云端记录用去 602M。[云端实测摘录与四个 LFS 对象指纹](evidence/cloud_r6.json)

## 制作与复拍

- 编辑[独立新区](../district_500/outer_district.blend)；整城的 `city_and_outer.local.blend` 由[组合脚本](../district_500/compose.py)从 25b 及新区重建。几何、材质和碰撞源见[主构建](../district_500/build.py)、[穿堂](../district_500/ground_floors.py)、[店铺及住房](../district_500/shop_rooms.py)、[院坝与坡巷](../district_500/hillside_courts.py)。集市牌字使用项目既有 OFL 字体重新取子集。
- 图板始终使用相同街面、室内和后院机位。后加的床边、柜台和楼廊近景随标签分别保存。使用 `survey.ps1 -Run 新目录 -View` 复拍，`survey.ps1 -Run 另一目录 -AllHalls` 重走各户，省略两开关时重走院坝。玩家短片用 [market_entry.gd](market_entry.gd)，需传 `--explore-500 --outer-market` 和全新 `CQ_QA_DIR`。
- 五类旧有扫描家具的作者、许可、纹理与编辑库哈希，店员与站立动作、字体及地图的来源均见[来源记录](sources.json)。临坡楼距、人物密度和部分粉墙的使用痕迹仍比实拍稀疏。这些街面请从两端在行进中审看。
