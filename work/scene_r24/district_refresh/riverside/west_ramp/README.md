# 南纪门桥西园路、坡道与滑梯区

北向正射瓦片经项目现用的 OSM way 734116601 控制投影，以北侧临江车道和南侧园路核对。蓝面为不规则梯形，浅砂色铺地在西北，南侧之间有绿化楔。瓦片上主滑梯约 E−148.06/N−183.71，西北双滑道约 E−170.24/N−169.48，二者相距 26.34 米。用户提供的主滑梯与浅砂地中心相距约 25 米，两次读图均支持两处独立场地。公园登记 1526167225863589888 确认滑梯类活动，其登记点离主滑梯影像中心约 15 米。该点作为场地登记引用。邻近其他照片能辨认独立球场。完整控制、照片逐张观察和文件指纹存于 [playground-controls.json](playground-controls.json)。[公园登记](https://park-tool.pre.paramst.cn/api/tourApp/TourTbParkActivityZone/selectById?id=1526167225863589888) · [北向正射](https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/19/217060/417337) · [OSM 公园界](https://www.openstreetmap.org/way/1499726225)

登记同址照片可见细粒蓝面、蓝色相连弧壳、端面钢网与金属滑槽、相邻的三色转盘、白色收边和嵌双滑道的浅砂及粉灰缓坡。独立制作蓝面、主滑梯、三色转盘与浅砂双槽，在两区之间铺接步道，绿化楔放置贴地乔灌。蓝面外轮廓、两组滑梯坐标和绿化楔轮廓为航片近似。主滑梯、转盘、双槽、园路接头和铺地高差用游戏尺度拟合，器械为静态场景资产。铺面与几何独立制作，合用旧工程已有许可的石材、混凝土与植被。观察照片与瓦片未嵌入工程。 [主滑梯及转盘](https://park-tool.pre.paramst.cn/api/resourceApp/resource/park-register/69d63f82519c6ef3b6ff71dd74172b49%282%29.jpg) · [主滑梯背面](https://park-tool.pre.paramst.cn/api/resourceApp/resource/park-register/cd480498bd067284588d8d8f8dc7758f%281%29.jpg) · [浅砂场地](https://park-tool.pre.paramst.cn/api/resourceApp/resource/park-register/cabc07c821a549ff3e69c36926786fd7%281%29.jpg)

固定回望机位旧原面命中 242、255、257。按原面调整连续 53 个墙段面灰石饰面，原东坡 27 个可走面加灰石旗板和端头、坡中接缝，坡肩铺叶土并植入六处小灌丛。西北接通处移除被新连续地面盖住的旧内墙片。东坡、整座旧平台和西梯的承面顶点保持原位。保留初版单场地源、导出和运行图，供复盘两区定位错误。

## 重建与实走

用 Blender 4.3.2 打开 `work/scene_r24/district_500/outer_district.blend`，执行 `build.py`。它引用旧西平台供体，另存独立 `west-ramp.blend` 及增量 GLB。Godot 4.6.3 正常加载 `first_shift.tscn`。以 `--explore-500 --west-court` 从东侧上层园路开局。运行本目录 `walk.gd` 并加 `--west-sand-continuous`，使用同一玩家从正常开局过东坡、蓝面和连接步道进入西北浅砂区，再原路返回。两段之间零重置。以 `--qa-without-west-ramp --site-view-only` 采集同机位改前图。用相邻 `west_court/verify.gd` 和 `west_court/ride.gd` 分别复测三条步行路线、承面和东西方向骑行。实测与原生画面见 [evidence](evidence)。

## 长滨路步行接头

原园内起点 E−123.20/N−201.93 离 OSM 59146737 中线 39.404 米，园路线保留单独验收。新街边起点 E−158.97/N−159.07 对应同一条登记道路，离中线 6.470 米，在航片近读的公园侧道路边缘外约 1.046 米。以局部铺面和矮缘石标清步行侧，在码头一侧用独立接道接到浅砂区，未设横穿车道的引导。航片用于定道路方向和公园铺地相接范围，路缘高度、开口弧段、接坡坡度属游戏拟合。小段街面在 55 号旧占位前收口。道路连续线和 55 号冲突仍按逐地块记录保留。

用正常 `first_shift.tscn` 开局参数 `--explore-500 --west-court --west-street-court` 进入长滨路公园侧步行带。同组 `walk.gd` 实走经开口到西北浅砂区并回原街点。证据保留穿越接头的地面碰撞命中、全程采样与相对道路中线最近距离。
