"""R16a authored corrections. Apply to R15 .blend or at the end of a rebuild.

Uses actual evaluated walking-surface meshes, not the analytical terrain alone.
No downloaded assets. Blender Z up, metres. Repeated application is a no-op.
"""
from pathlib import Path
import math, json, re, sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import props_library as props

ROOT = Path(__file__).resolve().parent

def apply(scene, report_path):
    if scene.get('r16_repairs_applied'):
        return json.loads(scene['r16_repair_report'])
    deps = bpy.context.evaluated_depsgraph_get()
    supports = []
    for ob in scene.objects:
        if ob.type != 'MESH' or not ob.name.startswith(('COL_Road_', 'COL_Walk_', 'Designed_Hillside_', 'COL_Terrain')):
            continue
        ev = ob.evaluated_get(deps)
        mesh = ev.to_mesh()
        vs = [ev.matrix_world @ v.co for v in mesh.vertices]
        faces = [tuple(p.vertices) for p in mesh.polygons]
        supports.append((ob.name, BVHTree.FromPolygons(vs, faces)))
        ev.to_mesh_clear()
    assert supports, 'No actual walkable surfaces; refusing guessed grounding'
    def ground(x,y,z):
        found=[]
        for name, tree in supports:
            hit,n,_,_ = tree.ray_cast(Vector((x,y,z+2.5)),Vector((0,0,-1)),6.)
            if hit is not None and abs(n.z)>.65:
                found.append((hit.z,name))
        if not found: raise RuntimeError('Missing ground at '+str((x,y,z)))
        return max(found)
    report={'revision':'R16a','ground_support_meshes':len(supports),'scooters':[],'clotheslines':[],'roof_seals':[],
            'open_defects':['residential_stairs_end_at_back_wall','rail_and_building_intersections','meter_box_detail']}
    groups={}
    for ob in scene.objects:
        m=re.match(r'CQF_Scooter_(\d+)_',ob.name)
        if m: groups.setdefault(m[1],[]).append(ob)
    for seed,objects in groups.items():
        ref=objects[0]; old=list(ref.location); yaw=ref.rotation_euler.z
        # Isolate each actual tyre's lower vertices; excludes grips and foot mat.
        tyres=[]
        for cy in [-.58,.66]:
            tyre=[v.co.copy() for ob in objects if ob.name.endswith(('_rubber','_rubber_worn')) for v in ob.data.vertices
                  if abs(v.co.y-cy)<.25 and abs(v.co.x)<.13 and v.co.z<.30]
            assert tyre
            tyres.append(tyre)
        pitch=0.; z=old[2]
        def gaps(pitch,z):
            matrix=Matrix.Translation(Vector((old[0],old[1],z))) @ Matrix.Rotation(yaw,4,'Z') @ Matrix.Rotation(pitch,4,'X')
            return [min((q.z-ground(q.x,q.y,old[2])[0]) for v in tyre for q in [matrix @ v]) for tyre in tyres]
        before=gaps(0.,z)
        for _ in range(7):
            rear,front=gaps(pitch,z)
            pitch-=math.atan2(front-rear,1.24)
            z-=(rear+front)/2-.002
        after=gaps(pitch,z)
        assert max(abs(v) for v in after)<.018, (seed,after)
        for ob in objects:
            ob.location.z=z; ob.rotation_euler=(pitch,0,yaw)
            ob['r16_grounded']=True
        report['scooters'].append({'seed':seed,'before_tyre_clearance_m':before,'after_tyre_clearance_m':after,'position': [old[0],old[1],z],'pitch_deg':math.degrees(pitch)})
    groups={}
    for ob in scene.objects:
        m=re.match(r'CQF_Clothesline_(-?\d+)_',ob.name)
        if m: groups.setdefault(m[1],[]).append(ob)
    for seed,objects in groups.items():
        ref=objects[0]; x,y,z=ref.location; yaw=ref.rotation_euler.z
        if seed=='-518': x,y,yaw=-70.3,-5.,math.pi/2 # outside the west lane travel corridor
        # Raise wire so every garment clears actual support by at least 1.20 m.
        rot=Matrix.Rotation(yaw,4,'Z')
        projected=[Vector((x,y,z))+rot@v.co for ob in objects for v in ob.data.vertices]
        lift=max(ground(q.x,q.y,z)[0]+1.2-q.z for q in projected)
        top=z+lift
        for ob in objects:
            ob.location=(x,y,top);ob.rotation_euler=(0,0,yaw)
        b=props.Batch('COL_R16_DryingRack_'+seed,(x,y,top),yaw,ref.users_collection[0])
        for local_x in [-1.9,1.9]:
            q=Vector((x,y,top))+rot@Vector((local_x,0,0))
            gz,_=ground(q.x,q.y,z)
            b.cylinder((local_x,0,gz-top-.06),(local_x,0,.08),.027,'black_metal',10)
            b.box((local_x,0,gz-top+.025),(.24,.24,.05),'stone')
            b.cylinder((local_x,-.16,-.06),(local_x,.16,-.06),.018,'steel',8)
        b.finish('authored_drying_rack')
        report['clotheslines'].append({'seed':seed,'wire_z':top,'minimum_cloth_clearance_m':1.2,'supported_ends':2,'relocated':seed=='-518'})
    # Close the wall-to-roof void along the actual footprint, including the ridge split.
    arch=json.loads((ROOT/'architecture_manifest.json').read_text(encoding='utf-8'))
    import district_geometry as geo
    for mat in bpy.data.materials:
        for prefix in ['CQ03_PBR_','CQ03_']:
            if mat.name.startswith(prefix): geo.MATS.setdefault(mat.name[len(prefix):],mat)
    collection=geo.col('R16_Repairs')
    for rec in arch['buildings']:
        style=rec['roof_form']
        if style not in ('gable','shed'): continue
        pts=rec['points']; base=rec['base_m']+rec['height_m']
        a,c=max(zip(pts,pts[1:]+pts[:1]),key=lambda e:math.dist(*e))
        u=Vector((c[0]-a[0],c[1]-a[1])).normalized();v=Vector((-u.y,u.x))
        ys=[(Vector(p)-Vector(a)).dot(v) for p in pts]
        front=min(ys)-.52;back=max(ys)+.52;ridge=(min(ys)+max(ys))/2
        rise=min(2.3,max(1.15,(max(ys)-min(ys))*.20))
        def roof(p):
            local_y=(Vector(p)-Vector(a)).dot(v)
            t=(local_y-front)/(back-front) if style=='shed' else ((local_y-front)/(ridge-front) if local_y<=ridge else (back-local_y)/(back-ridge))
            return base+.20+(rise-.20)*t-.025
        batch=geo.Batch('COL_R16_RoofSeal_'+str(rec['id']),collection)
        spans=0
        for p,q in zip(pts,pts[1:]+pts[:1]):
            direction=(Vector(q)-Vector(p)).normalized();normal=Vector((direction.y,-direction.x))
            count=max(1,math.ceil(math.dist(p,q)/.35))
            for i in range(count):
                start=Vector(p).lerp(Vector(q),i/count)-direction*.012
                end=Vector(p).lerp(Vector(q),(i+1)/count)+direction*.012
                corners=[start+normal*.014,end+normal*.014,end-normal*.16,start-normal*.16]
                verts=[(*r,base-.025) for r in corners]+[(*r,roof(r)) for r in corners]
                batch.mesh(verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],rec['wall_material'])
                spans+=1
        batch.finish()
        report['roof_seals'].append({'building':rec['id'],'closed_spans':spans,'status':'constructed; engine closeup required'})
    # Upgrade the actual repeated street service cabinets. Their eight-vertex
    # front panels preserve the exact authored wall anchor and local frame.
    utility=bpy.data.objects.get('District_surface_repairs_and_utilities_offwhite')
    report['meter_boxes']=[]
    if utility:
        vertices=[utility.matrix_world @ v.co for v in utility.data.vertices]
        assert len(vertices)%8==0, 'Unexpected cabinet topology; do not guess anchors'
        detail=geo.Batch('R16_MeterBox_Detail',collection)
        for index in range(0,len(vertices),8):
            vs=vertices[index:index+8]
            width=(vs[1]-vs[0]).length;thickness=(vs[3]-vs[0]).length;height=(vs[4]-vs[0]).length
            if abs(width-.46)>.002 or abs(height-.64)>.002 or abs(thickness-.025)>.002:continue
            center=sum(vs,Vector())/8
            tangent=(vs[1]-vs[0]).normalized();outward=(vs[3]-vs[0]).normalized()
            cabinet=geo.Batch('Meter_detail',collection,center,tuple(tangent)[:2],tuple(outward)[:2])
            # A framed gasket, metal door, glazed inspection window and latch.
            cabinet.box((0,.021,0),(.49,.018,.67),'dark')
            cabinet.box((0,.034,0),(.46,.014,.64),'painted_metal')
            cabinet.box((-.045,.046,.115),(.30,.014,.21),'aluminium')
            cabinet.box((-.045,.055,.115),(.27,.008,.18),'glass')
            cabinet.box((-.045,.061,.13),(.20,.006,.067),'offwhite')
            for digit in range(5):
                xx=-.12+digit*.037
                for zz in [.108,.13,.151]:cabinet.box((xx,.066,zz),(.022,.005,.004),'dark')
                for zz in [.119,.141]:
                    cabinet.box((xx-.011,.066,zz),(.004,.005,.021),'dark')
                    cabinet.box((xx+.011,.066,zz),(.004,.005,.021),'dark')
            for zz in [-.24,.24]:cabinet.box((-.229,.049,zz),(.028,.031,.065),'aluminium')
            cabinet.box((.18,.054,-.035),(.032,.034,.105),'aluminium')
            cabinet.cylinder((.18,.071,-.04),(.18,.079,-.04),.012,'dark',8)
            for xx in [-.203,.203]:
                for zz in [-.29,.29]:
                    cabinet.cylinder((xx,.043,zz),(xx,.05,zz),.008,'aluminium',8)
            for j in range(4):cabinet.box((-.04,.044,-.18-j*.025),(.23,.006,.008),'dark')
            cabinet.mesh([(-.05,.047,-.015),(.05,.047,-.015),(0,.047,.075)],[(0,1,2)],'paint_yellow')
            cabinet.box((0,.051,.03),(.008,.005,.035),'dark')
            cabinet.box((0,.051,.002),(.009,.005,.009),'dark')
            # Localized wear at the lower edge and a projecting drip hood.
            for j in range(7):cabinet.box((-.18+j*.058,.043,-.307),(.018+(j%3)*.012,.006,.007+(j%2)*.01),'rust')
            cabinet.mesh([(-.3,-.18,.415),(.3,-.18,.415),(.3,.12,.375),(-.3,.12,.375)],[(0,1,2,3),(3,2,1,0)],'painted_metal')
            cabinet.box((0,.12,.363),(.60,.018,.025),'rust')
            for key,(verts,faces,smooth) in cabinet.data.items():detail.mesh(verts,faces,key)
            report['meter_boxes'].append({'index':index//8,'panel_center':list(center),'width_m':width,'height_m':height})
        for ob in detail.finish(.002):
            tri=ob.modifiers.new('R16_Final_triangulation','TRIANGULATE')
            tri.keep_custom_normals=True
    assert report['meter_boxes'], 'Street cabinet anchors were not found'
    report['open_defects'].remove('meter_box_detail')
    scene['revision']=16
    scene['r16_repairs_applied']=True
    scene['r16_repair_report']=json.dumps(report)
    Path(report_path).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    import sys
    dest=Path(sys.argv[sys.argv.index('--')+1]);dest.mkdir(parents=True,exist_ok=True)
    result=apply(bpy.context.scene,dest/'geometry_repairs.json')
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(dest/'chongqing_district.blend'),compress=True)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH' and not ob.hide_render: ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(dest/'chongqing_district.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True,export_tangents=True,export_vertex_color='ACTIVE',export_all_vertex_colors=False)
    print('R16_REPAIR_COMPLETE',json.dumps({k:len(v) for k,v in result.items() if isinstance(v,list)}),flush=True)
