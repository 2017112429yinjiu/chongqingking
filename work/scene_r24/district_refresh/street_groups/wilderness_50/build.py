"""Editable public edge of the registered Wilderness Garden ruin."""
from math import ceil, cos, radians, sin
from pathlib import Path
import json
import runpy
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(HERE.parent), str(SCENE / 'district_500')]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, read
from riverside import make_strip, material, terrain_faces


def land(ground, point):
    x, y = point
    contact, _, _, _ = ground.ray_cast(Vector((x,y,95.)),Vector((0,0,-1)),125.)
    if contact is None:
        raise ValueError(f'No game surface under {point}')
    return contact.z


def band_mesh(mesh, path, ground, width, lower, upper, finish):
    path = list(map(Vector,path))
    side = [(b-a).normalized() for a,b in zip(path,path[1:])]
    side = [Vector((-p.y,p.x)) for p in side]
    corners = [side[0]]
    for a,b in zip(side,side[1:]):
        average = (a+b).normalized()
        corners.append(average/max(.62,average.dot(b)))
    corners.append(side[-1])
    pair = [(p-n*width/2,p+n*width/2) for p,n in zip(path,corners)]
    bottom = [[(*v,land(ground,v)+low) for v in row] for row,low in zip(pair,lower)]
    top = [[(*v,land(ground,v)+high) for v in row] for row,high in zip(pair,upper)]
    for i,(a,b) in enumerate(zip(top,top[1:])):
        mesh.face((a[0],b[0],b[1],a[1]),finish)
        low,high=bottom[i:i+2]
        mesh.face((low[0],high[0],b[0],a[0]),finish)
        mesh.face((high[1],low[1],a[1],b[1]),finish)
    mesh.face((*bottom[0][::-1],*top[0]),finish)
    mesh.face((*bottom[-1],*top[-1][::-1]),finish)


def seat(mesh, number, entry, ground, stone):
    e,n,angle=entry
    east=Vector((cos(radians(angle)),sin(radians(angle))))
    north=Vector((-east.y,east.x))
    origin=Vector((e,n))
    length=[1.64,1.36,1.92,1.27][number]
    size=[(-.5,-.21),(.42,-.21),(.5,-.13),(.5,.17),(.41,.21),(-.45,.21),(-.5,.16)]
    points=[origin+east*(length*x)+north*y for x,y in size]
    surface=max(land(ground,p) for p in points)
    mesh.solid([(*p,land(ground,p)-.078) for p in points], [(*p,surface+.40) for p in points],stone)
    return {'center_en':entry[:2],'base_z':surface,'seat_z':surface+.40}


def build(out):
    field=read(HERE/'field.json')
    original=terrain()
    flags=material('Renai shallow weathered flagstones',(.76,.75,.69),'stone_floor_diff_2k.jpg')
    border=material('Renai pale broken stone nosing',(.83,.80,.72),'concrete_floor_worn_001_diff_2k.jpg')
    face=material('Renai remnant damp coursed rubble',(.69,.68,.59),'stone_wall_05_diff_2k.jpg')
    top=material('Renai remnant worn upper stones',(.80,.78,.67),'stone_wall_05_diff_2k.jpg')
    tiles=list(terrain_faces())
    course=field['footway_en']
    first,second=map(Vector,course[:2]); penultimate,last=map(Vector,course[-2:]);
    # Leave measured start and turn inside the surface, including roundoff at
    # trimmed triangle edges in the game import.
    path=[list(first-(second-first).normalized()*.55),*course[1:-1],list(last+(last-penultimate).normalized()*.60)]
    walkway=make_strip({'id':'renai_registered_public_edge','points':path,'width_m':2.2,'finish':1,'raise_m':.074},tiles,[flags,flags,border])
    walkway.name='COL_Renai50_PublicFlagstones'
    walls=Mesh('COL_Renai50_LowRelicFragments')
    crowns=Mesh('Renai50_WeatheredCoping')
    for i,anchors in enumerate(field['walls_en']):
        heights=[[.82,.93,.86,.75,.69,.79,.54],[.82,.66,.48],[.75,.65,.48],[.79,.47]][i]
        band_mesh(walls,anchors,original,.51,[-.16]*len(anchors),heights,face)
        band_mesh(crowns,anchors,original,.56,[z-.10 for z in heights],[z+.10 for z in heights],top)
    stools=Mesh('COL_Renai50_ReusedStoneSeats')
    seating=[seat(stools,i,entry,original,border) for i,entry in enumerate(field['seats_en'])]
    archive=runpy.run_path(str(SCENE/'district_refresh/riverside/east_bend/build.py'))
    panda=runpy.run_path(str(HERE.parent/'panda_15_17/build.py'))
    replacements,retired,removed=panda['retire'](archive,(50,),HERE/'ownership.json')
    additions=[walkway,walls.save(),crowns.save(),stools.save()]
    plan={'retired_plots':[50],'retired_objects':retired,'replacement_meshes':[o.name for o in replacements],
          'new_meshes':[o.name for o in additions],'removed_face_counts':removed,
          'public_route':[[*p,land(original,p)+.074] for p in course],
          'old_outline_en':field['outline_en'],'old_center_en':field['center_en'],'seats':seating,
          'scope':'The local outdoor public route ends outside the derelict fragment. Ground follows measured game levels.'}
    plan['surface_textures']={}
    for finish in (flags,border,face,top):
        image=next(node.image for node in finish.node_tree.nodes if node.type=='TEX_IMAGE')
        plan['surface_textures'][finish.name]=f'res://assets/{Path(image.filepath).name}'
    keep=set(additions+replacements)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    donor=read(ASSETS/'fenghuangtai-11.json')['borrowed_materials']
    plan['borrowed_materials']={}
    for obj in replacements:
        slots=donor[obj.name]
        # The published parent source already carries the same aliases used
        # by its exported GLB. Keep these aliases and the real runtime names.
        used={mat.name for mat in obj.data.materials}
        if not used <= slots.keys() | set(slots.values()):
            raise ValueError((obj.name,used-slots.keys()-set(slots.values())))
        plan['borrowed_materials'][obj.name]={alias:name for alias,name in slots.items() if alias in used}
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'wilderness-50.blend'),compress=True,relative_remap=True)
    bpy.ops.export_scene.gltf(filepath=str(out/'wilderness-50.glb'),export_format='GLB',export_image_format='NONE',export_cameras=False,export_lights=False)
    (out/'wilderness-50.json').write_text(json.dumps(plan,indent=2)+'\n')
    print('CQ_RENAI50',removed,plan['public_route'])


if __name__=='__main__':
    build(Path(sys.argv[-1]).resolve())
