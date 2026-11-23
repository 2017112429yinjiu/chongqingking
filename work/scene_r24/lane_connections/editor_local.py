"""Splice the same junction into editor-only proxies while preserving the original scene elsewhere."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
here=Path(__file__).resolve().parent
out=here.parents[1]/'project/chongqing_godot_v05/assets/lane_connection_r24'
if '--' in sys.argv:
    out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(here/'editor_base.glb'))
original={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
for i,o in enumerate(original.values()):o.name='OriginalDrawing'+str(i)
bpy.ops.import_scene.gltf(filepath=str(out/'junction.glb'))
boxes=[(23.5,37.5,5.65,20.9)]
if (out/'inlets.json').is_file():
    for site in json.loads((out/'inlets.json').read_text('utf8')):
        x,_,neg_y=site['centre'];y=-neg_y;boxes.append((x-1.1,x+1.1,y-1.1,y+1.1))
def crop(obj,keep_inside):
    bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world)
    for xmin,xmax,ymin,ymax in boxes:
        def near(f):
            pts=[v.co for v in f.verts]
            return not(all(v.x<xmin-.001 for v in pts) or all(v.x>xmax+.001 for v in pts) or all(v.y<ymin-.001 for v in pts) or all(v.y>ymax+.001 for v in pts))
        faces=[f for f in bm.faces if near(f)]
        for axis,d in [(0,xmin),(0,xmax),(1,ymin),(1,ymax)]:
            use=[f for f in faces if f.is_valid and min(v.co[axis] for v in f.verts)<d-1e-6 and max(v.co[axis] for v in f.verts)>d+1e-6]
            if not use:continue
            geom=set(use)
            for f in use:geom.update(f.verts);geom.update(f.edges)
            at=Vector((0,0,0));at[axis]=d;n=Vector((0,0,0));n[axis]=1.
            change=bmesh.ops.bisect_plane(bm,geom=list(geom),plane_co=at,plane_no=n,dist=.000001)
            faces=list(set([f for f in faces if f.is_valid]+[f for f in change['geom'] if isinstance(f,bmesh.types.BMFace) and f.is_valid]))
    remove=[]
    for face in bm.faces:
        p=face.calc_center_median()
        inside=any(xmin-.000001<=p.x<=xmax+.000001 and ymin-.000001<=p.y<=ymax+.000001 for xmin,xmax,ymin,ymax in boxes)
        if inside!=keep_inside:remove.append(face)
    bmesh.ops.delete(bm,geom=remove,context='FACES')
    bm.transform(obj.matrix_world.inverted());bm.to_mesh(obj.data);bm.free();obj.data.update()
results=[]
for name,outer in original.items():
    donor=bpy.context.scene.objects.get(name)
    assert donor
    crop(outer,False);crop(donor,True)
    bpy.ops.object.select_all(action='DESELECT');outer.select_set(True);donor.select_set(True);bpy.context.view_layer.objects.active=outer
    bpy.ops.object.join();outer.name='Preview_'+name;results.append(outer)
bpy.ops.object.select_all(action='DESELECT')
for obj in results:obj.select_set(True)
(out/'editor').mkdir(exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(out/'editor/openings.glb'),use_selection=True,export_animations=False,export_image_format='NONE')
print('EDITOR17_LOCAL',len(results),[o.name for o in results])
