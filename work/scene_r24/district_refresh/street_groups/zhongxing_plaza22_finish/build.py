"""Finish plot 22's public paving and supported shallow planter."""
import json
from math import cos, floor, pi, sin
from pathlib import Path
from random import Random
import runpy
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
common = runpy.run_path(str(HERE.parent / "north_edges/build.py"))
Mesh, material, tint = (common[k] for k in ("Mesh", "material", "tint"))
earth = runpy.run_path(str(HERE.parents[2] / "district_500/interior_terrain.py"))
tree_limb = runpy.run_path(str(HERE.parent / "panda_15_17/build.py"))["tree_limb"]


def grade(east, north):
    return 34.766 + .021 * (north - 81.42) - .009 * (east - 112.)


def palette():
    mats, textures = {}, {}
    for key, label, color, texture in (
        ("joint", "Zhongxing22 pale grey stone repair mortar", (.43,.45,.43), "concrete_floor_worn_001_diff_2k.jpg"),
        ("stone", "Zhongxing22 plain grey flag paving", (.77,.78,.75), "concrete_floor_worn_001_diff_2k.jpg"),
        ("light", "Zhongxing22 weather-smoothed light flag paving", (.83,.83,.80), "concrete_floor_worn_001_diff_2k.jpg"),
        ("wall", "Zhongxing22 measured planter wall", (.65,.65,.61), "stone_wall_05_diff_2k.jpg"),
        ("cap", "Zhongxing22 bush hammered grey cap stones", (.72,.74,.69), "concrete_floor_worn_001_diff_2k.jpg"),
    ):
        mats[key] = material(label, color, texture)
        textures[label] = "res://assets/chongqing_district_" + texture
    for key, label, color in (
        ("sod", "Zhongxing22 live low grass mat", (.102,.178,.053)),
        ("grass", "Zhongxing22 olive grass blades", (.154,.225,.071)),
        ("shade", "Zhongxing22 dark grass blades", (.083,.142,.064)),
        ("leaves", "Zhongxing22 landscaped glossy shrubs", (.103,.201,.064)),
        ("wood", "Zhongxing22 weathered tree stakes", (.34,.23,.128)),
        ("ties", "Zhongxing22 flexible stake ties", (.17,.161,.117)),
    ):
        mats[key] = tint(label, color, .87)
    return mats, textures


def on_grade(point, inset=0.):
    return (*point, grade(*point) + inset)


def paving(apron, outside, sides, ground, mats):
    base = Mesh("COL_Zhongxing22_ContinuousPublicApron")
    stone = Mesh("Zhongxing22_HonedFlagPavingAndReturns")
    center = sum(apron, Vector((0.,0.))) / len(apron)
    for a, b in zip(apron, apron[1:] + apron[:1]):
        base.face([on_grade(center), on_grade(a), on_grade(b)], mats["joint"])
    for row in range(floor(min(p.y for p in apron)/.58), floor(max(p.y for p in apron)/.58)+1):
        offset = .32 * (row % 2)
        for col in range(floor(min(p.x for p in apron)/.65)-1, floor(max(p.x for p in apron)/.65)+1):
            x,y = col*.65+offset,row*.58
            cell = [Vector(p) for p in ((x+.004,y+.004),(x+.646,y+.004),(x+.646,y+.576),(x+.004,y+.576))]
            for start, normal in sides:
                cell = earth["clip_polygon"](cell, lambda p: normal.dot(p-start))[0]
                if not cell:
                    break
            if earth["area"]([Vector((*p,0.)) for p in cell]) > 1e-7:
                stone.face([on_grade(p,.008) for p in cell], mats["light" if (col*13+row*23)%11 in (1,6) else "stone"])
    joins = Mesh("COL_Zhongxing22_GradeMatchedApronJoins")
    for i,a in enumerate(apron):
        j = (i+1) % len(apron)
        b, c, d = apron[j], outside[i], outside[j]
        columns = int(max((b-a).length,(d-c).length)/.55)+1
        rows = int(max((c-a).length,(d-b).length)/.45)+1

        def grid(s,t):
            inner, outer = a.lerp(b,s),c.lerp(d,s)
            mid = inner.lerp(outer,t)
            return (*mid, grade(*inner)*(1.-t)+(ground.ground_y(outer)+.019)*t)

        for col in range(columns):
            for row in range(rows):
                s,t = col/columns,row/rows
                u,v = (col+1)/columns,(row+1)/rows
                cell = [grid(s,t),grid(s,v),grid(u,v),grid(u,t)]
                joins.face(cell[:3],mats["stone"])
                joins.face([cell[0],cell[2],cell[3]],mats["stone"])
    return [base.save(), stone.save(), joins.save()]


def planter(spec, mats):
    center = Vector(spec["center"])
    turn = spec["bearing_degrees"] * pi / 180.
    along, across = Vector((cos(turn),sin(turn))), Vector((-sin(turn),cos(turn)))
    radius = spec["round_end_radius_m"]
    half = spec["straight_half_length_m"]
    coping = grade(*center) + .55
    rim = Mesh("COL_Zhongxing22_SealedStonePlanter")
    bed = Mesh("Zhongxing22_TurfAndLowShrubs")
    supports = Mesh("Zhongxing22_TripodTreeStakes")

    def shape(inset):
        return [center + along * (sign*half+(radius-inset)*cos(theta)) + across * ((radius-inset)*sin(theta))
                for sign,begin in ((1.,-pi/2),(-1.,pi/2))
                for theta in (begin+k*pi/23 for k in range(24))]

    outside, cap, pocket, soil = (shape(inset) for inset in (0.,.025,.24,.265))
    exposed = []
    for i,(a,b) in enumerate(zip(outside,outside[1:]+outside[:1])):
        j = (i+1) % len(outside)
        heel = [on_grade(p,-.11) for p in (a,b)]
        rim.face([*heel,(*b,coping-.07),(*a,coping-.07)],mats["wall"])
        rim.face([(*a,coping-.07),(*b,coping-.07),(*cap[j],coping),(*cap[i],coping)],mats["cap"])
        rim.face([(*cap[i],coping),(*cap[j],coping),(*pocket[j],coping),(*pocket[i],coping)],mats["cap"])
        rim.face([(*pocket[i],coping),(*pocket[j],coping),(*soil[j],coping-.12),(*soil[i],coping-.12)],mats["wall"])
        bed.face([(*center,coping-.12),(*soil[i],coping-.12),(*soil[j],coping-.12)],mats["sod"])
        mid = (a+b)/2
        normal = Vector(((b-a).y,-(b-a).x)).normalized()
        cap_mid = (cap[i]+cap[j]+pocket[i]+pocket[j])*.25
        exposed.append({"floor_en":list(mid+.085*normal),"wall_en":list(mid),
                        "cap_en":list(cap_mid),"cap_y":coping,
                        "base_y":grade(*mid)-.11,"test_normal":list(normal)})
    rng = Random(22)
    for _ in range(410):
        local = along*rng.uniform(-2.85,2.85)+across*rng.uniform(-1.56,1.56)
        axial = along.dot(local)
        if ((max(abs(axial)-half,0.))**2 + across.dot(local)**2) > (radius-.32)**2:
            continue
        p = center+local
        width = rng.uniform(.012,.036)
        a = rng.uniform(0,2*pi)
        height = rng.uniform(.028,.069)
        for phase in (a,a+pi/2):
            tangent = Vector((cos(phase),sin(phase)))*width
            bed.face([(*(p-tangent),coping-.12),(*(p+tangent),coping-.12),
                      (*(p+tangent*.4),coping-.12+height)], rng.choice((mats["grass"],mats["shade"])))
    for u,v,height in ((-1.8,.52,.36),(-1.54,-.46,.30),(.59,-.79,.39),(1.75,.38,.45)):
        patch = center + along*u + across*v
        for _ in range(58):
            angle = rng.uniform(0,2*pi)
            rad = rng.uniform(.04,.30)
            p = patch + Vector((cos(angle),sin(angle))) * rad
            leaf = Vector((cos(angle+.9),sin(angle+.9))) * .083
            y = coping-.09+rng.uniform(.023,height)*(1.07-rad)
            bed.face([(*(p-leaf),y),(*(p+leaf),y-.018),(*p,y+.067)],mats["leaves"])
    trees = []
    for index,(u,v,scale,yaw) in enumerate(((-1.1,.52,.83,.53),(1.1,-.24,.70,2.03))):
        p = center + along*u + across*v
        base = coping-.115
        for phase in (.23, .23+2*pi/3, .23+4*pi/3):
            bearing = Vector((cos(phase),sin(phase)))
            tree_limb(supports,Vector((*(p+bearing*.49),base)),Vector((*(p+bearing*.105),base+1.29)),.033,mats["wood"])
            arc = p + bearing*.123
            tree_limb(supports,Vector((*arc,base+1.20)),Vector((*(p+bearing*.024),base+1.235)),.028,mats["ties"])
        trees.append({"donor":"Outer500_Plant_001","name":f"Zhongxing22_SupportedTree{index+1}",
                      "enu":[*p,base],"scale":scale,"yaw":yaw})
    return [rim.save(),bed.save(),supports.save()], trees, exposed


def build(out):
    field = json.loads((HERE/"field.json").read_text())
    mats, textures = palette()
    ground = common["Edge"]([(110.,81.),(111.,81.)], common["terrain"]())
    spec = field["approximate_local_plan"]
    apron = [Vector(p) for p in spec["apron_en"]]
    outside = [Vector(p) for p in spec["approach_edges_en"]]
    sides = [(a,Vector((a.y-b.y,b.x-a.x)).normalized()) for a,b in zip(apron,apron[1:]+apron[:1])]
    for a,normal in sides:
        assert all(normal.dot(p-a) > -1e-5 for p in apron), spec["apron_en"]
    layer = paving(apron,outside,sides,ground,mats)
    display, trees, exposed = planter(spec,mats)
    layer.extend(display)
    foot = [(Vector((*a,0.)),Vector((a.y-b.y,b.x-a.x,0.)).normalized())
            for a,b in zip(outside,outside[1:]+outside[:1])]
    for a,normal in foot:
        assert all(normal.dot(Vector((*p,0.))-a) > -1e-5 for p in outside), spec["approach_edges_en"]
    bounds = [(min(p[i] for p in outside),max(p[i] for p in outside)) for i in (0,1)]
    counts = {"22":0}
    regions = [("22",min(min(grade(*p) for p in apron),min(ground.ground_y(p) for p in outside))-.075,foot,bounds)]
    updates = [obj for obj in bpy.context.scene.objects if obj.name.startswith("COL_Outer500_Surface_")
               and earth["replace_terrain"](obj,regions,counts)]
    assert [obj.name for obj in updates] == ["COL_Outer500_Surface_07_06"] and counts["22"] > 0
    for obj in list(bpy.data.objects):
        if obj not in layer + updates:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    name = "zhongxing-plaza-22-finish"
    bpy.ops.wm.save_as_mainfile(filepath=str(out/f"{name}.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(out/f"{name}.glb"),export_format="GLB",export_image_format="NONE",
                              export_cameras=False,export_lights=False)
    retired = ["COL_Zhongxing22_PublicPaving","COL_Zhongxing22_RoundedStonePlanter","Zhongxing22_RecessedPlanterGround",
               "Zhongxing22_CourtyardTreeA","Zhongxing22_CourtyardTreeB"]
    walks = {"22":[on_grade(p) for p in field["walk_en"]]}
    manifest = dict(new_meshes=[x.name for x in layer], replacement_meshes=[x.name for x in updates],
                    retired_objects=retired, trees=trees, surface_textures=textures, walks=walks,
                    terrain_faces_clipped=counts["22"], exposure_sections=exposed)
    (out/f"{name}.json").write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == "__main__":
    build(Path(sys.argv[-1]).resolve())
