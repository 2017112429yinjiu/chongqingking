# 仁爱堂荒野花园 50 号公共遗址外缘

50 号原中心 E−214.48／N76.52 米。道合竣工鸟瞰显示该片段有折线石残墙、浅色公开步道和条石座凳。两张设计图的配准把旧中心读到约 `(168, 165)`，位于西北至东南走向的遗址廊。图间 RMS 1.51 米，独立留出圆井为 7.74 米，源道至 OSM RMS 2.08 米。以此判别片段，与实景对照确定可见设施。墙高、座位摆法和局部步面按游戏实测地形制作。外侧栈道线作公开接头定位，未把 2025 玻璃栏改修或相邻地块视为本次还原。 [定位和素材](field.json) · [两图拟合](../../evidence/E-donehome-registration.json) · [竣工实拍](https://mooool.com/wilderness-garden-theater-by-donehome.html)

撤下旧住宅框、台阶和所属碰撞。保留外部现有地形，增量由灰石步路、邻地形的低残墙和四块条石坐凳组成。公开步路从 OSM 734116600 接头定位处到遗址外观察点。室内、遗址真实基线、北缘住户和外栈道的其他段继续独立核对。画面只用项目既有纹理。独立 Blender 源的材质带这三张纹理，游戏 GLB 用同项目的现成纹理资源，避免重新抽出三套导入纹理。

用 Blender 4.3.2 在仓库根目录重建，Godot 4.6.3 打开正常探索入口。

```sh
site=work/scene_r24/district_refresh/street_groups/wilderness_50
assets=work/project/chongqing_godot_v05/assets/district_500
CQ_WILDERNESS_50_PARENT=1 blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.before_wilderness_50.local.blend --python-exit-code 1 --python "$site/build.py" -- "$assets"
blender -b "$site/wilderness-50.blend" --python-exit-code 1 --python "$site/check_source.py"
blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --wilderness-50
```

同矩阵采用 [视点](views.json)，沿 `walk.gd` 实际走至端点原地转身。父版加入 `--qa-without-wilderness-50` 后仍从同一公开接头起步。 [原生前后图、路线记录](evidence/README.md)
