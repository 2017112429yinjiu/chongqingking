from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'characters/shopkeeper_r18/shopkeeper_authoring.blend'))
rig=bpy.data.objects['ShopkeeperRig'];shirt=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'casualsuit' in o.name)
apron=bpy.data.objects['CQ_SoftApron'];results=[]
for clip,frames in [('idle',[1,60,150,210,270,301]),('serve',[30,50,75])]:
    rig.animation_data.action=bpy.data.actions[clip]
    for frame in frames:
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        ob=shirt.evaluated_get(deps);mesh=ob.to_mesh()
        names={g.index:g.name for g in shirt.vertex_groups}
        # A reaching sleeve in front of the bib is not a cloth intersection.
        torso=[]
        for poly in mesh.polygons:
            blocked=False
            for i in poly.vertices:
                groups=mesh.vertices[i].groups
                if groups:
                    name=names[max(groups,key=lambda g:g.weight).group]
                    if any(s in name for s in ['arm','hand','index','middle','ring','pinky','thumb']):blocked=True;break
            if not blocked:torso.append(list(poly.vertices))
        bvh=BVHTree.FromPolygons([ob.matrix_world@v.co for v in mesh.vertices],torso);ob.to_mesh_clear()
        ob=apron.evaluated_get(deps);mesh=ob.to_mesh();clearances=[];bad=[];skirt=[];skirt_bad=[]
        for v in mesh.vertices:
            p=ob.matrix_world@v.co
            bib=abs(p.x)<.17 and .91<=p.z<=1.23
            lower=abs(p.x)<.23 and .50<=p.z<.91
            if not (bib or lower):continue
            hit=bvh.ray_cast(Vector((p.x,-1,p.z)),Vector((0,1,0)),2)[0]
            if hit:
                gap=hit.y-p.y
                if bib:
                    clearances.append(gap)
                    if gap<-.004:bad.append([*p,gap])
                if lower:
                    skirt.append(gap)
                    if gap<-.004:skirt_bad.append([*p,gap])
        ob.to_mesh_clear()
        results.append({'clip':clip,'frame':frame,'tested':len(clearances),'min_front_clearance_m':min(clearances),'vertices_inside_shirt_over_4mm':len(bad),'examples':bad[:6],'skirt_tested':len(skirt),'skirt_min_clearance_m':min(skirt) if skirt else None,'skirt_vertices_inside_over_4mm':len(skirt_bad),'skirt_examples':skirt_bad[:6]})
report={'actions_saved':[a.name for a in bpy.data.actions],'bone_count':len(rig.pose.bones),'scope':'Front bib |x|<.17 z .91..1.23 and front skirt |x|<.23 z .50...91, evaluated torso/pants triangles, arm-dominant triangles excluded; ray checks only, not complete cloth self-collision certification','samples':results}
(root/'audit/r18_cloth_fit.json').write_text(json.dumps(report,indent=2))
print('CLOTH_FIT',json.dumps(report),flush=True)
