"""Reopen the editable source, inspect condenser mount contact and the exported floor colours."""
import json,os,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bpy

here=Path(__file__).resolve().parent
game=here.parents[1]/"project/chongqing_godot_v05/assets/district_500"
layout=json.loads((game/"layout.json").read_text(encoding="utf-8"))
assert Path(bpy.data.filepath).name=="outer_district.blend"
def tree(obj):
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[f.vertices[:] for f in obj.data.polygons])
mounts=[];bad=[];foot_gaps=[];units=0
for plot in layout["plots"]:
    shell=tree(bpy.data.objects["COL_Outer500_Frame_%02d"%plot["plot_id"]])
    for spec in plot["facade_work"]["condensers"]:
        obj=bpy.data.objects["Outer500_Condenser_%02d_%02d"%(plot["plot_id"],spec["floor"])]
        body=tree(obj);units+=1
        wide=.76+spec["template"]*.055;high=.51+spec["template"]*.025
        for sign in (-1,1):
            # Each steel wall foot overlaps the shell by 7 mm. Compare actual surfaces.
            pt=obj.matrix_world@Vector((sign*wide*.33,-.094,-high/2+.10))
            axis=(obj.matrix_world.to_3x3()@Vector((0,1,0))).normalized()
            wall=shell.ray_cast(pt,axis,.16)[0];end=body.ray_cast(pt+axis*.145,-axis,.10)[0]
            if wall is None or end is None:bad.append([obj.name,sign,"wall"]);continue
            signed=(end-wall).dot(axis);mounts.append(signed)
            if not -.002<=signed<=.015:bad.append([obj.name,sign,"mount",signed])
            # The foot pad and the bottom of the cabinet meet at the same support plane.
            p=obj.matrix_world@Vector((sign*wide*.33,-.28,-high/2-.017))
            seat=body.ray_cast(p,Vector((0,0,1)),.04)[0]
            if seat is None:bad.append([obj.name,sign,"pad"]);continue
            gap=seat.z-(obj.location.z-high/2);foot_gaps.append(gap)
            if abs(gap)>.004:bad.append([obj.name,sign,"pad",gap])
with (game/"outer_district.glb").open("rb") as f:
    f.seek(12);n,kind=struct.unpack("<II",f.read(8));doc=json.loads(f.read(n))
floors=[p for mesh in doc["meshes"] if mesh["name"].startswith("Outer500_InteriorFloor_") for p in mesh["primitives"]]
assert floors and all("COLOR_0" in p["attributes"] and "baseColorTexture" in doc["materials"][p["material"]]["pbrMetallicRoughness"] for p in floors)
record={"blender":bpy.app.version_string,"condensers":units,"wall_brackets":len(mounts),
        "mount_overlap_min_max_m":[min(mounts),max(mounts)],"foot_pad_samples":len(foot_gaps),
        "max_measured_foot_gap_m":max(map(abs,foot_gaps)) if foot_gaps else None,"failures":bad,
        "exported_floor_primitives_with_colour_and_texture":len(floors),"contact_bake":layout["floor_contact_bake"],
        "pierced_upper_windows":sum(p["facade_work"]["windows"] for p in layout["plots"]),
        "projecting_balconies":sum(p["facade_work"]["clipped_balconies"] for p in layout["plots"]),
        "enclosed_balconies":sum(p["facade_work"]["enclosed_galleries"] for p in layout["plots"]),
        "service_recesses":[p["facade_work"]["retaining_access"] for p in layout["plots"] if "retaining_access" in p["facade_work"]]}
out=Path(os.environ["CQ_QA_DIR"]);(out/"architecture_source.json").write_text(json.dumps(record,indent=2)+"\n")
print("ARCHITECTURE_SOURCE",units,len(mounts),len(bad));assert not bad,bad[:5]
