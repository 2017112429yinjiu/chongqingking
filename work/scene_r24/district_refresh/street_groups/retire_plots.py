"""Select precisely the old plot geometry in the existing editable district."""
from collections import Counter
from hashlib import sha256
import struct

import bmesh
import bpy

STATIC_FIXTURE = "COLH_Outer500_Household_contact"
RETAINING = "COL_Outer500_Retaining_and_boundaries"


def fingerprint(obj, polygon):
    vertices = sorted(tuple(obj.data.vertices[index].co) for index in polygon.vertices)
    return sha256(b"".join(struct.pack("<fff", *v) for v in vertices)).hexdigest()[:24]


def remove_faces(obj, indices):
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    mesh.faces.ensure_lookup_table()
    bmesh.ops.delete(mesh, geom=[mesh.faces[i] for i in indices], context="FACES")
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()


def replace_shared_geometry(ownership, ids, layout, prior_terrain):
    grouped = {}
    for pid in ids:
        for name, pieces in ownership[str(pid)].items():
            grouped.setdefault(name, []).extend(pieces)

    original = {name: bpy.data.objects[name] for name in grouped}
    with bpy.data.libraries.load(str(prior_terrain), link=False) as (_, local):
        local.objects = [RETAINING]
    retaining = local.objects[0]
    bpy.context.scene.collection.objects.link(retaining)
    bpy.data.objects.remove(original[RETAINING], do_unlink=True)
    retaining.name = RETAINING
    original[RETAINING] = retaining

    for name, pieces in grouped.items():
        obj = original[name]
        polygons = obj.data.polygons
        if name == RETAINING:
            # The previous fit of the 37 stairs changed face order in this mesh.
            # Match its current vertices to the original per-plot fingerprints.
            wanted = Counter(face for piece in pieces for face in piece["faces"])
            found = Counter()
            indices = []
            for poly in polygons:
                identity = fingerprint(obj, poly)
                if identity in wanted:
                    found[identity] += 1
                    indices.append(poly.index)
            if wanted != found:
                raise ValueError(f"Retaining faces differ from the verified plot ownership: {wanted-found}, {found-wanted}")
        else:
            indices = []
            for piece in pieces:
                start = piece["start"]
                for i, identity in enumerate(piece["faces"], start):
                    if fingerprint(obj, polygons[i]) != identity:
                        raise ValueError(f"Unverified face at {name} polygon {i}")
                    indices.append(i)
        remove_faces(obj, indices)
        print("CQ_PLOT_RETIRED_FACES", name, len(indices))

    household = [i for i,item in enumerate(layout["household"]) if item["plot"] in ids]
    contact = bpy.data.objects[STATIC_FIXTURE]
    assert len(contact.data.polygons) == 6*len(layout["household"])
    indices = [face for row in household for face in range(6*row, 6*row+6)]
    remove_faces(contact, indices)
    original[STATIC_FIXTURE] = contact
    print("CQ_PLOT_RETIRED_FACES", STATIC_FIXTURE, len(indices))

    prefixes = tuple(f"Outer500_Household_{i:03d}_" for i in household)
    prefixes += tuple(f"Outer500_Condenser_{pid:02d}_" for pid in ids)
    exact = {f"{prefix}_{pid:02d}" for pid in ids for prefix in (
        "COL_Outer500_Frame", "Outer500_Joinery", "Outer500_InteriorFloor",
        "COL_Outer500_Court", "Outer500_CourtDetails")}
    removed = sorted(obj.name for obj in bpy.context.scene.objects
                     if obj.name in exact or obj.name.startswith(prefixes))
    return list(original.values()), removed
