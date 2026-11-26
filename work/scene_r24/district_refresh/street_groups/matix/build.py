"""Build the registered Matix Street public passage from the exact outer source."""
import argparse
import json
from pathlib import Path
import sys

import bpy

HERE = Path(__file__).resolve().parent
SCENES = HERE.parents[2]
ASSETS = HERE.parents[3] / 'project/chongqing_godot_v05/assets/district_500'
sys.path[:0] = [str(HERE), str(HERE.parent), str(SCENES / 'district_500')]
from frontage import build_verges
from rear_stair import build_rear_stair
from retaining import open_crossings
from retire_plots import replace_shared_geometry
from riverside import make_strip, material, terrain_faces


def read(path):
    return json.loads(path.read_bytes())


def main(output, mapping):
    if Path(bpy.data.filepath).name != 'outer_district.blend':
        raise RuntimeError('Open the original outer_district.blend before export.')
    layout = read(ASSETS / 'layout.json')
    factory = read(ASSETS / 'match_factory.json')
    registration = read(HERE.parent / 'run/plot-registration.json')
    ways = registration['ways']
    retired_by = {7: 1025797976, 23: 59146654, 36: 59146654, 37: 59146654, 39: 59146654}
    owners = read(mapping)
    replacements, old_meshes = replace_shared_geometry(owners, list(retired_by) + factory['retired_trials'], layout,
        SCENES / 'district_500/interior_terrain.blend')
    openings = open_crossings(ways, read(HERE / 'retaining-owners.json'), owners)
    tile_faces = list(terrain_faces())
    stone = material('Matix worn dark stone setts', (.55, .57, .56), 'stone_floor_diff_2k.jpg')
    ash = material('Matix grey ashlar edge', (.66, .68, .68), 'concrete_floor_worn_001_diff_2k.jpg')
    new = []
    for oid, name, width in [('59146654','Matix_cartway',3.12), ('1025797976','Liangtingzi_lane',2.51)]:
        strip = make_strip({'id': name, 'points': ways[oid]['east_north'], 'width_m': width,
                            'finish': 0, 'raise_m': .021}, tile_faces, [stone, stone, ash])
        strip.name = 'Outer500_' + name
        new.append(strip)
    rear, stair_plan = build_rear_stair(next(p for p in layout['plots'] if p['plot_id'] == 43),
                                      ways['1025797976']['east_north'])
    edging, curb_plan = build_verges(ways)
    new += [rear, edging]
    manifest = {'replacement_meshes': [obj.name for obj in replacements],
                'retired_objects': sorted(set(old_meshes) - set(factory['retired_objects'])),
                'retired_by': retired_by, 'new_meshes': [obj.name for obj in new],
                'wall_openings': openings, 'rear_stair': stair_plan, 'curbs': curb_plan,
                'walk_ways': [59146654, 1025797976, 1025797980], 'source_sha256': registration['source_sha256'],
                'spawn_east_north': ways['59146654']['east_north'][6]}
    retained = set(new + replacements)
    for obj in list(bpy.data.objects):
        if obj not in retained:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output / 'matix_streets.blend'), compress=True)
    bpy.ops.export_scene.gltf(filepath=str(output / 'matix_streets.glb'), export_format='GLB',
                             export_cameras=False, export_lights=False)
    (output / 'matix_streets.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('ownership', type=Path)
    options = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    main(options.output.resolve(), options.ownership)
