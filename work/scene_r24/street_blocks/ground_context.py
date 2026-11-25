"""Register existing peripheral scenery against the exported terrain skirt in Blender metres."""
import json,bpy
from pathlib import Path
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
game=here.parents[2]/"work/project/chongqing_godot_v05"
ring=bpy.data.objects["Outer500_Background_transition"]
ground=BVHTree.FromObject(ring,bpy.context.evaluated_depsgraph_get())
def sample(x,north):
    v=ground.ray_cast((x,north,120),(0,0,-1))[0]
    return round(v.z,4) if v is not None else None
canopy=json.loads((game/"assets/district_r21/layout.json").read_bytes())["outer_canopy"]
supports={}
for i,t in enumerate(canopy):
    x,former,z=t["position"]
    if max(abs(x),abs(z))<=250:continue
    level=sample(x,-z)
    if level is not None:supports[str(i)]=level
a,b=json.loads((here.parents[1]/"scene_r21/district_rays.json").read_bytes())["meshes"]["Context_authored_4_0_plaster_ochre"]["bounds"]
land=[sample(x,y) for x in (a[0],(a[0]+b[0])*.5,b[0]) for y in (a[1],(a[1]+b[1])*.5,b[1])]
level=min(v for v in land if v is not None)
data={"outer_canopy_y":supports,"context_prefixes":["Context_authored_4_0_","Context_v04_detail_49400_"],"context_shift_z":round(level-a[2]-.12,4),"context_base_before":a[2],"context_skirt_samples":land}
(game/"assets/district_500/edge_ground.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
print("EDGE GROUND",len(supports),data["context_shift_z"])
