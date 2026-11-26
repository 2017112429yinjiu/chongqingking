"""Reopen the candidate Blender library and compare its actual meshes with the plan."""
from pathlib import Path
from runpy import run_path
import bpy, json, os
import numpy as np

here=Path(__file__).resolve().parent
spec=json.loads((here/"registered.json").read_bytes())
game=here.parents[2]/"work/project/chongqing_godot_v05"
layout=json.loads((game/"assets/district_500/historic_courts.json").read_bytes())
plots=json.loads((game/"assets/district_500/layout.json").read_bytes())
records=[]
for source,asset in zip(spec["buildings"],layout["buildings"]):
    label=source["id"]
    shell=bpy.data.objects["COL_Court_"+label]
    frame=bpy.data.objects["COL_Court_Structure_"+label]
    detail=bpy.data.objects["Court_Millwork_"+label]
    ring=np.array(source["points"])
    vertices=np.array([shell.matrix_world @ v.co for v in shell.data.vertices])
    # The decorative string courses, soffits and eaves project beyond these walls.
    errors=[float(np.linalg.norm(vertices[:,:2]-q,axis=1).min()) for q in ring]
    struct=np.array([frame.matrix_world @ v.co for v in frame.data.vertices])
    levels=np.unique(np.round(struct[:,2],2))
    report={"id":label,"registered_corner_deviation_in_mesh_m":errors,
            "footprint_area_m2":round(abs(float(np.dot(ring[:,0],np.roll(ring[:,1],-1))-np.dot(ring[:,1],np.roll(ring[:,0],-1))))/2,2),
            "min_structural_z":float(levels[0]),"max_structural_z":float(levels[-1]),"recorded_floor_z":asset["floor"],
            "structural_faces":len(frame.data.polygons),"openings_and_trim_faces":len(detail.data.polygons),
            "packed_texture_images":sorted(im.name for im in bpy.data.images if im.packed_file)}
    assert max(errors)<.12 and len(frame.data.polygons)>35 and abs(levels[0]-asset["floor"])<.23
    records.append(report)
remaining={v["plot_id"] for v in plots["plots"]}
registered={v["plot_id"] for v in plots["plots"] if v.get("registered_site")}
assert registered=={0} and len(remaining-registered)==70 and set(plots["retired_for_historic_courts"])=={3,5,47,48}
assert bpy.data.objects.get("Court_Jinma_painted_name")
# Sample the actual saved mesh at each foot, against the finish in the saved
# scene. A shared centre elevation previously left chair feet hanging on slopes.
from mathutils.bvhtree import BVHTree
deps=bpy.context.evaluated_depsgraph_get()
apron=BVHTree.FromObject(bpy.data.objects["COL_Court_Jinma_Apron"],deps)
finish=BVHTree.FromObject(bpy.data.objects["Court_Jinma_Flagstone"],deps)
school=next(row for row in layout["buildings"] if row["id"]=="jinma_classrooms")
a,b,c,d=np.asarray(school["ring"])
length=np.linalg.norm(b-a)
depth=(np.linalg.norm(d-a)+np.linalg.norm(c-b))/2
def xy(x,y):
    f,g=x/length,y/depth
    return ((1.-f)*a+f*b)*(1.-g)+((1.-f)*d+f*c)*g
def ground(point,tree):
    hit=tree.ray_cast((*point,school["floor"]+3),(0,0,-1),8)[0]
    return float(hit.z) if hit is not None else None
fittings=bpy.data.objects["Court_Fittings_jinma_classrooms"]
vertices=np.array([fittings.matrix_world @ v.co for v in fittings.data.vertices])
ux,uy=length*.83,-2.6
feet=[(ux+dx,uy+dy) for dx in (-.33,.33) for dy in (-.25,.25)]
feet+=[(ux+side*.97+dx*.19,uy+dy) for side in (-1,1) for dy in (-.18,.18) for dx in (-1,1)]
contacts=[]
for x,y in feet:
    centre=xy(x,y)
    nearby=vertices[np.linalg.norm(vertices[:,:2]-centre,axis=1)<.065]
    actual=nearby[np.argmin(nearby[:,2])]
    surface=ground(actual[:2],finish)
    if surface is None:surface=ground(actual[:2],apron)
    error=float(actual[2]-surface)
    assert abs(error)<.045,(actual,error)
    contacts.append(round(error,4))
roots=[]
for i,tree in enumerate(layout["school_trees"],1):
    trunk=bpy.data.objects[f"Court_Jinma_Tree_{i}_0"]
    world=np.array([trunk.matrix_world @ v.co for v in trunk.data.vertices])
    base=world[world[:,2]<world[:,2].min()+.07]
    q=base[:,:2].mean(axis=0)
    gap=float(base[:,2].min()-ground(q,apron))
    assert -.10<=gap<=.01,(i,gap)
    roots.append({"centre":q.round(3).tolist(),"root_to_soil_m":round(gap,4)})
for name in ("Seating","Trunks","PlanterBases"):
    proxy=bpy.data.objects["COLH_Court_Jinma_"+name]
    assert proxy.hide_render and proxy.display_type=="WIRE"
forecourt={"root_contacts":roots,"table_and_chair_foot_gaps_m":contacts}
output=Path(os.environ["CQ_QA_DIR"])
output.mkdir(exist_ok=True,parents=True)
(output/"blender.json").write_text(json.dumps({"blender":bpy.app.version_string,"source":Path(bpy.data.filepath).name,"remaining":len(remaining-registered),"buildings":records,"forecourt":forecourt,"books":run_path(str(here/"library_books/audit.py"))["audit"]()},indent=2)+"\n",encoding="utf-8")
