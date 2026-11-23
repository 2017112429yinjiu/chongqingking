"""Original noodle-shop stainless packing stand; Blender metres."""
from pathlib import Path
import bpy,math,json,sys
root=Path(__file__).resolve().parent
out=root/'characters/serving_counter_r18';out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color,rough=.6,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
steel=material('Brushed worktop',(.34,.36,.35),.39,.72)
sys.path.insert(0,str(root))
from counter_surface import bake
bake(steel,out)
legs=material('Aged enamel frame',(.12,.16,.14),.73,.25)
rubber=material('Rubber feet',(.023,.021,.018),.96)
wood=material('Lower pine shelf',(.23,.15,.075),.89)
for kind,socket in [('diff','Base Color'),('rough','Roughness'),('nor_gl','Normal')]:
    nt=wood.node_tree;bs=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(root/f'project/chongqing_blender_v05/materials/v05_scans/wood_table_worn/wood_table_worn_{kind}_2k.jpg'))
    if kind!='diff':tex.image.colorspace_settings.name='Non-Color'
    if kind=='nor_gl':
        normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.5
        nt.links.new(tex.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs[socket])
    else:nt.links.new(tex.outputs['Color'],bs.inputs[socket])
paper=material('Paper and bamboo',(.68,.61,.43),.92)
red=material('Faded red nameplate',(.22,.032,.018),.86)
diffuser=material('Warm white LED diffuser',(.82,.79,.69),.45)
bs=diffuser.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.91,.8,1);bs.inputs['Emission Strength'].default_value=2
def box(name,loc,scale,mat,bevel=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if mat==wood:
        uv=o.data.uv_layers.active
        for poly in o.data.polygons:
            axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[i for i in range(3) if i!=axis]
            for li in poly.loop_indices:
                co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
                uv.data[li].uv=(co[axes[0]]/.55,co[axes[1]]/.55)
    if bevel:
        m=o.modifiers.new('Rounded manufactured edge','BEVEL');m.width=bevel;m.segments=3
        m=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o
box('CQ_Worktop', (0,0,.782),(.86,.57,.026),steel,.008)
box('CQ_FoldedRearLip',(0,.277,.814),(.86,.018,.07),steel,.004)
for x in [-.371,.371]:
    for y in [-.225,.225]:
        box('CQ_SteelLeg',(x,y,.391),(.035,.035,.756),legs)
        box('CQ_RubberShoe',(x,y,.014),(.043,.043,.028),rubber,.004)
    box('CQ_SideBrace',(x,0,.195),(.024,.48,.025),legs)
for x in [-.27,-.09,.09,.27]:box('CQ_ShelfSlat',(x,0,.211),(.17,.48,.021),wood,.002)
box('CQ_FrontApron',(0,-.25,.735),(.79,.02,.065),legs)
box('CQ_HandpaintedPlate',(.235,-.264,.733),(.215,.005,.047),red,.003)
bpy.ops.object.text_add(location=(.235,-.269,.717),rotation=(math.pi/2,0,0));text=bpy.context.object;text.name='CQ_PackingSign'
text.data.font=bpy.data.fonts.load(str(root/'project/chongqing_godot_v05/assets/fonts/cq_ui.otf'))
text.data.body='打包取餐';text.data.size=.029;text.data.align_x='CENTER';text.data.extrude=.0004;text.data.materials.append(paper)
bpy.ops.object.convert(target='MESH')
# Worn pot, nested cups, chopsticks stay at the back-left away from hand/food sweep.
vv=[];ff=[];segments=48
for r,z in [(.039,.798),(.044,.892),(.0415,.892),(.0365,.802)]:
    for i in range(segments):a=i/segments*math.tau;vv.append((-.29+r*math.cos(a),.16+r*math.sin(a),z))
for ring in range(3):
    for i in range(segments):j=(i+1)%segments;ff.append((ring*segments+i,ring*segments+j,(ring+1)*segments+j,(ring+1)*segments+i))
ff.append(tuple(range(3*segments,4*segments)))
mesh=bpy.data.meshes.new('CQ_HollowUtensilPot');mesh.from_pydata(vv,[],ff);mesh.update();ob=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(ob);mesh.materials.append(steel)
uv=mesh.uv_layers.new(name='Cylinder')
for poly in mesh.polygons:
    for li in poly.loop_indices:
        point=mesh.vertices[mesh.loops[li].vertex_index].co
        uv.data[li].uv=((math.atan2(point.y-.16,point.x+.29)/math.tau)%1,(point.z-.798)/.10)
for p in mesh.polygons:p.use_smooth=True
for i in range(9):
    o=box('CQ_BambooChopstick',(-.30+(i%3)*.009,.15+(i//3)*.009,.913),(.003,.003,.21),paper,.0005);o.rotation_euler.y=(i%3-1)*.045
box('CQ_NapkinStack',(.28,.16,.805),(.11,.12,.018),paper,.001)
for i in range(4):box('CQ_NapkinEdges',(.28,.16,.803+i*.003),(.112,.122,.0006),paper,0)
# A supported rechargeable task lamp gives the packing station a real light source.
box('CQ_TaskLampClamp',(-.38,.225,.79),(.055,.05,.09),legs,.006)
curve=bpy.data.curves.new('CQ_TaskLampStem','CURVE');curve.dimensions='3D';curve.bevel_depth=.008;curve.bevel_resolution=3
spline=curve.splines.new('BEZIER');spline.bezier_points.add(3)
for bp,co in zip(spline.bezier_points,[(-.38,.225,.8),(-.38,.225,1.76),(-.32,.15,1.91),(-.13,-.02,1.92)]):
    bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
lamp=bpy.data.objects.new('CQ_TaskLampStem',curve);bpy.context.collection.objects.link(lamp);curve.materials.append(legs)
bpy.context.view_layer.objects.active=lamp;lamp.select_set(True);bpy.ops.object.convert(target='MESH')
box('CQ_TaskLampShade',(-.11,-.03,1.918),(.30,.075,.035),legs,.012)
box('CQ_TaskLampDiffuser',(-.11,-.03,1.898),(.267,.056,.006),diffuser,.003)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'serving_counter.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(root/'project/chongqing_godot_v05/assets/characters/serving_counter_r18.glb'),export_format='GLB',export_apply=True)
(out/'PROVENANCE.json').write_text(json.dumps({'source':'Original project-authored geometry including supported rechargeable task lamp; existing R15 Poly Haven Wood Table Worn maps reused; existing OFL project font','wood_source':'https://polyhaven.com/a/wood_table_worn','wood_license':'CC0-1.0','voluntary_credit':'Dimitrios Savva; Rico Cilliers; Poly Haven','units':'metres','top_height_m':.795,'size_m':[.86,.57,1.94]},indent=2))
