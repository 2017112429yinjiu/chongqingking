"""Transfer a separately simulated hanging bib while preserving the adopted skirt.
Neck-corner and waist supports, 150 Blender cloth frames, static rest blend only.
"""
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

def apply(root,out):
    source=root/'characters/cloth_bib_trial/drape_result.json'
    data=json.loads(source.read_text());initial=[Vector(p) for p in data['initial']];final=[Vector(p) for p in data['final']]
    apron=bpy.data.objects['CQ_SoftApron']
    assert len(apron.data.vertices)==len(initial)==4331
    error=max((v.co-initial[v.index]).length for v in apron.data.vertices)
    assert error<.0002,('Bib trial input no longer matches the cut garment',error)
    apron.data.calc_loop_triangles();triangles=[tuple(t.vertices) for t in apron.data.loop_triangles]
    surface=BVHTree.FromPolygons(initial,triangles,all_triangles=True)
    counts={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH' or not ob.name.startswith('CQ_'):continue
        count=0
        for vertex in ob.data.vertices:
            point=vertex.co.copy()
            if not .91<point.z<1.265 or point.y>-.025:continue
            nearest,normal,index,distance=surface.find_nearest(point)
            if index is None or distance>.035:continue
            a,b,c=triangles[index]
            delta=barycentric_transform(nearest,initial[a],initial[b],initial[c],final[a]-initial[a],final[b]-initial[b],final[c]-initial[c])
            weight=min(1,max(0,(point.z-.91)/.025))*min(1,max(0,(1.265-point.z)/.025))
            weight=weight*weight*(3-2*weight)
            vertex.co+=delta*weight;count+=1
        if count:counts[ob.name]=count
    report={'source_sha256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),'method':'Upper bib only, offline Blender gravity/collision 150 frames at 30 Hz; neck-corner and waist seam supports. Rest deltas transferred to adjacent trim and stitches. Lower skirt unchanged; not live cloth.','topology_match_error_m':error,'modified_vertices':counts}
    (out/'bib_drape_bake.json').write_text(json.dumps(report,indent=2));print('BIB_DRAPE_BAKED',report,flush=True)
