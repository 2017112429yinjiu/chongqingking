"""Turn the former plot 43 rear steps onto the uphill side of Liangtingzi."""
from math import ceil, cos, sin

from mathutils import Vector
from mathutils.geometry import convex_hull_2d

from factory import Mesh, material, terrain


def build_rear_stair(plot, street):
    ground = terrain()
    finish = material('Liangtingzi dressed stair stone', (.63, .65, .64), 'stone_floor_diff_2k.jpg')
    sides = material('Liangtingzi stair ashlar', (.67, .67, .64), 'stone_wall_05_diff_2k.jpg')
    stair = Mesh('COL_Liangtingzi_RearStair_43')
    width = 1.72

    def grade(point):
        hit, _, _, _ = ground.ray_cast(Vector((point.x, point.y, 105)), Vector((0, 0, -1)), 150)
        if hit is None:
            raise ValueError(f'Unsupported stair edge at {tuple(point)}')
        return hit.z

    def rect(a, b):
        direction = (b - a).normalized()
        side = Vector((-direction.y, direction.x)) * (width / 2)
        return [a - side, b - side, b + side, a + side]

    def stone_patch(ring, height):
        upper = [(p.x, p.y, height) for p in ring]
        lower = [(p.x, p.y, min(grade(p) - .10, height - .20)) for p in ring]
        stair.face(lower[::-1], sides)
        stair.face(upper, finish)
        for i, j in zip(range(len(ring)), (*range(1, len(ring)), 0)):
            stair.face([lower[i], lower[j], upper[j], upper[i]], sides)

    def steps(a, b, upper, lower):
        count = ceil((upper - lower) / .155)
        assert count >= 2 and (b - a).length / count >= .285
        for i in range(count):
            start = a.lerp(b, i / count)
            finish = a.lerp(b, (i + 1) / count)
            stone_patch(rect(start, finish), upper + (lower - upper) * i / count)
        return count

    bearing = plot['bearing']
    rear = Vector((-sin(bearing), cos(bearing)))
    centre = Vector(plot['east_north'])
    door = centre + plot['depth'] / 2 * rear + plot['door_u'] * Vector((cos(bearing), sin(bearing)))
    top = plot['height'] + .025
    first_tread = door + 1.18 * rear
    landing = door + 3.20 * rear
    hinge_level = top - .80
    stone_patch(rect(door, first_tread), top)
    first = steps(first_tread, landing, top, hinge_level)

    along = (Vector(street[4]) - Vector(street[3])).normalized()
    next_tread = landing + along * 1.04
    low = next_tread + along * 12.60
    bottom = grade(low) + .035
    turn = rect(landing - rear * .02, landing + rear * .20) + rect(landing, next_tread)
    stone_patch([turn[i] for i in convex_hull_2d(turn)], hinge_level)
    second = steps(next_tread, low, hinge_level, bottom)
    approach = low + .80 * along
    walk = [(*list(door - .55 * rear), top), (*list(first_tread), top),
            (*list(landing - .18 * rear), hinge_level + .10),
            (*list(next_tread - .16 * along), hinge_level),
            (*list(next_tread.lerp(low, .4)), hinge_level + (bottom - hinge_level) * .4),
            (*list(next_tread.lerp(low, .75)), hinge_level + (bottom - hinge_level) * .75),
            (*list(approach), grade(approach) + .04)]
    return stair.save(), {'path_east_north_up': walk, 'steps': [first, second],
                          'width_m': width, 'rise_m': top - bottom}
