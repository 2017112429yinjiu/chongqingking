# 照相巷市场、山坡住宅和共用院坝

在 Windows 双击[逛照相巷院坝](../../逛照相巷院坝.cmd)。人物站在市场台阶上，电瓶车停在通街的一侧。走过菜摊，从后门进院，转上石梯，沿二楼木廊可以走进 201。云桌面在独立检出运行 `bash work/scene_r24/district_500/play.sh --software -- --explore-500 --outer-market`。[玩家连续实走短片](evidence/market_to_201.mp4) · [六个原生视角](evidence/market_to_home.jpg)

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

## 最终实走

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

## 制作与复拍

- 编辑[独立新区](../district_500/outer_district.blend)；整城的 `city_and_outer.local.blend` 由[组合脚本](../district_500/compose.py)从 25b 及新区重建。几何、材质和碰撞源见[主构建](../district_500/build.py)、[穿堂](../district_500/ground_floors.py)、[店铺及住房](../district_500/shop_rooms.py)、[院坝与坡巷](../district_500/hillside_courts.py)。集市牌字使用项目既有 OFL 字体重新取子集。
- 图板始终使用相同街面、室内和后院机位。后加的床边、柜台和楼廊近景随标签分别保存。使用 `survey.ps1 -Run 新目录 -View` 复拍，`survey.ps1 -Run 另一目录 -AllHalls` 重走各户，省略两开关时重走院坝。玩家短片用 [market_entry.gd](market_entry.gd)，需传 `--explore-500 --outer-market` 和全新 `CQ_QA_DIR`。
- 五类旧有扫描家具的作者、许可、纹理与编辑库哈希，店员与站立动作、字体及地图的来源均见[来源记录](sources.json)。临坡楼距、人物密度和部分粉墙的使用痕迹仍比实拍稀疏。这些街面请从两端在行进中审看。
