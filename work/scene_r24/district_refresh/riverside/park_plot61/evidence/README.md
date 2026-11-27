# 61 号登记街景与引擎复测

游戏前后使用同一个 D 机。原生子视口恰为 900 × 560，垂直视野 80°，方位 130°，眼高为游戏街面上 2.32 米。两个视图均保存其真实像素，可逐点对到相同位置。实景原图只在云端临时参考目录。 [改前](registered-D-before.png) · [改后](registered-D-after.png) · [四束原像素、世界射线和扰动](ray_comparison.json) · [游戏像素对照](native-sky-pixels.json)

玩家由同一个滨江路公园侧步行带向南走，经树带西侧园路接到江侧，原地转身回同一出发段。新版去程 21.722 米、回程 21.880 米，各通过 6/6 路点，21 处地面探针均有支持。父版这条外围线也可走通。撤楼的判据是上层实心体量遮住了原景亮天空，旧屋中心碰撞柱在改后仅命中地面。 [新版实走](round-trip.json) · [父版实走](round-trip-parent.json) · [园路回望](player-look-back.png)

Blender 4.3.2 在独立源和组合城重复表面探针。组合城里的四个公厕网格依旧各自链接到 `pavilion62.blend`。Godot 4.6.3 复测公厕、修车及第一班送单。原生帧以 Mesa llvmpipe Compatibility 输出，两条已有 GL 纹理退出告警仍见于原始记录，退出码为 0。 [Blender 重开](blender-reopen.json) · [公厕](regression-62.json) · [修车](regression-repair.json) · [首班](regression-first-shift.txt)
