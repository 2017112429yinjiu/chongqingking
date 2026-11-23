"""Original supplementary urban dressing and city context, deliberately authored.
Core OSM outlines remain unchanged. All measurements outside those outlines
are art direction, not a surveyed replica. UVs retain metre-scale scan maps.
"""
import math,random
from mathutils import Vector
from district_layout import ground_height,raw_height,point_in_poly,line_distance,SUPPLEMENTAL,DATA,road_width


def context_facade(geo,poly,base,height,levels,seed,collection):
    """Add deep-looking individual window groups, balconies and roof services."""
    rng=random.Random(seed)
    b=geo.Batch('Context_v04_detail_'+str(seed),collection)
    if sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(poly,poly[1:]+poly[:1]))<0:poly=list(reversed(poly))
    for ei,(a,c) in enumerate(zip(poly,poly[1:]+poly[:1])):
        d=Vector((c[0]-a[0],c[1]-a[1]));width=d.length
        if width<3:continue
        d.normalize();out=Vector((d.y,-d.x))
        f=geo.Batch('Context_v04_bays_%s_%s'%(seed,ei),collection,(a[0],a[1],base),tuple(d),tuple(out))
        bays=max(1,int(width/3.15));bay=width/bays
        for level in range(levels):
            z=level*(height/levels)
            # Mid-century inset balcony strips / later enclosed additions.
            if level>0:
                f.box((width/2,.07,z),(width,.19,.13),'concrete')
            for k in range(bays):
                u=(k+.5)*bay;w=min(1.7,bay*.57);h=1.55
                if (k+ei+seed)%7==0 and level>0:
                    f.box((u,.38,z+.95),(w+.42,.85,.10),'concrete')
                    for xx in [-w*.52,0,w*.52]:f.cylinder((u+xx,.79,z+1),(u+xx,.79,z+1.8),.023,'frame',6)
                    f.cylinder((u-w*.55,.79,z+1.82),(u+w*.55,.79,z+1.82),.024,'frame',6)
                f.box((u,.035,z+1.95),(w+.15,.14,h+.17),'dark')
                f.box((u,.115,z+1.95),(w,.035,h),rng.choice(['glass','glass_blue','glass','glass_warm']))
                for xx in [-w/2,0,w/2]:f.box((u+xx,.15,z+1.95),(.055,.08,h+.08),'aluminium')
                for zz in [-h/2,h/2]:f.box((u,.15,z+1.95+zz),(w+.10,.09,.06),'aluminium')
                f.box((u,.20,z+1.12),(w+.28,.36,.10),'concrete')
                if (k*5+level*3+seed)%9==0:
                    f.box((u+w*.56+.24,.3,z+1.28),(.58,.45,.43),'offwhite')
                    f.box((u+w*.56+.24,.54,z+1.28),(.46,.025,.28),'dark')
                    for j in range(5):f.box((u+w*.56+.24,.56,z+1.18+j*.05),(.47,.018,.011),'aluminium')
        for k in range(1,bays,5):
            u=k*bay
            f.pipe([(u,.23,.2),(u,.23,height-.1),(u,-.4,height+.08)],.048,'offwhite')
        # Roof parapet gives a recognisable silhouette rather than a flat box.
        f.box((width/2,.02,height+.30),(width,.27,.65),'concrete')
        # Merge all sides by material; window count must not imply thousands
        # of independent draw objects in the surrounding city.
        for mat,(vs,fs,ss) in f.data.items():b.mesh(vs,fs,mat)
    cx=sum(p[0] for p in poly)/len(poly);cy=sum(p[1] for p in poly)/len(poly)
    b.box((cx,cy,base+height+.7),(3.5,3.,1.4),'plaster_grey')
    b.box((cx,cy,base+height+1.42),(3.8,3.3,.18),'concrete')
    for dx in [-3.,3.]:
        b.cylinder((cx+dx,cy,base+height+.2),(cx+dx,cy,base+height+1.45),.56,'offwhite',12)
        b.cylinder((cx+dx,cy,base+height+1.44),(cx+dx,cy,base+height+1.49),.59,'aluminium',12)
    b.finish()


def backdrop(geo,prism,collection,existing,revision):
    """Surrounding city is designed context, each block varies in profile."""
    if revision<5:return []
    rng=random.Random(49019);records=[]
    existing_polys=[x['points'] for x in DATA['context_buildings']]
    for row in range(5):
        for col in range(9):
            x=-260+col*62+rng.uniform(-14,14)
            y=-190+row*90+rng.uniform(-16,16)
            if abs(x)<122 and abs(y)<122:continue
            if any(point_in_poly((x,y),p) for p in existing_polys):continue
            w=rng.uniform(20,34);depth=rng.uniform(17,29);rot=rng.uniform(-.30,.30)
            c=math.cos(rot);s=math.sin(rot)
            coords=[(-w/2,-depth/2),(w/2,-depth/2),(w/2,depth/2),(-w/2,depth/2)]
            # Alternate L-shaped apartment / narrow mid-rise / terrace outline.
            if (row+col)%3==0:
                coords=[(-w/2,-depth/2),(w/2,-depth/2),(w/2,depth*.15),(w*.1,depth*.15),(w*.1,depth/2),(-w/2,depth/2)]
            poly=[(x+u*c-v*s,y+u*s+v*c) for u,v in coords]
            levels=rng.choice([5,6,7,8,10,12]);height=levels*3.05
            if y<-120:height=min(height,24.)
            base=raw_height(x,max(-240,min(240,y)))-.3
            b=geo.Batch('Context_authored_%s_%s'%(row,col),collection)
            wall=rng.choice(['plaster_grey','plaster_ochre','tile_cream','brick_dark','concrete'])
            prism(b,poly,base-2,base+height,wall);b.finish()
            context_facade(geo,poly,base,height,levels,49000+row*100+col,collection)
            records.append({'id':'authored_context_%s_%s'%(row,col),'points':poly,'levels':levels,'height_m':height,'source':'Original contextual city block, not a mapped building'})
    # Distant hill ridges hide the flat world boundary, a geographic atmosphere
    # appropriate to the art direction, not terrain derived from a DEM.
    b=geo.Batch('Authored_distant_hill_ridges',collection)
    for ri,(radius,height) in enumerate([(760,95),(1050,145)]):
        vs=[]
        for i in range(97):
            a=math.tau*i/96
            rr=radius*(1+.06*math.sin(a*7+ri))
            peak=height+36*math.sin(a*3+ri)+18*math.sin(a*9)
            vs.extend([(math.cos(a)*rr,math.sin(a)*rr,-35),(math.cos(a)*rr,math.sin(a)*rr,peak)])
        fs=[(i*2,i*2+2,i*2+3,i*2+1) for i in range(96)]
        b.mesh(vs,fs,'hill_far' if ri else 'hill_near')
    b.finish()
    return records


def micro_dressing(geo,arch,occupied,free_land,prism,collection,revision,audit_path=None):
    if revision<5:return {}
    import drain_support
    rng=random.Random(21919)
    b=geo.Batch('District_surface_repairs_and_utilities',collection)
    points=[p for rec in arch['buildings'] for p in rec['points']]
    bounds=(min(p[0] for p in points)-2.,min(p[1] for p in points)-2.,
            max(p[0] for p in points)+2.,max(p[1] for p in points)+2.)
    # Terrain has already been recessed and all road/walk overlays exist here.
    # Read evaluated current objects; never use the analytic design-height field.
    drain_surfaces=drain_support.ActualSurfaceSampler.from_scene(bounds)
    drain_records=[]
    count=0
    # Attach utility cabinets to solid masonry intervals, using the actual
    # facade opening rectangles rather than a percentage across a window bay.
    for bi,rec in enumerate(arch['buildings']):
        pts=rec['points']
        by_edge={f['edge']:f['holes'] for f in rec.get('facade_openings',[])}
        for ei,(a,c) in enumerate(zip(pts,pts[1:]+pts[:1])):
            d=Vector((c[0]-a[0],c[1]-a[1]));length=d.length
            if length<7:continue
            d.normalize();out=Vector((d.y,-d.x));holes=by_edge.get(ei,[])
            preferred=length*(.23 if bi%2 else .75)
            candidates=[.60+i*.20 for i in range(max(1,int((length-1.2)/.20)))]
            candidates.sort(key=lambda u:abs(u-preferred))
            chosen=None
            for u in candidates:
                x=a[0]+d.x*u;y=a[1]+d.y*u
                probe=(x+out.x*.22,y+out.y*.22)
                if occupied(probe,.12):continue
                if any(line_distance(probe,p)<w/2+.4 for _,p,w in SUPPLEMENTAL):continue
                z=ground_height(*probe)+.06
                lo=z-rec['base_m']+.02;hi=lo+2.38
                # 0.96 m-wide blank strip covers the cabinet, valve and pipes.
                if any(not(u+.48<l-.04 or u-.48>r+.04 or hi<bot-.04 or lo>top+.04)
                       for l,r,bot,top in holes):continue
                # The wider ground drain must also avoid all entry thresholds.
                if any(not(u+.59<l-.04 or u-.59>r+.04 or lo+.10<bot-.04 or lo>top+.04)
                       for l,r,bot,top in holes):continue
                chosen=(u,x,y,z);break
            if chosen is None:continue
            u,x,y,z=chosen
            wall=geo.Batch('Resident_services_%s_%s'%(bi,ei),collection,(x,y,z),tuple(d),tuple(out))
            # Back sits 10 mm off the facade; it is no longer 300 mm in midair.
            wall.box((0,.095,1.10),(.56,.17,.76),'painted_metal')
            wall.box((.03,.192,1.1),(.46,.025,.64),'offwhite')
            for j in range(3):wall.box((-.13+j*.12,.209,1.21),(.07,.006,.13),'dark')
            for j in range(3):
                xx=-.17+j*.14
                wall.pipe([(xx,.085,.72),(xx,.085,.28),(xx+.055,.06,.20)],.014,'dark')
            wall.pipe([(.35,.07,1.45),(.35,.07,2.32),(.18,.04,2.32)],.014,'dark')
            wall.pipe([(-.36,.08,.04),(-.36,.08,1.6),(-.28,.08,1.6),(-.28,-.10,1.6)],.027,'painted_metal')
            wall.cylinder((-.36,.05,.8),(-.36,.18,.8),.058,'faded_red',10)
            for mat,(vs,fs,ss) in wall.data.items():b.mesh(vs,fs,mat)
            grate_id='Drain_grate_%03d'%count
            drain_x,drain_y=x,y
            relocate=(grate_id=='Drain_grate_041' and rec['id']==809889629 and ei==1)
            if relocate:
                # This sole cover previously straddled a 12 cm kerb. Move only
                # the cover 17 cm outwards; the wall cabinet/pipes stay put.
                drain_x+=out.x*.17;drain_y+=out.y*.17
            drainpoly=[(drain_x+d.x*xx+out.x*yy,drain_y+d.y*xx+out.y*yy)
                       for xx,yy in [(-.56,.16),(.56,.16),(.56,.56),(-.56,.56)]]
            bar_lines=[]
            for j in range(13):
                xx=-.53+j*.088
                pa=(drain_x+d.x*xx+out.x*.18,drain_y+d.y*xx+out.y*.18)
                pb=(drain_x+d.x*xx+out.x*.54,drain_y+d.y*xx+out.y*.54)
                bar_lines.append((pa,pb))
            plan=drain_support.plan_grate(drain_surfaces,grate_id,rec['id'],bi,ei,
                    (drain_x,drain_y),tuple(d),tuple(out),drainpoly,bar_lines)
            plan[0]['wall_fixture_anchor_xy']=[x,y]
            if relocate:
                oldpoly=[(x+d.x*xx+out.x*yy,y+d.y*xx+out.y*yy)
                         for xx,yy in [(-.56,.16),(.56,.16),(.56,.56),(-.56,.56)]]
                drain_support.record_curb_relocation(drain_surfaces,plan[0],(x,y),oldpoly)
            grate=geo.Batch(grate_id,collection)
            drain_records.append(drain_support.add_grate(grate,plan))
            count+=1
    # Pavement repair seams / drainage crossings break large continuous scans.
    for name,pts,width in SUPPLEMENTAL:
        for a,c in zip(pts,pts[1:]):
            d=Vector((c[0]-a[0],c[1]-a[1]));length=d.length
            if not length:continue
            d.normalize();out=Vector((-d.y,d.x))
            for k in range(max(1,int(length/5.8))):
                t=(k+.65)/max(1,int(length/5.8));x=a[0]+(c[0]-a[0])*t;y=a[1]+(c[1]-a[1])*t
                # Keep below footstep tolerance; no physically blocking rubble.
                z=ground_height(x,y)+.145
                b.cylinder((x-out.x*width*.47,y-out.y*width*.47,z),(x+out.x*width*.47,y+out.y*width*.47,z),.004,'soil_dark',5)
    b.finish()
    drain_support.write_audit(audit_path,revision,drain_records,drain_surfaces)
    return {'service_clusters':count}


def courtyard_enclosures(geo,scanned,occupied,collection,landcollection,revision):
    """Low resident-managed courts give previously empty plots an edge.
    Preserve all existing lane clearances; gates are cut before geometry.
    """
    if revision<6:return {'authored_courtyard_edges':0}
    rng=random.Random(44149);wall_count=0
    # Openings face the existing circulation, with staggered boundary heights.
    courts=[(-12.5,-31.,.8,-3.,(-20.,-16.)),(44.,31.,60.,44.,(35.,38.)),(18.,-64.,32.,-53.,(-60.,-57.))]
    for ci,(x0,y0,x1,y1,gate) in enumerate(courts):
        outline=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        wall=geo.Batch('COL_Resident_court_boundary_%s'%ci,collection)
        trim=geo.Batch('Resident_court_coping_%s'%ci,collection)
        for ei,(a,c) in enumerate(zip(outline,outline[1:]+outline[:1])):
            length=math.dist(a,c);steps=max(1,int(length/.65));t=Vector((c[0]-a[0],c[1]-a[1])).normalized();n=Vector((-t.y,t.x))
            for k in range(steps):
                p=(a[0]+(c[0]-a[0])*(k+.5)/steps,a[1]+(c[1]-a[1])*(k+.5)/steps)
                if ei==3 and gate[0]<p[1]<gate[1]:continue
                if occupied(p,.6):continue
                if any(line_distance(p,pts)<w/2+1.0 for _,pts,w in SUPPLEMENTAL):continue
                if any(line_distance(p,item['points'])<road_width(item)/2+1.0 for item in DATA['roads'] if item['tags'].get('tunnel')!='yes'):continue
                z=ground_height(*p);h=.72 if ei in [0,3] else 1.12
                o=geo.Batch('Court_edge_%s_%s_%s'%(ci,ei,k),collection,(p[0],p[1],z),tuple(t),tuple(n))
                o.box((0,0,h*.5),(length/steps+.012,.25,h),'brick_dark' if ci==0 else 'stone')
                o.box((0,0,h+.04),(length/steps+.025,.33,.08),'concrete')
                # Merge world-space faces into one collider instead of each
                # section becoming a standalone object.
                for mat,(vs,fs,ss) in o.data.items():wall.mesh(vs,fs,mat)
                wall_count+=1
                if k%4==0 and ei in [1,2]:
                    trim.cylinder((p[0],p[1],z+h),(p[0],p[1],z+h+.62),.022,'frame',6)
        wall.finish(.018);trim.finish()
        # Planting is created from landscape_v05's shared soil-bed plan before
        # the wall pass.  No unbacked shrubs are scattered onto this paved court.
        # A light service canopy over a courtyard corner; its position is
        # tested against source footprints and all established walking paths.
        x=x1-2.2;y=y0+2.2
        corners=[(x+u,y+v) for u in [-1.7,1.7] for v in [-1.5,1.5]]
        if all(not occupied(p,.35) and all(line_distance(p,q)>w/2+.8 for _,q,w in SUPPLEMENTAL) for p in corners):
            z=max(ground_height(*p) for p in corners)
            shed=geo.Batch('Courtyard_service_canopy_%s'%ci,collection)
            for xx,yy in corners:shed.cylinder((xx,yy,ground_height(xx,yy)),(xx,yy,z+2.3),.043,'painted_metal',8)
            # Continuous gently sagging sheet, no disconnected flying cards.
            vs=[]
            for j in range(5):
                for i in range(13):
                    xx=x-1.9+3.8*i/12;yy=y-1.7+3.4*j/4
                    zz=z+2.4+.025*math.sin(i*math.pi)-.12*math.sin(i*math.pi/12)+.11*(j/4)
                    vs.append((xx,yy,zz))
            fs=[(j*13+i,j*13+i+1,(j+1)*13+i+1,(j+1)*13+i) for j in range(4) for i in range(12)]
            shed.mesh(vs,fs,'painted_metal');shed.finish()
            scanned.make_crate_group('Resident_storage_%s'%ci,(x,y,z+.05),seed=ci,count=4,collection=collection)
    return {'authored_courtyard_wall_sections':wall_count,'authored_courtyards':len(courts)}


def planted_edges(geo,scanned,free_land,collection,landcollection,revision):
    """Slope-supported masonry troughs; all ground beds share terrain zoning."""
    import landscape_v05
    result = landscape_v05.build_stairside_planters(
        geo, scanned, free_land, collection, landcollection, revision)
    # Keep the report current after the late planter pass as well as vegetation.
    import os
    from pathlib import Path
    out = Path(os.environ.get('CQ_OUTPUT_DIR', str(Path(__file__).resolve().parent/'outputs')))
    landscape_v05.write_report(out/'landscape_report.json')
    return result
