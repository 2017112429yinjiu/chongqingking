"""Terrain-conforming finishes and street fittings at the Binjiang public entrances."""
from math import cos, pi, sin
from random import Random

import bpy
import numpy as np
from mathutils import Vector

from factory import Mesh
from riverside import strip


def flagstone(material, writer, directory):
    """Lay out staggered stone flags in the normal two-metre ground UV tile."""
    size = 512
    x, y = np.meshgrid(np.arange(size), np.arange(size))
    row = y * 6 // size
    offset_x = (x + (row % 2) * 51) % size
    column = offset_x * 5 // size
    grout = ((offset_x * 5) % size < 12) | ((y * 6) % size < 12)
    variation = (column * 17 + row * 23) % 7 - 3
    grain = np.random.default_rng(72).normal(0, 1.8, (size, size))
    value = 157 + 2 * variation + grain - 32 * grout
    image = np.stack([value - 1, value, value + 1], axis=-1).clip(0, 255).astype(np.uint8)
    path = directory / "Binjiang-small-grey-street-flags.png"
    writer(path, image)
    tree = material.node_tree
    tex = tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(path))
    tex.image.pack()
    tree.links.new(tex.outputs["Color"], tree.nodes["Principled BSDF"].inputs["Base Color"])


def pad(center, tangent, width, depth):
    cross = Vector((-tangent.y, tangent.x))
    return [center + tangent * x + cross * y
            for x, y in ((-depth/2,-width/2),(depth/2,-width/2),(depth/2,width/2),(-depth/2,width/2))]


def solid(mesh, ring, ground, base, top, mat):
    heights = [ground(p) for p in ring]
    mesh.solid([(*p,z+base) for p,z in zip(ring,heights)],
               [(*p,z+top) for p,z in zip(ring,heights)],mat)


def rail_between(mesh, a, b, width, ground, base, top, mat):
    solid(mesh,pad((a+b)/2,(b-a).normalized(),width,(b-a).length),ground,base,top,mat)


def canopy(mesh, root, radius, height, leaves, finishes, seed):
    """Small branching clumps of broad leaves for the garden beds and roof edge."""
    random = Random(seed)
    for _ in range(leaves):
        azimuth = random.uniform(0, 2*pi)
        distance = radius * random.uniform(.32, 1.)
        level = random.uniform(.18, 1.)
        point = root + Vector((cos(azimuth)*distance*(1.-.48*level),
                               sin(azimuth)*distance*(1.-.48*level), height*level))
        direction = Vector((cos(azimuth),sin(azimuth),random.uniform(-.27,.38)))
        sideways = Vector((-sin(azimuth),cos(azimuth),random.uniform(-.27,.27)))
        scale = random.uniform(.13,.30)*radius
        tip = point+direction*scale*2.4
        broad = point+direction*scale
        finish = finishes[random.randrange(len(finishes))]
        mesh.face([tuple(point),tuple(broad+sideways*scale*.57),tuple(tip)],finish)
        mesh.face([tuple(point),tuple(tip),tuple(broad-sideways*scale*.50)],finish)


def planting_box(edges, plants, center, tangent, width, depth, ground, m, guard=False):
    ring = pad(center,tangent,width,depth)
    solid(edges,ring,ground,-.09,.21,m["foot"])
    solid(plants,pad(center,tangent,width-.18,depth-.18),ground,.17,.225,m["soil"])
    cross = Vector((-tangent.y,tangent.x))
    for index, offset in enumerate((-.31,-.06,.25)):
        position = center+tangent*(depth*offset)+cross*((index%2-.5)*width*.21)
        root = Vector((*position,ground(position)+.225))
        seed = int(1000*position.x)+int(1100*position.y)
        canopy(plants,root,min(width*.33,.46),.43+index*.063,136,
               [m["leaf"],m["leaf"],m["leaf_lit"]],seed)
    if guard:
        a,b=ring[0],ring[1]
        rail_between(edges,a,b,.075,ground,.49,.56,m["rail"])
        for index in range(6):
            p=a.lerp(b,index/5)
            solid(edges,pad(p,tangent,.068,.068),ground,.20,.51,m["rail"])


def public_entry(stations, ground, tiles, painter, m):
    pts = [Vector(p) for p in stations]
    along = (pts[1]-pts[0]).normalized()
    across = Vector((-along.y,along.x))
    entry = Mesh("COL_Binjiang_Walk_72")
    landings = Mesh("COL_Binjiang_Entry72_Footway")
    stripes = Mesh("Binjiang_Entry72_CrossingPaint")
    gutter = Mesh("Binjiang_Entry72_IronGrates")
    kerbs = Mesh("COL_Binjiang_Entry72_LowKerbs")
    planter = Mesh("COL_Binjiang_Entry_PlanterBorders")
    planting = Mesh("Binjiang_Entry_ContainedPlanting")
    gatehouse = Mesh("COL_Binjiang_Entry72_SetbackGatehouse")
    booth = Mesh("Binjiang_Entry72_GatehouseFrames")

    def project(mesh, faces, material, lift):
        targets = [triangle for face in faces for triangle in painter["triangle_parts"](face)]
        return painter["project"](mesh,targets,tiles,[],material,lift=lift)

    inlet = pts[0]-along*.53
    straight = [inlet,*pts[:4]]
    continuation = [*pts[3:],pts[-1]+(pts[-1]-pts[-2]).normalized()*.58]
    road_points = [p.to_3d() for p in straight]
    path_points = [p.to_3d() for p in continuation]
    project(entry,strip(road_points,2.65,-2.65),m["entry_asphalt"],.067)
    project(entry,strip(path_points,1.23,-1.23),m["entry_flags"],.067)
    for sign in (-1,1):
        limits=sorted((sign*2.65,sign*4.22),reverse=True)
        project(landings,strip(road_points[:4],*limits),m["entry_flags"],.113)
        for a,b in zip(straight[:3],straight[1:4]):
            delta=(b-a).normalized()
            border=Vector((-delta.y,delta.x))*sign*2.67
            rail_between(kerbs,a+border,b+border,.14,ground,.025,.129,m["edge"])
    crossing = pts[0]+along*1.46
    for i in range(10):
        center = crossing+across*((i-4.5)*.485)
        project(stripes,[pad(center,along,.274,2.18)],m["road_paint"],.080)
    project(stripes,[pad(inlet+along*.099,along,5.12,.15)],m["road_paint"],.079)
    drain_anchor=pts[0]+along*.23
    for sign in (-1,1):
        center=drain_anchor+across*(sign*2.13)
        project(gutter,[pad(center,along,.73,.27)],m["drain"],.079)
        for i in range(11):
            p=center+across*((i-5)*.061)
            project(gutter,[pad(p,along,.016,.235)],m["rail"],.086)
        side=pts[1]+along*.35+across*(sign*2.98)
        rail_between(kerbs,side-along*.13,side+along*.86,.16,ground,.032,.141,m["edge"])

    # The extant tree remains rooted at its local survey position, within a bounded bed outside the walking strip.
    planting_box(planter,planting,Vector((115.252,-129.066)),along,1.28,2.58,ground,m)
    planting_box(planter,planting,pts[1]+along*.1+across*4.57,along,1.40,3.15,ground,m,True)
    planting_box(planter,planting,pts[0]+along*2.86-across*4.52,along,1.16,1.63,ground,m,True)
    planting_box(planter,planting,Vector((88.16,-113.1)),along,1.12,2.22,ground,m)
    planting_box(planter,planting,Vector((106.18,-131.70)),along,1.02,2.10,ground,m)

    hut = Vector((115.45,-119.55))
    z=ground(hut)
    def flat(_):
        return z

    solid(gatehouse,pad(hut,along,1.44,1.51),flat,-.13,.59,m["foot"])
    solid(gatehouse,pad(hut,along,1.37,1.43),flat,.59,2.19,m["greyblue"])
    solid(gatehouse,pad(hut,along,1.78,1.80),flat,2.15,2.32,m["coping"])
    for side in (-1,1):
        for end in (-1,1):
            post=hut+across*(side*.66)+along*(end*.68)
            solid(booth,pad(post,along,.12,.12),flat,.54,2.2,m["rail"])
        for h in (.66,1.33,2.06):
            rail_between(booth,hut+across*(side*.674)-along*.72,hut+across*(side*.674)+along*.72,
                         .058,flat,h,h+.052,m["rail"])
    return [mesh.save() for mesh in (entry,landings,stripes,gutter,kerbs,planter,planting,gatehouse,booth)]
