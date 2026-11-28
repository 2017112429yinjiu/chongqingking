"""Dress the preserved game entries and the two public levels by Nanqu Road."""
from math import cos, sin
from pathlib import Path
import sys

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from build import ASSETS, SCENE, apply_finish, box, read
sys.path.insert(0,str(HERE))
from garage_return import finish as garage_finish
from garage_facade import finish_public_garage
from stone_stairs import low_stairs, upper_public_way
from repair_bench import EYE_FOOT, EYE_TARGET, make as make_repair_bench


def frame(plot):
    e, n = plot['east_north']
    c, s = cos(plot['bearing']), sin(plot['bearing'])
    return lambda u, v, z: (e + c*u - s*v, n + s*u + c*v, plot['height'] + z)


def repair(scope, plot):
    at = frame(plot)
    make_repair_bench(scope, at)
    court = plot['repair_court']
    scope.points['00'] = [court['street'], court['porch']]
    scope.points['00-tool-eye'] = [at(*EYE_FOOT), at(*EYE_TARGET)]


def tiers(scope):
    stone = scope.finish('worn granite street edge', (.60, .62, .57), 'stone_wall_05_diff_2k.jpg', .23)
    stripe = scope.finish('rough lower street shoulder', (.63, .63, .59), 'concrete_floor_worn_001_diff_2k.jpg', .20)
    slate = scope.mesh('Review52_LowFootwayPaleStoneEdge')
    def at(n, e, z):
        return (e, n, scope.floor(e, n) + z)
    # Narrow inlaid stones follow the public side. The upper road is a
    # different support layer and remains owned by the current grade model.
    for i in range(19):
        n = -110.87 + .745*i
        box(slate, at, n, n+.714, -172.17, -171.84, .009, .034, (stone, stripe)[i % 2])
    scope.points['52'] = [[-171.62, -111.25, 6.73], [-171.62, -96.85, 10.44]]


def stone_landing(scope):
    source = SCENE/'outer_neighborhood/landing_53.blend'
    step = scope.finish('dressed landing tread faces', (.68, .67, .62), 'concrete_floor_worn_001_diff_2k.jpg', .21)
    sides = scope.finish('split stone landing risers', (.53, .54, .48), 'stone_wall_05_diff_2k.jpg', .29)
    part = scope.donor(source, 'COL_Outer500_53_LowLanding')
    apply_finish(part, step, sides)
    scope.points['53'] = [[-141.8983, -76.5209, 10.2521], [-145.2315, -78.8738, 11.6776]]


def thresholds(scope, north, south):
    limestone = scope.finish('worn old entry granite', (.73, .70, .61), 'concrete_floor_worn_001_diff_2k.jpg', .30)
    basalt = scope.finish('damp threshold wall footing', (.39, .44, .43), 'stone_wall_05_diff_2k.jpg', .26)
    bronze = scope.finish('patinated directional insert', (.64, .43, .20), metal=.38)
    at = frame(north)
    edge = -north['depth']/2
    u = north['door_u']
    door = scope.mesh('Review54_DressedOldEntryThreshold')
    box(door, at, u-.98, u+.97, edge-.13, edge+.06, .035, .066, limestone)
    for low, high in ((u-1.14, u-1.02), (u+1.01, u+1.15)):
        box(door, at, low, high, edge-.11, edge+.014, .046, .268, basalt)
    scope.points['54'] = [[-143.4855, -118.4700, 4.5239], [-139.8706, -116.6737, 5.3352]]

    # A small game-route marker at the playable shared courtyard endpoint.
    # No new doorway is placed in the unresolved garage envelope.
    at = frame(south)
    u, v = south['court']['exit_local']
    sign = scope.mesh('Review56_SharedCourtyardEntryStoneAndMarker')
    for i in range(5):
        a = u+.31+i*.30
        box(sign, at, a, a+.281, v-.42, v-.25, .061, .084, limestone)
    sign.face([at(u+.61, v-.386, .085), at(u+.90, v-.386, .085), at(u+.90, v-.292, .085),
               at(u+.61, v-.292, .085)], bronze)
    sign.face([at(u+.61, v-.412, .085), at(u+.61, v-.269, .085), at(u+.47, v-.34, .085)], bronze)
    scope.points['56'] = [[-128.6075, -110.7911, 4.6314], [-124.3973, -123.9423, 4.3329]]


def make(scope):
    plots = {p['plot_id']: p for p in read(ASSETS/'district_500/layout.json')['plots']}
    repair(scope, plots[0])
    tiers(scope)
    stone_landing(scope)
    low_stairs(scope, plots[53])
    upper_public_way(scope)
    thresholds(scope, plots[54], plots[56])
    garage_finish(scope,frame(plots[56]),plots[56])
    finish_public_garage(scope)
