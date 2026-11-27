# 解放西路 25 号大阶门面

用 `work/scene_r24/district_500/play.sh --software -- --explore-500 --north-edge=25` 从近侧街边石铺进入。

2023-05-15 的 40° 近眼可辨宽石额、暗檐、门上竖格、稍内凹的深色玻璃和亮色拉手。同站70°和下一站80°分别核侧翼灰墙、阶脚铺带和黑色车缘栏。保留原已对位十一阶，按台阶最外支撑接街肩，门面用自制几何和仓库已有许可石纹。门后用途未知。门口只能在正常场景入行至顶平台。

[登记机位、观察和近似尺度](field.json) · [原始 07e02123 的固定图](../jiefang_public_24_25_26/evidence/25-field-axis-after.png) · [正常实走与定机位](evidence/README.md)

制作父组合使用 `CQ_JIEFANG_GATE25_PARENT=1 blender -b --factory-startup -P work/scene_r24/district_500/compose.py`，然后运行 `build.py -- <输出目录>`。独立和组合源均可用 `check_source.py` 核对。Godot 4.6.3 测量从台阶外石铺到门前原地转身，实跑 `walk.gd --explore-500 --north-edge=25`。相同矩阵对照另用 `--site-view-only --site-fixed-views=<views.json>`，父版带 `--qa-without-jiefang-gate25`。
