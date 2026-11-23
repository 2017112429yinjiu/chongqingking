"""Fit exposed edges of the street-entry stairs and the upper road to terrain."""
from collections import defaultdict
import math
from mathutils import Vector


def build(source, ground, surface, material):
    records = []
    selected = {
        'COL_Walk_OSM_734116594_0_step_concrete': 'Entry_stair',
        'COL_Road_734116597_0_asphalt': 'Upper_road',
    }
    for obj in source:
        if obj.name not in selected:
            continue
        label = selected[obj.name]
        boundary = defaultdict(list)
        for face in obj.data.polygons:
            if face.normal.z < .60:
                continue
            poly = [obj.matrix_world @ obj.data.vertices[i].co for i in face.vertices]
            for a, b in zip(poly, poly[1:] + poly[:1]):
                key = tuple(sorted((tuple(round(v, 3) for v in a.xy), tuple(round(v, 3) for v in b.xy))))
                boundary[key].append((a, b))
        mesh = surface('COL_R21_Footing_' + label, [material])
        samples = []
        for edge in boundary.values():
            if len(edge) != 1:
                continue
            a, b = edge[0]
            # Keep the masonry under the lip, inside the original route footprint.
            tangent = b - a
            if tangent.xy.length < .02:
                continue
            inward = Vector((-tangent.y, tangent.x, 0)).normalized()
            inset = .047 if label == 'Entry_stair' else .063
            a, b = a + inward * inset, b + inward * inset
            length = (b - a).length
            n = max(1, math.ceil(length / .68))
            for i in range(n):
                p, q = a.lerp(b, i / n), a.lerp(b, (i + 1) / n)
                gp, gq = ground(p.x, p.y), ground(q.x, q.y)
                # Limit work to the two camera-facing runs inside the playable
                # district. Keep open crossings and elevated structures clear.
                mid = (p + q) / 2
                if label == 'Upper_road' and not (-50 < mid.x < 2 and 70 < mid.y < 99):
                    continue
                if max(p.z - gp, q.z - gq) < .086 or max(p.z - gp, q.z - gq) > 1.55:
                    continue
                lo_p = Vector((p.x, p.y, min(p.z - .08, gp - .067)))
                lo_q = Vector((q.x, q.y, min(q.z - .08, gq - .067)))
                hi_p, hi_q = p - Vector((0, 0, .028)), q - Vector((0, 0, .028))
                coord_p, coord_q = p.dot(tangent.normalized())/2.65, q.dot(tangent.normalized())/2.65
                mesh.quad([lo_p,lo_q,hi_q,hi_p],
                          [(coord_p,lo_p.z/2.65),(coord_q,lo_q.z/2.65),(coord_q,hi_q.z/2.65),(coord_p,hi_p.z/2.65)])
                samples.append({'midpoint': list(mid), 'height': round(mid.z-(gp+gq)*.5, 3),
                                'outward': [-inward.x, -inward.y]})
        if samples:
            mesh.finish()
            records.append({'source':obj.name,'name':mesh.name,'segments':len(samples),
                            'height_range_m':[min(x['height'] for x in samples), max(x['height'] for x in samples)],
                            'sample':max(samples,key=lambda item:item['height'])})
    return records
