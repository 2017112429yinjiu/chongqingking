"""Transfer an offline gravity drape to the loose apron skirt and sewn trim.
The upper bib stays tailored. No live physics is exported or advertised.
"""
import json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
import bpy

def apply(root,out):
    source=root/'characters/cloth_trial/drape_result.json'
    data=json.loads(source.read_text());initial=[Vector(p) for p in data['initial']];final=[Vector(p) for p in data['final']]
    apron=bpy.data.objects['CQ_SoftApron']
    assert len(apron.data.vertices)==len(initial)==4331,'Drape topology has changed; rerun isolated physics trial.'
    maximum=max((v.co-initial[v.index]).length for v in apron.data.vertices if v.co.z<.90)
    assert maximum<.0002,('Rest fit changed; do not apply incompatible cloth deltas',maximum)
    apron.data.calc_loop_triangles();triangles=[tuple(t.vertices) for t in apron.data.loop_triangles]
    surface=BVHTree.FromPolygons(initial,triangles,all_triangles=True)
    changes={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH' or not ob.name.startswith('CQ_'):continue
        count=0
        for vertex in ob.data.vertices:
            point=vertex.co.copy()
            if point.z>=.91 or point.y>-.025:continue
            nearest,normal,index,distance=surface.find_nearest(point)
            if index is None or distance>.045:continue
            a,b,c=triangles[index]
            delta=barycentric_transform(nearest,initial[a],initial[b],initial[c],final[a]-initial[a],final[b]-initial[b],final[c]-initial[c])
            weight=min(1,max(0,(.91-point.z)/.025));weight=weight*weight*(3-2*weight)
            # Full gravity settling exaggerated the regularly seeded folds.
            # Blend with the cut panel to keep a work apron, not a pleated skirt.
            vertex.co+=delta*weight*.50;count+=1
        if count:changes[ob.name]=count
    report={'source_sha256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),'method':'Offline Blender cloth gravity/collision 120 frames at 30 Hz; lower skirt deltas transferred barycentrically to pocket and edge bindings at 50% blend; upper bib kept tailored. Runtime remains skinned secondary bones.','blend':.50,'topology_match_error_m':maximum,'modified_vertices':changes}
    (out/'drape_bake.json').write_text(json.dumps(report,indent=2));print('LOWER_APRON_DRAPE_BAKED',report,flush=True)
