"""Validate current evidence and preserve an internal recovery point, never a ZIP."""
from pathlib import Path
import json,hashlib,shutil,struct,datetime
W=Path(__file__).resolve().parent;ROOT=W.parent;P=W/'project/chongqing_godot_v05';V=P/'verification_r19';C=V/'current'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4194304),b''):h.update(b)
    return h.hexdigest()
main_sha=sha(P/'scripts/main.gd');layer_sha=sha(P/'assets/street_r19/street_life.glb');profile_sha=sha(P/'assets/render_profile_r19.json')
evidence={};counts={}
for name in ['street_test.json','gameplay_test.json','delivery_end_to_end.json','survey.json']:
    r=read(C/name);assert r['passed'],name
    assert r['runtime_sha256']['res://scripts/main.gd']==main_sha,name
    for path,digest in r['runtime_sha256'].items():assert sha(P/path.removeprefix('res://'))==digest,(name,path)
    assert r['street_layer']['sha256']==layer_sha,name
    assert r['art_profile']['sha256']==profile_sha,name
    evidence[name]=sha(C/name);counts[name]=len(r['tests'])
survey=read(C/'survey.json');delivery=read(C/'delivery_end_to_end.json')
assert len(survey['tested_route_names'])==24
assert delivery['teleports_between_stages']==0
geometry=read(W/'audit/r19_geometry.json');assembled=read(W/'audit/r19_assembled.json')
assert geometry['passed'] and geometry['glb_sha256']==layer_sha
assert assembled['passed'] and assembled['detail_layer']['sha256']==layer_sha
assert assembled['blender_scene_sha256']==sha(W/'scene_r19/chongqing_district.blend')
capture=read(C/'captures/capture_manifest.json')
assert capture['art_profile_sha256']==profile_sha
assert capture['script_sha256']['res://scripts/main.gd']==main_sha
assert capture['scene_identity']['street_r19']['sha256']==layer_sha
assert not capture['failures'] and len(capture['captures'])==9
shots={}
for p in sorted((C/'captures').glob('godot_*.png')):
    with p.open('rb') as f:head=f.read(24)
    size=struct.unpack('>II',head[16:24]);assert size==(1600,900)
    shots[p.name]={'sha256':sha(p),'size':list(size)}
perf=read(C/'performance.json');base=read(V/'baseline_performance/performance.json');omni=read(V/'omni_shadow_trial/performance.json')
assert perf['art_profile']['sha256']==profile_sha and perf['street_layer']['sha256']==layer_sha
for p,d in perf['runtime_sha256'].items():assert sha(P/p.removeprefix('res://'))==d
comparison=[]
for row in perf['views']:
    prior=next(v for v in base['views'] if v['view']==row['view'])
    comparison.append({'view':row['view'],'baseline_p95_ms':prior['p95_ms'],'current_p95_ms':row['p95_ms'],'current_draw_calls':row['draw_calls']})
record={'revision':'R19_scene_05_internal','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Internal work in progress; not cinematic acceptance, delivery, publication or background execution.','base_scene_sha256':assembled['base_city']['sha256'],'detail_layer_sha256':layer_sha,'profile_sha256':profile_sha,'runtime_sha256':perf['runtime_sha256'],'evidence_sha256':evidence,'checks':counts,'reopened_geometry_checks':len(geometry['checks']),'routes':len(survey['tested_route_names']),'delivery_teleports_between_stages':delivery['teleports_between_stages'],'blender_composition':assembled,'captures':shots,'capture_manifest_sha256':sha(C/'captures/capture_manifest.json'),'performance':{'gpu':perf['gpu'],'viewport':perf['window_size'],'samples_per_view':240,'warmup_frames':90,'comparison':comparison,'note':'One independent run per variant, fixed cameras and one occupied stationary scooter. Frame intervals include CPU/GPU/OS effects; not a crowd, continuous driving, minimum-FPS or universal 60-FPS guarantee.','omni_light_rider_p95_ms':omni['views'][-1]['p95_ms'],'spot_light_rider_p95_ms':perf['views'][-1]['p95_ms']},'known_limits':['Whole 200m district not rebuilt to photographic/film quality. Repeated facades, empty slopes, generic railings/storefronts and sparse actual activity remain.','Original final R15 photo ZIP is still missing; no new photo pixels used as game textures.','8 inherited glTF shared-image sampler warnings; reopened layer sampler settings consistent. No new invalid-mesh warning in this detail export.','SSR, reflection probes and SDFGI disabled. SDFGI trial rejected for visible dotted edge artifacts.','No new crowd simulation, schedules, traffic, environment sound or full-body scooter mounting animations.'],'new_sources':'assets/street_r19/PROVENANCE.json','review_doc':'docs/SCENE_R19_REVIEW.md'}
(V/'review_summary.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
checkpoint=W/'checkpoints/R19_scene_05';checkpoint.mkdir(parents=True,exist_ok=True)
paths=[W/'scene_r19/chongqing_district.blend',W/'scene_r19/street_life.blend',W/'build_street_r19.py',W/'assemble_scene_r19.py',W/'audit_street_r19.py',W/'audit_assembled_r19.py',W/'verify_scene_r19.ps1',W/'record_scene_sources_r19.py',Path(__file__),P/'project.godot']
paths+=list((P/'scripts').glob('*.gd'))+list((P/'shaders').glob('*.gdshader'))+list((P/'assets').glob('render_profile_r19*.json'))
paths+=list((P/'assets/street_r19').glob('*'))+[P/'assets/sky/kloofendal_overcast_puresky_2k.hdr',P/'assets/scene_composition_r19.json']
for p in paths:
    if not p.is_file():continue
    dest=checkpoint/p.relative_to(W);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
shutil.copytree(V,checkpoint/'verification_r19',dirs_exist_ok=True)
shutil.copytree(P/'docs',checkpoint/'docs',dirs_exist_ok=True)
for name in ['r19_geometry.json','r19_assembled.json','r19_import05.log','r19_build05.log']:
    shutil.copy2(W/'audit'/name,checkpoint/name)
(checkpoint/'README.txt').write_text('Internal recovery point only. Not a packaged game. Preserved base city GLB and source generator/library remain in the working project, identified by SHA256. Full editable Blender city and independent layer are copied here. Runtime is Godot 4.6.3 Forward+. See verification_r19/review_summary.json.\n',encoding='utf-8')
handoff=f'''## 2026-11-20：R19 场景第05次内部构建（未封包）

用户明确要求场景也继续按实景照片/电影级目标自我迭代。此轮真实改动面馆—中央梯坎，不是继续只改人物。完整可编辑城市在 work/scene_r19/chongqing_district.blend，已重开 {assembled['objects']} 对象、{assembled['packed_images']} 张打包图、未打包引用图0。独立层 work/scene_r19/street_life.blend；build_street_r19.py 从原 R17 输入生成，assemble_scene_r19.py 合并源。Godot 默认 render_profile_r19.json；运行时仍组合 R17 基础 GLB + R19 layer，基础 scene_manifest 不可改成新导出19。店主20/骑手09保持。

细节层52对象、19级踏步覆层、7件可碰撞生活物件。重做店招与布雨棚、支持件/灯具/排烟管、局部修补和附墙线路；摆餐桌椅/碗筷/盆栽/晾晒，把垃圾移进侧面服务区；补格栅、梯坎分缝/挡边、连续远景山体。当前层 SHA256 {layer_sha}。组合与其他资产哈希在 assets/scene_composition_r19.json、verification_r19/review_summary.json。

实际对照：基线6机位，多轮日光/程序阴天/摄影阴天；当前9张1600×900固定图已逐张观察。SDFGI试验出现屋檐/窗框黑点，拒绝采用。排烟管挡窗、灯穿雨棚、餐桌挨垃圾、地砖感踏步、整体最低点导致单腿悬空均在本轮继续修正；原失败图/日志保留。新摄影天空是Greg Zaal/Poly Haven CC0，MD5核验匹配；不是重庆实拍天空。原项目6类CC0扫描模型复用、保留出处，不谎称新下载。John Rash黑白阶梯照片只做视觉观察，没有照片像素入游戏。原最终R15照片包仍缺。

当前验证：Blender几何{len(geometry['checks'])}项、引擎街景{counts['street_test.json']}项、既有交互{counts['gameplay_test.json']}项、整单{counts['delivery_end_to_end.json']}阶段、巡查{len(survey['tested_route_names'])}路线/{counts['survey.json']}项通过。整单步骤间传送0。旧巡查110帧备餐假设引起4项失败，已改等真实READY状态并保留300帧超时，旧证据在survey_failure_legacy_timing。当前结果绑定最终层/配置/代码，未覆盖R18已确认结果。

GPU {perf['gpu']}，1920×1080，每视角90帧预热后240帧；六机位当前P95为 {', '.join(str(round(v['current_p95_ms'],3)) for v in comparison)} ms（顺序见summary）。面馆新增灯具从全向阴影改为有灯罩的向下投射，骑手镜头P95从{omni['views'][-1]['p95_ms']:.3f}降到{perf['views'][-1]['p95_ms']:.3f}ms。属于单次固定机位对照，不能声称全流程/人群稳定60帧。

运行入口 work/verify_scene_r19.ps1；内部恢复点 work/checkpoints/R19_scene_05，没有ZIP/发布。新增导出保留8条共享纹理采样器提示，重开检查采样设置一致；不是零警告工程。继续缺口：大面积空坡、建筑重复、栏杆/店招同质化、真实营业/居民活动、环境音与稳定间接光照。下一步推进主要路线两侧平台、门前空间与建筑差异，做第二段连续精修街巷；当前远低于电影级，不得当交付完成，也不声称会话后后台运行。

'''
log=ROOT/'HANDOFF_LOG.md';text=log.read_text(encoding='utf-8');marker='## 2026-11-20：R19 场景第05次内部构建（未封包）'
if marker not in text:log.write_text(text.replace('# 持续交接日志\n','# 持续交接日志\n\n'+handoff,1),encoding='utf-8')
start=ROOT/'START.md';s=start.read_text(encoding='utf-8')
s=s.replace('城市主体保持 R17 修正，人物/取餐台为当前 R18 内部迭代','城市基础保留 R17 修正并叠加 R19 场景层，人物/取餐台为当前 R18 内部迭代')
s=s.replace('Blender 可编辑新场景：work/r17_scene/chongqing_district.blend。','Blender 现行完整组合：work/scene_r19/chongqing_district.blend。work/r17_scene/chongqing_district.blend 为保留的基础输入。')
start.write_text(s,encoding='utf-8')
shutil.copy2(ROOT/'START.md',checkpoint/'START.md');shutil.copy2(ROOT/'HANDOFF_LOG.md',checkpoint/'HANDOFF_LOG.md')
print(json.dumps({'checks':counts,'routes':24,'shots':len(shots),'geometry':len(geometry['checks']),'checkpoint':str(checkpoint),'p95_ms':[v['current_p95_ms'] for v in comparison]},ensure_ascii=False))
