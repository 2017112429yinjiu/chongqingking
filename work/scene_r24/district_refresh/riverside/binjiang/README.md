# 滨江壹号与解放西路 70–73 号

| 旧地块 | 位置与图像证据 | 进入正常场景的范围 |
|---|---|---|
| 70 | 旧足迹 116.595 平方米落在滨江壹号 `1128648941` 内。2019 年南区路背面照片与 2020 年滨江路照片分别见树带后的塔脚、浅色竖分格和深窗。龙帆完工斜照核对了塔身和桥路关系。 | 一座浅色塔与同一裙房。沿解放西路人行带进入北侧公开门前，门槛后以可见的窗门收口。 |
| 71 | 旧足迹与同一开放轮廓只交叠 35.44 平方米。滨江路照片显示连续裙房，北面老照片确认两楼之间有前缘和通道。 | 同一裙房的外侧柱网、夹层开口与沿边灰石铺地。走到沿边可证的公开外部位置。 |
| 72 | 旧足迹小角擦到相邻楼 `704006726` 约 6.82 平方米。2019 年北侧可见两楼间入口与铺地。2020 年南侧相反视角看到车库和桥底的遮挡。 | 还原两楼之间的通道、铺地和临街前缘，路线止于可证的外部平台。 |
| 73 | 旧足迹与现存开放楼轮廓没有交叠。2019 与 2023 年对向街景都出现红褐色弧形裙房、连续横窗与路肩。滨江路一侧可见深车库开孔。 | 公共弧边铺地和相邻楼独立外立面。弧形进深与开孔按街景近似，楼门后收口。 |

© OpenStreetMap contributors，ODbL 1.0。站点沿用 `734116601` 控制点。2024 与 2025 两期正射的圆形亮面相对道路和楼足偏移约 25 米，作为高处表面与遮挡的观察，街道弧线以地面照片为准。`1128648941` 标 40 层，公开酒店资料涉及 41 楼。`704006726` 标 29 层。楼层高度、内墙、车库分格及背面遮挡段使用试作拟合，照片用作观察。 [开放轮廓、街景元数据和逐地块坐标](site.json) · [滨江壹号朝向登记](../south_edge/tower-70-orientation.json) · [2022 重庆日报](https://app.cqrb.cn/economic/2022-01-09/1181630.html) · [龙帆完工斜照](https://epaper.cqrb.cn/cqrb/2023-10/26/004/cqrb20231026004.pdf) · [2024 正射](https://www.arcgis.com/home/item.html?id=24efa4fabd92463d805bfd82ef8f8b32) · [2025 正射](https://www.arcgis.com/home/item.html?id=b4c5c1b59c4141c5b503335b5baa2df4)

## 制作与试玩

增量源可用 Blender 4.3.2 独立重开，旧共有网格的已许可材质仍链接先前依赖。新实体复用现有许可的砂色石、砖、混凝土与石板纹理，贴面和窗洞使用独立 UV。Godot 4.6.3 按正常 `first_shift.tscn` 叠加这组地块。历史 `R24_East_Block_0` 的五个面组仍在原资产，当前试玩将它们隐藏，避免把旧外观叠在红褐色弧形裙房上。[逐像素定位和前后返图](evidence)

```sh
CQ_BINJIANG_PARENT=1 blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.before_binjiang.local.blend --python-exit-code 1 --python work/scene_r24/district_refresh/riverside/binjiang/build.py
blender -b --python-exit-code 1 --python work/scene_r24/district_500/compose.py
blender -b work/scene_r24/district_500/city_and_outer.local.blend --python-exit-code 1 --python work/scene_r24/district_refresh/riverside/binjiang/check_source.py
godot --headless --path work/project/chongqing_godot_v05 --import
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --binjiang-plot=72
```

`--binjiang-plot=70` 至 `73` 可切换公共街边入口。用 `walk.gd`、全新 `CQ_QA_DIR` 和 `--fixed-fps 60` 运行往返。`--qa-without-binjiang` 可重现旧几何。原生前后图采用固定眼位、指向和视野，关闭太阳阴影以沿用父版拍摄条件。

## 40f77024 后的同址精修

72 号以 2019 年南区路正面为准，重排入口斑马纹、街口白边、灰砖人行带、两侧低缘石与浅层排水。退入小门房并把原有树根纳入带石边的种植槽。70、71 号在塔裙门前压低门槛、后退玻璃并细分门梃，补门前种植槽。73 号以 2019 年北侧和 2020 年长滨路反侧为准，分别做凸弧玻璃带及有斜升层板的厚框开孔。照片用于外形和层位判读，坡度、精确尺寸和不可见内部为有限试作。 [三张同址资料、观察与指纹](finish/field.json) · [本轮原生前后与往返](finish/README.md)

重开与导出沿用上面的命令。使用 `finish_views.gd -- --day-one-test --qa-still-frames --qa-no-sun-shadows --explore-500 --binjiang-plot=72` 导出登记人眼高视图并复走入口。追加 `--site-view-only` 可单独复拍机位。
