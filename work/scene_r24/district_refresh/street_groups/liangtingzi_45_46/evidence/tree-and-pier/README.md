# 凉亭子树井登记与下巷白牌墩收尾

2019 年 181° 与 192° 两眼可反复辨认实景下巷白牌砖墩、蓝小牌砖墩、树井和低围栏，重取树干不同高度、白牌、灰铺及长椅。2015、2016、2017 年原片独立确认公共树井位于栏外，座椅接灰铺，浅灰楼在栏内。2017 明亮街眼还可见窗上铁笼、压顶与下巷转折。2019 的 161° 和 186° 用于核对相邻立面、窗根和构件顺序。[街眼、像素、年份和指纹](../../tree-and-pier-registration.json) · [原有白牌及蓝牌旁树干控制](../../field.json)

白牌同两眼重算 E156.296／N169.533，与已发布 149°／169° 白牌解相差约 0.45 米。旧模型的白牌位于这一可重复定位的街角。公共侧补细框、白底墨线、压顶分层和一段灰色错缝石铺。饰板上的文字在原片无法读清，保留可证的框、底板和印刷密度。现有下坡末段的整幅承面改为灰石纹理，加一层分缝细线。原路径的碰撞和高度一致。

树干底轴两眼候选 E150.681／N172.616，在旧轮廓内约 0.87 米。186° 的未校正射线相差 1.97 米，历史角度的 GPS 和姿态有较大差异。正常场景候选树根及灰铺处上方有 45 号旧框架，围护碰撞约 Y41.20，地面 Y40.26。长椅候选端 E154.551／N171.362 同样位于旧轮廓内约 0.89 米。蓝牌砖墩亦命中旧屋。登记的树、座椅和栏外关系足以确认冲突。楼脚的横向退界尚不能由这些点精确定界。现有许可树保留游戏落点，树井迁移、座椅和旧壳局部裁切待后续控制。后方真实共墙、私门和门牌分别待核。[正常场景竖剖面](tree-samples.json) · [28 点配置](sections-plan.json)

## 固定机位

Godot 4.6.3，Mesa llvmpipe Compatibility，700 × 440。前后逐帧保留一致的相机矩阵及光照。[相机矩阵和 SHA‑256](fixed-views.json)

| 机位 | 改前 | 改后 |
|---|---|---|
| 45 正向 | [PNG](before/45-field-axis.png) | [PNG](after/45-field-axis.png) |
| 46 正向 | [PNG](before/46-field-axis.png) | [PNG](after/46-field-axis.png) |
| 45 白牌控制 | [PNG](before/45-shared-pier-control.png) | [PNG](after/45-shared-pier-control.png) |
| 46 白牌控制 | [PNG](before/46-shared-pier-control.png) | [PNG](after/46-shared-pier-control.png) |
| 白牌墩和灰铺近看 | [PNG](before/lane-pier-close.png) | [PNG](after/lane-pier-close.png) |
| 下巷向街回望 | [PNG](before/lane-pier-back.png) | [PNG](after/lane-pier-back.png) |

终版复拍的首次尝试在第四张后受内存上限中止。归档两个原始退出记录。核验远端与本地工作副本的大小和 SHA‑256 后，释放相同的临时 LFS 对象再跑。[首件退出码](failed/native-exit.txt) · [终版首次尝试](failed/native-one-thread-engine.log) · [终版首次退出码](failed/native-one-thread-exit.txt)

首件铺面在近景表现为孤立棕色短条，保留原图。该趟写出六帧和矩阵后，软件渲染进程在退出时遇到内存限制，记录为 137。终版把灰铺并进整段面并以单线程软件渲染重拍，退码为 0。[保留首件和失败](failed/first-cut-paving.png) · [退出日志](failed/native-engine.log) · [主要步道、石梯几何对照](physical-model-compare.json)

终版正常首班场景。45 号实走去／回 11.397／11.432 米，各 5/5。折返点 E151.680／N179.857／Y42.563。46 号实走去／回 10.468／10.518 米，各 5/5。折返点 E157.492／N169.156／Y40.739。43 号正门双向各 3/3，后梯去／回 17.727／17.666 米，各 6/6。独立制作源复开，原两处通道支承 12/12。[最终 45／46](after/round-trip.json) · [最终 43](after/43-approaches.json) · [父版 45／46](parent-walk.json) · [父版 43](parent-43.json) · [Blender 4.3.2](blender-reopen.log)
