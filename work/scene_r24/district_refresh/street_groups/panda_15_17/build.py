"""Make the two registered public bays of the Zhongxing Road Panda podium in Blender 4.3.2."""
from collections import Counter
import json
from math import atan2, ceil, cos, pi, sin
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


def tree_limb(mesh, start, end, radius, finish):
    axis=(end-start).normalized()
    radial=axis.cross(Vector((0,0,1))).normalized()
    side=axis.cross(radial)
    def ring(center, width):
        return [tuple(center+width*(cos(k*pi/4)*radial+sin(k*pi/4)*side)) for k in range(8)]
    mesh.solid(ring(start,radius),ring(end,radius*.36),finish)


def flat(name, rgb, roughness=.83):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*rgb,1)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = material.diffuse_color
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def folded_pier(mesh, position, bottom, upper, finishes):
    # Alternating chamfers and shallow diagonal joints on the street-facing stone.
    for a,b,side in ((-.155,0,-1),(0,.155,1)):
        rise = .115
        depth_a,depth_b = ((5.755,5.663) if side<0 else (5.663,5.755))
        for i in range(ceil((upper-bottom)/.255)):
            lo=bottom+i*.255
            hi=min(lo+.242,upper)
            a_low, b_low = (0,rise) if side<0 else (rise,0)
            if hi+rise > upper:
                a_low=b_low=0
            p,q=en(position+a,depth_a),en(position+b,depth_b)
            mesh.face([(*p,lo+a_low),(*q,lo+b_low),(*q,hi+b_low),(*p,hi+a_low)],finishes[0 if i%4 else 1])


def facade(ground,m):
    frame = Mesh("COL_Panda228_PodiumStructure")
    trim = Mesh("Panda228_StoneRevealsAndShops")
    signs = []
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
    for s in storefronts:
        folded_pier(trim,s,ground(s,6.25)+.35,roof-.34,(m["rib"],m["stone"]))
    # Setbacks are narrower along the bus-stop bay and deeper at the passage.
    for i,(a,b) in enumerate(zip(storefronts,storefronts[1:])):
        public_gate = a == portal[0]
        paving = ground((a+b)*.5,6.4)+.08
        glazing = 7.55 if public_gate else 6.69 + (.26 if i in (2,4,8) else 0.)
        for edge in (a,b):
            solid(frame,edge-.18,edge+.18,5.82,glazing+.24,paving-.44,roof-.16,m["stone"])
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
            for l,r in ((a+.42,a+.64),(b-.64,b-.42)):
                solid(trim,l,r,6.72,7.94,paving-.12,opening_top-.29,m["deep_stone"])
            solid(trim,a+.59,b-.59,7.34,7.93,opening_top-.29,opening_top-.12,m["deep_stone"])
            for s in [a+.94,a+1.46,b-1.39]:
                solid(trim,s-.12,s+.12,7.73,7.84,paving+.87,paving+1.75,m["muted_board"])
            for f in (.31,.63):
                u=a+f*(b-a)
                solid(trim,u-.033,u+.033,7.85,7.94,paving,opening_top-.26,m["metal"])
            continue
        sill = max(floor_base+.07,paving+.30) if i in (2,3,4) else paving+(.29 if i in (0,5,8) else .17)
        top = max(sill+1.65,28.86)
        solid(frame,a+.17,b-.17,5.96,6.65,paving-.43,sill,m["basalt"])
        glass = m["glass_clear"] if i in (1,2,4,7,11) else m["glass"] if i%3 else m["shadowglass"]
        solid(frame,a+.23,b-.23,glazing,glazing+.035,sill,top,glass)
        solid(trim,a+.18,b-.18,glazing-.23,glazing+.05,sill-.017,sill+.075,m["edge"])
        if i in (1,2,4,7,11):
            solid(trim,a+.23,b-.23,glazing+.49,glazing+.54,sill,top,m["deep_stone"])
            for j in range(3):
                h=sill+.43+j*.30
                solid(trim,a+.26,b-.28,glazing+.21,glazing+.51,h,h+.042,m["awning"])
                for k in range(3):
                    s=a+.51+(b-a-.95)*(k+.15*(j%2))/3
                    solid(trim,s,s+.17,glazing+.23,glazing+.39,h+.045,h+.21,m["ceramic"] if k%2 else m["muted_board"])
        solid(trim,a+.19,b-.19,glazing-.13,glazing+.02,sill+.07,sill+.16,m["metal"])
        solid(trim,a+.20,b-.20,glazing-.1,glazing+.01,top-.1,top+.06,m["metal"])
        if i not in (0,6,10):
            solid(trim,a+.18,b-.18,5.90,6.62,top-.05,top+.17,m["awning"])
        for fraction in (.31,.67):
            u=a+fraction*(b-a)
            solid(trim,u-.037,u+.037,glazing-.07,glazing+.05,sill,top,m["metal"])
        sign_text={2:"玉雕商行",4:"旧物陈列",7:"古玩交流",11:"小酒馆"}.get(i)
        if sign_text:
            lower=top+.08 if i in (4,7,11) else sill-.06
            solid(trim,a+.24,b-.24,5.89,6.00,lower,lower+.42,m["pale_board"] if i==2 else m["muted_board"])
            signs.append({"text":sign_text,"enu":[*en((a+b)*.5,5.878),lower+.22],"color":"#262b27" if i==2 else "#f1e6d2","pixel_size":.0037})
    # Upper fabric has sills, stone piers and a mixed rhythm of glazing and
    # recessed vents, with no visible residential interior behind the glass.
    for row,lower in enumerate([29.48,32.72,35.96]):
        for i,(a,b) in enumerate(zip(storefronts,storefronts[1:])):
            l,r=a+.22,b-.22
            solid(frame,l,r,5.98,7.15,lower,lower+.57,m["stone"])
            solid(frame,l,r,6.58,6.67,lower+.57,lower+2.68,m["glass"] if (i+row)%4 else m["shadowglass"])
            sill_depth=5.71 if (i+2*row)%3 else 5.85
            solid(trim,l,r,sill_depth,6.51,lower+.48,lower+.63,m["edge"])
            for fraction in (.39,.70):
                u=l+fraction*(r-l)
                solid(trim,u-.043,u+.043,6.51,6.60,lower+.63,lower+2.67,m["metal"])
            solid(frame,l,r,5.92,7.4,lower+2.68,min(roof,lower+3.25),m["rib"])
            if (i+2*row)%5==0:
                for k in range(5):
                    z=lower+.79+k*.185
                    solid(trim,l+.18,r-.20,6.42,6.55,z,z+.052,m["metal"])
            if (i+row)%3==1:
                for f in (.12,.76):
                    x=l+f*(r-l)
                    solid(trim,x,x+.16,6.30,6.53,lower+.74,lower+2.32,m["deep_stone"])
            if row==0:
                for k in range(ceil((r-l)/.19)):
                    s=l+k*.19
                    if s+.097 < r:
                        solid(trim,s,s+.097,5.92,5.96,lower+.07,lower+.47,m["rib"])
    return [frame.save(),trim.save()],signs


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
    for i in range(180):
        s=8.25+i*.28
        band(detail,s,s+.271,.07,.39,.132,.129,m["tactile" if i%8 else "tactile_worn"])
        for d in (.123,.208,.293,.348):
            band(detail,s+.044,s+.227,d,d+.012,.138,.135,m["tactile"])

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
    solid(detail,16.03,18.51,-1.73,-1.65,z+.32,z+2.25,m["glass_clear"])
    solid(detail,11.74,15.53,-1.92,-1.55,z+.45,z+.51,m["canopy"])
    solid(detail,12.25,15.34,-1.627,-1.608,z+.49,z+1.82,m["muted_board"])
    solid(detail,12.25,15.34,-1.755,-1.725,z+.49,z+1.82,m["muted_board"])
    for i in range(6):
        x=12.40+i*.39
        solid(detail,x,x+.27,-1.606,-1.594,z+.66,z+.75+i*.072,m["board_green"])
        solid(detail,x,x+.27,-1.765,-1.754,z+.66,z+.75+i*.072,m["board_green"])
    board=18.87
    solid(detail,board-.08,board+.08,-1.57,-1.37,z+.14,z+2.18,m["metal"])
    solid(detail,board-.23,board+.23,-1.70,-1.43,z+1.38,z+2.14,m["pale_board"])
    solid(detail,board-.23,board+.23,-1.72,-1.66,z+1.88,z+2.14,m["awning"])
    for k in range(6):
        bottom=z+1.45+k*.063
        solid(detail,board-.17,board+.16,-1.717,-1.695,bottom,bottom+.021,m["metal"] if k%2 else m["ceramic"])
    # Keep the fifth root at the measured position of the leaning trial tree.
    # The other tree-pit centres are aligned with the existing public verge.
    plantings=[(8.90,-1.84,.20,1.08),(24.90,-1.84,1.12,1.20),
               (34.80,-1.84,-.42,1.06),(43.25,-1.84,.63,1.16),(49.932,-2.094,-.13,1.11)]
    for i,(s,d,yaw,scale) in enumerate(plantings,1):
        h=ground(s,d)+.13
        for a,b,c,e in ((s-.65,s+.65,d-.54,d-.47),(s-.65,s+.65,d+.47,d+.54),
                        (s-.65,s-.57,d-.47,d+.47),(s+.57,s+.65,d-.47,d+.47)):
            solid(curb,a,b,c,e,h-.12,h+.015,m["basalt"])
        solid(detail,s-.54,s+.54,d-.46,d+.46,h-.018,h+.006,m["pit_bed"])
        for j in range(-6,7):
            o=j*.082
            if abs(o)>.18:
                solid(detail,s+o-.012,s+o+.012,d-.45,d+.45,h+.006,h+.028,m["metal"])
                solid(detail,s-.54,s+.54,d+o-.012,d+o+.012,h+.006,h+.028,m["metal"])
        radius=.175+i*.012
        root=en(s,d)
        levels=[h-.095,h+.63,h+2.59,h+4.42]
        rings=[]
        for j,up in enumerate(levels):
            r=radius*(1-j*.18)
            rings.append([(root.x+r*cos(k*pi/5),root.y+r*sin(k*pi/5),up) for k in range(10)])
        for bottom,top_ring,finish in zip(rings,rings[1:],(m["trunk_pale"],m["trunk"],m["trunk"])):
            curb.solid(bottom,top_ring,finish)
        for k in range(4):
            angle=yaw+k*pi*.51
            direction=Vector((cos(angle),sin(angle),0))
            a=Vector((*root,h+3.39+k*.22))
            b=a+direction*(.79+k*.10)+Vector((0,0,.87))
            c=b+direction*.81+Vector((0,0,.60))
            tree_limb(detail,a,b,.087,m["trunk"])
            tree_limb(detail,b,c,.046,m["trunk"])
            side=Vector((-direction.y,direction.x,0))
            tree_limb(detail,b,b+side*.67+Vector((0,0,.71)),.042,m["trunk"])
        for dx,dy in ((-.28,-.24),(.28,-.24),(-.28,.24),(.28,.24)):
            solid(detail,s+dx-.023,s+dx+.023,d+dy-.025,d+dy+.025,h+.025,h+.91,m["tree_guard"])
        for rise in (.29,.74):
            for dy in (-.24,.24):
                solid(detail,s-.30,s+.30,d+dy-.019,d+dy+.019,h+rise,h+rise+.062,m["tree_guard"])
        trees.append({"name":f"Panda228_TreeCrown_{i:02}","enu":[*root,h+1.66],"yaw":yaw,"scale":scale})
    sign={"text":"中兴路站","enu":[*en(board,-1.734),z+2.00],"color":"#e9edea","pixel_size":.0018}
    return [path.save(),curb.save(),detail.save()],trees,sign


def canopies(specs):
    donor=bpy.context.scene.objects["Outer500_Plant_014"]
    model=donor.data.copy()
    base=bpy.data.objects.new(specs[0]["name"],model)
    bpy.context.collection.objects.link(base)
    leaf_slot=next(i for i,material in enumerate(model.materials) if material.name.endswith("_leaves"))
    indices=[face.index for face in model.polygons if face.material_index!=leaf_slot or
             max(model.vertices[i].co.z for i in face.vertices)<2.05]
    remove_faces(base,indices)
    assert 10_000 < len(base.data.polygons) < len(donor.data.polygons)
    trees=[base]
    for spec in specs[1:]:
        tree=bpy.data.objects.new(spec["name"],model)
        bpy.context.collection.objects.link(tree)
        trees.append(tree)
    for tree,spec in zip(trees,specs):
        tree.location=spec["enu"]
        tree.rotation_euler.z=spec["yaw"]
        tree.scale=(spec["scale"],spec["scale"],1.08)
    return trees


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
       "rib":material("Panda striated pier revetment",(.70,.67,.63),"concrete_wall_006_diff_2k.jpg"),
       "edge":material("Panda eased slab nosing",(.69,.68,.64),"concrete_floor_worn_001_diff_2k.jpg"),
       "basalt":material("Panda dark plinth",(.39,.43,.46),"stone_wall_05_diff_2k.jpg"),
       "rear":flat("Panda blind slope return",(.19,.185,.175)),
       "glass":flat("Panda slightly blue show window",(.068,.105,.112),.34),
       "glass_clear":flat("Panda low-reflection shop panes",(.084,.116,.111),.32),
       "shadowglass":flat("Panda deeply shaded glass",(.028,.044,.045),.43),
       "deep":flat("Panda arcade depth",(.023,.026,.021)),
       "deep_stone":material("Panda recessed rubbed stone",(.32,.31,.28),"brick_wall_08_diff_2k.jpg"),
       "metal":flat("Panda anodised dark grille",(.073,.085,.083)),
       "orange":flat("Panda nested amber-orange portal",(.56,.163,.039),.53),
       "tactile":flat("Panda worn amber tactile slabs",(.43,.33,.137)),
       "tactile_worn":flat("Panda weathered tactile slab",(.35,.281,.124)),
       "awning":flat("Panda worn navy-grey shop lintels",(.094,.111,.122)),
       "canopy":flat("Panda slim grey shelter",(.19,.224,.230)),
       "panel":flat("Panda shelter display backing",(.16,.232,.227)),
       "trunk":material("Panda upright trunk bark",(.48,.45,.345),"tree_small_02_diff_2k.jpg"),
       "trunk_pale":flat("Panda lime-washed trunk",(.44,.413,.348)),
       "tree_guard":flat("Panda pale planted-tree support",(.53,.52,.46)),
       "pit_bed":material("Panda shaded grating bed",(.28,.29,.26),"leaf_scattered_gravel_diff_2k.jpg"),
       "muted_board":flat("Panda red-brown shop sign enamel",(.19,.068,.048),.64),
       "pale_board":flat("Panda off-white information board",(.54,.53,.45),.64),
       "board_green":flat("Panda subdued shelter board print",(.078,.16,.12),.64),
       "ceramic":flat("Panda glazed display accent",(.26,.42,.36),.36),
    }
    finishes["glass_clear"].node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value=.59
    with bpy.data.libraries.load(str(SCENE/"district_refresh/riverside/park_edge_finish/park-edge-finish.blend")) as (stock,donor):
        assert "Park Edge neutral grey stone slabs" in stock.materials
        donor.materials=["Park Edge neutral grey stone slabs"]
    finishes["walk"]=donor.materials[0]
    finishes["street"]=donor.materials[0]
    built,trees,shelter=paving(ground,finishes)
    front,signs=facade(ground,finishes)
    built+=front+canopies(trees)
    signs.append(shelter)
    replacement,retired,counts=retire(previous)
    assert "Outer500_Plant_014" in bpy.context.scene.objects
    retired.append("Outer500_Plant_014")
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
          "route":sites,"minor_cross_sections":samples,"trees":[],"upright_trees":trees,"visual_signs":signs,
          "portal_sign":{"enu":[*en(48.4,5.65),29.18],"yaw":atan2(TANGENT.y,TANGENT.x),"text":"中兴路熊猫古玩文化金街"},
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
