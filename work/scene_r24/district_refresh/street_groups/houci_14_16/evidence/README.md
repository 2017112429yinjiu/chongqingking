# 14、16 号接头与 18 号候车带证据

| 固定机位 | 父版原生 PNG | 最终原生 PNG |
| --- | --- | --- |
| 14 号低街 | [父版](14-lower-street-before.png) | [最终](14-lower-street-after.png) |
| 14 号弯口回望 | [父版](14-upper-bend-return-before.png) | [最终](14-upper-bend-return-after.png) |
| 16 号低侧坡脚 | [父版](16-spur-slope-foot-before.png) | [最终](16-spur-slope-foot-after.png) |
| 16 号低侧反向 | [父版](16-spur-return-before.png) | [最终](16-spur-return-after.png) |
| 16 号上层接近 | [父版](16-deck-approach-before.png) | [最终](16-deck-approach-after.png) |
| 16 号上层反向 | [父版](16-deck-reverse-before.png) | [最终](16-deck-reverse-after.png) |
| 18 号候车带看桥 | [父版](18-public-bridge-overlook-before.png) | [最终](18-public-bridge-overlook-after.png) |

机位组使用同一相机矩阵、视场与昼间设置。16 高机位取拟建匝道驾驶眼位，父版该处缺车面。14 号从街边可辨新弯，保留外围旧背景。16 号最早的试件在低机位表现为两道过高的砖墙。最终用有封底的短跨与落地支承，接上砖路缘和金属栏。现场支承样式仍待实地断面。原生 PNG 为 900 × 506，Godot 4.6.3 用 Xvfb、Mesa llvmpipe 和 OpenGL Compatibility。部分引擎在保存完毕后退出时报告两条 GL 纹理释放警告，所有出图进程成功退出。 [矩阵和结果摘要](summary.json)

| 公共步带正常玩家 | 连续路线及接触 | 端点实际回望 |
| --- | --- | --- |
| 14 | [去回及断面](14-public-round-trip.json) | [玩家回望](14-normal-player-look-back.png) |
| 16 | [去回及断面](16-public-round-trip.json) | [玩家回望](16-normal-player-look-back.png) |
| 18 | [候车处去回及断面](18-public-round-trip.json) | [玩家回望](18-normal-player-look-back.png) |

步行从 `first_shift.tscn` 的 `--explore-500` 正常玩法入口出发，在同一观察端点转身走回原街边，去回间未重置位置。14、16 的端点停在公共步带，记录离旧足迹的最短距离。骑行用首班电瓶车控制器与物理，16 逆向仅作封闭 QA。改造前失败包含当时原六路点基准与同一组新版路点的精确父版回放。 [原失败](original-failed-rides.json) · [同路点父版](exact-parent-rides.json) · [新版车测和断面](road-14-16-rides.json) · [单独 18 号原上层桥面](regression-upper-18.json)

独立 Blender 源和链接组合城均用 4.3.2 重新打开。验证新网格 UV 和 48 个断面点，原地块框架及旧附属撤下。Godot 重新导入并复验正常首班、修车、照相巷便民市场和山城巷送单。 [Blender 复开](blender-reopen.json) · [首班](regression-first.json) · [修车](regression-repair.json) · [照相巷](regression-market.json) · [山城巷](regression-handoff.json)
