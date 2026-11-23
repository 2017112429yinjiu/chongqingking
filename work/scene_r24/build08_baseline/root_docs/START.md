# 重庆外卖王：恢复与持续开发

## 当前工作版 R24 · 南区路上下街

Godot 4.6.3 打开 `work/project/chongqing_godot_v05/project.godot`，F5 进入南区路，Tab 落地。沿下层人行道往前，右手是车道，左边挡墙的开口有六级梯坎。上梯后往左到菜摊，往右到修伞配钥匙铺；下梯回头可看路对面的高架。机位菜单可直接选择这些位置。鼠标移动转向，Esc 释放。

整城编辑源在 `work/scene_r24/chongqing_district.blend`。复查命令和证据见 `work/verify_frontage_r24.ps1` 以及日常工程的 `docs/FRONTAGE_R24_REVIEW.md`。当前阶段为内部优化。

## 历史城区工作版 R23 · 南区路与坡地街面

使用 Godot 4.6.3 打开 `work/project/chongqing_godot_v05/project.godot`，按 F5 进入南区路。按 Tab 在当前街口落地，WASD 行走，移动鼠标转向，低头看脚，Esc 释放鼠标，左键点回画面恢复。R 回到配送街口。右上机位菜单末尾可选球场长椅、晾衣、临街窗内、梯坎便利、树池与花坛等复查位置。

整城编辑源在 `work/scene_r23/chongqing_district.blend`。行人、电瓶车以外的两款主路车辆与步行身体分别有同目录的 Blender 工作源。日常游戏由原城区和多层增量组合；这次的建筑与环境修改由 `assets/block_r23/block.glb` 和节点替换清单载入。

工作区 `work/verify_street_r23.ps1` 提供导入、启动和实测入口。原始九图在 `work/scene_r23/user_evidence`，本轮主工程证据在 `work/project/chongqing_godot_v05/verification_r23/current`。整改范围和待复核处详见游戏文档 `docs/STREET_R23_REVIEW.md`。本版为内部试玩。

## 上一版城区工作记录 R22

当前第七次构建使用第六次建设的整城几何和美术，在 32 张 2K 环境扫描上启用高质量显存压缩。主工程仍使用 MSAA 2×。现行检查位于 `verification_r22/import01`，压缩前的第六次检查在 `verification_r22/current`。

用 Godot 4.6.3 Forward+ 打开 `work/project/chongqing_godot_v05/project.godot` 并按 F5。默认配置为 `assets/render_profile_r22.json`。整城 Blender 4.3.2 源是 `work/scene_r22/chongqing_district.blend`。来源、迭代和复现见[屋顶与江岸记录](work/project/chongqing_godot_v05/docs/DISTRICT_R22_REVIEW.md)。当前优先项仍是玩家实际走过的城区环境。人物继续使用现有版本。

## 历史城区工作版 R21 第七次构建

在 Godot 4.6.3 里打开 `work/project/chongqing_godot_v05/project.godot` 并按 F5 运行工程。默认美术配置为 `assets/render_profile_r21.json`。整城 Blender 4.3.2 源为 `work/scene_r21/chongqing_district.blend`，独立增量图层为同目录 `district_environment.blend`。保留旧项目名以沿用 Godot 用户数据路径。

本轮重点是街口、梯坎、上巷和屋顶之间的空间关系。源文件、实拍参考、引擎对照、运行成本和遗留问题见 [城区环境记录](work/project/chongqing_godot_v05/docs/DISTRICT_R21_REVIEW.md)。取送餐和树池居民仍从原入口体验。以下 R20 及以前的记录作为历史版本保留。

现行光影配置为 `R20_lane_12_internal`。使用上巷和面馆的实景遮挡采样，屏幕空间环境遮蔽按半分辨率计算。街坊、座板及城市源与第十一次构建相同。对照、连续动作及其适用范围见最新交接记录。

树池居民的独立 Blender 源在 `work/characters/court_resident/court_resident.blend`。上巷进入树池后可向木凳上的街坊问路，旁边有可坐的位置。Godot 仍通过下方 R20 入口打开。

**当前工作版为 R20 上巷与树池。** Godot 入口是 `work/project/chongqing_godot_v05/project.godot`。完整可编辑城市在 `work/scene_r20/chongqing_district.blend`，本轮独立图层在同目录的 `upper_lane.blend`。操作、来源与验证见工程 docs/UPPER_LANE_R20.md。下方 R19、R18 段落记录历史构建。

当前场景推进到 **R19 第05次内部构建**，不是最终交付：完整可编辑城市为 `work/scene_r19/chongqing_district.blend`；独立细节源为 `work/scene_r19/street_life.blend`；生成入口 `work/build_street_r19.py`，组合入口 `work/assemble_scene_r19.py`。Godot 默认读取 `render_profile_r19.json`，运行时组合原 R17 城市与 R19 细节层；基础 GLB 仍为 R17，勿混淆。店主20、骑手09保持原版本。场景对照、许可、未达标项见工程 `docs/SCENE_R19_REVIEW.md`；本轮证据在 `verification_r19`。`work/verify_scene_r19.ps1` 提供当前场景检查，历史 R18 证据不可覆盖。

当前工作根目录已迁入 `C:/Users/尹久/Documents/重庆外卖王`。完整复制 11694 个文件、约 12.75 GiB，复制失败 0；旧目录保留。R17 人物美术已被用户明确否定，正在重做，不能以此前测试通过视为合格。

进行中的人物迭代为 R18：`work/build_shopkeeper_r18.py` 是现行生成入口，配套 `shopkeeper_tailoring.py` / `shopkeeper_performance.py` / `shopkeeper_skin.py`。可编辑文件在 `work/characters/shopkeeper_r18/shopkeeper_authoring.blend`；取餐台源在 `work/characters/serving_counter_r18`。城市主体仍为已修正的 R17，不要混淆为城市已全量重建。`prepare_r18_character.py` 只是历史起步脚本，已阻止覆盖现行源。

R18 的 `work/verify_r18.ps1` 支持 import / character / gameplay / delivery / lab / capture / performance。人物检查新增餐袋跟手、连续取放、眼睑、10秒实录待机循环和双眼注视；原始近景在 Godot 工程 `verification_r18`。这些是内部迭代证据，尚未达到用户要求的电影级验收，不要封包。

补充模块：`shopkeeper_face_rig.py`（58骨骼含两眼）、`mocap_idle_reference.py`（100STYLE CC BY 4.0，必须保留署名）、`shopkeeper_drape_bake.py`（离线下摆褶皱转移）、`shopkeeper_bib_drape.py`（胸片悬垂转移）。布料试验在 `work/characters/cloth_trial` 与 `cloth_bib_trial`，不可误称运行时布料。第20次胸片改动已完成对应检查并保存 work/checkpoints/R18_character_20；后续游戏逻辑有变化，旧整体验证不能自动代表新逻辑。

骑手09已接入并通过当前专项、交互与整单检查，恢复点 `work/checkpoints/R18_vehicle_09`：`work/build_rider_trial.py` 生成 `work/characters/rider_r18_trial/rider_authoring.blend` 与 `scooter_articulated.blend`，`work/install_rider_trial.py` 复制开发资产。Microsoft Rocketbox Male_Adult_10 为 MIT，原始素材/许可/哈希在 assets_incoming/rocketbox_research，运行时保留完整许可；未使用其动作库。当前骑姿、平滑脚部支撑、转向接触、头盔为原创，人物不是新店主。车轮、把手和脚撑由 scooter_visual.gd 驱动；精确现状见 HANDOFF_LOG 与 verification_r18/vehicle_review_summary.json。无完整上/下车全身动画，横坡脚部拟合和美术细节仍未完成。

人物 GLB 的高级导入设置单独关闭动画优化器：默认精简把脚部位移变成一个关键帧，破坏固定脚 IK。源动画必须同时导出脚部位置键。R18 脚锁检查现在要求漂移小于0.2毫米；不要把城市资产的优化一并关闭。

城市基础保留 R17 修正并叠加 R19 场景层，人物/取餐台为当前 R18 内部迭代，R16a 为历史检查点。用户要求继续自我迭代至电影级画面与玩法，不急于封包；当前没有新 ZIP、发布或最终验收。

先读 AGENTS.md 与 HANDOFF_LOG.md。原始三份工程包和六张截图在 outputs/R15原始资产，禁止覆盖。最终 R15 照片包仍未回收，不能以本地截图冒充。

Godot 工作工程：work/project/chongqing_godot_v05/project.godot。
Blender 现行完整组合：work/scene_r19/chongqing_district.blend。work/r17_scene/chongqing_district.blend 为保留的基础输入。
建筑生成与修正源：work/project/chongqing_blender_v05；其中原 chongqing_district.blend 仍为 R15 输入，不是最新场景。
历史 R17 人物源：work/characters/shopkeeper_r17/shopkeeper_authoring.blend；历史脚本 work/build_shopkeeper.py。现行人物源与脚本见上方 R18，许可原包 work/assets_incoming/mpfb。
独立工具：work/tools/godot-4.6.3 与 work/tools/blender-4.3.2-windows-x64。用户 Downloads 工程未修改。

work/verify_r17.ps1 支持 import / gameplay / survey / delivery / capture / performance。报告在工作 Godot 工程 verification_r17；历史 verification、verification_r16 不作为当前结果。运行前须留意是否已有同一项目的导入进程，不并发修改导入缓存。

用户已授权日常修改、下载、引擎测试。平台强制权限门槛不能绕过。会话结束后不声称仍在后台工作。
