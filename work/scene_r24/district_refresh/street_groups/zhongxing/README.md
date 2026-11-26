# 中兴路东北接坡

在登记街线 `176034707` 上找到两处原地面控制器接触。两点落在原山脊挡土面 7850、7848，面级误差 0.10、0.13 毫米。开口沿同一挡墙量 10.00 米，保留两侧现有坡地与墙段。通行范围使用游戏的既有坡面，路边楼体与台地按下回水沟市场的同址证据独立制作。[最初接触取样](../run/northeast-wall.json) · [开放道路](https://www.openstreetmap.org/way/176034707)

以 Blender 4.3.2 打开上级 `matix/matix_streets.blend`，执行 `cut_wall.py`。脚本参数 `-- <输出目录>`，输出可重开的独立挡土源、GLB、接坡清单。源几何逐件验算原碰撞面后才裁切。将 BLEND 放在本目录，GLB 和 JSON 放入 `assets/district_500/`。`compose.py` 链接独立挡土源，常规 `first_shift.tscn` 在马蹄街共享网格后加载这项替换。

Godot 4.6.3 使用 `district_refresh/riverside/survey.gd`、独立 `CQ_QA_DIR`、`--fixed-fps 60` 及用户参数 `--day-one-test --explore-500 --riverside` 复测。另以同一街线的 8 米采样复跑，检查原较稀测试路线和靠中心线的较细走法。

```bash
blender -b work/scene_r24/district_refresh/street_groups/matix/matix_streets.blend --python-exit-code 8 -P work/scene_r24/district_refresh/street_groups/zhongxing/cut_wall.py -- /tmp/zhongxing-export
CQ_QA_DIR=/tmp/zhongxing-qa godot --headless --fixed-fps 60 --path work/project/chongqing_godot_v05 --script "$PWD/work/scene_r24/district_refresh/street_groups/zhongxing/walk.gd" -- --day-one-test --explore-500 --riverside
```

建立独立的输出目录后执行。七条常规路线的 14 个方向全部走通。中兴路原采样两向通过 9/9 个路点，加密两向通过 27/27 个路点，四向停滞接触均为 0。改前反向 4/9 后撞墙的记录与往返复测一起留存。[路线检查](../../riverside/south_edge/checks.json)

[上坡改前](views/uphill_before.png) · [同机位改后](views/uphill_after.png) · [下坡回望](views/downhill_after.png) · [摄影机坐标](views/cameras.json)
