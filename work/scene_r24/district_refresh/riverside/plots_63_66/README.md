# 长滨路东接 · 63–66 号弯道与公园侧

以 64fe77f1 为父版。按山城巷控制点 OSM 734116601 登记四栋原试作足迹，逐点对照百度原始不同机位、龙帆完工斜照、规资局反向图及两期正射。近邻 2020 年街景仍有工程期车辆和临时隔挡，2023 年西侧机位也有围挡。完工照片确认道路用途和可见的层位关系，现场绝对标高、红面配方和地下空间用途仍待核。图像只供观察。 [足迹、道路、照片机位、原始链接与指纹](field-controls.json)

| 原试作 | 判读 | 本批 |
|---|---|---|
| 63 | 1256839997 与 1375242615 的上层弯道越过旧足迹，反向可见梁腹、圆墩、车库连续立面与地面车道。 | 撤五层假楼及附属，保留已建匝道，在车库外侧恢复灰色铺带与挡土收边。 |
| 64 | 59146737 和低匝道 1324001436 穿原足迹。完工斜照里红面有车行箭头，公园侧另有浅边和树带。 | 撤四层假楼，区分车行红铺带、地面车道和园侧灰铺地。 |
| 65 | 1375242615 的弯道覆盖旧楼位。近邻与反向实景支持独立的梁腹、低处挡土和上层双线。地铁隧道 1151519554 只是下层平面重叠。 | 撤五层试作体量，在已建匝道内侧补可读弯梁和分隔边。车库内场和隧道留待专项资料。 |
| 66 | 地面 1256859184 与两组 1 层匝道跨旧足迹。对向图从道路两侧看到独立的栏边与桥下空间，完工图确认平行沿街铺带。 | 撤四层假楼，车道继续服务车辆。实走沿长滨路同侧公园边完成，旧楼中心单独做层位和碰撞复查。 |

工程层位控制沿现有场景和开放道路轴制作。新建的内弯段为局部外观及碰撞，出图范围止于本批，路宽、支挡高度、铺装缝与盖板间距按游戏地表拟合。63/65 下层由车库外侧铺带接入，64/66 从 62 公厕东侧的人行带沿公园边接入。在两组照片中可见的障碍边和两个交通层分别装配。运行用石面、沥青、草地和旧化混凝土复用仓内贴图或同源着色纹理。 [Blender 4.3.2 重开与 Godot 走测](evidence) · [资产来源许可](../../../../project/chongqing_godot_v05/assets/material_provenance.json)

## 重建与试玩

    blender -b work/scene_r24/district_500/outer_district.blend --python-exit-code 1 -P work/scene_r24/district_refresh/riverside/plots_63_66/build.py
    blender -b --python-exit-code 1 -P work/scene_r24/district_500/compose.py
    godot --headless --path work/project/chongqing_godot_v05 --import
    work/scene_r24/district_500/play.sh --software -- --explore-500 --changbin-bend
    work/scene_r24/district_500/play.sh --software -- --explore-500 --changbin-park-edge

walk.gd 从正常 first_shift.tscn 启动，用两个试玩入口分别连续步行去回。指定新 CQ_QA_DIR，Godot 4.6.3 用 --fixed-fps 60 --script，用户参数加 --day-one-test --qa-still-frames --explore-500 和上述入口参数。切换 --qa-without-changbin-bend 可从同一站位复查父版。 check_source.py 可验证独立源与组合城。
