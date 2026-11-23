"""Record the lighting-only iteration on top of the verified editable R20-11 sources."""
from pathlib import Path
import json
import hashlib
import shutil
W=Path(__file__).resolve().parent
root=W.parent;P=W/'project/chongqing_godot_v05';V=P/'verification_r20'
read=lambda path:json.loads(path.read_text(encoding='utf-8'))
record=read(V/'review_summary.json')
prior=read(V/'trial11/review_summary.json')
assert record['revision']=='R20_lane_12_internal' and prior['revision']=='R20_lane_11_internal'
for key in ['source_sha256','layer_blend_sha256','runtime_layers','animated_resident']:
    assert prior['composition'][key]==record['composition'][key],key
assert prior['runtime']==record['runtime'] and prior['resident']['runtime']==record['resident']['runtime']
decision=read(V/'ambient_trial/decision.json')
new=read(P/'assets/render_profile_r20.json')
old=read(W/'checkpoints/R20_lane_11/project/chongqing_godot_v05/assets/render_profile_r20.json')
assert {k for k in old if old[k]!=new[k]}=={'lighting','art_revision'}
assert {k for k in old['lighting'] if old['lighting'][k]!=new['lighting'][k]}=={'ssao_half_size'}
stage=V/'current/resident_motion'
motion=read(stage/'encoding.json')
assert motion['profile_sha256']==hashlib.sha256((P/'assets/render_profile_r20.json').read_bytes()).hexdigest()
assert motion['take_frames']==262 and (stage/'lighting_motion_review.json').is_file()
record['ambient_occlusion_trial']=decision
record['lighting_motion_qa']=read(stage/'lighting_motion_review.json')
record['roof_and_entrance_lighting_qa']=read(V/'ambient_trial/district_comparison.json')
record['preceding_verified_sources']='work/checkpoints/R20_lane_11'
(V/'review_summary.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
checkpoint=W/'checkpoints/R20_lane_12';checkpoint.mkdir(parents=True,exist_ok=True)
for f in [P/'assets/render_profile_r20.json',P/'assets/scene_composition_r20.json',P/'project.godot',V/'review_summary.json',W/'record_lane_r20.py',W/'review_court_lighting_motion.py',W/'review_district_views_r20.py',Path(__file__)]:
    target=checkpoint/f.relative_to(W);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
for folder in [V/'current',V/'resident_ab',V/'resident_court_gpu',V/'resident_meter_comparison',V/'ambient_trial',P/'docs']:
    shutil.copytree(folder,checkpoint/folder.relative_to(W),dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.import'))
shutil.copy2(W/'audit/court_resident.mp4',checkpoint/'court_resident.mp4')
(checkpoint/'README.txt').write_text('This internal lighting recovery point layers render_profile_r20.json over the exact R20_lane_11 sources. Verified identical city, lane, resident and runtime hashes. Full sources live in the project and R20_lane_11.\n',encoding='utf-8')
summary=', '.join(f"{v['current_p95_ms']:.2f}" for v in record['performance']['fixed_views'])
court=', '.join(f"{v['p95_ms']:.2f}" for v in record['resident']['court_performance'])
title='## 2026-11-20　上巷环境光影，第十二次内部构建'
entry=f'''{title}

在第十一次城市、人物及交互源的基础上，仅调整屏幕空间环境遮蔽的采样分辨率。继承同一份可编辑整城和居民源，哈希逐项核对一致。保留实际建筑的天空遮挡、原有扫描纹理及其分辨率、日照阴影范围和所有机位。当前默认配置为 R20_lane_12_internal，恢复点为 work/checkpoints/R20_lane_12，配套完整源在前一恢复点和工作工程。

先以全分辨率、半分辨率、全分辨率三次独立启动测量。邻座机位 P95 分别为 23.663、20.501、23.552 毫秒，中央阶梯为 23.004、19.182、21.207 毫秒，人物正面为 10.484、10.530、10.670 毫秒。四个同机位原图中，人物眼周、头发及凳脚接地可辨，最大的逐通道差来自阶梯，绝大多数像素差在 8/255 以内。原图和实验数据在 verification_r20/ambient_trial，最终配置另有十二张 1600×900 图及 8.73 秒连续动作复查。

最终实际导入及启动、上巷及街坊 {record['tests']['lane_test']} 项、街景 {record['tests']['street_test']} 项、玩法 {record['tests']['gameplay_test']} 项、整单 {record['tests']['delivery_end_to_end']} 项、{record['survey_routes']} 路线及 {record['tests']['survey']} 项巡查通过。取送餐阶段之间传送 0 次。六个 1080p 固定视角 P95 为 {summary} 毫秒。另测的树池全景、近身和邻座为 {court} 毫秒。设备时钟及系统负载会波动，独立测试仅代表记录的条件。

保留未达到目标的项目：树池外侧灰坡、成排相同的远楼、行人和交通生活不足，以及面馆人物表演与服装的近景质量。R15 原最终照片包仍缺。未封包。
'''
log=root/'HANDOFF_LOG.md';old_log=log.read_text(encoding='utf-8')
if title not in old_log:log.write_text(old_log.replace('# 持续交接日志\n','# 持续交接日志\n\n'+entry+'\n',1),encoding='utf-8')
for path in [log,root/'START.md',root/'AGENTS.md']:shutil.copy2(path,checkpoint/path.name)
print(record['revision'],'six views',summary,'court',court)
