"""Reopen the candidate Blender library and compare its actual meshes with the plan."""
from pathlib import Path
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
assert len(remaining)==71 and set(plots["retired_for_historic_courts"])=={3,5,47,48}
assert bpy.data.objects.get("Court_Jinma_painted_name")
output=Path(os.environ["CQ_QA_DIR"])
output.mkdir(exist_ok=True,parents=True)
(output/"blender.json").write_text(json.dumps({"blender":bpy.app.version_string,"source":Path(bpy.data.filepath).name,"remaining":len(remaining),"buildings":records},indent=2)+"\n",encoding="utf-8")
