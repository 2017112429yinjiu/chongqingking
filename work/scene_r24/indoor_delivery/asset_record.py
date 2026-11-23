"""Record the exact local artwork used on this playable residential passage."""
from pathlib import Path
import hashlib,json
here=Path(__file__).resolve().parent
work=here.parents[1]
game=work/'project/chongqing_godot_v05'
def record(path):
    with path.open('rb') as f:
        digest=hashlib.sha256()
        for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    return {'file':path.relative_to(work).as_posix(),'sha256':digest.hexdigest()}
items=[]
for name,maker in [('plastered_wall_04','Rob Tuytel'),('concrete_floor_worn_001','Dimitrios Savva, Rico Cilliers'),('rusty_painted_metal','Amal Kumar')]:
    spec='1k' if name=='plastered_wall_04' else '2k'
    items.append({'source':'https://polyhaven.com/a/'+name,'author':maker,'licence':'CC0-1.0','licence_url':'https://polyhaven.com/license','credit_required':False,'use':'Existing local colour and OpenGL normal maps reused on metre-scaled UVs with local colour adjustment.', 'files':[record(game/f'assets/chongqing_district_{name}_{suffix}_{spec}.jpg') for suffix in ('diff','nor_gl')]})
items.append({'source':'https://polyhaven.com/a/sandstone_cracks','author':'Rob Tuytel','licence':'CC0-1.0','credit_required':False,'use':'Existing colour-adjusted city stone and scan normals on the exposed gallery and its steps.','files':[record(game/'assets/district_r21'/n) for n in ('terraces_washed_sandstone.jpg','terraces_sandstone_cracks_nor_gl_2k.jpg','provenance.json')]})
data={'authoring':'Original local mesh cuts, two doors, workshop fittings, corridor, slab and stepped gallery. The original A04 entry leaf, frame and hardware are moved together. No new external models acquired.','source':record(here/'city_and_unit.blend'),'runtime':[record(game/'assets/indoor_delivery'/name) for name in ('unit.glb','layout.json','interior_wall_faces.res')],'reused_materials':items,'notices':{'art':record(game/'assets/district_age/wall_prints.png'),'maker':'District project, original fictional text and layout from build 20','font':'Existing renamed Noto Sans CJK SC subset, SIL OFL 1.1; retain the licence and font notices.', 'font_files':[record(game/'assets/fonts'/n) for n in ['first_shift.otf','first_shift_sources.json','R20_OFL.txt']]},'existing_district':'Existing street base and HUD map attribution preserved. The indoor passage and routes are authored game geometry.'}
(here/'assets.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
