# 16 号东端并线复查

父版为 `d73189a8c68c9621a43d60807dcfdf2d5f92a4d1`。Godot 4.6.3 正常首班场景中，在同一路点、车速和通过阈值下，16 号并入 `176034697` 的去、回离地帧分别由 6、5 降为 0、0，两向各走通 12/12 个目标，里程 50.916、50.913 米。[父版逐帧接触](parent/join-rides.json) · [修订逐帧接触](candidate/join-rides.json)

- 父版去程第 410–412 帧，前轮触及另一股铺面的斜侧缘，接触法线向上分量最低 0.686。回程第 677–681 帧从接缝落回支线。
- 去程第 596–603 帧的接触来自圆形补面。第 605–607 帧离开补面后悬空，地面射线已命中下方主路。第 608 帧重新接触主路。原台阶与接尾分别造成去程的两组离地。
- Blender 4.3.2 沿两段轮迹取北向间隔 25 毫米的断面。第一处最大相邻高度变化由 114.6 降到 1.78 毫米，第二处由 76.5 降到 2.02 毫米，两段均只有一层铺面。首轮候选的分区边缘在 E212.326/N44.293 漏射。最终的同一碰撞网格在原锚点命中。[源剖面](source-sweeps.json) · [首轮漏射原记录](failures/join-rides.json)

另一股 `1189963552` 并线去、回各 12/12、零离地，里程 60.207、60.232 米。西接头去、回各 13/13、零离地。[接头实测](candidate/join-rides.json)

上游三点断面按原窗口复测，16 号 27/27，14 号 21/21。第一次共面试作中，16 两个上游测点落在原窗口下方；本版渐接从 N33.9 米开始，到 N37.0 米匹配共同坡面。[断面结果](regression/roads-14-16.json) · [原窗口失败](failures/early-blend-cross-sections.json)

04 原车线与江侧偏线均双向各 8/8，无墙体命中或离地。53 原石梯去、回各 6/6，里程 8.626、8.614 米，回到原点误差 4.3 厘米。GLB 有 51 件网格数据逐件与父版相同。[04 回归](regression/scooter-04-06-51.json) · [53 踏步](regression/stairs-53.json) · [导出对照](export-geometry.json)

## 固定机位

Godot 4.6.3 原生 700 × 440 PNG，Mesa llvmpipe Compatibility 软件渲染。每组前后使用同一相机矩阵及日照设置。

| 位置 | 父版 | 修订 |
|---|---|---|
| 16 支线来向 | [原图](parent/16-out.png) | [原图](candidate/16-out.png) |
| 16 并线后回望 | [原图](parent/16-back.png) | [原图](candidate/16-back.png) |
| 台阶低机位 | [原图](parent/16-contact.png) | [原图](candidate/16-contact.png) |
| 04 原桥下机位 | [原图](parent/legacy-04-under-rail-regraded-eye.png) | [原图](candidate/legacy-04-under-rail-regraded-eye.png) |
| 53 原石梯 | [原图](parent/53-original-stair.png) | [原图](candidate/53-original-stair.png) |

五组原图已逐张核对。16 两个来向和低机位的原车道立边消失。53 石梯图逐像素一致。04 图差异限于远处背景的 26 × 6 像素范围。53 落地的 129 个断面无失败，最大缝高差 5.257 毫米。Blender 重开整城组合后，六件接头源网格的三角面坐标与独立源一致。[相机与图像核对](native-check.json) · [53 断面](regression/landing-53.json) · [整城复开](candidate/combined-reopen.log)
