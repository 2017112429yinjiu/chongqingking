# 正常场景仍加载的试作框架

Godot 4.6.3，正常 `first_shift.tscn`，500 米城区全部增量开启。登记簿 78 个数字地块，71 个属于曾有可实例化布局，另有 7 处飞越、撤回或未实例化保留点。实测有 **20 个可见旧独立框架**，50 个布局条目查不到独立框架或其旧共享壳命中。02 号已没有旧屋框和共享壳命中，茶摊保留两个院落对象。原 200 米 14 条楼栋、道路、入口继续用原标识。[逐号最新状态、地图、同址图和走线](plots-current.tsv) · [载入节点与运行资产指纹](runtime.json) · [全区原台账](../plots.tsv)

保留旧独立框架的编号为 00、01、12、22、26、30、31、34、35、40、41、42、43、45、46、49、52、53、54、56。公开改造程度和仍待定位的墙脚、私门、地表遮蔽均逐条列出。45 的树池位置与旧屋公共侧冲突、56 的正门阻断属于两项不同的待核问题；各用独立地面与走线证据。

以 `district_500/build.py` 的原始逐面归属建立 Blender 参考，再在正常 Godot 初始化后的可见对象和共享碰撞壳网格中检查。共享外壳栏统计正匹配的旧三角面；已经重分割或改变的面会使该值偏低。判断是否加载独立试作屋使用可见 `COL_Outer500_Frame_XX`，并逐号保留窗框、地板、院落等邻属对象的名称。不能据目前测试推断现实建筑的产权或用途。

```sh
CQ_OUTER_PLOT_OWNERSHIP=/tmp/cq-shell-ownership.json blender -b -P work/scene_r24/district_500/build.py
blender -b work/scene_r24/district_500/outer_district.blend \
  -P work/scene_r24/district_refresh/evidence/current-shells/reference.py -- /tmp/cq-shell-ownership.json /tmp/cq-shell-reference.json
CQ_QA_DIR=/tmp/cq-shell-audit godot --headless --fixed-fps 60 --path work/project/chongqing_godot_v05 \
  --script "$PWD/work/scene_r24/district_refresh/evidence/current-shells/inspect.gd" -- \
  --day-one-test --legacy-shell-reference=/tmp/cq-shell-reference.json
python3 work/scene_r24/district_refresh/evidence/current-shells/ledger.py /tmp/cq-shell-audit/legacy-shells.json /tmp/plots-current.tsv
```
