from pathlib import Path
import shutil,json,hashlib
root=Path(__file__).resolve().parents[1]
game=root/'work/project/chongqing_godot_v05'
blend=root/'work/project/chongqing_blender_v05'
out=root/'outputs/Chongqing_v06_R16a'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
assert json.loads((game/'verification_r16/gameplay_test.json').read_text(encoding='utf-8'))['passed']
out.mkdir(exist_ok=True)
shutil.copytree(game,out/'Godot',dirs_exist_ok=True,ignore=shutil.ignore_patterns('.godot','export_templates','feature_profiles','script_templates','text_editor_themes'))
shutil.copytree(blend,out/'Blender',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.blend','*.blend1','godot_project','outputs'))
shutil.copy2(root/'work/r16_scene/chongqing_district.blend',out/'Blender/chongqing_district.blend')
shutil.copy2(root/'work/r16_scene/geometry_repairs.json',out/'Blender/geometry_repairs_r16.json')
shutil.copy2(root/'work/audit/r16_blender.json',out/'Blender/open_check_r16.json')
shutil.copy2(root/'AGENTS.md',out/'AGENTS.md')
start='''# 重庆街区 v06 / R16a 本地接续原型

基线：v05 / R15。此版本不是全部缺陷修复完成版。原始三份资产 ZIP 单独保存在相邻的 R15原始资产 目录。

## 打开和操作
使用 Godot **4.6.3** 导入 `Godot/project.godot`，等待首次模型导入，再运行主场景。首次导入体积较大的 GLB 需要时间。此次用的是 Forward+，实测显卡 RTX 4070 Laptop GPU。

按 Tab 切到步行，WASD 移动、按住右键转向、Shift 快走，向小面馆走。电瓶车在店门前，靠近 E 上车；W 前进，S 先刹车后倒车，A/D 转向，空格刹车，停稳 P 停车，再 E 下车。出口阻挡时需换位置。

到“梯坎小面 · 店主”附近按 E 接单，等待打包，再按 E 取餐；到上层住宅的送餐标记按 E 交付。角色和食物是简单占位体。F12 截图、H 隐藏 HUD，1–0 和方括号选择原有固定视角。

Blender **4.3.2** 打开 `Blender/chongqing_district.blend`。源代码、字体、材质与扫描资产同在 Blender 目录。修正入口为 `repair_scene_r16.py`，全量生成器 `build_district.py` 默认 R16。全量从零重建尚未执行；本次已执行恢复 R15 主场景的修正、保存、导出与重新打开。

## 本次范围
已修改七辆静态车的轮胎贴地、三组晾衣绳支撑与高度、六栋斜屋顶墙顶封口、街头电表箱细节；加入可复用交互目标、取送餐状态机与一辆可驾驶电瓶车。驾驶车从狭窄原停放点移到小面馆前空地，其余车辆保留原位。

尚未完成：住宅入口五级台阶仍接后墙；部分楼梯/栏杆与建筑相交；完整 NPC 日程、导航网、交通与分层模拟只完成设计；没有骑手动画、车轮旋转、跨启动存档、多订单或最终人物美术。

## 验证与历史
本次证据位于 `Godot/verification_r16`，交接与许可在 `Godot/docs` 的大写命名 Markdown 中。原有 `verification`、`review_zh.txt`、`delivery_metadata.json` 与 v05 README 是 R15 历史资料，不能作为 R16 验收结论。候选打开与封包哈希见根目录 DELIVERY_MANIFEST.json。

R15 最终 22 张照片的原压缩包仍待恢复，浏览器来源访问权限曾被拒绝。已保存六张用户缺陷图和本次新引擎截图；新截图不是旧照片包的替代品。
'''
(out/'START.md').write_text(start,encoding='utf-8')
(out/'Godot/START.md').write_text(start,encoding='utf-8')
manifest={'version':'v06 / R16a','baseline':'v05 / R15','status':'candidate_staged; exact_candidate_open_check_pending','engine':'Godot 4.6.3','blender':'4.3.2','files':{}}
for rel in ['Godot/assets/chongqing_district.glb','Godot/project.godot','Godot/scripts/main.gd','Godot/scripts/gameplay.gd','Godot/scripts/scooter_controller.gd','Blender/chongqing_district.blend','Blender/repair_scene_r16.py']:
    p=out/rel;manifest['files'][rel]={'bytes':p.stat().st_size,'sha256':sha(p)}
(out/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(out),flush=True)
