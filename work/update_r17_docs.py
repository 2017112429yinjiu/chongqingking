from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parent.parent
GAME=ROOT/'work/project/chongqing_godot_v05'
DOCS=GAME/'docs'
def write(name,text): (DOCS/name).write_text(text.strip()+'\n',encoding='utf-8')
write('BUILDING_RULES.md','''# 建筑与通行规则
建筑地基必须贴合坡地；墙、楼板、屋檐交接应有封闭实体和明确厚度。斜屋顶按真实建筑轮廓封口，不能只用包围盒上的三角片。

R17 将 13 处非商铺入口的 65 级装饰台阶拆除，改为净高 2.71 m 的平层门厅、真实关闭的住宅户门、门铃和信件口。这里是私人住宅前室，未实现上楼通行；不能将门厅修正说成打通所有楼层。

五条公共路线按建筑轮廓重新布置。全步行宽度加 6 cm 余量、每 10 cm 采样检查平面距离；这只能验证平面包络，不能取代运行时通行。西侧绕开山城里凸出入口并提前接入上层道路；东巷保留树与树池并绕行，树池外缘与通道边缘余量约 0.93 m。窄巷宽 1.35 m。

栏杆不能跨门洞、建筑或通路分支，端部要有立柱。转角平台、阶梯侧壁、物件支撑仍须近景复查。R17 将西侧垃圾桶/袋/筐移出台阶，路灯移出上层路径；所有树干和路灯提供简化碰撞。

楼梯设计目标：踏高约 0.15–0.18 m，净高至少 2.1 m、步行净宽至少 0.9 m，坡地长阶应有平台。此为项目设计值，并非建筑法规认证。当前长阶踏面较长，转角平台造型仍需细化。

验收包含门洞正视图、邻接结构视图、双向连续角色行走、扫掠与实际障碍。垂直射线打到屋顶不等于地面可走。不得宣称整个街区已无任何穿插。
''')
write('INTERACTION_SYSTEM.md','''# 交互系统
interaction_target 定义稳定 ID、提示、可用条件、执行动作和半径。interaction_manager 注册目标、筛选最近目标并在执行前重新检查步行状态、距离、世界遮挡；穿墙与远距离交互拒绝。

R17 注册 16 个目标：面馆、送达点、电瓶车、13 个住宅门铃。门铃使用原创建音效和回应文本；私人户门尚不能打开进入。任务送达点为山城里小院 1 号真实门厅前的可站立位置。

订单 AVAILABLE→PREPARING→READY→CARRYING→DELIVERED。备餐 1.5 s；取餐后纸袋隐藏，交付只计一次 8 元配送收入。送达后可回店接下一单。当前订单目的地固定、收入只在本次运行保存，尚无存档和完整经济系统。

店主为 MPFB CC0 人物与衣服，原创围裙；带 idle/serve 动作与实体碰撞。动作目前为程序关键帧，未达到正式角色动画标准。取餐袋为原创折叠纸袋、提手和面馆标签；处于 READY 时显示在取餐桌上。

电瓶车交互要求停车后安全退出，见 VEHICLE_SYSTEM.md。qa_gameplay 检查边界、幂等与再次接单；qa_delivery 只有一次初始摆位，此后接单、步行靠车、实际骑行、停车下车和步行入户都不在步骤间传送。
''')
write('NPC_SYSTEM.md','''# NPC 与交通模拟架构
R17 已实现一名带骨骼和碰撞的店主、待机/递餐动作、重复订单与住宅门铃。没有运行行人群体、NPC 日程、AI 车流或完整导航网。以下架构仍为待实施设计。

实体数据与可见节点分离。EntityRecord 保存 stable_id、角色、当前位置/道路边、时间、日程索引、目的地、任务和随机种子。SimulationClock 用统一游戏时间；跳时按日程落位，不逐帧补算全部历史。

近层 <=25 m：10 Hz 决策、60 Hz 物理和局部避障；中层 25–70 m：2 Hz 沿已验证路线推进、降低动画频率；远层 >70 m：0.2 Hz 按路线长度和事件时间推进，无骨骼和碰撞节点。分层采用 5 m 滞回、至少驻留 2 秒，屏幕内避免突现。数值是初始预算，必须以实测调整。

日程包含回家、营业、备餐、采购、上下班、休息。订单中断闲置并以幂等事件恢复。仅近层向 NavigationServer3D 申请路线，集中排队每帧最多 2 次；目标变化、路线失效才重算。

步行导航与车辆道路图分离。楼梯只允许行人，小车不进窄巷。按实际碰撞烘焙，门洞、桥梁、楼梯用明确连接；分块异步更新并等待地图同步。交互靠近点必须有身体空间。R17 的连续步行路径是 QA 路径，尚不是 NPC 自动寻路结果。

跨层保留 ID、订单、路线进度和时钟；不得复制实体/订单。车辆用车道图、停靠点、路口预约与跟车，近层再依赖物理碰撞。QA 应覆盖 25/100/250 实体、固定种子回放、跨层长跑、堵塞恢复、楼梯禁行、无重复实体、路径有效率、P50/P95 帧时/CPU/内存；当前这些群体测试均未执行。
''')
write('ART_GUIDELINES.md','''# 美术规范
重庆 200×200 米坡地街巷，目标为电影级可玩画面，当前 R17 尚未达到。Blender Z 向上，Godot Y 向上、北方 -Z，1 单位=1 米。OSM 提供平面布局，不能称实测建筑复刻。

生活痕迹按用途摆放：晾衣两端支撑并离地，车轮接触真实路面，面馆有店主与备餐状态，住宅有门牌和门铃，垃圾桶不占台阶。锈蚀集中在接缝与滴水处，返潮和雨痕局部变化；禁止整体发黑掩盖几何问题。

R17 电表箱有三种漆色、112 组独立读数、额定值、铰链、螺丝、锁、百叶、挡雨沿和离散底缘锈点。旧统一 88888 已替换；仍须用近景核对，不能以面数作为真实感指标。

店主采用逐项 CC0 的 MakeHuman 核心资产，原创围裙和关键帧动作。现有人物面部、手势、服装褶皱与皮肤仍需艺术打磨。取餐纸袋是可复用原创模型。新资产必须保存来源、原包、作者、许可、修改和哈希。

验收以 Godot 实时固定机位和运动观察为准，不用 Blender 渲染或修图替代。近景应显示支撑物、邻接建筑与行走空间。诊断截图可固定动作时间/备餐状态，必须在 capture_manifest 记录该状态。

待改进：大面积铺地与街道边界、台阶转角平台、重复墙面/锈纹、人物年龄与表演、骑手与车轮动画、真实生活活动、环境音、湿润表面层次及性能预算。通过碰撞测试不代表画面验收通过。
''')
licenses=DOCS/'ASSET_LICENSES.md'
base=licenses.read_text(encoding='utf-8').split('\n## R17 人物资产')[0]
licenses.write_text(base+'''\n## R17 人物资产

已实际下载 MPFB 2.0.18 源码 ZIP 与 makehuman_system_assets_cc0.zip，校验 ZIP CRC，原包与 SHA256 在 work/assets_incoming/mpfb/PROVENANCE.json。官方来源 https://github.com/makehumancommunity/mpfb2 与 https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html 。

工具程序为 GPL-3.0-or-later，仅用于构建，未置入游戏。核心模型、目标、骨骼和配套包为 CC0-1.0；官方 https://static.makehumancommunity.org/mpfb/faq/can_i_sell_models.html 允许商用。实际使用的 middleage_asian_male、low-poly eyes、eyebrow001、eyelashes01、short02、male_casualsuit01、shoes02 文件头均单独含 CC0 声明。完整使用项与文件哈希、原声明在 assets/characters/shopkeeper_r17_provenance.json，CC0 法律文本已随资源保存。

CC0 无强制署名要求，仍自愿保留 MakeHuman team / Data Collection AB / Joel Palmius / Jonas Hauquier 来源说明。原创围裙、关键帧动作和取餐纸袋另行标注。不能将此结论扩展到未审查的社区人物资产。
''',encoding='utf-8')
write('QA_CHECKLIST.md','''# 验收清单
R15 历史证据在 verification；R16 检查点在 verification_r16；R17 当前证据在 verification_r17。只有报告中的场景哈希、脚本与配置版本对应时，结果才适用。

- 三份核心 R15 ZIP、主 .blend/.glb 已校验并保留原件；六张缺陷图已恢复。最终 R15 照片 ZIP 仍受浏览器保存的权限限制，未找回。
- R16 已核对 7 车/14 轮、3 组晾衣支撑、6 栋屋顶墙顶封口。
- R17 已实现 5 条改线路径、13 个平层门厅与住宅户门、65 级假台阶拆除、树池绕行、物件重摆、57 个树干/路灯碰撞。
- R17 物理巡查：24 条连续路线（包括 5 条完整路线双向与 2 处入户）、88 点胶囊体净空、121 点垂直覆盖。垂直覆盖不是地面通行认证。
- R17 交互：24 项边界和状态检查；整单测试包含实际骑行约 6 m 与步行最后约 77 m，无阶段间传送。以当前 JSON 的 passed 值为准，不把早期成功当最后版本成功。
- R17 图像：固定机位、人物待机/递餐与餐食状态截图；每图记录视角、画幅、GPU及场景哈希，未修图。
- R17 性能：一名带骨骼店主和一辆可驾驶车，不代表群体仿真性能。

未完成：完整 NPC/车辆导航、群体与日程实现/规模测试、存档、骑手/轮轴动画、全路网驾驶、上楼室内、电影级画面验收。从零完整生成器的 R17 全量重建未执行；已验证从恢复 R15 编辑场景经 R16/R17 修正的工作流。

Blender 导出仍有继承的部分室内叶片网格无效及纹理采样器警告；不能称零警告。Godot 导入/运行错误以日志检查为准。下一轮应清理这些网格并保持叶片轮廓、UV与遮蔽数据。
''')
vehicle=(DOCS/'VEHICLE_SYSTEM.md').read_text(encoding='utf-8').replace('R16a 原型','R17 开发版')
vehicle+='\nR17 另外验证面馆真实停车点出发、实际骑行、停车下车后连续步行入户；这不代表车辆可以进入所有阶梯路线。\n'
(DOCS/'VEHICLE_SYSTEM.md').write_text(vehicle,encoding='utf-8')
(ROOT/'START.md').write_text('''# 重庆外卖王：恢复与持续开发

当前 R17 为本地开发迭代，R16a 为内部检查点。用户要求继续自我迭代至电影级画面与玩法，不急于封包；当前没有新 ZIP、发布或最终验收。

先读 AGENTS.md 与 HANDOFF_LOG.md。原始三份工程包和六张截图在 outputs/R15原始资产，禁止覆盖。最终 R15 照片包仍未回收，不能以本地截图冒充。

Godot 工作工程：work/project/chongqing_godot_v05/project.godot。
Blender 可编辑新场景：work/r17_scene/chongqing_district.blend。
建筑生成与修正源：work/project/chongqing_blender_v05；其中原 chongqing_district.blend 仍为 R15 输入，不是最新场景。
人物可编辑源：work/characters/shopkeeper_r17/shopkeeper_authoring.blend；生成脚本 work/build_shopkeeper.py；许可原包 work/assets_incoming/mpfb。
独立工具：work/tools/godot-4.6.3 与 work/tools/blender-4.3.2-windows-x64。用户 Downloads 工程未修改。

work/verify_r17.ps1 支持 import / gameplay / survey / delivery / capture / performance。报告在工作 Godot 工程 verification_r17；历史 verification、verification_r16 不作为当前结果。运行前须留意是否已有同一项目的导入进程，不并发修改导入缓存。

用户已授权日常修改、下载、引擎测试。平台强制权限门槛不能绕过。会话结束后不声称仍在后台工作。
''',encoding='utf-8')
(GAME/'CHANGELOG.md').write_text('''# 开发变更记录

## R17 · 2026-11-20 · 未封包
修复五段公共路线穿建筑与住宅入口冲突；13 个门厅用真实关闭的户门替代通墙假台阶。绕开完整树池、重摆垃圾物件与路灯，增加 57 个环境障碍碰撞。电表箱加入独立读数和局部漆面损耗。

以逐项 CC0 的有骨骼人物替换方块店主，加入原创围裙、待机与递餐动作、折叠取餐袋、13 个门铃和可重复订单。送达点移至山城里小院 1 号门厅。新增连续整单 QA 和修复路线双向 QA。

尚不具备电影级画面、群体模拟或完整上楼室内。美术与性能结果见当轮实测证据。

## R16a · 内部检查点
恢复并校验 R15 资产，修正车轮、晾衣和屋顶接缝，建立交互、可驾驶电瓶车和首个取送餐原型。保存在 work/checkpoints/R16a_20261120，非对外交付。
''',encoding='utf-8')
print('R17 documentation updated')
