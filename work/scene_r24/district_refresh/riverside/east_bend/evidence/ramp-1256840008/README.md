# 1256840008 匝道接坡

登记轴保留五个节点，由 `11684497756` 至 `1865946191`（E89.9377／N−96.7129）。终点连 `1189963598` 南区路和 `830761786` 解放西路。2023 年南区路东西对向街景可辨独立的高架曲梁、圆柱、邻侧护栏和连续低层沥青。照片只支持这些层级和关系。真实纵坡、绝对标高和护栏施工顺序留待现场核查。 [向东的 104°](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230514155823653AU&heading=104&pitch=0&fovy=79&width=900&height=560) · [向西回望 252°](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230514155820465AU&heading=252&pitch=0&fovy=79&width=900&height=560) · [机位、来源和制作参数](../../grade-1256840008.json)

父版 `95d42021` 在 E76.2 截断，原模型局部最大纵坡为 30.64%。游戏射线先命中坡土，随后才碰到核心区的旧短车面。登记合流节点中心测到 7.722 米的原地表，两侧既有沥青在约 7.95 米。新版把两侧沥青接齐，并以实测上桥车面高程接入 1256839997。匝道全长 **40.163 米**，两端中心车面实测 **11.796 米和 7.955 米**。弯段纵坡平顺，合流前收窄内侧边缘。导出核对仅三个既有网格发生变化，增一个节点补面，其余网格数据一致。 [父版接触断面](baseline-contact.json) · [纵断面对比图](longitudinal-profile.png) · [导出范围](mesh-scope.json)

Godot 4.6.3 最终 **360/360** 个匝道样点、**45/45** 个邻侧车道样点通过。中心线最大实测纵坡 **11.81%**。匝道测点法线竖向分量最小 **0.99116**，最高贴合偏差 **6.81 毫米**。45 个邻侧测点向上查 8 米，均无悬顶命中。第一版虽骑完，但在南区路侧有一个 **0.247 米** 的净空失败点，修正后复跑。Blender 4.3.2 重开独立源和组合城。 [最终法线、接头与邻侧净空](final-surface.json) · [中间版净空失败](intermediate-clearance-failure.json) · [Blender 重开](blender-reopen.json)

## 玩家电瓶车

正常 `first_shift.tscn` 的 `PlayerElectricScooter` 使用原控制器、原碰撞体和原上车流程。每方向在既有车面放置一次测试起点，上车后只给油门、转向和刹车输入。两次试验分开，封闭反向用于坡道牵引验证。两方向骑行中均无传送。

| 方向 | 父版 | 最终 |
|---|---|---|
| 顺行下坡，1256839997 → 1256840008 → 830761786 | 走 50.651 米后离开车面，进入坡土 | 70.763 米，接入现有解放西路沥青 |
| 封闭反向上坡 | 走 20.193 米后失去车面支承，最长离地 4 帧 | 71.723 米，返回上游 1256839997 |

最终两次均无离地、无碰撞阻挡。顺行下坡在 **15.36 km/h** 时制动，**0.483 秒、0.989 米** 刹停，保持 1 秒位移为零，随后继续驶过合流。封闭上坡到达上游后刹停，测得 **0.483 秒、0.984 米**。 [原版骑行](baseline-rider.json) · [最终骑行与车轮下方射线](final-rider.json)

同一候选重跑上批 63／65、64／66、68 的三条独立步行路线。 [63／65](walk-bend.json) · [64／66](walk-park.json) · [68](walk-east.json)

另用 Xvfb 和 Mesa llvmpipe Compatibility 连续重跑骑行，从实际玩家镜头取两张 900 × 506 原生帧。 [实车下坡刹停](downhill-brake-stop.png) · [驶向解放西路合流](toward-jiefang-merge.png) · [渲染后端和帧位置](native-capture.json)

从仓库根目录按 [原重建步骤](../../README.md) 导出和导入。以全新输出目录运行骑行。

```sh
checks=work/scene_r24/district_refresh/riverside/east_bend
CQ_QA_DIR=/tmp/cq-ramp-new CQ_RAMP_PLAN="$PWD/$checks/grade-1256840008.json" \
  godot --headless --path work/project/chongqing_godot_v05 --fixed-fps 60 \
  --script "$PWD/$checks/ride_1256840008.gd" -- --day-one-test --qa-still-frames --explore-500
```

`CQ_RAMP_BASELINE=1` 在精确父版的正常场景只跑同样的骑行检查，便于复现原版失败。
