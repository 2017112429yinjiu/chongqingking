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
def geometry(name):
    ob = objects[name]
    return [ob.matrix_world @ v.co for v in ob.data.vertices]

entry = objects["COL_Binjiang_Walk_72"]
flags = next(mat for mat in entry.data.materials if mat.name == "Binjiang Small grey street flags")
texture, = [node.image for node in flags.node_tree.nodes if node.type == "TEX_IMAGE"]
assert texture.packed_file and tuple(texture.size) == (512, 512)
paint = geometry("Binjiang_Entry72_CrossingPaint")
assert max(p.x for p in paint) - min(p.x for p in paint) > 4.7
assert max(p.y for p in paint) - min(p.y for p in paint) > 2.6
glass = geometry("COL_Binjiang_73_Continuous_Bowed_Glazing")
ribbon_bands = [(14.32, 16.71), (17.59, 19.93)]
for low,high in ribbon_bands:
    band = [p for p in glass if low-.001 < p.z < high+.001]
    assert max(p.x for p in band) - min(p.x for p in band) > 34.

site = json.loads((HERE/"site.json").read_text())
_,_,se,sw = map(Vector,site["ways"]["704006726"]["east_north"][:-1])
axis = (se-sw).normalized()
inward = Vector((-axis.y, axis.x))
ramps = geometry("COL_Binjiang_73_South_Visible_Ramp_Slabs")
front = [(round((p.xy-sw).dot(axis),3),round((p.xy-sw).dot(inward),3),round(p.z,3)) for p in ramps]
base = sorted({z for x,y,z in front if x==8.9 and y==1.49})
crest = sorted({z for x,y,z in front if x==31.4 and y==1.49})
assert len(base)==len(crest)==12 and all(abs(b-a-2.025)<.003 for a,b in zip(base,crest))
assert max(y for _,y,_ in front)-min(y for _,y,_ in front)>5.4

box = objects["COL_Binjiang_Entry_PlanterBorders"]
soil = objects["Binjiang_Entry_ContainedPlanting"]
def planter_top(obj, material):
    vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
    faces = [list(f.vertices) for f in obj.data.polygons
             if obj.data.materials[f.material_index].name == material]
    surface = BVHTree.FromPolygons(vertices,faces)
    return surface.ray_cast(Vector((115.252,-129.066,30.)),Vector((0,0,-1)),50.)[0]
enclosure = planter_top(box,"Binjiang textured stone base")
bed = planter_top(soil,"Binjiang Contained planter soil")
assert enclosure is not None and bed is not None and 0 < bed.z-enclosure.z < .08, (enclosure,bed)

if assembly:
    root=objects["Outer500_Plant_063"].matrix_world.translation
    assert (root.xy-Vector((115.252,-129.066))).length < .02 and abs(root.z-bed.z)<.28
    assert objects.get("COL_EastRoad_PublicWalk") and objects.get("COL_EastRoad_1256840008")
    assert objects.get("COL_Riverside_62_registered_body") and objects.get("COL_Outer500_RepairCourt")
    assert all(objects[name].library and objects[name].library.filepath.endswith("binjiang-70-73.blend") for name in names)
print("CQ_BINJIANG_SOURCE",json.dumps({"version":bpy.app.version_string,"assembly":assembly,"buildings":boundaries,
                                      "paving_points_checked":len(paths),"paving":paths,"original_faces_retired":meta["removed_face_counts"],
                                      "entry_detail":{"flag_module_m":[.40,2/6],"tree_bed_top_m":bed.z},
                                      "bowed_glass_bands_m":ribbon_bands,"garage":{"rise_m":round(crest[-1]-base[-1],3),
                                      "visible_slope_run_m":22.5,"physical_ramp_depth_m":5.42,"rising_levels":len(base)//2}}))
