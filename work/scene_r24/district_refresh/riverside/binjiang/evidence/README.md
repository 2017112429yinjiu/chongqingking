# 滨江壹号与解放西路 70–73 号实测

四组使用同一眼位、朝向和视野。父版为 `7208f355`。Godot 4.6.3 通过 Xvfb、Mesa llvmpipe 和 Compatibility 导出原生 900 × 506 PNG，沿用关闭太阳阴影的拍摄参数。70、71 的浅色塔和裙房属同一栋。72 的铺地通向两楼之间。73 看到的是相邻楼红褐色弧形裙房和街边公共铺地。层高、门后、停车层深度和被遮挡背面仍待实测。 [图源与观察表](../README.md) · [机位和图像指纹](native-conditions.json)

| 旧地块 | 同机位改前 | 同机位改后 | 从解放西路走入 | 转身返回同一街边 | 地表测点 | 距道路中心线最小值 |
|---|---|---|---:|---:|---:|---:|
| 70 | [原图](plot-70-before.png) | [原图](plot-70-after.png) | 15.236 米，5/5 | 15.157 米，5/5 | 18 | 8.35 米 |
| 71 | [原图](plot-71-before.png) | [原图](plot-71-after.png) | 29.178 米，7/7 | 29.230 米，7/7 | 24 | 8.14 米 |
| 72 | [原图](plot-72-before.png) | [原图](plot-72-after.png) | 24.581 米，6/6 | 24.614 米，6/6 | 21 | 7.07 米 |
| 73 | [原图](plot-73-before.png) | [原图](plot-73-after.png) | 16.490 米，5/5 | 16.446 米，5/5 | 18 | 7.03 米 |

四组在正常 `first_shift.tscn` 以同一玩家实体走去回两段，转身时零传送，最终均无卡点。 [70 实走](walk-70.json) · [71 实走](walk-71.json) · [72 实走](walk-72.json) · [73 实走](walk-73.json) · [72 玩家眼高转身](plot-72-turn-after.png)

- 父版 71 走到约 29.564 米处撞旧壳，达到 6/7 个目标点。72 父版在 20.604 米处撞旧壳，达到 5/6。73 父版在 8.159 米处撞旧壳，达到 2/5。70 父版在同一走线可通。 [71 玩家撞墙原图](blocked-71.png) · [71 碰撞日志](blocked-71.json) · [72 父版](baseline-walk-72.json) · [73 父版](baseline-walk-73.json) · [70 父版](baseline-walk-70.json)
- 73 的中间版出现浅灰外墙穿插。以原图像素发斜射线，命中 `R24_East_Block_0` 的旧墙、阳台与玻璃。最终试玩隐藏五个确认重叠的面组。 [中间失败图](plot-73-overlap-trial.png) · [逐像素射线记录](overlap-rays.json) · [修后同机位](plot-73-after.png)
- Blender 4.3.2 重开独立增量与组合城，两者的楼体边界、81 个铺地测点和退役面数一致。Godot 4.6.3 重新导入后实走，原生图导出成功，退出日志记录了 Compatibility 下的纹理释放告警。 [Blender 复开](blender-reopen.json) · [Godot 导入](godot-import.txt) · [渲染器日志](native-conditions.json)

| 回归项目 | 结果 |
|---|---|
| [长滨路弯](regression-bend.json) | 27.360 / 27.343 米，两向各 8/8 |
| [滨江园路](regression-park.json) | 54.251 / 54.227 米，两向各 15/15 |
| [雷家坡东弯步行](regression-east.json) | 22.879 / 22.955 米，两向各 8/8 |
| [雷家坡东弯电动车](regression-rider.json) | 顺行下坡 70.763 米，封闭测试上坡 71.723 米，两向零腾空帧与传送。 [坡面与邻道测点](regression-ramp-surface.json) |
| [山城巷取送](regression-shancheng.json) | 12/12 |
| [修车](regression-repair.json) | 10/10 |
| [默认首班](regression-first-shift.txt) | 85/85 |

[实测数值汇总](measurements.json)
