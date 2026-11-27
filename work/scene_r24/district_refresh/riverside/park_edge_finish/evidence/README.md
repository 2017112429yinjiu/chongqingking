# 原生同机位、地表与往返

同一机位、同一曝光条件与时段。Godot 4.6.3 Compatibility 通过 Xvfb 和 Mesa llvmpipe 输出原生 PNG，文件实际均为 900 × 506 像素。父版为 `2390fa09`，用引擎参数关闭收尾图层。两套都使用原 Linux 软件返图的关闭太阳阴影监测参数。街边接头相机复用了 59 号上一版的眼位和视野。

| 观察位置 | 改前 | 改后 |
|---|---|---|
| 长滨路步行带朝 59 | [原图](street-to-59-before.png) | [原图](street-to-59-after.png) |
| 地表折线接头近景 | [原图](west-fold-joint-before.png) | [原图](west-fold-joint-after.png) |
| 浅砂、草楔、树池与树带 | [原图](sand-grass-and-tree-plaza-before.png) | [原图](sand-grass-and-tree-plaza-after.png) |
| 59 原地转身，玩家镜头回望 | [原图](59-player-look-back-before.png) | [原图](59-player-look-back-after.png) |
| 61 走测终点的玩家眼高回望 | [原图](61-eye-back-toward-street-before.png) | [原图](61-eye-back-toward-street-after.png) |

街口两处原近景像素 `(538,475)`、`(632,445)` 由直接命中落叶土，变为先命中灰石补片。保留的老地表在下面，两处覆面相对原地表均高约 0.061 米。浅砂从旧混凝土分格改为无缝细粒底图，蓝绿改用哑光骨料，草和窄边单独铺设。最终返图前移除了试图中可见的规律斜纹。Blender 4.3.2 重开独立源与组合城，复核 3,529 个相关面、六套投影尺度、三株共用现有植物网格的新实例。 [表面逐点前后、材质和 UV](surface-comparison.json) · [导出 GLB 材质](glb-materials.json) · [Blender 重开](blender-reopen.json) · [61 号遮挡回归](plot61-sky-regression.json)

| 正常场景路线 | 从街进园 | 原地转身回同一街边 | 断面 |
|---|---:|---:|---:|
| 59 号至浅砂 | 14.626 米，6/6 | 14.607 米，6/6 | 24/24 点 |
| 61 号树带园路至江侧步道 | 21.722 米，6/6 | 21.880 米，6/6 | 21/21 点 |

每条去、回使用同一个玩家连续运动，报告中的两段间传送数均为 0。 [59 实走](walk-59.json) · [61 实走](walk-61.json) · [Godot 导入](import.txt) · [软件渲染改前](native-before.json) · [软件渲染改后](native-after.json) · [渲染后端与日志](native-renderer.txt)

叶种、准确株距和石板分格属于试作。61 冠下看不清的低设施仍待核。 [62 公厕](regression-pavilion-62.json) · [修车](regression-repair.json) · [首班](regression-first-shift.txt)
