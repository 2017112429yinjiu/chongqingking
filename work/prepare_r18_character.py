from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent
if (p/'build_shopkeeper_r18.py').exists():
    raise SystemExit('Historical bootstrap only. Use build_shopkeeper_r18.py directly; do not overwrite the iterated authoring source.')
s=(p/'build_shopkeeper.py').read_text(encoding='utf-8')
s=s.replace('shopkeeper_r17','shopkeeper_r18').replace("'age':.58,'muscle':.42,'weight':.57", "'age':.73,'muscle':.46,'weight':.61")
s=s.replace("('hair','short02','Hair')", "('hair','short04','Hair')")
s=s.replace("TargetService.reapply_macro_details(human)","""TargetService.reapply_macro_details(human)
targets=ROOT/'assets_incoming/mpfb/mpfb2-master/src/mpfb/data/targets'
for target,value in {'head/head-age-incr':.38,'head/head-rectangular':.17,'head/head-fat-incr':.12,'mouth/mouth-angles-up':.10,'mouth/mouth-laugh-lines-out':.13,'eyes/l-eye-bag-incr':.15,'eyes/r-eye-bag-incr':.12}.items():
    TargetService.load_target(human,str(targets/(target+'.target.gz')),weight=value)
""")
start=s.index('# Original fabric apron');end=s.index('bpy.ops.file.pack_all()',start)
s=s[:start]+'''# Garment and animation are separate reproducible authoring modules.
sys.path.insert(0,str(ROOT))
from shopkeeper_tailoring import build
from shopkeeper_performance import animate
shirt=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'casualsuit' in o.name)
for ob in bpy.context.scene.objects:
    if ob.type=='MESH':
        for poly in ob.data.polygons:poly.use_smooth=True
        for slot in ob.material_slots:
            if slot.material and slot.material.use_nodes:
                bs=slot.material.node_tree.nodes.get('Principled BSDF')
                if bs:
                    bs.inputs['Roughness'].default_value=.64 if ob==human else .79
                    bs.inputs['Metallic'].default_value=0
                    bs.inputs['Emission Strength'].default_value=0
build(rig,shirt,ROOT)
animate(rig,OUT)
'''+s[end:]
s=s.replace("'animations':['idle','serve']", "'animations':['idle','serve','greet']")
s=s.replace('Authored procedural keyframes, not motion capture; motion requires visual refinement.','Asymmetric authored IK baked at 30 Hz; planted feet; one-hand grip; delayed weighted hem bones. Not motion capture or live cloth simulation.')
s=s.replace('Fitted cotton apron, neck straps and pocket; authored geometry.','Cut draped apron with curved pocket, bound seams, waist ties, hem bones. Poly Haven Cotton Jersey CC0 PBR maps; colormass and Rico Cilliers, voluntary attribution.')
(p/'build_shopkeeper_r18.py').write_text(s,encoding='utf-8')
d=p/'assets_incoming/cotton_jersey';api=json.loads((p/'assets_incoming/cotton_jersey_api.json').read_text())
files=[]
for key in ['Diffuse','nor_gl','Rough']:
    info=api[key]['1k']['jpg'];f=d/info['url'].split('/')[-1]
    assert hashlib.md5(f.read_bytes()).hexdigest()==info['md5']
    files.append({'name':f.name,'url':info['url'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'api_md5_verified':True})
(d/'PROVENANCE.json').write_text(json.dumps({'asset':'Cotton Jersey','source':'https://polyhaven.com/a/cotton_jersey','license_url':'https://polyhaven.com/license','license':'CC0-1.0','commercial_use':True,'redistribution':True,'attribution_required':False,'voluntary_credit':'colormass; Rico Cilliers; Poly Haven','files':files},indent=2))
print('R18 character authoring prepared; three PBR downloads verified against official MD5')
