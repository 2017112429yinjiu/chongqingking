"""Cut the two feeder roads at the receiving asphalt edge, then grade the approaches."""
import bisect,bmesh,json,math
from mathutils import Vector
from roads import scene,changed,road_record,asset
from high_approaches import smooth
def cut(bm,faces,point,normal):
    good=[]
    for f in faces:
        if not f.is_valid:continue
        ds=[(v.co-point).dot(normal) for v in f.verts]
        if min(ds)<-.000005 and max(ds)>.000005:
            r=bmesh.ops.bisect_plane(bm,geom=[f,*f.verts,*f.edges],plane_co=point,plane_no=normal,dist=.000001)
            pieces={q for q in r['geom'] if isinstance(q,bmesh.types.BMFace) and q.is_valid}
            if f.is_valid:pieces.add(f)
            good.extend(pieces)
        else:good.append(f)
    return good
def load(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world);return bm
def finish(ob,bm):
    bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);ob.data.update();changed.add(ob.name);bm.free()
def local(bm,c,r):
    x,y=c
    return [f for f in bm.faces if max(v.co.x for v in f.verts)>x-r and min(v.co.x for v in f.verts)<x+r and max(v.co.y for v in f.verts)>y-r and min(v.co.y for v in f.verts)<y+r]
edits={}
for title,receiving,feeder,c,reach in [('north','734116597','734116595',(66.85,74.5),7),('south','1189963598','1324001442',(-49.,-94.),5)]:
    main=scene.objects['COL_Road_'+receiving+'_0_asphalt'];edge={}
    for f in main.data.polygons:
        if f.normal.z<.1:continue
        vs=[main.matrix_world@main.data.vertices[i].co for i in f.vertices]
        if max(p.x for p in vs)<c[0]-16 or min(p.x for p in vs)>c[0]+16 or abs(f.center.y-c[1])>10:continue
        # These ribbons are east-west at both junctions; each station contributes the southern boundary point.
        southern=sorted(vs,key=lambda p:p.y)[:2]
        for v in southern:edge[round(v.x,4)]=(v.y,v.z)
    xs=sorted(edge)
    def rim(x):
        i=min(len(xs)-2,max(0,bisect.bisect_right(xs,x)-1))
        a,b=xs[i:i+2];t=(x-a)/(b-a)
        return tuple(edge[a][k]+(edge[b][k]-edge[a][k])*t for k in [0,1])
    assert len(xs)>7
    for kind in ['asphalt','pavement','curb_concrete']:
        ob=scene.objects.get('COL_Road_'+feeder+'_0_'+kind)
        if not ob:continue
        bm=load(ob);pool=local(bm,c,12)
        for x in xs:
            pool=cut(bm,pool,Vector((x,0,0)),Vector((1,0,0)))
        # Branch sidewalks meet the outside of the receiving sidewalk; motor lanes continue to its asphalt lip.
        offset=0 if kind=='asphalt' or title=='south' else -1.15
        bits=[]
        for f in pool:
            x=f.calc_center_median().x;y1,z=rim(x);y2,_=rim(x+.0001)
            bits+=cut(bm,[f],Vector((x,y1+offset,0)),Vector((-(y2-y1)/.0001,1,0)).normalized())
        discard=[f for f in bits if f.calc_center_median().y>rim(f.calc_center_median().x)[0]+offset+.00001]
        if discard:bmesh.ops.delete(bm,geom=discard,context='FACES')
        moved=0
        for v in bm.verts:
            p=v.co
            if abs(p.x-c[0])>13 or abs(p.y-c[1])>13:continue
            y,h=rim(p.x);d=y+offset-p.y
            if -.001<d<reach:
                w=1-smooth(0.,reach,d)
                # Preserve the vertical curb faces relative to the paved shoulder.
                extra=(.10 if kind=='pavement' else .103 if kind=='curb_concrete' else 0.)
                if kind=='curb_concrete':extra+=max(-.11,min(.012,p.z-(h+.10-.15*(y-p.y))))
                v.co.z+=(h+extra-.045*d-p.z)*w;moved+=1
        edits[ob.name]=[len(discard),moved];finish(ob,bm)
    if title=='north':
        # Open the pavement across the mouth. Its two new ends meet the feeder's curb; upper sidewalk stays intact.
        for kind in ['pavement','curb_concrete']:
            ob=scene.objects['COL_Road_'+receiving+'_0_'+kind];bm=load(ob)
            faces=local(bm,c,8)
            for x in [64.1842,69.3838]:
                faces=cut(bm,faces,Vector((x,77.38,0)),Vector((1,.01312,0)).normalized())
            gone=[f for f in faces if 64.1842<f.calc_center_median().x+(f.calc_center_median().y-77.38)*.01312<69.3838 and f.calc_center_median().y<rim(f.calc_center_median().x)[0]+.18]
            bmesh.ops.delete(bm,geom=gone,context='FACES');edits[ob.name]=[len(gone),0];finish(ob,bm)
# A former shared footing survived inside the opened mouth, including both side curbs
# of the old feeder under the receiving street. Remove those interior supports only.
ob=scene.objects['COL_R23_PathFoundations'];bm=load(ob);pool=local(bm,(66.8,75.7),9)
for a,normal in [((62.6,0,0),(1,0,0)),((71.15,0,0),(1,0,0)),((0,73.1,0),(0,1,0)),((0,78.1,0),(0,1,0))]:
    pool=cut(bm,pool,Vector(a),Vector(normal))
gone=[f for f in pool if 62.60<f.calc_center_median().x<71.15 and 73.10<f.calc_center_median().y<78.10 and 32.8<f.calc_center_median().z<34.7]
edits[ob.name]=[len(gone),0];bmesh.ops.delete(bm,geom=gone,context='FACES');finish(ob,bm)
# Bring the ground outside the two side pavements up to their new level at the corner.
sidewalk=scene.objects['COL_Road_734116595_0_pavement']
from survey import Surfaces
samples=Surfaces([sidewalk])
for ob in scene.objects:
    if ob.type!='MESH' or not ob.name.startswith('COL_Terrain_200m'):continue
    count=0
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co;x,y,z=p
        if not 58<x<76 or not 64<y<76.:continue
        left=63.0343-.01312*(y-77.38);right=70.534-.01312*(y-77.38)
        mid=(left+right)*.5;outer=left if x<mid else right
        # The terrain returns to the outer edge at either side, without rising through the asphalt.
        across=(outer-x) if x<mid else (x-outer)
        if not -.9<across<3.5:continue
        at_y=min(73.40,y);sx=(63.0343+.12 if x<mid else 70.534-.12)-.01312*(at_y-77.38)
        hits=samples.down(sx,at_y,36,6)
        if not hits:continue
        h=hits[0][0]+.018*(y-at_y)-.035*max(0.,across)-.02
        w=smooth(64.,69.,y)*(1.-smooth(74.15,76.,y))*(1.-smooth(.15,3.5,across))
        if across<0:w*=smooth(-.90,-.14,across)
        if 0.<h-z<1.1:p.z+=(h-z)*w;v.co=ob.matrix_world.inverted()@p;count+=1
    if count:ob.data.update();changed.add(ob.name)
road_record['feeder_mouths']=edits
# Match the base of two retained stone flights on their actual ground, preserving the intentional risers above them.
for ob in scene.objects:
    if ob.type!='MESH' or not ob.name.startswith(('COL_Terrain_200m','COL_D18_NanquShoulder')):continue
    count=0;inv=ob.matrix_world.inverted()
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co;x,y,z=p;w=0;target=z
        if 13.3<x<19.0 and -79.5<y<-74.2:
            w=(1-smooth(1.30,2.75,abs(x-16.17)))*smooth(-79.35,-76.22,y)*(1-smooth(-75.61,-74.28,y))
            target=9.335+.103*(y+76.12)
        if -28.5<x<-19.0 and 60.2<y<67.5:
            along=-(x+23.85)*.904+(y-63.45)*.427
            across=(x+23.85)*.427+(y-63.45)*.904
            w=smooth(-3.7,-.12,along)*(1-smooth(1.9,3.2,along))*(1-smooth(1.4,3.1,abs(across)))
            target=29.095+.044*along
        if w>.00001 and 0<target-z<.75:p.z+=(target-z)*w;v.co=inv@p;count+=1
    if count:ob.data.update();changed.add(ob.name)
# The path passes the southeast garden wall on its downhill side. Keep the corners clear of handlebars.
alignment=[[15.9718,-66.2409],[23.0,-65.45],[27.5,-65.66],[32.05,-65.49],[36.3,-64.82],[41.85,-63.15],[52.0052,-61.6629]]
(asset/'wall_side_passage.json').write_text(json.dumps(alignment),'utf8')
