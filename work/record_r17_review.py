"""Persist reviewed evidence and handoff. Does not package or publish a game."""
from pathlib import Path
import json,hashlib,shutil,datetime
ROOT=Path(__file__).resolve().parent.parent
GAME=ROOT/'work/project/chongqing_godot_v05'
VERIFY=GAME/'verification_r17'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
scene_hash=sha(GAME/'assets/chongqing_district.glb')
reports={k:read(VERIFY/v) for k,v in {'survey':'survey_test.json','gameplay':'gameplay_test.json','delivery':'delivery_end_to_end.json','character':'character_animation.json','performance':'performance.json','capture':'captures/capture_manifest.json'}.items()}
for name in ['survey','gameplay','delivery']:
    assert reports[name]['passed'] and reports[name]['scene_sha256']==scene_hash,name
assert reports['character']['passed']
assert reports['character']['asset_sha256']==sha(GAME/'assets/characters/shopkeeper_r17.glb')
assert reports['performance']['scene_sha256']==scene_hash
assert reports['capture']['scene_sha256']==scene_hash
assert len(reports['capture']['captures'])==11
for name in ['import','gameplay','survey','delivery','character','capture','performance']:
    log=(VERIFY/'logs'/f'{name}.log').read_text(encoding='utf-8')
    assert not any(s in log for s in ['SCRIPT ERROR:','Parse Error:','\nERROR:']),name
manifest=read(GAME/'assets/scene_manifest.json');manifest['current_evidence']='verification_r17/review_summary.json; R17 internal development, not artistic acceptance'
(GAME/'assets/scene_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[*GAME.glob('scripts/*.gd'),GAME/'project.godot',*GAME.glob('assets/*.json'),GAME/'assets/characters/shopkeeper_r17.glb']
summary={'status':'R17 internal development; not packaged, not cinematic acceptance','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scene_sha256':scene_hash,'character_sha256':reports['character']['asset_sha256'],'checks':{'survey':len(reports['survey']['tests']),'continuous_routes':len(reports['survey']['tested_route_names']),'gameplay':len(reports['gameplay']['tests']),'delivery_stages':len(reports['delivery']['tests']),'character_bones':reports['character']['bone_count'],'runtime_captures':len(reports['capture']['captures'])},
 'performance':reports['performance'],'source_fingerprints':{str(p.relative_to(GAME)):sha(p) for p in files},
 'known_limits':['Not cinematic final art','No NPC/traffic crowd simulation or navigation implementation','No persistence, rider rig or wheel animation','No accessible upper storeys','Inherited Blender leaf mesh and texture sampler warnings','Full from-scratch generator not run','R15 final photo ZIP still blocked by saved browser permissions']}
(VERIFY/'review_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(ROOT/'work/audit/r17_blend_open.json',VERIFY/'blender_open.json')
shutil.copy2(ROOT/'work/audit/character_glb_geometry.json',VERIFY/'character_glb_geometry.json')
out=ROOT/'outputs/R17进度检查';out.mkdir(parents=True,exist_ok=True)
for source,name in [('godot_r17_worker_entry.png','山城里入口.png'),('godot_r16_shop.png','店主与面馆.png'),('godot_r16_meter.png','电表箱.png'),('godot_r17_takeaway.png','取餐纸袋.png')]:
    shutil.copy2(VERIFY/'captures'/source,out/name)
shutil.copy2(VERIFY/'review_summary.json',out/'本轮验证.json')
status='''R17 本地开发进度，非最终交付；未封包、未发布。

已恢复并校验 Godot、Blender主场景、Blender重建三份 R15 核心包，以及六张用户缺陷截图。原件在 outputs/R15原始资产，未覆盖。R15最终照片ZIP仍受浏览器保存的权限设置限制，尚未取回；不能据此推断旧云端整个工作区丢失。

本轮修正五段穿楼/入口冲突的路线，13处通墙假台阶改为有户门的平层门厅。绕开树池、重摆垃圾物件和路灯，增加树干与灯柱碰撞；电表箱增加112组独立读数、不同漆色和局部锈迹。

面馆加入已核查CC0的带骨骼店主、原创围裙与纸袋；支持接单、取餐、电瓶车驾驶/刹停/倒车/停车/下车、步行入户送达、回店再次接单，以及13处住宅门铃。

最新城市哈希对应的实测：242项巡查（24条连续路线）、24项交互、11阶段整单流程通过；动作导入检查通过，11张固定机位为Godot原始截图。整单流程仅初始摆位一次，其后实际骑行约6.17米、最后一段步行约76.72米，无阶段间传送。

RTX4070 Laptop，1920×1080，一名带骨骼店主与一辆车：三视角P95帧间隔8.40–11.50ms。这不是人群模拟或所有硬件的性能承诺。

画面尚未达到电影级。后续重点是铺地/台阶转角和生活使用痕迹、人物服装与表演、骑手和车轮动画、继承网格警告、NPC与车流导航。现阶段没有存档、人群/交通日程或可通行的完整住宅楼层。

工程与下一轮操作记录已保存在工作区 START.md、HANDOFF_LOG.md 和工程 docs。会话结束后没有宣称后台持续执行。
'''
(out/'开发状态.txt').write_text(status,encoding='utf-8')
log=ROOT/'HANDOFF_LOG.md'
old=log.read_text(encoding='utf-8')
entry='''## R17 本轮最终已核对记录

城市 SHA256：'''+scene_hash+'''。Godot 4.6.3 导入和运行无日志错误；242 项巡查/24 条连续路线、24 项交互、11 阶段整单流程均通过。53 骨骼人物的 idle/serve 实际上臂变化 0.548 rad，独立 GLB 蒙皮计算在两动作 0/1/2 秒的鞋底最低点接近0、总高约1.71 m。修复诊断截图混合导致旧姿势未刷新的问题，现11视角截图已完成并复查相关改动。动作仍是伸手递餐原型，尚无手部精确接触/袋子跟随。

独立性能采样 RTX4070 Laptop、1920×1080：街口P95 11.499 ms，住宅8.396 ms，俯视10.312 ms。单人物/单车，不代表群体规模。所有当前证据和源文件指纹在 verification_r17/review_summary.json。Blender城市重开116打包图/零外链。原始截图副本和非最终进度说明在 outputs/R17进度检查，未生成游戏压缩包。

最后修改的 main.gd 已再次跑完 gameplay/survey/delivery；人物/截图/性能是该脚本版本。scene_manifest 的证据文字在记录阶段更新，不影响城市GLB或游戏逻辑。当前保留局限：继承叶片无效网格警告、场景和服装重复/平整感、长台阶转角缺少精细平台、角色表演未精修、无存档/骑手/轮轴动画/群体导航、全量从零生成器未跑、R15最终照片包未恢复。继续按这些项迭代；此处没有宣告项目或电影级目标完成。

'''
log.write_text(old.replace('# 持续交接日志\n','# 持续交接日志\n\n'+entry,1),encoding='utf-8')
print(json.dumps(summary['checks'],ensure_ascii=False))
