"""Two level timber arcs around an existing upper-court tree. Blender metres."""
import math, json, random
import bpy
from mathutils import Vector

def build(g, kit, ground_z, out_dir):
    cx,cy=-26.36,70.02
    wood=g.Batch('R20_Tree_seat',kit);steel=g.Batch('R20_Seat_frame',kit)
    proxy=g.Batch('COLH_R20_Tree_seat',kit)
    supports=[];places=[]
    def pos(radius,deg,z):
        t=math.radians(deg)
        return (cx+radius*math.cos(t),cy+radius*math.sin(t),z)
    def height(radius,angle):
        return ground_z(Vector(pos(radius,angle,0)))
    def segment(batch,lo,hi,r1,r2,bottom,top,material):
        corners=[pos(r1,lo,bottom),pos(r2,lo,bottom),pos(r2,hi,bottom),pos(r1,hi,bottom)]
        verts=corners+[(x,y,top) for x,y,_ in corners]
        batch.mesh(verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)
    for arc,(start,end,count) in enumerate([(211,326,25),(49,133,18)]):
        middle=(start+end)/2
        top=height(1.56,middle)+.46
        for i in range(count):
            a=start+(end-start)*i/count;b=start+(end-start)*(i+1)/count
            segment(wood,a+.17,b-.17,1.32,1.79,top-.040,top,'wood')
            for r in [1.416,1.695]:
                pin=pos(r,(a+b)*.5,top)
                steel.cylinder(pin,(pin[0],pin[1],top+.0015),.004,'pin',10)
        for i in range(9):
            a=start+(end-start)*i/9;b=start+(end-start)*(i+1)/9
            for r in [1.41,1.69]:
                segment(steel,a,b,r-.019,r+.019,top-.098,top-.040,'iron')
            segment(proxy,a,b,1.32,1.79,min(height(1.55,a),height(1.55,b))-.025,top,'iron')
        for a in [start+4,middle,end-4]:
            for r in [1.405,1.698]:
                z=height(r,a);p=pos(r,a,z)
                steel.cylinder((p[0],p[1],z-.012),(p[0],p[1],top-.056),.022,'iron',12)
                steel.cylinder((p[0],p[1],z-.009),(p[0],p[1],z+.018),.046,'iron',12)
                supports.append({'xyz':list(p),'underside_gap_m':round(top-.04-z,4)})
        seat=pos(1.56,middle,top);front=pos(1.98,middle,height(1.98,middle))
        places.append({'seat':[seat[0],seat[2],-seat[1]],'front':[front[0],front[2],-front[1]],'arc':arc})
    for ob in wood.finish(.005):
        attr=ob.data.color_attributes.new(name='COLOR_0',type='FLOAT_COLOR',domain='CORNER')
        for lp in ob.data.loops:
            board=lp.vertex_index//8
            age=.77+.17*math.sin(13.59*board)
            # The nearest screws see more exposed end grain than the middle.
            value=age+.045*(lp.vertex_index%8>=4)
            attr.data[lp.index].color=(value,value*.94,value*.87,1)
        ob.data.color_attributes.active_color=attr
    steel.finish(.002)
    for ob in proxy.finish():ob.hide_render=True
    assert len(places)==2 and all(.22<p['underside_gap_m']<.58 for p in supports),supports
    court_surfaces(g,kit,ground_z,cx,cy)
    (out_dir/'tree_seats.json').write_text(json.dumps({'tree':'tree_41','center_blender_xy':[cx,cy],'places':places,'supports':supports},indent=2),encoding='utf-8')

def court_surfaces(g,kit,ground_z,cx,cy):
    from pathlib import Path
    import scanned_assets as scans
    rng=random.Random(2088)
    for key in ('step_concrete','soil_dark','stone'):
        mat=bpy.data.materials.get('CQ03_PBR_'+key) or bpy.data.materials.get('CQ03_'+key)
        if mat is None:raise ValueError(key)
        g.MATS[key]=mat
    paving=g.Batch('R20_Court_paving',kit)
    def point(r,ang,offset):
        x=cx+r*math.cos(ang);y=cy+r*math.sin(ang)
        return (x,y,ground_z(Vector((x,y,0)))+offset)
    radii=[1.31,1.70,2.12,2.54,2.93]
    for j,(inner,outer) in enumerate(zip(radii,radii[1:])):
        count=round(math.tau*(inner+outer)*.5/.65)
        for i in range(count):
            a=(i+.37*j)*math.tau/count+.002
            b=(i+1+.37*j)*math.tau/count-.002
            # Each flag follows the local grade. Subdivide long arcs and fit
            # the outer edge to the existing walk surface without a new step.
            c=(a+b)/2
            outline=[point(inner+.003,a,.015),point(outer-.003,a,.015),point(outer-.003,c,.015),point(outer-.003,b,.015),point(inner+.003,b,.015),point(inner+.003,c,.015)]
            core=point((inner+outer)*.5,c,.015)
            paving.mesh(outline+[core],[(k,(k+1)%6,6) for k in range(6)],'step_concrete')
    # Vertex tint samples the real tree and seat frame against the sky.
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    directions=[]
    for i in range(32):
        r=math.sqrt((i+.5)/32);angle=i*math.pi*(3-math.sqrt(5))
        directions.append(Vector((r*math.cos(angle),r*math.sin(angle),math.sqrt(1-r*r))))
    for ob in paving.finish():
        values=[]
        for idx,p in enumerate(ob.data.vertices):
            point3=p.co+Vector((0,0,.024))
            occlusion=0
            for direction in directions:
                hit,location,_,_,item,_=bpy.context.scene.ray_cast(dg,point3,direction,distance=15)
                if hit:
                    trans=.58 if 'Planted_tree_' in item.name else 1.
                    occlusion+=trans*(1-min(1,(location-point3).length/15))
            flag_tone=.92+.075*math.sin((idx//7)*21.54)
            shade=min(.995,max(0.,flag_tone*(1-.42*occlusion/32)))
            values.append((shade,shade*.982,shade*.95,1))
        color=ob.data.color_attributes.new(name='COLOR_0',type='FLOAT_COLOR',domain='CORNER')
        for lp in ob.data.loops:color.data[lp.index].color=values[lp.vertex_index]
        ob.data.color_attributes.active_color=color
    beds=g.Batch('COL_R20_Garden_edge',kit)
    earth=g.Batch('COL_R20_Terrace_soil',kit)
    herb=g.Batch('R20_Kitchen_garden',kit)
    g.MATS['herb']=g.solid('R20_garlic_chive',(.084,.165,.045),.92)
    # Two level beds step uphill along the west side of the tree court.
    scans.setup(Path(__file__).resolve().parent/'project/chongqing_blender_v05')
    for j,(x,y,width,depth) in enumerate([(-30.42,71.18,1.52,1.52),(-30.64,73.18,1.94,1.66)]):
        x0=x-width/2;x1=x+width/2;y0=y-depth/2;y1=y+depth/2
        corners=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        soil=max(ground_z(Vector((px,py,0))) for px,py in corners)+.13
        earth.box((x,y,soil-.065),(width-.13,depth-.13,.13),'soil_dark')
        for side,(a,b) in enumerate(zip(corners,corners[1:]+corners[:1])):
            aa=Vector(a);bb=Vector(b);length=(bb-aa).length;count=round(length/.41)
            for i in range(count):
                h=aa.lerp(bb,(i+.5)/count)
                foot=ground_z(Vector((h.x,h.y,0)))-.06;cap=soil+.068+rng.uniform(-.010,.006)
                w,d=(length/count-.006,.15) if side%2==0 else (.15,length/count-.006)
                beds.box((h.x,h.y,(foot+cap)/2),(w,d,cap-foot),'stone')
        scans.make_shrub('R20_Court_shrub_'+str(j),(x-.22,y+.17,soil-.018),height=.60+.17*j,seed=221+j,collection=kit,lod='low')
        for k in range(10):
            bx=rng.uniform(x+.10,x1-.14);by=rng.uniform(y0+.15,y1-.14)
            for blade in range(8):
                ang=rng.random()*math.tau;dx,dy=math.cos(ang),math.sin(ang)
                tall=rng.uniform(.12,.28);spread=rng.uniform(.035,.105)
                q=Vector((bx+.017*dx,by+.017*dy,soil-.012))
                tip=q+Vector((spread*dx,spread*dy,tall*.88));bend=q+Vector((spread*.43*dx,spread*.43*dy,tall))
                w=Vector((dy,-dx,0))*.008
                herb.mesh([q-w,q+w,bend+w*.5,bend-w*.5,tip],[(0,1,2,3),(3,2,4)],'herb')
    beds.finish(.012);earth.finish();herb.finish()
