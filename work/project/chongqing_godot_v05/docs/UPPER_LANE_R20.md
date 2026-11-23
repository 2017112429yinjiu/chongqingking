# 梯坎里 · 上巷与树池

树池南段木凳上有一位歇脚的街坊。玩家可坐在相邻位置看街，站到她前方按 E 问路。她会在自然坐姿和张望之间切换，面馆与送餐住宅对应两种问路提示。人物、两段动作和修正后鞋底均可在 Blender 内逐帧查看。工程内的 assets/characters/court_resident/PROVENANCE.json 和 LICENSE.txt 保存了原始来源、修改与完整许可。

Godot 4.6.3 Forward+ 默认从 render_profile_r20.json 进入。上巷墙面手握扶手从实测墙脚延伸到高处，23 个原踏步标高上铺独立切石。玩家可以在居民告示前按 E 轮读三张纸，使用对面的冲洗龙头，在上巷出口树池边的两段木座休息。水流最长五秒，具有空间水声。休息采用第一人称坐姿视角，步行碰撞体留在接近座位的安全位置。

### 空间与美术依据

沿窄巷每米对原模型进行墙面和地面采样。两处晾衣架锚固点与七处扶手支撑旁的实墙均重新射线核对。树池选用已有的 tree_41。水平座面分成南北两段，各自的腿长按地面标高计算。外圈铺石沿原坡面铺设，西侧两个土池分级。树边遮光采样考虑现有树冠和座框。晾晒衣物以固定上缘和渐强的下摆位移模拟微风。

参考图19的树下休息点、图20的石墙扶手，见[《2015年中国城市步行友好性评价报告》，印刷页19](https://www.nrdc.cn/Public/uploads/2016-12-02/58416d12760d3.pdf#page=21)。仅观察照片；游戏使用独立建模。图中文字、晾晒衣物、座椅、水龙头、植物叶片和水声均为本工程制作。告示中的营业时间、社区文字和门牌属于虚构街区。原 R15 最终照片包仍待回收。

完整字体来自 [Noto CJK 官方源](https://github.com/notofonts/noto-cjk)，遵循 [SIL OFL 1.1](https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE)。字库副本、修订号、许可和哈希保存在 work/assets_incoming/r20_noto。游戏用的衍生字体已另命名，许可与版权在 assets/fonts/R20_font_sources.json 和 R20_OFL.txt。旧版告示曾漏字，失败截图保存在 verification_r20/trial01。

铺石、木纹、土和灌木复用工程的既有材质与模型。来源、作者与许可见 assets/lane_r20/PROVENANCE.json。工程原有各项许可继续适用。

### 可编辑源

居民的独立编辑源在 work/characters/court_resident/court_resident.blend。work/build_court_resident.py 从校验过的上游素材重建骨架动作和材质，work/fit_court_resident.py 计算树池落位，work/audit_court_motion.py 检查人物与实景的接触。17 个姿态提供坡面修正输入，正式检查每段 65 帧，另含 48 个未用于拟合的姿态。work/capture_court_resident.gd 以相同机位记录连续动作。

work/scene_r20/chongqing_district.blend 是完整编辑文件。独立层 work/scene_r20/upper_lane.blend、四张印刷原稿及生成脚本一并保留。初始输入是 work/scene_r19/chongqing_district.blend。运行时组合 R17 城市、R19 街景、R20 上巷，并按独立柜体显示电表细节。原电表高模仍在完整编辑文件内。

- work/paint_lane_prints_r20.py、work/subset_lane_type_r20.py 生成原创告示和界面字库。
- work/build_lane_r20.py 调用 work/upper_court_seat_r20.py 生成上巷、树池与交互位置。
- work/bake_sky_r20.py 从基础建筑和屋檐采样面馆及上巷的天空可见度，影响指定表面的环境光。
- work/build_water_sound_r20.py 合成循环水声。work/locate_meters_r20.py 和 work/build_meter_lod_r20.py 从原始数据拆分电表。
- work/assemble_lane_r20.py 重组并重开整座城市。当前组合记录见 assets/scene_composition_r20.json。

### 检查与缺口

第十二次内部构建对比了两档屏幕空间环境遮蔽。人物近景、树池、邻座和梯坎均用同样的镜头复拍，另对相同动作的两条引擎原片匹配了 262 帧。不同采样方式的性能对照在 verification_r20/ambient_trial，人物有无的独立对照在 verification_r20/resident_ab。最终配置的实际截图与动作记录在 verification_r20/current。

work/verify_lane_r20.ps1 提供 import、lane、capture、street、gameplay、delivery、survey、performance。当前证据和视角分别保存在 verification_r20/current 和其 captures 目录。review_summary.json 汇总当前指纹和性能。街面固定视角的帧间隔反映本机和当时的负载。

巷口远楼仍有重复，树池外仍有大面积裸露坡面。居民营业、活动、对话和人群交通需要进一步制作。晾衣属于程序化布料摆动，树影与天空遮挡为静态近似。当前主要用照片检视了使用空间与材料关系，尚无整区摄影级验收。
