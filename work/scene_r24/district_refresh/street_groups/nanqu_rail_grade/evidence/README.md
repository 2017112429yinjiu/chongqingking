# 04 号轨道桥回归证据

对照组来自 `6b2e0d2b7043217b5fecfa7f27cd379b659d45be`。三列为 Godot 4.6.3 的原生 700 × 440 PNG，采用同一时段光照和 Xvfb／Mesa llvmpipe Compatibility，太阳阴影关闭。中列保持左列的固定世界眼位，矩阵逐项一致。右列保持同向和同投影，相机升到新车面上 2.32 米。原游戏机位使用游戏原眼高 1.63 米。[矩阵及帧 SHA-256](native/matrix-check.json) · [运行日志](native/corrected-engine.log)

| 站号 | 原车面 → 新车面（游戏米） | 中央视线近／远缘 N（米） | 原版固定 | 修后同世界坐标 | 修后同眼高 |
|---|---:|---:|---|---|---|
| 1 | 10.33 → 33.90 | −70.93 / −79.78 | [PNG](native/baseline-fixed/pano-2922191AU.png) | [PNG](native/corrected-world-fixed/pano-2922191AU.png) | [PNG](native/corrected-eye/pano-2922191AU.png) |
| 2 | 7.80 → 33.78 | −78.53 / −87.38 | [PNG](native/baseline-fixed/pano-2924863AU.png) | [PNG](native/corrected-world-fixed/pano-2924863AU.png) | [PNG](native/corrected-eye/pano-2924863AU.png) |
| 3 | 7.39 → 33.72 | −81.38 / −90.23 | [PNG](native/baseline-fixed/pano-2926254AU.png) | [PNG](native/corrected-world-fixed/pano-2926254AU.png) | [PNG](native/corrected-eye/pano-2926254AU.png) |
| 4 | 7.37 → 33.59 | −83.22 / −92.08 | [PNG](native/baseline-fixed/pano-2927597AU.png) | [PNG](native/corrected-world-fixed/pano-2927597AU.png) | [PNG](native/corrected-eye/pano-2927597AU.png) |
| 5 | 7.65 → 33.48 | −84.19 / −93.05 | [PNG](native/baseline-fixed/pano-2928988AU.png) | [PNG](native/corrected-world-fixed/pano-2928988AU.png) | [PNG](native/corrected-eye/pano-2928988AU.png) |
| 6 | 8.30 → 33.27 | −84.88 / −93.73 | [PNG](native/baseline-fixed/pano-2930784AU.png) | [PNG](native/corrected-world-fixed/pano-2930784AU.png) | [PNG](native/corrected-eye/pano-2930784AU.png) |
| 原游戏机位 | | | [PNG](native/baseline-fixed/legacy-04-under-rail.png) | [PNG](native/corrected-world-fixed/legacy-04-under-rail.png) | [PNG](native/corrected-eye/legacy-04-under-rail.png) |

右列肉眼复核，前三站的陆侧接头位于左侧车缘之外，箱梁和声屏罩跨过整条车道，照片中接头所在区域有树冠遮挡。第 4、5 站罩体与梁下缘横贯画幅，第 6 站已在梁下，箱梁仍横贯画幅，罩面位于视锥上方并露出右上边缘。Blender 箱梁、罩体以及 Godot 箱梁碰撞的 90 个断面点全部命中。罩体沿已登记双线进入陆侧接头，双线的实测平面端点分别为 N−47.46、−45.71 米。现有陆侧地形和树冠与实景仍有差异，前几站看得到结构收头。站位 4–6 的下层背景、紫花密度及远处街缘也有可见差异。[覆盖实测](normal/rail-span-coverage.json) · [站位和原照片链接](field/camera-reprojection.json) · [柱头与梁底独立复算](field/independent-rail-rays.json)

## 实际走测

| 路线 | 去／回 |
|---|---|
| 04 原轨迹 | 45.624 / 45.613 米，两向各 8/8，无离地或墙体命中 |
| 04 江侧偏线 | 45.674 / 45.714 米，两向各 8/8，无离地或墙体命中 |
| 06–51 车线 | 51.606 / 51.596 米，两向各 9/9，沿街花箱脚 32/32 |
| 51 望江铺带 | 89.879 / 89.890 米，两向各 15/15 |
| 西接头 | 63.205 / 63.183 米，双向通过 |
| 16 并入 `176034697` | 50.914 / 50.936 米，双向通过，合流区 6 / 5 帧短时离地 |
| `1189963552` 并入 `176034697` | 60.143 / 60.223 米，双向通过 |
| 18 上桥 | 20.407 / 20.412 米，两向各 7/7 |
| 21 下层步带 | 22.536 / 22.467 米，两向各 6/6 |
| 53 原石梯 | 8.626 / 8.614 米，两向各 6/6；降差 3.072 米，回到原点误差 0.043 米 |

53 号踏面有 15 / 49 帧接触记录，129 个断面取样无失败，落地缝最大高度差 5.257 毫米。16 号局部断面 27/27 有车面，含并线处 2 个样点。历史路线、并线早期未通过及环境失败均保留。[04 骑测](normal/scooter-04-06-51.json) · [两端接头](normal/joins.json) · [53 踏步](normal/stairs-53.json) · [53 断面](normal/landing-53.json) · [失败记录](failures/)

正常首班回归包含首班教学、送餐与存档 85/85，市场走到 201 为 5/5，修车及回街 10/10。全路按去、回各三批运行，各通过 26 条和 1,173 个目标。地面审计记录 16,004 个断面点，原路线 `59146775` 的 1,043 个采样使用新车面垂直参考。软件截图前一次超出内存，隔离后完整输出。两版软件引擎退出时均有等量 GL 纹理清理警告。[首班](normal/first-shift.json) · [市场](normal/market.json) · [修车](normal/repair.json) · [全路](normal/all-roads/summary.json) · [地面审计](normal/ground.json)
