"""Static vertex occlusion and sky visibility for the Godot district.

The bake uses geometry in the current Blender scene, not edited screenshots or
external image data. It approximates near-field ambient occlusion in a linear
RGB vertex multiplier; it is not a full global-illumination solution.

Integration, after geometry construction and before glTF export::

    from bake_vertex_ao import bake
    ao_report = bake(bpy.context.scene)
    bpy.ops.export_scene.gltf(..., export_vertex_color='ACTIVE',
                              export_all_vertex_colors=False)

The exporter flags matter: the Blender 4.3 default, MATERIAL, omits a vertex
color that is not referenced in the material node graph. ACTIVE exports this
attribute as COLOR_0 without rewriting each material.

Run this file directly with Blender to execute a small isolated corner/export
probe. It does not open or overwrite any project blend or scene file.
"""
import math
import time

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


COLOR_NAME = 'CQ_StaticAO'
TARGET_COLLECTION_PREFIXES = (
    '01_Terrain', '02_Roads', '03_District', '04_District',
)
SKIP_MATERIAL_WORDS = (
    'glass', 'leaf', 'foliage', 'grime', 'moss_grime', 'light_', 'lamp',
    'emission', 'emissive', 'sign_', 'water', 'paper',
)
SKIP_OBJECT_PREFIXES = ('Type_', 'Text_', 'Context_', 'Sky', 'Camera', 'Light')


def _skip_material(mat):
    if mat is None:
        return False
    low = mat.name.lower()
    if any(s in low for s in SKIP_MATERIAL_WORDS):
        return True
    if mat.get('is_weathering_overlay', False):
        return True
    if mat.use_nodes and mat.node_tree:
        for node in mat.node_tree.nodes:
            if node.type != 'BSDF_PRINCIPLED':
                continue
            alpha = node.inputs.get('Alpha')
            if alpha and (alpha.is_linked or alpha.default_value < .995):
                return True
            emission = node.inputs.get('Emission Color')
            strength = node.inputs.get('Emission Strength')
            if emission and strength and strength.default_value > 0:
                if emission.is_linked or max(emission.default_value[:3]) > .001:
                    return True
    return False


def _eligible(ob):
    if ob.type != 'MESH' or not ob.data.polygons or ob.hide_render:
        return False
    if ob.name.startswith(SKIP_OBJECT_PREFIXES):
        return False
    if any(_skip_material(m) for m in ob.data.materials):
        return False
    return any(c.name.startswith(TARGET_COLLECTION_PREFIXES) for c in ob.users_collection)


def _is_interior(ob):
    """Only explicitly authored interior surfaces receive the room treatment."""
    return bool(ob.get('cq_interior', False) or ob.get('cq_room_envelope', False))


def _geometry_bvh(scene, include_interiors=False):
    """Build from actual opaque meshes; never add proxies or collision objects.

    The original COL-only BVH remains the exterior bake's occluder set.  A
    second BVH adds tagged room envelopes and real furniture for interior
    queries, so fixing a room cannot introduce broad outdoor darkening.
    """
    vertices = []
    polygons = []
    count = 0
    room_count = 0
    furniture_count = 0
    for ob in scene.objects:
        envelope = bool(ob.get('cq_room_envelope', False))
        furniture = bool(ob.get('cq_interior_occluder', False))
        selected = ob.name.startswith('COL_') or (include_interiors and (envelope or furniture))
        if ob.type != 'MESH' or not selected or ob.hide_render:
            continue
        if not ob.data.polygons or any(_skip_material(m) for m in ob.data.materials):
            continue
        mesh = ob.data
        start = len(vertices)
        matrix = ob.matrix_world
        vertices.extend(matrix @ v.co for v in mesh.vertices)
        polygons.extend(tuple(start+i for i in p.vertices) for p in mesh.polygons)
        count += 1
        room_count += int(envelope)
        furniture_count += int(furniture and not envelope)
    report = {'objects': count, 'vertices': len(vertices), 'polygons': len(polygons)}
    if include_interiors:
        report.update({'room_envelope_objects': room_count,
                       'real_furniture_objects': furniture_count,
                       'render_or_collision_objects_added': 0})
    if not polygons:
        return None, report
    bvh = BVHTree.FromPolygons(vertices, polygons, all_triangles=False, epsilon=.0001)
    return bvh, report


def _upper_sky_directions(count):
    """Deterministic equal-area directions, including low window-level sky."""
    golden = math.pi*(3-math.sqrt(5))
    result = []
    for i in range(count):
        z = (i+.5)/count
        r = math.sqrt(1-z*z)
        az = (i+.5)*golden
        result.append(Vector((math.cos(az)*r, math.sin(az)*r, z)))
    return result


def _room_sky_visibility(bvh, origin, normal, directions, distance):
    """Cosine-weighted, binary visibility of the real upper hemisphere.

    An opaque room wall transmits no direct sky.  The separately reported
    bounce floor is applied later; it is not counted as visible sky here.
    Downward-facing ceilings see no upper hemisphere and use that floor.
    """
    visible = 0.
    weight = 0.
    cast = 0
    for direction in directions:
        w = max(0., normal.dot(direction))
        if w < 1e-6:
            continue
        hit, _, _, _ = bvh.ray_cast(origin, direction, distance)
        visible += w if hit is None else 0.
        weight += w
        cast += 1
    return visible/max(1e-8, weight), cast


def _room_visibility_probe(directions, distance, bounce_floor):
    """Numerical aperture check, held only in memory and never in the scene."""
    # Three-metre room, 1.8 x 1.6 m aperture, metre-scale coordinates.
    sides = [
        [(-1.5,0,0),(-1.5,3,0),(-1.5,3,2.8),(-1.5,0,2.8)],
        [(1.5,0,0),(1.5,0,2.8),(1.5,3,2.8),(1.5,3,0)],
        [(-1.5,3,0),(1.5,3,0),(1.5,3,2.8),(-1.5,3,2.8)],
        [(-1.5,0,0),(1.5,0,0),(1.5,3,0),(-1.5,3,0)],
        [(-1.5,0,2.8),(-1.5,3,2.8),(1.5,3,2.8),(1.5,0,2.8)],
    ]
    front = [
        [(-1.5,0,0),(-.9,0,0),(-.9,0,2.8),(-1.5,0,2.8)],
        [(.9,0,0),(1.5,0,0),(1.5,0,2.8),(.9,0,2.8)],
        [(-.9,0,0),(.9,0,0),(.9,0,.9),(-.9,0,.9)],
        [(-.9,0,2.5),(.9,0,2.5),(.9,0,2.8),(-.9,0,2.8)],
    ]
    def make_bvh(quads):
        verts = [Vector(v) for quad in quads for v in quad]
        faces = [tuple(range(i*4,i*4+4)) for i in range(len(quads))]
        return BVHTree.FromPolygons(verts, faces, all_triangles=False, epsilon=.0001)
    open_bvh = make_bvh(sides+front)
    closed_bvh = make_bvh(sides+[[(-1.5,0,0),(1.5,0,0),(1.5,0,2.8),(-1.5,0,2.8)]])
    normal = Vector((0,-1,0))
    near = Vector((0,.40,1.50))
    deep = Vector((0,2.60,1.50))
    closed, _ = _room_sky_visibility(closed_bvh, near, normal, directions, distance)
    at_window, _ = _room_sky_visibility(open_bvh, near, normal, directions, distance)
    at_back, _ = _room_sky_visibility(open_bvh, deep, normal, directions, distance)
    passed = closed < 1e-7 and at_window > at_back+.10 and at_back < .30
    return {'scope': 'In-memory numerical visibility check; no scene objects or proxy geometry',
            'room_dimensions_m': [3.,3.,2.8], 'aperture_dimensions_m': [1.8,1.6],
            'closed_room_sky_visibility': round(closed,6),
            'near_window_sky_visibility': round(at_window,6),
            'deep_room_sky_visibility': round(at_back,6),
            'near_window_distance_m': .40, 'deep_room_distance_m': 2.60,
            'closed_room_sky_multiplier': round(bounce_floor+(1-bounce_floor)*closed,6),
            'near_window_sky_multiplier': round(bounce_floor+(1-bounce_floor)*at_window,6),
            'deep_room_sky_multiplier': round(bounce_floor+(1-bounce_floor)*at_back,6),
            'passed': passed}


def _sample_summary(values):
    if not values:
        return {'samples': 0}
    a = np.asarray(values, dtype=np.float32)
    q = np.quantile(a, [.1,.5,.9])
    return {'samples': len(values), 'min': round(float(a.min()),6),
            'mean': round(float(a.mean()),6), 'p10': round(float(q[0]),6),
            'p50': round(float(q[1]),6), 'p90': round(float(q[2]),6),
            'max': round(float(a.max()),6)}


def _loop_data(ob):
    mesh = ob.data
    mesh.update()
    size = len(mesh.loops)
    coords = np.empty(len(mesh.vertices)*3, np.float32)
    mesh.vertices.foreach_get('co', coords)
    coords = coords.reshape((-1,3))
    indices = np.empty(size, np.int32)
    mesh.loops.foreach_get('vertex_index', indices)
    matrix = np.array(ob.matrix_world, dtype=np.float32)
    coords = coords @ matrix[:3,:3].T + matrix[:3,3]
    normals = np.empty(size*3, np.float32)
    try:
        # Blender 4.3 provides split/corner normals through this collection.
        mesh.corner_normals.foreach_get('vector', normals)
        normals = normals.reshape((-1,3))
    except (AttributeError, TypeError):
        # Flat polygon normals are appropriate for the un-smoothed building
        # shells. The fallback also works with an older bundled Blender.
        normals = normals.reshape((-1,3))
        for p in mesh.polygons:
            normals[p.loop_start:p.loop_start+p.loop_total] = p.normal
    normal_matrix = np.array(ob.matrix_world.to_3x3().inverted_safe().transposed(), dtype=np.float32)
    normals = normals @ normal_matrix.T
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    normals /= np.maximum(lengths, 1e-8)
    return coords[indices], normals


def bake(scene=None, radius=2.0, strength=.40, rays=6, cell_size=.34,
         max_samples=120000, progress_every=100, sky_radius=0., sky_strength=.40,
         interior_sky_floor=.18, interior_sky_rays=48):
    """Bake the scene's building/ground meshes and return a JSON-safe report.

    ``radius`` and ``cell_size`` are metres. ``strength`` is clamped to .45.
    The limited ray set and spatial/normal cache are intentional approximations
    for a district-size offline bake, not per-pixel path tracing. With the
    default radius, distant buildings cannot darken a whole open street.

    Tagged interiors use a separate, geometrically complete visibility bake.
    ``interior_sky_floor`` is an explicit approximation for indirect bounce,
    not transmitted sky and not full GI.  Exterior parameters are unchanged.
    """
    scene = scene or bpy.context.scene
    bpy.context.view_layer.update()
    start = time.monotonic()
    radius = max(.25, float(radius))
    strength = max(0., min(.45, float(strength)))
    rays = max(4, min(8, int(rays)))
    cell_size = max(.16, float(cell_size))
    bvh, solid_report = _geometry_bvh(scene)
    targets = [ob for ob in scene.objects if _eligible(ob)]
    interior_targets = [ob for ob in targets if _is_interior(ob)]
    report = {
        'method': 'Geometry raycast near-field AO and optional hemispherical sky visibility in linear vertex RGB; not full GI',
        'attribute': COLOR_NAME, 'domain': 'CORNER', 'type': 'FLOAT_COLOR',
        'radius_m': radius, 'strength': strength, 'rays_per_sample': rays,
        'cell_size_m': cell_size, 'occluders': solid_report,
        'sky_radius_m':sky_radius,'sky_strength':sky_strength,'sky_visibility_rays':8 if sky_radius else 0,
        'objects': 0, 'corners': 0, 'unique_samples': 0, 'cache_hits': 0,
        'fallback_samples': 0, 'local_reuse_corners': 0, 'rays_cast': 0, 'min_multiplier': 1.,
        'max_multiplier': 1., 'duration_seconds': 0.,
        'export_flags': {'export_vertex_color': 'ACTIVE', 'export_all_vertex_colors': False},
    }
    if bvh is None:
        report['skipped_reason'] = 'No opaque COL_ occluder meshes'
        report['duration_seconds'] = round(time.monotonic()-start,3)
        return report

    cache = {}
    coarse_cache = {}
    interior_cache = {}
    interior_bvh = None
    interior_floor = max(.08, min(.40, float(interior_sky_floor)))
    interior_ray_count = max(24, min(96, int(interior_sky_rays)))
    interior_sky_radius = max(12., float(sky_radius))
    interior_cell = min(.18, cell_size)
    interior_radius = min(1.25, radius)
    interior_contact_rays = 12
    interior_directions = _upper_sky_directions(interior_ray_count)
    interior_visibility_values = []
    interior_multiplier_values = []
    room_observations = {}
    interior_report = {'enabled': bool(interior_targets),
                       'method': 'Actual opaque room envelope and furniture; cosine-weighted binary upper-sky visibility, local contact AO and explicit indirect-bounce floor',
                       'exterior_bvh_and_formula': 'Original COL-only occluders and exterior formula retained',
                       'target_objects': len(interior_targets),
                       'sky_rays': interior_ray_count, 'sky_radius_m': interior_sky_radius,
                       'indirect_bounce_floor': interior_floor, 'cell_size_m': interior_cell,
                       'contact_radius_m': interior_radius, 'contact_rays': interior_contact_rays,
                       'contact_strength': strength, 'cache_coarsening': False,
                       'unique_samples': 0, 'cache_hits': 0, 'rays_cast': 0}
    report['interior_visibility'] = interior_report
    if interior_targets:
        interior_bvh, interior_solid_report = _geometry_bvh(scene, include_interiors=True)
        interior_report['occluders'] = interior_solid_report
        interior_report['numerical_aperture_probe'] = _room_visibility_probe(
            interior_directions, interior_sky_radius, interior_floor)
        if not interior_report['numerical_aperture_probe']['passed']:
            raise RuntimeError('Interior sky visibility failed the closed-room / open-aperture numerical check')
        if interior_solid_report['room_envelope_objects'] == 0:
            interior_report['warning'] = 'Interior targets exist but no cq_room_envelope tags were found'
    # Cosine-weighted hemisphere points; the fixed low-discrepancy azimuths
    # produce a reproducible result without high-frequency random speckle.
    hemi=[]
    golden=math.pi*(3-math.sqrt(5))
    for i in range(rays):
        r=math.sqrt((i+.5)/rays)*.97
        phi=(i+.5)*golden
        hemi.append((r*math.cos(phi),r*math.sin(phi),math.sqrt(1-r*r)))
    interior_hemi=[]
    for i in range(interior_contact_rays):
        r=math.sqrt((i+.5)/interior_contact_rays)*.97
        phi=(i+.5)*golden
        interior_hemi.append((r*math.cos(phi),r*math.sin(phi),math.sqrt(1-r*r)))

    def query(position, normal, key):
        old=cache.get(key)
        if old is not None:
            report['cache_hits']+=1
            return old
        coarse=(int(key[0])//3,int(key[1])//3,int(key[2])//3,
                int(key[3]),int(key[4]),int(key[5]))
        if len(cache) >= max_samples and coarse in coarse_cache:
            report['fallback_samples']+=1
            value=coarse_cache[coarse]
            cache[key]=value
            return value
        n=Vector(tuple(float(x) for x in normal))
        if n.length_squared < .001:
            cache[key]=1.
            return 1.
        n.normalize()
        p=Vector(tuple(float(x) for x in position))
        # Large surfaces use their actual corner position. Avoid rays starting
        # inside their own face, while retaining contact within a few cm.
        origin=p+n*.035
        aux=Vector((0,0,1)) if abs(n.z)<.92 else Vector((1,0,0))
        tangent=n.cross(aux).normalized()
        bitangent=n.cross(tangent).normalized()
        occlusion=0.
        for x,y,z in hemi:
            direction=tangent*x+bitangent*y+n*z
            hit,_,_,distance=bvh.ray_cast(origin,direction,radius)
            if hit is not None and distance is not None and distance>.0005:
                # Squared range falloff limits shadowing to close contacts.
                occlusion += (1-min(radius,distance)/radius)**1.7
        value=1-strength*occlusion/rays
        value=max(1-strength,min(1.,value))
        if sky_radius>0:
            # World-space upper hemisphere measures whether a surface sees
            # open sky, giving narrow courts real broad-scale enclosure.
            # This is explicit visibility, not a painted image or full GI.
            visible=0.; weight=0.
            for si in range(8):
                az=(si+.5)*golden
                zz=.22+.72*((si+.5)/8)
                rr=math.sqrt(1-zz*zz)
                dr=Vector((math.cos(az)*rr,math.sin(az)*rr,zz))
                w=max(.08,n.dot(dr))
                hit,_,_,distance=bvh.ray_cast(origin,dr,sky_radius)
                visible+=w*(1. if hit is None else .12+.35*min(1.,distance/sky_radius))
                weight+=w
            sky_fraction=visible/max(.01,weight)
            value*=1.-sky_strength*(1.-sky_fraction)
            report['rays_cast']+=8
        cache[key]=value
        coarse_cache[coarse]=value
        report['rays_cast']+=rays
        report['unique_samples']+=1
        return value

    def query_interior(position, normal, key):
        old = interior_cache.get(key)
        if old is not None:
            report['cache_hits'] += 1
            interior_report['cache_hits'] += 1
            return old
        n = Vector(tuple(float(x) for x in normal))
        if n.length_squared < .001:
            interior_cache[key] = (1.,1.)
            return 1.,1.
        n.normalize()
        p = Vector(tuple(float(x) for x in position))
        # A smaller bias retains contact at actual chair/table feet.  Interior
        # sampling is never coarsened across a thin wall or a narrow aperture.
        origin = p+n*.015
        aux = Vector((0,0,1)) if abs(n.z)<.92 else Vector((1,0,0))
        tangent = n.cross(aux).normalized()
        bitangent = n.cross(tangent).normalized()
        occlusion = 0.
        for x,y,z in interior_hemi:
            direction = tangent*x+bitangent*y+n*z
            hit,_,_,distance = interior_bvh.ray_cast(origin,direction,interior_radius)
            if hit is not None and distance is not None and distance>.0005:
                occlusion += (1-min(interior_radius,distance)/interior_radius)**1.7
        contact = max(1-strength, min(1., 1-strength*occlusion/interior_contact_rays))
        visibility, sky_cast = _room_sky_visibility(
            interior_bvh, origin, n, interior_directions, interior_sky_radius)
        value = contact*(interior_floor+(1-interior_floor)*visibility)
        result = (value, visibility)
        interior_cache[key] = result
        interior_visibility_values.append(visibility)
        interior_multiplier_values.append(value)
        cast = interior_contact_rays+sky_cast
        report['rays_cast'] += cast
        report['unique_samples'] += 1
        interior_report['rays_cast'] += cast
        interior_report['unique_samples'] += 1
        return result

    color_sum = 0.
    for index,ob in enumerate(targets):
        if ob.data.users>1:
            ob.data=ob.data.copy()
        mesh=ob.data
        points,normals=_loop_data(ob)
        is_interior = _is_interior(ob)
        # Independent normal bins prevent the two faces at a hard corner from
        # sharing an occlusion sample, even when they share mesh vertices.
        keys=np.empty((len(points),6),np.int32)
        keys[:,:3]=np.rint(points/(interior_cell if is_interior else cell_size)).astype(np.int32)
        keys[:,3:]=np.rint(normals*(8 if is_interior else 5)).astype(np.int32)
        unique,first,inverse=np.unique(keys,axis=0,return_index=True,return_inverse=True)
        report['local_reuse_corners'] += len(points)-len(unique)
        values=np.empty(len(unique),np.float32)
        visibilities=np.empty(len(unique),np.float32) if is_interior else None
        for j,(k,original) in enumerate(zip(unique,first)):
            if is_interior:
                values[j], visibilities[j] = query_interior(points[original],normals[original],tuple(k))
            else:
                values[j]=query(points[original],normals[original],tuple(k))
        if is_interior and 'cq_room_aperture_center' in ob and 'cq_room_inward' in ob:
            center=np.asarray(ob['cq_room_aperture_center'],dtype=np.float32)
            inward=np.asarray(ob['cq_room_inward'],dtype=np.float32)
            depth=float(ob.get('cq_room_depth',0.))
            if center.shape==(3,) and inward.shape==(3,) and depth>.1 and np.linalg.norm(inward)>.5:
                inward=inward/np.linalg.norm(inward)
                distances=(points[first]-center)@inward
                room_id=str(ob.get('cq_room_id',ob.name))
                record=room_observations.setdefault(room_id,{'depth_m':depth,'objects':[],
                    'near_window_visibility':[],'near_window_multiplier':[],
                    'deep_room_visibility':[],'deep_room_multiplier':[]})
                record['objects'].append(ob.name)
                # Exclude downward-facing ceiling corners from the depth
                # comparison: they cannot directly see the upper hemisphere.
                oriented=normals[first,2]>-.5
                near=oriented & (distances>=-.10) & (distances<=min(.85,depth*.35))
                deep=oriented & (distances>=depth*.65) & (distances<=depth+.10)
                for label,mask in [('near_window',near),('deep_room',deep)]:
                    record[label+'_visibility'].extend(float(v) for v in visibilities[mask])
                    record[label+'_multiplier'].extend(float(v) for v in values[mask])
        result=values[inverse]
        colors=np.ones((len(points),4),np.float32)
        colors[:,:3]=result[:,None]
        attr=mesh.color_attributes.get(COLOR_NAME)
        if attr and (attr.domain!='CORNER' or attr.data_type!='FLOAT_COLOR'):
            mesh.color_attributes.remove(attr);attr=None
        if attr is None:
            attr=mesh.color_attributes.new(name=COLOR_NAME,type='FLOAT_COLOR',domain='CORNER')
        attr.data.foreach_set('color',colors.ravel())
        color_index=mesh.color_attributes.find(COLOR_NAME)
        mesh.color_attributes.active_color_index=color_index
        mesh.color_attributes.render_color_index=color_index
        mesh.update()
        if is_interior:
            ob['static_ao']='Actual room/furniture sky visibility and contact AO; indirect bounce floor %.2f'%interior_floor
        else:
            ob['static_ao']='Geometry-derived vertex AO; radius %.2fm, max strength %.2f'%(radius,strength)
        report['objects']+=1
        report['corners']+=len(points)
        if len(result):
            report['min_multiplier']=min(report['min_multiplier'],float(result.min()))
            color_sum += float(result.sum(dtype=np.float64))
        if progress_every and (index+1)%progress_every==0:
            print('CQ_AO_PROGRESS',index+1,'/',len(targets),'samples',report['unique_samples'],
                  'seconds',round(time.monotonic()-start,1),flush=True)
    report['duration_seconds']=round(time.monotonic()-start,3)
    report['min_multiplier']=round(report['min_multiplier'],5)
    report['mean_multiplier']=round(color_sum/max(1,report['corners']),5)
    report['cache_entries']=len(cache)+len(interior_cache)
    report['exterior_cache_entries']=len(cache)
    interior_report['raw_sky_visibility'] = _sample_summary(interior_visibility_values)
    interior_report['combined_vertex_multiplier'] = _sample_summary(interior_multiplier_values)
    interior_report['actual_tagged_room_depth_comparison'] = {
        room_id: {key: (_sample_summary(value) if isinstance(value,list) and key!='objects' else value)
                  for key,value in record.items()}
        for room_id,record in room_observations.items()}
    scene['static_vertex_ao']=True
    scene['static_vertex_ao_radius_m']=radius
    scene['static_vertex_ao_strength']=strength
    print('CQ_AO_COMPLETE',report,flush=True)
    return report


def _probe():
    """Validate useful occlusion and actual COLOR_0 export in a tiny scene."""
    import json,struct
    from pathlib import Path
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    col=bpy.data.collections.new('01_Terrain_AO_probe')
    bpy.context.scene.collection.children.link(col)
    mat=bpy.data.materials.new('AO_opaque_probe');mat.use_nodes=True
    verts=[(x*.25-2,y*.25-2,0) for y in range(17) for x in range(17)]
    faces=[(y*17+x,y*17+x+1,(y+1)*17+x+1,(y+1)*17+x) for y in range(16) for x in range(16)]
    mesh=bpy.data.meshes.new('ProbeFloor');mesh.from_pydata(verts,[],faces);mesh.update()
    floor=bpy.data.objects.new('COL_ProbeFloor',mesh);col.objects.link(floor);mesh.materials.append(mat)
    # A simple L corner shades the nearby floor; open floor remains white.
    for name,location,scale in [('COL_ProbeWallX',(0,0,1),(.10,4.,2.)),('COL_ProbeWallY',(1,1.8,1),(2.,.10,2.))]:
        bpy.ops.mesh.primitive_cube_add(size=1,location=location)
        ob=bpy.context.object;ob.name=name;ob.scale=scale
        for old in list(ob.users_collection):old.objects.unlink(ob)
        col.objects.link(ob);ob.data.materials.append(mat)
    report=bake(bpy.context.scene,progress_every=0)
    assert report['min_multiplier']<.95,report
    path=Path('/tmp/cq03_ao_probe.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_apply=True,
                             export_vertex_color='ACTIVE',export_all_vertex_colors=False)
    blob=path.read_bytes();size,_=struct.unpack_from('<II',blob,12)
    doc=json.loads(blob[20:20+size])
    primitives=[p for m in doc['meshes'] for p in m['primitives']]
    assert all('COLOR_0' in p['attributes'] for p in primitives),doc
    min_color=1.
    # Inspect a few actual float color accessor values rather than accepting
    # only the attribute name; this detects an exporter emitting dummy white.
    bin_start=20+size+8
    for prim in primitives:
        acc=doc['accessors'][prim['attributes']['COLOR_0']]
        view=doc['bufferViews'][acc['bufferView']]
        start=bin_start+view.get('byteOffset',0)+acc.get('byteOffset',0)
        comp=acc['componentType'];channels=4 if acc['type']=='VEC4' else 3
        stride=view.get('byteStride',channels*(4 if comp==5126 else 2 if comp==5123 else 1))
        for i in range(acc['count']):
            if comp==5126:val=struct.unpack_from('<f',blob,start+i*stride)[0]
            elif comp==5123:val=struct.unpack_from('<H',blob,start+i*stride)[0]/65535
            else:val=blob[start+i*stride]/255
            min_color=min(min_color,val)
    assert min_color<.95,min_color
    report['probe']={'exported_COLOR_0_primitives':len(primitives),'actual_glb_min_color':min_color,'passed':True}
    Path('/tmp/cq03_ao_probe_report.json').write_text(json.dumps(report,indent=2)+'\n')
    path.unlink()
    print('CQ_AO_EXPORT_VERIFIED',json.dumps(report['probe']))


if __name__=='__main__':
    _probe()
