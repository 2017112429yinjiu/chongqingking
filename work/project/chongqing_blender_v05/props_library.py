"""Original metres-scale streetscape assets for the Chongqing refinement.

Blender 4.3+, Z up, positions at ground level, yaw in radians. All visible
geometry is authored here. Color materials are original; optional bark and
concrete scans come from the parent project's attributed CC0 material library.
No downloaded models, branded logos, or alpha-card vegetation. Functions never clear,
save, export, or otherwise mutate the caller's scene outside their own objects.

Leaves are curved, pointed meshes with real open silhouettes. Geometry is
batched by material per prop, with explicit hard/smooth polygon settings.
"""

from collections import defaultdict
import math
import random

import bpy
from mathutils import Vector


PALETTE = {
    "bark": ((0.19, 0.135, 0.082), 0.99, 0.0),
    "bark_light": ((0.30, 0.245, 0.155), 0.99, 0.0),
    "bark_dark": ((0.095, 0.085, 0.047), 1.0, 0.0),
    "leaf_dark": ((0.035, 0.095, 0.025), 0.87, 0.0),
    "leaf_mid": ((0.078, 0.18, 0.037), 0.83, 0.0),
    "leaf_light": ((0.145, 0.255, 0.066), 0.83, 0.0),
    "leaf_new": ((0.22, 0.29, 0.089), 0.89, 0.0),
    "leaf_dead": ((0.265, 0.17, 0.058), 0.98, 0.0),
    "stone": ((0.255, 0.27, 0.239), 0.97, 0.0),
    "stone_edge": ((0.40, 0.415, 0.365), 0.97, 0.0),
    "stone_dark": ((0.135, 0.175, 0.13), 0.99, 0.0),
    "soil": ((0.065, 0.048, 0.031), 1.0, 0.0),
    "steel": ((0.34, 0.37, 0.355), 0.48, 0.8),
    "black_metal": ((0.03, 0.037, 0.035), 0.59, 0.65),
    "rust": ((0.27, 0.115, 0.046), 0.95, 0.22),
    "rubber": ((0.016, 0.019, 0.019), 0.93, 0.0),
    "rubber_worn": ((0.042, 0.045, 0.043), 0.96, 0.0),
    "seat": ((0.026, 0.03, 0.028), 0.79, 0.0),
    "paint_teal": ((0.035, 0.24, 0.23), 0.31, 0.3),
    "paint_cream": ((0.68, 0.65, 0.53), 0.42, 0.2),
    "paint_white": ((0.68, 0.70, 0.67), 0.47, 0.2),
    "window": ((0.032, 0.069, 0.077), 0.20, 0.32),
    "paint_red": ((0.40, 0.055, 0.035), 0.56, 0.1),
    "plastic_orange": ((0.86, 0.32, 0.025), 0.8, 0.0),
    "plastic_green": ((0.06, 0.20, 0.13), 0.87, 0.0),
    "plastic_green_light": ((0.10, 0.285, 0.185), 0.84, 0.0),
    "plastic_blue": ((0.04, 0.13, 0.23), 0.84, 0.0),
    "plastic_yellow": ((0.59, 0.40, 0.05), 0.84, 0.0),
    "cream": ((0.63, 0.62, 0.53), 0.84, 0.0),
    "wood": ((0.30, 0.165, 0.065), 0.94, 0.0),
    "wood_light": ((0.45, 0.29, 0.12), 0.94, 0.0),
    "wood_dark": ((0.16, 0.085, 0.03), 0.98, 0.0),
    "bottle": ((0.025, 0.11, 0.058), 0.24, 0.1),
    "paper": ((0.66, 0.61, 0.44), 0.97, 0.0),
    "lamp": ((0.94, 0.75, 0.43), 0.32, 0.1),
    "tail_lamp": ((0.40, 0.015, 0.008), 0.28, 0.1),
    "mirror": ((0.27, 0.36, 0.36), 0.17, 0.92),
}


def _materials():
    # The parent project's licensed scan library supplies bark and masonry.
    # Standalone users can omit it; original color materials remain a fallback.
    pbr = {key:bpy.data.materials.get('CQ_PBR_'+key) for key in ('bark','concrete')}
    if any(v is None for v in pbr.values()):
        try:
            import material_library
            loaded = material_library.build_materials()
            pbr = {key:loaded.get(key) for key in ('bark','concrete')}
        except (ImportError, FileNotFoundError):
            pass
    mats = {}
    for key, (color, rough, metal) in PALETTE.items():
        scan_key = 'bark' if key == 'bark' else ('concrete' if key in ('stone','stone_edge') else None)
        if scan_key and pbr.get(scan_key):
            mats[key] = pbr[scan_key]
            continue
        name = "CQF_" + key
        mat = bpy.data.materials.get(name)
        if mat is None:
            mat = bpy.data.materials.new(name)
            mat.use_nodes = True
            p = mat.node_tree.nodes.get("Principled BSDF")
            p.inputs["Base Color"].default_value = (*color, 1)
            p.inputs["Roughness"].default_value = rough
            p.inputs["Metallic"].default_value = metal
            if key in ("lamp", "tail_lamp"):
                p.inputs["Emission Color"].default_value = (*color, 1)
                p.inputs["Emission Strength"].default_value = 0.35 if key == "lamp" else 0.1
            mat.diffuse_color = (*color, 1)
            # Leaf geometry is a real curved surface, visible from both sides.
            mat.use_backface_culling = not key.startswith("leaf")
            mat["asset_origin"] = "Original authored procedural material"
        mats[key] = mat
    return mats


def _collection(col):
    if col is None:
        return bpy.context.scene.collection
    if isinstance(col, str):
        existing = bpy.data.collections.get(col)
        if existing:
            return existing
        existing = bpy.data.collections.new(col)
        bpy.context.scene.collection.children.link(existing)
        return existing
    return col


class Batch:
    def __init__(self, name, position=(0, 0, 0), yaw=0.0, collection=None):
        self.name = name
        self.position = Vector(position)
        self.c = math.cos(yaw)
        self.s = math.sin(yaw)
        self.collection = _collection(collection)
        self.data = defaultdict(lambda: [[], [], [], []])

    def mesh(self, vertices, faces, material, smooth=False, uv_faces=None):
        verts, polys, smoothing, uvs = self.data[material]
        k = len(verts)
        # Keep local geometry local; the object carries placement and yaw.
        verts.extend(tuple(v) for v in vertices)
        polys.extend(tuple(k + i for i in f) for f in faces)
        if isinstance(smooth, (list, tuple)):
            smoothing.extend(smooth)
        else:
            smoothing.extend([smooth] * len(faces))
        uvs.extend(uv_faces if uv_faces is not None else [None]*len(faces))

    def box(self, center, size, material):
        x, y, z = center
        a, b, c = [v / 2 for v in size]
        if min(a, b, c) <= 0:
            return
        self.mesh([(x-a, y-b, z-c), (x+a, y-b, z-c), (x+a, y+b, z-c), (x-a, y+b, z-c),
                   (x-a, y-b, z+c), (x+a, y-b, z+c), (x+a, y+b, z+c), (x-a, y+b, z+c)],
                  [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
                   (2, 3, 7, 6), (3, 0, 4, 7)], material)

    def cylinder(self, a, b, radius, material, sides=10, end_radius=None, smooth=True):
        a, b = Vector(a), Vector(b)
        delta = b - a
        if delta.length < 1e-5:
            return
        n = delta.normalized()
        q = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((0, 1, 0))
        u = n.cross(q).normalized()
        v = n.cross(u).normalized()
        end_radius = radius if end_radius is None else end_radius
        vertices = []
        for origin, r in [(a, radius), (b, end_radius)]:
            for j in range(sides):
                angle = j * math.tau / sides
                vertices.append(origin + r * (u * math.cos(angle) + v * math.sin(angle)))
        faces = [tuple(reversed(range(sides))), tuple(range(sides, 2*sides))]
        faces += [(j, (j+1) % sides, (j+1) % sides+sides, j+sides) for j in range(sides)]
        uv_faces = None
        if material == 'bark':
            cap = lambda r, ids: [(r*math.cos(math.tau*(j % sides)/sides),r*math.sin(math.tau*(j % sides)/sides)) for j in ids]
            uv_faces = [cap(radius,faces[0]),cap(end_radius,faces[1])]
            for j in range(sides):
                uv_faces.append([(j*math.tau*radius/sides,0),((j+1)*math.tau*radius/sides,0),
                                 ((j+1)*math.tau*end_radius/sides,delta.length),(j*math.tau*end_radius/sides,delta.length)])
        self.mesh(vertices, faces, material, [False, False] + [smooth]*sides, uv_faces)

    def sphere(self, center, radii, material, rings=8, sides=16):
        center = Vector(center)
        # Two single poles avoid degenerate pole quads.
        vertices = [center + Vector((0, 0, radii[2]))]
        for r in range(1, rings):
            latitude = math.pi * r / rings
            for j in range(sides):
                angle = math.tau * j / sides
                vertices.append(center + Vector((radii[0]*math.sin(latitude)*math.cos(angle),
                                                 radii[1]*math.sin(latitude)*math.sin(angle),
                                                 radii[2]*math.cos(latitude))))
        vertices.append(center - Vector((0, 0, radii[2])))
        faces = [(0, 1+j, 1+(j+1) % sides) for j in range(sides)]
        for r in range(rings-2):
            a = 1+r*sides
            faces.extend((a+j, a+sides+j, a+sides+(j+1) % sides, a+(j+1) % sides) for j in range(sides))
        last = 1 + (rings-2)*sides
        pole = len(vertices)-1
        faces.extend((last+j, pole, last+(j+1) % sides) for j in range(sides))
        self.mesh(vertices, faces, material, True)

    def torus(self, center, major, minor, material, axis="X", steps=32, sides=8, flatten=1.0):
        center = Vector(center)
        vertices = []
        for i in range(steps):
            a = math.tau*i/steps
            for j in range(sides):
                b = math.tau*j/sides
                radial = major + minor*math.cos(b)
                v = Vector((minor*math.sin(b)*flatten, radial*math.sin(a), radial*math.cos(a)))
                if axis == "Z":
                    v = Vector((v.y, v.z, v.x))
                elif axis == "Y":
                    v = Vector((v.y, v.x, v.z))
                vertices.append(center + v)
        faces = []
        for i in range(steps):
            for j in range(sides):
                faces.append((i*sides+j, ((i+1) % steps)*sides+j,
                              ((i+1) % steps)*sides+(j+1) % sides, i*sides+(j+1) % sides))
        # This parameterization runs around YZ with positive X tube coordinate.
        self.mesh(vertices, [tuple(reversed(f)) for f in faces], material, True)

    def tube_path(self, centers, radii, material, sides=12):
        """Continuous tapered trunk/pipe: shared rings avoid dark segment seams."""
        path = [Vector(p) for p in centers]
        vertices = []
        for i, (center, radius) in enumerate(zip(path, radii)):
            n = (path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized()
            q = Vector((0,1,0)) if abs(n.y)<.9 else Vector((1,0,0))
            u = n.cross(q).normalized()
            v = n.cross(u).normalized()
            for j in range(sides):
                a = math.tau*j/sides
                r = radius*(1+.045*math.sin(j*2.3))
                vertices.append(center+r*(u*math.cos(a)+v*math.sin(a)))
        faces = [tuple(reversed(range(sides))),tuple(range((len(path)-1)*sides,len(path)*sides))]
        distance = [0]
        for a,c in zip(path,path[1:]):distance.append(distance[-1]+(c-a).length)
        uv_faces = [None,None]
        for i in range(len(path)-1):
            for j in range(sides):
                faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
                uv_faces.append([(j*math.tau*radii[i]/sides,distance[i]),((j+1)*math.tau*radii[i]/sides,distance[i]),
                                 ((j+1)*math.tau*radii[i+1]/sides,distance[i+1]),(j*math.tau*radii[i+1]/sides,distance[i+1])])
        self.mesh(vertices,faces,material,[False,False]+[True]*(len(faces)-2),uv_faces)

    def loft_y(self, profiles, material, sides=16):
        """Profiles are (y, z_center, x_radius, z_radius), rounded body shell."""
        vertices = []
        for y, z, rx, rz in profiles:
            for i in range(sides):
                angle = math.tau*i/sides
                vertices.append((rx*math.cos(angle), y, z+rz*math.sin(angle)))
        faces = [tuple(range(sides)), tuple(reversed(range((len(profiles)-1)*sides, len(profiles)*sides)))]
        for p in range(len(profiles)-1):
            for i in range(sides):
                faces.append((p*sides+i, (p+1)*sides+i,
                              (p+1)*sides+(i+1) % sides, p*sides+(i+1) % sides))
        self.mesh(vertices, faces, material, [False, False] + [True]*(len(faces)-2))

    def leaf(self, center, direction, width, material, roll=0.0):
        """A curved lanceolate broadleaf, 6 triangles and a shallow ridge."""
        p = Vector(center)
        long = Vector(direction)
        length = long.length
        if length < 1e-5:
            return
        n = long.normalized()
        q = Vector((0, 0, 1)) if abs(n.z) < 0.85 else Vector((1, 0, 0))
        u = n.cross(q).normalized()
        v = n.cross(u).normalized()
        side = u*math.cos(roll)+v*math.sin(roll)
        normal = n.cross(side)
        vertices = [p-long*0.5,
                    p-long*0.18-side*width*0.48,
                    p+long*0.20-side*width*0.38,
                    p+long*0.5+normal*length*0.045,
                    p+long*0.20+side*width*0.38,
                    p-long*0.18+side*width*0.48,
                    p+normal*length*0.045]
        self.mesh(vertices, [(i, (i+1) % 6, 6) for i in range(6)], material, True)

    def finish(self, prop_type):
        materials = _materials()
        objects = []
        for key, (vertices, faces, smoothing, uv_faces) in self.data.items():
            if not vertices:
                continue
            mesh = bpy.data.meshes.new(self.name + "_" + key)
            mesh.from_pydata(vertices, [], faces)
            mesh.update()
            mesh.materials.append(materials[key])
            for polygon, smooth in zip(mesh.polygons, smoothing):
                polygon.use_smooth = smooth
            if key in ('bark','stone','stone_edge'):
                uv_layer = mesh.uv_layers.new(name='UVMap')
                meters = float(materials[key].get('uv_meters',1.0))
                for polygon, supplied in zip(mesh.polygons,uv_faces):
                    axis = max(range(3),key=lambda i:abs(polygon.normal[i]))
                    plane = (1,2) if axis == 0 else ((0,2) if axis == 1 else (0,1))
                    for j, loop_index in enumerate(polygon.loop_indices):
                        co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
                        uv = supplied[j] if supplied else (co[plane[0]],co[plane[1]])
                        uv_layer.data[loop_index].uv = (uv[0]/meters,uv[1]/meters)
            ob = bpy.data.objects.new(mesh.name, mesh)
            self.collection.objects.link(ob)
            ob.location = self.position
            ob.rotation_euler.z = math.atan2(self.s, self.c)
            ob["asset_origin"] = "Original procedural geometry; original color materials and optional licensed CC0 bark/concrete scans"
            ob["prop_type"] = prop_type
            ob["collision"] = "visual_only; caller supplies simple obstacles"
            ob["units"] = "metres"
            objects.append(ob)
        return objects


def _leaf_color(rng):
    return rng.choices(["leaf_dark", "leaf_mid", "leaf_light", "leaf_new", "leaf_dead"],
                       [0.25, 0.46, 0.22, 0.055, 0.015])[0]


def make_tree(position, scale=1.0, seed=1, collection=None):
    """A 6.5–7 m street tree: irregular trunk, roots, branches, 3,000+ leaves.

    Scale multiplies all dimensions, including crown diameter (about 5 m).
    The canopy has no opaque ellipsoids or billboard cards.
    """
    rng = random.Random(seed)
    b = Batch("CQF_Tree_%s" % seed, position, collection=collection)
    s = scale
    trunk = [Vector((0, 0, 0)), Vector((0.05, -0.025, 0.85)), Vector((0.04, 0.03, 1.7)),
             Vector((-0.12, 0.11, 2.55)), Vector((-0.20, 0.07, 3.35)), Vector((-0.12, 0.18, 4.05)),
             Vector((0.10, 0.13, 4.8)), Vector((0.22, 0.25, 5.75))]
    radii = [0.25, 0.19, 0.17, 0.145, 0.12, 0.09, 0.06, 0.018]
    b.tube_path([p*s for p in trunk],[r*s for r in radii],"bark",sides=14)
    for k in range(7):
        angle = k*math.tau/7 + rng.uniform(-0.25, 0.25)
        root_end = Vector((math.cos(angle)*rng.uniform(0.55, 0.95), math.sin(angle)*rng.uniform(0.55, 0.95), 0.015))
        b.cylinder(Vector((0, 0, 0.20))*s, root_end*s, 0.105*s, "bark", 9, end_radius=0.014*s)
    # Bark ribs and patches hug the trunk and break up its smooth silhouette.
    for k in range(45):
        z = rng.uniform(0.15, 3.85)
        i = min(len(trunk)-2, int(z / 0.82))
        t = max(0, min(1, (z-trunk[i].z)/(trunk[i+1].z-trunk[i].z)))
        c = trunk[i].lerp(trunk[i+1], t)
        radius = radii[i]*(1-t)+radii[i+1]*t
        a = rng.uniform(0, math.tau)
        start = c+Vector((math.cos(a)*radius, math.sin(a)*radius, 0))
        end = start+Vector((rng.uniform(-0.015, 0.015), rng.uniform(-0.015, 0.015), rng.uniform(0.12, 0.38)))
        b.cylinder(start*s, end*s, 0.008*s, rng.choice(["bark_light", "bark_dark"]), 4, end_radius=0.003*s)

    clusters = []
    # Radial branches are deliberately staggered in height and asymmetrical.
    for i in range(14):
        angle = i*2.39996+rng.uniform(-0.22, 0.22)
        base_z = 2.65 + i*0.19 + rng.uniform(-0.15, 0.15)
        start = Vector((-0.12, 0.12, base_z))
        extent = rng.uniform(1.35, 2.25)*(1.0 if i < 10 else 0.83)
        delta = Vector((math.cos(angle)*extent, math.sin(angle)*extent, rng.uniform(0.75, 1.7)))
        elbow = start + Vector((delta.x*0.47, delta.y*0.47, delta.z*0.65))
        end = start + delta
        b.cylinder(start*s, elbow*s, 0.065*s, "bark", 8, end_radius=0.036*s)
        b.cylinder(elbow*s, end*s, 0.036*s, "bark", 7, end_radius=0.008*s)
        for j in range(6):
            t = 0.33+j*0.11
            origin = elbow.lerp(end, t)
            branch_angle = angle + (-1 if j % 2 else 1)*rng.uniform(0.4, 1.25)
            endpoint = origin + Vector((math.cos(branch_angle)*rng.uniform(0.38, 0.80),
                                         math.sin(branch_angle)*rng.uniform(0.38, 0.80),
                                         rng.uniform(0.08, 0.48)))
            b.cylinder(origin*s, endpoint*s, 0.012*s, "bark", 5, end_radius=0.003*s)
            clusters.append((endpoint, branch_angle))
        clusters.append((end, angle))
    for c, angle in clusters:
        for j in range(49):
            # Volumetric scatter around tiny twigs: open gaps, layered leaves.
            r = rng.random()**(1/3)
            phi = rng.uniform(0, math.tau)
            cz = rng.uniform(-1, 1)
            rr = math.sqrt(max(0, 1-cz*cz))*r
            p = c+Vector((math.cos(phi)*rr*0.58, math.sin(phi)*rr*0.58, cz*r*0.40))
            leaf_angle = phi+rng.uniform(-0.65, 0.65)
            length = rng.uniform(0.17, 0.28)
            direction = Vector((math.cos(leaf_angle)*length, math.sin(leaf_angle)*length, rng.uniform(-0.06, 0.07)))
            b.leaf(p*s, direction*s, length*rng.uniform(0.43, 0.58)*s, _leaf_color(rng), rng.uniform(-1.1, 1.1))
    return b.finish("street_tree")


def make_planter(position, length=3.0, width=1.0, yaw=0.0, seed=1, collection=None):
    """Masonry planter, 0.52 m rim, dense irregular evergreen shrub (~1.2 m)."""
    rng = random.Random(seed)
    b = Batch("CQF_Planter_%s" % seed, position, yaw, collection)
    h = 0.52
    for y in (-width/2, width/2):
        b.box((0, y, h/2), (length, 0.15, h), "stone")
        b.box((0, y, h+0.025), (length+0.13, 0.23, 0.095), "stone_edge")
    for x in (-length/2, length/2):
        b.box((x, 0, h/2), (0.15, width, h), "stone")
        b.box((x, 0, h+0.025), (0.23, width+0.18, 0.095), "stone_edge")
    b.box((0, 0, h-0.075), (length-0.15, width-0.12, 0.09), "soil")
    # Joints and small low damp patches are real raised narrow strips.
    for x in range(max(1, int(length/0.6))):
        xx = -length/2+0.3+x*0.6
        for y in (-width/2-0.077, width/2+0.077):
            b.box((xx, y, 0.26), (0.01, 0.004, 0.46), "stone_dark")
    for i in range(int(length*7)):
        p = Vector((rng.uniform(-length/2+0.16, length/2-0.16), rng.uniform(-width/2+0.12, width/2-0.12), h-0.06))
        top = p + Vector((rng.uniform(-0.13, 0.13), rng.uniform(-0.13, 0.13), rng.uniform(0.4, 0.72)))
        b.cylinder(p, top, 0.015, "bark_dark", 5, end_radius=0.005)
        for j in range(52):
            phi = rng.uniform(0, math.tau)
            dist = rng.uniform(0.06, 0.28)
            leafpos = top+Vector((math.cos(phi)*dist, math.sin(phi)*dist, rng.uniform(-0.31, 0.13)))
            length_leaf = rng.uniform(0.08, 0.145)
            d = Vector((math.cos(phi)*length_leaf, math.sin(phi)*length_leaf, rng.uniform(-0.045, 0.06)))
            b.leaf(leafpos, d, length_leaf*0.6, _leaf_color(rng), rng.uniform(-1.1, 1.1))
    return b.finish("masonry_planter")


def _wheel(b, y, z, radius=0.225):
    b.torus((0, y, z), radius-0.045, 0.05, "rubber", steps=36, sides=10, flatten=1.45)
    for x in (-0.072, 0.072):
        b.cylinder((x-0.006, y, z), (x+0.006, y, z), radius*0.69, "steel", 24)
        b.torus((x, y, z), radius*0.72, 0.008, "black_metal", steps=24, sides=6)
        for i in range(6):
            a = i*math.tau/6
            b.cylinder((x, y, z), (x, y+math.sin(a)*radius*0.62, z+math.cos(a)*radius*0.62), 0.009, "black_metal", 6)
    b.cylinder((-0.105, y, z), (0.105, y, z), 0.032, "steel", 12)
    # Shallow rubber tread strips on the surface.
    for i in range(22):
        a = i*math.tau/22
        p = Vector((-0.047, y+math.sin(a)*(radius+0.006), z+math.cos(a)*(radius+0.006)))
        q = Vector((0.047, y+math.sin(a+0.07)*(radius+0.006), z+math.cos(a+0.07)*(radius+0.006)))
        b.cylinder(p, q, 0.006, "rubber_worn", 4)


def make_scooter(position, yaw=0.0, delivery=True, seed=1, collection=None):
    """Street electric scooter; forward is local +Y; ~1.9 x 0.68 x 1.25 m."""
    b = Batch("CQF_Scooter_%s" % seed, position, yaw, collection)
    paint = "paint_teal" if seed % 2 else "paint_cream"
    _wheel(b, -0.58, 0.24)
    _wheel(b, 0.66, 0.24)
    # Rounded engine cover and fender, swept rather than box-bodied.
    b.loft_y([(-0.88, 0.44, 0.08, 0.07), (-0.70, 0.50, 0.23, 0.17),
              (-0.30, 0.50, 0.25, 0.20), (-0.08, 0.39, 0.22, 0.12)], paint, 20)
    b.loft_y([(-0.08, 0.29, 0.19, 0.045), (0.35, 0.29, 0.19, 0.045),
              (0.48, 0.39, 0.18, 0.09), (0.49, 0.67, 0.21, 0.08),
              (0.49, 0.87, 0.21, 0.08), (0.54, 0.98, 0.16, 0.05)], paint, 16)
    b.box((0, 0.15, 0.345), (0.34, 0.52, 0.022), "rubber_worn")
    for x in (-0.11, -0.04, 0.04, 0.11):
        b.box((x, 0.15, 0.359), (0.018, 0.43, 0.006), "rubber")
    b.loft_y([(-0.76, 0.72, 0.10, 0.025), (-0.65, 0.755, 0.22, 0.052),
              (-0.13, 0.75, 0.21, 0.05), (0.02, 0.70, 0.13, 0.035)], "seat", 20)
    # Side seam, tail lens and rack rails.
    for side in (-1, 1):
        b.cylinder((side*0.22, -0.64, 0.61), (side*0.23, -0.16, 0.58), 0.009, "steel", 6)
        b.cylinder((side*0.14, -0.77, 0.60), (side*0.14, -0.90, 0.79), 0.014, "black_metal", 7)
        b.cylinder((side*0.14, -0.90, 0.79), (side*0.14, -0.42, 0.79), 0.014, "black_metal", 7)
        # Front fork, rear swingarm, small shiny suspension section.
        b.cylinder((side*0.10, 0.67, 0.24), (side*0.10, 0.49, 0.77), 0.022, "steel", 9)
        b.cylinder((side*0.11, -0.59, 0.26), (side*0.15, -0.22, 0.48), 0.025, "black_metal", 8)
        b.cylinder((side*0.17, -0.60, 0.32), (side*0.17, -0.47, 0.60), 0.018, "steel", 9)
    b.sphere((0, -0.86, 0.55), (0.115, 0.023, 0.055), "tail_lamp", 6, 14)
    # Front fender, handle housing, lamp and mirrors.
    b.loft_y([(0.43, 0.47, 0.055, 0.015), (0.63, 0.51, 0.11, 0.043),
              (0.85, 0.43, 0.08, 0.022)], paint, 16)
    b.cylinder((0, 0.47, 0.89), (0, 0.40, 1.10), 0.029, "black_metal", 10)
    b.cylinder((-0.34, 0.38, 1.10), (0.34, 0.38, 1.10), 0.023, "black_metal", 10)
    b.sphere((0, 0.46, 1.10), (0.18, 0.11, 0.09), paint, 8, 16)
    b.sphere((0, 0.55, 1.10), (0.12, 0.024, 0.054), "lamp", 6, 16)
    for side in (-1, 1):
        b.cylinder((side*0.27, 0.38, 1.10), (side*0.37, 0.38, 1.10), 0.028, "rubber", 10)
        b.cylinder((side*0.23, 0.39, 1.11), (side*0.32, 0.47, 1.34), 0.009, "steel", 6)
        b.sphere((side*0.33, 0.46, 1.36), (0.075, 0.025, 0.048), "black_metal", 6, 12)
        b.sphere((side*0.33, 0.438, 1.36), (0.065, 0.006, 0.038), "mirror", 6, 12)
        b.cylinder((side*0.25, 0.36, 1.09), (side*0.33, 0.30, 1.07), 0.008, "steel", 5)
    # Foot stand, small pale unbranded rear plate.
    b.cylinder((-0.08, -0.31, 0.30), (-0.26, -0.37, 0.025), 0.012, "black_metal", 6)
    b.box((-0.26, -0.37, 0.018), (0.08, 0.05, 0.024), "black_metal")
    b.box((0, -0.904, 0.40), (0.18, 0.018, 0.10), "cream")
    if delivery:
        # Insulated fabric delivery box with black edging, lid and straps.
        b.box((0, -0.58, 1.05), (0.52, 0.46, 0.47), "plastic_orange")
        b.box((0, -0.58, 1.29), (0.55, 0.49, 0.045), "plastic_orange")
        for x in (-0.258, 0.258):
            for y in (-0.809, -0.351):
                b.box((x, y, 1.05), (0.017, 0.017, 0.48), "rubber")
        for y in (-0.816, -0.344):
            for z in (0.825, 1.27):
                b.box((0, y, z), (0.52, 0.015, 0.018), "rubber")
        b.box((0, -0.819, 1.08), (0.30, 0.009, 0.115), "cream")
        for x in (-0.16, 0.16):
            b.box((x, -0.58, 1.316), (0.031, 0.46, 0.008), "rubber")
    return b.finish("delivery_scooter" if delivery else "electric_scooter")


def _bin(b, x, y, color, lid_tilt=0.0):
    # Tapered four-sided body with reinforcing lip and ribs.
    z0, z1 = 0.08, 0.94
    a, c = 0.225, 0.285
    vertices = [(x-a, y-a, z0), (x+a, y-a, z0), (x+a, y+a, z0), (x-a, y+a, z0),
                (x-c, y-c, z1), (x+c, y-c, z1), (x+c, y+c, z1), (x-c, y+c, z1)]
    b.mesh(vertices, [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)], color)
    b.box((x, y, 0.925), (0.60, 0.60, 0.065), color)
    b.box((x, y+0.015, 0.985), (0.63, 0.64, 0.075), color)
    b.box((x, y-0.295, 0.997), (0.27, 0.06, 0.035), "black_metal")
    for xx in (-0.17, 0.17):
        b.box((x+xx, y-0.26, 0.52), (0.025, 0.025, 0.69), color)
        b.cylinder((x+xx, y+0.28, 0.96), (x+xx, y+0.32, 0.88), 0.035, "black_metal", 8)
    b.cylinder((x-0.32, y+0.22, 0.135), (x+0.32, y+0.22, 0.135), 0.025, "steel", 8)
    for xx in (-0.295, 0.295):
        b.cylinder((x+xx-0.033, y+0.22, 0.135), (x+xx+0.033, y+0.22, 0.135), 0.12, "rubber", 16)
        b.cylinder((x+xx-0.035, y+0.22, 0.135), (x+xx+0.035, y+0.22, 0.135), 0.038, "steel", 12)
    b.box((x, y-0.291, 0.68), (0.25, 0.006, 0.13), "cream")
    # A simple three-line symbol, without a third-party logo or copied label.
    for zz in (0.65, 0.68, 0.71):
        b.box((x, y-0.296, zz), (0.15 if zz != 0.71 else 0.10, 0.005, 0.009), "plastic_green")


def make_bins(position, yaw=0.0, collection=None):
    b = Batch("CQF_Bins", position, yaw, collection)
    _bin(b, -0.37, 0.04, "plastic_green")
    _bin(b, 0.35, 0, "plastic_green_light")
    return b.finish("wheelie_bins")


def make_street_lamp(position, height=5.0, collection=None):
    b = Batch("CQF_StreetLamp", position, collection=collection)
    b.cylinder((0, 0, 0), (0, 0, 0.36), 0.12, "black_metal", 12, end_radius=0.085)
    b.cylinder((0, 0, 0.30), (0, 0, height), 0.062, "black_metal", 12, end_radius=0.038)
    path = [(0, 0, height-0.40), (0, 0.12, height-0.04), (0, 0.45, height+0.12), (0, 0.90, height+0.12)]
    for a, c in zip(path, path[1:]):
        b.cylinder(a, c, 0.035, "black_metal", 10)
    b.sphere((0, 0.90, height+0.09), (0.23, 0.36, 0.10), "black_metal", 8, 16)
    b.sphere((0, 0.90, height+0.025), (0.18, 0.27, 0.028), "lamp", 6, 16)
    for x in (-0.07, 0.07):
        for y in (-0.07, 0.07):
            b.cylinder((x,y,0), (x,y,0.04), 0.014, "steel", 6)
    return b.finish("street_lamp")


def _chair(b, position, angle=0.0):
    p = Vector(position)
    c, s = math.cos(angle), math.sin(angle)
    def t(v):
        return p+Vector((c*v[0]-s*v[1], s*v[0]+c*v[1], v[2]))
    for x in (-0.18, 0.18):
        for y in (-0.18, 0.18):
            b.cylinder(t((x*1.15,y*1.15,0.02)), t((x,y,0.45)), 0.014, "steel", 8)
        b.cylinder(t((x,0.18,0.36)), t((x,0.22,0.86)), 0.014, "steel", 8)
        b.cylinder(t((x,-0.18,0.24)), t((x,0.18,0.24)), 0.01, "steel", 6)
    # Rotated boxes supplied as transformed corner meshes.
    for z, y, dims in [(0.46, 0, (0.43,0.40,0.037)), (0.70,0.21,(0.43,0.035,0.12)), (0.82,0.22,(0.43,0.035,0.10))]:
        a, d, h = [v/2 for v in dims]
        vs = [t((xx,y+yy,z+zz)) for xx,yy,zz in [(-a,-d,-h),(a,-d,-h),(a,d,-h),(-a,d,-h),(-a,-d,h),(a,-d,h),(a,d,h),(-a,d,h)]]
        b.mesh(vs, [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)], "paint_red")


def make_cafe_set(position, yaw=0.0, collection=None):
    b = Batch("CQF_CafeSet", position, yaw, collection)
    b.cylinder((0,0,0.68),(0,0,0.75),0.45,"wood_light",32)
    b.cylinder((0,0,0.06),(0,0,0.71),0.048,"black_metal",10)
    for i in range(4):
        a = math.tau*i/4
        b.cylinder((0,0,0.12),(math.cos(a)*0.34,math.sin(a)*0.34,0.025),0.027,"black_metal",8)
    _chair(b, (0,-0.82,0), math.pi)
    _chair(b, (0.78,0.06,0), -math.pi/2)
    b.cylinder((-0.16,0.12,0.754),(-0.16,0.12,0.90),0.042,"cream",16)
    b.cylinder((0.13,0.02,0.756),(0.13,0.02,0.82),0.11,"cream",24)
    b.cylinder((0.13,0.02,0.821),(0.13,0.02,0.826),0.092,"wood_dark",24)
    for x in (-0.10,-0.07):
        b.cylinder((x,-0.18,0.756),(x+0.19,-0.07,0.756),0.003,"wood",5)
    return b.finish("cafe_table_and_chairs")


def make_crates(position, yaw=0.0, collection=None):
    b = Batch("CQF_Crates", position, yaw, collection)
    for n, (x,y,z) in enumerate([(0,0,0), (0.56,0.05,0), (0.05,0,0.35)]):
        color = "wood_light" if n == 2 else "wood"
        for k in range(4):
            yy = y-0.19+k*0.125
            b.box((x,yy,z+0.025),(0.50,0.10,0.04),color)
        for xx in (-0.23,0.23):
            for yy in (-0.21,0.21):
                b.box((x+xx,y+yy,z+0.17),(0.035,0.035,0.34),"wood_dark")
        for k in range(3):
            for yy in (-0.23,0.23):
                b.box((x,y+yy,z+0.075+k*0.115),(0.51,0.025,0.08),color)
            for xx in (-0.26,0.26):
                b.box((x+xx,y,z+0.075+k*0.115),(0.025,0.46,0.08),color)
        if n == 1:
            for i in range(3):
                for j in range(3):
                    xx,yy=x-0.15+i*0.15,y-0.15+j*0.15
                    b.cylinder((xx,yy,z+0.04),(xx,yy,z+0.25),0.045,"bottle",12)
                    b.cylinder((xx,yy,z+0.25),(xx,yy,z+0.30),0.045,"bottle",12,end_radius=0.023)
                    b.cylinder((xx,yy,z+0.30),(xx,yy,z+0.39),0.023,"bottle",12)
                    b.cylinder((xx,yy,z+0.39),(xx,yy,z+0.405),0.025,"plastic_yellow",12)
    return b.finish("wood_crates_and_bottles")


def make_clothesline(position, span=5.0, yaw=0.0, seed=1, collection=None):
    """A lightly sagged wire with original low-poly shirts and towels."""
    b = Batch("CQF_Clothesline_%s" % seed, position, yaw, collection)
    points = [(-span/2+span*i/12,0,-0.12*math.sin(math.pi*i/12)) for i in range(13)]
    for a,c in zip(points,points[1:]):
        b.cylinder(a,c,0.004,"black_metal",5)
    rng = random.Random(seed)
    for i in range(5):
        x = -span*0.35+i*span*0.17
        z = -0.12*math.sin(math.pi*(x/span+0.5))
        mat = rng.choice(["cream","paint_teal","paint_red","plastic_blue"])
        for j in range(5):
            xx = x-0.20+j*0.1
            y = 0.026*math.sin(j*1.7+i)
            cloth=[(xx,y,z-0.06), (xx+0.1,0.026*math.sin((j+1)*1.7+i),z-0.06),
                   (xx+0.1,0.06*math.sin((j+1)*1.7+i),z-0.70), (xx,0.06*math.sin(j*1.7+i),z-0.70)]
            # Independent vertices keep front/back smooth normals from cancelling.
            b.mesh(cloth,[(0,3,2,1)],mat,True)
            b.mesh(cloth,[(0,1,2,3)],mat,True)
        for xx in (x-0.14,x+0.14):
            b.box((xx,0,z-0.02),(0.018,0.028,0.075),"wood_light")
    return b.finish("clothesline")


def make_van(position, yaw=0.0, collection=None):
    """Original unbranded compact cargo van, local +Y forward, 4 x 1.8 x 2 m.

    Deliberately a parked background prop: no rig, suspension simulation,
    drivable vehicle system, copied manufacturer badges, or trademarks.
    """
    b = Batch("CQF_WhiteMicrovan", position, yaw, collection)
    profiles = [(-1.98, .78, .37, 1.72, 1.90), (-1.82, .86, .31, 1.80, 2.00),
                (.72, .86, .31, 1.80, 2.00), (1.40, .83, .31, 1.38, 1.58),
                (1.93, .78, .37, 1.04, 1.19)]
    vs = []
    for y, w, low, shoulder, roof in profiles:
        vs.extend([(-w+.06,y,low), (w-.06,y,low), (w,y,low+.10), (w,y,shoulder),
                   (w-.10,y,roof), (-w+.10,y,roof), (-w,y,shoulder), (-w,y,low+.10)])
    faces = [tuple(range(7,-1,-1)),tuple(range((len(profiles)-1)*8,len(profiles)*8))]
    for i in range(len(profiles)-1):
        for j in range(8):
            faces.append((i*8+j, i*8+(j+1)%8, (i+1)*8+(j+1)%8, (i+1)*8+j))
    # Viewed from the front, profiles run counter-clockwise. Reverse all
    # surface faces to keep the van body uniformly outward.
    b.mesh(vs,[tuple(reversed(f)) for f in faces],"paint_white",False)
    b.box((0,0,.29),(1.48,3.65,.15),"black_metal")
    # Both wheel sets are separate, with real tire profile and hub shapes.
    for y in (-1.25,1.27):
        for side in (-1,1):
            x=side*.84
            b.torus((x,y,.34),.265,.075,"rubber",steps=40,sides=10,flatten=1.35)
            b.cylinder((x-.085,y,.34),(x+.085,y,.34),.215,"black_metal",28)
            xo=x+side*.092
            b.cylinder((xo-.008,y,.34),(xo+.008,y,.34),.182,"steel",24)
            b.cylinder((xo-.012,y,.34),(xo+.012,y,.34),.072,"paint_white",20)
            for j in range(6):
                a=j*math.tau/6
                yy,zz=y+math.sin(a)*.115,.34+math.cos(a)*.115
                b.cylinder((xo-.012,yy,zz),(xo+.012,yy,zz),.028,"black_metal",10)
    # Side glazing, large sliding cargo panel, metal door seams, mirror stalk.
    for side in (-1,1):
        x=side*.866
        def side_quad(y0,y1,z0,z1,mat):
            verts=[(x,y0,z0),(x,y1,z0),(x,y1,z1),(x,y0,z1)]
            b.mesh(verts,[(0,1,2,3) if side>0 else (3,2,1,0)],mat)
        side_quad(-1.62,-.56,1.11,1.69,"black_metal")
        # Van rear glazing partially blanked by an opaque white cargo panel.
        side_quad(-1.57,-.61,1.16,1.64,"window")
        side_quad(-.42,.48,1.10,1.73,"black_metal")
        side_quad(-.37,.43,1.15,1.68,"window")
        # Driver quarter-window follows the slanted windshield pillar.
        verts=[(side*.86,.56,1.08),(side*.823,1.30,1.08),
               (side*.823,1.27,1.50),(side*.76,.60,1.91)]
        b.mesh(verts,[(0,1,2,3) if side>0 else (3,2,1,0)],"black_metal")
        inset=[(side*.863,.63,1.13),(side*.827,1.24,1.13),
               (side*.827,1.21,1.48),(side*.765,.64,1.82)]
        b.mesh(inset,[(0,1,2,3) if side>0 else (3,2,1,0)],"window")
        for y0 in (-1.74,-.51,.53):
            b.cylinder((x,y0,.53),(x,y0,1.79),.006,"black_metal",5)
        b.cylinder((x,-1.72,.54),(x,.52,.54),.006,"black_metal",5)
        b.cylinder((x,-1.72,.91),(x,.52,.91),.017,"rubber",7)
        for yy in (-.37,.65):
            b.box((x+side*.008,yy,1.0),(.035,.18,.039),"black_metal")
        b.cylinder((side*.84,1.17,1.2),(side*1.00,1.20,1.32),.018,"black_metal",8)
        b.sphere((side*1.04,1.20,1.34),(.064,.13,.075),"black_metal",7,14)
        b.sphere((side*1.05,1.09,1.34),(.051,.012,.06),"mirror",6,12)
    # Front windshield and rubber surround follow the slanted cab plane.
    front=[(-.69,.745,1.999),(.69,.745,1.999),(.735,1.386,1.606),(-.735,1.386,1.606)]
    b.mesh(front,[(0,1,2,3)],"black_metal")
    glass=[(-.625,.790,1.974),(.625,.790,1.974),(.68,1.34,1.635),(-.68,1.34,1.635)]
    b.mesh(glass,[(0,1,2,3)],"window")
    for x in (-.39,.31):
        b.cylinder((x,1.37,1.59),(x+.17,1.13,1.74),.011,"black_metal",6)
    b.box((0,1.944,.62),(1.58,.105,.16),"rubber_worn")
    b.box((0,1.987,.86),(.68,.019,.22),"black_metal")
    for z in (.79,.85,.91):
        b.box((0,2.002,z),(.62,.012,.012),"steel")
    for x in (-.57,.57):
        b.box((x,1.974,1.05),(.28,.03,.15),"lamp")
        b.box((x,1.98,.92),(.25,.03,.06),"plastic_orange")
    b.box((0,2.009,.58),(.39,.015,.11),"plastic_blue")
    # Rear doors, seals, cargo handle, vertical red tail lenses.
    b.box((0,-1.99,1.12),(.012,.012,1.40),"black_metal")
    for x in (-.37,.37):
        b.box((x,-1.992,1.52),(.58,.016,.43),"black_metal")
        b.box((x,-2.003,1.52),(.51,.01,.36),"window")
    b.box((0,-2.015,.55),(1.56,.10,.15),"rubber_worn")
    b.box((.12,-2.016,1.0),(.14,.022,.04),"black_metal")
    for x in (-.69,.69):
        b.box((x,-2.006,.92),(.12,.03,.30),"tail_lamp")
        b.box((x,-2.024,1.015),(.10,.012,.07),"plastic_orange")
    b.box((-.2,-2.026,.68),(.33,.012,.12),"plastic_blue")
    return b.finish("parked_cargo_microvan")


def create_props(collection=None):
    """Optional independent mini-layout. Production assembly should place explicitly."""
    placements = [
        ("tree", make_tree((9,8,0), seed=11, collection=collection)),
        ("planter", make_planter((3,5,0), length=3, seed=12, collection=collection)),
        ("scooter", make_scooter((0,0,0), seed=13, collection=collection)),
        ("bins", make_bins((-2,0,0), collection=collection)),
        ("lamp", make_street_lamp((5,0,0), collection=collection)),
        ("cafe", make_cafe_set((0,4,0), collection=collection)),
        ("crates", make_crates((-3,4,0), collection=collection)),
    ]
    return {"origin":"Original procedural props", "units":"metres", "assets":[
        {"kind":kind, "objects":[o.name for o in objects],
         "triangles":sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)}
        for kind,objects in placements]}
