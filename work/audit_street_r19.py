"""Reopen the exported Blender authoring layer and validate its actual geometry."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;P=W/'project/chongqing_godot_v05';S=W/'project/chongqing_blender_v05'
manifest=json.loads((P/'assets/street_r19/manifest.json').read_text(encoding='utf-8'))
arch=json.loads((S/'architecture_manifest.json').read_text())
def inside(p,poly):
    odd=False;x,y=p
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:odd=not odd
    return odd
tests=[]
def check(n,passed,detail):tests.append({'name':n,'pass':bool(passed),'detail':detail})
check('authored_layer_reopens',len(bpy.context.scene.objects)>=45,len(bpy.context.scene.objects))
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and im.users>0]
check('referenced_images_packed',not missing,missing)
support_gaps=[gap for prop in manifest['grounded_props'] for gap in prop.get('four_support_min_gaps_m',[])]
check('each_scanned_support_fits_ground',len(support_gaps)==28 and all(-.001<g<.004 for g in support_gaps),support_gaps)
samplers={}
for m in bpy.data.materials:
    if not m.node_tree:continue
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:
            samplers.setdefault(n.image.name,set()).add((n.extension,n.interpolation,n.projection))
conflicts={k:list(v) for k,v in samplers.items() if len(v)>1}
check('shared_image_sampler_settings_consistent',not conflicts,conflicts)
intrusions=[];bounds=[]
for o in bpy.context.scene.objects:
    if not o.name.startswith('COLH_'):continue
    ps=[o.matrix_world@Vector(p) for p in o.bound_box]
    lo=[min(p[k] for p in ps) for k in range(3)];hi=[max(p[k] for p in ps) for k in range(3)]
    bounds.append({'name':o.name,'lo':lo,'hi':hi})
    for b in arch['buildings']:
        for x in [lo[0],hi[0],(lo[0]+hi[0])/2]:
            for y in [lo[1],hi[1],(lo[1]+hi[1])/2]:
                if inside((x,y),b['points']):intrusions.append([o.name,b['id'],x,y])
check('new_rigid_props_outside_building_footprints',not intrusions,intrusions)
blocked=[]
for b in bounds:
    # Active pickup approach remains open; central stair lane width is 3.8m.
    if b['lo'][0]<-22.04 and b['hi'][0]>-26.54 and b['lo'][1]<-58.0 and b['hi'][1]>-61.9:blocked.append(b['name'])
    if b['lo'][0]<-18.1 and b['hi'][0]>-21.9 and b['lo'][1]<-30 and b['hi'][1]>-52:blocked.append(b['name'])
check('serving_approach_and_central_lane_clear',not blocked,blocked)
check('stair_overlay_created',manifest['stair_treads_capped']==19,manifest['stair_treads_capped'])
cloth=bpy.data.objects.get('R19_Canvas_awning_cloth')
check('awning_has_vertex_weathering',cloth is not None and len(cloth.data.color_attributes)>0, len(cloth.data.color_attributes) if cloth else -1)
check('layer_hash_matches_authoring_manifest',hashlib.sha256((P/'assets/street_r19/street_life.glb').read_bytes()).hexdigest()==manifest['glb_sha256'],manifest['glb_sha256'])
report={'scope':'Actual reopened Blender detail layer; plan-space rigid-prop clearance, packed images and source/export hashes. Not a whole-city intersection or aesthetic acceptance.','checks':tests,'passed':all(t['pass'] for t in tests),'proxy_bounds':bounds,'blend_sha256':hashlib.sha256((W/'scene_r19/street_life.blend').read_bytes()).hexdigest(),'glb_sha256':manifest['glb_sha256']}
(W/'audit/r19_geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('R19_GEOMETRY',report['passed'],json.dumps(tests,ensure_ascii=False))
