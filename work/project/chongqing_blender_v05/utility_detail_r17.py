"""Commercially original meter cabinet geometry; no new external artwork."""
import bpy,json,random
from mathutils import Vector
import district_geometry as geo

def apply(scene):
    if scene.get('r17_meters'):return json.loads(scene['r17_meters'])
    for mat in bpy.data.materials:
        for prefix in ['CQ03_PBR_','CQ03_']:
            if mat.name.startswith(prefix):geo.MATS.setdefault(mat.name[len(prefix):],mat)
    geo.setup(geo.MATS)
    for i,color in enumerate([(.22,.27,.25),(.30,.32,.33),(.27,.31,.35)]):geo.solid('meter_enamel_'+str(i),color,.72,.12)
    geo.solid('meter_display',(.48,.54,.43),.6)
    geo.solid('meter_oxide',(.105,.042,.019),.97)
    for ob in list(scene.objects):
        if ob.name.startswith('R16_MeterBox_Detail'):bpy.data.objects.remove(ob,do_unlink=True)
    coll=geo.col('R17_Utility_closeups');batch=geo.Batch('R17_Meter_Details',coll)
    panel=bpy.data.objects['District_surface_repairs_and_utilities_offwhite']
    vertices=[panel.matrix_world@v.co for v in panel.data.vertices]
    digits={0:'abcedf',1:'bc',2:'abged',3:'abgcd',4:'fgbc',5:'afgcd',6:'afgecd',7:'abc',8:'abcdefg',9:'abfgcd'}
    records=[]
    for index in range(0,len(vertices),8):
        vs=vertices[index:index+8]
        if abs((vs[1]-vs[0]).length-.46)>.002 or abs((vs[4]-vs[0]).length-.64)>.002:continue
        center=sum(vs,Vector())/8;t=(vs[1]-vs[0]).normalized();out=(vs[3]-vs[0]).normalized()
        rng=random.Random(17000+index);finish='meter_enamel_'+str(rng.randrange(3))
        b=geo.Batch('Meter',coll,center,tuple(t)[:2],tuple(out)[:2])
        b.box((0,.021,0),(.49,.018,.67),'dark')
        b.box((0,.034,0),(.462,.014,.646),finish)
        b.box((-.04,.044,.12),(.31,.018,.205),'aluminium')
        b.box((-.04,.055,.12),(.278,.008,.174),'dark')
        b.box((-.04,.061,.135),(.226,.005,.072),'meter_display')
        value=1031+(index//8*379)%85000
        for i,char in enumerate(str(value).zfill(5)):
            x=-.12+i*.039;z=.135
            for code,dz in [('a',.023),('g',0),('d',-.023)]:
                if code in digits[int(char)]:b.box((x,.066,z+dz),(.022,.003,.003),'dark')
            for code,dx,dz in [('f',-.011,.012),('b',.011,.012),('e',-.011,-.012),('c',.011,-.012)]:
                if code in digits[int(char)]:b.box((x+dx,.066,z+dz),(.003,.003,.020),'dark')
        b.box((-.04,.062,.083),(.21,.004,.018),'offwhite')
        for i in range(13):b.box((-.13+i*.014,.065,.082),(.002+.001*(i%2),.002,.012),'dark')
        for z in [-.24,.24]:
            b.box((-.23,.049,z),(.027,.024,.067),'aluminium')
            b.cylinder((-.228,.065,z-.035),(-.228,.065,z+.035),.009,'aluminium',10)
        b.box((.18,.054,-.035),(.03,.025,.10),'aluminium')
        b.cylinder((.18,.069,-.04),(.18,.078,-.04),.009,'dark',10)
        for x in [-.203,.203]:
            for z in [-.29,.29]:
                b.cylinder((x,.044,z),(x,.051,z),.0065,'aluminium',10)
                b.box((x,.052,z),(.008,.002,.0015),'dark')
        for j in range(5):b.box((-.04,.044,-.16-j*.026),(.23,.006,.0055),'dark')
        b.mesh([(-.035,.048,-.017),(.035,.048,-.017),(0,.048,.047)],[(0,1,2)],'paint_yellow')
        b.box((0,.052,.017),(.006,.003,.023),'dark')
        b.box((0,.052,-.004),(.006,.003,.006),'dark')
        # Vary sparse chips along moisture-trapping lower seams, not uniform stripes.
        for j in range(rng.randint(3,8)):
            x=rng.uniform(-.21,.21);z=-.312+rng.uniform(0,.018)
            b.box((x,.043,z),(rng.uniform(.004,.023),.003,rng.uniform(.002,.009)),'meter_oxide')
        b.mesh([(-.29,.015,.345),(.29,.015,.345),(.29,.15,.323),(-.29,.15,.323)],[(0,1,2,3)],finish)
        b.box((0,.148,.317),(.58,.009,.018),finish)
        for key,(verts,faces,smooth) in b.data.items():batch.mesh(verts,faces,key)
        # Small readable rating; merge the font geometry into the common material batch.
        label=geo.label_local('220V  5(60)A',b,(-.04,.044,-.07),size=.024,mat='offwhite',bold=False)
        batch.mesh([label.matrix_world@v.co for v in label.data.vertices],[list(p.vertices) for p in label.data.polygons],'offwhite')
        bpy.data.objects.remove(label,do_unlink=True)
        records.append({'panel':index//8,'reading':value,'finish':finish})
    for ob in batch.finish(.001):
        tri=ob.modifiers.new('Final triangulation','TRIANGULATE');tri.keep_custom_normals=True
    result={'count':len(records),'unique_readings':len({r['reading'] for r in records}),'records':records}
    scene['r17_meters']=json.dumps(result)
    return result
