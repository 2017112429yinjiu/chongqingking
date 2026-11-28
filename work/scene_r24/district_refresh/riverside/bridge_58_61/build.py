"""Build a mapped north-bank bridge and a separate ground-level park path."""
import json
from math import ceil, cos, pi, radians, sin
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
SCENE=HERE.parents[2]
GROUPS=SCENE/"district_refresh/street_groups"
sys.path[:0]=[str(GROUPS),str(GROUPS/"guoco"),str(SCENE/"district_500")]
from factory import Mesh, material, terrain
from factory_glazing import glaze_material
from refresh_geometry import ASSETS, latest_donors, load_current, read, strip_plots
from riverside import make_strip, terrain_faces

PARK=[[-121.9,-177.82],[-116.8,-179.7],[-109,-184.8],[-102.4,-187.6],[-93.8,-190.1],
      [-85.9,-190.7],[-81.7,-193.4],[-80.1,-197.3],[-75.0,-200.5],[-68.1,-202.4],
      [-58.5,-204.8],[-51.2,-204.6],[-44.0,-203.5],[-39.3,-202.2]]
LOOKOUT=[[ -81.7,-193.4],[-84.2,-188.7],[-83.8,-184.5]]
PAVING_WIDTH=2.9
WALL_STONE="stone_wall_05_diff_2k.jpg"
GARAGE_FRONT=[(-150,-145.5),(-135,-150.8),(-111,-156.9),(-91,-161.4),
              (-80,-163.8),(-70,-165.5),(-61,-165.8),(-53,-165.0),
              (-46,-162.1),(-41.6,-158.15),(-38.6,-152.7)]


def read_axis(points, value, column):
    for a,b in zip(points,points[1:]):
        if min(a[column],b[column])<=value<=max(a[column],b[column]) and a[column]!=b[column]:
            t=(value-a[column])/(b[column]-a[column])
            return Vector(a).lerp(Vector(b),t)
    raise ValueError((column,value))


def sweep(mesh, centres, profile, finish):
    if sum(u*h2-u2*h for (u,h),(u2,h2) in zip(profile,profile[1:]+profile[:1]))<0:
        profile=profile[::-1]
    rows=[]
    for index,(position,z) in enumerate(centres):
        before=centres[max(0,index-1)][0]
        after=centres[min(len(centres)-1,index+1)][0]
        direction=(after-before).normalized()
        cross=Vector((-direction.y,direction.x))
        rows.append([(position.x+cross.x*u,position.y+cross.y*u,z+h) for u,h in profile])
    mesh.face(rows[0][::-1],finish)
    mesh.face(rows[-1],finish)
    for a,b in zip(rows,rows[1:]):
        for i,j in zip(range(len(profile)),(*range(1,len(profile)),0)):
            mesh.face([a[i],b[i],b[j],a[j]],finish)


def columns(mesh, p, bottom, top, radius, concrete):
    def circle(z,r):
        return [(p.x+r*cos(i*pi/9),p.y+r*sin(i*pi/9),z) for i in range(18)]
    mesh.solid(circle(bottom,radius*1.13),circle(bottom+.23,radius*1.13),concrete)
    mesh.solid(circle(bottom+.23,radius),circle(top-.47,radius),concrete)
    mesh.solid(circle(top-.47,radius),circle(top+.05,radius*1.3),concrete)


def rail_meshes(axes, ground, street_level, vertical_adjustment=None, northern_end=None):
    lines=[axes[key] for key in ("878019566","1134456893")]
    def center(n):
        a,b=[read_axis(line,n,1) for line in lines]
        return (a+b)*.5
    def level(n):
        return street_level+42.-.013*(n+175.)+(vertical_adjustment(n) if vertical_adjustment else 0.)
    steel=material("North rail muted steel box finish",(.56,.63,.64),"concrete_wall_006_diff_2k.jpg")
    shell=material("North rail pale acoustic canopy",(.85,.89,.87),"concrete_wall_006_diff_2k.jpg")
    light=material("North rail pale fair-faced concrete piers",(.90,.92,.90),"plastered_wall_04_diff_1k.jpg")
    dark=glaze_material("North rail recessed vent band",(.044,.073,.080),.79)
    beam=Mesh("COL_Nanjimen_NorthRailSteelBox")
    canopy=Mesh("Nanjimen_NorthAcousticHood")
    vents=Mesh("Nanjimen_NorthHoodDivisions")
    pier=Mesh("COL_Nanjimen_NorthRailPiers")
    underside=Mesh("Nanjimen_NorthRailBoxStiffeners")
    river=Mesh("Nanjimen_RiverSpanContext")
    span_stations=list(range(-278,-79,3)) if northern_end is None else [*range(-278,ceil(northern_end),3),northern_end]
    stations=[(center(n),level(n)) for n in span_stations]
    box=[(-11.5,2.95),(-11.5,2.05),(-8.1,0.),(8.1,0.),(11.5,2.05),(11.5,2.95)]
    sweep(beam,stations,box,steel)
    continuation=[(center(n),level(n)) for n in (*range(-1158,-279,20),-278)]
    sweep(river,continuation,box,steel)
    cover_stop=-88 if northern_end is None else ceil(northern_end-1.)
    cover=[(center(n),level(n)) for n in range(-263,cover_stop,3)]
    sweep(canopy,cover,[(-10.72,2.78),(-10.72,4.7),(-10.15,5.68),(-8.92,6.43),
                        (-6.50,6.70),(6.50,6.70),(8.92,6.43),(10.15,5.68),(10.72,4.7),(10.72,2.78)],shell)
    for side in (-1.,1.):
        sweep(vents,cover,[(side*10.65,3.59),(side*10.77,3.59),(side*10.77,4.3),(side*10.65,4.3)],dark)
        for n in range(-261,cover_stop-1,2):
            rows=[(center(k),level(k)) for k in (n-.10,n+.10)]
            sweep(vents,rows,[(side*10.77,3.59),(side*10.84,3.59),(side*10.84,4.3),(side*10.77,4.3)],shell)
    for offset in (-6.8,-2.25,2.25,6.8):
        sweep(underside,stations,[(offset-.11,-.22),(offset+.11,-.22),(offset+.11,.06),(offset-.11,.06)],steel)
    for n in range(-275,-83 if northern_end is None else ceil(northern_end-1.0),3):
        ties=[(center(k),level(k)) for k in (n-.08,n+.08)]
        sweep(underside,ties,[(-7.65,-.17),(7.65,-.17),(7.65,.04),(-7.65,.04)],steel)
    for n,h in ((-365.,72.),(-837.,109.)):
        p,z=center(n),level(n)
        for offset in (-10.3,10.3):
            def leg(up,width,depth):
                return [(p.x+offset+x,p.y+y,up) for x,y in
                        ((-width,-depth),(width,-depth),(width,depth),(-width,depth))]
            river.solid(leg(-22.,3.52,4.5),leg(z+3.,2.2,3.1),light)
            river.solid(leg(z+2.9,2.2,3.1),leg(z+h,1.65,2.3),light)
            for side in (-1,1):
                for d in (31,50,71,90,108,126,145):
                    cable_end=n+side*d
                    end=center(cable_end)
                    start=Vector((p.x+offset,p.y,z+h*.64+d*.12))
                    finish=Vector((end.x+offset,end.y,level(cable_end)+3.20))
                    narrow=Vector((.052,0.,0.))
                    thick=Vector((0.,0.,.052))
                    river.face([start-narrow,finish-narrow,finish+narrow,start+narrow],steel)
                    river.face([start-thick,finish-thick,finish+thick,start+thick],steel)
        def cap(up):
            return [(p.x+x,p.y+y,up) for x,y in ((-12.5,-2.35),(12.5,-2.35),(12.5,2.35),(-12.5,2.35))]
        river.solid(cap(z+h-2.8),cap(z+h-.7),light)
    bases=[]
    for n in (-245.,-175.,-105.):
        p=center(n)
        base=ground(p)
        if base is None:
            # The out-of-game shoreline carry ends below the existing river surface.
            base=-22.0
        z=level(n)
        def ring(w,l,up):
            return [(p.x+x,p.y+y,up) for x,y in ((-w,-l),(w,-l),(w,l),(-w,l))]
        pier.solid(ring(2.36,1.64,base-.88),ring(2.16,1.42,z-2.8),light)
        pier.solid(ring(2.16,1.42,z-2.8),ring(4.83,1.65,z+.22),light)
        bases.append([p.x,p.y,base,z])
    records=[{"east_north":list(center(n)),"box_soffit_game_m":level(n)} for n in (-245,-187,-175,-154,-105)]
    return [x.save() for x in (beam,canopy,vents,pier,underside,river)],records,bases


def ramp_meshes(axes,ground,street_level):
    concrete=material("Raijiapo light ash fascia",(.75,.77,.72),"concrete_wall_006_diff_2k.jpg")
    pier_finish=material("Raijiapo pale concrete round supports",(.81,.84,.82),"plastered_wall_04_diff_1k.jpg")
    asphalt=material("Raijiapo retained asphalt surface",(.48,.49,.48),"asphalt_02_diff_1k.jpg")
    base=glaze_material("Raijiapo cream lining paint",(.79,.78,.66),.85)
    steel=glaze_material("Raijiapo grey blue parapet rails",(.24,.31,.34),.56)
    beams=[]
    profiles={}
    supports=Mesh("COL_Raijiapo_RampRoundColumns")
    footings={}
    setups={"1256840000":(list(reversed(axes["1256840000"])),12.85,2.45),
            "1324001438":(axes["1324001438"],15.25,2.52),
            "1256839997":(axes["1256839997"],13.00,3.28)}
    for id,(series,low,half) in setups.items():
        centres=[Vector(series[0])]
        for a,b in zip(series,series[1:]):
            a,b=Vector(a),Vector(b)
            steps=ceil((b-a).length/3.8)
            centres.extend(a.lerp(b,i/steps) for i in range(1,steps+1))
        parts=[(p,street_level+low+.019*(p.x+102.)) for p in centres]
        mesh=Mesh("COL_Raijiapo_Ramp_"+id)
        sweep(mesh,parts,[(-half,1.37),(-half+.13,.49),(-half+.61,0.),
                          (half-.61,0.),(half-.13,.49),(half,1.37)],concrete)
        sweep(mesh,parts,[(-half+.12,1.36),(-half+.12,1.41),(half-.12,1.41),(half-.12,1.36)],asphalt)
        for s in (-1,1):
            edge=s*(half-.14)
            sweep(mesh,parts,[(edge-.09,1.40),(edge+.09,1.40),(edge+.09,1.64),(edge-.09,1.64)],concrete)
            for z in (1.83,2.10):
                sweep(mesh,parts,[(edge-.038,z),(edge+.038,z),(edge+.038,z+.043),(edge-.038,z+.043)],steel)
            for i in range(0,len(parts),2):
                p,z=parts[i]
                a,b=parts[max(0,i-1)][0],parts[min(len(parts)-1,i+1)][0]
                t=(b-a).normalized()
                p=p+Vector((-t.y,t.x))*edge
                def bar(h):
                    return [(p.x+x,p.y+y,z+h) for x,y in ((-.037,-.04),(.037,-.04),(.037,.04),(-.037,.04))]
                mesh.solid(bar(1.58),bar(2.13),steel)
        sweep(mesh,parts,[(-.04,1.411),(.04,1.411),(.04,1.419),(-.04,1.419)],base)
        beams.append(mesh.save())
        profiles[id]=[{"east_north":list(p),"girder_bottom_game_m":z,"road_game_m":z+1.41} for p,z in parts]
        footings[id]=[]
        for i in (0,*range(5,len(parts)-2,5),len(parts)-1):
            p,z=parts[i]
            if id=="1256839997" and abs(p.x+111.)<4.:
                continue
            land=ground(p)
            if land is None or land >= z-.60:
                assert land is not None, (id,list(p))
                footings[id].append([*p,land,z,"terrain"])
                continue
            columns(supports,p,land-.30,z,.70 if id=="1324001438" else .60,pier_finish)
            footings[id].append([*p,land,z,"round pier"])
        if id=="1256839997":
            p=Vector((-109.8,-134.82))
            cap=street_level+13.0
            land=ground(p)
            assert land is not None and cap-land>.70, (p,land,cap)
            columns(supports,p,land-.38,cap,.66,pier_finish)
            footings[id].append([*p,land,cap,"photo-registered inland pier"])
    beams.append(supports.save())
    return beams,profiles,footings


def garage_meshes(ground):
    bands=material("Raijiapo sandy cast stone bands",(.95,.90,.77),"plastered_wall_04_diff_1k.jpg")
    inner=material("Raijiapo rough grey covered parking slabs",(.68,.68,.65),"concrete_wall_006_diff_2k.jpg")
    dark=material("Raijiapo deep parking wall and ramp lining",(.38,.42,.43),"concrete_wall_006_diff_2k.jpg")
    rails=glaze_material("Raijiapo galvanized opening rails",(.32,.36,.36),.55)
    planting=material("Raijiapo rooftop planted ground",(.59,.68,.44),"brown_mud_leaves_01_diff_2k.jpg")
    masonry=Mesh("COL_Raijiapo_GaragePublicEnvelope")
    sections=Mesh("COL_Raijiapo_GarageParkingSlabs")
    details=Mesh("Raijiapo_GarageRecessedCoursesAndRails")
    roof=Mesh("Raijiapo_GaragePlantedRoof")
    front=[Vector(p) for p in GARAGE_FRONT]
    centres=[front[0]]
    for a,b in zip(front,front[1:]):
        steps=max(1,ceil((b-a).length/5.55))
        centres.extend(a.lerp(b,i/steps) for i in range(1,steps+1))
    levels=[(p,11.06+.039*(p.x+103.)) for p in centres]
    depths=[13.50 if p.x<-48 else 12.65 for p in centres]
    offsets=[-10.3,-7.74,-5.08,-2.46,0.]
    for offset in offsets:
        sweep(sections,levels,[(.03,offset-.27),(13.05,offset-.27),(13.05,offset+.10),(.03,offset+.10)],inner)
        sweep(masonry,levels,[(-.36,offset-.20),(.30,offset-.20),(.30,offset+.46),(-.36,offset+.46)],bands)
        if offset==0:
            continue
        for h in (.04,.17,.29,.41):
            sweep(details,levels,[(-.395,offset+h),(-.357,offset+h),(-.357,offset+h+.025),
                                  (-.395,offset+h+.025)],dark)
        sweep(details,levels,[(.27,offset+.53),(.32,offset+.53),(.32,offset+.57),(.27,offset+.57)],rails)
        sweep(details,levels,[(.27,offset+.82),(.32,offset+.82),(.32,offset+.86),(.27,offset+.86)],rails)
    sweep(masonry,levels,[(12.63,-10.6),(13.10,-10.6),(13.10,.12),(12.63,.12)],dark)
    for index,(p,z) in enumerate(levels):
        a,b=centres[max(0,index-1)],centres[min(len(centres)-1,index+1)]
        direction=(b-a).normalized()
        inward=Vector((-direction.y,direction.x))
        def rect(u0,u1,v0,v1,h):
            return [(*(p+u*direction+v*inward),h) for u,v in
                    ((u0,v0),(u1,v0),(u1,v1),(u0,v1))]
        base_levels=[ground(p+inward*v) for v in (.1,7.4,12.7)]
        assert all(h is not None for h in base_levels),list(p)
        width=.61 if index%4==0 else .48
        depth=depths[index]
        masonry.solid(rect(-width/2,width/2,-.10,1.0,base_levels[0]-.33),
                      rect(-width/2,width/2,-.10,1.0,z),bands)
        sections.solid(rect(-.28,.28,7.0,7.8,base_levels[1]-.4),
                      rect(-.28,.28,7.0,7.8,z-.18),inner)
        if index in (0,len(levels)-1):
            masonry.solid(rect(-.21,.21,.04,depth, min(base_levels)-.40),
                          rect(-.21,.21,.04,depth,z-.08),inner)
        if index<len(levels)-1:
            next_p,next_z=levels[index+1]
            low_next=ground(next_p+inward*.19)
            floor=z+offsets[0]-.17
            floor_next=next_z+offsets[0]-.17
            if min(floor-base_levels[0],floor_next-low_next) > .15:
                sweep(masonry,[(p,z),(next_p,next_z)],
                      [(-.11,-11.6),(.35,-11.6),(.35,-10.46),(-.11,-10.46)],inner)
    for start,finish in ((4,11),(15,21)):
        patch=levels[start:finish]
        sweep(roof,patch,[(3.95,.08),(11.15,.08),(11.15,.17),(3.95,.17)],planting)
        for u in (3.94,11.14):
            sweep(details,patch,[(u-.10,.09),(u+.10,.09),(u+.10,.31),(u-.10,.31)],bands)
    return [x.save() for x in (masonry,sections,details,roof)],{
        "front_east_north":GARAGE_FRONT,"modeled_faces_toward_changbin_road":len(levels)-1,
        "levels_relative_to_roof_m":offsets,"roof_game_east_north_up":[[*p,z] for p,z in levels],
        "retired_trial_plots":[58,60],"model_scope":"visible road-side facade, columns and covered decks",
    }


def build():
    ctl=read(HERE/"field-controls.json")
    primary=read(ASSETS/"park-plot57.json")
    park57=HERE.parent/"park_plot57/park-plot57.blend"
    west=HERE.parent/"west_ramp/west-ramp.blend"
    donors=latest_donors([
        ("west-ramp",west),
        ("guoco-frontages",GROUPS/"guoco/guoco-frontages.blend"),
        ("public-edges",GROUPS/"matix/public-edges.blend"),
        ("xingchen",GROUPS/"xingchen/xingchen.blend"),
        ("pavilion62",HERE.parent/"pavilion62/pavilion62.blend"),
        ("collectibles-market",GROUPS/"zhongxing/collectibles/collectibles-market.blend"),
        ("market-stall-row",GROUPS/"zhongxing/collectibles/stall_row/stall-row.blend"),
        ("park-plot57",park57),
    ])
    layout=read(ASSETS/"layout.json")
    replacements,retired,counts=strip_plots(read(HERE/"ownership.json"),(58,60),layout,donors)
    for name in ("COL_Outer500_Surface_01_01","COL_Outer500_Surface_02_01"):
        load_current(name,donors[name])
    land=terrain()
    def ground(p):
        hit,*_=land.ray_cast(Vector((p[0],p[1],80.)),Vector((0.,0.,-1.)))
        return None if hit is None else hit.z
    geo=list(terrain_faces())
    flags=material("Bridge park grey saw-cut slab",(.70,.73,.69),"stone_floor_diff_2k.jpg")
    toe=material("Bridge park dusty pale concrete",(.77,.78,.72),"concrete_floor_worn_001_diff_2k.jpg")
    curb=material("Bridge park warm grey curb band",(.66,.69,.64),WALL_STONE)
    earth=material("Bridge park shaded rooted mulch",(.52,.57,.38),"brown_mud_leaves_01_diff_2k.jpg")
    axes=ctl["registered_road_and_rail_east_north"]
    street_level=ground(Vector(ctl["street_view"]["58"]["camera_game_east_north"]))
    street_positions=(-117.,-109.,-104.,-100.,-96.,-90.,-80.,-73.,-62.,-50.,-41.)
    offsets=(7.6,9.6,11.7,11.5,9.5,7.6,7.6,7.6,7.6,7.6,7.6)
    footway=[[e,read_axis(axes["59146737"],e,0).y-offset] for e,offset in zip(street_positions,offsets)]
    garage_side=[[e,read_axis(axes["59146737"],e,0).y+5.55] for e in (-133.,-120.,-101.,-88.,-75.,-61.,-49.)]
    link=[PARK[4],[-94.0,-183.1],[-91.2,-179.1],footway[5]]
    paths=[("EastGroundWalk",PARK,PAVING_WIDTH,0),("RampViewSpur",LOOKOUT,2.36,1),
           ("ChangbinParkFootway",footway,2.30,0),("PierFootwayLink",link,2.14,1),
           ("ChangbinGarageVerge",garage_side,2.18,1),
           ("ParkSidePlantingToe",[[-93.1,-192.27],[-86.0,-192.61],[-84.3,-194.3]],.75,2),
           ("EastPlantingToe",[[-65.8,-204.6],[-58.7,-207.13],[-50.9,-207.02],[-43.7,-205.93]],.93,2),
           ("EastPlantedBelt",[[-74.,-207.0],[-64.,-209.32],[-52.,-209.9],[-38.,-208.4]],3.15,3)]
    parts=[]
    for name,line,width,index in paths:
        obj=make_strip({"id":name,"points":line,"width_m":width,"finish":index,"raise_m":.023},geo,[flags,toe,curb,earth])
        obj.name="BridgePark_"+name
        parts.append(obj)
    trees=[]
    for i,(e,n,scale) in enumerate(((-113.8,-185.9,.83),(-91.0,-195.0,.89),(-79.1,-201.8,.66),
                                     (-72.2,-206.6,1.11),(-62.5,-208.4,.88),(-52.2,-209.1,1.10),
                                     (-43.2,-207.5,.87),(-37.,-207.6,1.04),(-47.0,-183.5,1.22),
                                     (-55.5,-185.5,1.19),(-69.4,-184.45,1.16),(-76.2,-183.4,.89)),1):
        p=Vector((e,n))
        z=ground(p)
        tree_id=(10,18,24,14)[i%4]
        plant=bpy.data.objects[f"Outer500_Plant_{tree_id:03}"].copy()
        plant.name=f"BridgePark_Plant_{i:02}"
        plant.location=(e,n,z-.04)
        plant.rotation_euler.z+=i*1.11
        plant.scale*=scale
        bpy.context.collection.objects.link(plant)
        parts.append(plant)
        trees.append([e,n,z])
    rails,rail_info,bases=rail_meshes(axes,ground,street_level)
    ramps,ramp_info,footings=ramp_meshes(axes,ground,street_level)
    garage,garage_info=garage_meshes(ground)
    parts.extend(rails+ramps+garage)
    before=primary["route_east_north"]
    route=[*before,*PARK[1:5],*link[1:],footway[6],footway[5],*link[-2::-1],
           *PARK[5:7],*LOOKOUT[1:],*LOOKOUT[-2::-1],*PARK[7:]]
    visits={"58":PARK[3],"59":PARK[9],"60":LOOKOUT[-1],"61":PARK[-2]}
    cameras={}
    for id,row in ctl["street_view"].items():
        pos=Vector(row["camera_game_east_north"])
        azimuth=radians(row["heading_deg"])
        stationary=ground(pos)+1.68
        aim=pos+Vector((sin(azimuth),cos(azimuth)))*16
        cameras[id]={"eye_enu":[*pos,stationary],"target_enu":[*aim,stationary],
                     "fov_deg":76,"registered_heading_deg":row["heading_deg"]}
    metas={"plots":visits,"route_east_north":route,"route_finish_m":ground(PARK[-1]),
           "surface_width_m":PAVING_WIDTH,"modeled_rail":rail_info,"fitted_pier_bases_and_box_soffits":bases,
           "modeled_vehicle_ramps":ramp_info,"motor_ramp_footings":footings,"parking":garage_info,
           "camera_58_street_floor_game_m":street_level,
           "replacement_meshes":[obj.name for obj in replacements],"retired_objects":retired,
           "removed_shared_geometry":counts,"street_views":cameras,"trees":trees,
           "footway":footway,"park_walk":PARK,"road_axis":axes["59146737"],
           "new_meshes":[obj.name for obj in parts],
           "views":[["rail_south_bank",[-119.2,-180.6],[-102.9,-190.1],14.8],
                    ["ramp_and_open_park",[-86.1,-185.8],[-68.2,-161.8],10.2],
                    ["east_footpath",[-75.1,-200.9],[-40.8,-203.4],1.2]]}
    keep=set(replacements+parts)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"bridge-park.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSETS/"bridge-park.glb"),export_format="GLB",
                              export_cameras=False,export_lights=False)
    (ASSETS/"bridge-park.json").write_text(json.dumps(metas,indent=2)+"\n")
    print("CQ_BRIDGE_PARK",json.dumps({"objects":len(parts),"park_stations":len(route),"finish_m":metas["route_finish_m"]}))


if not globals().get("CQ_RAIL_FUNCTIONS_ONLY",False):
    build()
