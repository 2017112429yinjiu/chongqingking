"""Independent public edges around Zhongxing Road and the west public planter."""
from math import ceil,cos,pi,sin
from pathlib import Path
import json
import os
import runpy
import sys

import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
common=runpy.run_path(str(HERE.parent/"north_edges/build.py"))
Edge,Mesh,material,paint,box=(common[key] for key in ("Edge","Mesh","material","tint","box"))


def finishes():
    mats,textures={},{}
    for key,label,color,texture in (
        ("walk","Zhongxing public grey flags",(.79,.79,.74),"stone_floor_diff_2k.jpg"),
        ("kerb","Zhongxing public light curb",(.75,.75,.70),"concrete_floor_worn_001_diff_2k.jpg"),
        ("plaza","Zhongxing planter brushed grey honey stone",(.69,.64,.57),"stone_wall_05_diff_2k.jpg"),
        ("soil","Zhongxing planter local warm-green groundcover",(.36,.48,.26),"leaf_scattered_gravel_diff_2k.jpg"),
        ("brick","Zhongxing footway dark red brick",(.77,.60,.49),"brick_wall_08_diff_2k.jpg"),
        ("timber","Zhongxing dark red aged canopy timbers",(.44,.21,.17),"wood_table_worn_diff_2k.jpg"),
        ("skin","Zhongxing pale wall stained stucco",(.81,.80,.73),"concrete_wall_006_diff_2k.jpg"),
    ):
        mats[key]=material(label,color,texture)
        textures[label]=f"res://assets/chongqing_district_{texture}"
    for key, label, value in (
        ("royal","Zhongxing blue road rail posts",(.115,.315,.53)),
        ("pale","Zhongxing offwhite tubular painted rail",(.83,.85,.83)),
        ("shade","Zhongxing recessed street-side brick bays",(.10,.095,.079)),
        ("mural_green","Zhongxing muted green street mural backing",(.20,.43,.27)),
        ("mural_blue","Zhongxing muted blue street mural backing",(.15,.36,.54)),
    ):
        mats[key]=paint(label,value)
    return mats,textures


def plant_plaza(spec,terrain,m):
    planter=Mesh("COL_Zhongxing22_RoundedStonePlanter")
    greenery=Mesh("Zhongxing22_RecessedPlanterGround")
    center=Vector(spec["center"])
    rx,ry=spec["radii"]
    top=terrain.ray_cast(Vector((*center,90.)),Vector((0.,0.,-1.)),100.)[0].z+.65

    def ring(angle,scale=1.):
        return center+Vector((rx*cos(angle),ry*sin(angle)))*scale

    def bottom(p):
        return terrain.ray_cast(Vector((*p,90.)),Vector((0.,0.,-1.)),100.)[0].z-.25

    for k in range(48):
        a,b=2*pi*k/48,2*pi*(k+1)/48
        u,v,w,x=ring(a),ring(b),ring(b,.95),ring(a,.95)
        planter.face([(*u,bottom(u)),(*v,bottom(v)),(*v,top),(*u,top)],m["plaza"])
        planter.face([(*u,top),(*v,top),(*w,top+.10),(*x,top+.10)],m["kerb"])
        greenery.face([(*center,top+.031),(*x,top+.031),(*w,top+.031)],m["soil"])
    tree_pins=[{"donor":"Outer500_Plant_036","name":"Zhongxing22_CourtyardTreeA","enu":[center.x-1.70,center.y,top+.04],"scale":.87,"yaw":.53},
               {"donor":"Outer500_Plant_036","name":"Zhongxing22_CourtyardTreeB","enu":[center.x+1.52,center.y+.55,top+.04],"scale":.66,"yaw":2.03}]
    return [planter.save(),greenery.save()],tree_pins


def roadside_guard(edge,code,left,stop,m):
    rails=Mesh(f"COL_Zhongxing{code}_WhiteAndBlueRail")
    a=.49
    while a<stop-.40:
        b=min(a+1.52,stop)
        for y in (.155,.83):
            box(rails,edge,a,b,left-.035,left+.037,y,.058,m["pale"])
        for i in range(1,9):
            s=a+(b-a)*i/9
            box(rails,edge,s-.017,s+.017,left-.019,left+.019,.18,.67,m["pale"])
        box(rails,edge,a-.048,a+.047,left-.057,left+.057,-.003,.99,m["royal"])
        a=b
    return rails.save()


def market_front(edge,m):
    base=Mesh("COL_Zhongxing10_PublicArcadeFace")
    moulding=Mesh("Zhongxing10_ArcadePlinthAndRecesses")
    for a,b in ((.8,4.2),(4.2,7.8),(7.8,10.6)):
        for l,r in ((a,a+.45),(b-.42,b)):
            box(base,edge,l,r,2.46,3.06,-.12,3.61,m["brick"])
            box(moulding,edge,l-.035,r+.035,2.40,2.63,.041,.21,m["plaza"])
        box(base,edge,a,b,2.10,3.27,2.90,.58,m["brick"])
        box(base,edge,a+.41,b-.40,3.16,3.27,.075,2.90,m["shade"])
        box(moulding,edge,a+.38,b-.39,2.32,3.19,.047,.089,m["kerb"])
    return [base.save(),moulding.save()]


def shade_gate(terrain,control,m):
    e,n=control
    boundary=Edge([(e,n-3.75),(e,n+4.2)],terrain)
    frame=Mesh("COL_Zhongxing12_RegisteredTimberGate")
    roof=Mesh("Zhongxing12_OverlappingTileEaves")
    for a in (2.62,4.72):
        box(frame,boundary,a,a+.16,-.14,.18,-.08,2.57,m["timber"])
        box(frame,boundary,a-.09,a+.23,-.22,.25,-.045,.36,m["plaza"])
    box(frame,boundary,2.53,4.98,-.16,.22,2.31,.22,m["timber"])
    box(frame,boundary,4.94,7.22,.11,.43,-.12,1.90,m["brick"])
    # The main roof and a smaller eave overlap along the same axis. Their
    # support geometry documents the visible exterior without opening a house.
    for a,b,c,d,h in ((2.16,5.21,-.78,1.37,2.55),(2.46,5.42,-.33,1.55,3.08)):
        ridge=(c+d)*.5
        for u,v,g0,g1 in ((c,ridge,h,h+.48),(ridge,d,h+.48,h)):
            outer=[boundary.at(s,lift,z) for s,lift,z in ((a,u,g0),(b,u,g0),(b,v,g1),(a,v,g1))]
            roof.solid(outer,[(x,y,z+.09) for x,y,z in outer],m["kerb"])
        box(roof,boundary,a,b,c-.015,c+.036,h-.065,.091,m["timber"])
        for k in range(ceil((b-a)/.22)):
            s=a+.22*k
            box(roof,boundary,s,min(s+.065,b),c-.052,c+.38,h-.075,.09,m["timber"])
    return [frame.save(),roof.save()]


def mural_wall(edge,m):
    wall=Mesh("COL_Zhongxing13_OuterMuralWall")
    panels=Mesh("Zhongxing13_PaintedPanels")
    setback=-1.62
    def wall_box(mesh,a,b,c,d,base,height,finish):
        box(mesh,edge,a,b,c+setback,d+setback,base,height,finish)
    for i,(a,b) in enumerate(((.8,5.15),(5.15,9.59),(9.59,13.34))):
        wall_box(wall,a,b,-1.73,-1.31,-.15,1.93,m["skin"])
        wall_box(wall,a,b,-1.78,-1.27,1.76,.095,m["plaza"])
        wall_box(wall,a-.07,a+.11,-1.78,-1.23,-.08,1.96,m["plaza"])
        color=m["mural_green"] if i%2==0 else m["mural_blue"]
        wall_box(panels,a+.65,b-.61,-1.32,-1.302,.37,.95,color)
        for j in range(4):
            s=a+.78+j*.42
            wall_box(panels,s,s+.23,-1.301,-1.294,.59+j*.087,.095,m["pale"])
    return [wall.save(),panels.save()]


def build(out):
    field=json.loads((HERE/"field.json").read_text())
    terrain=common["terrain"]()
    tiles=list(common["terrain_faces"]())
    m,textures=finishes()
    new,trees=plant_plaza(field["planter"],terrain,m)
    walks={}
    for plot,points in field["proposed_public_lines"].items():
        edge=Edge(points,terrain)
        length=edge.stations[-1]
        label=f"COL_Zhongxing{plot}_PublicPaving"
        if plot=="13":
            street,height=common["graded_footway"](edge,0.,{"flags":m["walk"],"border":m["kerb"]})
            street.name=label
        else:
            street=edge.strip(label,0.,1.63,.066,tiles,m["walk"],m["kerb"])
            def height(s):
                return edge.at(s,0.,.066)[2]
        new.append(street)
        if plot=="10":
            new.extend(market_front(edge,m))
            new.append(roadside_guard(edge,plot,-1.04,length-.2,m))
        elif plot=="12":
            new.extend(shade_gate(terrain,field["gate_control"]["match_en"],m))
            new.append(roadside_guard(edge,plot,1.04,3.4,m))
        elif plot=="13":
            new.extend(mural_wall(edge,m))
            new.append(roadside_guard(edge,plot,.98,length-.2,m))
        stops=[.42+(length-.92)*i/5 for i in range(6)]
        walks[plot]=[(*edge.en(s,0.),height(s)) for s in stops]
    existing=runpy.run_path(str(HERE.parent/"panda_15_17/build.py"))
    riverside=HERE.parents[1]/"riverside/east_bend/build.py"
    substitutions,retired,cut=existing["retire"](runpy.run_path(str(riverside)),(13,),HERE/"ownership-13.json")
    data=json.loads((common["ASSETS"]/"north-38-40-41.json").read_text())["borrowed_materials"]
    borrowed={obj.name:{alias:original for alias,original in data[obj.name].items()
                       if alias in {slot.name for slot in obj.data.materials if slot}}
              for obj in substitutions}
    for obj in list(bpy.data.objects):
        if obj not in new and obj not in substitutions:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    for mesh in substitutions:
        for slot in mesh.material_slots:
            if slot.material and slot.material.library:
                slot.material=slot.material.make_local()
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    name="zhongxing-public-10-12-13-22"
    bpy.ops.wm.save_as_mainfile(filepath=str(out/f"{name}.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(out/f"{name}.glb"),export_format="GLB",export_image_format="NONE",export_cameras=False,export_lights=False)
    plan={"retired_plots":[13],"retired_objects":retired,"new_meshes":[x.name for x in new],
          "replacement_meshes":[x.name for x in substitutions],"retired_plot_faces":cut,
          "walks":walks,"surface_textures":textures,"borrowed_materials":borrowed,"trees":trees}
    (out/f"{name}.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n")
    print("CQ_ZHONGXING_PUBLIC",json.dumps(walks))


if __name__=="__main__":
    build(Path(sys.argv[-1]).resolve())
