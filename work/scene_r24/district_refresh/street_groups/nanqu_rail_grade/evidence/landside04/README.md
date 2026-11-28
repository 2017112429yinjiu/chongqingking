# 04 陆侧树冠与坡地

父版 `9888c95c0c8a94200525963ece3aee7ad9c0d64f`。用 2023-05-15 同车前三站的 110° 正向和 58° 陆侧补图对照。正向图在罩体的窗带高度，冠缘随车从约 x314、221 退到 x128。三组视线两两相交落在约 E−151 至 −145、N−59 至 −58 米。三站看到的是树冠群的不同边缘，交点给出遮挡带的范围。陆侧补图能看见花槽带之后的对向车辆，只有少量坡石、砌体从冠下和桥旁显露。另用正射图确认树带在南区路车行带的陆侧。[照片、航片链接及指纹](observations.json)

原桥端伸入坡地的位置照原轨道登记保留。新增坡体位于 `49182408` 中心线陆侧，植坡及单株树高按游戏地表和可见范围拟合。不从照片推断绝对高程。木干复用项目已有的扫描树材，树冠用独立建模的绿叶和小簇体。开着树冠和只保留坡体分别拍摄，前者遮住陆侧收头，后者显示坡体和梁端各自在哪里。第三站桥下仍可辨局部支承。其余罩、梁、行车路面继续使用父版文件。[源码控制](landside-plan.json) · [根部实测](blender-root-contacts.json) · [冠、桥、路排交](blender-crown-clearance.json)

## 行车与相邻玩法

- 04 原车线去／回 45.624／45.613 米，江侧偏线 45.674／45.714 米，四向各 8/8，零离地、零挡墙命中。06 至 51 双向各 9/9。[原车线和偏线接触](after/rides.json)
- 32 条梁、路面与低街的完整竖剖面射线及 64 个 `49182408` 中心、陆侧近肩采样与父版逐项一致。[父版地表](before/profiles.json) · [修订地表](after/profiles.json) · [差分](profiles-compared.json)
- 00 号修车场的首次回归撞到新增坡体后缘。最终给原玩法路线预留 4.9 米宽度控制范围，再用同一输入实走、充气与返街，10/10 通过。[相邻玩法失败](failed/repair-slope-hit.json) · [最终走测](after/repair.json)
- Blender 4.3.2 复开新增源与重建的组合城。12 处树根落在设计坡面，树冠和木干与箱梁、罩体、桥台及上层车面均无交面。[单独复开](blender-reopen.log) · [组合城复开](blender-combined-reopen.log)

## 原生固定视图

同机位前后 700 × 440 PNG，Godot 4.6.3，Xvfb／Mesa llvmpipe Compatibility。原行车视角、机位矩阵、日照和视宽相同。前三站陆侧树冠遮住跨路段之外的接头，第三站冠下仍可见局部支承。第 4、5 站的梁下缘和罩体横贯画幅。第 6 站走到梁下，箱梁横贯画幅，罩体在右上方入画。第 4 至 6 站的改前和改后图逐字节一致。树冠形状、地下不可见范围和背景楼群仍属近似。入库图片均由引擎实际输出。[相机参数](camera-plan.json) · [逐帧指纹与可见范围](native-comparison.json) · [过疏树冠试作](failed/sparse-trees-station-3.png)

| 站 | 父版 | 新树冠和坡地 | 只显坡体 |
|---|---|---|---|
| 1 | [PNG](before/pano-2922191AU-regraded-eye.png) | [PNG](after/pano-2922191AU-regraded-eye.png) | [PNG](bank-only/pano-2922191AU-regraded-eye.png) |
| 2 | [PNG](before/pano-2924863AU-regraded-eye.png) | [PNG](after/pano-2924863AU-regraded-eye.png) | [PNG](bank-only/pano-2924863AU-regraded-eye.png) |
| 3 | [PNG](before/pano-2926254AU-regraded-eye.png) | [PNG](after/pano-2926254AU-regraded-eye.png) | [PNG](bank-only/pano-2926254AU-regraded-eye.png) |
| 4 | [PNG](before/pano-2927597AU-regraded-eye.png) | [PNG](after/pano-2927597AU-regraded-eye.png) | |
| 5 | [PNG](before/pano-2928988AU-regraded-eye.png) | [PNG](after/pano-2928988AU-regraded-eye.png) | |
| 6 | [PNG](before/pano-2930784AU-regraded-eye.png) | [PNG](after/pano-2930784AU-regraded-eye.png) | |

六站每站取陆侧、路中和江侧三线，各五点重打正常场景竖射线。90 点均从上下命中同一箱梁碰撞体，完整命中与已发布剖面一致。当前箱梁和罩体所在模型指纹与父版一致，已发布 Blender 测量均为 90/90。梁罩沿原轴实际延伸到陆侧接头，采用 N−47.6 米控制。首、二、末站中央视线的近／远缘仍为 N−70.93／−79.78、−78.53／−87.38、−84.88／−93.73 米。原跨路箱梁及罩体由同一套资产接管。[本批六站碰撞实测](after/six-span-readback.json) · [既有网格覆盖](../normal/rail-span-coverage.json)
