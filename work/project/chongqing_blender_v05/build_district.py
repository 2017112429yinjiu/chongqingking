"""Full 200 x 200 metre Chongqing art district. Run with Blender in background.
Planar source footprints/roads: OSM; terrain and architectural details: authored.
The real photographs are visual references only, never used as copied textures.
"""
from pathlib import Path
from collections import defaultdict
from types import SimpleNamespace
import sys,math,json,random,time,shutil,os
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from district_layout import *
import district_geometry as geo
from material_library import build_materials
import props_library as props
import urban_fabric
import scanned_assets as scanned

REVISION=int(os.environ.get('CQ_REVISION','17'))
OUT=Path(os.environ.get('CQ_OUTPUT_DIR',str(ROOT/'outputs')));OUT.mkdir(parents=True,exist_ok=True)
STAGE_ONLY=os.environ.get('CQ_STAGE_ONLY','0')=='1'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
for stale_key in ('r16_repairs_applied','r16_repair_report','r17_repairs_applied','r17_repair_report','r17_meters'):
    if stale_key in scene:del scene[stale_key]
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.
scene['title']='梯坎里 · 重庆街区 05'
scene['revision']=REVISION
scene['source_note']='200m OSM XY; authored elevations, heights, facades, supplementary paths and infill. No claim of measured 1:1 reconstruction.'
MATS=build_materials();geo.setup(MATS)
palette={
 'frame':((.065,.075,.071),.66,.25),'aluminium':((.30,.33,.32),.58,.30),
 'painted_metal':((.14,.19,.17),.73,.25),'rust':((.22,.095,.045),.91,.15),
 'dark':((.016,.021,.022),.94,0),'glass':((.055,.085,.091),.40,.08),
 'glass_blue':((.075,.12,.14),.40,.08),'glass_warm':((.22,.17,.10),.42,.06),
 'curtain':((.37,.35,.30),.96,0),'offwhite':((.58,.60,.55),.82,.02),
 'faded_red':((.28,.053,.038),.78,.08),'faded_green':((.065,.15,.12),.82,.12),
 'sign_cream':((.85,.76,.56),.74,0),'paint_yellow':((.68,.43,.10),.87,0),
 'electric_blue':((.055,.12,.18),.75,.12),'wood':((.17,.09,.045),.93,0),
 'water':((.045,.061,.066),.13,.25),'paper':((.61,.57,.45),.97,0),
 'line_white':((.66,.67,.61),.89,0),'court_green':((.12,.20,.18),.94,0),
 'court_red':((.26,.12,.087),.96,0),'leaf_olive':((.10,.17,.055),.94,0),
 'soil_dark':((.075,.063,.038),1.,0),'black_rubber':((.024,.027,.025),.96,0),
 'ceramic_glaze':((.63,.63,.54),.28,0),'room_wall':((.45,.43,.37),.93,0)
}
for key,(c,r,m) in palette.items():
    if key not in MATS:geo.solid(key,c,r,m)
geo.solid('light_warm',(1.,.68,.33),.5,0,1.8)
geo.solid('hill_near',(.10,.15,.13),1.,0.)
geo.solid('hill_far',(.16,.20,.21),1.,0.)
if REVISION>=6:
    # Normal/roughness retain the measured cloth weave. Individual households
    # use restrained plain cloth colours instead of repeating one red print.
    for key,rgb in [('curtain_linen',(.38,.36,.31)),('curtain_beige',(.50,.46,.36)),('curtain_sage',(.20,.27,.23))]:
        mat=MATS['curtain'].copy();mat.name='CQ04_Cloth_'+key
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs is None:bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        for link in list(bs.inputs['Base Color'].links):mat.node_tree.links.remove(link)
        bs.inputs['Base Color'].default_value=(*rgb,1.)
        mat.diffuse_color=(*rgb,1.)
        mat['origin']='Authored plain cloth colour with original Poly Haven fabric_pattern_07 weave normal and roughness maps'
        MATS[key]=mat
if REVISION>=5:scanned.setup(ROOT)
geo.ground_height=ground_height;geo.ROOT=ROOT
Batch=geo.Batch;col=geo.col
groundcol=col('01_Terrain_and_retaining_walls')
roadcol=col('02_Roads_stairs_and_courts')
landcol=col('05_Trees_and_ground_cover')
propcol=col('06_Street_life')
backcol=col('07_Distant_city')
lights=[];route_records=[];prop_counts=defaultdict(int)

def prism(batch,poly,z0,z1,mat):
    if len(poly)<3:return
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly=list(reversed(poly))
    n=len(poly);flat=[Vector((p[0],p[1],0)) for p in poly]
    def zz(z,p):return z(*p) if callable(z) else z
    vs=[(p[0],p[1],zz(z0,p)) for p in poly]+[(p[0],p[1],zz(z1,p)) for p in poly]
    fs=[]
    for tri in tessellate_polygon([flat]):
        ids=tuple(int(v) if isinstance(v,int) else min(range(n),key=lambda k:(flat[k]-v).length_squared) for v in tri)
        fs.extend([tuple(reversed(ids)),tuple(i+n for i in ids)])
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    batch.mesh(vs,fs,mat)

def densify(pts,spacing=1.):
    out=[pts[0]]
    for a,b in zip(pts,pts[1:]):
        n=max(1,int(math.ceil(math.dist(a,b)/spacing)))
        out.extend((a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(1,n+1))
    return out

def strip(batch,pts,width,zfun,mat,offset=0.,lift=.0):
    pts=densify(pts,1.0);vs=[]
    for i,p in enumerate(pts):
        a=pts[max(0,i-1)];b=pts[min(len(pts)-1,i+1)]
        d=Vector((b[0]-a[0],b[1]-a[1]));d.normalize();n=Vector((-d.y,d.x))
        z=zfun(*p)+lift
        for side in [-1,1]:vs.append((p[0]+n.x*(offset+side*width*.5),p[1]+n.y*(offset+side*width*.5),z))
    fs=[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(pts)-1)]
    batch.mesh(vs,fs,mat)

def kerb(batch,pts,offset,zfun,mat='concrete',width=.18,height=.20):
    pts=densify(pts,1.8)
    for a,b in zip(pts,pts[1:]):
        d=Vector((b[0]-a[0],b[1]-a[1]));l=d.length
        if l<.01:continue
        d.normalize();n=Vector((-d.y,d.x))
        poly=[(a[0]+n.x*(offset-width/2),a[1]+n.y*(offset-width/2)),(b[0]+n.x*(offset-width/2),b[1]+n.y*(offset-width/2)),(b[0]+n.x*(offset+width/2),b[1]+n.y*(offset+width/2)),(a[0]+n.x*(offset+width/2),a[1]+n.y*(offset+width/2))]
        # Every curb corner follows the graded road. Horizontal per-segment
        # blocks used to float/sink along this steep Chongqing road.
        prism(batch,poly,lambda x,y:zfun(x,y)-height*.25,lambda x,y:zfun(x,y)+height*.75,mat)

def rail(batch,pts,offset,zfun,height=.96):
    pts=densify(pts,2.)
    rail_metal='painted_metal' if REVISION>=7 else 'frame'
    for i,(a,b) in enumerate(zip(pts,pts[1:])):
        d=Vector((b[0]-a[0],b[1]-a[1]));d.normalize();n=Vector((-d.y,d.x))
        pa=Vector((a[0]+offset*n.x,a[1]+offset*n.y,zfun(*a)))
        pb=Vector((b[0]+offset*n.x,b[1]+offset*n.y,zfun(*b)))
        for h in [height,.45]:batch.cylinder(pa+Vector((0,0,h)),pb+Vector((0,0,h)),.028,rail_metal,8)
        batch.cylinder(pa,pa+Vector((0,0,height)),.034,rail_metal,8)
    if len(pts)>1:
        # A rail needs a supported final end as well as the start of each span.
        d=Vector((pts[-1][0]-pts[-2][0],pts[-1][1]-pts[-2][1])).normalized()
        n=Vector((-d.y,d.x))
        end=Vector((pts[-1][0]+offset*n.x,pts[-1][1]+offset*n.y,zfun(*pts[-1])))
        batch.cylinder(end,end+Vector((0,0,height)),.034,rail_metal,8)

def build_ground():
    # One shared landscape plan controls both the continuous ground mesh and
    # plant roots.  No blanket concrete substitution hides the planting soil.
    import landscape_v05
    landscape_v05.build_ground(geo, groundcol, backcol)


def build_roads():
    for item in DATA['roads']:
        if item['tags'].get('tunnel')=='yes':continue
        bridge=item['tags'].get('bridge')=='yes'
        width=road_width(item)
        zfun=lambda x,y:ground_height(x,y)+(.18 if not bridge else 5.4)
        for k,pts in enumerate(clip_line(item['points'])):
            name='COL_Road_%s_%s'%(item['id'],k);b=Batch(name,roadcol)
            strip(b,pts,width,zfun,'asphalt')
            curb=Batch(name+'_curb',roadcol)
            if item['type'] in ['residential','tertiary']:
                for s in [-1,1]:
                    strip(b,pts,1.15,zfun,'pavement',s*(width/2+.575),.10)
                    kerb(curb,pts,s*(width/2+.05),zfun)
            marking=Batch('Road_paint_'+str(item['id']),roadcol)
            if item['type']!='residential':
                p=densify(pts,1.3)
                for a,c in zip(p[::5],p[2::5]):strip(marking,[a,c],.085,zfun,'line_white',lift=.012)
                for s in [-1,1]:strip(marking,pts,.07,zfun,'line_white',s*(width*.5-.3),.011)
            if bridge:
                deck=Batch('Bridge_structure_'+str(item['id']),roadcol)
                strip(deck,pts,width+.4,lambda x,y:zfun(x,y)-.65,'concrete')
                for s in [-1,1]:rail(curb,pts,s*(width*.5-.05),zfun,1.05)
                for p in densify(pts,13.)[::10]:
                    h=zfun(*p);deck.box((p[0],p[1],(h+ground_height(*p))/2),(1.1,1.1,h-ground_height(*p)), 'concrete')
                deck.finish()
            b.finish();curb.finish(.025);marking.finish()
            route_records.append({'name':item['tags'].get('name',str(item['id'])),'type':'OSM road','points':pts,'width_m':width,'authored_height':True})

def build_walk(pts,width,name,stepped=False,railed=False):
    b=Batch('COL_Walk_'+name,roadcol);trim=Batch('Walk_details_'+name,roadcol)
    step_surface='step_concrete' if REVISION>=6 else 'pavement'
    if stepped:
        for a,c in zip(pts,pts[1:]):
            z0=ground_height(*a)+.13;z1=ground_height(*c)+.13
            l=math.dist(a,c);dz=z1-z0
            if l<.2:continue
            if abs(dz)<.26:strip(b,[a,c],width,ground_height,step_surface,lift=.13);continue
            count=max(1,math.ceil(abs(dz)/.17));d=Vector((c[0]-a[0],c[1]-a[1]));d.normalize();n=Vector((-d.y,d.x))
            for i in range(count):
                p=(a[0]+(c[0]-a[0])*i/count,a[1]+(c[1]-a[1])*i/count)
                q=(a[0]+(c[0]-a[0])*(i+1)/count,a[1]+(c[1]-a[1])*(i+1)/count)
                top=z0+dz*((i+1)/count if dz>0 else i/count)
                poly=[(p[0]-n.x*width/2,p[1]-n.y*width/2),(q[0]-n.x*width/2,q[1]-n.y*width/2),(q[0]+n.x*width/2,q[1]+n.y*width/2),(p[0]+n.x*width/2,p[1]+n.y*width/2)]
                prism(b,poly,top-.24,top,step_surface)
                # A worn, slim stone nosing catches the light.
                trim.cylinder((q[0]-n.x*width*.495,q[1]-n.y*width*.495,top+.005),(q[0]+n.x*width*.495,q[1]+n.y*width*.495,top+.005),.016,'stone',6)
    else:strip(b,pts,width,ground_height,'pavement',lift=.13)
    for s in [-1,1]:
        edge_width=.06 if name=='Narrow_upper_passage' else .14
        strip(trim,pts,edge_width,ground_height,'stone',s*(width*.5-edge_width*.5),.14)
        if railed:rail(trim,pts,s*(width*.5-.07),lambda x,y:ground_height(x,y)+.13)
    b.finish();trim.finish()
    if REVISION>=4 and name in ['Central_stair_lane','West_residential_link']:
        # Leave each junction and landing open; add full-height support rails
        # on the longer stair flights, with real collision geometry.
        safety=Batch('COL_Handrails_'+name,roadcol)
        for a,c in zip(pts,pts[1:]):
            length=math.dist(a,c)
            if length<9:continue
            t=1.6/length
            q=(a[0]+(c[0]-a[0])*t,a[1]+(c[1]-a[1])*t)
            r=(c[0]-(c[0]-a[0])*t,c[1]-(c[1]-a[1])*t)
            pieces=[(q,r)]
            if name=='Central_stair_lane':
                # The court and south-courtyard branch join mid-flight, not at
                # the centreline vertices. Leave explicit full-width openings.
                for lo,hi in [(-2.2,2.2),(-22.,-17.4)]:
                    clipped=[]
                    for p0,p1 in pieces:
                        dy=p1[1]-p0[1]
                        if abs(dy)<1e-8:
                            if not lo<=p0[1]<=hi:clipped.append((p0,p1))
                            continue
                        cuts=sorted(set([0.,1.]+[max(0.,min(1.,(v-p0[1])/dy)) for v in [lo,hi]]))
                        for u,v in zip(cuts,cuts[1:]):
                            mid=p0[1]+dy*(u+v)/2
                            if lo<=mid<=hi or v-u<1e-5:continue
                            pa=tuple(p0[k]+(p1[k]-p0[k])*u for k in [0,1])
                            pc=tuple(p0[k]+(p1[k]-p0[k])*v for k in [0,1])
                            clipped.append((pa,pc))
                    pieces=clipped
            for p0,p1 in pieces:
                for side in [-1,1]:rail(safety,[p0,p1],side*(width*.5+.15),lambda x,y:ground_height(x,y)+.13)
        safety.finish()
    route_records.append({'name':name,'type':'Authored supplementary walk','points':pts,'width_m':width,'stepped':stepped})

def build_paths():
    for item in DATA['paths']:
        if item['tags'].get('tunnel')=='yes':continue
        for i,pts in enumerate(clip_line(item['points'])):
            build_walk(pts,road_width(item),'OSM_'+str(item['id'])+'_'+str(i),item['type']=='steps',item['type']=='steps')
    for name,pts,w in SUPPLEMENTAL:
        if name=='Main hillside lane':
            build_walk(pts[:6],w,'Central_stair_lane',True,False)
            build_walk(pts[5:9],1.65,'Narrow_upper_passage',True,False)
            build_walk(pts[8:],2.5,'Upper_terrace_connection',True,False)
        else:build_walk(pts,w,name.replace(' ','_'),name in ['West residential link','East photo alley'],False)

def court_and_details():
    b=Batch('COL_Community_court',roadcol)
    if REVISION>=3:
        b.box((-34,0,20.43),(24,30,.20),'pavement')
        b.box((-34,0,20.54),(20,28,.015),'court_green')
        for y in [-10.15,10.15]:b.box((-34,y,20.555),(4.9,5.7,.015),'court_red')
        for x in [-41.5,-26.5]:b.box((x,0,20.57),(.055,26,.012),'line_white')
        for y in [-13,13,0]:b.box((-34,y,20.57),(15,.055,.012),'line_white')
        for y in [-10.15,10.15]:
            for x in [-36.45,-31.55]:b.box((x,y,20.57),(.055,5.7,.012),'line_white')
        for y in [-7.3,7.3]:b.box((-34,y,20.57),(4.9,.055,.012),'line_white')
        for cy,r in [(0.,1.8),(-7.3,1.8),(7.3,1.8)]:
            pts=[(-34+r*math.cos(i*math.tau/80),cy+r*math.sin(i*math.tau/80),20.575) for i in range(81)]
            b.pipe(pts,.025,'line_white',4)
        for cy,sg in [(-10.9,1),(10.9,-1)]:
            pts=[(-34+6.5*math.cos(i*math.pi/70),cy+sg*6.5*math.sin(i*math.pi/70),20.575) for i in range(71)]
            b.pipe(pts,.025,'line_white',4)
            for x in [-40.5,-27.5]:b.box((x,(cy+sg*-13)/2,20.57),(.055,abs(sg*-13-cy),.012),'line_white')
    else:
        b.box((-34,0,20.43),(24,28,.20),'court_green')
        for x in [-42,-26]:b.box((x,0,20.54),(7.5,8,.015),'court_red')
        for x in [-45,-23]:b.box((x,0,20.56),(.06,26,.012),'line_white')
        for y in [-13,13,0]:b.box((-34,y,20.56),(22,.06,.012),'line_white')
        for cx in [-42.5,-25.5]:
            for x in [cx-2.5,cx+2.5]:b.box((x,0,20.56),(.06,7,.012),'line_white')
            b.box((cx,0,20.56),(5,.06,.012),'line_white')
    b.finish()
    deco=Batch('Court_fence_and_hoops',propcol)
    for y,sg in [(-12,1),(12,-1)]:
        x=-34;z=20.56
        deco.cylinder((x,y,z),(x,y,z+3.45),.085,'faded_green',12)
        deco.cylinder((x,y,z+3.35),(x,y+sg*.75,z+3.35),.07,'faded_green',10)
        deco.box((x,y+sg*.80,z+3.36),(1.8,.08,1.10),'offwhite')
        for xx in [x-.28,x+.28]:deco.box((xx,y+sg*.85,z+3.24),(.035,.02,.43),'faded_red')
        # Rim built as a circle in a horizontal plane.
        ring=[(x+.24*math.cos(i*math.tau/24),y+sg*1.10+.24*math.sin(i*math.tau/24),z+3.05) for i in range(25)]
        deco.pipe(ring,.019,'faded_red',6)
        for i in range(12):
            a=i*math.tau/12
            deco.cylinder((x+.23*math.cos(a),y+sg*1.10+.23*math.sin(a),z+3.03),(x+.12*math.cos(a),y+sg*1.10+.12*math.sin(a),z+2.62),.008,'offwhite',4)
    for y in [-15.5,15.5]:
        for x in range(-46,-21,3):deco.cylinder((x,y,20.4),(x,y,22.6),.035,'frame',8)
        for h in [.3,1.0,1.7,2.2]:deco.cylinder((-46,y,20.4+h),(-22,y,20.4+h),.016,'frame',6)
        # Real diamond wire infill replaces the implausibly empty fence bays.
        # Clipped diagonals share one material batch; no opaque billboard net.
        net_w=24.;net_h=2.12;spacing=.20
        for direction in [-1,1]:
            for k in range(-int(net_h/spacing)-1,int(net_w/spacing)+2):
                origin=k*spacing
                lo=max(0.,-origin);hi=min(net_h,net_w-origin)
                if hi-lo<.01:continue
                xa=origin+lo;xb=origin+hi
                if direction<0:xa,xb=net_w-xa,net_w-xb
                deco.cylinder((-46+xa,y+direction*.003,20.44+lo),
                              (-46+xb,y+direction*.003,20.44+hi),.0023,'painted_metal',4)
    deco.finish()
    # Short retaining edges and coping are interrupted on the east approach.
    base=Batch('COL_Court_retaining',groundcol)
    for y in [-15.1,15.1]:
        for x in range(-46,-22,2):
            low=raw_height(x,y)-.08
            if low<20.3:base.box((x+1,y,(low+20.5)/2),(2.,.4,20.5-low),'stone')
    base.finish()
    if REVISION>=2:
        fill=Batch('COL_Court_side_foundations',groundcol)
        for x in [-46.1,-21.9]:
            for k in range(30):
                y=-15.+k+.5;lo=min(raw_height(x,y),20.30)-.1
                if REVISION>=3 and x>-30 and abs(y)<1.6:continue
                fill.box((x,y,(lo+20.52)/2),(.35,1.01,20.52-lo),'stone')
        fill.finish()
    if REVISION>=3:
        entry=Batch('COL_Court_east_entry_steps',roadcol)
        start=-18.;end=-23.;z0=ground_height(start,0)+.13;z1=20.54
        count=max(1,math.ceil((z1-z0)/.16))
        for i in range(count):
            a=start+(end-start)*i/count;c=start+(end-start)*(i+1)/count
            top=z0+(z1-z0)*(i+1)/count
            entry.box(((a+c)/2,0,top-.12),(abs(c-a)+.01,2.8,.24),'step_concrete' if REVISION>=6 else 'pavement')
        entry.finish()
        rails=Batch('Court_entry_rails',propcol)
        for y in [-1.48,1.48]:
            rails.cylinder((start,y,z0+.88),(end,y,z1+.88),.029,'frame',8)
            for x,z in [(start,z0),(end,z1)]:rails.cylinder((x,y,z),(x,y,z+.88),.035,'frame',8)
        rails.finish()

build_ground();build_roads();build_paths();court_and_details()
import architecture_full
arch=architecture_full.build(geo)
import landscape_v05
terrain_interior_report=landscape_v05.recess_terrain_for_interiors(
    geo,groundcol,arch,OUT/'terrain_interior_audit.json')
interior_assets=col('04_District_real_furniture_and_houseplants')
for marker in arch.get('interior_asset_markers',[]):
    placed=scanned.make_prop(marker['asset'],marker['name'],marker['position'],
        height=marker.get('height'),width=marker.get('width'),yaw=marker.get('yaw',0.),
        lod=marker.get('lod','base'),collection=interior_assets)
    for ob in placed:
        ob['cq_interior']=True
        ob['cq_interior_occluder']=True
        for key,value in marker.items():
            if key.startswith('cq_room_'):ob[key]=value
print('REAL_INTERIOR_ASSETS',len(arch.get('interior_asset_markers',[])),flush=True)
print('ARCHITECTURE_READY',flush=True)

def occupied(p,margin=1.):
    for rec in arch['buildings']:
        poly=rec['points']
        if point_in_poly(p,poly):return True
        if min(distance_segment(p,a,b)[0] for a,b in zip(poly,poly[1:]+poly[:1]))<margin:return True
    return False

def free_land(p,clear=1.5):
    if not(-98<p[0]<98 and -76<p[1]<98):return False
    if -50<p[0]<-17 and -20<p[1]<19:return False
    if occupied(p,clear):return False
    for item in DATA['roads']+DATA['paths']:
        if item['tags'].get('tunnel')=='yes':continue
        if line_distance(p,item['points'])<road_width(item)/2+clear:return False
    for _,pts,w in SUPPLEMENTAL:
        if line_distance(p,pts)<w/2+clear:return False
    return True

def put(fn,p,**kw):
    prop_counts[fn.__name__]+=1
    z=kw.pop('z',ground_height(*p)+.13)
    return fn((p[0],p[1],z),collection=propcol,**kw)

def vegetation():
    import landscape_v05
    prop_counts.update(landscape_v05.build_planting(
        geo, scanned, props, arch, free_land, occupied, landcol, propcol, REVISION))
    landscape_v05.write_report(OUT / 'landscape_report.json')


def street_life():
    if REVISION>=2:
        for bi,rec in enumerate(arch['buildings']):
            for en in rec.get('entrances',[]):
                if en['type']!='shop':continue
                p=en['position'];q=en['approach'];out=Vector((q[0]-p[0],q[1]-p[1]));out.normalize();t=Vector((-out.y,out.x))
                side=1 if bi%2 else -1
                place=(q[0]+t.x*side*2.2,q[1]+t.y*side*2.2)
                if occupied(place,.3):continue
                if line_distance(place,SPINE)<1.5:continue
                put(props.make_crates,place,yaw=math.atan2(out.y,out.x)-math.pi/2)
                if bi%3==0:
                    cafe=(q[0]-t.x*side*2.8+out.x*.6,q[1]-t.y*side*2.8+out.y*.6)
                    if not occupied(cafe,.5) and line_distance(cafe,SPINE)>2.3:put(props.make_cafe_set,cafe,yaw=math.atan2(out.y,out.x))
    for i,(p,yaw,delivery) in enumerate([((-18,-70),.4,True),((11,-64),1.2,True),((-25,-55),-.4,False),((-48,-35),.2,False),((-71,-38),-.7,True),((46,54),2.2,True),((61,75),.3,False)]):
        if not occupied(p,.3):put(props.make_scooter,p,yaw=yaw,delivery=delivery,seed=99+i)
    for p,yaw in [((-36,-72),.0),((-70,-32),.6),((-48,18),1.7),((60,63),.0),((78,-43),1.1)]:
        if not occupied(p,.3):put(props.make_bins,p,yaw=yaw)
    for p,yaw in [((-25,-72),0),((-70,-53),0),((47,53),math.pi*.3)]:
        if not occupied(p,.3):put(props.make_cafe_set,p,yaw=yaw)
    for p,yaw in [((-22,-70),.1),((-53,-45),1.4),((8,-38),0)]:
        if not occupied(p,.2):put(props.make_crates,p,yaw=yaw)
    for p,yaw in [((68,61),0),((-6,80),math.pi*.5),((46,-78),.5)]:
        if not occupied(p,.4):
            if REVISION>=5:
                scanned.make_covered_car('Parked_car_%s_%s'%p,(*p,ground_height(*p)+.12),yaw=yaw,collection=propcol,length=4.35)
                prop_counts['scanned_parked_cars']+=1
            else:put(props.make_van,p,yaw=yaw)
    for p,yaw in [((-49,10),.4),((-74,-5),0),((-13,66),.5)]:
        if not occupied(p,0):put(props.make_clothesline,p,span=3.8,yaw=yaw,seed=int(p[0]*7))
    lamp_positions=[(-91,-70),(-61,-72),(-29,-76),(7,-75),(39,-71),(74,-47),(-22,-44),(-17,-15),(-20,20),(-27,62),(-9,76),(42,76),(64,45),(-75,37)]
    for i,p in enumerate(lamp_positions):
        if occupied(p,.35):continue
        h=5.0 if i<6 else 4.3
        put(props.make_street_lamp,p,height=h)
        if i%2==0:lights.append({'name':'Street lamp %02d'%i,'position':godot((p[0],p[1],ground_height(*p)+h)),'color':[1,.76,.49],'energy':.30,'range':5.8,'shadows':False})
    # Bench, drain gratings, bollards, electrical boxes and coiled hoses.
    b=Batch('Street_small_furniture',propcol)
    for x,y in [(-46,-9),(-46,9),(40,56),(-12,61),(-72,-35)]:
        z=ground_height(x,y)+.14
        for dx in [-.65,.65]:
            b.box((x+dx,y,z+.22),(.07,.55,.43),'frame')
            b.box((x+dx,y+.23,z+.60),(.07,.07,.7),'frame')
        for dy in [-.22,0,.22]:b.box((x,y+dy,z+.44),(1.8,.14,.06),'timber')
        for h in [.68,.88]:b.box((x,y+.26,z+h),(1.8,.07,.12),'timber')
    for _,pts,w in SUPPLEMENTAL:
        for i,p in enumerate(densify(pts,5.)[::3]):
            z=ground_height(*p)+.145
            b.box((p[0]+w*.32,p[1],z),(.4,.28,.022),'dark')
            for j in range(7):b.box((p[0]+w*.32-.17+j*.055,p[1],z+.014),(.017,.27,.017),'aluminium')
    for p in [(16,-64),(-21,-50),(-20,17),(62,75)]:
        for dx in [-1.,1.]:
            z=ground_height(p[0]+dx,p[1])+.13
            b.cylinder((p[0]+dx,p[1],z),(p[0]+dx,p[1],z+.7),.075,'frame',10)
            b.cylinder((p[0]+dx,p[1],z+.46),(p[0]+dx,p[1],z+.52),.079,'paint_yellow',10)
    b.finish(.012)
    if REVISION>=5:
        for bi,rec in enumerate(arch['buildings']):
            for en in rec.get('entrances',[]):
                p=en['position'];q=en['approach'];out=Vector((q[0]-p[0],q[1]-p[1]));out.normalize();t=Vector((-out.y,out.x))
                site=(q[0]+t.x*3.15,q[1]+t.y*3.15)
                if occupied(site,.7) or any(line_distance(site,pts)<w/2+.75 for _,pts,w in SUPPLEMENTAL):continue
                scanned.make_debris_group('Resident_waste_%s'%bi,(*site,ground_height(*site)+.12),seed=390+bi,collection=propcol,yaw=math.atan2(out.y,out.x)-math.pi/2)
                prop_counts['scanned_waste_groups']+=1
                break
        prop_counts.update(urban_fabric.micro_dressing(geo,arch,occupied,free_land,prism,propcol,REVISION,
            audit_path=OUT/'drain_grate_support_audit.json'))
    # Overhead sagged cables give the lanes a convincing inhabited scale.
    cable=Batch('Utility_cables',propcol)
    for a,c,zoff in [((-32,-57),(5,-56),5.),((-71,-35),(-51,-32),5.2),((-18,-25),(8,-23),6.2),((-73,33),(-42,40),6.5),((-25,60),(14,59),5.8)]:
        for offset in [0.,.13,.25]:
            pts=[]
            for i in range(19):
                t=i/18;x=a[0]+(c[0]-a[0])*t;y=a[1]+(c[1]-a[1])*t+offset
                z=ground_height(*a)*(1-t)+ground_height(*c)*t+zoff-1.05*4*t*(1-t)
                pts.append((x,y,z))
            cable.pipe(pts,.014,'dark',5)
    cable.finish()

context_ownership={'excluded_refined_building_ids':[], 'rule':'One architectural representation per OSM building ID; refined core geometry owns its entire source identity.'}

def distant_city():
    records=[]
    refined_ids={str(record['id']) for record in arch['buildings']}
    all_sources=DATA['context_buildings']+[b for b in DATA['buildings'] if b['id'] in [809889625,809889603]]
    if REVISION>=3:
        # The two towers also occur in context_buildings; duplicate coplanar
        # shells produced visible z-fighting, especially in the overview.
        all_sources=list({item['id']:item for item in all_sources}.values())
    for i,item in enumerate(all_sources):
        pts=item['points'];cx=sum(p[0] for p in pts)/len(pts);cy=sum(p[1] for p in pts)/len(pts)
        if max(abs(cx),abs(cy))>280:continue
        if abs(cx)<95 and abs(cy)<95:continue
        if REVISION>=2 and cy<-95:continue
        # A centroid outside the 200 m square does not make a second shell
        # safe: three northern/western source footprints cross its edge.
        # Their old solid context prisms previously sealed real core windows.
        # Preserve the refined representation and omit all parts of the
        # duplicate context object (prism, painted windows and facade props).
        if str(item['id']) in refined_ids:
            context_ownership['excluded_refined_building_ids'].append(item['id'])
            continue
        rng=random.Random(item['id']);levels=int(item.get('levels') or rng.choice([5,6,7,9,12,16]))
        height=item.get('height') or levels*3.05
        base=raw_height(cx,cy)-.1
        b=Batch('Context_%s'%item['id'],backcol)
        wall=['plaster_grey','plaster_ochre','tile_blue','tile_cream'][i%4]
        prism(b,pts,base-4,base+height,wall)
        if sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(pts,pts[1:]+pts[:1]))<0:pts=list(reversed(pts))
        detail=Batch('Context_windows_%s'%item['id'],backcol)
        for a,c in zip(pts,pts[1:]+pts[:1]):
            d=Vector((c[0]-a[0],c[1]-a[1]));w=d.length
            if w<2:continue
            d.normalize();out=Vector((d.y,-d.x));bays=max(1,int(w/3.2))
            for f in range(levels):
                for k in range(bays):
                    t=(k+.5)/bays;u=a[0]+(c[0]-a[0])*t;v=a[1]+(c[1]-a[1])*t;z=base+f*3.05+1.9
                    hh=.68;ww=min(.72,w/bays*.31)
                    vs=[(u-d.x*ww+out.x*.035,v-d.y*ww+out.y*.035,z-hh),(u+d.x*ww+out.x*.035,v+d.y*ww+out.y*.035,z-hh),(u+d.x*ww+out.x*.035,v+d.y*ww+out.y*.035,z+hh),(u-d.x*ww+out.x*.035,v-d.y*ww+out.y*.035,z+hh)]
                    detail.mesh(vs,[(0,1,2,3)],'glass_blue' if rng.random()>.16 else 'glass_warm')
            for f in range(1,levels):
                z=base+f*3.05
                detail.cylinder((a[0],a[1],z),(c[0],c[1],z),.055,'concrete',4)
        b.finish();detail.finish()
        if REVISION>=5:urban_fabric.context_facade(geo,pts,base,height,levels,item['id'],backcol)
        records.append({'osm_id':item['id'],'levels':levels,'height_m':height,'height_estimated':not bool(item.get('height'))})
    if REVISION>=5:records.extend(urban_fabric.backdrop(geo,prism,backcol,records,REVISION))
    return records

vegetation();street_life()
prop_counts.update(urban_fabric.courtyard_enclosures(geo,scanned,occupied,propcol,landcol,REVISION))
prop_counts.update(urban_fabric.planted_edges(geo,scanned,free_land,propcol,landcol,REVISION))
context_records=distant_city()
context_ownership['remaining_context_ids']=[r['osm_id'] for r in context_records if 'osm_id' in r]
context_ownership['duplicate_ids_remaining']=sorted({str(r['id']) for r in arch['buildings']} & {str(i) for i in context_ownership['remaining_context_ids']})
context_ownership['passed']=not context_ownership['duplicate_ids_remaining']
assert context_ownership['passed'], 'A refined building still has a duplicate context shell'
(OUT/'context_ownership_audit.json').write_text(json.dumps(context_ownership,ensure_ascii=False,indent=2)+'\n')
print('LANDSCAPE_READY',dict(prop_counts),flush=True)

def make_viewpoints():
    views={}
    def shot(key,title,p,target,fov=57):
        views[key]={'title':title,'position':godot(p),'target':godot(target),'fov':fov}
    def walkshot(key,title,p,t,eye=1.7,lookheight=3.2,fov=60):
        shot(key,title,(p[0],p[1],ground_height(*p)+eye),(t[0],t[1],ground_height(*t)+lookheight),fov)
    shot('overview','全街区 · 南向北',(90,-120,230) if REVISION>=3 else (115,-145,143),(0,5,20),53 if REVISION>=3 else 54)
    walkshot('street_entry','山城巷街口',(24,-77),(1,-63),lookheight=3.8,fov=60)
    shot('noodle_corner','小面馆与下层街面',(-24,-53.5,13.8122),(-26.5,-62.05,14.6),64)
    walkshot('central_steps','中央梯坎与临街住家',(-20,-52),(-20,-25),lookheight=4.1,fov=59)
    walkshot('west_lane','西侧居民巷',(-73,-34),(-77,-10),lookheight=4.3,fov=61)
    shot('community_court','社区球场与住宅',(-20,-19,22.3),(-36,4,23.5),66)
    shot('narrow_passage','上坡楼间通道',(-35.5,46.2,27.5861),(-30.6,54.6,28.8952),70)
    shot('upper_houses','上层院落回望',(-12,63,30.9218),(-43,65,32.6),63)
    walkshot('east_gallery','东侧砖墙坡巷',(50,-49),(65,-32),lookheight=3.6,fov=61)
    walkshot('residential_road','东侧居民道路',(64,34),(65,67),lookheight=5.1,fov=59)
    walkshot('upper_street','上层长街与店面',(4,80),(28,67),lookheight=4.0,fov=62)
    shot('roofscape','台地、院落与屋顶',(14,-20,64),(-31,8,22),59)
    walkshot('community_front','社区服务站',(28,4),(13,11),lookheight=2.4,fov=61)
    shot('residential_entry','居民楼入口与墙脚',(-43,-22,17.7423),(-52.9,-19.5,18.85),64)
    # These remain live player-height views of the same scene, including the
    # panes and window frames; no isolated furniture stage is used for review.
    closeups={
      'window_A05_1':('window_dining','临街住家 · 备餐间近景'),
      'window_A04_1':('window_reading','坡巷住家 · 窗内生活近景'),
      'window_809889624_1':('window_courtyard','院落住家 · 家务间近景'),
      'window_809889629_1':('window_living','坡道住家 · 深房与木椅近景'),
      'window_809889630_1':('window_north','北侧住家 · 窗内生活近景'),
      'shop_A01':('noodle_interior','小面馆 · 门口看店内'),
      'shop_809889626':('tea_interior','巷口茶馆 · 门口看店内')}
    for candidate in arch.get('interior_review_views',[]):
        if candidate['name'] in closeups:
            key,title=closeups[candidate['name']]
            views[key]={'title':title,'position':candidate['position'],
                        'target':candidate['target'],'fov':candidate['fov']}
    walkshot('planting_detail','树池、土壤与旧铺装近景',(52.2,-48.2),(56.5,-45.2),eye=1.65,lookheight=.18,fov=55)
    samples=[]
    for name,pts,w in SUPPLEMENTAL:
        for p in densify(pts,9.)[::2]:
            if not occupied(p,.4):samples.append(godot((p[0],p[1],ground_height(*p)+2.8)))
    for item in DATA['paths']:
        if item['tags'].get('tunnel')=='yes':continue
        for pts in clip_line(item['points']):
            for p in densify(pts,15.)[::2]:
                if not occupied(p,.4):samples.append(godot((p[0],p[1],ground_height(*p)+2.8)))
    walls=[]
    for rec in arch['buildings'][::4]:
        pts=rec['points'];a,c=max(zip(pts,pts[1:]+pts[:1]),key=lambda pair:math.dist(*pair))
        d=Vector((c[0]-a[0],c[1]-a[1]));d.normalize();n=Vector((d.y,-d.x));mid=((a[0]+c[0])/2,(a[1]+c[1])/2)
        z=rec['base_m']+1.
        walls.append({'name':'wall_'+str(rec['id']),'from':godot((mid[0]+n.x*2,mid[1]+n.y*2,z)),'to':godot((mid[0]-n.x*2,mid[1]-n.y*2,z))})
    walking=[]
    for name,a,c,progress,gain in [
        ('central_stair_ascent',(-20,-49),(-20,-31),14.,2.0),
        ('west_lane_ascent',(-73,-25),(-73,-10),11.,1.2),
        ('upper_road_walk',(0,78),(44,78),38.,-.3),
        ('narrow_upper_passage',(-36.5,44),(-29,56),9.,1.2)
    ]:
        walking.append({'name':name,'from':godot((a[0],a[1],ground_height(*a)+.30)),'to':godot((c[0],c[1],ground_height(*c)+.30)),'frames':max(420,int(math.dist(a,c)*29)),'min_progress_m':progress,'min_height_gain_m':gain})
    pickup=(-24.29,-60.2);drop=(-12,59)
    settings={
      'coordinate_system':'Godot X east,Y up,Z south; 1 unit=1 metre',
      'authored_patch_center':[0,20,0],'authored_patch_extent_m':[200,200],
      'walk_spawn':godot((20,-76,ground_height(20,-76)+.32)),
      'walk_target':godot((16,-65,ground_height(16,-65)+1.7)),
      'view_order':list(views),'views':views,
      'pickup':godot((*pickup,ground_height(*pickup)+.2)),
      'dropoff':godot((*drop,ground_height(*drop)+.2)),
      'pickup_label':'梯坎小面馆','dropoff_label':'上层住宅',
      'ground_samples':samples,'wall_tests':walls,'walking_tests':walking,
      'survey_grid_count':11,'survey_extent':98,'survey_ray_top':200,
      'lights':lights+arch.get('lights',[])[:15],
      'lighting':{'sun_rotation_deg':[-36,-48,0],'sun_energy':.50,'ambient_energy':.42,'exposure':1.0,
        'sun_color':[1.,.95,.86],'ambient_color':[.68,.77,.87],
        'fog_color':[.67,.72,.75],'fog_density':.0016,
        'contrast':1.025,'saturation':.91,'shadow_max_distance':180.,'shadow_bias':.08,'shadow_normal_bias':1.0},
      'lighting_profiles':{'forward_plus':{'ambient_energy':.48,'sun_energy':1.2,'exposure':1.05}},
      'provenance':'OSM XY + independent architecture; authored terrain/dimensions, not a surveyed replica.'
    }
    if REVISION>=3:
        settings['lighting'].update({'procedural_clouds':True,'cloud_coverage':.76,'cloud_strength':.62,'cloud_scale':1.35,'cloud_seed':17.,'fog_density':.00125})
        settings['lighting_profiles']['forward_plus'].update({'ambient_energy':.52,'sun_energy':1.10,'exposure':1.05,'ssr':False,'ssao_half_size':True,'ssao_radius':1.25,'ssao_intensity':1.1,'ssao_detail':.5,'sun_angular_distance':1.2,'contrast':1.04,'saturation':.93})
    if REVISION>=4:
        settings['lighting']['fog_density']=.00045
        settings['lighting_profiles']['forward_plus']['contrast']=1.06
    return settings

config=make_viewpoints()
project=ROOT/'godot_project/assets';project.mkdir(parents=True,exist_ok=True)
if not STAGE_ONLY:(project/'viewpoints.json').write_text(json.dumps(config,ensure_ascii=False,indent=2))
(OUT/'viewpoints.json').write_text(json.dumps(config,ensure_ascii=False,indent=2))

# R16 corrections share the exact same pass used on the recovered editable R15 scene.
if REVISION>=16:
    import repair_scene_r16
    repair_scene_r16.apply(scene,OUT/'geometry_repairs.json')
if REVISION>=17:
    import repair_scene_r17
    repair_scene_r17.apply(scene,OUT/'geometry_repairs_r17.json')

# Active color layers store a light occlusion bake in later review iterations.
ao_report={'enabled':False}
if REVISION>=2:
    try:
        import bake_vertex_ao
        ao_report=bake_vertex_ao.bake(scene,sky_radius=12.0 if REVISION>=5 else 0.,sky_strength=.42)
    except ImportError:print('VERTEX_AO_HELPER_PENDING',flush=True)

# Keep bevels mild: they improve the grazing highlights without changing scale.
# All runtime meshes have valid UVs, including originally solid-color props.
for ob in scene.objects:
    if ob.type!='MESH':continue
    if not ob.data.uv_layers:
        uv=ob.data.uv_layers.new(name='UVMap')
        for f in ob.data.polygons:
            axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=(1,2) if axis==0 else ((0,2) if axis==1 else (0,1))
            for li in f.loop_indices:
                p=ob.data.vertices[ob.data.loops[li].vertex_index].co
                uv.data[li].uv=(p[axes[0]]/2,p[axes[1]]/2)
    if 'asset_origin' not in ob:
        ob['asset_origin']='Original authored geometry; geospatial source where recorded in architecture_manifest.json'
    if REVISION>=3 and not ob.get('scanned_asset',False):
        # Evaluate triangulation after bevels so glTF tangent-space normals have
        # valid triangles even on pipe caps and irregular facade components.
        tri=ob.modifiers.new('Final_export_triangulation','TRIANGULATE')
        tri.quad_method='BEAUTY';tri.ngon_method='BEAUTY';tri.keep_custom_normals=True

# Editable Blender presentation cameras are supplied, while acceptance images
# come exclusively from Godot's live World3D.
presentation=col('08_Presentation_cameras')
for key,v in config['views'].items():
    data=bpy.data.cameras.new('Camera_'+key);data.lens=32
    ob=bpy.data.objects.new('Camera_'+key,data);presentation.objects.link(ob)
    p=v['position'];t=v['target'];ob.location=(p[0],-p[2],p[1]);target=Vector((t[0],-t[2],t[1]))
    ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
scene.camera=bpy.data.objects['Camera_central_steps']
ld=bpy.data.lights.new('Preview_Sun','SUN');ld.energy=2.0;ld.angle=.12
lo=bpy.data.objects.new('Preview_Sun',ld);presentation.objects.link(lo);lo.rotation_euler=(.58,-.48,-.62)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.49,.61,.74,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1920;scene.render.resolution_y=1080
scene.view_settings.view_transform='AgX'

bpy.ops.file.pack_all()
blend=OUT/'chongqing_district.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
bpy.ops.object.select_all(action='DESELECT')
exported=[]
for ob in scene.objects:
    if ob.type=='MESH' and not ob.hide_render:ob.select_set(True);exported.append(ob)
glb=OUT/'chongqing_district.glb'
kwargs=dict(filepath=str(glb),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True,export_tangents=True)
if REVISION>=2:
    kwargs.update(export_vertex_color='ACTIVE',export_all_vertex_colors=False)
bpy.ops.export_scene.gltf(**kwargs)
if not STAGE_ONLY:
    shutil.copy2(glb,project/glb.name)
    shutil.copy2(ROOT/'architecture_manifest.json',project/'architecture_manifest.json')
    shutil.copy2(ROOT/'materials/material_provenance.json',project/'material_provenance.json')
report={'title':scene['title'],'revision':REVISION,'extent_metres':[200,200],
 'source_buildings':sum(r['source'].startswith('OpenStreetMap') for r in arch['buildings']),
 'detailed_buildings':len(arch['buildings']),'unique_building_signatures':arch['checks']['unique_geometry_signatures'],
 'architecture_profiles':arch['checks']['architecture_profile_count'],'background_buildings':len(context_records),
 'context_ownership':context_ownership,
 'meshes':len(exported),'triangles_before_modifiers':sum(max(0,len(p.vertices)-2) for ob in exported for p in ob.data.polygons),
 'props':dict(prop_counts),'routes':route_records,'vertex_ao':ao_report,
 'interior_terrain':{key:terrain_interior_report[key] for key in (
     'checked_rooms','original_intruding_rooms','final_intruding_rooms',
     'minimum_final_clearance_m','passed')},
 'blend_bytes':blend.stat().st_size,'glb_bytes':glb.stat().st_size,
 'provenance':{'planar':'OpenStreetMap contributors / ODbL 1.0; source outlines are retained in source_data/geo_layout.json','terrain':'Authored hillside and distant ridges, not DEM survey','architecture':'21 individually composed core buildings (14 mapped planar outlines, 7 authored infill); facade details/heights are authored. Additional surrounding blocks are context design, not surveyed reconstructions.','reference_photos':'Wikimedia Commons Shancheng Lane photographs used for visual study; no photo pixels are bundled as game textures','textures':'Poly Haven CC0 scans + original procedural surface assets; exact files and credits in material_provenance.json','props_and_vegetation':'Original authored props plus Poly Haven CC0 scan models. Prepared instances, controlled LODs, and edited plant grouping; source credits in scanned_assets/source_credits.json.','lighting':'Godot runtime profile and CC0 photographic HDRI supplied in the engine project. Blender preview lighting is not the acceptance render.'},
 'runtime_captures':'Produced by Godot, not Blender renders. See verification/capture_manifest.json in each review round.'}
(OUT/'scene_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if not STAGE_ONLY:(project/'scene_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('DISTRICT_BUILD_COMPLETE',json.dumps({k:v for k,v in report.items() if k not in ['routes','provenance']},ensure_ascii=False),flush=True)

