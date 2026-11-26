# 0 号修车院上层开口登记

`courtyard.upper()` 在临街与后侧各造七个上层窗孔。旧布局中的 `facade_work.windows` 始于 0，原专用木窗分支未增加计数。现生成器每造一个窗孔就计数，随附布局同步为 14。原碰撞、窗玻璃和窗墙模型沿用已交付资产。无障碍和私人住宅的现场开口仍以同址证据为准。

Godot 4.6.3 用 `check_openings.gd` 从 `first_shift.tscn` 检查结构洞口。马蹄街批原测和关马蹄街的控制组都在 0 号记录 `[0,14,0]`，两份报告字节相同，退出码 2。更正后，退出码 0；其余逐地块计数完全相同。共有 1,856 个上层开口，各有窗台与过梁。另有 196 个街层登记开口，196 个通过。[初测](before.json) · [关闭新街组对照](matix-disabled.json) · [更正后](after.json)

复测使用独立 `CQ_QA_DIR` 与 `--headless --fixed-fps 60`，脚本从 `work/scene_r24/outer_neighborhood/check_openings.gd` 启动，用户参数为 `--day-one-test --explore-500 --repair-court`。

修车专项仍为 10/10，踏板车充气到 2.4，前门进院及绕回原街累计 55.83 米。[服务复测](service.json)
