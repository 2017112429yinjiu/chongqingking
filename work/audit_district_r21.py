"""Reopen the saved city and audit its installed geometry independently."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parent;S=W/'scene_r21';P=W/'project/chongqing_godot_v05'
D=P/'verification_r21/current';D.mkdir(parents=True,exist_ok=True)
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
layout=json.loads((P/'assets/district_r21/layout.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(S/'chongqing_district.blend'))
stat={'city_sha256':sha(S/'chongqing_district.blend'),'kit_sha256':sha(S/'district_environment.blend'),
      'objects':len(bpy.context.scene.objects),'packed_images':sum(bool(i.packed_file) for i in bpy.data.images)}
assert stat['kit_sha256']==layout['kit_sha256']
missing=[i.name for i in bpy.data.images if i.users and i.filepath and not i.packed_file]
assert not missing,missing
col=bpy.data.collections['R21_District_environment']
stat['authored_objects']=len(col.objects)
stat['atlas_preview_cards']=len(col.objects['R21_Exterior_canopy_authoring'].data.polygons)
assert stat['atlas_preview_cards']==len(layout['outer_canopy'])
stone=[]
for flight in layout['stonework']:
    base=bpy.data.objects[flight['structure']]
    bvh=BVHTree.FromPolygons([base.matrix_world@v.co for v in base.data.vertices],[list(p.vertices) for p in base.data.polygons])
    piece=col.objects[flight['mesh']]
    errors=[]
    for poly in piece.data.polygons:
        if len(poly.vertices)!=8 or poly.normal.z<.99:continue
        p=piece.matrix_world@poly.center
        hit=bvh.ray_cast(p+Vector((0,0,.03)),Vector((0,0,-1)),.14)[0]
        assert hit is not None,(flight['mesh'],p)
        errors.append(p.z-hit.z)
    assert len(errors)==flight['individual_stones'] and min(errors)>.0029 and max(errors)<.0075,(len(errors),min(errors),max(errors))
    stone.append({'source':base.name,'tested_stone_centres':len(errors),'clearance_m':[min(errors),max(errors)]})
stat['stair_physical_support']=stone
col.hide_viewport=True;bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
roof_hits=[]
for spec in layout['rooftops']:
    x,z,my=spec['position'];p=Vector((x,-my,z))
    ok,where,_,_,o,_=bpy.context.scene.ray_cast(dg,p+Vector((0,0,.11)),Vector((0,0,-1)),distance=.25)
    roof_hits.append({'source':spec['donor'],'first_hit':o.name if ok else None,'delta_m':where.z-z if ok else None})
stat['roof_hits']=roof_hits
assert all(v['delta_m'] is not None and abs(v['delta_m'])<.07 for v in roof_hits),[v for v in roof_hits if v['delta_m'] is None or abs(v['delta_m'])>=.07]
stat['runtime_glb_sha256']=sha(P/'assets/district_r21/terraces.glb')
assert stat['runtime_glb_sha256']==layout['terraces_glb_sha256']
stat['marked_wall_sockets']=sum(len(r['four_socket_depths_m']) for r in layout['facades'])
stat['unpacked_images']=missing
bpy.ops.wm.open_mainfile(filepath=str(S/'district_environment.blend'))
stat['standalone_kit_objects']=len(bpy.context.scene.objects)
assert stat['standalone_kit_objects']==stat['authored_objects'],stat
(D/'blender_reopen.json').write_text(json.dumps(stat,indent=2,ensure_ascii=False),encoding='utf8')
print('REOPENED',stat['objects'],stat['packed_images'],stone,len(roof_hits))
