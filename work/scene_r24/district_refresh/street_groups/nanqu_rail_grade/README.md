# 04 南纪门轨道罩与南区路纵断面

## 配准与层位

六站属 2023 年 5 月 15 日的同一车载片段。第一站位于南区路接线 `176034685`，其余接续 `59146775` 的露天层。末站的平面投影距地下 `1256840005` 很近。全景里的天空、桥面花带和连续车辆方向，以及同设备片段的相邻顺序，确定该站仍在 `59146775`。另一天的长滨路四站距 `59146737` 为 0.36–1.45 米，上方看到独立钢箱梁与车行匝道，路旁车库曾在施工。两组图只用于比对观察。

十站元数据均登记 `DeviceHeight=2.32`，供应方编号均为 9。重新从 `X,Y` 完成百度米制坐标到 BD‑09、GCJ‑02、WGS84 和项目 `734116601` 的换算，保留原坐标及旧游戏机位。两组供方 Z 的原始差为 32.54–33.78 米。设备高相同，仍可能存在日期间偏差。用这组差值做相对控制。公开工程环评的参考横断面在长滨路邻地给出 186 米、轨顶 230 米，在南区路居民参考点给出 220 米、轨顶 227 米。两处均为邻地和轨顶，游戏场景使用自身局部 ENU。另将轨道与公路逐点纵断面取样。[轨道环评图 3‑2 和敏感点表](https://sthjj.cq.gov.cn/zwgk_249/zfxxgkzl/fdzdgknr/hjyxpj/pzgcxx/sljsxmhpxxgg/201901/P020220914562460734710.pdf) · [工程导则附录 D](https://zfcxjw.cq.gov.cn/zwgk_166/zfxxgkmls/zcwj/qtwj/202507/W020250709635119442632.pdf) · [雷家坡立交批复](https://www.cqyz.gov.cn/bm_229/qfzggw/zwgk_97157/jczwgk/ywjyxxgk/pzjgxx/pfwj/fgwbmpzxx/202105/t20210510_9260859.html)

上六站沿侧面暗梁的远端下缘取像素，与 `1297385297` 的平面远侧求交。换算到长滨路参考面是 39.27–41.41 米。长滨路下四站用白墩柱头像素独立交会，落点 E−103.516 / N−174.458，横向残差 0.12–1.46 米，柱头距各站路面 39.63–43.60 米。两组像素对应轨道同一结构上不同站距的构件，柱头与暗缘资料无法确定每一块下缘的绝对标高。2023 年完工斜照还可辨各车道层、白罩及可通行的下穿关系。[完工照片](https://www.cq.gov.cn/sy/lb/202310/t20231026_12473668.html) · [环评桥型图](https://sthjj.cq.gov.cn/zwgk_249/zfxxgkzl/fdzdgknr/hjyxpj/pzgcxx/sljsxmhpxxgg/201901/P020220914562460734710.pdf)

原游戏上层六点约 7.4–10.3 米，长滨路四点约 0.38–1.38 米。原箱梁的远缘约 42.6 米，长滨路白墩位置也量到约 42 米的相对高度。上层车道欠高是主因，北端箱梁拟合另有约 2 米调整。历史试验里放置的第二条低梁继续留作失败证据。[旧实验](../../evidence/visual-recheck-04-55/rail-soffit/README.md)

## 道路与源码

东西两端沿同日采集片段复算。西侧实证共点为 `1865946215`，外侧分流点 `1865946288` 超出 500 米玩法边界。东侧 `733200823` 将 `59146775` 接至 `176968735`，后者在 `1865946322` 与 `1189963552` 汇合并接入 `176034697`。同日片段覆盖 18 号车桥和 16 号支线。21 号下层步道独立登记。端部同址证据和游戏接坡取样见 JSON。

Blender 4.3.2 用 `blender -b -P work/scene_r24/district_refresh/street_groups/nanqu_rail_grade/build.py -- <grade-controls.json> <output>` 从原 R24、南区路、18/21、16 和轨道桥源取受影响的实体。增量替换原道面、箱梁、栏杆、铺带、柱、材质和 Godot 碰撞。东侧连接按地图节点和实测游戏地面衔接，控制点之间为游戏接坡。导出 GLB 进入正常首班场景，保留原街道材质并使用本批调整的轨道材料。Godot 4.6.3 用 `survey.gd` 的 `--rail-guide=<survey-plan.json>` 参数取竖剖面和原生固定视图。`through_joins.gd` 对三条接头车线往返。`stairs53.gd` 用角色沿原石梯核对踏步和转身，`landing_profile.gd` 保留原 129 点断面。

### 轨道横跨

同一根箱梁及声屏罩沿原轴接续至北端，使用 N−47.6 米的北接控制，箱梁网格最北 N−45.44 米，罩体最北 N−47.99 米。六台相机的 110° 视线按陆侧、车道中央和江侧分别求交。首站中央近缘、远缘为 N−70.93、−79.78 米，第二站为 N−78.53、−87.38 米，末站为 N−84.88、−93.73 米。每条视线沿梁宽取五点，90 点全部命中 Blender 箱梁和罩体以及正常场景的箱梁碰撞。附近资产只保留一套跨道路的梁与罩，南端保留原江上桥段的衔接。

从原整城打开并执行 `work/scene_r24/district_500/compose.py` 可复建可编辑整城，默认输出 `city_and_outer.nanqu_grade.local.blend`，也可用 `CQ_NANQU_GRADE_OUTPUT` 指定独立输出路径。[21 张返图、逐向实测和历史失败](evidence/README.md)

东端 16 号并线修订将重叠的车面裁成同一连续坡面，去除内部侧立面和圆形补面独立碰撞。原道板足迹保留，标线随新面落位。[并线逐帧实测及同机位原图](evidence/merge16/README.md)

04 号陆侧植坡与高冠独立保存在 `nanqu-landside.blend`。从仓库根目录用 Blender 4.3.2 执行 `blender -b -P work/scene_r24/district_refresh/street_groups/nanqu_rail_grade/build_landside.py -- work/scene_r24/district_refresh/street_groups/nanqu_rail_grade/evidence/high_crowns04/landside-plan.json <output>` 可重建可编辑源及 Godot 增量。[前一阶段坡体和树冠](evidence/landside04/README.md) · [高冠同机位、细部和实测](evidence/high_crowns04/README.md)

```sh
bash work/scene_r24/district_500/play.sh --software -- --explore-500 --nanqu-riverwalk
```
