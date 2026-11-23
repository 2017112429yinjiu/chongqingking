from pathlib import Path
import json,shutil
root=Path(__file__).resolve().parents[1]
project=root/'work/project/chongqing_godot_v05'
docs=project/'Docs';docs.mkdir(exist_ok=True)
texts={
'ART_GUIDELINES.md':'''# 美术规范
重庆 200×200 米坡地街巷。1 单位=1 米；Blender Z 向上，Godot Y 向上、北方为 -Z。保留既有独立建筑、坡地尺度、居民日常用品与潮湿旧表面。不得把 OSM 平面数据称为实测建筑复刻。

生活痕迹按用途布置：晾衣有两端支撑、衣物离地，食物有店主与交付状态，车轮接触真实路面。锈蚀集中在铁件接缝和滴水处，墙脚返潮、屋檐雨痕、踏步磨损采用局部变化；不得用整体发黑掩盖几何错误。

占位角色是逻辑验证资产，不能称为最终人物美术。R16a 未新增下载的美术资源。新资源必须记录来源、原文件、作者、许可、修改和哈希。

验收使用 Godot 实时固定机位，不用 Blender 渲染或修图代替。缺陷近景必须同时看到支撑物、邻接建筑和行走空间。
''',
'ASSET_NAMING.md':'''# 资产命名
保留 R15 既有名称，防止碰撞筛选失效。新增修正使用 COL_R16_RoofSeal_<building>、COL_R16_DryingRack_<seed>。COL_ 表示真实碰撞几何，COLH_ 为必要的隐藏碰撞面，禁止为掩盖视觉缺陷增加碰撞墙。

交互使用稳定 ID：vehicle.scooter.99、shop.noodle、delivery.home。显示文字与 ID 分离。文件使用小写英文与下划线，版本写入清单。不得以文件修改时间推断版本。

所有交付必须保留 source / scene / exported asset 的对应关系；geometry_repairs_r16.json 记录修正，scene_manifest.json 记录当前版本，旧测试放在明确标注的历史目录。
''',
'BUILDING_RULES.md':'''# 建筑与通行规则
建筑地基必须贴合坡地；墙、楼板、屋檐交接应有封闭实体和明确厚度。斜屋顶按真实建筑轮廓封口，不能只用包围盒上的三角片。

楼梯必须有明确起点、连续踏步、终点平台与有效去向。不得以通向整面后墙的五级装饰台阶冒充楼梯。R16a 仍保留此缺陷，待后续改变入口空间与楼板开口后进行完整连通验收。

新楼梯设计目标：踏高约 0.15–0.18 m、踏面约 0.28–0.32 m，净高至少 2.1 m、步行净宽至少 0.9 m，适应地形时应增加平台。此为项目设计值，并非建筑法规认证。

栏杆按建筑轮廓、门洞和平台生成排除区；端部要有立柱。仍须修复既有栏杆/楼梯穿建筑的问题，不得仅删去栏杆后宣称安全。

验收必须包含侧视图、门洞正视图、连续角色通行，以及胶囊体扫掠；垂直射线打到屋顶不等于地面可走。
''',
'NPC_SYSTEM.md':'''# NPC 与交通模拟架构
状态：本文件为设计；R16a 只实现一个无寻路的店主占位角色。没有上线行人群体、日程或车流系统。

实体数据与可见节点分离。EntityRecord 保存 stable_id、角色、当前位置/道路边、时间、日程索引、目的地、任务和随机种子。SimulationClock 用统一游戏时间；时间跳跃后按日程重新落位，不逐帧补算全部历史。

分层计划：near <=25 m 角色 10 Hz 决策、60 Hz 物理和局部避障；mid 25–70 m 每秒 2 次沿路线推进、降低动画频率；far >70 m 每秒 0.2 次按路线长度和事件时间推进，无骨骼与碰撞节点。升降级采用 5 m 滞回，至少驻留 2 秒，屏幕内实体不突然消失。以上为初始预算，必须用实测调整。

统一日程活动：回家、营业、备餐、采购、上下班、休息。订单可中断店主闲置活动；活动恢复使用幂等事件。仅近层实体向 NavigationServer3D 请求路径，集中排队每帧最多 2 次；目的地变化或路径失效才重算。

步行网与车辆道路图分开：楼梯只允许行人，小车不进入窄巷。楼梯/桥梁/门洞需明确导航连接，按实际碰撞烘焙；场景分块、异步更新并等地图同步后才发请求。交互靠近点与入口不同，不把目的地放进墙里。

跨层只转移表现形式，保存实体 ID、订单、路线进度和时钟；不能复制订单或车辆。车辆采用车道图、停靠点、路口预约与跟车，近层再用碰撞。QA：25/100/250 实体分档，固定种子回放、长时间跨层、堵塞恢复、楼梯限行、无重复实体、无无效路径、P50/P95 帧时/CPU/内存。当前均未执行。
''',
'VEHICLE_SYSTEM.md':'''# 车辆系统
R16a 原型使用真实导入的 99 号电瓶车，CharacterBody3D 街道驾驶。前进上限 6 m/s、倒车 1.8 m/s，W 前进、S 先刹车后倒车，A/D 转向、空格急刹、P 停车、E 下车。停车点保持在本次运行中；尚无跨启动存档、车轮旋转、骑手动画或真实悬架。

静态七辆车通过 Blender 实际路面 BVH 检查轮胎下缘，拟合车身俯仰和高度；不使用统一抬高量。驾驶时物理盒保持竖直，前后轮探测调整模型俯仰。其横坡贴合和陡坎表现仍需专项测试。

上车暂停步行输入与碰撞；下车必须停车且四个候选位置存在可站立地面、身体空间和不穿墙的连线。全部被挡时拒绝下车。速度归零后确认停车，禁止瞬间下车保留车辆速度。

后续车辆类型通过配置共享控制接口；性能与输入由控制器负责，美术模型只提供座位、轮轴、出口锚点。道路图必须禁止楼梯、坡度过大及过窄路段。当前没有 AI 交通。
''',
'INTERACTION_SYSTEM.md':'''# 交互系统
interaction_target.gd 定义稳定 ID、半径、可用条件、提示与动作；interaction_manager.gd 管理注册、最近可用目标、距离与视线，并在执行时复查。必须处于步行模式，避免自由观察的 E 上升与交互混用。

流程：靠近电瓶车 → E 上车 → 驾驶/刹车/倒车 → 刹停 P 停车 → E 下车。取送餐：靠近店主 → E 接单 → 1.5 秒打包 → E 取餐 → 到目标 E 交付。没有食物不能送达；重复交付不能加次数。骑车时交互用于安全下车。

店主与食物是原创简单占位体，只用于验证流程。没有任务存档、经济奖励、背包容量、多个订单、对话树或正式人物动画。

主入口是 gameplay.gd，不在角色控制器内硬编码商店。后续门、座椅、收件人等复用目标协议。每项动作要有 unavailable 的提示、可逆退出或幂等保护。
''',
'TASK_WORKFLOW.md':'''# 工作流程
1. 先读 START、AGENTS、HANDOFF_LOG，确认源文件、哈希、版本与最新未解决项。
2. 保留 R15 原始压缩包；只改工作副本。每次模型修复同时保留可重跑的源代码。
3. 先复现：截图 ID、对象名、位置、实际碰撞。单项修复建立可量化标准。
4. Blender 打开 → 几何检测 → 保存 → GLB 导出 → Godot 导入 → 实际运行 → 固定机位 → 步行/交互/性能。
5. 引擎退出码与日志一起检查；Blender 使用 --python-exit-code 1，不能只看默认退出码。
6. 将新测试与 R15 历史报告分开；只有验证过的准确候选才可封包，记录未完成内容。

当前开发机 Windows，独立 Godot 4.6.3 Forward+ / Blender 4.3.2，GPU 经实际 Vulkan 运行确认 RTX 4070 Laptop GPU。不得直接修改 Downloads 中由 Godot 4.7.2 打开的旧副本。

全量重建：在 Blender 目录运行 build_district.py，环境 CQ_REVISION=16、CQ_STAGE_ONLY=1、CQ_OUTPUT_DIR 为指定工作目录；R16 修正共用 repair_scene_r16.py。此次只实际执行了基于恢复场景的修正及导出，全量从零重建尚未测试。
''',
'QA_CHECKLIST.md':'''# 验收清单
历史证据与本次验证必须分开，详见 HANDOFF_LOG 和 verification_r16。

- [x] 三份核心原始 ZIP CRC 与复制前后 SHA256 校验；主 .blend / .glb 匹配 R15 交付元数据。
- [x] 六张缺陷图回收；R15 Blender 打开，2713 对象、124 内嵌图，无外链缺失图片。
- [x] R15 Godot 4.6.3 导入、4 条连续步行路线与原取送餐检查通过。
- [x] R15 实际 Forward+ 三固定机位 1280×720，非最终原始照片包替代品。
- [x] R16 Blender 7 辆车 / 14 个轮胎下缘相对真实路面约 2 mm；3 组晾衣绳加支撑并抬高，6 栋斜屋顶加封口。
- [ ] R15 最终 22 张照片压缩包恢复（浏览器权限拒绝，保留原链接）。
- [ ] 住宅台阶终点修复与连接上下楼层。
- [ ] 电表箱近景细化。
- [ ] 既有栏杆/楼梯与建筑的全街区相交修复。
- [ ] 完整行人/车辆导航网、日程、近中远模拟实现及规模性能。

R16 导入、运行、交互、固定机位和性能结果在完成后由实际报告记录，不能以勾选代替。新斜屋顶封口仍需近景审查；晾衣支撑/车辆横坡与停车交互要检查，不等同于全场景无交叉。
''',
'ASSET_LICENSES.md':'''# 资源与工具许可核查（2026-11-20）
这不是新素材集；R16a 没有下载或集成新的第三方美术资产。保留 R15 material_provenance.json、scanned_assets/source_credits.json、字体许可证与 OSM 来源。

| 来源 | 核查结果 | 署名/再分发 | 本次使用 |
|---|---|---|---|
| Poly Haven https://polyhaven.com/license | 资产 CC0，可用于商业作品 | 不强制署名，仍保留来源；可再分发原资产 | 已恢复 R15 既有扫描植物/家具/材质 |
| ambientCG https://docs.ambientcg.com/license/ | CC0，商业可用 | 不强制署名，允许原资产再分发 | 候选旧墙面/地面，未下载 |
| Kenney Food Kit https://kenney.nl/assets/food-kit 与 https://kenney.nl/support | 页面标示 CC0 | 不强制署名 | 候选取餐食物，未下载 |
| Quaternius https://quaternius.com/license.html | 当前 QAL v1.0，页面与部分旧包 CC0 标示冲突 | 可商用但限制原资产再分发；不能直接把它塞进可编辑工程包 | 暂不采用，需逐包许可核实 |
| Godot https://docs.godotengine.org/en/stable/about/complying_with_licenses.html | MIT | 发布引擎运行文件须保留 MIT 与适用第三方通知 | 使用官方 4.6.3 工具，交付工程不附引擎二进制 |
| Blender https://www.blender.org/support/faq/ | 软件 GPL，作品不因此自动 GPL | 如再分发 Blender 程序需履行其义务 | 使用官方 4.3.2 工具，交付工程不附程序 |
| OpenStreetMap https://www.openstreetmap.org/copyright | ODbL 1.0 | 署名 OpenStreetMap contributors、提供许可链接；派生数据库的共享义务需保留 | R15 既有 XY 布局，source_data 完整保留 |

禁止依据网站标题就把整站所有内容归为 CC0。每个新下载包需保留原许可、作者、具体 URL、版本、日期、原始哈希、改动和交付范围。照片只作参考时不得擅自作为贴图封包。
'''
}
for name,text in texts.items(): (docs/name).write_text(text,encoding='utf-8')
evidence=root/'outputs/R15原始资产/用户缺陷截图';evidence.mkdir(exist_ok=True)
for num,temp in [(6,'7HwO2B'),(7,'zTQESd'),(5,'mBU0sN'),(4,'Nl0Jnu'),(3,'Pjlh5I'),(2,'WqgTPv')]:
    src=Path.home()/'AppData/Local/Temp'/('codex-file-preview-'+temp)/('image(%d).png'%num)
    if src.exists():shutil.copy2(src,evidence/src.name)
source=(root/'outputs/R15原始资产')
(source/'恢复状态与原下载链接.md').write_text('''# R15 / v05 资产恢复状态
三份核心原始包已经恢复并校验：Godot 工程、Blender 可编辑主场景、Blender 重建源代码/材质/扫描资产。它们不是仅从 GLB 反向导入的替代品。主 .blend 与 .glb 的哈希匹配原交付元数据。

六张用户缺陷截图保存在本目录。验收说明 chongqing_v05_review_zh.txt 从 Godot 包中原样提取。

未完成：最终 R15 引擎照片包。当前下载目录只有 R14 照片，不把 R14 冒充 R15。浏览器访问 ChatGPT 的权限被拒绝，未继续通过其它渠道访问该来源。

[原 R15 最终照片包下载入口](https://chatgpt.com/library?file_id=libfile_fde3_f-0d871093e264819195355fb145906d31_90cf8250be808191af2b6f07daa2cb26&account_id=personal)

[原交付聊天](https://chatgpt.com/c/6afdba42-f1b4-83ec-8e88-e7ab091dabb5)

不能确认旧云端临时工作区仍存在，也不能因本次未连接就判断它已丢失。此次恢复的是原聊天交付的持久文件。新的本地工程与原始包分开；本地测试不会更改原始交付。
''',encoding='utf-8')
manifest=json.loads((project/'assets/scene_manifest.json').read_text(encoding='utf-8'))
manifest['revision']=16
manifest['iteration']='R16a-local-prototype'
manifest['baseline_revision']=15
manifest['current_evidence']='verification_r16; historical verification and docs are R15 only'
(project/'assets/scene_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Wrote',len(texts),'project documents; copied screenshot evidence')
