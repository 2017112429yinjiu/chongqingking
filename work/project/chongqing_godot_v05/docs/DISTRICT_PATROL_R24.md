# 200 × 200 米街区巡检 · 构建 25

从[穿楼托送练习](../../../穿楼托送练习.cmd)进入下院，到一单元 202 取餐。在二楼可直接从本楼楼梯上三楼，或经背巷进入蓝砖楼，爬折返梯、过连廊，回到同一个 301 户门。两条线都实际操作了取餐、敲门、放餐、结算和返回。正式入口 `first_shift.tscn` 从第一天入职开始。[本楼实走](../verification_r24/district_patrol/reviewed25/home/route.json) · [穿楼实走](../verification_r24/district_patrol/reviewed25/bridge/route.json)

## 老彭的 14 趟往返

在 Godot 4.6.3 正常街区中，老彭上自己的车，用带教时的车辆控制与碰撞开到每条路的终点，再原路回来。每条新路线单独就位一次。到终点后原地调头，行驶中没有传送。28 段共 3,453.91 米，全部到达。路线覆盖南区路、中兴路、东侧弯道、北界横街、临江路、坡下横街、南侧横巷、墙边支路、中央梯坎、西侧住区、小院入口、上院步道、旧校路和东照相巷。[14 条路线画面](../verification_r24/district_patrol/reviewed25/ride/visuals.jpg) · [逐段轨迹与距离](../verification_r24/district_patrol/reviewed25/ride/patrol.json)

## 现场修正与复核

| 地点 | 改动 | 复核 |
| --- | --- | --- |
| 一单元和蓝砖楼 | 在 202 层开出楼梯入口，接 17 级踏步和回廊，直通 301。封闭蓝砖楼入口可望穿的墙缝，撤下悬空斜顶，重建楼梯中墙、壁灯、靠墙扶手。 | 两路均完成送餐。蓝砖楼、天桥和回廊取 369 个地面及净高样点，所测最小净高 2.35 米。另从桥上恢复进度继续送达。 |
| 东照相巷和社区站后院 | 原路面、路基、压边和地面重叠。同步裁去旧面，以相邻真实边界重接。东巷局部最多削低约 38 厘米，后院约 18 厘米。服务站前后共用铺装尺度和颜色，后院在真实楼梯前收边。 | 两处各抽查 253 点，均命中各自的连续地面。老彭分别纵向、横向穿过接头并走回起点。 |
| 西侧住区和东巷的三个转角 | 裁去斜接两侧多余踏步，补转向平台及路基外露处。西侧另找到一层伸进平台的旧饰面，已裁掉。将挡在落脚区的长椅挪到路旁，并按新地面重调椅脚。 | 老彭从每个平台外起步，跨过两端再走回来。[三个转角](../verification_r24/district_patrol/reviewed25/turns/visuals.jpg) |
| 篮球场 | 三分线、边线、圆弧及红绿区域画在同一块地面。按坡脚和坡顶实际边界重切侧面石材，台阶口独立收边。 | 横跨各条标线的 585 个测点只命中球场基层，高度均为 20.530 米。 |
| 雨棚、住户外墙和铺装 | 三处雨棚共六摞筐按四角地面重新落位，原偏高 34～36 厘米。10 号住户外机连同机脚、支架和管线移到旁边实墙。撤掉旧式七条地漏箅的两组模型，保留墙边排水。按落点清理误入铺装的木屑、碎石。 | 对照脚部、门洞及支架近景，核对外机背后 20 个实墙样点。[十三个近景](../verification_r24/district_patrol/reviewed25/sites/visuals.jpg) · [源场景测量](../../../scene_r24/district_patrol/measurements.json) |

## 复验

为追查截图 9，又从旧场景的踏步和相邻道路交线找出三个需要返工的路口，分别位于街口、中央梯坎上段和上院窄巷。四个方向的旧画面可见踏步顶穿或互不相接。根据保留踏步的边界切除旧面和旧基础，重做三个接坡平台，把街口双柱移到平台外并落地。三个路口分别用老彭走完进路、转弯、出路和折返。保留原位对照；这三处加上西侧及东巷的三处转角，共六处。[旧接头四向对照](../verification_r24/district_patrol/legacy_match/visuals.jpg) · [修后同位置](../verification_r24/district_patrol/reviewed25/older_crossings/visuals.jpg)

本轮完整复跑 13 组功能与场景检查，共 278 项通过；计时单独运行。第一天三单、结业后的柜台、普通散单、午市拼送和桥上恢复均走原有入口。RTX 4070 Laptop、1152 × 648 窗口、692 × 389 内部视口，折返梯、桥面、301 各测 150 帧，GPU 中位数分别为 4.19、7.78、6.82 毫秒。[计时原始记录](../verification_r24/district_patrol/reviewed25/timing/timing.json)

在项目根目录运行 `work/scene_r24/district_patrol/verify.ps1 -Run 新目录名 -Timing` 可独立重验。Blender 4.3.2 的[完整制作源](../../../scene_r24/district_patrol/city_and_patrol.blend)已关闭后重开；游戏加载对应的导出层。[源与导出校验](../../../scene_r24/district_patrol/reopened.json) · [素材来源](../../../scene_r24/district_patrol/assets.json)

## 边界与保留记录

14 条骑行路线覆盖主路及支巷的通行线，步巡和近景集中在反馈地点。截图 9 的房屋与树池缺少唯一可辨的地址；同类接头已处理，原始拍摄点仍待对位。东巷外围仍有旧台阶向远处延伸，当前重铺范围和原图均已保留。街面美术效果留待玩家在游戏中判断。

十张[玩家原图](../../../scene_r24/district_patrol/player)、第一次卡在楼梯口的走查、重铺前仍有翘边的机位，以及老石阶饰面穿出新平台的实机画面都保留在本轮记录中。[首次受阻](../verification_r24/district_patrol/local01/route.json) · [重铺前的东巷](../verification_r24/district_patrol/sites_final/11_east_steps.png) · [重铺后的东巷](../verification_r24/district_patrol/reviewed25/sites/11_east_steps.png)
