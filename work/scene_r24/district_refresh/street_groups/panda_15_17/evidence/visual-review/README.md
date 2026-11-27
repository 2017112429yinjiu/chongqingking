# 15、17 号近景复拍

原 `5b770510` 固定镜头的红夹克来自 Explorer 的第一人称身体图层。原机位、光线和默认掩码重拍所得 PNG 与已发布原图逐字节相同。镜头距玩家身体原点 2.041 米，`StreetNeighbor` 网格在第 18 层。保持相机矩阵，只在独立固定机位隐藏该层，遮挡随即消失。正常游戏相机仍显示原第一人称身体，玩家眼高实拍无遮挡。 [原图](../15-portal-after.png) · [只改固定相机掩码](15-fixed-player-layer-excluded.png) · [正常玩法](15-normal-playing-eye.png) · [测量](camera-audit.json)

| 同矩阵固定机位 | 父版无遮挡 | 精修后无遮挡 |
| --- | --- | --- |
| 15 橙框门廊 | [父版](15-portal-parent-clean.png) | [精修](15-portal-retouched.png) |
| 17 候车棚与店面 | [父版](17-bus-stop-parent-clean.png) | [精修](17-bus-stop-retouched.png) |
| 17 回望街边 | [父版](17-street-return-parent-clean.png) | [精修](17-street-return-retouched.png) |

窗口请求 900 × 560，16:9 原生画幅实际存为 900 × 506。三组相机矩阵、FOV 和昼间光照配置均沿用。Mesa llvmpipe 软件渲染，沿用前次固定帧的日照阴影开关。 [同机位与光照输入](summary.json)

15 号按同址实拍补柱面折纹、入门石侧墙、暗退进、分开的窗台与店招。17 号补低柜展品的浅后层、候车牌、直立树干及带边格栅树池。灰铺齐边，贴上逐块分缝和纵向触条。原来在玩家眼前偏斜的树沿用同一根位，树冠用项目既有许可的树材，主干、树池、站牌和可见招牌独立制作。招牌按可辨业态提示，窗后陈列为游戏的浅背景。只开放原可验公共门槛和候车步带。 [候车牌及触砖近看](17-shelter-sign-and-paving-retouched.png) · [15 号实景观察](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230515132559478AU&heading=326&pitch=0&fovy=80&width=900&height=560) · [17 号实景观察](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230515132603259AU&heading=334&pitch=0&fovy=80&width=900&height=560)

两种运行后端均从原 `first_shift.tscn` 用正常玩家控制器走两条线路、到端点原地返回。原走测继续留在上一层证据目录。追加精修的玩家原回望相机写入两张新帧。 [15 实走](15-native-walk.json) · [15 玩家回望](15-player-look-back-retouched.png) · [17 实走](17-native-walk.json) · [17 玩家回望](17-player-look-back-retouched.png) · [Blender 复开](blender-reopen.json)
