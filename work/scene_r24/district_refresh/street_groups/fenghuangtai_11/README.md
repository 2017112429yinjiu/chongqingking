# 11 号凤凰台路与下回水沟低街接头

旧住宅分别与凤凰台路 `1017606351` 和下回水沟 `59146751` 相交 10.587 米和 9.474 米。已登记的低侧中兴路 `176034697` 分别接两条线。2019 同址和较新的 2023 路边角度能看见灰铺、砖角、道路分出与远端的同一市场长面。2025-10-28 影像能分辨两路口与狭窄的沿街开敞范围。政府记录把共享裙房的车库出入口定位到凤凰台街邻接范围，照片暂未确认具体洞口。 [现场锚点与许可](field.json) · [B 组观察](../../evidence/B-market-sources.md)

本件处理公开道路与灰铺转折，在 500 米东框内截断支路。最早试件保持旧游戏上坡。2023-05-15 路口近角与 2019-06-29 巷内回拍都支持凤凰台侧巷出街后下落，能看见砖边、浅灰路缘与临街台阶。独立地表层据此下切，先与原中兴路口同高，再沿照片能确认的方向下坡。新地表及挡墙高程为游戏尺度，北侧下回水沟保留实测原地面。模型分别收两条道路和灰铺边，撤去冲突的旧住宅壳、梯与碰撞。灰铺终点为街边观察点。车库、私宅、巷后公共权属和实测工程断面留待定位。 [2023 路口近角](https://mapsv0.bdimg.com/?qt=pr3d&panoid=0902920012230515131744752AU&heading=93&pitch=0&fovy=78&width=900&height=560) · [2019 巷内向东](https://mapsv0.bdimg.com/?qt=pr3d&panoid=09029200121906291717399251L&heading=58&pitch=0&fovy=78&width=900&height=560)

从仓库根目录，用 Blender 4.3.2 从尚未加 11 号的组合城生成增量。

```sh
site=work/scene_r24/district_refresh/street_groups/fenghuangtai_11
assets=work/project/chongqing_godot_v05/assets/district_500
CQ_FENGHUANGTAI_11_PARENT=1 blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.before_fenghuangtai_11.local.blend --python-exit-code 1 --python "$site/build.py" -- "$assets"
blender -b "$site/fenghuangtai-11.blend" --python-exit-code 1 --python "$site/check_source.py"
blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --fenghuangtai-11
```

Godot 4.6.3 `ride.gd` 以 `--headless --fixed-fps 60` 跑两条支路去回，`walk.gd` 使用 `--explore-500 --fenghuangtai-11`。机位定义在 [机位表](views.json)，父版固定出图加 `--qa-without-fenghuangtai-11`。 [注册路点](road-stations.json)
