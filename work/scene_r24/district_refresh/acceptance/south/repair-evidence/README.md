# 00 修车铺柱间工作台

工作台移入既有柱间，保留原钢筋混凝土柱、绿脚包边、打气点和院口。旧台面与包边相交。新台面离同层最近包边 0.720 米，四腿及脚垫最近净距分别 1.597、1.861、0.793、1.241 米。台钳最近净距 1.148 米，中央柱间净宽约 3.690 米，与既有柜唇留 0.555 米。脚垫下缘与原水磨石可见面齐平。两件南片碰撞网格及碰撞替换表逐项比对一致。 [实际 GLB 量测](clearances.json)

工作台为自制木板与金属底架。台钳有底座、固定和滑动钳口、两根圆导杆、带螺纹的螺杆和横把。手工具分别为开口扳手、带铰轴的双柄钳和带筋握柄的平口螺丝刀。木作和不同金属表面使用仓库已有 CC0 扫描图，按面、边和圆周布 UV。 [Poly Haven 磨损木台](https://polyhaven.com/a/wood_table_worn) · [Poly Haven 磨损金属](https://polyhaven.com/a/rusty_painted_metal)

裸钢的浅灰色图由已登记的锈漆扫描图调出，保留表面点蚀和磨痕，法线及粗糙度沿用项目原图。重新生成后按南片的正常流程导出 Blender 和 GLB。 [色图重建脚本](../repair_texture.py) · [增量重建说明](../../README.md#重建增量)

[原工作台同眼](../refinement/after/00-tools-service-close.png) · [新工作台同眼](00-tools-service-close.png) · [玩家可达斜近景](00-tools-reachable-diagonal.png) · [机位矩阵、分辨率及 SHA](fixed-views.json)

## 正常玩法复核

从街上进场，使用 E 将玩家踏板车打到标准胎压，重复 E 不移动踏板车也不扣钱。另从打气点步行到斜视机位的脚点，再沿原线进后院、返回相同街口。 [真实输入、脚点支承与导入材质](walk.json) · [原验收入口复跑](normal-tyres.json) · [Blender 4.3.2 重开](blender-reopen.log)
