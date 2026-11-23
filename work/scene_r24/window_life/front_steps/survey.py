"""Trace the visible ends of the main-street retaining ledges in the complete city."""
import json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[1] / "stair_neighborhood"))
from site_neighborhood import Surfaces, extent

closer = "--front" in sys.argv
manifest = json.loads(((here / "before" if closer else here.parent / "window_art_views") / "capture_manifest.json").read_text("utf8"))
view = next(row for row in manifest["captures"] if row["view"] == ("r24_market_steps_front" if closer else "r23_main_road"))
def blender(v):
    return Vector((v[0], -v[2], v[1]))
def game(v):
    return [round(float(x), 4) for x in (v.x, v.z, -v.y)]
eye = blender(view["position"])
forward = (blender(view["target"])-eye).normalized()
right = forward.cross(Vector((0, 0, 1))).normalized()
up = right.cross(forward).normalized()
fov = float(view.get("fov", 67.0))
structure = []
for obj in bpy.context.scene.objects:
    if obj.type != "MESH" or obj.hide_render:
        continue
    if any(word in obj.name.lower() for word in ("tree", "canopy", "rocketbox", "planting", "pedestrian", "traffic")):
        continue
    low, high = extent(obj)
    if all(low[i] < eye[i]+60 and high[i] > eye[i]-60 for i in range(3)):
        structure.append(obj)
surf = Surfaces(structure)
samples = []
pixels = [(688,389),(693,391),(696,392),(697,396),(703,398),(716,413),(716,418),(722,423),(730,421),(738,424),(715,433),(681,414),(708,401),(703,412),(681,401),(675,391),(682,392)]
if closer:
    pixels = [(350,340),(350,366),(425,381),(461,400),(465,421),(330,402),(910,338),(928,372),(971,371),(957,408),(787,342),(538,355),(641,432),(605,465)]
for x,y in pixels:
    aim = (forward + (right*((x+.5-640)/360) + up*((360-y-.5)/360))*math.tan(math.radians(fov)*.5)).normalized()
    hits = []
    for obj in structure:
        pt, normal, face, distance = surf.tree(obj).ray_cast(eye, aim, 60.)
        if pt is not None:
            hits.append((round(distance,4), obj.name, game(pt), game(normal), face))
    samples.append({"pixel":[x,y], "surfaces":sorted(hits)[:5]})
(here/("front_survey.json" if closer else "survey.json")).write_text(json.dumps({"camera":view["position"],"target":view["target"],"fov":fov,"pixels":samples},indent=2),"utf8")

if closer:
    obj = bpy.data.objects["COL_R24_MarketStairs_R24_step_stone"]
    data=[]
    for face in obj.data.polygons:
        corners=[obj.matrix_world @ obj.data.vertices[i].co for i in face.vertices]
        if face.normal.z > .96:
            data.append([[round(min(v[i] for v in corners),5),round(max(v[i] for v in corners),5)] for i in range(3)])
    (here/"step_bounds.json").write_text(json.dumps(data,indent=2),"utf8")
