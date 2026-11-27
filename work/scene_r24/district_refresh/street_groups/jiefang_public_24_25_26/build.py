"""Restore physically separate public margins along the two Jiefang West Road lines."""
import json
from math import ceil, cos, pi, sin
from pathlib import Path
import runpy
import sys

import bpy

HERE=Path(__file__).resolve().parent
common=runpy.run_path(str(HERE.parent/"north_edges/build.py"))
Edge,Mesh,material,tint,box=(common[key] for key in ("Edge","Mesh","material","tint","box"))


def palette():
    mats,textures={},{}
    for key,label,color,filename in (
        ("flags","Jiefang West street grey flag paving",(.81,.78,.70),"stone_floor_diff_2k.jpg"),
        ("border","Jiefang West kerb worn stone",(.70,.66,.61),"concrete_floor_worn_001_diff_2k.jpg"),
        ("bay","Jiefang West lower road lay-by surface",(.72,.71,.67),"asphalt_02_diff_1k.jpg"),
        ("box","Jiefang West raised planter masonry",(.49,.36,.28),"brick_wall_08_diff_2k.jpg"),
        ("fill","Jiefang West raised planters and bed",(.39,.45,.27),"leaf_scattered_gravel_diff_2k.jpg"),
        ("beam","Chongqing waterfront ageing concrete beam",(.63,.64,.61),"concrete_wall_006_diff_2k.jpg"),
        ("step","Jiefang West stone stair treads",(.71,.71,.69),"stone_floor_diff_2k.jpg"),
    ):
        mats[key]=material(label,color,filename)
        textures[label]=f"res://assets/chongqing_district_{filename}"
    mats["rail"]=tint("Jiefang West worn iron with graphite paint",(.103,.109,.096))
    mats["mark"]=tint("Jiefang West aged pale lay-by line",(.78,.77,.67))
    mats["green"]=tint("Changbin shaded dark green pier coating",(.079,.183,.119))
    mats["blue"]=tint("Changbin coated pale-blue handrail",(.16,.38,.62))
    mats["canvas"]=tint("Riverside tea cart old canvas hood",(.35,.20,.139))
    return mats,textures


def roadside_detail(edge,plot,m):
    detail=Mesh(f"Jiefang{plot}_RoadEdgeFinish")
    length=edge.stations[-1]
    count=ceil((length-.8)/.63)
    for k in range(count):
        a=.34+k*.63
        b=min(a+.63,length-.21)
        box(detail,edge,a,b,-.83,-.66,.032,.10,m["border"])
    if plot=="24":
        for k in range(5):
            a=1.05+k*2.95
            b=a+2.35
            for x in (a,b):
                box(detail,edge,x-.062,x+.068,-1.11,-.974,-.03,.99,m["rail"])
                box(detail,edge,x-.10,x+.10,-1.147,-.92,.86,.075,m["rail"])
            for h in (.27,.58,.84):
                box(detail,edge,a,b,-1.072,-1.018,h,.052,m["rail"])
            if k%2==0:
                center=(a+b)*.5
                box(detail,edge,center-.48,center+.48,-1.56,-1.17,.02,.34,m["box"])
                box(detail,edge,center-.45,center+.45,-1.51,-1.22,.36,.076,m["fill"])
    if plot=="26":
        for a in (2.15,7.40,12.64):
            box(detail,edge,a,a+.048,-2.23,-.87,.028,.012,m["mark"])
    return detail.save()


def tea_public_deck(field,m):
    tree_court=Mesh("COL_Jiefang02_ExistingTeaCourtyardFlags")
    edge_finish=Mesh("Jiefang02_ExistingTeaCourtyardStripe")
    fixtures=Mesh("Jiefang02_FictionalTeaCartAndDeliveryShelf")
    spec=field["fictional_tea_land_side"]
    e,n=spec["center_en"]
    angle=spec["bearing_rad"]
    c,s=cos(angle),sin(angle)
    z=spec["confirmed_floor_y"]+.048

    def local(u,v,h):
        return (e+c*u-s*v,n+s*u+c*v,h)

    for k in range(26):
        a=-6.5+k*.5
        b=a+.50
        ring=[local(u,v,z) for u,v in ((a,6.75),(b,6.75),(b,8.22),(a,8.22))]
        tree_court.face(ring,m["flags"])
        edge=[local(u,v,z+.004) for u,v in ((a,8.08),(b,8.08),(b,8.20),(a,8.20))]
        edge_finish.face(edge,m["border"])
    path=[local(u,7.50,z) for u in (-6.2,-3.75,-1.25,1.25,3.75,6.2)]

    def solid(u0,u1,v0,v1,pad,height,finish):
        low=[local(u,v,z+pad) for u,v in ((u0,v0),(u1,v0),(u1,v1),(u0,v1))]
        fixtures.solid(low,[(x,y,h+height) for x,y,h in low],finish)

    for u in (-4.89,-3.49):
        for v in (8.35,9.31):
            solid(u,u+.10,v,v+.095,0.,1.86,m["rail"])
    solid(-5.06,-3.23,8.09,9.58,1.84,.09,m["canvas"])
    solid(-4.85,-3.48,8.32,8.86,.09,.73,m["box"])
    solid(-4.95,-3.38,8.29,8.91,.82,.084,m["border"])
    for u in (4.10,5.43):
        solid(u,u+.12,8.35,8.55,.01,.80,m["rail"])
    solid(4.04,5.62,8.22,8.58,.81,.085,m["border"])

    def target(u,v,h):
        ee,nn,yy=local(u,v,z+h)
        return [ee,yy,-nn]

    stops=[{"approach":list(local(-4.20,7.50,z)),"target":target(-4.20,8.18,.96)},
           {"approach":list(local(4.85,7.50,z)),"target":target(4.85,8.19,.96)}]
    tea={"stand_east_north_up":local(-4.20,9.29,z),"approach":list(path[0]),
         "public_stops":stops,"fictional_in_place_of_old_model":True}
    return [tree_court.save(),edge_finish.save(),fixtures.save()],path,tea


def waterfront_underpass(field,ground,m):
    e,n=field["pier_02"]["en"]
    levels=field["pier_02"]["fit_game"]
    low,beam,deck=(levels[k] for k in ("ground_game_y","beam_underside_y","top_game_y"))
    axis=Edge([(e-25,n+3.125),(e+30,n-3.75)],ground)
    deck_mesh=Mesh("COL_Changbin02_RegisteredFlyoverBay")
    piers=Mesh("COL_Changbin02_RegisteredPiers")
    paved_margin=Mesh("COL_Changbin02_RaisedPierFootway")
    coping=Mesh("Changbin02_ParapetAndSoffitRibs")
    badge=Mesh("Changbin02_OriginalSkylineEmblemStudy")

    def at(s,c,y):
        return (*axis.en(s,c),y-.009*(s-25.2))

    def beam_block(mesh,a,b,c,d,y,height,finish):
        lower=[at(s,t,y) for s,t in ((a,c),(b,c),(b,d),(a,d))]
        mesh.solid(lower,[(x,y,z+height) for x,y,z in lower],finish)

    length=axis.stations[-1]
    beam_block(deck_mesh,0.,length,-8.85,2.88,beam+.36,deck-beam-.36,m["beam"])
    for row in (-7.45,-5.60,-3.35,-1.2,1.0):
        beam_block(coping,0.,length,row,row+.23,beam+.21,.18,m["beam"])
    for s in (4.05,25.2,47.6):
        p=axis.en(s,0.) if s!=25.2 else (e,n)
        y=axis.ground_y(p)
        foot=min(y,low)-.21
        radius=levels["diameter_m"]*.50 if s==25.2 else .75
        lower=[(p[0]+radius*cos(k*pi/16),p[1]+radius*sin(k*pi/16),foot) for k in range(32)]
        upper=[(x,y,beam-.009*(s-25.2)) for x,y,_ in lower]
        piers.solid(lower,upper,m["green"])
        beam_block(coping,s-.62,s+.62,-8.30,2.69,beam-.05,.39,m["beam"])
    # The photos show the pier on a raised, grey paved band alongside the travel lane.
    # Follow the existing supporting ground and keep the riverward edge clear of OSM 1256859184.
    stations=sorted({3.,51.,*[3.+i*.60 for i in range(1,80)]})
    levels={s:max(axis.ground_y(axis.en(s,t)) for t in (-.97,0.,1.01))+.103 for s in stations}
    for i,(a,b) in enumerate(zip(stations,stations[1:])):
        points=[axis.en(s,t) for s,t in ((a,-.97),(b,-.97),(b,1.01),(a,1.01))]
        top=[(*p,levels[s]) for p,s in zip(points,(a,b,b,a))]
        low=[(*p,min(axis.ground_y(p)-.06,z-.07)) for p,(_,_,z) in zip(points,top)]
        paved_margin.face(top,m["flags"])
        paved_margin.face([low[0],low[1],top[1],top[0]],m["border"])
        paved_margin.face([low[2],low[3],top[3],top[2]],m["border"])
        if i==0:
            paved_margin.face([low[3],low[0],top[0],top[3]],m["border"])
        if i==len(stations)-2:
            paved_margin.face([low[1],low[2],top[2],top[1]],m["border"])
    for c in (-8.72,2.73):
        beam_block(deck_mesh,0.,length,c-.12,c+.12,deck,.59,m["beam"])
        for j in range(22):
            a=length*j/22
            b=length*(j+1)/22
            beam_block(coping,a,b,c-.04,c+.04,deck+.66,.061,m["blue"] if j%2 else m["mark"])
    # Self-authored tower silhouette on the river-facing portion of the coating.
    for i,x in enumerate((-.25,-.123,0.,.123,.249)):
        y=n-(.822**2-x*x)**.5-.018
        h=(.26,.45,.64,.48,.31)[i]
        badge.face([(e+x-.033,y,-.16),(e+x+.037,y,-.16),(e+x+.037,y,-.16+h),(e+x-.033,y,-.16+h)],m["mark"])
    return [deck_mesh.save(),piers.save(),paved_margin.save(),coping.save(),badge.save()]


def public_stair(field,ground,m):
    spec=field["stairs_25"]
    axis=Edge([spec["left"]["en"],spec["right"]["en"]],ground)
    stair=Mesh("COL_Jiefang25_RegisteredStoneSteps")
    side=Mesh("COL_Jiefang25_DoorPiersAndStepReturns")
    width=axis.stations[-1]
    length=4.64

    def step_height(s,index):
        f=index/11.
        low=axis.ground_y(axis.en(s,-length-.26))+.06
        top=axis.ground_y(axis.en(s,0.))+.53
        return low+(top-low)*f

    for k in range(12):
        a=-length+(k-1)*length/11.
        b=-length+k*length/11.
        if k==0:
            a=-length-.61
        for i in range(13):
            s,t=width*i/13.,width*(i+1)/13.
            ring=[(*axis.en(u,v),step_height(u,k)) for u,v in ((s,a),(t,a),(t,b),(s,b))]
            stair.solid([(x,y,z-.37) for x,y,z in ring],ring,m["step"])
    for i in range(13):
        s,t=width*i/13.,width*(i+1)/13.
        ring=[(*axis.en(u,v),step_height(u,11)) for u,v in ((s,0.),(t,0.),(t,.83),(s,.83))]
        stair.solid([(x,y,z-.39) for x,y,z in ring],ring,m["step"])
    for s in (.0,width-.38):
        box(side,axis,s,s+.38,-.17,.38,.40,2.68,m["beam"])
    box(side,axis,0.,width,.14,.76,2.92,.21,m["beam"])
    center=width/2
    stations=[(*axis.en(center,-length-.28),step_height(center,0))]
    for i in (2,4,6,8,10,11):
        stations.append((*axis.en(center,-length+(i-.5)*length/11.),step_height(center,i)))
    stations.append((*axis.en(center,.27),step_height(center,11)))
    return [stair.save(),side.save()],stations


def build(out):
    field=json.loads((HERE/"field.json").read_text())
    terrain=common["terrain"]()
    faces=list(common["terrain_faces"]())
    mats,textures=palette()
    layer,tea_path,tea=tea_public_deck(field,mats)
    layer.extend(waterfront_underpass(field,terrain,mats))
    walks={"02":tea_path}
    for plot in ("24","25","26"):
        edge=Edge(field["public_lines"][plot],terrain)
        surfaced,height=common["graded_footway"](edge,0.,mats)
        surfaced.name=f"COL_Jiefang{plot}_PublicFlags"
        layer.extend((surfaced,roadside_detail(edge,plot,mats)))
        if plot=="26":
            layby=edge.strip("COL_Jiefang26_LowerRoadLayBy",-1.56,1.68,.022,faces,mats["bay"],mats["border"])
            layer.append(layby)
        stops=[.48+(edge.stations[-1]-.95)*k/5 for k in range(6)]
        walks[plot]=[(*edge.en(s,0.),height(s)) for s in stops]
    steps,walks["25"]=public_stair(field,terrain,mats)
    layer.extend(steps)
    helper=runpy.run_path(str(HERE.parent/"panda_15_17/build.py"))
    adjacent=runpy.run_path(str(HERE.parents[1]/"riverside/east_bend/build.py"))
    updated,removed,counts=helper["retire"](adjacent,(2,24,25),HERE/"ownership.json")
    parent=json.loads((common["ASSETS"]/"zhongxing-public-10-12-13-22.json").read_text())["borrowed_materials"]
    inherited={ob.name:{alias:origin for alias,origin in parent[ob.name].items()
                        if alias in {x.name for x in ob.data.materials if x}}
               for ob in updated}
    for obj in list(bpy.data.objects):
        if obj not in layer and obj not in updated:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    for mesh in updated:
        for slot in mesh.material_slots:
            if slot.material and slot.material.library:
                slot.material=slot.material.make_local()
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    name="jiefang-public-02-24-25-26"
    bpy.ops.wm.save_as_mainfile(filepath=str(out/f"{name}.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(out/f"{name}.glb"),export_format="GLB",export_image_format="NONE",export_cameras=False,export_lights=False)
    entries={"retired_plots":[2,24,25],"retired_objects":removed,"replacement_meshes":[x.name for x in updated],
             "new_meshes":[x.name for x in layer],"retired_plot_faces":counts,"walks":walks,
             "surface_textures":textures,"borrowed_materials":inherited,"tea":tea}
    (out/f"{name}.json").write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')


if __name__=="__main__":
    build(Path(sys.argv[-1]).resolve())
