# 南纪门轨道桥西侧蓝面平台

2023 年市政府照片与原始配准航片都可辨桥西、车道和园路之间的蓝色场地。按 OSM 公园界和原地图坐标定位，独立设计 203.52 平方米平台，内铺 142.70 平方米蓝面。平台及两条接头都在开放公园界内，最近距 57 号原轮廓 6.90 米。本次地表尺度、铺面、栏杆和楼梯用作游戏设计。后续公园登记 1526167225863589888 确认相邻两区为滑梯活动场地，北向航片给出两区和绿化楔的近似轮廓，见 [桥西分区试作](../west_ramp/README.md)。[西侧观察与地面采样](../south_edge/west-court-registration.json) · [滨江公园 OSM](https://www.openstreetmap.org/way/1499726225) · [同址实拍](https://www.cq.gov.cn/sy/lb/202310/t20231026_12473668.html)

用原地面三角形裁出平台与接头，周围山坡的形状和原园路继续沿用。平台实测标高 −5.83 米，东北角从原坡切入，坡外侧由挡边落到原地。东侧从园路接无级坡道，西侧接 18 级石梯，两路可穿场往返。朝下坡的边界有独立护栏，两处通道净宽保留。首轮回望照发现蓝面上原有的灯杆。按回望机位射线命中的源网格锁定灯杆、灯头及发光罩 18 个面，整件移到园路旁原地面，保留同一街具网格的其他构件。材质复用项目原有 Poly Haven CC0 扫描，Dimitrios Savva 与 Rico Cilliers 的磨损混凝土用于蓝面与灰色铺地，Charlotte Baglioni 的石墙用于挡边，Amal Kumar 的旧漆钢用于护栏。实景照片仅供观察。[混凝土](https://polyhaven.com/a/concrete_floor_worn_001) · [石墙](https://polyhaven.com/a/stone_wall_05) · [旧漆钢](https://polyhaven.com/a/rusty_painted_metal)

## 重建与试玩

使用 Blender 4.3.2 以 `outer_district.blend` 为底稿运行 `build.py`，需要已交付的 `matix_streets.blend` 作街具供体。脚本输出独立源、GLB 与运行登记。组装脚本将两个替换地表和平台源链接到组合城。用 Godot 4.6.3 重新导入，GLB 的纹理嵌在资产中。正常 `first_shift.tscn` 在生成碰撞之前接入平台。

```bash
blender -b work/scene_r24/district_500/outer_district.blend --python-exit-code 8 \
  -P work/scene_r24/district_refresh/riverside/west_court/build.py -- /tmp/west-court-export
GODOT_BIN=/path/to/godot bash work/scene_r24/district_500/play.sh --software -- --explore-500 --west-court
```

将 `CQ_QA_DIR` 设为各自独立的输出目录。`verify.gd` 测平台、踏步和坡道，实走三组往返。`ride.gd` 延用全区常规骑行脚本验证东坡道，包含停稳和下车。两者使用 `--headless --fixed-fps 60` 及用户参数 `--day-one-test --explore-500 --riverside`。`views.gd` 在图形模式用同视点显示改前和新版地面。摄像机从同一园路位置取样，灯杆修正前后的改前控制图字节相同。最终四张原生图用 Xvfb 与 Mesa llvmpipe 渲染，日志记录两条退出时纹理告警。

[园路看台同机位改前](views/from_park_before.png) · [改后](views/from_park_after.png) · [平台回望](views/terrace_reverse.png) · [相机与渲染器](views/cameras.json)

实测平台 108 个支承点、坡道 18 个横向采样点及西梯 18 级均通过，六个步行方向均无停滞接触。东坡道双向骑行可停稳下车。滨江旧线路 14/14，整区 7 处断面及 20 段步行和骑行通过，首班 85/85，送单 6/6，修车 10/10。[实测汇总](checks.json)
