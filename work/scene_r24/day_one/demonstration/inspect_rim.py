from pathlib import Path
import bpy,bmesh
g=Path(__file__).resolve().parents[3]/'project/chongqing_godot_v05'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(g/'assets/vehicles/scooter_r18.glb'))
mesh=bpy.data.objects['Scooter_Body_rubber'].data
bm=bmesh.new();bm.from_mesh(mesh)
pending=set(bm.verts)
while pending:
    group={pending.pop()};active=list(group)
    while active:
        for e in active.pop().link_edges:
            for v in e.verts:
                if v in pending: pending.remove(v);group.add(v);active.append(v)
    mi=[min(v.co[i] for v in group) for i in range(3)]
    ma=[max(v.co[i] for v in group) for i in range(3)]
    if mi[1]<-.30 and ma[2]>.80:print('BOX_RUBBER',tuple(round(x,3) for x in mi),tuple(round(x,3) for x in ma))
bm.free()
