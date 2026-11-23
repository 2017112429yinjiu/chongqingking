"""Author an unbranded Chongqing street taxi and a small commercial MPV in metres."""
from pathlib import Path
import bpy, math, sys
from mathutils import Vector

W=Path(__file__).resolve().parent; S=W/'scene_r23'
sys.path.insert(0,str(W/'project/chongqing_blender_v05'))
import district_geometry as geo

for vehicle in ['taxi','microvan']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    collection=bpy.context.scene.collection
    van=vehicle=='microvan';half=.86 if van else .875
    h=1.80 if van else 1.48
    geo.MATS={}
    for name,col,rough,metal in [
        ('paint',(.48,.21,.015) if not van else (.47,.47,.41),.29,.48),
        ('apron',(.24,.25,.23),.45,.53),('black',(.018,.022,.023),.56,.07),
        ('tyre',(.022,.022,.024),.84,.03),('rim',(.32,.34,.34),.29,.78),
        ('glass',(.060,.111,.135),.19,.48),('lamp',(.72,.78,.74),.19,.32),
        ('tail',(.37,.018,.012),.22,.44),('plate',(.022,.058,.14),.44,.31),
        ('cream',(.67,.64,.49),.64,.10),('seat',(.078,.082,.072),.87,0)]:
        geo.solid('r23_'+name,col,rough,metal);geo.MATS[name]=geo.MATS['r23_'+name]
    b=geo.Batch('R23_Body',collection)
    front=2.17;rear=-2.16
    axles=[-1.32,1.31];rad=.315
    ys=sorted(set([rear,-2.03,-1.91,-.90,-.69,0,.67,.86,1.90,2.03,front]+
        [round(a+.379*math.cos(i*math.pi/16),5) for a in axles for i in range(17)]))
    def proportions(y):
        taper=max(0,(abs(y)-1.60)/.58)
        return half-.14*taper*taper, (.98 if van else .875)-.135*taper
    def ring(y):
        w,z=proportions(y);floor=.245
        for a in axles:
            if abs(a-y)<=.38:floor=.325+math.sqrt(max(0,.38**2-(y-a)**2))
        return [(0,y,.225),(w*.93,y,floor),(w,y,min(z-.05,floor+.082)),
                (w*1.01,y,z-.074),(w*.965,y,z),(0,y,z+.037)]
    for sign in [-1,1]:
        previous=None
        for y in ys:
            row=[(sign*x,yy,z) for x,yy,z in ring(y)]
            if previous:
                for k in range(5):
                    points=[previous[k],row[k],row[k+1],previous[k+1]]
                    if sign<0:points.reverse()
                    b.mesh(points,[(0,1,2,3)],'apron' if k<=1 else 'paint',True)
            previous=row
        for y in [rear,front]:
            row=[(sign*x,yy,z) for x,yy,z in ring(y)]
            if (sign==1)==(y==front):row.reverse()
            b.mesh(row,[tuple(range(6))],'paint')
    # Glazed cabin with shaped pillars, rubber seals and a gently crowned roof.
    base_a,base_b=(-1.98,1.32) if van else (-1.58,.98)
    roof_a,roof_b=(-1.75,.73) if van else (-.91,.28)
    low=.96 if van else .864
    def glass_point(t,z,side):
        y=(base_a+(base_b-base_a)*t)*(1-z)+(roof_a+(roof_b-roof_a)*t)*z
        return Vector((side*(half*.94*(1-z)+half*.77*z),y,low+(h-low)*z))
    for sign in [-1,1]:
        for t1,t2 in zip([0,.07,.47,.53,.92],[.07,.47,.53,.92,1.]):
            pts=[glass_point(t1,0,sign),glass_point(t2,0,sign),glass_point(t2,1,sign),glass_point(t1,1,sign)]
            if sign<0:pts.reverse()
            b.mesh(pts,[(0,1,2,3)],'glass' if t1 in [.07,.53] else 'paint')
        for level in [.045,.98]:
            b.cylinder(glass_point(.02,level,sign),glass_point(.98,level,sign),.017,'black',8)
        for t in [.44,.88]:
            p=glass_point(t,0,sign);b.box((p.x*1.057,p.y,p.z-.09),(.033,.14,.032),'black')
        p=glass_point(.93,.13,sign)
        b.cylinder(p,(p.x+sign*.15,p.y,p.z+.016),.025,'black',10)
        b.box((p.x+sign*.18,p.y,p.z+.046),(.14,.17,.085),'paint')
    for t in [0,1]:
        row=[glass_point(t,0,-1),glass_point(t,0,1),glass_point(t,1,1),glass_point(t,1,-1)]
        if t==1:row.reverse()
        b.mesh(row,[(0,1,2,3)],'glass')
        for sign in [-1,1]:b.cylinder(glass_point(t,0,sign),glass_point(t,1,sign),.036,'paint',12)
    for j in range(8):
        u=-1+2*j/8;v=u+.25
        def roof(x,y):return (x*half*.77,y,h+.041*(1-x*x))
        b.quad(roof(u,roof_a),roof(v,roof_a),roof(v,roof_b),roof(u,roof_b),'paint')
    for y,sign in [(front,1),(rear,-1)]:
        b.box((0,y,.45),(1.39,.045,.065),'apron')
        b.box((0,y+sign*.034,.57),(.44,.021,.135),'plate')
        for x in [-.155,-.09,-.025,.041,.108,.17]:
            b.box((x,y+sign*.047,.57),(.02,.006,.055),'cream')
        for side in [-1,1]:
            b.box((side*.53,y,.71),(.30,.059,.10),'lamp' if sign==1 else 'tail')
            b.box((side*.62,y+sign*.034,.687),(.085,.014,.042),'cream')
    for z in [.525,.56,.595,.63]:
        b.box((0,front+.015,z),(.81,.025,.014),'black')
    if van:
        for side in [-1,1]:b.box((side*.885,-.59,.74),(.018,1.39,.023),'black')
    else:
        b.box((0,-.25,h+.105),(.45,.25,.12),'cream')
        for sign in [-1,1]:b.box((0,-.25+sign*.127,h+.108),(.28,.007,.050),'glass')
    b.finish()
    for j,y in enumerate(axles):
        for s in [-1,1]:
            w=geo.Batch('Tread',collection)
            w.cylinder((-.10,0,0),(.10,0,0),rad,'tyre',40)
            face=s*.108
            w.cylinder((0,0,0),(face,0,0),rad*.69,'black',32)
            w.cylinder((face,0,0),(face+s*.015,0,0),rad*.38,'rim',24)
            for k in range(10):
                angle=k*math.tau/10
                w.cylinder((face+s*.018,.075*math.cos(angle),.075*math.sin(angle)),(face,.211*math.cos(angle+.13),.211*math.sin(angle+.13)),.022,'rim',8)
            parent=bpy.data.objects.new('Hub_'+str(j)+('L' if s<0 else 'R'),None);collection.objects.link(parent)
            parent.location=(s*(half-.095),y,rad)
            for ob in w.finish():ob.parent=parent
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(S/(vehicle+'.blend')),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(S/'assets'/(vehicle+'.glb')),export_format='GLB')
