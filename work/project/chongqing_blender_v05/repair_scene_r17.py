"""Replace intersecting public paths and fake residential stairs.

Works on the verified R16 scene. Full generation calls the same apply pass.
Plan clearance is checked before mutation. Engine traversal is a separate gate.
"""
from pathlib import Path
import sys,math,json,ast
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import bpy,bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
import district_geometry as geo
import district_layout as dl
from circulation_r17 import ROUTES,domestic_entry

def triangulate_routes(scene):
    for ob in scene.objects:
        if ob.type=='MESH' and any(ob.name.startswith(prefix+name+'_') for name,_,_,_ in ROUTES for prefix in ['COL_Walk_','Walk_details_','COL_Handrails_']):
            if not ob.modifiers.get('R17_Final_triangulation'):
                tri=ob.modifiers.new('R17_Final_triangulation','TRIANGULATE');tri.keep_custom_normals=True

def _apply_circulation(scene,report_path):
    if scene.get('r17_repairs_applied'):return json.loads(scene['r17_repair_report'])
    arch=json.loads((ROOT/'architecture_manifest.json').read_text(encoding='utf-8'))
    for mat in bpy.data.materials:
        for prefix in ['CQ03_PBR_','CQ03_']:
            if mat.name.startswith(prefix):geo.MATS.setdefault(mat.name[len(prefix):],mat)
    for key in ['pavement','step_concrete','stone','timber','painted_metal','wood']:
        assert key in geo.MATS,key
    report={'revision':17,'routes':[],'entrances':[],'removed_fake_stair_blocks':0,'rail_spans_skipped':0,'prop_adjustments':[]}
    buildings=arch['buildings']
    def in_building(p,margin=.06):
        for r in buildings:
            poly=r['points']
            if not(min(q[0] for q in poly)-margin<=p[0]<=max(q[0] for q in poly)+margin and min(q[1] for q in poly)-margin<=p[1]<=max(q[1] for q in poly)+margin):continue
            if dl.point_in_poly(p,poly) or min(dl.distance_segment(p,a,b)[0] for a,b in zip(poly,poly[1:]+poly[:1]))<margin:return str(r['id'])
        return None
    # Check every 0.1 m along the full public walking envelope, not just its centre.
    for name,points,width,stepped in ROUTES:
        contacts=[]
        for a,b in zip(points,points[1:]):
            count=max(1,math.ceil(math.dist(a,b)/.1))
            for i in range(count+1):
                p=tuple(a[k]+(b[k]-a[k])*i/count for k in [0,1])
                hit=in_building(p,width/2+.06)
                if hit:contacts.append({'building':hit,'point':p})
        assert not contacts,(name,contacts[:3])
        report['routes'].append({'name':name,'points':points,'width_m':width,'plan_clearance_m':.06,'sample_spacing_m':.1,'intersections':contacts})
    for ob in list(scene.objects):
        if any(ob.name.startswith(prefix+name+'_') for name,_,_,_ in ROUTES for prefix in ['COL_Walk_','Walk_details_','COL_Handrails_']):
            bpy.data.objects.remove(ob,do_unlink=True)
    # Reuse the original geometry implementation without executing its scene reset.
    tree=ast.parse((ROOT/'build_district.py').read_text(encoding='utf-8'))
    helpers={'prism','densify','strip','rail','build_walk'}
    functions=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in helpers],type_ignores=[])
    roadcol=geo.col('02_Roads_stairs_and_courts')
    env={'math':math,'Vector':Vector,'tessellate_polygon':tessellate_polygon,'Batch':geo.Batch,'roadcol':roadcol,'REVISION':17,'ground_height':dl.ground_height,'route_records':[]}
    exec(compile(functions,str(ROOT/'build_district.py'),'exec'),env)
    original_rail=env['rail']
    entries=[en for rec in buildings for en in rec.get('entrances',[])]
    def protected_door(p):
        for en in entries:
            origin=Vector(en['position'][:2]);out=(Vector(en['approach'][:2])-origin).normalized();side=Vector((-out.y,out.x));d=Vector(p)-origin
            if -.35<d.dot(out)<3.6 and abs(d.dot(side))<en['width_m']/2+.35:return True
        return False
    def clipped_rail(batch,pts,offset,zfun,height=.96):
        # Split in world XY; restore supported terminal posts on each retained run.
        samples=env['densify'](pts,.20)
        run=[]
        for a,b in zip(samples,samples[1:]):
            direction=(Vector(b)-Vector(a)).normalized();normal=Vector((-direction.y,direction.x))
            pa=Vector(a)+normal*offset;pb=Vector(b)+normal*offset
            good=all(not in_building(p,.07) and not protected_door(p) for p in [pa,(pa+pb)/2,pb])
            if good:
                if not run:run=[tuple(pa)]
                run.append(tuple(pb))
            else:
                report['rail_spans_skipped']+=1
                if len(run)>1:original_rail(batch,run,0,zfun,height)
                run=[]
        if len(run)>1:original_rail(batch,run,0,zfun,height)
    env['rail']=clipped_rail
    for name,points,width,stepped in ROUTES:env['build_walk'](points,width,name,stepped,False)
    # Keep the scan tree/well intact: route around its full trunk and soil ring.
    tree=(48.93,-4.84)
    distance=min(dl.distance_segment(tree,a,b)[0]-width/2 for name,pts,width,_ in ROUTES for a,b in zip(pts,pts[1:]))
    assert distance>1.5,('tree_25_well_clearance',distance)
    report['tree_25_well_edge_clearance_m']=distance-1.5
    # Reposition whole bin material groups together; support each scanned item
    # by its lowest evaluated geometry, rather than preserving its former Z.
    for prefix,delta in [('Resident_waste_1_bin_',(-2.2,1.2)),('Resident_waste_1_bagA_',(-2.2,1.2)),('Resident_waste_1_bagB_',(-2.2,1.2)),('Resident_waste_1_crate_',(-2.2,1.2)),('CQF_StreetLamp_',None)]:
        objects=[o for o in scene.objects if o.type=='MESH' and o.name.startswith(prefix) and (delta is not None or o.name.endswith('.009'))]
        if not objects:continue
        if delta is None:delta=(-2.5,.3)
        before=list(objects[0].location)
        for o in objects:o.location.x+=delta[0];o.location.y+=delta[1]
        bottom=min((o.matrix_world@v.co).z for o in objects for v in o.data.vertices)
        bpy.context.view_layer.update()
        verts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
        bottom=min(v.z for v in verts)
        offset=max(dl.ground_height(v.x,v.y)-v.z for v in verts if v.z<bottom+.08)+.012
        for o in objects:o.location.z+=offset
        report['prop_adjustments'].append({'group':prefix,'objects':[o.name for o in objects],'before':before,'after':list(objects[0].location),'minimum_clearance_m':.012})
    # Identify the exact original 5 cuboids by geometry. Never delete by broad AABB.
    collection=geo.col('R17_Residential_entries')
    for rec in buildings:
        for entry_index,en in enumerate(rec.get('entrances',[])):
            if en['type']=='shop':continue
            out=(Vector(en['approach'][:2])-Vector(en['position'][:2])).normalized()
            tangent=Vector((-out.y,out.x))
            origin=Vector((en['position'][0]-.1*out.x,en['position'][1]-.1*out.y,rec['base_m']))
            width=en['width_m'];removed=[]
            expected=[origin+Vector((out.x*(-1.45-k*.19),out.y*(-1.45-k*.19),.05+.065*(k+1))) for k in range(5)]
            for ob in list(scene.objects):
                if ob.type!='MESH' or not ob.name.startswith('COL_B_'+str(rec['id'])+'_') or not ob.name.endswith('_pavement'):continue
                bm=bmesh.new();bm.from_mesh(ob.data);seen=set();delete=[]
                for vertex in bm.verts:
                    if vertex in seen:continue
                    component=[];stack=[vertex];seen.add(vertex)
                    while stack:
                        v=stack.pop();component.append(v)
                        for edge in v.link_edges:
                            other=edge.other_vert(v)
                            if other not in seen:seen.add(other);stack.append(other)
                    if len(component)!=8:continue
                    centre=sum((ob.matrix_world@v.co for v in component),Vector())/8
                    for k,target in enumerate(expected):
                        if (centre-target).length<.002:
                            delete.extend(component);removed.append(k);break
                if delete:
                    bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(ob.data);ob.data.update()
                bm.free()
            assert sorted(removed)==list(range(5)),(rec['id'],entry_index,removed)
            report['removed_fake_stair_blocks']+=len(removed)
            batch=geo.Batch('R17_Entry_'+str(rec['id'])+'_'+str(entry_index),collection,origin,tuple(tangent),tuple(out))
            domestic_entry(batch,batch,width)
            for ob in batch.finish(.004):
                tri=ob.modifiers.new('R17_Final_triangulation','TRIANGULATE');tri.keep_custom_normals=True
            report['entrances'].append({'building':str(rec['id']),'index':entry_index,'origin':list(origin),'outward':list(out),'width_m':width,'floor_top_m':rec['base_m']+.09,'ceiling_m':rec['base_m']+2.8,'clear_height_m':2.71,'type':'private_vestibule_closed_residential_door','approach':en['approach'],'removed_steps':len(removed)})
    triangulate_routes(scene)
    scene['revision']=17
    scene['r17_repairs_applied']=True
    scene['r17_repair_report']=json.dumps(report)
    Path(report_path).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

def apply(scene,report_path):
    result=_apply_circulation(scene,report_path)
    from utility_detail_r17 import apply as meter_pass
    result['meter_boxes']=meter_pass(scene)
    scene['r17_repair_report']=json.dumps(result)
    Path(report_path).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    dest=Path(sys.argv[sys.argv.index('--')+1]);dest.mkdir(parents=True,exist_ok=True)
    result=apply(bpy.context.scene,dest/'geometry_repairs_r17.json')
    triangulate_routes(bpy.context.scene)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(dest/'chongqing_district.blend'),compress=True)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH' and not ob.hide_render:ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(dest/'chongqing_district.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True,export_tangents=True,export_vertex_color='ACTIVE',export_all_vertex_colors=False)
    print('R17_REPAIR_COMPLETE',json.dumps({'routes':len(result['routes']),'entries':len(result['entrances']),'steps_removed':result['removed_fake_stair_blocks']}),flush=True)
