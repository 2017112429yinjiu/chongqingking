"""Build the two mapped street bends on their measured game levels."""
from pathlib import Path
import json
import math
import runpy
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = HERE.parents[2]
sys.path[:0] = [str(HERE.parent), str(SCENE / 'district_500')]
from factory import Mesh, terrain
from refresh_geometry import ASSETS, read
from riverside import make_strip, material, terrain_faces

FIELD = read(HERE/'field.json')


def hit(index, point):
    return index.ray_cast(Vector((*point, 110)), Vector((0, 0, -1)), 130)[0]


def height(index, point):
    point_on_surface = hit(index, point)
    if point_on_surface is None:
        raise ValueError(f'No measured ground at {tuple(point)}')
    return point_on_surface.z


def stations(points, spacing=.65):
    """Interpolate the registered line, keeping actual junction vertices."""
    rows = [Vector(p) for p in points]
    output = [rows[0]]
    for a,b in zip(rows,rows[1:]):
        steps = math.ceil((b-a).length/spacing)
        output.extend(a.lerp(b, t/steps) for t in range(1,steps+1))
    result=[]
    distance=0.
    for i,p in enumerate(output):
        previous, following = output[max(i-1,0)], output[min(i+1,len(output)-1)]
        tangent=(following-previous).normalized()
        lateral=Vector((-tangent.y,tangent.x))
        if i:
            distance+=(p-output[i-1]).length
        result.append((p,lateral,distance))
    return result


def smooth(t):
    t=max(0.,min(1.,t))
    return t*t*(3.-2.*t)


def solid_tops(mesh, top, bottoms, finish):
    mesh.solid([(x,y,z) for (x,y,_),z in zip(top,bottoms,strict=True)],top,finish)


def spur_structure(line, pairs, ground, concrete, galvanized):
    slab = Mesh('COL_Houci16_SpurSlab')
    piers = Mesh('COL_Houci16_SpurBearings')
    rail = Mesh('COL_Houci16_SpurGuardrail')
    length = line[-1][2]
    for i, (a, b) in enumerate(zip(pairs, pairs[1:])):
        distance = line[i][2]
        if distance < 1.3:
            continue
        # Close the underside of the running surface without changing its contact.
        # The existing deck supports the overlap. Near the merge the slab beds
        # directly into the grade. The exposed section spans the low ground.
        top = [(x,y,z-.018) for x,y,z in (a[0],b[0],b[-1],a[-1])]
        thickness = .62*smooth((length-distance)/3.)
        solid_tops(slab,top,[z-thickness for _,_,z in top],concrete)
        if not 2.3 < distance < length-4.:
            continue
        for side, sign in ((0,-1),(-1,1)):
            left, right = a[side], b[side]
            p, q = Vector(left[:2]), Vector(right[:2])
            n, m = line[i][1]*sign, line[i+1][1]*sign
            if min(left[2]-height(ground,p),right[2]-height(ground,q)) < .55:
                continue
            profile = [(p+n*.106,left[2]), (q+m*.106,right[2]),
                       (q+m*.169,right[2]), (p+n*.169,left[2])]
            if sign < 0:
                profile.reverse()
            solid_tops(rail,[(*v,z+.82) for v,z in profile],[z+.75 for _,z in profile],galvanized)
            if i%3==0:
                t=Vector((n.y,-n.x))*sign
                post=[p+t*u+n*v for u,v in ((-.041,.099),(.041,.099),(.041,.160),(-.041,.160))]
                if sign<0:
                    post.reverse()
                solid_tops(rail,[(*v,left[2]+.82) for v in post],[left[2]+.21]*4,galvanized)
    for station in (7.5,21.,34.):
        i=min(range(len(line)),key=lambda index:abs(line[index][2]-station))
        p,n,_=line[i]
        t=Vector((n.y,-n.x))
        bearing=[p+t*along+n*across for along,across in ((-.44,-.59),(.44,-.59),(.44,.59),(-.44,.59))]
        top=[(*q,pairs[i][2][2]-.57) for q in bearing]
        solid_tops(piers,top,[height(ground,q)-.10 for q in bearing],concrete)
    return [slab.save(),piers.save(),rail.save()]


def road(plot, points, ground, deck, materials):
    pale, dark, ash, brick, paint, concrete, galvanized = materials
    name = '1306489251' if plot==14 else '176968735'
    surface=Mesh(f'COL_Houci{plot}_Road_{name}')
    retaining=Mesh(f'COL_Houci{plot}_RoadsideEdges')
    details=Mesh(f'Houci{plot}_JointsAndRoadPaint')
    line=stations(points)
    length=line[-1][2]
    half=2.18 if plot==14 else 2.57
    if plot==16:
        deck_level=height(deck,line[0][0])
        tie_level=height(ground,line[-1][0])+.014
    pairs=[]
    for i,(p,n,distance) in enumerate(line):
        if plot==14:
            highest=max(height(ground,p+n*shift) for shift in (-half,-half*.5,0.,half*.5,half))
            shoulder_taper=smooth(min(distance,length-distance)/2.7)
            center=highest+.026
        else:
            over_deck=hit(deck,p)
            # At the bridge end follow the last metre of the existing grade, then
            # flatten smoothly through the berm to the lower-road merge.
            if over_deck is not None and distance < 2.3:
                center=over_deck.z+.010
            else:
                end_height=max(deck_level+.16,tie_level+.10)
                center=end_height+.15*math.sin(math.pi*distance/length)
                center=center*(1.-smooth((distance-length+8.)/8.))+tie_level*smooth((distance-length+8.)/8.)
            shoulder_taper=smooth((length-distance)/4.0)
        cross=[]
        for fraction in (-1.,-.5,0,.5,1.):
            q=p+n*(fraction*half)
            prior=height(ground,q)
            live_deck=hit(deck,q) if plot==16 and distance<2.3 else None
            if live_deck is not None:
                top=live_deck.z+.011
            else:
                aim=center-.020*abs(fraction*half)
                top=max(prior+.016,prior+.016+(aim-prior-.016)*shoulder_taper)
            cross.append((*q,top))
        pairs.append(cross)
    for i,(a,b) in enumerate(zip(pairs,pairs[1:])):
        distance=line[i][2]
        for j in range(4):
            surface.face([a[j],b[j],b[j+1],a[j+1]],pale if plot==14 else dark)
        for side in (0,-1):
            aa,bb=a[side],b[side]
            pa,pb=Vector(aa[:2]),Vector(bb[:2]); sign=-1 if side==0 else 1
            na,nb=line[i][1]*sign,line[i+1][1]*sign
            va,vb=pa+na*.17,pb+nb*.17
            rise=.105*smooth(min(distance,length-distance)/2.8)
            if plot==16:
                rise*=smooth((distance-1.6)/2.1)
            top=[aa,bb,(*vb,bb[2]+rise),(*va,aa[2]+rise)]
            if side==0: top.reverse()
            if plot==16:
                # Raised brick kerb over the concrete edge, clear of the low
                # ground and lower carriageway. Its ends blend into the deck.
                rise=.30*smooth((distance-2.)/3.)*smooth((length-distance)/4.)
                top=[(x,y,z+rise) for x,y,z in top]
                bottoms=[z-rise-.065 for _,_,z in top]
            else:
                bottoms=[min(z-.022,height(ground,Vector((x,y)))-.035) for x,y,z in top]
            # Bridge overlap needs only the running strip. The existing deck
            # and its structure remain the sole contacts there.
            if plot==14 or distance>2.05:
                solid_tops(retaining,top,bottoms,ash if plot==14 else brick)
            if plot==16 and 2.4<distance<length-5:
                q0=pa-na*.30;q1=pb-nb*.30
                out0=pa-na*.195;out1=pb-nb*.195
                marks=[(*q0,aa[2]+.015),(*q1,bb[2]+.015),(*out1,bb[2]+.014),(*out0,aa[2]+.014)]
                details.face(marks if side==-1 else marks[::-1],paint)
    measures=[]
    for index,row in enumerate(pairs):
        if 2.4<line[index][2]<length-2.4 and (index%8==0 or index==len(pairs)//2):
            measures.append([row[1],row[2],row[3]])
    objects=[obj.save() for obj in (surface,retaining,details) if obj.faces]
    # The grades keep their measured faces. Shared normals keep their joints
    # from reading as large flat triangles at the bend.
    joined=bmesh.new()
    joined.from_mesh(objects[0].data)
    bmesh.ops.remove_doubles(joined,verts=list(joined.verts),dist=.0001)
    for face in joined.faces:
        face.smooth=True
    joined.to_mesh(objects[0].data)
    joined.free()
    if plot==16:
        objects.extend(spur_structure(line,pairs,ground,concrete,galvanized))
    return objects, pairs, line, measures


def paved_route(points, material_list):
    pavement=make_strip({'id':'Zhongxing_registered_public_footway_734116598','points':points,'width_m':1.90,'finish':1,'raise_m':.044},list(terrain_faces()),material_list)
    pavement.name='COL_Zhongxing_734116598_Public_Stonewalk'
    return pavement


def main(out):
    assert Path(bpy.data.filepath).name in {'city_and_outer.before_houci_14_16.local.blend','city_and_outer.local.blend'}
    build_bridge=runpy.run_path(str(HERE.parent/'zhongxing_bridge_18_21/build.py'))
    existing=runpy.run_path(str(SCENE/'district_refresh/riverside/east_bend/build.py'))
    panda=runpy.run_path(str(HERE.parent/'panda_15_17/build.py'))
    ground=terrain()
    deck=build_bridge['deck_index']()
    galvanized=build_bridge['tint']('Zhongxing blue-grey steel road guard',(.48,.56,.61))
    finishes=(material('Houci light broom-cut road concrete',(.78,.79,.77),'concrete_floor_worn_001_diff_2k.jpg'),
              material('Zhongxing spur dark aggregate',(.75,.75,.72),'asphalt_02_diff_1k.jpg'),
              material('Ash granite kerb and retained slope foot',(.71,.71,.67),'stone_wall_05_diff_2k.jpg'),
              material('Zhongxing subdued masonry roadside abutment',(.63,.57,.53),'brick_wall_08_diff_2k.jpg'),
              material('Worn warm road lining',(.86,.84,.74),'concrete_floor_worn_001_diff_2k.jpg'),
              material('Exposed concrete of the spur bearing and slab',(.65,.66,.64),'concrete_floor_worn_001_diff_2k.jpg'),
              galvanized)
    points14=[[230.46,50.51],[238.22,68.91],[238.52,71.87],[237.78,75.14],[235.84,77.36],[226.61,80.99]]
    points16=[[188.4,7.54],[189.7151,8.4458],*FIELD['ways_enu']['176968735'][1:]]
    r14, grades14, line14, cross14=road(14,points14,ground,deck,finishes)
    r16, grades16, line16, cross16=road(16,points16,ground,deck,finishes)
    path=[[177.60,31.80],[183.76,36.94],[193.25,46.39],[198.46,51.82],[204.56,60.61],[208.07,70.70],[208.77,72.76]]
    walkway=paved_route(path,[finishes[2],material('Medium grey open sidewalk stone',(.78,.79,.77),'stone_floor_diff_2k.jpg'),finishes[2]])
    walk_by_plot={}
    for plot, points in FIELD['public_route_station_en'].items():
        measured=[]
        for p in points:
            z=height(ground,Vector(p))
            measured.append([*p,z+(.10 if plot=='18' else .044)])
        walk_by_plot[plot]=measured
    old=read(HERE/'ownership.json')
    absent={}
    from collections import Counter
    from retire_plots import fingerprint
    for group in set(old['14']) | set(old['16']):
        expected=Counter(face for plot in ('14','16') for block in old[plot].get(group,[]) for face in block['faces'])
        o=bpy.context.scene.objects[group]
        current=Counter(fingerprint(o,face) for face in o.data.polygons)
        missing=expected-current
        if missing:
            absent[group]=dict(missing)
    if absent:
        raise ValueError(f'Inspect parent ownership differences before retiring anything: {absent}')
    replacements, retired, counts=panda['retire'](existing,(14,16),HERE/'ownership.json')
    new=r14+r16+[walkway]
    keep=set(new+replacements)
    plan={'retired_plots':[14,16],'retired_objects':retired,'replacement_meshes':[ob.name for ob in replacements],
          'new_meshes':[ob.name for ob in new],'removed_face_counts':counts,'public_walks':walk_by_plot,
          'roads':{'14':{'way':1306489251,'centres_enu':[row[2] for row in grades14], 'drives_enu':[row[2] for row in grades14[3:-3:7]],'across_enu':cross14},
                   '16':{'way':176968735,'centres_enu':[row[2] for row in grades16], 'drives_enu':[row[2] for row in grades16[2:-2:7]],'across_enu':cross16}},
          'access_limits':'14/16 are viewed from the mapped 734116598 pedestrian frontage; 18 is viewed from Panda bus-stop strip. Traffic layers are separate.'}
    for ob in list(bpy.data.objects):
        if ob not in keep:
            bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'houci-14-16.blend'),compress=True,relative_remap=True)
    donor=read(ASSETS/'zhongxing-bridge-18-21.json')['borrowed_materials']
    plan['borrowed_materials']=existing['borrow_slots'](replacements,{name:set(values.values()) for name,values in donor.items()})
    bpy.ops.export_scene.gltf(filepath=str(out/'houci-14-16.glb'),export_format='GLB',export_cameras=False,export_lights=False)
    (out/'houci-14-16.json').write_text(json.dumps(plan,indent=2)+'\n')
    print('CQ_HOUCI_14_16',counts,len(cross14),len(cross16))


if __name__=='__main__':
    main(Path(sys.argv[-1]).resolve())
