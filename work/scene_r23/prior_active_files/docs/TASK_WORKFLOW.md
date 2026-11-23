# 工作流程

R22 先从旧工程测屋面、立面及桌面，再生成屋顶与街角图层。整城安装图层后才拟合岸坡、桥台及视线。修改数据或模型后必须更新对应导入、复开和相机证据。运行入口为 work/verify_roofs_r22.ps1，旧版渲染配置可用 -Baseline 指定。每次失败试验用不同的 Run 名保留。

R21 环境源的重建顺序和证据目录见 [城区环境记录](DISTRICT_R21_REVIEW.md)。全城 Blender 冷启动和 Godot 摄制/性能测试顺序运行。每次调整外观先用固定镜头比较、登记淘汰原因，再用正式入口复跑。展示用小图保留尺寸变化说明，原始 PNG 与原始 Movie Maker 录像单独保存。

对第十二次光影构建，先完成常规引擎回归、树池专项性能、居民开关对照及录像，再运行 work/review_court_lighting_motion.py 和 work/review_district_views_r20.py。work/record_lane_r20.py 核对工作源和实测指纹，work/checkpoint_lighting_r20.py 将光影实验与整城源恢复点关联。

R20 开发先读根目录 START.md 和最新交接记录。上巷与树池的模型、现场问路及分距离动画使用 work/verify_lane_r20.ps1 检查。完整图组、巡查与性能证据写入 verification_r20/current，树池专项性能用独立 Run 名保存。人物接触检查入口为 work/audit_court_motion.py，使用已重开的居民和城市 Blender 文件。已确认的中间版本保留原图、日志和资产指纹。
R19场景入口：`work/build_street_r19.py` 从原R17场景生成独立层，`work/assemble_scene_r19.py` 生成可编辑完整组合，再用 `audit_street_r19.py` / `audit_assembled_r19.py` 实际重开检查。`verify_scene_r19.ps1` 的证据写入 verification_r19；不可覆盖已确认的R18报告。运行时使用基础GLB+细节GLB，不应将基础清单的revision直接改成19。

1. 先读 START、AGENTS、HANDOFF_LOG，确认源文件、哈希、版本与最新未解决项。
2. 保留 R15 原始压缩包；只改工作副本。每次模型修复同时保留可重跑的源代码。
3. 先复现：截图 ID、对象名、位置、实际碰撞。单项修复建立可量化标准。
4. Blender 打开 → 几何检测 → 保存 → GLB 导出 → Godot 导入 → 实际运行 → 固定机位 → 步行/交互/性能。
5. 引擎退出码与日志一起检查；Blender 使用 --python-exit-code 1，不能只看默认退出码。
6. 将新测试与 R15 历史报告分开。用户目前要求持续迭代、不急于封包；任何未来候选必须先验证准确副本可打开，并保留未完成内容。

当前开发机 Windows，独立 Godot 4.6.3 Forward+ / Blender 4.3.2，GPU 经实际 Vulkan 运行确认 RTX 4070 Laptop GPU。不得直接修改 Downloads 中由 Godot 4.7.2 打开的旧副本。

全量重建：在 Blender 目录运行 build_district.py，环境 CQ_REVISION=17、CQ_STAGE_ONLY=1、CQ_OUTPUT_DIR 为指定的新工作目录；共用 repair_scene_r16.py、repair_scene_r17.py、utility_detail_r17.py。此次实际执行的是 R15 编辑场景经 R16/R17 修正与导出，全量从零重建尚未测试。不得让新构建覆盖输入基线。

R17 检查脚本为 work/verify_r17.ps1，阶段 import、gameplay、survey、delivery、character、capture、performance。相同项目导入缓存不并发写；性能测试时不同时运行其他引擎测试。人物构建脚本 work/build_shopkeeper.py 以 GPL-3.0-or-later 与 MPFB 工具配合，原始 CC0 输入和导出图形不因此改变许可范围，构建工具不放进游戏运行时。

R18 当前入口为 work/build_shopkeeper_r18.py，模块为 shopkeeper_tailoring / shopkeeper_performance / shopkeeper_skin / shopkeeper_face_rig / mocap_idle_reference；所有输入许可在 assets_incoming，各阶段导出日志在 work/audit。可编辑人物源 work/characters/shopkeeper_r18/shopkeeper_authoring.blend，取餐台源 work/characters/serving_counter_r18/serving_counter.blend。build_shopkeeper.py 与 R17 验证入口仅历史用途。

当前使用 work/verify_r18.ps1 的 import / character / lab / capture / gameplay / delivery / performance。构建完成后才导入；导入完成后才运行截图；不要让同一路径的新 GLB 哈希与旧导入缓存图像混合。Model/脚本有新改动，前一哈希的测试不自动转为新版本通过。持续检查点不是用户验收，更不是停止迭代或封包许可。

骑手与可动电瓶车工作链：build_rider_trial.py → audit_rider_trial.py → install_rider_trial.py → import → configure_rider_import.py（首次生成导入文件后）→ import → rider / gameplay / delivery → 独立 performance。rider 为GPU固定截图+物理，rider_physics 为无图物理，两者证据目录分开。源36姿势只覆盖选定鞋面/踏板，车轮与把手运行测量只覆盖试验路段，禁止泛化为全场景无穿透。

连续骑行记录使用 --r18-rider-motion、--motion-tag=<唯一标记>，--left-side 观察支撑脚；Godot MovieMaker 的原AVI与拍摄时指纹必须保留。transcode_motion_review.py 仅作无剪切、无调色H264转码和原帧解码，不得将转码当作再次运行引擎。用 record_rider_review.py <内部构建号> <电影标记> 检查当前资产/导入配置/控制脚本/电影一致，再保存恢复点，无游戏压缩包。
