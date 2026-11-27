# 凉亭子 45、46 街边实走

Godot 4.6.3 普通 `first_shift.tscn`，先在公开面起步，抵发布标记后原地转身再回同一街边。两向不重新安置玩家。38 等已发布地块继续正常实例化。46 的实测腿沿图中中央坡带，分列短阶为可见形体，未拿坡带结果替代踏阶计数。

| 地块 | 去 / 回 m | 路点去 / 回 | 离旧楼边 / 旧游戏门槛 m | 同矩阵主视 | 同矩阵回望 | 玩家回望 |
| --- | ---: | --- | ---: | --- | --- | --- |
| 45 | 11.40 / 11.43 | 5/5、5/5 | 6.44 / 6.82 | [父](45-field-axis-before.png) · [今](45-field-axis-after.png) | [父](45-return-axis-before.png) · [今](45-return-axis-after.png) | [原生](45-player-turn.png) |
| 46 | 10.03 / 9.98 | 5/5、5/5 | 3.08 / 7.60 | [父](46-field-axis-before.png) · [今](46-field-axis-after.png) | [父](46-return-axis-before.png) · [今](46-return-axis-after.png) | [原生](46-player-turn.png) |

每处 6 个 Godot 支撑点、共 12/12 命中各自增量铺面。独立 Blender 4.3.2 及链接组合也各验 12 点。首班 85/85、市场去 201 5/5、修车 10/10。原生前后图 900×506，Compatibility／llvmpipe，相同游戏日照并关闭太阳阴影。现版可见局部石带、栏和台阶；邻院、树冠、住户门牌和代表标高仍需独立实景复核。 [无头走测](current-walk.json) · [原生走测](native-walk.json) · [旧门槛](old-threshold-distances.json) · [父版剖面](parent-sections.json) · [Blender](blender-support.json) · [首班](first-shift.json) · [市场](market-to-201.json) · [修车](repair-court.json)
