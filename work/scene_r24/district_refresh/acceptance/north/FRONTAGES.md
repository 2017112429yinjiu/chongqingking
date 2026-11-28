# 杏林中学校、凉亭子 43 南街和 46 公共巷

42 的杏林中学校门墩、三级石步、白绿扇形砖与矮篱按 2019 年学校公开入口制作。校名牌是自行排字，住宅入口保持另一个身份。东侧窄巷用深浅砌块和黑铁栏衔接。 [校门和东侧固定站](refined-field-register.json)

43 南横匾使用三眼交会得到的约 3.67 米长度。自排的「生活超市」配合深绿底、浅青绿小粒马赛克、灰砖廊洞与深色双门。店门规格为游戏化拟合。此前记录的南眼遮挡与原两跑踏面要一起检查。 [南街站位和原图差异](evidence/fixed-views.json)

46 的 137° 和 169° 为同一反算 EN 的不同朝向。两条固定眼用于核对下降混凝土面、沿阶店边和蓝折篷、灰砖栏、已登记白牌墩与树下座位。45 原测树根与旧屋壳仍交叠约 0.87 米。新增的遮荫树位使用已有许可植被，公开可见的树形和树下围合用作复核。 [45/46 原几何和控制](../../street_groups/liangtingzi_45_46/field.json)

    python3 work/scene_r24/district_refresh/acceptance/east/material_maps.py
    python3 work/scene_r24/district_refresh/acceptance/north/material_maps.py
    blender -b work/scene_r24/district_500/outer_district.blend -P work/scene_r24/district_refresh/acceptance/build.py -- north /absolute/build/output

牌面使用 Noto Sans CJK，SIL Open Font License 1.1。泥石、水泥与植物材质复用项目已许可来源。现场图仅用于观察。 [Noto CJK 许可证](https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE)

南街原眼中心像素首撞门台端，距 4.166 米，固定图中横匾右段仍被承托挡住。走到檐下能看见绿匾、门扇与马赛克。与原模型逐顶点核对，原后梯 22 个上表面一致。42 东眼可读校门和远处街缘，新栏在该机位仍比实景远。46 的 137°、169° 保留广场与旧楼的可见差距，现版能辨认下行面、石级、蓝檐、灰墙铁栏和近树。 [11 组固定矩阵与原生图](refinement/fixed-views.json) · [43 原眼命中](refinement/43-pixel-43-same-pixel.json) · [原踏面核验](refinement/43-unchanged-treads.json)
