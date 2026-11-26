"""Build the two registered towers, a grounded passage and the Match Factory glazing."""
import argparse
import json
from math import ceil, cos, sin
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENES = HERE.parents[2]
sys.path[:0] = [str(HERE), str(HERE.parent), str(SCENES / 'district_500')]
from factory import Mesh, build as factory_build, terrain
from factory_glazing import Glazing, glaze_material
from refresh_geometry import ASSETS, latest_donors, read, strip_plots
from riverside import make_strip, material, terrain_faces

PLOT_IDS = (74, 75, 76)
FACTORY_OBJECTS = ('COL_Guoco_MatchFactory_704006706', 'Guoco_MatchFactory_BrickPiersAndCasements', 'Guoco_MatchFactory_HippedGableSmallTiles')
WALKS = {
    'frontage_lower': [[138,-99.4],[145,-100],[157,-99.6],[164,-95.6],[176,-95.5],[188,-94.9],[202,-95],[216,-94]],
    'between_towers': [[192,-99],[192,-91],[192,-82],[192,-75],[192,-66],[192,-57],[191,-51]],
    'frontage_upper': [[177,-54],[184,-53],[193,-53],[201,-53],[206,-49],[219,-46]],
}


def xyz(p, z):
    return (p.x, p.y, z)


def samples(ring, pitch):
    return [a.lerp(b, i / parts) for a, b in zip(ring, ring[1:]+ring[:1])
            for parts in [max(1,ceil((b-a).length/pitch))] for i in range(parts)]


def tower(oid, label, raw, floors, height, ground, finishes):
    ring = [Vector(p) for p in raw]
    perimeter = samples(ring, 2.45)
    centre = sum(ring, Vector((0.,0.))) / len(ring)
    levels = [ground(p) for p in samples(ring, 3.)]
    foot = sorted(levels)[len(levels)//2]
    support = Mesh(f'COL_Guoco_{label}_{oid}')
    low = min(levels)-.35
    support.solid([xyz(p,low) for p in ring], [xyz(p,foot+2.2) for p in ring], finishes['stone'])
    # This closed upper envelope provides a body for external cameras and collisions.
    core = [centre+(p-centre)*.94 for p in ring]
    support.solid([xyz(p,foot+2.2) for p in core], [xyz(p,foot+height-.34) for p in core], finishes['dark'])
    finish = Mesh(f'Guoco_{label}_RibbonWindowsAndCrown')
    field = finishes['glass']
    crown = 4.1 if label == 'T1' else 5.2
    pitch = (height-crown-2.2)/floors

    def scale(t):
        return .964 + .035*sin(t*1.6) + .004*sin(t*4.3)

    def on_face(p, fraction, extension=0.):
        x, y = p-centre
        angle = .028 * sin(fraction*2.6) * (1 if label=='T1' else -1)
        return centre+Vector((x*cos(angle)-y*sin(angle), x*sin(angle)+y*cos(angle))) * (scale(fraction)+extension)

    for floor in range(floors):
        u, v = floor/floors, (floor+1)/floors
        z, top = foot+2.2+pitch*floor, foot+2.2+pitch*(floor+1)
        for i, (p,q) in enumerate(zip(perimeter,perimeter[1:]+perimeter[:1])):
            band = .38 if i%13 in (0,1,2) else .25
            # Panel shade follows orientation, with sparse dark interior shutters.
            idx = (2*(i//4)%5 + int((floor*7+i*11)%17==0)) % len(field)
            a, b = on_face(p,u), on_face(q,u)
            c, d = on_face(q,v), on_face(p,v)
            finish.face([xyz(a,z+band),xyz(b,z+band),xyz(c,top),xyz(d,top)],field[idx])
            finish.face([xyz(on_face(p,u,.004),z),xyz(on_face(q,u,.004),z),
                         xyz(on_face(q,u,.004),z+band),xyz(on_face(p,u,.004),z+band)], finishes['bronze'])
            seam = p.lerp(q,min(.18,.13/(q-p).length))
            finish.face([xyz(on_face(p,u,.0065),z+band),xyz(on_face(seam,u,.0065),z+band),
                         xyz(on_face(seam,v,.0065),top),xyz(on_face(p,v,.0065),top)], finishes['fin'])
    deck = [on_face(p,1.) for p in ring]
    setback = [centre+(p-centre)*.92 for p in deck]
    head = foot+height
    finish.solid([xyz(p,head-crown) for p in deck],[xyz(p,head-crown+.62) for p in deck],finishes['bronze'])
    finish.solid([xyz(p,head-crown+.62) for p in setback],[xyz(p,head-.38) for p in setback],finishes['coal_glass'])
    finish.solid([xyz(p,head-.46) for p in setback],[xyz(p,head) for p in setback],finishes['bronze'])
    return [support.save(),finish.save()], {'way':oid,'storeys':floors,'height_m':height,'datum_in_game_m':foot,
            'terrain_min_max_m':[min(levels),max(levels)],'foundation_lap_m': min(levels)-low,
            'roof_game_m':head, 'outline_east_north':raw}


def podium(ground, finish):
    supporting = Mesh('COL_Guoco_PodiumPublicPassage')
    trim = Mesh('Guoco_PodiumScreenAndGalleries')
    wings = [([(169,-83),(188,-83),(188,-67),(169,-67)],.6),
             ([(197,-83),(211,-83),(211,-67),(197,-67)],.22)]
    grade = max(ground(Vector(p)) for p in [(188,-76),(192,-76),(197,-76),(192,-68)])
    soffit = grade+4.25
    for corners, raise_roof in wings:
        ring = [Vector(p) for p in corners]
        bottom = min(ground(p) for p in samples(ring,2.5))-.24
        supporting.solid([xyz(p,bottom) for p in ring],[xyz(p,soffit+3.2+raise_roof) for p in ring],finish['stone'])
        centre = sum(ring, Vector((0.,0.)))/len(ring)
        for i, (a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
            out = Vector((b.y-a.y,a.x-b.x)).normalized()*.045
            line = [a.lerp(b,j/max(1,ceil((b-a).length/2.4)))+out for j in range(1+max(1,ceil((b-a).length/2.4)))]
            for bay,(p,q) in enumerate(zip(line,line[1:])):
                grade_here = max(ground(p),ground(q))
                for storey, z in enumerate((soffit-2.26,soffit+.14)):
                    if z < grade_here+.25:
                        continue
                    left, right = p.lerp(q,.10), p.lerp(q,.90)
                    lip = out.normalized()*.10

                    def panel(a, b, low, high, surface, step=0.):
                        a, b = a+lip*step, b+lip*step
                        trim.face([xyz(a,low),xyz(b,low),xyz(b,high),xyz(a,high)],surface)

                    window = finish['glass'][(bay+i+storey)%4]
                    panel(left,right,z,z+1.85,finish['dark'])
                    for start, end in ((.055,.305),(.35,.60),(.65,.945)):
                        panel(left.lerp(right,start),left.lerp(right,end),z+.09,z+1.75,window,1.)
                    for t in (0.,.323,.623,.935):
                        panel(left.lerp(right,t),left.lerp(right,t+.065),z,z+1.85,finish['bronze'],1.4)
                    for top in (z,z+1.75):
                        panel(left,right,top,top+.10,finish['bronze'],1.4)
                    if (bay+storey)%3==0:
                        for louver in range(4):
                            h=z+.12+louver*.095
                            panel(left.lerp(right,.04),left.lerp(right,.30),h,h+.028,finish['dark'],1.2)
                # Large-format stone skirting follows the sloped frontage.
                panel_height = max(ground(p),ground(q)) + .52
                lip = out.normalized()*.022
                trim.face([xyz(p+lip,ground(p)-.03),xyz(q+lip,ground(q)-.03),
                           xyz(q+lip,panel_height),xyz(p+lip,panel_height)],finish['sockle'])
            edge = [centre+(p-centre)*1.026 for p in ring]
        trim.solid([xyz(p,soffit+3.18+raise_roof) for p in edge],
                   [xyz(p,soffit+3.36+raise_roof) for p in edge],finish['bronze'])
    bridge = [Vector(p) for p in ((187.8,-77.8),(197.2,-77.8),(197.2,-68.),(187.8,-68.))]
    supporting.solid([xyz(p,soffit) for p in bridge],[xyz(p,soffit+.46) for p in bridge],finish['stone'])
    supporting.solid([xyz(p,soffit+2.67) for p in bridge],[xyz(p,soffit+2.91) for p in bridge],finish['bronze'])
    for j in (0,2):
        a,b=bridge[j],bridge[j+1]
        offset=Vector((b.y-a.y,a.x-b.x)).normalized()*.015
        count=12
        for k in range(count):
            p,q=a.lerp(b,k/count)+offset,a.lerp(b,(k+1)/count)+offset
            r=p.lerp(q,.12)
            trim.face([xyz(p,soffit+.46),xyz(r,soffit+.46),xyz(r,soffit+2.67),xyz(p,soffit+2.67)],finish['fin'])
            trim.face([xyz(r,soffit+.46),xyz(q,soffit+.46),xyz(q,soffit+2.67),xyz(r,soffit+2.67)],finish['glass'][k%3])
    return [supporting.save(),trim.save()], {'soffit_game_m':soffit, 'graded_headroom_m': 4.25,
                                            'span_east_north':[list(v) for v in bridge]}


def make_materials():
    return {
        'glass':[glaze_material(f'Guoco glass ribbon {i}',c,.29,.39) for i,c in enumerate((
            (.081,.138,.179),(.115,.177,.205),(.128,.201,.231),(.057,.100,.132),(.109,.157,.168)))],
        'bronze':glaze_material('Guoco matte warm metal bands',(.33,.209,.101),.43,.48),
        'fin':glaze_material('Guoco warm champagne fins',(.48,.311,.147),.40,.52),
        'coal_glass':glaze_material('Guoco setback crown dark glazing',(.053,.086,.112),.30,.45),
        'dark':glaze_material('Guoco shadow slab interior',(.068,.085,.100),.73),
        'stone':material('Guoco stone at the street threshold',(.69,.65,.58),'concrete_floor_worn_001_diff_2k.jpg'),
        'sockle':material('Guoco charcoal grey wall skirting',(.36,.37,.35),'stone_wall_05_diff_2k.jpg'),
        'paving':material('Guoco dark grey traffic apron setts',(.53,.57,.59),'stone_floor_diff_2k.jpg'),
        'drain':material('Guoco open stone edge drainage',(.26,.28,.26),'stone_wall_05_diff_2k.jpg'),
    }


def main(out):
    assert bpy.app.version[:3] == (4,3,2)
    output = Path(out).resolve()
    output.mkdir(parents=True,exist_ok=True)
    registration=read(HERE/'field-registration.json')
    layout=read(ASSETS/'layout.json')
    donors=latest_donors()
    terrain_bvh=terrain()
    terrain_tiles=list(terrain_faces())

    def ground(p):
        hit, _, _, _ = terrain_bvh.ray_cast(Vector((p.x,p.y,120.)),Vector((0.,0.,-1.)))
        if hit is None:
            raise ValueError(f'No source terrain at {p!r}')
        return hit.z

    finishes=make_materials()
    replacements, retired, counts = strip_plots(read(HERE/'owned-faces.json'),PLOT_IDS,layout,donors)
    objects=[]
    towers={}
    for oid, key, floors, height in ((1374780314,'T1',42,151.),(1374780313,'T2',51,193.)):
        parts, towers[key] = tower(oid,key,registration['ways'][str(oid)]['east_north'],floors,height,ground,finishes)
        objects.extend(parts)
    pad, lower = podium(ground,finishes)
    objects.extend(pad)
    for name in ('between_towers','frontage_upper'):
        walkway = make_strip({'id':name,'points':WALKS[name],'width_m':2.45,'raise_m':.020,'finish':0},
                             terrain_tiles,[finishes['paving'],finishes['stone'],finishes['stone']])
        walkway.name = 'Guoco_Public_' + name
        objects.append(walkway)
    glazing=Glazing()
    factory, _, local = factory_build(read(HERE.parent/'factory.json'), terrain_bvh,glazing)
    assert tuple(obj.name for obj in factory) == FACTORY_OBJECTS
    for label, v, width, slot, rise in (('FactoryRoadKerb',-3.37,.28,0,.032),('FactoryStoneDrain',-3.68,.26,1,.019)):
        edge = make_strip({'id':label,'points':[list(local(u,v,0)[:2]) for u in (1,7,14,22,29.)],
                           'width_m':width,'raise_m':rise,'finish':slot},terrain_tiles,[finishes['stone'],finishes['drain'],finishes['stone']])
        edge.name='Guoco_' + label
        objects.append(edge)
    rings=[[Vector(p) for p in registration['ways'][str(t['way'])]['east_north']] for t in towers.values()]

    def inside(e,n,ring):
        return sum((a.y>n)!=(b.y>n) and e < (b.x-a.x)*(n-a.y)/(b.y-a.y)+a.x
                   for a,b in zip(ring,ring[1:]+ring[:1]))%2 == 1

    uprooted = [item['east_north_up'][:2] for item in layout['planting']
                if any(inside(*item['east_north_up'][:2],ring) for ring in rings)]
    manifest = {'replacement_meshes':[o.name for o in replacements+factory], 'retired_objects':retired,
                'new_meshes':[obj.name for obj in objects], 'retired_plots':list(PLOT_IDS), 'retired_source_faces':counts,
                'towers':towers,'podium':lower,'ground_walks':WALKS,'retired_roots_east_north':uprooted,
                'factory_glazing':{'openings':glazing.units,'operable_leaf_demonstrations':glazing.opened},
                'source_osm_sha256':registration['osm_sha256'],'attribution':registration['attribution']}
    keep = set(objects + replacements + factory)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'guoco-frontages.blend'),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(output/'guoco-frontages.glb'),export_format='GLB',
                              export_cameras=False,export_lights=False)
    (output/'guoco-frontages.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('CQ_GUOCO_GROUP', towers['T1']['roof_game_m'], towers['T2']['roof_game_m'], lower['soffit_game_m'], counts)


if __name__ == '__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('out',type=Path)
    main(cli.parse_args(sys.argv[sys.argv.index('--')+1:]).out)
