"""Bind internal evidence to actual files. This creates no game package."""
from pathlib import Path
import json,hashlib,datetime,argparse
parser=argparse.ArgumentParser();parser.add_argument('--build',type=int,required=True);parser.add_argument('--motion',required=True)
args=parser.parse_args();assert args.motion.replace('_','').isalnum()
root=Path(__file__).resolve().parent;project=root/'project/chongqing_godot_v05';verify=project/'verification_r18'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
char=digest(project/'assets/characters/shopkeeper_r18.glb');counter=digest(project/'assets/characters/serving_counter_r18.glb')
import_hash=digest(project/'assets/characters/shopkeeper_r18.glb.import')
tests={}
for name in ['shopkeeper_performance','gameplay_test','delivery_end_to_end']:
    report=read(verify/(name+'.json'))
    assert report['passed'] and report['character_sha256']==char and report['character_import_sha256']==import_hash,name
    tests[name]={'passed':True,'count':len(report['tests']),'report_sha256':digest(verify/(name+'.json'))}
captures=read(verify/'city_current/capture_manifest.json');assert captures['character_sha256']==char and captures['counter_sha256']==counter and captures['character_import_sha256']==import_hash
performance=read(verify/'performance.json');assert performance['character_sha256']==char and performance['character_import_sha256']==import_hash
motion=read(root/f'audit/{args.motion}_metadata.json');assert motion['character_sha256']==char and motion['counter_sha256']==counter and motion['character_import_sha256']==import_hash
for name,value in motion['scripts'].items():assert digest(project/f'scripts/{name}.gd')==value,('movie script has changed',name)
for path,value in captures['script_sha256'].items():assert digest(project/path.removeprefix('res://'))==value,('capture script has changed',path)
source=read(root/'audit/r18_source_integrity.json');assert set(source['actions'])=={'idle','serve','greet'} and len(source['bones'])==58 and all(i['packed'] for i in source['images'])
counter_source=read(root/'audit/r18_counter_source.json');assert all(i['packed'] for i in counter_source['images'])
cloth=read(root/'audit/r18_cloth_fit.json');assert all(s['vertices_inside_shirt_over_4mm']==0 and s.get('skirt_vertices_inside_over_4mm',0)==0 for s in cloth['samples'])
paths=list((project/'scripts').glob('*.gd'))+[project/'project.godot',project/'assets/render_profile_r18.json',project/'assets/characters/shopkeeper_r18.glb.import']
paths+=[root/x for x in ['build_shopkeeper_r18.py','shopkeeper_tailoring.py','shopkeeper_performance.py','shopkeeper_skin.py','shopkeeper_face_rig.py','mocap_idle_reference.py','shopkeeper_drape_bake.py','build_serving_counter.py','counter_surface.py','prototype_cloth_rest.py']]
paths+=[root/'characters/shopkeeper_r18/shopkeeper_authoring.blend',root/'characters/serving_counter_r18/serving_counter.blend',root/'characters/cloth_trial/input_character.blend',root/'characters/cloth_trial/drape_result.json']
paths+=[root/'shopkeeper_bib_drape.py',root/'prototype_bib_drape.py',root/'characters/cloth_bib_trial/input_character.blend',root/'characters/cloth_bib_trial/drape_result.json']
report={'revision':'R18 internal character build 17; brushed counter','status':'Internal iteration only. User has not accepted the art; no package or release.','created':datetime.datetime.now().astimezone().isoformat(),'character_sha256':char,'counter_sha256':counter,'city_sha256':digest(project/'assets/chongqing_district.glb'),'tests':tests,'captures':len(captures['captures']),'performance':performance,'movie':motion,'source_reopened':{'bones':58,'actions':source['actions'],'character_packed_images':len(source['images']),'counter_packed_images':len(counter_source['images'])},'cloth_check_scope':cloth['scope'],'hashes':{str(p.relative_to(root)):digest(p) for p in paths},'unresolved':['Art remains below cinematic acceptance: face/hair, garment drape, environment repetition and large empty streets.','Cloth is skinned with an offline 50-percent gravity-informed rest blend, not live cloth physics.','Grip QA measures attachment anchors; close image review is still needed for fingers and handle shape.','No crowd schedules/navigation implementation, rider/wheel animation, save system or full road-network driving.','R15 final photo ZIP remains unavailable; three core archives and six defect screenshots preserved.','Inherited city export leaf/sampler warnings remain; city was not rebuilt in this character iteration.']}
report['revision']=f'R18 internal character build {args.build}; hanging bib, strand brows, planted feet and task-aware attention'
report['character_import_sha256']=import_hash
report['unresolved'][1]='Cloth uses offline lower-skirt and upper-bib gravity/collision rest transfers with skinned secondary bones, not live cloth physics.'
report['unresolved'].append('Blender character export retains inherited sampler and greater-than-four bone influence warnings; runtime tests do not certify every skin vertex.')
(verify/'review_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','character_sha256','counter_sha256','tests','captures','source_reopened']},ensure_ascii=False,indent=2))
