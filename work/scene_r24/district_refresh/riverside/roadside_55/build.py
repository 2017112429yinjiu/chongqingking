"""Extend the verified Changbin Road shoulder along old plot 55."""
import json
import os
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
R24=HERE.parents[2]
sys.path[:0]=[str(R24/"district_refresh/street_groups"),str(R24/"district_500")]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, read
from riverside import bounds, make_strip, material, terrain_faces


def main(out):
    field=read(HERE/"field.json")
    west=read(ASSETS/"west-ramp.json")["playground"]["street_access"]
    west_shoulder=west["shoulder_east_north"]
    x0,y0=west_shoulder[-1]
    # Keep the exact start and alignment of the accepted park-side sidewalk.
    q=Vector(west_shoulder[-2])
    axis=(Vector((x0,y0))-q).normalized()
    normal=Vector((axis.y,-axis.x))
    start=Vector(west_shoulder[-3])-axis*1.05
    end=Vector((x0,y0))+axis*18.4
    length=(end-start).length
    terrain_mesh=terrain()
    pieces=list(terrain_faces())
    former_entry=bpy.context.scene.objects["COL_WestPlayground_GradedSurfaces"]
    access_points=[former_entry.matrix_world @ v.co for v in former_entry.data.vertices]
    access_faces=[list(poly.vertices) for poly in former_entry.data.polygons if poly.normal.z>.83]
    approach=BVHTree.FromPolygons(access_points,access_faces)
    fitted_approach=[[access_points[v] for v in face] for face in access_faces]
    pieces.append((bounds(access_points),[(bounds(face),face) for face in fitted_approach]))
    tints={
        "flags":("Changbin55 grey footway flags",(.72,.76,.78),"stone_floor_diff_2k.jpg"),
        "asphalt":("Changbin55 weathered road shoulder",(.64,.65,.66),"asphalt_02_diff_1k.jpg"),
        "kerb":("Changbin55 ash kerb blocks",(.75,.76,.72),"concrete_floor_worn_001_diff_2k.jpg"),
    }
    mats={key:material(*data) for key,data in tints.items()}

    def make(name,c,width,mat,height):
        shape=make_strip({"id":name,"points":[list(start+c*normal),list(end+c*normal)],
                          "width_m":width,"finish":1,"raise_m":height},pieces,[mat,mat,mat])
        shape.name=name
        return shape

    path=make("COL_Changbin55_PublicShoulder",0.,1.62,mats["flags"],.032)
    # Reuse the mapped carriageway. The low stone curb separates the new
    # pedestrian band from the existing travelled lane.
    new_road_center=make("COL_Changbin55_AsphaltLaneEdge",-2.47,2.75,mats["asphalt"],.018)

    def land(point):
        origin=Vector((*point,90.))
        down=Vector((0,0,-1))
        levels=[hit.z for surface in (terrain_mesh,approach)
                if (hit:=surface.ray_cast(origin,down,130.)[0]) is not None]
        if not levels:
            raise ValueError(f"Missing existing physical ground at {tuple(point)}")
        return max(levels)

    curb=Mesh("COL_Changbin55_CurbBlocks")
    for i in range(50):
        a=start+axis*(i*length/50.)
        b=start+axis*((i+1)*length/50.)
        edge=[a-normal*.815,b-normal*.815,b-normal*1.035,a-normal*1.035]
        low=[(*p,land(p)+.022) for p in edge]
        curb.solid(low,[(x,y,z+.073) for x,y,z in low],mats["kerb"])
    seam_finish=Mesh("Changbin55_StaggeredGreyJoints")
    mortar=bpy.data.materials.new("Fine dark Changbin paver joints")
    mortar.diffuse_color=(.200,.213,.205,1.)
    for i in range(1,48):
        a=start+axis*(i*.51)
        for j in range(3):
            p=a+normal*(-.68+j*.48)+axis*(.12 if j%2 else 0.)
            q=p+normal*.47
            r=p+axis*.012
            s=q+axis*.012
            seam_finish.face([(*q,land(q)+.035),(*s,land(s)+.035),(*r,land(r)+.035),(*p,land(p)+.035)],mortar)

    earlier=runpy.run_path(str(HERE.parent/"east_bend/build.py"))
    common=runpy.run_path(str(R24/"district_refresh/street_groups/panda_15_17/build.py"))
    replacements,retired,counts=common["retire"](earlier,(55,),HERE/"ownership.json")
    parent=read(ASSETS/"nanqu-04-06-51.json")["borrowed_materials"]
    slots={}
    for obj in replacements:
        names={m.name for m in obj.data.materials}
        slots[obj.name]={alias:label for alias,label in parent.get(obj.name,{}).items() if alias in names}
    additions=[path,curb.save(),new_road_center,seam_finish.save()]
    walk=[]
    origin=Vector((x0,y0))
    for pos in [Vector(west_shoulder[-3]),Vector(west_shoulder[-2]),origin+.6*axis,
                origin+4.5*axis,origin+8.6*axis,origin+13.5*axis,origin+17.3*axis]:
        walk.append([*pos,land(pos)+.032])
    for obj in list(bpy.data.objects):
        if obj not in set((*replacements,*additions)):
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    source=Path(os.environ.get("CQ_ROADSIDE55_SOURCE",out/"changbin-55.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=True)
    bpy.ops.export_scene.gltf(filepath=str(out/"changbin-55.glb"),export_format="GLB",
                              export_image_format="NONE",export_cameras=False,export_lights=False)
    values={"retired_plots":[55],"retired_objects":retired,"replacement_meshes":[o.name for o in replacements],
            "new_meshes":[o.name for o in additions],"removed_face_counts":counts,
            "borrowed_materials":slots,"walk":walk,"osm_way":west["osm_way"],"old_outline":field["55_old_outline_en"],
            "road_line_en":west["registered_segment_east_north"],
            "lane_offset_m":west["shoulder_centre_offset_m"]-2.47,
            "surface_textures":{name:f"res://assets/chongqing_district_{file}" for name,_,file in tints.values()}}
    (out/"changbin-55.json").write_text(json.dumps(values,indent=2)+"\n")
    print("CQ_CHANGBIN55",counts)


if __name__=="__main__":
    main(Path(sys.argv[-1]).resolve())
