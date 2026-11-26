"""Remove verified old plot faces from the latest shared meshes, preserving earlier fits."""
from collections import Counter
import json
from pathlib import Path

import bpy

from retire_plots import STATIC_FIXTURE, fingerprint, remove_faces

HERE = Path(__file__).resolve().parent
SCENES = HERE.parents[1]
ASSETS = SCENES.parent / 'project/chongqing_godot_v05/assets/district_500'


def read(path):
    return json.loads(path.read_bytes())


def load_current(name, donor):
    original = bpy.data.objects.get(name)
    if not donor:
        return original
    if original:
        bpy.data.objects.remove(original, do_unlink=True)
    with bpy.data.libraries.load(str(donor), link=False) as (source, output):
        if name not in source.objects:
            raise ValueError(f'{name} is missing from {donor}')
        output.objects = [name]
    obj = output.objects[0]
    assert obj.name == name
    bpy.context.scene.collection.objects.link(obj)
    return obj


def latest_donors(extra=()):
    sources = [
        (read(ASSETS / 'interior_terrain.json')['tiles_and_wall'], SCENES / 'district_500/interior_terrain.blend'),
    ]
    upstream = [
        ('match_factory', HERE / 'match_factory.blend'),
        ('matix_streets', HERE / 'matix/matix_streets.blend'),
        ('zhongxing-retaining', HERE / 'zhongxing/zhongxing-retaining.blend'),
        ('west-court', HERE.parent / 'riverside/west_court/west-court.blend'),
        *extra,
    ]
    for manifest, donor in upstream:
        plan = read(ASSETS / (manifest + '.json'))
        sources.append((plan['replacement_meshes'] + plan.get('new_meshes', []), donor))
    return {name: donor for names, donor in sources for name in names}


def strip_plots(ownership, plots, layout, donors):
    grouped = {}
    for pid in plots:
        for name, pieces in ownership[str(pid)].items():
            grouped.setdefault(name, Counter()).update(face for piece in pieces for face in piece['faces'])
    household = [i for i, item in enumerate(layout['household']) if item['plot'] in plots]
    contact = bpy.data.objects[STATIC_FIXTURE]
    assert len(contact.data.polygons) == 6 * len(layout['household'])
    if household:
        grouped[STATIC_FIXTURE] = Counter(fingerprint(contact, contact.data.polygons[i])
                                         for row in household for i in range(6 * row, 6 * row + 6))
    replacements, removed_counts = [], {}
    for name, wanted in sorted(grouped.items()):
        target = load_current(name, donors.get(name))
        hits, found = [], Counter()
        for face in target.data.polygons:
            key = fingerprint(target, face)
            if key in wanted:
                hits.append(face.index)
                found[key] += 1
        if wanted != found:
            raise ValueError(f'{name} plot ownership differs. Missing {sum((wanted - found).values())}, surplus {sum((found - wanted).values())}.')
        remove_faces(target, hits)
        removed_counts[name] = len(hits)
        replacements.append(target)
    prefixes = tuple(f'Outer500_Household_{i:03d}_' for i in household)
    prefixes += tuple(f'Outer500_Condenser_{pid:02d}_' for pid in plots)
    whole = {f'{prefix}_{pid:02d}' for pid in plots for prefix in (
        'COL_Outer500_Frame', 'Outer500_Joinery', 'Outer500_InteriorFloor',
        'COL_Outer500_Court', 'Outer500_CourtDetails')}
    retired = sorted(obj.name for obj in bpy.context.scene.objects if obj.name in whole or obj.name.startswith(prefixes))
    return replacements, retired, removed_counts
