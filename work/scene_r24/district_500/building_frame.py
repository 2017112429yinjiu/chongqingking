"""Occupied outer buildings, using one aligned frame from plinth to roof."""
from math import ceil


STOREY = 2.95
SLAB = .15


def split_bays(anchors, span):
    axes = [anchors[0]]
    for left, right in zip(anchors, anchors[1:]):
        count = ceil((right - left) / span)
        axes.extend(left + (right - left) * i / count for i in range(1, count + 1))
    return axes


def build(plot, draw, concrete):
    width, depth = plot["width"], plot["depth"]
    half_w, half_d = width / 2, depth / 2
    aisle = plot["door_u"]
    left, right = -half_w + .19, half_w - .19
    if plot["name"]:
        anchors = [left, aisle - 2.04, aisle + 2.04, right]
    else:
        side = 1 if aisle < 0 else -1
        partition = aisle + side * 1.40
        opposite = aisle - side * 1.50
        anchors = sorted((left, partition, opposite, right))
    us = split_bays(anchors, 4.85)
    # The cross-passage and the two opposing side windows sit midway along the
    # house. Put the middle pair of cross frames either side of those openings.
    vs = split_bays([-half_d + .20, -1.75, 1.75, half_d - .20], 4.85)
    radius = .19 if plot["name"] or plot["floors"] >= 5 else .16
    depth_u = .39 if plot["name"] else .32
    depth_v = .29
    z = plot["height"]
    for x in us:
        for y in vs:
            draw(x-radius, y-radius, z-.18, x+radius, y+radius, plot["roof"], concrete)
    for level in range(1, plot["floors"] + 1):
        top = z + STOREY * level
        underside = top - SLAB
        draw(-half_w, -half_d, underside, half_w, half_d, top, concrete)
        for y in vs:
            for a, b in zip(us, us[1:]):
                draw(a+radius, y-.145, underside-depth_u, b-radius, y+.145, underside, concrete)
        for x in us:
            for a, b in zip(vs, vs[1:]):
                draw(x-.125, a+radius, underside-depth_v, x+.125, b-radius, underside, concrete)
    plot["frame"] = {"u": us, "v": vs, "radius": radius, "storey": STOREY,
                     "slab": SLAB, "transverse_drop": depth_u, "longitudinal_drop": depth_v}
