梯坎里 · 重庆街区 05 — Godot 工程

交付范围与画面标准
这是可运行、可继续编辑的街区环境样板，尚未达到参考图所要求的电影级成品标准。
当前仍存在部分铺地过于均匀、背景楼与窗格重复、近景树叶有面片感、室内接触阴影偏弱和生活细节不足的问题。
部分窗口只完成基础室内空间；并非所有房间均可进入或已完成精装。
这是重庆风格街区设计：核心建筑包含14个地图平面轮廓与7个原创补建，地形、高度、立面和外围背景含设计内容，不是测绘级1:1复刻。
已修复与未修复项、实机检查结论以随附逐图复核记录为准。

交付身份
场景 revision：15
核心范围：200 × 200 米
GLB SHA256：06c280f56fb58152688aaf058cd87f7a3f71819478bea0ad7ab2869ce5bd5223
最终运行记录中的引擎：4.6.3-stable (official)
最终运行记录中的渲染器：forward_plus
当前渲染配置：assets/render_profile_v05.json
配置记录：v05_lighting_c_r10_actual_practical_completion
最终天空资源：res://assets/sky/kloofendal_48d_partly_cloudy_puresky_2k.hdr

打开工程
解压后，在 Godot 中导入 project.godot，然后运行 main.tscn / 按 F5。
本包保留模型、脚本、shader、字体、HDRI 和 .import 输入配置。Godot 首次打开时会在本机重新生成导入缓存；包内不附 .godot 缓存或从 GLB 解出的重复贴图。
使用与最终记录相同的引擎和渲染器，可减少环境差异。其他硬件上的帧率需在目标设备测量；本交付没有据此声明固定帧率。

操作
W A S D：移动；按住鼠标右键：观察；Shift：加速。
Tab：步行 / 自由镜头；空格：步行时跳跃；Q / E：自由镜头下降 / 上升。
E：步行时在目标附近取餐或送达；R：步行时回到街口，自由镜头时重置当前机位；Esc：释放鼠标。
1–9、0：前十个固定机位；[ / ]：循环机位；右上角下拉框：选择机位。
H：显示 / 隐藏界面；F12：保存当前运行截图。
实际提供 22 个机位，名称见 assets/viewpoints.json 与随附最终捕获清单。

最终机位
  01. overview — 全街区 · 南向北
  02. street_entry — 山城巷街口
  03. noodle_corner — 小面馆与下层街面
  04. central_steps — 中央梯坎与临街住家
  05. west_lane — 西侧居民巷
  06. community_court — 社区球场与住宅
  07. narrow_passage — 上坡楼间通道
  08. upper_houses — 上层院落回望
  09. east_gallery — 东侧砖墙坡巷
  10. residential_road — 东侧居民道路
  11. upper_street — 上层长街与店面
  12. roofscape — 台地、院落与屋顶
  13. community_front — 社区服务站
  14. residential_entry — 居民楼入口与墙脚
  15. window_courtyard — 院落住家 · 家务间近景
  16. tea_interior — 巷口茶馆 · 门口看店内
  17. window_living — 坡道住家 · 深房与木椅近景
  18. window_north — 北侧住家 · 窗内生活近景
  19. noodle_interior — 小面馆 · 门口看店内
  20. window_reading — 坡巷住家 · 窗内生活近景
  21. window_dining — 临街住家 · 备餐间近景
  22. planting_detail — 树池、土壤与旧铺装近景

复核资料
verification/capture_manifest.json 记录实际机位、输出尺寸、保存结果、引擎与模型/配置哈希。
verification/physics_survey.json 记录 216 项检查、12 条路线、88 个步行空间采样和 121 个区域碰撞采样。
区域垂直碰撞采样允许命中地面或屋顶；可行走性应结合独立路线与胶囊体空间记录判断。
verification 中的 root_review_zh.txt、interior_review_zh.txt、lighting_review_zh.txt 为逐图视觉复核原文。
docs/delivery_metadata.json 是本次实际交付身份与数量汇总。最终照片由单独照片包提供。

资料与范围
本项目为包含行走交互的环境美术样板。平面资料、地形、建筑与周边背景的来源范围以 scene_manifest 的 provenance 为准：
  planar: OpenStreetMap contributors / ODbL 1.0; source outlines are retained in source_data/geo_layout.json
  terrain: Authored hillside and distant ridges, not DEM survey
  architecture: 21 individually composed core buildings (14 mapped planar outlines, 7 authored infill); facade details/heights are authored. Additional surrounding blocks are context design, not surveyed reconstructions.
  reference_photos: Wikimedia Commons Shancheng Lane photographs used for visual study; no photo pixels are bundled as game textures
  textures: Poly Haven CC0 scans + original procedural surface assets; exact files and credits in material_provenance.json
  props_and_vegetation: Original authored props plus Poly Haven CC0 scan models. Prepared instances, controlled LODs, and edited plant grouping; source credits in scanned_assets/source_credits.json.
  lighting: Godot runtime profile and CC0 photographic HDRI supplied in the engine project. Blender preview lighting is not the acceptance render.

素材来源、作者与许可证保存在 docs/MATERIAL_PROVENANCE.json、docs/MATERIAL_CREDITS_zh.txt、docs/MODEL_CREDITS.json，以及 assets/fonts 与 assets/sky 中的来源记录。
