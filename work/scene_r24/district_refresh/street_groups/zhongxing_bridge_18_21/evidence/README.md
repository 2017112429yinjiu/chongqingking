# 18、21 号返图与正常场景复查

Godot 4.6.3 正常 `first_shift.tscn`，骑行和步行使用原控制器。原生图用 Xvfb、Mesa llvmpipe 和 OpenGL Compatibility，请求窗口 900 × 560，实存原生游戏画幅 900 × 506。四组父版和结果图共享各自的相机坐标、FOV 和原软件日照条件。

| 固定机位 | 父版 | 本轮结果 |
| --- | --- | --- |
| 18 低位看桥 | [改前](18-low-side-before.png) | [改后](18-low-side-after.png) |
| 18 上层反向 | [改前](18-bridge-return-before.png) | [改后](18-bridge-return-after.png) |
| 21 低位斜看 | [改前](21-low-side-before.png) | [改后](21-low-side-after.png) |
| 21 低位原路回望 | [改前](21-lower-return-before.png) | [改后](21-lower-return-after.png) |

18 号父版上层双向均在第一个目标前停住，实移 2.67、1.11 米。新版桥面原车各走约 20.40 米，双向各 7/7，零空中帧。最后的反向测试在封闭 QA 中运行。 [父版停骑](18-parent-stopped.json) · [新版完整轨迹](18-deck-rides.json)

21 号父版能经相邻原土坡往返，但旧住宅贴梁挡住视线。新步带在原路线 22.54 米去、22.47 米原地回，两向各 6/6。首次贴原坡的版本有 1 个过陡边缘点，复做石铺浅帽后 21/21 落脚样点通过。相机近侧仍可见原桥阴面与栏杆，回望图给出路肩、梁侧和原柱的连续关系。 [父版](21-parent-walk.json) · [首次断面不合格](21-first-grade-failure.json) · [新版](21-roadside-walk.json)

父版四地块共 1,680 条上下分层剖面，原始报告 `A2/base-sections/sections.json` 留在云端运行目录。本提交包含 18、21 中心剖面。Blender 4.3.2 独立源及组合城均重新打开，核三条带宽线的 21 个足点以及 88 个花槽支承参考点。 [父版中心剖面](parent-central-sections.json) · [Blender 复开](blender-reopen.json) · [统计与回归](summary.json)

首次软件返图的连续绘制开销使取图未完成，终止后用同条件停绘、逐帧读回。首次读盘和坡度尝试的日志留在云端手记指向的 `A2/`。 [仓内恢复入口](../../../evidence/REFRESH_RESUME.md)

父版与结果的原生批次退出码均为 0。每批在四张图保存完毕后，Compatibility 退出时各报两条 GL 纹理释放警告。原日志继续保留。
