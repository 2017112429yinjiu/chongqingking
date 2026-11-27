# 11 号低街路口和侧巷实测

| 固定机位 | 原场景 | 改造后 |
| --- | --- | --- |
| 低侧中兴路回看红砖裙房邻口 | [原图](11-main-street-before.png) | [新图](11-main-street-after.png) |
| 凤凰台路侧巷反向 | [原图](11-south-spur-return-before.png) | [新图](11-south-spur-return-after.png) |
| 下回水沟反向 | [原图](11-north-spur-return-before.png) | [新图](11-north-spur-return-after.png) |
| 路缘灰铺 | [原图](11-public-footway-before.png) | [新图](11-public-footway-after.png) |

四对画面使用同矩阵、视场和昼间设置。侧巷反向眼位沿用父版高度，可俯看新版下切车面。固定帧 900×506，Godot 4.6.3，Xvfb 和 Mesa llvmpipe OpenGL Compatibility。[实际玩家起步](11-normal-start.png) · [实际玩家回望](11-normal-look-back.png) · [原街边返回](11-normal-street-return.png)

基准场景采了 520 个竖向剖面点，原 11 号旧住宅与两处登记道路在平面和高度都有干涉。父版按实测游戏地面起步，四个方向没有走完。第一次清障后四个方向能走完，但游戏地形让凤凰台侧巷往外上升，和同址照片可见的坡向冲突。这次失败图及试骑保留。终版使用局部下切和落地的砖石边，灰铺通到可见的公共路侧观察点。游戏标高在保留原中兴路连接后调整。现场工程坡度、裙房洞口和北侧住区内部仍待定位。[父版同路剖面](parent-road-centrelines.json) · [父版试骑](parent-rides.json) · [首次上坡试件](11-original-uphill-attempt.png) · [首次可通试骑](uphill-attempt-rides.json)

终版两条路用首班电瓶车控制器跑来回。步行从正常探索入口起步，在灰铺端点原地转身回到同一街边。Blender 4.3.2 重开独立资产及组合城。 [最终车测](final-rides.json) · [最终步行](final-public-walk.json) · [Blender](blender-reopen.json) · [首班](regression-teaching.json) · [照相巷](regression-market.json) · [收藏品市场](regression-collectibles.json) · [修车](regression-repair.json) · [摘要](summary.json)
