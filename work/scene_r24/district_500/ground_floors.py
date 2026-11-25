"""Public ground floors and their two hillside thresholds, in plot metres."""
from math import ceil


def through_floor(p, draw, ground, mats):
    w, d, z = p["width"], p["depth"], p["height"]
    left, right, front, back = -w/2, w/2, -d/2, d/2
    mid = p["door_u"]
    half = 1.92 if p["name"] else 1.08
    wall, stone, masonry, slab, lining = mats
    crown = z+2.82
    draw(left, front, crown, right, back, p["roof"], wall)
    for edge in (front, back-.23):
        if p["name"] and edge==front:
            draw(left,edge,z,left+.49,edge+.28,crown,wall)
            draw(right-.49,edge,z,right,edge+.28,crown,wall)
            continue
        draw(left, edge, z, mid-half, edge+.23, crown, wall)
        draw(mid+half, edge, z, right, edge+.23, crown, wall)
        draw(mid-half, edge, z+2.45, mid+half, edge+.23, crown, slab)
    # The lower band and lintel frame an actual window cut into each end wall.
    for edge in (left, right-.24):
        draw(edge, front+.23, z, edge+.24, back-.23, z+.87, masonry)
        draw(edge, front+.23, z+2.13, edge+.24, back-.23, crown, wall)
        for v0,v1 in ((front+.23,-1.18),(1.18,back-.23)):
            draw(edge, v0, z+.87, edge+.24, v1, z+2.13, wall)
    draw(left+.02,front+.02,z+.005,right-.02,back-.02,z+.035,lining)
    # Steps start at a sampled lower landing. Extend the run until its
    # nosings can clear the local terrain with ordinary residential risers.
    def apron(edge, direction):
        pad=1.40
        for steps in range(1,34):
            run=pad+steps*.32
            low=ground(mid,edge+direction*run)
            if z-low <= steps*.155:
                break
        rise=max(0,z+.025-low)
        for i in range(steps):
            v0=edge+direction*(pad+i*.32)
            v1=v0+direction*.32
            level=z+.025-rise*i/steps
            lower=min(ground(mid-1.18,v0),ground(mid+1.18,v1),level-.2)-.15
            draw(mid-1.25,min(v0,v1),lower,mid+1.25,max(v0,v1),level,stone)
        v=edge+direction*pad
        draw(mid-1.25,min(edge,v),min(ground(mid-1.25,v),ground(mid+1.25,v),z-.15)-.18,
             mid+1.25,max(edge,v),z+.025,stone)
        return round(run,3)
    p["back_stair_m"] = apron(back,1)
    if not p["name"]:
        p["front_stair_m"] = apron(front,-1)
