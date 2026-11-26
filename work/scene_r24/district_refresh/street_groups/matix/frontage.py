"""Ground the short dressed verges on the existing street crossfalls."""
from mathutils import Vector

from factory import Mesh, material, terrain


def build_verges(ways):
    relief = terrain()
    stone = material('Matix grey dressed curb stone', (.76, .76, .72), 'concrete_floor_worn_001_diff_2k.jpg')
    seam = material('Matix channel setts', (.52, .55, .54), 'stone_wall_05_diff_2k.jpg')
    mesh = Mesh('COL_Matix_StreetEdges')

    def position(point, up):
        contact, _, _, _ = relief.ray_cast(Vector((point.x, point.y, 105.0)), Vector((0, 0, -1)), 150)
        assert contact is not None
        return (point.x, point.y, contact.z + up)

    records = []
    sections = [('59146654', 6, 1.56, .45, 14.6), ('59146654', 18, 1.56, .33, 6.2),
                ('1025797976', 3, -1.255, 20.0, 49.0)]
    for way, start, offset, lo, hi in sections:
        line = ways[way]['east_north']
        a, b = Vector(line[start]), Vector(line[start + 1])
        tangent = (b - a).normalized()
        normal = Vector((-tangent.y, tangent.x)) * (1 if offset > 0 else -1)
        assert hi < (b - a).length
        base = a + normal * (abs(offset) + .036)
        length = lo
        joints = [.69, .86, .76, .92]
        index = 0
        while length < hi - .12:
            end = min(length + joints[index % len(joints)], hi)
            p, q = base + tangent * length, base + tangent * end
            slab = [p, q, q + .19 * normal, p + .19 * normal]
            trim = [p - .25 * normal, q - .25 * normal, q, p]
            if offset < 0:
                slab.reverse()
                trim.reverse()
            mesh.solid([position(v, -.045) for v in slab], [position(v, .123) for v in slab], stone)
            mesh.face([position(v, .034) for v in trim], seam)
            length = end + .012
            index += 1
        records.append({'way': way, 'segment': start, 'length_m': round(hi - lo, 3), 'blocks': index})
    return mesh.save(), records
