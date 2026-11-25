"""Run in the reopened composed Blender scene, with the former mask and an output JSON as arguments."""
import hashlib,json,sys
from pathlib import Path
import bpy
import numpy as np
from runpy import run_path

here=Path(__file__).resolve().parent
game=here.parents[2]/"work/project/chongqing_godot_v05"
art=game/"assets/district_500"
oldmask,report=map(Path,sys.argv[sys.argv.index("--")+1:])
layout=json.loads((art/"layout.json").read_bytes())
group=json.loads((here/"mapped_group.json").read_bytes())
plan=run_path(str(here/"street_plan.py"))
street=plan["Streets"](plan["roads"](layout))
def pixels(path):
    image=bpy.data.images.load(str(path.resolve()),check_existing=False)
    image.colorspace_settings.name="Non-Color"
    width,height=image.size
    rgba=np.empty(width*height*4,np.float32);image.pixels.foreach_get(rgba)
    return rgba.reshape(height,width,4)
before=pixels(oldmask);after=pixels(art/"surface_mask.png")
def samples(pixels,points):
    points=np.array(points);height,width,_=pixels.shape
    coords=np.clip(((points+250)/500*np.array([width,height])).astype(int),[0,0],[width-1,height-1])
    return pixels[coords[:,1],coords[:,0]]
results=[]
for feature in group["buildings"]:
    name=feature["osm"].split("@")[0][1:]
    obj=bpy.context.scene.objects["COL_Shancheng_OSM_"+name]
    detail=bpy.context.scene.objects["Shancheng_Joinery_"+name]
    vertices=np.array([tuple(obj.matrix_world@v.co) for v in obj.data.vertices])
    err=[float(np.linalg.norm(vertices[:,:2]-q,axis=1).min()) for q in feature["points"]]
    assert max(err)<.002 and obj.visible_get() and detail.visible_get()
    results.append({"osm":feature["osm"],"footprint_corner_error_m":err,"structure_faces":len(obj.data.polygons),"joinery_faces":len(detail.data.polygons)})
points=[]
for p in layout["plots"]:
    for u in np.arange(-p["width"]*.5+.6,p["width"]*.5,.55):
        for distance in (2.4,3.0,3.6):
            points.append(plan["xy"](p,u,-p["depth"]*.5-distance))
old=samples(before,points);new=samples(after,points)
non_road=(np.maximum(old[:,0],new[:,0])<.15)
def count(q):return int(np.sum(q))
stats={"sampling":"Existing street-facing plots, every 0.55 m along the facade, at 2.4 / 3 / 3.6 m, max carriageway mask below .15. Counts of mask samples, not area.","samples":count(non_road),"former_paved":count((old[:,1]>.70)&non_road),"current_paved":count((new[:,1]>.70)&non_road)}
assert stats["current_paved"]>stats["former_paved"]
stairs=[]
for p in layout["plots"]:
    for end,points in plan["footprints"](p):
        margin=float(street.margin(points).min())
        stairs.append({"plot":p["plot_id"],"end":end,"clear_m":round(margin,3),"turned":end in p.get("kerb_stairs",{})})
assert min(row["clear_m"] for row in stairs)>0
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
record={"blender":bpy.app.version_string,"reopened":Path(bpy.data.filepath).name,"registered_houses":results,"street_front_ground":stats,"roadside_stairs":stairs,"park":"OSM 1499726225 excluded from mapped-footprint paving pass","inputs_sha256":{p.name:sha(p) for p in [here/"shancheng_lane.blend",art/"shancheng_lane.glb",art/"outer_district.glb",oldmask,art/"surface_mask.png"]}}
report.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("STREET BLOCKS",stats,len(stairs))
