# 中兴路 22 号花池周边

用 `work/scene_r24/district_500/play.sh --software -- --explore-500 --north-edge=22` 进入。沿西侧朝南，绕过前缘到东侧，停在仍属公共铺地的位置再转身。

2019 年同址四眼均见抬高的圆端园池、长直边、浅灰公共分缝铺装、草地与少量灌木。近眼可见两株树的三脚木撑。登记机位、朝向、旧池标高与拟合边界在 [field.json](field.json)。素材复用项目已有许可的石面、混凝土和树，叶片、木撑、石材及铺地细缝为独立建模。照片用于观察。

旧版 38e7183f 盖石设计顶高 35.933m。可独立识别旧外地表的35处中，E114.292/N87.923 盖石估算埋下0.079m，E118.329/N83.880 露出1.483m。另13处在旧壳及附属地表混叠下没有获得同类命中。新铺地和池身均顺游戏内部承托关系制作，形状及坡度为近似，四眼不提供测绘标高。保留后侧的旧户界。

用 Blender 4.3.2 打开 `work/scene_r24/district_500/outer_district.blend`，执行本目录 `build.py -- <输出目录>`。GLB 和 JSON 位于 `assets/district_500`。完成后 `compose.py` 可链接组合。设置 `CQ_ZHONGXING22_PARENT=1` 复开父组合。以 `check_source.py` 复测48个边段。Godot 4.6.3 的 `walk.gd` 用正常场景测碰撞、缝隙与三侧实走，原生固定视角参数 `--site-view-only --site-fixed-views=<views.json>`，父版另外带 `--qa-without-zhongxing22-finish`。

[同机位影像和物理实走](evidence/README.md)
