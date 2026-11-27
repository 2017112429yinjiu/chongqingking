# 原机位检修与三条路的连续往返

改前取公开父版 `75b9e2bb` 的原始帧。改后在相同眼位、指向、视野和光照参数下复拍。渲染为 Godot 4.6.3，Xvfb 下 OpenGL Compatibility 和 Mesa llvmpipe，PNG 实际为 900 × 506。 [渲染条件及退出告警](native-renderer.txt)

| 观察位置 | 父版 | 本批 |
|---|---|---|
| 弯道下层东向西看两梁端、圆柱和车库转角 | [原图](../../plots_63_66/evidence/bend-east-reverse-after.png) | [复拍](bend-east-reverse-after.png) |
| 长滨路园侧看灰路断点和相邻车道 | [原图](../../plots_63_66/evidence/road-and-park-west-after.png) | [复拍](road-and-park-west-after.png) |

[68 街边进园](east-side-street-entry-after.png) · [68 人行带旁的红色车道与方向箭头](east-road-markings-eye-after.png) · [走到终点后玩家原地转身](east-player-turn-after.png)

原图两处梁端像素分别命中 `1324001438`、`1256840000` 的旧结构。新图相同射线已越过旧梁端，地表和洞口是否接通另作断面检查。车库旧封闭转角的射线在新图命中浅色立框和邻近结构。原灰路尽头 `(768,327)` 从命中草坡变成命中长滨路连续沥青面，旧草面仍在其下。两处新车道红带和标线可从添设的街边眼位核对，原园边机位只能从柱梁和路面之间看到部分车带。 [同机位射线及可见标线采样](matched-camera-rays.json) · [源、导出和原图的 SHA-256](asset-and-frame-fingerprints.json)

Blender 4.3.2 独立源与组合城均复开，七段建模车道共 888 个面高样点。两处洞口及上层接续段各取 21 个接头点。两个洞口的重叠面高差分别小于 9 毫米和 8 毫米。 [重开与测点](blender-reopen.json) · [早期失败和修正](iterations.json) · [Godot 导入](godot-import.txt)

| 正常场景路线 | 进入 | 原地转身返同一街边 | 地面测点 | 两向最小车道中心线距离 |
|---|---:|---:|---:|---:|
| 63／65 车库外侧 | 27.360 米 · 8/8 | 27.343 米 · 8/8 | 27/27 | 6.875 米，1256859184 北侧 |
| 64／66 公厕与园边 | 54.251 米 · 15/15 | 54.227 米 · 15/15 | 48/48 | 5.525 米，59146737 南侧 |
| 67–69 批次的 68 下层公共步行带 | 22.879 米 · 8/8 | 22.955 米 · 8/8 | 27/27 | 7.244 米，1256859184 北侧 |

去回由同一角色连续完成，传送数和卡住记录均为零。上层机动车匝道在本批做了几何断面和原生画面检查。`1256840008` 接入游戏地形的局部样段最大纵坡为 30.64%，现场高程和骑行通过性待复查。 [63／65](bend-regression.json) · [64／66](park-regression.json) · [68](east-walk-native.json) · [62 公厕](pavilion-62-regression.json) · [修车](repair-regression.json) · [首班](first-shift-regression.txt)
