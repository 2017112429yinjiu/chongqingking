# 南区路 04、06、51 同层步带和桥面

南区路 176034685 与桥线 59146775 共用 E−201.3047／N−48.9926 节点。同车的 2023-05-15 街景在节点两边连续显示同一侧的灰色分格砖、浅路缘、金属栏和木色花树箱。后续三处机位显示双桶、禁行牌、两侧紫花隔带和轨道白罩下封闭车行段。相机原 Z 用来确认下降方向。2023-10-25 竣工斜照可交叉辨认步带、匝道分叉和轨道罩。 [地图和逐帧 SHA](field.json) · [竣工照片](https://epaper.cqrb.cn/cqrb/2023-10/26/004/cqrb20231026004.pdf)

西接坡与原 R24 桥面衔接。51 望江平台从同一座桥的钢筋混凝土边缘延伸，保留原车面、梁箱与墩帽。近侧回填按游戏实测局部下切，原有树根随测过的地面调高程。停步位置按街景落在约 54.5 米链程，步行到此回身。E/N 的局部边距、原城市高程与轨道罩净高仍有游戏拟合。外围楼宇与远景留在当前试作。04 两向骑行是封闭测试，正常使用按 OSM 单向。53 号旧楼沿用已验石梯。按所有权和碰撞范围裁去三张伸入步带的低基础片，及 57 张伸入原车轮轨迹的挡边相关面。复验原石梯的 129 个点。

用 Blender 4.3.2 在当前仓根重建独立源和增量，再由 Godot 4.6.3 导入：

```bash
site=work/scene_r24/district_refresh/street_groups/nanqu_04_06_51
assets=work/project/chongqing_godot_v05/assets/district_500
CQ_NANQU_PARENT=1 blender -b --factory-startup -t 2 --python-exit-code 1 --python work/scene_r24/district_500/compose.py
CQ_NANQU_SOURCE="$PWD/$site/nanqu-04-06-51.blend" blender -b work/scene_r24/district_500/city_and_outer.before_nanqu.local.blend -t 2 --python-exit-code 1 --python "$site/build.py" -- "$assets"
blender -b "$site/nanqu-04-06-51.blend" --python-exit-code 1 --python "$site/check_source.py"
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --nanqu-riverwalk
```

`walk.gd` 从正常开局检验步行到禁行牌前转身返回。`rides.gd` 检验西接坡和车行桥两段，04 默认重跑原轮迹。加 `--qa-nanqu-both-wheel-lines` 可同时运行原轮迹及江侧车轮轨迹。`sections.gd` 检验轮面、步带和梁腹净空。加 `--qa-without-nanqu-04-06-51` 可在同一入口载入父资产；用 `views.json` 读取固定机位。
