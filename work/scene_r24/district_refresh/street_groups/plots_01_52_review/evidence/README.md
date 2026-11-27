# 01 和 52 固定机位与正常第一班实走

照片直接由 Godot 4.6.3 导出，Xvfb/Mesa llvmpipe OpenGL Compatibility，申请窗口 900×560，导出的原生视口为 900×506。两个过程均以软件截图参数关闭太阳阴影。比较源一端为 Git 47ab84257a64e9465af4edd37bdbd10f6eaa155e，另一端为 bb91ddda 几何和同批新托送脚本。六台相机逐项比对了实际 Godot View 矩阵、Projection 矩阵、视口和镜头输入，完全相等。每帧原始 PNG 和 SHA-256 都保留。

| 位置 | 实走及物理结果 | 折返点与旧轮廓 |
| --- | --- | --- |
| 01 | 从真实试玩街肩到时令菜摊 11.849 米，E 取件后走 2.865 米至干货柜台，以 E 交件并一次结算 6 元。同一身体沿原路回街肩 14.900 米，交互、支撑及返回检查12/12。 | 在原市场里面，距最近旧边 5.833 米。 |
| 52 低外侧 | 现有低街侧地表 14.154/14.169 米，两向6/6。登记低街的位置另存地面命中。 | 折回在旧壳外 6.652 米。 |
| 52 相邻高步道 | 06/51 对应独立步带 30.133/30.116 米，两向5/5，支撑每向39/39。 | 折回距旧壳 25.461 米。 |

01 原运行只有摊主动效，现场观察仅支持街侧坡阶。原来的游戏市场、201 和现有柜台保持。市场交接是此次加在正常探索里的虚构玩法。候选主厅首次交接点被现有柜台物件遮住，原失败保留。修正后使用柜台另一段现有台面，未改模型。

52 的低街、外坡、相邻高步道及旧屋分别登记。低外坡折返点不在旧屋内；不同 EN 行走的游戏标高不直接代表实景测绘高差。照片和地图支持开放步带和栏杆，植被与遮挡后面的屋址及入口继续待证。52 的独立源、GLB和原有空间保持。

[真实交接与回程](market-normal-E-handoff.json) · [52 断面及步行](plot52-two-levels.json) · [实际矩阵](matched-camera-matrices.json) · [相同轮廓坐标](old-outline-distances.json) · [PNG 指纹](png-comparisons.json)

沿用的玩法也在待发布脚本上复跑通过。[桥下茶摊](plot02-tea-regression.json) · [修车院](repair-court-regression.json) · [原市场到 201](market-201-regression.json) · [山城巷](shancheng-regression.json) · [首班](first-shift-regression.json)

- 01-street-approach [47ab8425 原生帧](01-street-approach-47ab8425.png) · [当前原生帧](01-street-approach-current.png)
- 01-hall-look-back [47ab8425 原生帧](01-hall-look-back-47ab8425.png) · [当前原生帧](01-hall-look-back-current.png)
- 52-low-street-approach [47ab8425 原生帧](52-low-street-approach-47ab8425.png) · [当前原生帧](52-low-street-approach-current.png)
- 52-low-exterior-look-back [47ab8425 原生帧](52-low-exterior-look-back-47ab8425.png) · [当前原生帧](52-low-exterior-look-back-current.png)
- 52-upper-walkway-approach [47ab8425 原生帧](52-upper-walkway-approach-47ab8425.png) · [当前原生帧](52-upper-walkway-approach-current.png)
- 52-upper-walkway-look-back [47ab8425 原生帧](52-upper-walkway-look-back-47ab8425.png) · [当前原生帧](52-upper-walkway-look-back-current.png)
