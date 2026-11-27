# 厚慈街 14、16 号接头与 18 号候车步带

| 地块 | 已确定的位置 | 场景改动与开放范围 |
| --- | --- | --- |
| 14 | `1306489251` 穿旧轮廓 1.465 米。2023 两向街景确定车路走向和窄边，2025-10-28 影像确定浅灰弯段与内侧窄带。 | 撤旧独栋及附属。在实测地表上接回窄弯，做混凝土车面和石路缘。公共步行沿西侧登记步带至可见端点。 |
| 16 | `176968735` 穿旧轮廓 9.834 米，低层沿 `1189963552`。2023 同址确认行车朝向、外弯砖缘和浅色铺边。 | 撤旧独栋及附属。用实测游戏原桥面和坡脚接头确定新的匝道纵断面，做短梁式承托、闭合混凝土底面和浅砖路缘，保留低侧游戏地面。承托与高度是游戏实作，现场柱位及断面尺寸待核。 |
| 18 | `734116598` 熊猫古玩城候车步带可见桥侧。上层仍由 `59146775` 原车面承托。 | 新增候车步带上的正常玩家实走，原地回到出发点。单独保留上层顺行和封闭逆向车测。 |

照片与航片供定位和观察。车面、路缘与步带使用已许可的混凝土、石、砖与沥青贴纹。14 号围挡内开口和16 号暗侧步行的公共权属待核。两处旧房足迹改为道路或路缘。公共脚路沿实景可见侧走至观测点。 [注册源、坐标及判断](field.json) · [厚慈街道路](https://www.openstreetmap.org/way/1306489251) · [匝道](https://www.openstreetmap.org/way/176968735) · [低侧道路](https://www.openstreetmap.org/way/1189963552) · [公共步带](https://www.openstreetmap.org/way/734116598)

在仓库根目录，使用固定版 Blender 4.3.2 重建。

```sh
site=work/scene_r24/district_refresh/street_groups/houci_14_16
assets=work/project/chongqing_godot_v05/assets/district_500
CQ_HOUCI_14_16_PARENT=1 blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.before_houci_14_16.local.blend --python-exit-code 1 --python "$site/build.py" -- "$assets"
blender -b "$site/houci-14-16.blend" --python-exit-code 1 --python "$site/check_source.py"
blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.local.blend --python-exit-code 1 --python "$site/check_source.py"
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --zhongxing-public=18
```

Godot 4.6.3 `walk_public.gd` 用正常 `first_shift.tscn`，引擎参数 `--headless --fixed-fps 60`，场景参数 `--day-one-test --qa-still-frames --explore-500 --zhongxing-public=14`，将 `14` 换成 `16` 或 `18` 复走各线。`ride_connectors.gd` 使用相同固定步长和首班脚本宿主，16 的逆向为封闭验收。每条巡检使用独立 `CQ_QA_DIR`。固定返图由原生软件渲染运行 `../zhongxing_bridge_18_21/fixed_views.gd`，以 `--a2-views` 指向本目录 [机位表](views.json)，加 `--qa-without-houci-14-16` 复现父版。 [走测及返图](evidence/README.md)
