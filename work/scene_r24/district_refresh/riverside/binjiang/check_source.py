"""Reopen the authored increment and check the same public paving in the combination."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
assets=HERE.parents[3]/"project/chongqing_godot_v05/assets/district_500"
meta=json.loads((assets/"binjiang-70-73.json").read_text())
objects=bpy.context.scene.objects
assembly=Path(bpy.data.filepath).name=="city_and_outer.local.blend"
names=meta["new_meshes"]+meta["replacement_meshes"]
assert all(objects.get(name) and objects[name].type=="MESH" for name in names)
assert all(objects[name].data.uv_layers.active for name in names)
assert all(objects.get(name) is None for name in meta["retired_objects"])
boundaries={}
for name in ("Binjiang_Tower_1128648941","Binjiang_Adjacent_Tower_704006726",
             "COL_Binjiang_1128648941_Podium","COL_Binjiang_704006726_Curved_Podium"):
    ob=objects[name]
    vertices=[ob.matrix_world@v.co for v in ob.data.vertices]
    boundaries[name]={"min":[min(p[d] for p in vertices) for d in range(3)],
                      "max":[max(p[d] for p in vertices) for d in range(3)],"materials":[mat.name for mat in ob.data.materials],
                      "faces":len(ob.data.polygons)}
paths=[]
for plot,plan in meta["public_routes"].items():
    ob=objects["COL_Binjiang_Walk_"+plot]
    verts=[ob.matrix_world@v.co for v in ob.data.vertices]
    mesh=BVHTree.FromPolygons(verts,[list(f.vertices) for f in ob.data.polygons])
    for e,n in plan["stations"]:
        for x in (-.53,0.,.53):
            hit,normal,_,_=mesh.ray_cast(Vector((e+.017+x,n+.015,40.)),Vector((0,0,-1)),70.)
            assert hit is not None and normal.z>.78,(plot,e,n,x,hit,normal)
            paths.append([plot,*hit,normal.z])
if assembly:
    assert objects.get("COL_EastRoad_PublicWalk") and objects.get("COL_EastRoad_1256840008")
    assert objects.get("COL_Riverside_62_registered_body") and objects.get("COL_Outer500_RepairCourt")
    assert all(objects[name].library and objects[name].library.filepath.endswith("binjiang-70-73.blend") for name in names)
print("CQ_BINJIANG_SOURCE",json.dumps({"version":bpy.app.version_string,"assembly":assembly,"buildings":boundaries,
                                      "paving_points_checked":len(paths),"paving":paths,"original_faces_retired":meta["removed_face_counts"]}))
