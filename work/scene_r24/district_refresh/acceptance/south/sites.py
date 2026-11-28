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


def frame(plot):
    e, n = plot['east_north']
    c, s = cos(plot['bearing']), sin(plot['bearing'])
    return lambda u, v, z: (e + c*u - s*v, n + s*u + c*v, plot['height'] + z)


def repair(scope, plot):
    at = frame(plot)
    bench = scope.mesh('Review00_RepairBenchAndHandTools')
    wood = scope.finish('scuffed workshop timber', (.57, .44, .29), 'wood_table_worn_diff_2k.jpg', .32)
    paint = scope.finish('old green workshop paint', (.19, .31, .24), 'rusty_painted_metal_diff_2k.jpg', .22)
    steel = scope.finish('oxidized workshop steel', (.40, .43, .40), metal=.47, rough=.61)
    rubber = scope.finish('rubber and cork handle', (.082, .083, .067))
    for u in (-3.12, -1.75):
        for v in (-1.92, -1.34):
            box(bench, at, u, u+.089, v, v+.09, .044, .886, paint)
    for v in (-1.98, -1.72, -1.46):
        box(bench, at, -3.24, -1.59, v, v+.251, .854, .915, wood)
    for v in (-1.91, -1.26):
        box(bench, at, -3.12, -1.66, v, v+.06, .21, .29, steel)
    for i, u in enumerate((-2.94, -2.67, -2.34)):
        v = -1.69 + .043*i
        box(bench, at, u, u+.23, v, v+.028, .917, .944, steel)
        box(bench, at, u-.063, u+.09, v-.011, v+.039, .917, .961, rubber)
        box(bench, at, u+.21, u+.26, v-.022, v+.01, .917, .94, steel)
        box(bench, at, u+.21, u+.26, v+.03, v+.055, .917, .94, steel)
    box(bench, at, -1.98, -1.81, -1.68, -1.46, .913, 1.084, paint)
    box(bench, at, -2.013, -1.78, -1.70, -1.62, 1.061, 1.119, steel)
    box(bench, at, -2.013, -1.78, -1.51, -1.43, 1.059, 1.119, steel)
    court = plot['repair_court']
    scope.points['00'] = [court['street'], court['porch']]


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
