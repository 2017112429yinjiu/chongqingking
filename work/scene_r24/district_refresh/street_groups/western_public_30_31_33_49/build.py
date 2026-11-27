"""Build the west slope's registered public stone edges."""
import json
from math import ceil
from pathlib import Path
from random import Random
import runpy
import sys

import bpy

HERE = Path(__file__).resolve().parent
common = runpy.run_path(str(HERE.parent/"north_edges/build.py"))
Mesh, Edge, material, tint = (common[k] for k in ("Mesh","Edge","material","tint"))


def finishes():
    mats, bindings = {}, {}
    for key, name, tint_rgb, image in (
        ("flags","West slope weathered grey flags",(.77,.79,.77),"concrete_floor_worn_001_diff_2k.jpg"),
        ("border","West slope dressed stone lip",(.551,.573,.549),"concrete_floor_worn_001_diff_2k.jpg"),
        ("ashlar","West slope irregular damp ashlar",(.548,.566,.535),"stone_wall_05_diff_2k.jpg"),
        ("wet","West slope shaded lower stone courses",(.369,.408,.366),"stone_wall_05_diff_2k.jpg"),
        ("grey","West slope cold grey dressed stones",(.60,.599,.558),"stone_wall_05_diff_2k.jpg"),
        ("warm","West slope grey brown ashlar accents",(.588,.533,.452),"stone_wall_05_diff_2k.jpg"),
    ):
        mats[key] = material(name,tint_rgb,image)
        bindings[name] = "res://assets/chongqing_district_"+image
    mats["leaf"] = tint("West slope low retaining wall greenery",(.129,.215,.072))
    mats["ivy_young"] = tint("West slope young ivy tips",(.178,.275,.079))
    mats["ivy_shade"] = tint("West slope ivy deep green",(.070,.133,.046))
    mats["cut"] = tint("West slope scattered old stone tool scars",(.43,.405,.345))
    mats["pipe"] = tint("West slope weathered zinc downpipe",(.31,.35,.37),.46)
    mats["pipe_dark"] = tint("West slope original pipe clamps",(.17,.20,.205),.62)
    return mats, bindings


def surface(edge, code, mats):
    path,height = common["graded_footway"](edge,0.,mats)
    path.name = f"COL_Western{code}_OutdoorStoneFlags"
    start = 1.55 if code=="33" else .52
    stations = [start+(edge.stations[-1]-start-.52)*i/6. for i in range(7)]
    route = [(*edge.en(s,0.),height(s)) for s in stations]
    skirt = Mesh(f"Western{code}_SteppedMargins")
    rng = Random(code)
    length = edge.stations[-1]
    side = -.91 if code in ("31","49") else .92
    # The old housing threshold is unreconciled. Finish only the visible verge.
    count = ceil((length-.38)/.62)
    for i in range(count):
        a=.19+i*(length-.38)/count
        b=.19+(i+1)*(length-.38)/count
        near, far = sorted((side,side+.165*(1 if side>0 else -1)))
        common["box"](skirt,edge,a,b,near,far,.011,.14,mats["border"])
        if code=="49" or (code=="31" and 2<=i<7):
            # Break the low stone face into non-uniform courses and retain the steep ground behind it.
            top = rng.uniform(.34,.52) if code in ("30","49") else rng.uniform(.5,.74)
            common["box"](skirt,edge,a+.009,b-.012,near,far,-.061,top,mats["wet"] if i%3==1 else mats["ashlar"])
        if code=="31" and i%2==0:
            stem=edge.at(a+.11,far,.24)
            for k in range(3):
                p = edge.at(a+k*.12,far + rng.uniform(-.075,.075),.38+rng.uniform(.0,.17))
                skirt.face([stem,p,(p[0]+.093,p[1]+.041,p[2]+.047)],mats["leaf"])
    result = [path,skirt.save()]
    if code in ("30","31","49"):
        # Join the new flag surface back to the old verified street height at each end.
        joins = Mesh(f"COL_Western{code}_ExistingStreetJoins")
        for base,span in ((0.,-.81),(length,.91)):
            for c,d in ((-.66,-.33),(-.33,0.),(0.,.33),(.33,.66)):
                a,b = edge.en(base,c),edge.en(base,d)
                u,v = edge.en(base+span,c),edge.en(base+span,d)
                first = [(*a,height(base)),(*b,height(base))]
                last = [(*u,edge.ground_y(u)+.013),(*v,edge.ground_y(v)+.013)]
                ring = [last[0],*first,last[1]] if span<0. else [first[0],*last,first[1]]
                joins.face(ring[:3],mats["flags"])
                joins.face([ring[0],ring[2],ring[3]],mats["flags"])
                skirts = []
                if c==-.66:
                    skirts.append((first[0],last[0]))
                if d==.66:
                    skirts.append((last[1],first[1]))
                for positive,negative in skirts:
                    if span<0.:
                        positive,negative = negative,positive
                    joins.face([positive,negative,
                        (negative[0],negative[1],edge.ground_y(negative[:2])-.043),
                        (positive[0],positive[1],edge.ground_y(positive[:2])-.043)],mats["border"])
        result.append(joins.save())
    return result, route


def build(out):
    field=json.loads((HERE/"field.json").read_text())
    terrain=common["terrain"]()
    mats,bindings=finishes()
    layer,walks=[],{}
    for code,points in field["public_lines"].items():
        edges,walks[code]=surface(Edge(points,terrain),code,mats)
        layer.extend(edges)
    fit = field["registered_2015_wall_pipe"]
    layer.extend(runpy.run_path(str(HERE/"wall33.py"))["wall"](common,terrain,fit,mats))
    helper = runpy.run_path(str(HERE.parent/"panda_15_17/build.py"))
    previous = runpy.run_path(str(HERE.parents[1]/"riverside/east_bend/build.py"))
    replacements,retired,counts = helper["retire"](previous,(33,),HERE/"ownership-33.json")
    retired.extend(name for name in ("COL_Outer500_Court_33","Outer500_CourtDetails_33")
                   if name in bpy.context.scene.objects)
    earlier = json.loads((common["ASSETS"]/"jiefang-public-02-24-25-26.json").read_text())["borrowed_materials"]
    material_slots = {obj.name: {slot.name:earlier[obj.name][slot.name]
                      for slot in obj.data.materials if slot and slot.name in earlier.get(obj.name,{})}
                      for obj in replacements}
    for obj in list(bpy.data.objects):
        if obj not in layer+replacements:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    for obj in replacements:
        for slot in obj.material_slots:
            if slot.material and slot.material.library:
                slot.material = slot.material.make_local()
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    name="western-public-30-31-33-49"
    bpy.ops.wm.save_as_mainfile(filepath=str(out/f"{name}.blend"),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(out/f"{name}.glb"),export_format="GLB",export_image_format="NONE",
                              export_cameras=False,export_lights=False)
    manifest = dict(new_meshes=[obj.name for obj in layer],replacement_meshes=[obj.name for obj in replacements],
                    retired_plots=[33],retired_objects=retired,borrowed_materials=material_slots,
                    retired_plot_faces=counts,walks=walks,surface_textures=bindings)
    (out/f"{name}.json").write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=="__main__":
    build(Path(sys.argv[-1]).resolve())
