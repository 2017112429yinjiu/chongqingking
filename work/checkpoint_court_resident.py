"""Save the verified working sources, their reference hashes, and a concise handoff."""
from pathlib import Path
import json
import shutil
W=Path(__file__).resolve().parent
root=W.parent
P=W/'project/chongqing_godot_v05'
V=P/'verification_r20'
report=json.loads((V/'review_summary.json').read_text())
assert report['revision']=='R20_lane_11_internal'
r=report['resident']; blend=report['composition']; counts=report['tests']
dest=W/'checkpoints/R20_lane_11'
sources=[P/'project.godot',P/'assets/render_profile_r20.json',P/'assets/scene_composition_r20.json',W/'scene_r20/chongqing_district.blend',W/'scene_r20/upper_lane.blend',V/'review_summary.json']
for sub in ['characters/court_resident','project/chongqing_godot_v05/assets/characters/court_resident','project/chongqing_godot_v05/assets/fonts']:
    sources.extend(p for p in (W/sub).glob('*') if p.is_file())
sources.extend((P/'scripts').glob('*.gd'))
sources.extend((P/'shaders').glob('*shader*'))
sources.extend(W.glob('*r20.py'))
sources.extend(W.glob('*court*.py'))
sources.extend(W.glob('*court*.ps1'))
sources.extend([W/'capture_court_resident.gd',W/'verify_lane_r20.ps1',W/'activate_court_trial11.py'])
for path in sources:
    if path.suffix in ['.blend1','.uid']:continue
    target=dest/path.relative_to(W);target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,target)
for folder in [V/'current',V/'resident_court_gpu',V/'resident_ab',V/'resident_meter_comparison',P/'docs']:
    shutil.copytree(folder,dest/folder.relative_to(W),dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.import'))
for name in ['court_resident.mp4','r20_assembled11.log','r20_trial11_face_audit_court_motion.log']:
    shutil.copy2(W/'audit'/name,dest/name)
(dest/'README.txt').write_text('Internal editable recovery point for R20_lane_11_internal. Use the preserved R15/R17 base, R19 street layer and R20_lane_09 lane resources in the working project. Exact runtime layer, source and evidence hashes are in verification_r20/review_summary.json.\n',encoding='utf-8')
ab=r['resident_on_off_p95_ms']
line=lambda key:', '.join(f'{v:.2f}' for v in ab[key].values())
frames=', '.join(f"{v['current_p95_ms']:.2f}" for v in report['performance']['fixed_views'])
court=', '.join(f"{v['p95_ms']:.2f}" for v in r['court_performance'])
heading='## 2026-11-20　上巷树池居民，R20 第十一次内部构建'
entry=f'''{heading}

Godot 4.6.3 Forward+ 的入口和 render_profile_r20.json 保持在原工程。Blender 4.3.2 已重开整城工作源 work/scene_r20/chongqing_district.blend，包含 {blend['objects']} 个对象、{blend['packed_images']} 张打包图，以及一位在实际座板上的 80 骨骼居民。独立人物源在 work/characters/court_resident/court_resident.blend。居民上游文件固定版本和逐文件校验在 work/assets_incoming/court_resident/provenance.json。两段动作、模型及纹理来自 Microsoft Rocketbox，MIT 全文保存在游戏的 assets/characters/court_resident/LICENSE.txt。

玩家靠近居民按 E 可问路。携餐和普通状态提供不同指引，玩家车辆和订单继续使用原系统。居民会歇脚、张望、眨眼，问路时出现轻微笑意。近处逐帧呈现动作，中距离减少采样，远处隐藏并保留活动时钟。此处只有一名常驻居民，未实现全区通勤和人群。没有新增语音或口型。

第一轮按单点鞋底接触校正后，全鞋底扫描发现脚跟嵌入最多约 37 毫米。第十一次构建保留鞋姿态和腿段长度，按坡度调整目标脚位。每段动作额外检查 48 个未参与拟合的姿势，连同拟合时的姿势共计 130 帧，双鞋的最大离地约 1.7 毫米、最大嵌入约 1.5 毫米。坐面与衣物的最大间隙约 8 毫米。模型导出保留了共享采样器和未导出非材质顶点色的提示，最终动作、脸部控制、三种材质与五张贴图均由实际导入检视。完整数据在 verification_r20/current/resident_motion。

当前引擎通过上巷及人物 {counts['lane_test']} 项、街景 {counts['street_test']} 项、既有玩法 {counts['gameplay_test']} 项、整单 {counts['delivery_end_to_end']} 项、{report['survey_routes']} 条路线共 {counts['survey']} 项巡查。整单各阶段之间传送 0 次。十二张 1600×900 引擎图包含树池原机位、近身和邻座眼高。work/audit/court_resident.mp4 是同一机位 262 帧连续引擎录像，按脚本触发问路，30 fps，只裁去启动和相机就位时间，未调色。原始 AVI 和动作触发记录保留。

本机六个 1080p 固定视角 P95 依次为 {frames} 毫秒，树池全景、近景和邻座三个独立视角分别为 {court} 毫秒。另做一轮同配置关闭／开启／再次关闭居民的对照，机位依次为树池、邻座和骑手。三组分别为 {line('off_a')}；{line('on')}；{line('off_b')} 毫秒。每个视角预热 90 帧后取 240 帧。样本受运行时负载影响，不能据此推断全城人群或连续驾驶帧率。完整记录在 verification_r20/resident_ab。

可从 work/checkpoints/R20_lane_11 恢复本轮改动，原先的工程、场景层和 R15 回收档案保持独立。原最终 R15 照片包仍缺。树池镜头前景已有可互动的生活场面，远处的裸坡、重复住宅、单调路缘和稀少的人流仍很醒目。面馆店主及围裙本轮沿用之前的源与动作，人物美术仍需继续检查。未封包。
'''
log=root/'HANDOFF_LOG.md';old=log.read_text(encoding='utf-8')
if heading not in old:log.write_text(old.replace('# 持续交接日志\n','# 持续交接日志\n\n'+entry+'\n',1),encoding='utf-8')
for name in ['START.md','AGENTS.md','HANDOFF_LOG.md']:shutil.copy2(root/name,dest/name)
print('Saved',dest,frames,court)
