"""Fit two nearby floating estate grates into native paving, preserving the earlier junction source."""
from pathlib import Path
import bpy, bmesh, json, math, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
work=here.parents[2]
project=work/'project/chongqing_godot_v05'
base=project/'assets/lane_connection_r24'
output=project/'assets/lane_inlets_r24'
output.mkdir(exist_ok=True)
sys.path.insert(0,str(here.parents[1]/'city_frame_11864101'))
from trim_paving import cut
plan=json.loads((base/'layout.json').read_text('utf8'))
objects=bpy.context.scene.objects
floor=objects['COL_Terrain_200m_pavement']
positions=[(38.133333,1.),(45.133333,-11.)]
vertices=[floor.matrix_world@v.co for v in floor.data.vertices]
surface=BVHTree.FromPolygons(vertices,[p.vertices[:] for p in floor.data.polygons])
def height(x,y):
    point=surface.ray_cast(Vector((x,y,30)),Vector((0,0,-1)),16)[0]
    if point is None:raise ValueError(('no paving',x,y))
    return float(point.z)

def choose_site(x,y):
    # Restrict relocation to an adjacent piece of the same sloping paving.
    # A rigid casting must fit one slope; a ridge that passes through the seat cannot support it.
    options=[]
    for ix in range(-5,6):
        for iy in range(-5,6):
            cx=x+ix*.08;cy=y+iy*.08
            samples=[(cx+a*.235,cy+b*.155) for a in (-1,-.5,0,.5,1) for b in (-1,-.5,0,.5,1)]
            z=height(cx,cy)
            sx=(height(cx+.235,cy)-height(cx-.235,cy))/.47
            sy=(height(cx,cy+.155)-height(cx,cy-.155))/.31
            deviation=max(abs(height(px,py)-(z+sx*(px-cx)+sy*(py-cy))) for px,py in samples)
            if deviation<.0015:options.append((math.hypot(cx-x,cy-y),deviation,cx,cy,z,sx,sy))
    if not options:raise ValueError(('no planar seat',x,y))
    return min(options)

def remove_old(name):
    obj=objects[name]
    bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world)
    remaining=set(bm.verts);dead=[]
    while remaining:
        group=[remaining.pop()]
        for v in group:
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in remaining:
                    remaining.remove(other);group.append(other)
        p=sum((v.co for v in group),Vector())/len(group)
        if any(abs(p.x-x)<.204 and abs(p.y-y)<.15 for x,y in positions):dead.append(group)
    assert len(dead)==(14 if name.endswith('aluminium') else 2),(name,len(dead))
    bmesh.ops.delete(bm,geom=[v for g in dead for v in g],context='VERTS')
    bm.transform(obj.matrix_world.inverted());bm.to_mesh(obj.data);bm.free();obj.data.update()

for key in ['Street_small_furniture_dark','Street_small_furniture_aluminium']:remove_old(key)
# Use the same cast frame, radii and cross bearers as the reference. Remove the old
# seat's pitch from each vertex and install the complete casting in the surveyed plane.
rim=[Vector((x,-z,y)) for x,y,z in plan['drain_rim']]
u=Vector((rim[1].x-rim[0].x,rim[1].y-rim[0].y)).normalized()
v=Vector((rim[3].x-rim[0].x,rim[3].y-rim[0].y)).normalized()
origin=(rim[0]+rim[1]+rim[2]+rim[3])*.25
names=['COL_East17_IronGrate','East17_GrateBearers','East17_GullyBed']
donors={n:objects[n].data.copy() for n in names}
sites=[]
for x,y in positions:
    shift,error,cx,cy,z,sx,sy=choose_site(x,y)
    corners=[Vector((cx+a,cy+b,z+sx*a+sy*b)) for a,b in [(-.235,-.155),(.235,-.155),(.235,.155),(-.235,.155)]]
    assert cut(floor,[(Vector((cx,cy,z)),corners)])>0
    for name in names:
        obj=objects[name]
        clone=donors[name].copy()
        for vertex in clone.vertices:
            pt=vertex.co;delta=Vector((pt.x-origin.x,pt.y-origin.y))
            a=delta.dot(u);b=delta.dot(v)
            fx=a/.47+.5;fy=b/.31+.5
            old_z=(1-fy)*((1-fx)*rim[0].z+fx*rim[1].z)+fy*((1-fx)*rim[3].z+fx*rim[2].z)
            vertex.co=(cx+a,cy+b,z+sx*a+sy*b+(pt.z-old_z))
        bm=bmesh.new();bm.from_mesh(obj.data);bm.from_mesh(clone);bm.to_mesh(obj.data);bm.free()
        obj.data.update();bpy.data.meshes.remove(clone)
    sites.append({'original_xy':[x,y],'centre':[cx,z,-cy],'slope':[sx,sy],'seat_max_error_m':error,'shift_m':shift,
                  'corners':[[p.x,p.z,-p.y] for p in corners], 'original_bar_gap_m':next(r for r in json.loads((here.parent/'legacy_grate_contacts.json').read_text('utf8'))['sites'] if abs(r['position'][0]-x)<.001 and abs(r['position'][2]+y)<.001)['bar_top_above_collision_max_m']})
for mesh in donors.values():bpy.data.meshes.remove(mesh)
(output/'inlets.json').write_text(json.dumps(sites,indent=2),'utf8')
bpy.ops.object.select_all(action='DESELECT')
for n in plan['source_nodes']+plan['new_nodes']:objects[n].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(output/'junction.glb'),export_format='GLB',use_selection=True,export_animations=False,export_image_format='NONE')
bpy.context.scene['street_revision']='R24 build 17b, the east alley and its three fitted drain seats'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_inlets.blend'),compress=True,relative_remap=True)
print('EAST17B_INLETS',sites)
