"""Rebuild the two registered lower Zhongxing junctions at the old plot 11."""
import json
from math import ceil
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(HERE.parent), str(SCENE / 'district_500')]
from factory import Mesh, terrain
from interior_terrain import area, clip_polygon
from refresh_geometry import ASSETS, read
from riverside import make_strip, material, terrain_faces


def clip_spur(pair, end_east):
    start, outside = map(Vector, pair)
    return [tuple(start), tuple(start.lerp(outside,(end_east-start.x)/(outside.x-start.x)))]


def lower_phoenix_spur(points, width, parent, original, brick, ash):
    """Cut the downhill side from the existing terrain, keeping the street join."""
    start, end = (Vector((*p,0.)) for p in points)
    along = (end-start).normalized()
    across = Vector((-along.y,along.x,0.))
    length = (end-start).length
    half = width/2+.20
    lead = 2.7

    def land(p):
        hit,_,_,_ = original.ray_cast(Vector((p.x,p.y,105)),Vector((0,0,-1)),125.)
        assert hit is not None, p
        return hit.z

    threshold = land(start+along*lead)

    def lower(p):
        distance = along.dot(p-start)
        center = start+along*min(length,max(0.,distance))
        ramp = min(1.,max(0.,(distance-lead)/3.5))
        dropout = min(0.,threshold-.10*(distance-lead)-land(center))
        return Vector((p.x,p.y,p.z+dropout*ramp*ramp*(3.-2.*ramp)))

    edges = [(start+along*lead,along),(end+along*.37,-along),
             (start-across*half,across),(start+across*half,-across)]
    box = [start+along*lead+across*s*half for s in (-1,1)]
    box.extend(end+across*s*half+along*.37 for s in (-1,1))
    corridor_bounds = [(min(p[i] for p in box),max(p[i] for p in box)) for i in (0,1)]
    altered = []
    for obj in list(bpy.context.scene.objects):
        if not obj.name.startswith('COL_Outer500_Surface_'):
            continue
        points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        if any(max(p[i] for p in points)<low or min(p[i] for p in points)>high
               for i,(low,high) in enumerate(corridor_bounds)):
            continue
        amended = Mesh(obj.name)
        changed = False
        for face in obj.data.polygons:
            polygon = [points[i] for i in face.vertices]
            inside = polygon
            outside = []
            for origin,direction in edges:
                inside,rejected = clip_polygon(inside,lambda p:direction.dot(p-origin))
                if area(rejected)>1e-6:
                    outside.append(rejected)
            finish = obj.data.materials[face.material_index]
            if area(inside)<1e-6:
                amended.face(polygon,finish)
                continue
            lowered = [lower(p) for p in inside]
            for part in outside+[lowered]:
                amended.face(part,finish)
            changed = True
        if changed:
            copy = parent['local_copy'](obj)
            generated = amended.save()
            copy.data = generated.data
            bpy.data.objects.remove(generated,do_unlink=True)
            altered.append(copy)
    assert altered

    # The registered side photo shows brick against the slope and grey stone
    # on the opposite side. Approximate heights follow the game section.
    edge = Mesh('COL_Fenghuangtai11_CutRetaining')
    count = ceil((length-lead)/.65)
    for side,finish in ((1,brick),(-1,ash)):
        rows=[]
        for i in range(count+1):
            distance=lead+(length-lead)*i/count
            point=start+along*distance+across*(side*half)
            point.z=land(point)
            rows.append((point,lower(point)))
        for (a,b),(c,d) in zip(rows,rows[1:]):
            if max(a.z-b.z,c.z-d.z)<.01:
                continue
            face=[a,c,d,b]
            edge.face(face if side==-1 else face[::-1],finish)
    return altered,edge.save()


def main(output):
    if Path(bpy.data.filepath).name not in ('city_and_outer.local.blend','city_and_outer.before_fenghuangtai_11.local.blend'):
        raise ValueError('Open the linked city before the plot 11 layer')
    field = read(HERE/'field.json')
    ways = {part['way']:part['east_north'] for part in field['ways']}
    roads={
        176034697: (ways[176034697][7:11],5.0,.025),
        1017606351: (clip_spur(ways[1017606351][:2],249.32),4.40,.042),
        59146751: (clip_spur(ways[59146751][:2],249.32),4.15,.054),
    }
    ground = terrain()
    panda=runpy.run_path(str(HERE.parent/'panda_15_17/build.py'))
    earlier=runpy.run_path(str(SCENE/'district_refresh/riverside/east_bend/build.py'))
    asphalt = material('Fenghuangtai aggregate carriageway',(.69,.69,.68),'asphalt_02_diff_1k.jpg')
    paving = material('Huihuigou split grey paving',(.75,.74,.71),'stone_floor_diff_2k.jpg')
    edging = material('Fenghuangtai worn limestone edging',(.74,.74,.71),'concrete_floor_worn_001_diff_2k.jpg')
    brick = material('Fenghuangtai weathered brick cut edge',(.79,.66,.58),'brick_wall_08_diff_2k.jpg')
    south_points, south_width, _ = roads[1017606351]
    grades, retaining = lower_phoenix_spur(south_points,south_width,earlier,ground,brick,edging)
    bpy.context.view_layer.update()
    surface = list(terrain_faces())
    graded_ground = terrain()
    walk = [[231.14,137.45],[233.20,138.43],[235.50,139.37],[237.91,140.37],[240.20,141.25]]
    cuts = [retaining]
    for way,(points,width,delta) in roads.items():
        street = make_strip({'id':str(way),'points':points,'width_m':width,'finish':0,'raise_m':delta},surface,[asphalt,paving,asphalt])
        street.name=f'COL_Fenghuangtai11_Road_{way}'
        cuts.append(street)
    start, end = Vector(walk[0]), Vector(walk[-1])
    direction = (end-start).normalized()
    walk_edges = [start-direction*.30,end+direction*.30]
    footway = make_strip({'id':'public_stone_turn','points':walk_edges,'width_m':1.85,'finish':1,'raise_m':.083},surface,[asphalt,paving,edging])
    footway.name='COL_Fenghuangtai11_StoneTurn'
    cuts.append(footway)
    heights=[]
    for e,n in walk:
        hit,_,_,_ = graded_ground.ray_cast(Vector((e,n,110)),Vector((0,0,-1)),135.)
        assert hit is not None
        heights.append([e,n,hit.z+.083])

    replacements,retired,counts=panda['retire'](earlier,(11,),HERE/'ownership.json')
    replacements.extend(grades)
    old_stations=read(HERE/'road-stations.json')
    drive_stations={}
    for way,points in old_stations.items():
        drive_stations[way]=[]
        for e,n,_ in points:
            hit,_,_,_=graded_ground.ray_cast(Vector((e,n,109)),Vector((0,0,-1)),134.)
            assert hit is not None, (way,e,n)
            drive_stations[way].append([e,n,hit.z+roads[int(way)][2]])
    plan={'retired_plots':[11],'retired_objects':retired,'replacement_meshes':[ob.name for ob in replacements],
          'new_meshes':[ob.name for ob in cuts],'removed_face_counts':counts,'site_walk':heights,
          'projected_ways':{str(way):{'centre_enu':data[0],'width_m':data[1]} for way,data in roads.items()},
          'drive_stations':drive_stations,
          'public_limit':'The stone connection ends at the registered visible roadside apron. No house entrance or garage is represented.'}
    keep=set(cuts+replacements)
    for ob in list(bpy.data.objects):
        if ob not in keep:
            bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    donor=read(ASSETS/'houci-14-16.json')['borrowed_materials']
    donor_materials={name:set(slots.values()) for name,slots in donor.items()}
    donor_materials.update({ob.name:{material.name for material in ob.data.materials} for ob in grades})
    plan['borrowed_materials']=earlier['borrow_slots'](replacements,donor_materials)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'fenghuangtai-11.blend'),compress=True,relative_remap=True)
    bpy.ops.export_scene.gltf(filepath=str(output/'fenghuangtai-11.glb'),export_format='GLB',export_cameras=False,export_lights=False)
    (output/'fenghuangtai-11.json').write_text(json.dumps(plan,indent=2)+'\n')
    print('CQ_FENGHUANGTAI11',counts)


if __name__=='__main__':
    main(Path(sys.argv[-1]).resolve())
