"""Make the two registered public bays of the Zhongxing Road Panda podium in Blender 4.3.2."""
from collections import Counter
import json
from math import atan2, ceil
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(HERE.parent),str(SCENE/"district_500")]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, read
from retire_plots import STATIC_FIXTURE, fingerprint, remove_faces
from riverside import material

PLOTS = (15, 17)
ORIGIN = Vector((142.5653,5.0098))
TANGENT = Vector((41.1997,31.9343)).normalized()
INWARD = Vector((-TANGENT.y,TANGENT.x))


def en(street,inset):
    return ORIGIN + TANGENT*street + INWARD*inset


def solid(mesh,a,b,c,d,bottom,top,finish):
    ring = [en(s,q) for s,q in ((a,c),(b,c),(b,d),(a,d))]
    mesh.solid([(*v,bottom) for v in ring],[(*v,top) for v in ring],finish)


def flat(name, rgb, roughness=.83):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*rgb,1)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = material.diffuse_color
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def facade(ground,m):
    frame = Mesh("COL_Panda228_PodiumStructure")
    trim = Mesh("Panda228_StoneRevealsAndShops")
    floor_base = 26.24
    roof = 39.20
    portal = [45.44,51.37]
    # One continuous street front spans the two former occupancies. The rear
    # return closes the shallow visible strip and follows the occupied slope.
    solid(frame,7.8,56.4,8.7,15.4,23.4,roof,m["rear"])
    for a,b in [(7.8,8.12),(56.08,56.4)]:
        solid(frame,a,b,5.85,8.75,ground((a+b)*.5,5.85)-.28,roof,m["stone"])
    for level in [floor_base,29.48,32.72,35.96,roof]:
        lip = .27 if level < roof else .39
        spans = [(7.79,portal[0]),(portal[1],56.41)] if level == floor_base else [(7.79,56.41)]
        for a,b in spans:
            solid(frame,a,b,5.85,8.73,level-.28,level,m["stone"])
            solid(trim,a, b,5.68,5.91,level-.16,level+lip*.30,m["edge"])
    storefronts = [8.0,11.86,15.46,19.66,23.25,26.96,30.46,34.35,38.12,42.07,*portal,54.18,56.30]
    # Setbacks are narrower along the bus-stop bay and deeper at the passage.
    for i,(a,b) in enumerate(zip(storefronts,storefronts[1:])):
        public_gate = a == portal[0]
        paving = ground((a+b)*.5,6.4)+.08
        glazing = 7.55 if public_gate else 6.69 + (.26 if i in (2,4,8) else 0.)
        for edge in (a,b):
            solid(frame,edge-.18,edge+.18,5.82,glazing+.24,paving-.44,roof-.16,m["stone"])
            solid(trim,edge-.10,edge+.10,5.75,5.84,paving+.20,roof-.24,m["rib"])
        if public_gate:
            opening_top = 28.95
            # Four nested returns give the visible orange portal real depth.
            for step in range(4):
                spread = .17+step*.11
                d = 5.71 + step*.35
                for l,r in ((a+spread,a+spread+.11),(b-spread-.11,b-spread)):
                    solid(trim,l,r,d,d+.24,paving-.10,opening_top-step*.085,m["orange"])
                solid(trim,a+spread,b-spread,d,d+.24,opening_top-.15-step*.085,opening_top-step*.085,m["orange"])
            # Dark glass reads as the visible deep lobby end. The public survey
            # follows the exterior flags up to the registered threshold.
            solid(frame,a+.48,b-.48,7.93,8.06,paving-.25,opening_top-.26,m["deep"])
            for f in (.31,.63):
                u=a+f*(b-a)
                solid(trim,u-.033,u+.033,7.85,7.94,paving,opening_top-.26,m["metal"])
            continue
        sill = max(floor_base+.07,paving+.30) if i in (2,3,4) else paving+.17
        top = max(sill+1.65,28.86)
        solid(frame,a+.17,b-.17,5.96,6.65,paving-.43,sill,m["basalt"])
        solid(frame,a+.23,b-.23,glazing,glazing+.07,sill,top,m["glass"] if i%3 else m["shadowglass"])
        solid(trim,a+.19,b-.19,glazing-.13,glazing+.02,sill+.07,sill+.16,m["metal"])
        solid(trim,a+.20,b-.20,glazing-.1,glazing+.01,top-.1,top+.06,m["metal"])
        if i not in (0,6,10):
            solid(trim,a+.18,b-.18,5.90,6.62,top-.05,top+.17,m["awning"])
        for fraction in (.31,.67):
            u=a+fraction*(b-a)
            solid(trim,u-.037,u+.037,glazing-.07,glazing+.05,sill,top,m["metal"])
    # Upper fabric has sills, stone piers and a mixed rhythm of glazing and
    # recessed vents, with no visible residential interior behind the glass.
    for row,lower in enumerate([29.48,32.72,35.96]):
        for i,(a,b) in enumerate(zip(storefronts,storefronts[1:])):
            l,r=a+.22,b-.22
            solid(frame,l,r,5.98,7.15,lower,lower+.57,m["stone"])
            solid(frame,l,r,6.58,6.67,lower+.57,lower+2.68,m["glass"] if (i+row)%4 else m["shadowglass"])
            solid(trim,l,r,5.80,6.51,lower+.53,lower+.63,m["edge"])
            for fraction in (.39,.70):
                u=l+fraction*(r-l)
                solid(trim,u-.043,u+.043,6.51,6.60,lower+.63,lower+2.67,m["metal"])
            solid(frame,l,r,5.92,7.4,lower+2.68,min(roof,lower+3.25),m["rib"])
            if (i+2*row)%5==0:
                for k in range(5):
                    z=lower+.79+k*.185
                    solid(trim,l+.18,r-.20,6.42,6.55,z,z+.052,m["metal"])
    return [frame.save(),trim.save()]


def paving(ground,m):
    path=Mesh("COL_Panda228_PublicFlagstones")
    curb=Mesh("COL_Panda228_CurbsAndLedge")
    detail=Mesh("Panda228_TactileAndShelter")
    trees=[]
    start, stop = 8., 59.4

    def top(s,d,lift):
        p=en(s,d)
        return (*p,ground(s,d)+lift)

    def band(mesh,a,b,c,d,h0,h1,finish,width_steps=1):
        steps=ceil((b-a)/.55)
        for i in range(steps):
            s,t=a+(b-a)*i/steps,a+(b-a)*(i+1)/steps
            for j in range(width_steps):
                f,g=j/width_steps,(j+1)/width_steps
                v,w=c+(d-c)*f,c+(d-c)*g
                low,high=h0+(h1-h0)*f,h0+(h1-h0)*g
                mesh.face([top(s,v,low),top(t,v,low),top(t,w,high),top(s,w,high)],finish)

    # Stable planted/road-side edge, clear footway, and the approach apron.
    band(path,start,stop,-2.75,-.62,.081,.129,m["street"],7)
    band(path,start,stop,-.62,2.20,.129,.112,m["walk"],7)
    band(path,start,stop,2.20,5.80,.112,.102,m["walk"],9)
    band(path,44.8,52.,5.80,7.83,.102,.085,m["street"],6)
    band(curb,start,stop,-2.91,-2.75,.073,.081,m["edge"])
    band(curb,start,stop,-2.91,-2.91,-.062,.073,m["basalt"])
    band(detail,8.25,58.9,.07,.39,.143,.145,m["tactile"],2)

    # Lower shop frontage seen behind the grey ledge and dark slim railing.
    band(curb,10.5,34.6,3.98,4.16,.37,.37,m["edge"])
    band(curb,10.5,34.6,3.98,3.98,.112,.37,m["basalt"])
    for k in range(15):
        s=10.6+k*1.68
        z=ground(s,4.06)+.36
        solid(curb,s-.027,s+.027,4.02,4.09,z,z+.64,m["metal"])
        if k>0:
            prior=10.6+(k-1)*1.68
            for lift in (.65,.96):
                band(curb,prior,s,4.035,4.070,lift,lift,m["metal"])

    z=ground(14.5,-1.81)+.12
    for s in [11.75,15.63,18.75]:
        bottom=ground(s,-1.78)+.11
        solid(detail,s-.045,s+.045,-1.83,-1.70,bottom,z+2.43,m["metal"])
    solid(detail,11.34,19.12,-2.10,-.69,z+2.40,z+2.60,m["canopy"])
    solid(detail,12.12,15.47,-1.72,-1.62,z+.34,z+1.96,m["panel"])
    solid(detail,16.03,18.51,-1.73,-1.64,z+.32,z+2.25,m["glass"])
    solid(detail,11.74,15.53,-1.92,-1.55,z+.45,z+.51,m["canopy"])
    # Reuse the existing street tree on the northeast end and add verified
    # tree-row typology at the same curbside band. Centres are game positions.
    for i,s in enumerate((8.9,24.9,34.8,43.25),1):
        d=-1.84
        h=ground(s,d)+.13
        for a,b,c,e in ((s-.65,s+.65,d-.54,d-.47),(s-.65,s+.65,d+.47,d+.54),
                        (s-.65,s-.57,d-.47,d+.47),(s+.57,s+.65,d-.47,d+.47)):
            solid(curb,a,b,c,e,h-.12,h+.015,m["basalt"])
        solid(curb,s-.10,s+.10,d-.11,d+.11,h-.16,h+1.75,m["trunk"])
        trees.append({"name":f"Panda228_Tree_{i:02}","donor":"Outer500_Plant_014",
                      "enu":[*en(s,d),h-.10],"yaw":[.2,1.,-.4,.6][i-1],"scale":[.96,1.09,.91,1.02][i-1]})
    return [path.save(),curb.save(),detail.save()],trees


def retire(prior, plots=PLOTS, ownership_file=HERE/"ownership.json", absent_faces=None):
    scene=bpy.context.scene
    stock=read(ASSETS/"layout.json")
    owners=read(ownership_file)
    wanted={}
    for plot in plots:
        for name,sets in owners[str(plot)].items():
            wanted.setdefault(name,Counter()).update(v for block in sets for v in block["faces"])
    for name, absent in (absent_faces or {}).items():
        assert Counter(absent) <= wanted[name], name
        wanted[name] -= Counter(absent)
    household=[i for i,d in enumerate(stock["household"]) if d["plot"] in plots]
    if household:
        with bpy.data.libraries.load(str(SCENE/"district_500/outer_district.blend"),link=True) as (_,q):
            q.objects=[STATIC_FIXTURE]
        fixture=q.objects[0]
        wanted[STATIC_FIXTURE]=Counter(fingerprint(fixture,fixture.data.polygons[i])
                            for k in household for i in range(6*k,6*k+6))
    replacements=[]
    counts={}
    for name,expected in sorted(wanted.items()):
        ob=prior["local_copy"](scene.objects[name])
        hits=[face.index for face in ob.data.polygons if fingerprint(ob,face) in expected]
        assert Counter(fingerprint(ob,ob.data.polygons[i]) for i in hits)==expected,name
        remove_faces(ob,hits)
        replacements.append(ob)
        counts[name]=len(hits)
    exact={f"{part}_{plot}" for plot in plots for part in ("COL_Outer500_Frame","Outer500_Joinery","Outer500_InteriorFloor")}
    prefixes=tuple(f"Outer500_Condenser_{plot}_" for plot in plots)+tuple(f"Outer500_Household_{i:03d}_" for i in household)
    retired=sorted(ob.name for ob in scene.objects if ob.name in exact or ob.name.startswith(prefixes))
    assert exact.issubset(retired),retired
    return replacements,retired,counts


def main(out):
    assert Path(bpy.data.filepath).name=="city_and_outer.before_panda.local.blend"
    previous=runpy.run_path(str(SCENE/"district_refresh/riverside/east_bend/build.py"))
    ground_mesh=terrain()
    def ground(s,d):
        p=en(s,d)
        hit,_,_,_=ground_mesh.ray_cast(Vector((*p,100.)),Vector((0,0,-1)),150.)
        assert hit is not None, (s,d)
        return hit.z
    finishes = {
       "stone":material("Panda warm-grey split limestone",(.71,.64,.60),"concrete_wall_006_diff_2k.jpg"),
       "rib":material("Panda striated pier revetment",(.65,.57,.50),"stone_wall_05_diff_2k.jpg"),
       "edge":material("Panda eased slab nosing",(.69,.68,.64),"concrete_floor_worn_001_diff_2k.jpg"),
       "basalt":material("Panda dark plinth",(.39,.43,.46),"stone_wall_05_diff_2k.jpg"),
       "rear":flat("Panda blind slope return",(.19,.185,.175)),
       "glass":flat("Panda slightly blue show window",(.068,.105,.112),.34),
       "shadowglass":flat("Panda deeply shaded glass",(.028,.044,.045),.43),
       "deep":flat("Panda arcade depth",(.023,.026,.021)),
       "metal":flat("Panda anodised dark grille",(.073,.085,.083)),
       "orange":flat("Panda nested amber-orange portal",(.56,.163,.039),.53),
       "tactile":flat("Panda worn amber tactile slabs",(.43,.33,.137)),
       "awning":flat("Panda worn navy-grey shop lintels",(.094,.111,.122)),
       "canopy":flat("Panda slim grey shelter",(.19,.224,.230)),
       "panel":flat("Panda shelter display backing",(.16,.232,.227)),
       "trunk":flat("Panda physical trunk core",(.141,.125,.100)),
    }
    with bpy.data.libraries.load(str(SCENE/"district_refresh/riverside/park_edge_finish/park-edge-finish.blend")) as (stock,donor):
        assert "Park Edge neutral grey stone slabs" in stock.materials
        donor.materials=["Park Edge neutral grey stone slabs"]
    finishes["walk"]=donor.materials[0]
    finishes["street"]=material("Panda smaller grey flags",(.63,.71,.83),"stone_floor_diff_2k.jpg")
    built,trees=paving(ground,finishes)
    built+=facade(ground,finishes)
    replacement,retired,counts=retire(previous)
    sites={}
    routes={
       "15":[(55.9,-.65),(53.5,.68),(51.6,2.68),(49.40,4.18),(48.54,5.53),(48.41,6.52)],
       "17":[(10.4,.79),(13.55,.86),(16.66,.91),(19.32,1.23),(22.65,1.84),(24.82,2.98)],
    }
    for plot,points in routes.items():
        xy=[list(en(*p)) for p in points]
        positions=[[xy[i][0],xy[i][1],ground(*p)] for i,p in enumerate(points)]
        sites[plot]={"stations":xy,"start_ray_y":positions[0][2]+1.35,"destination_y":positions[-1][2]+.10,
                     "street_focus":[*xy[-1],positions[-1][2]+1.75],"return_focus":[*xy[0],positions[0][2]+1.50],
                     "original_grade":positions}
    samples=[[list(en(s,d)) for d in [-2.45,-1.1,.8,2.6,3.65,5.35]]
              for s in [12.5,21.,26.5,33.,39.2,46.8,51.6,56.1]]
    data={"retired_plots":list(PLOTS),"retired_objects":retired,"removed_face_counts":counts,
          "replacement_meshes":[ob.name for ob in replacement],"new_meshes":[ob.name for ob in built],
          "route":sites,"minor_cross_sections":samples,"trees":trees,
          "portal_sign":{"enu":[*en(48.4,5.65),29.18],"yaw":atan2(TANGENT.y,TANGENT.x)},
          "nonpublic_depth_behind_portal":7.93,"route_axis":"OpenStreetMap footway 734116598"}
    keep=set(built+replacement)
    for ob in list(bpy.data.objects):
        if ob not in keep:
            bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"panda-15-17.blend"),compress=True,relative_remap=True)
    donor=read(ASSETS/"houci-77.json")["borrowed_materials"]
    data["borrowed_materials"]=previous["borrow_slots"](replacement,{name:set(values.values()) for name,values in donor.items()})
    bpy.ops.export_scene.gltf(filepath=str(out/"panda-15-17.glb"),export_format="GLB",export_cameras=False,export_lights=False)
    (out/"panda-15-17.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print("CQ_PANDA_BUILD",counts,retired,list(sites),len(trees))


if __name__=="__main__":
    main(Path(sys.argv[-1]).resolve())
