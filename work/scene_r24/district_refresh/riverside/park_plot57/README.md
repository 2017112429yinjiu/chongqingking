# 南纪门桥西 57 号旧占位复核

沿用 `district_refresh/plot_sources.py` 的旧旋转轮廓和 OSM way 734116601 配准。57 号原中心约 E−121.98/N−177.79，旧四层占位约 15.66 × 9.53 米。正射下可辨蓝区东侧至轨道桥西沿的绿带、收边和窄白构件。公园登记的三张地面照片可按桥柱、江岸和园路方向核对开敞关系。窄白构件用途和高度仍待核，施工坐标采用项目游戏高程。58、59、60、61 的图证及邻近道路、车行匝道与轨道桥分层各记在控制表。 [逐地块控制表](field-controls.json) · [桥西原正射](https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/19/217060/417337) · [相邻正射](https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/19/217060/417338) · [公园边界](https://www.openstreetmap.org/way/1499726225) · [10 号线桥段](https://www.openstreetmap.org/way/878019566)

正常场景回读前版有旧 `COL_Outer500_Frame_57`、旧室内地板、门窗、旧空调与陈设，旧用途登记为 `washroom`。本批按旧有逐面哈希撤去其建筑、共用挡墙里的附属梯段、旧洗手间及相应共用碰撞。沿恢复地带补灰石园路、硬地压边和落地植被，再用游戏坡面接回蓝区。保留独立登记的 62 号公厕，图证及运行记录仍单列。 [62 号](../pavilion62/FIELD.md)

## 三台原生机位的断面复核

使用 `52031ffe` 的 `sand-return-look.png`、`street-edge-return.png`、`blue-after.png` 机位和镜头参数。原画里的深黑矩形多处命中现有 `COL_WestPlayground_PerimeterSupport` 石墙贴图面。浅砂回望和街边回望也各有像素命中旧 57 外围护或门窗，已随旧住宅撤除。蓝场后缘 (712,229)、(719,228)、(724,229) 原来均穿空，两墙间实测缺口约 0.40 米宽，使用独立六面石材体封端。改后同样三条光线命中实体，Godot 另在 −5.62、−5.30、−5.00、−4.71、−4.41 米五个高程复查碰撞。

再次复查街边回望，在 (749,371) 确认还有一小段旧挡墙背面伸进园门缓坡。已沿两段铺地的实测高程改成低石边，原有高差的挡墙暗侧保留。用 `entry_joint_walk.gd` 可直接复验旧碰撞与新接头，并从同一长滨路步行带穿过接头后原路返回。 [三台机位返图和复测](evidence/street-entry-recheck)

## 重建和走测

在 Blender 4.3.2 打开 `work/scene_r24/district_500/outer_district.blend` 后执行同目录 `build.py`。它按逐面归属和当前已发布供体输出独立源、增量 GLB 和场景清单。可用 `check_source.py` 重开源及组合城，`check_registered_pixels.py` 在组合城复做三台机位的像素射线。摄影资料仅用于观察，铺装使用工程已有许可的原材质和独立几何。

在正常 Godot 4.6.3 `first_shift.tscn` 用 `--explore-500 --west-court --west-street-court` 从长滨路步行带开局，以本目录 `walk.gd` 走过原公园接头、蓝区、复原坡道到 57 号再原路回街。脚本测六处三列横断面、五处封端碰撞和 58–61 的试作场景层。加 `--qa-without-park-plot57` 保留改前场景和阻断原始输出。云端截图用 Mesa llvmpipe Compatibility 软件渲染。 [原生图、测量与回归](evidence)
