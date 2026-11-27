# 厚慈街 77 号实测和原像素返图

镜头坐标、视角、分辨率与确认的渲染后端见 [机位表](../views.json) 和运行日志。改前与改后都是 Godot 4.6.3 Compatibility 从同一组固定机位导出的 900 × 560 窗口原生 PNG。运行条件为 Xvfb、Mesa llvmpipe 和项目原有软件模式的日照阴影关闭参数。

| 机位 | 改前 | 改后 |
| --- | --- | --- |
| 沿厚慈街向东看原占位 | [原图](west-street-before.png) | [原图](west-street-after.png) |
| 由东向西回望弯道 | [原图](east-street-before.png) | [原图](east-street-after.png) |
| 对面低街朝旧足迹和北坡 | [原图](street-to-podium-before.png) | [原图](street-to-podium-after.png) |

[第一次收尾的车道内路灯与偏褐铺面](east-street-first-finish.png) · [原地转身时的玩家镜头](player-look-back-after.png)

旧版同路线从街边起步，走 10.19 米到 3/6 个路点后被 `COL_Outer500_Building_envelopes` 挡停。新版保留同一套路点，16.97 米走到旧足迹内，原地转身后 17.04 米走回同一街边。两向均通过 6/6，两段之间传送数为 0。路线离车行中心的最小距离分别为 4.74 和 4.70 米。 [旧版遇阻](walk-before-stopped.json) · [最终实走与 81 个接触点](walk-after.json)

9 组断面各查 9 个点，石板、路缘和沥青均命中相应的碰撞面。断面中心车面高程 16.440–17.864 米，T1 基座旁外侧地面 17.046–17.679 米。E216 / N−50 的室外地表与 77 号转身点高差 0.93 米。各值为游戏实测。Blender 4.3.2 分别重开独立源和组合城，复核同一组 81 个面接触点。 [改前地表、旧楼与相邻塔脚](baseline.json) · [高程](foot-and-road-height.json) · [制作源复开](blender-reopen.json)

最终资产的国浩 74–76 回归通过 25/25 项，实际走通 6/6 段。山城巷两套取送线路合计 12/12，包含取件、交付和回程。当前首班脚本 85/85，三单结算共 24 元。 [国浩回归](retained-guoco.json) · [山城巷取送](retained-shancheng-handoff.json) · [首班](retained-first-shift.json)

额外跑了早期 52 项首日入口。首轮试作和关闭 77 号图层的对照同为 50/52，失败均为首次交接结算和解锁条件。当前 85 项首班入口通过。 [早期脚本对照](early-day-one-comparison.json) · [原生后端记录](native-renderers.txt)

云端原始记录在 `/workspace/work/runtime/district-refresh/houci-77-2SHdvmUw`。当前地块和街道来源登记在 [现场记录](../field-registration.json)。图中还能看见邻地保留的旧试作体量，其单体位置与当前样貌另需逐地块核查。
