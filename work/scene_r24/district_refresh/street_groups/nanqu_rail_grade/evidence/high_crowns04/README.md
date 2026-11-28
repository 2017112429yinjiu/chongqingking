# 04 号陆侧高冠与近景叶材

上一阶段 `da09e3f9639ae4655bed7f2a02ce663d083efd2f`，工作父版 `06a5e8c91977e3d476b3a678d0f9514789c31c1c`。复看同车前三站 110° 正向、各站 58° 陆侧补图与正射。正向窗带两端的低冠继续按先前控制，优先补第 16 行与第 75 行的断空。陆侧对照确定对向路仍有净空，草、坡、砖石、下层路及树根高程沿用原剖面。近树的分枝与较远的树带分别补上部轮廓。坡体绝对标高、现场单株与树种仍无足够证据。[阶段原图](../landside04/README.md) · [正反同址照片的链接与指纹](../landside04/observations.json) · [建模控制](landside-plan.json)

前版冠体的实色折面改为逐片裁形和 UV 的叶簇。使用 Poly Haven `Island Tree 01` 原许可叶扫，六种轮廓取点沿各叶内部，不为黑色背景加透明板。叶簇分散在单独的小枝空间，旧干及新增分枝复用项目已许可的树材。本次只改栽植增量的可见部分。引擎里的桥、罩和道面指纹以及坡体和树根触地保持一致。[许可与作者](../../../../../../project/chongqing_godot_v05/docs/MODEL_CREDITS.json) · [叶材原始来源](https://polyhaven.com/a/island_tree_01)

十一机位固定在同一 700 × 440 窗口、日照及视锥，使用 Godot 4.6.3、Mesa llvmpipe Compatibility，关闭太阳阴影。第 4 至 6 站的像素对照单列为控制。上缘诊断按第 y 行及相邻两行取绿像素连续性，色调与曝光会影响检测，读数为轮廓近似。现场照片不入库。[相机与原图对照](camera-and-image-compare.json) · [逐行像素](silhouette-rows.json) · [初件过宽和可见球团](failed/high-crown-first-fit.png)

| 机位 | 阶段图 | 最终图 |
|---|---|---|
| 1 | [正向](../landside04/after/pano-2922191AU-regraded-eye.png) · [陆侧](before/landward-1.png) | [正向](after/pano-2922191AU-regraded-eye.png) · [陆侧](after/landward-1.png) |
| 2 | [正向](../landside04/after/pano-2924863AU-regraded-eye.png) · [陆侧](before/landward-2.png) | [正向](after/pano-2924863AU-regraded-eye.png) · [陆侧](after/landward-2.png) |
| 3 | [正向](../landside04/after/pano-2926254AU-regraded-eye.png) · [陆侧](before/landward-3.png) | [正向](after/pano-2926254AU-regraded-eye.png) · [陆侧](after/landward-3.png) |
| 叶簇近看 | [阶段](before/crown-detail.png) | [细部](after/crown-detail.png) |

以同一色阈读三站，实景第 16 行的有色树冠右缘约 134／119／85 像素。阶段图三站空白，本版为 144／112／64。第 75 行现场约 189／151／155，阶段约 110／45／82，本版为 180／173／138。第二站的中高冠轮廓仍比实景宽约 22 像素，第三站略收窄。窗带高度的低缘仍看得到冠下、道路边缘、部分桥支承和对向净空。枝叶隐显随镜头移动，逐行像素只作诊断。[两种被拒试验](failed/)

原阶段的坡体与 12 支树干碰撞的几何、索引和变换逐项相同。Blender 4.3.2 复开 378 面坡体和 12 个树根，48 件树干、分枝或叶簇与北箱梁、罩、桥台和原车面均无交面。栽植增量 GLB 从 20,460,256 字节增至 59,996,612 字节。[碰撞导出比对](collision-export-compare.json) · [复开树根](blender-roots.json) · [净空](blender-crown-clearance.json)

Godot 4.6.3 从首班正常场景实跑。04 原轮线去／回 45.624／45.613 米，江侧偏线 45.674／45.714 米，均为各向 8/8、零离地、零撞墙。06–51 同层路线各向 9/9。00 进修车铺、互动充气、后院和返街 10/10。53 原石梯上下各 6/6，8.626／8.614 米。石梯接坡取样 129/129，接头最大变化约 5.257 毫米。39 组岸坡、车缘及相邻地面共 416 点的完整上下射线与阶段版逐项相同，另六站箱梁 90 点全与阶段版相同。第 4 至 6 站和旧桥下控制图逐字节相同。[运动和剖面](result.json) · [完整剖面](after/profiles.json) · [原生对照](camera-and-image-compare.json)

并行跑骑行与修车时骑行进程遇云端内存上限，退出 137。修车通过后用独立 QA 目录串行重跑骑行、石梯及踏面剖面，均退出 0。[内存失败原记录](failed/parallel-ride-engine.log) · [串行骑行](after/rides.json) · [石梯原记录](after/stairs-53.json)
