"""Original metre-scale garment tailoring. CC0-compatible project-authored meshes.
Designed folds, cut seams and weighted secondary bones, not a live cloth solver.
"""
import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def build(rig,shirt,root):
    bpy.context.view_layer.update()
    evaluated=shirt.evaluated_get(bpy.context.evaluated_depsgraph_get());m=evaluated.to_mesh()
    surface=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in m.vertices],[list(p.vertices) for p in m.polygons]);evaluated.to_mesh_clear()
    def front(x,z):
        h=surface.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)[0]
        return h.y if h else -.13
    cloth=bpy.data.materials.new('CQ_Apron_CottonJersey');cloth.use_nodes=True
    nt=cloth.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.9
    for kind,socket in [('diff','Base Color'),('rough','Roughness'),('nor_gl','Normal')]:
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(root/f'assets_incoming/cotton_jersey/cotton_jersey_{kind}_1k.jpg'))
        if kind!='diff':tex.image.colorspace_settings.name='Non-Color'
        if kind=='nor_gl':
            normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.8
            nt.links.new(tex.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
        elif kind=='diff':
            attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='GarmentWear'
            mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
            nt.links.new(tex.outputs['Color'],mix.inputs[1]);nt.links.new(attr.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs[socket])
        else:nt.links.new(tex.outputs['Color'],bs.inputs[socket])
    seam=bpy.data.materials.new('CQ_Cotton_BoundSeams');seam.use_nodes=True
    s=seam.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(.20,.17,.12,1);s.inputs['Roughness'].default_value=.96
    thread=bpy.data.materials.new('CQ_Cotton_Lockstitch');thread.use_nodes=True
    thread.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.37,.31,.22,1)
    thread.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.98
    # Dedicated hem bones allow delayed cloth sway without rotating a rigid bib.
    bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
    for side,x in [('L',.15),('C',0),('R',-.15)]:
        bone=rig.data.edit_bones.new('apron_'+side);bone.head=(x,-.17,.91);bone.tail=(x,-.17,.50);bone.parent=rig.data.edit_bones['pelvis']
    bpy.ops.object.mode_set(mode='OBJECT')
    anchors=[(.88,'pelvis'),(.99,'spine_01'),(1.08,'spine_02'),(1.21,'spine_03')]
    def piece(name,vv,ff,uv=None,mat=cloth,thickness=.0012):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vv,[],ff);mesh.update()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.parent=rig;mesh.materials.append(mat)
        layer=mesh.uv_layers.new(name='FabricMetres')
        colors=mesh.color_attributes.new(name='GarmentWear',type='FLOAT_COLOR',domain='POINT')
        for v in mesh.vertices:
            x,y,z=v.co
            oil=math.exp(-((x-.11)/.085)**2-((z-.82)/.10)**2)*.24
            oil+=math.exp(-((x+.12)/.04)**2-((z-.62)/.065)**2)*.16
            wear=.008*math.sin(x*31+z*17)*math.sin(z*23)
            colors.data[v.index].color=(.49-oil+wear,.45-oil+wear,.34-oil*.8+wear,1)
        for p in mesh.polygons:
            p.use_smooth=True
            for loop in p.loop_indices:
                i=mesh.loops[loop].vertex_index;co=mesh.vertices[i].co
                layer.data[loop].uv=uv[i] if uv else (co.x/.264,co.z/.264)
        groups={n:ob.vertex_groups.new(name=n) for n in ['pelvis','spine_01','spine_02','spine_03','apron_L','apron_C','apron_R']}
        for v in mesh.vertices:
            z=v.co.z;weights={}
            if z<.90:
                hem=min(1,max(0,(.91-z)/.25));side='L' if v.co.x>0 else 'R';blend=min(1,abs(v.co.x)/.19)
                weights={'pelvis':1-hem,'apron_C':hem*(1-blend),'apron_'+side:hem*blend}
            elif z>=anchors[-1][0]:weights={'spine_03':1.}
            else:
                for (za,ba),(zb,bb) in zip(anchors,anchors[1:]):
                    if za<=z<=zb:
                        t=(z-za)/(zb-za);weights={ba:1-t,bb:t};break
                if not weights:weights={'pelvis':1.}
            for bone,w in weights.items():
                if w>0:groups[bone].add([v.index],w,'REPLACE')
        arm=ob.modifiers.new('Tailored skin weights','ARMATURE');arm.object=rig
        if thickness:
            solid=ob.modifiers.new('Cotton edge thickness','SOLIDIFY');solid.thickness=thickness
        return ob
    def ribbon(name,line,width=.006,mat=seam):
        # Curved, slightly cupped woven tape; sparse input points must not leave
        # straight rigid plates at the shoulder or in the loose waist tails.
        points=[Vector(p) for p in line];curve=[]
        for i in range(len(points)-1):
            p0=points[max(0,i-1)];p1=points[i];p2=points[i+1];p3=points[min(len(points)-1,i+2)]
            for k in range(max(1,math.ceil((p2-p1).length/.008))):
                t=k/max(1,math.ceil((p2-p1).length/.008))
                curve.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
        curve.append(points[-1]);vv=[];ff=[];strips=4
        for i,pt in enumerate(curve):
            tangent=curve[min(i+1,len(curve)-1)]-curve[max(0,i-1)]
            across=tangent.cross(Vector((0,1,0))).normalized()
            for j in range(strips+1):
                u=j/strips*2-1
                vv.append(pt+across*(u*width*.5)+Vector((0,-width*.09*(1-u*u),0)))
                if i and j:
                    k=i*(strips+1)+j;ff.append((k-strips-2,k-strips-1,k,k-1))
        return piece(name,vv,ff,mat=mat)
    def position(u,t):
        # t=0 hem, t=1 bib top. Lower panel wraps the hips; upper bib is cut inward.
        z=.51+t*.73
        if z<=.91:
            f=(.91-z)/.40;theta=u*1.27
            x=(.228+.026*f)*math.sin(theta)
            y=-.174*math.cos(theta)-.025-.018*f
            # Unequal gravity folds spread from tied waist into the loose hem.
            y-=(.006+.014*f)*math.sin(u*math.pi*3.1+.32*f)+.004*math.sin(u*math.pi*6.5-.9*f)*f
            z+=f*f*(.008*math.sin(5*u+.6)+.006*u)
        else:
            f=(z-.91)/.33;width=.216*(1-f)+.120*f
            x=width*math.sin(u*1.27)/math.sin(1.27)
            # Smooth across button gaps while retaining the torso's round section.
            hits=[front(d,z+dz) for d in [-.05,0,.05] for dz in [-.012,0,.012]]
            center=min(hits)-.023
            blend=min(1,f*4);blend=blend*blend*(3-2*blend)
            y=-.199*(1-blend)+center*blend+.174*(1-math.cos(u*1.27))*(1-f)+.030*f*u*u
            y-=.006*math.sin(u*math.pi*3.1)*(1-f)**4
            y-=.010*f*f
            # Diagonal tension wrinkles converge at the waistband.
            y-=.005*math.sin(24*f+7*abs(u))*(1-abs(u))*(1-f)
            z-=.010*(1-u*u)*f**4
        return Vector((x,y,z))
    rows=71;cols=61;vv=[];uv=[];ff=[]
    for iz in range(rows):
        for ix in range(cols):
            u=ix/(cols-1)*2-1;t=iz/(rows-1);vv.append(position(u,t));uv.append(((u+1)*.31/.264,t*.73/.264))
            if iz and ix:
                k=iz*cols+ix;ff.append((k-cols-1,k-cols,k,k-1))
    apron=piece('CQ_SoftApron',vv,ff,uv)
    for side in [-1,1]:ribbon('CQ_ApronSideBinding',[(position(side,i/70)+Vector((0,-.002,0))) for i in range(71)],.004)
    for t in [0,1]:ribbon('CQ_ApronHem',[(position(i/40*2-1,t)+Vector((0,-.002,0))) for i in range(41)],.0045)
    # Sewn curved pocket follows the apron instead of bridging it as a quad.
    pv=[];pf=[]
    for row in range(15):
        for col in range(25):
            u=(col/24*2-1)*.48;t=.44+row/14*.17
            p=position(u,t);p.y-=.008+.009*math.sin(col/24*math.pi)*math.sin(row/14*math.pi)
            if row==14:p.z-=.007*math.sin(col/24*math.pi)
            pv.append(p)
            if row and col:
                k=row*25+col;pf.append((k-26,k-25,k,k-1))
    piece('CQ_ApronPocket',pv,pf)
    ribbon('CQ_PocketRolledLip',pv[-25:],.004)
    for col in [0,24]:ribbon('CQ_PocketStitch',[(pv[r*25+col]+Vector((0,-.0015,0))) for r in range(15)],.002,mat=seam)
    # One skinned mesh for small sewn dashes. Actual thread scale: 0.6 x 2.4 mm.
    stitches=[];stitch_faces=[]
    def stitch_line(points):
        distance=0.;next_dash=.001
        for a,b in zip(points,points[1:]):
            length=(b-a).length
            if length<1e-7:continue
            direction=(b-a)/length;across=direction.cross(Vector((0,1,0))).normalized()*.0003
            while next_dash+.0024<=distance+length:
                if next_dash>=distance:
                    start=a+direction*(next_dash-distance)+Vector((0,-.001,0));end=start+direction*.0024
                    k=len(stitches);stitches.extend([start-across,start+across,end+across,end-across]);stitch_faces.append((k,k+1,k+2,k+3))
                next_dash+=.004
            distance+=length
            if next_dash<distance:next_dash=distance+.001
    for t in [.008,.992]:stitch_line([position(i/120*2-1,t) for i in range(121)])
    stitch_line([p+Vector((0,-.001,-.005)) for p in pv[-25:]])
    piece('CQ_ApronSewnThread',stitches,stitch_faces,mat=thread,thickness=0)
    # Single neck loop drapes over shoulders, two waist ties meet behind the back.
    for side in [-1,1]:
        line=[tuple(position(side,1)+Vector((0,-.002,0))),(side*.105,-.092,1.32),(side*.09,-.02,1.365),(side*.085,.065,1.345),(side*.10,.09,1.28)]
        ribbon('CQ_CottonNeckLoop',line,.024,cloth)
    belt=[]
    for i in range(65):
        a=1.27+i/64*(math.tau-2*1.27);belt.append((.225*math.sin(a),-.150*math.cos(a)-.030,.92+.003*math.cos(a*3)))
    ribbon('CQ_ApronWaistTie',belt,.024,cloth)
    for side in [-1,1]:
        ribbon('CQ_ApronLooseTie',[(0,.125,.92),(side*.07,.14,.87),(side*.065,.135,.78),(side*.085,.14,.71)],.019,cloth)
    return apron
